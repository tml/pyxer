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

#try:
#    from cStringIO import StringIO
#except:

from StringIO import StringIO

import html5lib
from html5lib import treebuilders, serializer, treewalkers
from html5lib.filters import sanitizer
from html5lib.constants import voidElements

from pyxer.utils import * 
from xml.dom import minidom, Node
 
_commands = re.compile(u"\&lt;\%(.*?)\%\&gt;", re.M)
_vars = re.compile(u"""
    \$(
        \$
        |
        \{(.*?)\}
        |
        ([a-z_][a-z_0-9]*)(\.[a-z_][a-z_0-9]*)*
    )
    """, re.M|re.VERBOSE)

class TemplateError(Exception):
    pass

class pyxer_tohtml:

    def __init__(self, value):
        self.value = value

def pyxer_start_tag(tag, attr, close=False):
    sys.stdout.write("<" + tag)
    for k, v in attr.items():
        sys.stdout.write(' %s="%s"' % (
            html_escape(k),
            html_escape(v),
            ))
    if close:
        sys.stdout.write(" />")
    else:
        sys.stdout.write(">")

def pyxer_tostring(x, escape=True):
    try:
        if x is None:
            return u''
        #if instanceof(x, pyxer_tohtml):
        #    return x.value
        if type(x) is types.FunctionType:
            if escape:
                return html_escape(x())
            return x()
        if escape:
            return html_escape(unicode(x))
        return unicode(x)
    except:
        return u''    
    
#def pyxer_byid(id):
#    exec "__pyxer_byId" + id + "()"

class Context:

    def __init__(self, vars):
        #for k, v in vars.items():
        #    self.setattr(k, v)
        pass

_appContainer = """
import sys
def __pyxer_main__():    
    __pyxer_stdout_backup__, sys.stdout = sys.stdout, __pyxer_stdout__
    try:
%s    
    finally:
        sys.stdout = __pyxer_stdout_backup__
"""

class Parser:

    def __init__(self):
        pass

    def parse(self, src, html=True):
        self.xhtml = False
        self._indent = 2
        self._code = []
        self._escape = True
        self._functions = {}
        self._pos_line = 0        
        if html:
            f = StringIO(src)
            parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
            document = parser.parse(f)
            self._data = []
            self._id_pool = []
            # print document.toxml()            
            self._walkNodes(document)
            self._flushData()
        else:
            self._addCommand(src)        
        functions = "\n".join(["\n".join(block) for block in self._functions.values()])         
        self.source = functions + _appContainer % ("\n".join(self._code))
        return self.source

    def _attrToDict(self, attributes):
        attrs = {}
        if attributes:
            for k, v in attributes.items():
                try:
                    attrs[unicode(k).lower()] = unicode(v)
                except:
                    attrs[k] = v
        return attrs

    def _removeAttrByPrefix(self, node, prefix="py:"):
        for k in node.attributes.keys():
            if k.lower().startswith(prefix):
                del node.attributes[k]
        return node.attributes

    def _addIndent(self, diff=0):
        return ((self._indent + diff)* 4) * " "

    def _addText(self, src):
        pos = 0
        if src:
            for m in _vars.finditer(src):
                cmd = m.group(1)
                if cmd != "$":
                    if cmd.startswith("{"):
                        cmd = cmd[1:-1].strip()
                    if src[pos:m.start()]:
                        self._code.append(self._addIndent() + "sys.stdout.write(%r)" % src[pos:m.start()])
                    self._code.append(self._addIndent() + "try:")
                    self._code.append(self._addIndent(+1) + "sys.stdout.write(__pyxer_tostring__(%s, __pyxer_html__))" % cmd)
                    self._code.append(self._addIndent() + "except: pass")
                else:
                    # Escaped dollar $$ -> $
                    self._code.append(self._addIndent() + "sys.stdout.write(%r)" % u"$")
                pos = m.end()
            if src[pos:]:
                self._code.append(self._addIndent() + "sys.stdout.write(%r)" % src[pos:])
        else:
            self._code.append(self._addIndent() + "pass")

    def _addPos(self):
        self._code.append(self._addIndent() + "pos = (1,1)")

    def _addCommand(self, src):
        pos = 0
        for m in _commands.finditer(src):
            cmd = html_unescape(m.group(1).strip())                    
            self._addText(src[pos:m.start()])
            if cmd.endswith(":"):
                if (cmd.startswith("elif") or cmd.startswith("else")):
                    self._indent -= 1
                else:
                    self._addPos()
                self._code.append(self._addIndent() + cmd)
                self._indent += 1
            elif cmd=="end":
                self._indent -= 1
            else:
                self._addPos()
                self._code.append(self._addIndent() + cmd)
            pos = m.end()
        self._addText(src[pos:])
        return self

    def _flushData(self):
        self._addCommand(u"".join(self._data))
        self._data = []

    def _handleTag(self, node):
        loop = 0
        indent = 0
        tag = node.nodeName
        # byid = None
        self._flushData()
        attr = self._attrToDict(node.attributes)
        """
           1. py:def
           2. py:match
           3. py:when
           4. py:otherwise
           5. py:for
           6. py:if
           7. py:choose
           8. py:with
           9. py:replace
          10. py:content
          11. py:attrs
          12. py:strip
        """
        
        block = None
        _code = None
        strip = attr.has_key("py:strip")
        if attr.has_key("py:def"):
            fname = attr["py:def"].strip()
            if not fname.endswith(")"):
                fname += u"()"
            
            _code = self._code
            self._code = self._functions[fname] = []            
            _indent = self._indent
            self._indent = 0
            
            self._code.append(self._addIndent() + u"def %s:" % fname)
            self._indent += 1
            indent += -1
        
        elif attr.has_key("py:block"):
            fname = block = attr["py:block"].strip() or attr.get("id", "") or attr.get("name", "") or attr.get("class", "") or tag
            if not fname:
                raise Exception("py:block needs id")
            
            if not fname.endswith(")"):
                fname += u"()"
            
            _code = self._code
            self._code = self._functions[fname] = []    
            _indent = self._indent
            self._indent = 0
            
            self._code.append(self._addIndent() + u"def %s:" % fname)
            self._indent += 1
            indent += -1
            strip = True
        
        if attr.has_key("py:for"):
            expr = attr["py:for"].strip()
            self._code.append(self._addIndent() + u"for %s:" % expr)
            self._indent += 1
            indent += -1
        
        if attr.has_key("py:if"):
            expr = attr["py:if"].strip()
            self._code.append(self._addIndent() + u"if %s:" % expr)
            self._indent += 1
            indent += -1
        
        if attr.has_key("py:replace"):
            expr = attr["py:replace"].strip()
            self._flushData()
            self._code.append(self._addIndent() + "sys.stdout.write(__pyxer_tostring__(%s, __pyxer_html__))" % expr)
            return
            
        # self._code.append(self._addIndent() + u"for %s:" % expr)
        
        if attr.has_key("py:content"):
            expr = attr["py:content"].strip()
            # self._code.append(self._addIndent() + u"for %s:" % expr)
        
        if attr.has_key("py:attrs"):
            expr = attr["py:attrs"].strip()            
            # self._code.append(self._addIndent() + u"for %s:" % expr)
        
        if attr.has_key("py:fill"):
            expr = attr["py:fill"].strip()
                        
            # self._code.append(self._addIndent() + u"for %s:" % expr)
        
        if attr.has_key("py:extends"):
            expr = attr["py:extends"].strip()
            self._code.append(self._addIndent() + u"extends(%s)" % expr)
            
        if attr.has_key("py:include"):
            expr = attr["py:include"].strip()
            self._code.append(self._addIndent() + u"include(%s)" % expr)
        
        if attr.has_key("py:eval"):
            expr = attr["py:eval"].strip()
            self._code.append(self._addIndent() + u"%s" % expr)
                    
        # Prepare Tag        
        if not strip:
            self._removeAttrByPrefix(node)
            self._data.append(u"<%s" % tag)
            if node.hasAttributes():
                for name, value in node.attributes.items():
                    self._data.append(' %s="%s"' % (
                        html_escape(name),
                        html_escape(value)))                
                # self._data.append(u" ")
            
            has_childs = node.hasChildNodes() 
            if (not has_childs) and self.xhtml and (tag not in ("script", "style")):
                self._data.append(u"/>")
            else:                
                self._data.append(u">")                                        
                    
                # Special feature byID
                #if attr.has_key("id"):
                #    expr = attr["id"].strip()
                #    if expr and (expr not in self._id_pool):
                #        self._flushData()
                #        byid = "id_" + expr
                #        self._code.append(self._addIndent() + u"def %s():" % byid)
                #        self._indent += 1
                #        self._id_pool.append(expr)
                # Walk sub nodes
        
        if tag in ("script", "style"):
            self._escape = False
        
        for node in node.childNodes:
            self._walkNodes(node)

        if tag in ("script", "style"):
            self._escape = True
            has_childs = True
            
        # Closing tag
        if (not strip) and has_childs and (tag not in voidElements):
            self._data.append(u"</%s>" % tag)
                
        # Flush all including indent
        if indent:
            self._flushData()
            self._indent += indent

            if _code:
                self._code = _code
                self._indent = _indent
        
            # Call Block
            if block:                
                # self._indent -= 1
                self._code.append(self._addIndent() + u"%s()" % block)
            
        return loop

    def _walkNodes(self, node):

        loop = 1
        dump = 0
        
        # Document Type        DOM Treebuilder 
        if node.nodeType == Node.DOCUMENT_TYPE_NODE:
            if node.name:
                if node.publicId or node.systemId:
                    pubid = node.publicId or ""
                    sysid = node.systemId or ""
                    self.xhtml = "xhtml" in (pubid + " " + sysid).lower()                     
                    self._data.append(u'<!DOCTYPE %s' % node.name.upper())
                    if pubid:
                        self._data.append(u' PUBLIC "%s"' % pubid)
                    elif sysid:
                        self._data.append(u' SYSTEM')
                    if sysid:
                        self._data.append(u' "%s"' % sysid)
                    self._data.append(u'>\n')
                else:
                    self._data.append(u"<!DOCTYPE %s>\n" % (node.name))
            else:
                self._data.append(u"<!DOCTYPE >\n")

        # Text
        elif node.nodeType == Node.TEXT_NODE:
            if dump: print "TEXT", repr(node.data)
            if self._escape:
                self._data.append(html_escape(node.data))
            else:
                self._data.append(node.data)

        # Tag
        elif node.nodeType == Node.ELEMENT_NODE:    
            if dump: print "TAG", repr(node.tagName)     
            loop = self._handleTag(node)

        # Comment
        elif node.nodeType == Node.COMMENT_NODE:
            if not node.data.lstrip().startswith("!"):
                self._data.append(node.toxml())

        # Errors/ Unknown
        else:
            pass
            # print "???", node, node.nodeType, node.normalize() #.toxml()

        if loop:
            for node in node.childNodes:
                self._walkNodes(node)

class Template:

    """
    Very very simple templating language
    """

    def __init__(self, src=None, path="", html=True):
        self.path = path
        self.isHTML = html
        if src is not None:
            self.translate(src)

    def translate(self, src):
        # self.isHTML = html
        self.source = Parser().parse(src, self.isHTML)
        # log.debug("\n%s", self.source)                
        return self

    parse = translate

    def compile(self):        
        bytecode = compile(self.source, self.path, "exec")        
        return bytecode

    def render(self, vars={}, encoding="utf8", parent=None):
        bytecode = self.compile()
        self._extends = None
        out = StringIO()
        context = Dict(vars)
        context.update(dict(
            __pyxer_stdout__=out,
            __pyxer_tostring__=pyxer_tostring,
            __pyxer_path__=self.path,
            __pyxer_html__=self.isHTML,
            self=self,
            extends=self.extends,
            include=self.include,
            HTML=pyxer_tohtml,
            ))
        # print context.keys()
        try:
            exec(bytecode, context)
            context["__pyxer_main__"]()
        except:
            pos = inspect.trace()[-1][0].f_locals.get("pos", None)
            # print pos
            exc_info = sys.exc_info()
            e = exc_info[1]
            if getattr(e, 'args', None):
                arg0 = e.args[0]
            else:
                arg0 = str(e)
            # raise Exception("Somewhat")
            raise exc_info[0], e, exc_info[2]
        if self._extends is not None:
            template = Template().load(self.find(self._extends))        
            # print context.keys()
            return template.render(context)
        #for l in out.buf:
        #    print "->", repr(l)
        return out.getvalue().encode(encoding, "ignore")

    def find(self, filename):
        if not self.path:
            raise TemplateError("You have to provide a path to the directory of the template")
        return os.path.join(os.path.dirname(self.path), filename)

    def load(self, filename, encoding="utf8"):
        self.path = filename
        src = open(self.path, "rb").read()
        return self.translate(src)

    def extends(self, template):
        self._extends = template

    def include(self, filename):
        template = Template().load(self.find(filename))
        sys.stdout.write(template.render(globals()))

def HTMLTemplate(src=None, path=""):
    " Shortcut for HTML Templates "
    return Template(src, path, html=True)

if __name__=="__main__":
    _test = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
    <script type="text/javascript">
    <!--
        if(i>2) alert(1)
    // -->
    </script>
</head>
<body>
    <h1>Start</h1>

    <% def test(a): %>

        <p>Hier wohnt $a.</p>

        <% return "Nix" %>

    <% end %>

    <% x=1; y='ä' %>

    <% if name: %>

        <% for i in range(1,5): %>

            $i Hello ${name.capitalize()} $x$y <br />

            <% print 2*3 %>

        <% end %>

    <% else: %>

        What's your name? äöü

    <% end %>

    ${test('Anna')}
    <% test('Jupp') %>

    <h1 py:def="title" py:strip class="py_$name">Title</h1>

    <p id="content">
        Some <b>Content</b>
    </p>

    ${id_content}

    <!--! Weg -->
    <? Was? ?>
    <br>

    <p py:if="x==1">X1 Und noch was Text</p>
    <p py:if="x!=1">X0 Und noch was Text</p>

    $${title}

</html>
"""

    _test2 = u"""<h1>Start ÄÜÖ</h1>

      <% def test(a): %>

          <p>Hier wohnt $a.</p>

      <% end %>

      <% x=1; y='ä' %>

      <% if name: %>

          <% for i in range(zuzu,5): %>

              $i Hello ${name.capitalize()} $x$y <br>

              <% print 2*3 %>

          <% end %>

      <% else: %>

          What's your name? Nüx￶￼

      <% end %>

      ${test('Anna')}
      <% test('Jupp') %>
      """

    _test3 = """
    <div py:def="a"
    
    >
        <div py:def="b">
             Test
        </div>
    </div>
    ${b()}    
    """

    # t = Template(_test)
    t = Template(_test3, html=True, path=r"c:\test.html")
    print t.source.encode("latin1", "ignore")
    print t.render(dict(name='dirk "enzo" holtwick'), encoding="ascii")
