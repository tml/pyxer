# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

from webob import Request
from webob import exc

from pyxer.controller import \
    Controller, isController, c, g, h, config, \
    session, response, request, resp, req

import re
import urllib
import copy
import sys
import types
import os
import os.path

import paste.fileapp

def static():
    filename = os.path.join(req.urlvars["pyxer.path"], req.urlvars["static"])
    return paste.fileapp.FileApp(filename)(request.environ, request.start_response)

static.app = True

var_regex = re.compile(r'''
    \{              # The exact character "{"
    (\w+)           # The variable name (restricted to a-z, 0-9, _)
    (?::([^}]+))?   # The optional :regex part
    \}              # The exact character "}"
    ''', re.VERBOSE)

def template_to_regex(template):
    regex = ''
    last_pos = 0
    for match in var_regex.finditer(template):
        regex += re.escape(template[last_pos:match.start()])
        var_name = match.group(1)
        expr = match.group(2) or '[^/]+'
        expr = '(?P<%s>%s)' % (var_name, expr)
        regex += expr
        last_pos = match.end()
    regex += re.escape(template[last_pos:])
    regex = '^%s$' % regex
    return regex

'''
def url(*segments, **vars):
    base_url = get_request().application_url
    path = '/'.join(str(s) for s in segments)
    if not path.startswith('/'):
        path = '/' + path
    if vars:
        path += '?' + urllib.urlencode(vars)
    return base_url + path
'''

class RouteObject(object):

    def __init__(self,
            template,
            module = None,
            controller = None,
            name = None,
            vars = {}):
        self.template = re.compile(template) #template_to_regex
        self.module = module
        self.controller = controller
        self.name = name
        self.vars = copy.copy(vars)
        self.vars["controller"] = self.controller
        self.vars["module"] = self.module

    def __repr__(self):
        return "<RouteObject '%s'; pattern '%s'>" % (
            self.name, self.template.pattern)

    __str__ = __repr__

class Router(object):

    def __init__(self, module = None, prefix = "", use_default = True):
        self.module = None
        self.module_name = None
        self.prefix = prefix
        self.routes = []
        self.routes_default = []
        self.set_module(module)

        # Default routings
        if use_default:
            # /
            self.add_default("^$",
                controller = "index",
                name = "_action_index")
            # /demo
            # /demo.html
            self.add_default("^(?P<controller>[^\/\.]+?)(\.html?)?$",
                name = "_action")
            # /demo/
            self.add_default("^(?P<module>[^\/\.]+?)\/",
                name = "_module")
            # demo.py
            self.add_default("^[^\/\.]+?\.(py[co]?)$",
                name = "_ignore_py")
            # demo.xyz
            self.add_default("^(?P<static>[^\/\.]+?\.[^\/\.]+?)$",
                controller = "static",
                name = "_static")
            # demo.xyz.abc
            self.add_default(".*",
                controller = "default",
                name = "_action_default")
            # demo.xyz
            self.add_default("^(?P<static>.*?)$",
                controller = "static",
                name = "_static")

    def set_module(self, module = None):
        if module is not None:
            if isinstance(module, basestring):
                self.module = self.load_module(module)
            else:
                self.module = module
            self.module_name = self.module.__name__

    def load_module(self, *names):
        name = ".".join(names)
        # print "load module:", name
        if sys.modules.has_key(name):
            return sys.modules[name]
        try:
            __import__(name)
        except ImportError:
            return None
        module = sys.modules[name]
        return module

    def load_object(self, name):
        return module

#...     name, func_name = string.split(':', 1)
#...     __import__(name)
#...     module = sys.modules[name]
#...     func = getattr(module, func_name)
#...     return func

    def add(self, template, **kw):
        #if isinstance(controller, basestring):
        #    controller = load_controller(controller)
        self.routes.append(RouteObject(template_to_regex(template), **kw))

    def add_re(self, template, **kw):
        self.routes.append(RouteObject(template, **kw))

    def add_default(self, template, **kw):
        self.routes_default.append(RouteObject(template, **kw))

    def match(self, path):
        if path.startswith("/"):
            path = path[1:]
        obj, vars = self._match(path)
        return obj, vars

    def _match(self, path, module = None, urlvars = {}):
        # Normalize module infos
        self.set_module(module)
        # Search
        for route in self.routes + self.routes_default:
            match = route.template.match(path)
            # print "  ?", route, match
            if match:
                urlvars = {}
                urlvars.update(route.vars)
                urlvars.update(match.groupdict())
                tail = path[match.end():].lstrip("/")
                urlvars["pyxer.tail"] = tail
                urlvars["pyxer.path"] = os.path.dirname(os.path.abspath(self.module.__file__))

                # print "->", path, route, urlvars, route.vars

                if urlvars["module"] is not None:
                    obj = urlvars["module"]

                    # If it is a module go ahead
                    if isinstance(obj, types.ModuleType):
                        module = obj

                    # If it is a string it could be a module or a
                    elif isinstance(obj, basestring):

                        # Load module relatively or absolute
                        module = (
                            self.load_module(self.module_name, obj)
                            or self.load_module(obj))

                        if module is None:
                            continue

                    # If it is anything else, let the caller decide what to do
                    else:
                        raise Exception("No module")

                    # Let's see if they need a Router()
                    if not hasattr(module, "router"):
                        module.router = Router(module)

                    # The router goes to the next round
                    return module.router._match(tail, module) #, urlvars)

                # A controller
                if urlvars["controller"] is not None:
                    obj = urlvars["controller"]
                    if hasattr(self.module, obj):
                        return getattr(self.module, obj), urlvars
                    continue

        return (None, None)

"""
- urlvars nicht bei modulen möglich, oder doch z.B. für sprachen?
- subdomain ermöglichen, z.b. für sprachwechsel?
- genaues macthing nicht test -> test/
- '' oder '*' einführen, steht nur alleine und heisst: der gnaze rest
- umleitung zu default static oder als parameter? ('', static)
- url_for equivalent
- benannte url schemata
- module, controller, action heissen alle object und können auch strings sein
- explizite actions in den urlvars {action:*}
- redirects, auch zu großen domains: ('google', redirect('google.com')
- auf für fehler error(404)
"""

def test():
    from pyxer.controller import getObjectsFullName, isController

    static = "pyxer.routing:static"

    if __name__=="__main__":
        module = "__main__"
    else:
        module = "pyxer.routing"

    data = [
        ("",                            "public:index"),
        ("index",                       "public:index"),
        ("/index",                       "public:index"),
        ("index.htm",                   "public:index"),
        ("index.html",                  "public:index"),
        ("index.gif",                   "pyxer.routing:static", dict(static="index.gif")),
        ("sub1",                        'pyxer.routing:static', {'static': 'sub1'}),
        ("sub1/",                       "public.sub1:index"),
        ("sub1/dummy",                  "public.sub1:dummy"),
        ("sub1/dummy2",                 "public.sub1:default"),
        ("sub1/content1",               "public.sub1:content1"),
        ("sub1/content1/some",          "public.sub1:content1", dict(name="some")),
        ("sub1/content2/some",          "public.sub1:content2", dict(name="some")),
        ("sub1/content1/some/more",     "public.sub1:content1", dict(name="some/more")),
        ("sub1/content2/some/more",     "public.sub1:default", dict()),
        ("/some/path/index.gif",        "pyxer.routing:static", dict(static="some/path/index.gif")),
        #"hans/peter",
        #"hans.gif",
        #"hans.htm",
        #"hans.html",
        #"",
        #"quatsch.mit.sosse",
        #"wiki/content/some",
        #"wiki/commit",
        ]

    router = Router("public")
    for sample in data:
        if len(sample)==3:
            path, object_name, object_vars = sample
        else:
            path, object_name = sample
            object_vars = dict()

        obj, vars = router.match(path)
        if vars is None:
            vars = dict()
        else:
            vars.pop("controller")
            vars.pop("module")
            vars.pop("pyxer.tail")
            vars.pop("pyxer.path")
        name = getObjectsFullName(obj)
        ct = isController(obj)
        print "%-35r %r, %r" % (path, name, vars)
        assert object_name == name
        assert object_vars == vars

if __name__ == "__main__":
    import sys
    import os.path
    sys.path.insert(0, os.path.join(__file__, "..", "..", "..", "tests"))
    test()

    '''
    print template_to_regex('/a/static/path')
    print template_to_regex('/{year:\d\d\d\d}/{month:\d\d}/{slug}')

    route('/', controller='controllers:index')
    route('/{year:\d\d\d\d}/',
                  controller='controllers:archive')
    route('/{year:\d\d\d\d}/{month:\d\d}/',
                  controller='controllers:archive')
    route('/{year:\d\d\d\d}/{month:\d\d}/{slug}',
                  controller='controllers:view')
    route('/post', controller='controllers:post')
    '''
