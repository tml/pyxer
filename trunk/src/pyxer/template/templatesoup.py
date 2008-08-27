# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

import cgi
import copy
import inspect
import logging
import os
import os.path
import re
import string
import sys
import types
log = logging.getLogger(__name__)

from BeautifulSoup import *
import StringIO
import re

import logging
log = logging.getLogger(__name__)

# _commands = re.compile(u"\&lt;\%(.*?)\%\&gt;", re.M)
_vars = re.compile(u"""
    \$(
        \$
        |
        \{(.*?)\}
        |
        ([a-z_][a-z_0-9]*)(\.[a-z_][a-z_0-9]*)*
    )
    """, re.M|re.VERBOSE)

class Dict(dict):

    " Helper class to map dicts to attributes "

    def __getattr__(self, name):
        try:
            return dict.__getattr__(self, name)
        except:
            return self[name]

    def __setattr__(self, name, value):
        self[name] = value

class PyxerSoup(BeautifulSoup):

    def byid(self, name):
        res = self.findAll(id=name)
        if len(res)==1:
            return res[0].contents
        return None

class CodeGenerator(object):

    level = 0
    tab = '\t'

    def __init__(self, code=None, level=0, tab='\t'):
        self.code = code or []
        if level != self.level:
            self.level = level
        if tab != self.tab:
            self.tab = tab
        self.pad = self.tab * self.level

    def line(self, *lines):
        for text in lines:
            self.code.append(self.pad + text)

    def start_block(self, text):
        self.line(text)
        self.level += 1
        self.pad += self.tab

    def end_block(self, nblocks=1, with_pass=False):
        for n in range(nblocks):
            if with_pass:
                self.line('pass')
            self.level -= 1
            self.pad = self.pad[:-len(self.tab)]

    def insert_block(self, block):
        lines = block.splitlines()
        if len(lines) == 1:
            # special case single lines
            self.line(lines[0].strip())
        else:
            # adjust the block
            for line in _adjust_python_block(lines, self.tab):
                self.line(line)

    def __str__(self):
        return '\n'.join(self.code + [''])

    def debug(self):
        for n in range(0, len(self.code)):
            print "%4d:" % (n+1), self.code[n]

    def pretty(self):
        out = []
        for n in range(0, len(self.code)):
            out.append("%4d: %s" % (n+1, self.code[n].replace("\t", "    ")))
        return "\n".join(out)

# tree = etree.parse(input, PyxerTreeBuilder())
#for node in tree:
#    print "#", len(node)

class TemplateSoup(object):

    def __init__(self, source, html5=False, strict=True):
        self.strict = strict
        self.html5 = html5
        self.bytecode = None
        self.sourcecode = u""
        self.layout = []
        self.extends = []
        self.parse(source)
        self.generateCode()
        self.generateByteCode()

    def parse(self, source):
        self.source = source

        # Parse source
        if self.html5:
            import html5lib
            import html5lib.treebuilders
            parser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("beautifulsoup"))
            self.soup = parser.parse(StringIO.StringIO(self.source))
        else:
            self.soup = PyxerSoup(self.source)
        return self.soup

    def generateCode(self):
        self.code = CodeGenerator()
        self.code_line = 1

        # Create code
        #self.code.line(
            # "from BeautifulSoup import *",
            # "soup = BeautifulSoup()",
        #)
        self.code.start_block("def main():")
        self.code.line(
            "soup = parent = node = PyxerSoup()",
        )

        try:
            self.current_node = self.soup
            self.loop(self.soup)
        except SyntaxError, e:
            #print "###", self.code_line
            #part = self.source.splitlines()[self.code_line: self.code_line+4]
            #print "\n".join(part)
            raise

        self.code.line(
            "return soup"
        )

        self.code.end_block()
        #self.code.line(
        #    "main(soup)",
        #    "print soup",
        #    # "print soup.prettify()",
        #)

        self.sourcecode = unicode(self.code)

    def generateByteCode(self):
        self.bytecode = compile(self.sourcecode, "<string>", "exec")

    def render(self, vars={}, encoding="utf8", parent=None):

        # Prepare context
        context = Dict(vars)
        context.update(
            add=add,
            PyxerSoup=PyxerSoup,
            HTML=PyxerSoup,
            XML=PyxerSoup,
            Tag=Tag,
            CData=CData,
            Comment=Comment,
            NavigableString=NavigableString,
            Declaration=Declaration,
            )

        # print context.keys()
        soup = None
        try:
            exec(self.bytecode, context)
            soup = context["main"]()
            context["top"] = soup

            # Applying the layouts
            for layout in self.layout:
                template = eval(layout, context)
                if isinstance(template, TemplateSoup):
                    soup = template.render(context, encoding, parent)

        except:
            # XXX must become more Python conform
            error = inspect.trace()[-1][0].f_locals.get("error", None)
            if not error:
                raise
            exc_info = sys.exc_info()
            e = exc_info[1]
            if getattr(e, 'args', None):
                arg0 = e.args[0]
            else:
                arg0 = str(e)
            msg = arg0 + "\nError in template line %d: %s" % error
            raise exc_info[0], msg, exc_info[2]
        return soup

    def getAttr(self, node, name):
        value = None
        if node.has_key("py:" + name):
            value = node["py:" + name]
            del node["py:" + name]
        # Only <meta> has an 'content' attribute
        if node.name != "meta" and name != "content" and node.has_key(name):
            if value is not None:
                raise "Attribute %s is defined twice"
            value = node[name]
            del node[name]
        return value

    def checkSyntax(self, value, mode="eval"):
        if self.strict:
            try:
                compile(value, "<string>", mode)
            except SyntaxError, msg:
                raise SyntaxError, str(msg) + " in expression %s" % value
        return value

    def loop(self, nodes, depth=0):
        for node in nodes:
            indent = 0
            pyDef = None

            # Handle tags
            if isinstance(node, Tag):

                pyDef = self.getAttr(node, "def")
                pyMatch = self.getAttr(node, "match")                   # XXX todo
                pyWhen = self.getAttr(node, "when")                     # XXX todo
                pyOtherwise = self.getAttr(node, "otherwise")           # XXX todo
                pyFor = self.getAttr(node, "for")
                pyIf = self.getAttr(node, "if")
                pyChoose = self.getAttr(node, "choose")                 # XXX todo
                pyWith = self.getAttr(node, "with")
                pyReplace = self.getAttr(node, "replace")
                pyContent = self.getAttr(node, "content")
                pyAttrs = self.getAttr(node, "attrs")
                pyStrip = self.getAttr(node, "strip")

                pyExtends = self.getAttr(node, "extends")               # XXX todo
                pyLayout = self.getAttr(node, "layout")                 # XXX todo

                if pyExtends:
                    self.extends.append(pyExtends)

                if pyLayout:
                    self.layout.append(pyLayout)

                if pyDef:
                    self.code, code_backup = CodeGenerator(), self.code
                    if not pyDef.strip().endswith(")"):
                        pyDef += "()"
                    self.code.start_block("def %s:" % pyDef)
                    self.code.line(
                        "soup = parent = node = PyxerSoup()"
                    )

                # For error handling
                self.code.line(
                    "error = (%d, %r)" % (self.code_line, unicode(node)[:60])
                    )

                if pyFor:
                    self.code.start_block("for %s:" % self.checkSyntax(pyFor))
                    indent += 1

                if pyIf:
                    self.code.start_block("if %s:" % self.checkSyntax(pyIf))
                    indent += 1

                if pyWith:
                    self.code.line(
                        self.checkSyntax(pyWith, "exec"),
                        # pyWith
                    )

                if pyReplace or pyStrip:
                    pyStrip = True
                else:
                    self.code.line(
                        "node = Tag(soup, %r, %r)" % (node.name, node.attrs),
                        "parent.append(node)",
                    )

                if pyStrip and pyContent:
                    pyReplace = pyContent
                    pyContent = None

                if pyReplace:
                    self.code.line(
                        "add(parent, %s)" % self.checkSyntax(pyReplace),
                        )

                elif pyContent:
                    self.code.line(
                        "add(node, %s)" % self.checkSyntax(pyContent),
                        # "print '#', type(value)",
                        # "node.append(value)",
                        )

                if pyAttrs and not pyStrip:
                    self.code.line(
                        "attrs = %s" % self.checkSyntax(pyAttrs),
                        "for key, value in attrs.items(): node[key] = unicode(value)",
                        )

                # print " " * depth, "<%s> %s" % (node.name, node.attrs)

            # Handle the rest
            elif isinstance(node, NavigableString):

                # Count line numbers for error reporting
                self.code_line += unicode(node).count(u'\n')

                if isinstance(node, ProcessingInstruction):
                    pass
                elif isinstance(node, Declaration):
                    self.code.line(
                        "node = Declaration(%r)" % NavigableString.__str__(node),
                        "parent.append(node)",
                    )
                elif isinstance(node, CData):
                    self.code.line(
                        "node = CData(%r)" % NavigableString.__str__(node),
                        "parent.append(node)",
                    )
                elif isinstance(node, Comment):
                    value = NavigableString.__str__(node)
                    if not value.startswith("!"):
                        self.code.line(
                            "node = Comment(%r)" % value,
                            "parent.append(node)",
                        )
                else:

                    # Handle ${...}
                    pos = 0
                    src = unicode(node)
                    for m in _vars.finditer(src):
                        cmd = m.group(1)
                        if cmd != "$":
                            if cmd.startswith("{"):
                                cmd = cmd[1:-1].strip()
                            if src[pos:m.start()]:
                                self.code.line(
                                    "node = NavigableString(%r)" % unicode(src[pos:m.start()]),
                                    "parent.append(node)",
                                )
                            self.code.line(
                                "add(parent, %s)" % self.checkSyntax(cmd),
                                # "node = NavigableString(value)",
                                # "parent.append(value)",
                            )
                        else:
                            # Escaped dollar $$ -> $
                            self.code.line(
                                "node = NavigableString(%r)" % u"$",
                                "parent.append(node)",
                            )
                        pos = m.end()
                    if src[pos:]:
                        self.code.line(
                            "node = NavigableString(%r)" % unicode(src[pos:]),
                            "parent.append(node)",
                        )

            # This must be an error!
            else:
                # print "XXX", type(node), repr(node)
                raise "Unknown element"

            # Next level
            if hasattr(node, "contents") and not(pyContent or pyReplace):
                self.code.line(
                    "parent = node",
                )
                self.loop(node, depth + 1)
                self.code.line(
                    "parent = parent.parent",
                )

            for i in range(indent):
                self.code.end_block()

            if pyDef:
                self.code.line(
                    "return soup"
                )
                self.code.end_block()
                lines = self.code.code
                self.code = code_backup
                self.code.code = lines + self.code.code

def add(parent, value):
    try:
        if type(value) is types.FunctionType:
            value = value()
        if value is None:
            return
        if isList(value):
            for node in value:
                parent.append(node)
            return
        if not isinstance(value, Tag):
            value = unicode(value)
        node = NavigableString(value)
        parent.append(node)
    except Exception, e:
        log.exception("element error")
        node = NavigableString(unicode(e))
        parent.append(node)

if __name__=="__main__":

    def layout(name):
        return TemplateSoup("""
        <html>
            <head>
                <title>Great!</title>
            </head>
            <strong py:content="top.byid('test')">$demo</strong>
        </html>
        """)

    ts = TemplateSoup("""
    <html py:layout1="layout(123)">
    <div py:with="a=1; b=2">$a $b</div>
    <div py:def="demo" py:strip="1">Hier ist was drin</div>
    <hr />
    $demo
    <!-- Comment -->
    <!--! Comment -->
    <div id="super">
        Super important
    </div>
    End
    <div py:content="soup.findAll(id='super')[0].contents">Ersetzen!</div>
    </html>
    """)
    ts = TemplateSoup("""
    <html py:layout="layout(123)">
        <body id="test">
            Here we go!
        </body>
    </html>
    """)
    print ts.code.pretty()
    soup = ts.render(dict(x=1, layout=layout))

    print 40*"-"
    print soup.prettify()

    if 0:
        mod = TemplateSoup(data2, html5=True)
        mod.code.debug()
        exec(str(mod.code), dict(
            x=1,
            samples=[
                ("Home", "/"),
                ("Developer", "/developer"),
                ("Contacts", "/legal"),
                ]))

    if 0:
        # t = Template(_test)
        t = Template(_test3, html=True, path=r"c:\test.html")
        print t.source.encode("latin1", "ignore")
        print t.render(dict(name='dirk "enzo" holtwick'), encoding="ascii")
