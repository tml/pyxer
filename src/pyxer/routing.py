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

import paste.fileapp

def static(filename):
    return paste.fileapp.FileApp(filename)

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
            object = None,
            name = None,
            vars = {}):
        self.template = re.compile(template) #template_to_regex
        self.object = object
        self.name = name
        self.vars = vars
        self.vars["object"] = self.object

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
                object = "index",
                name = "_action_index")
            # /demo
            # /demo.html
            self.add_default("^(?P<object>[^\/\.]+?)(\.html?)?$",
                name = "_action")
            # /demo/
            self.add_default("^(?P<object>[^\/\.]+?)\/",
                name = "_module")
            # demo.py
            self.add_default("^[^\/\.]+?\.(py[co]?)$",
                name = "_ignore_py")
            # demo.xyz
            self.add_default("^[^\/\.]+?\.[^\/\.]+?$",
                object = static,
                name = "_static")
            # demo.xyz.abc
            self.add_default(".*",
                object = "default",
                name = "_action_default")

    def set_module(self, module = None):
        if module is not None:
            if isinstance(module, basestring):
                self.module = sys.modules[module]
            else:
                self.module = module
            self.module_name = self.module.__name__

    def load_module(self, name):
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

    def match(self, path, module = None, urlvars = {}):
        # Normalize module infos
        self.set_module(module)
        # Search        
        print "path:", path
        for route in self.routes + self.routes_default:
            print "?", route
            match = route.template.match(path)
            if match:
                urlvars.update(copy.copy(match.groupdict()))
                if urlvars.has_key("object"):
                    obj = urlvars["object"]                    
                    if isinstance(obj, types.ModuleType):
                        module = obj
                    else:
                        module = (self.load_module(obj) 
                            or self.load_module(self.module_name + obj))
                    if module is None:
                        if hasattr(self.module, obj):
                            return getattr(self.module, obj), urlvars
                    else:
                        if not hasattr(module, "router"):
                            module.router = Router(module)
                        tail = path[match.end():].lstrip("/")
                        return module.router.match(tail, module) #, urlvars)
                # urlvars.update(route.vars)
                # return (route, urlvars)
        return None

    def __call__(self, environ, start_response):
        req = Request(environ)
        for regex, controller, vars in self.routes:
            match = regex.match(req.path_info)
            if match:
                req.urlvars = match.groupdict()
                req.urlvars.update(vars)
                print controller
                # return controller(environ, start_response)
                return []
        return exc.HTTPNotFound()(environ, start_response)

"""
- keine vorgaben für urlvars
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

if __name__ == "__main__":

    import sys
    sys.path.insert(0, "../../example")

    import public
    import public.wiki

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

    static = "*static"

    router = Router(public)

    tests = [
        #"hans",
        #"hans/",
        #"hans/peter",
        #"hans.gif",
        #"hans.htm",
        #"hans.html",
        "",
        #"quatsch.mit.sosse",
        "wiki/content/some",
        "wiki/commit",
        ]

    for path in tests:
        print "%-20s %s" % (path, router.match(path))
