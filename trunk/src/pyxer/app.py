# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

from webob import Request, Response
from webob import exc

from paste.urlparser import StaticURLParser
from paste.cascade import Cascade
# from paste.cgitb_catcher import CgitbMiddleware
from paste.registry import RegistryManager
from paste.config import ConfigMiddleware #, CONFIG
from paste.exceptions.errormiddleware import ErrorMiddleware
from paste.util.import_string import import_module

import paste.deploy

from pyxer.base import *

import sys
import logging
import string
import mimetypes
import imp
import os
import os.path
import types
import pprint
import site
import zipimport

import logging
log = logging.getLogger(__name__)

# XXX Needed?
# sys.path = [os.getcwd()] + sys.path

'''
class ContextObj(object):
    pass

class PyxerStatic(StaticURLParser):

    # def __call__(self, environ, start_response):
    pass

# The WSGI application
class PyxerApp2(object):

    def __init__(self, base = ["public"]):
        self.base = base

    def __call__(self, environ, start_response):

        try:

            url = environ["PATH_INFO"]

            # Mod Python corrections
            if environ.has_key("SCRIPT_FILENAME"):
                prefix = environ["SCRIPT_FILENAME"][len(environ['DOCUMENT_ROOT']):]
                environ["WSGI_PREFIX"] = prefix
                url = url[len(prefix):]

            # environ["PATH_INFO"] = url
            #environ["SCRIPT_URL"] = url
            # environ["REQUEST_URI"] = url

            # 1/0

            # XXX Ein Punkt wird entwedet als Dateiendung benutzt oder hat sonst im
            # Pfad auch nichts zu suchen, daher direkt weiter an die anderen
            if "." in url:
                abort(404)

            # URL aufsplitten in seine Bestandteile (ohne Slashes)
            parts = [x for x in url.strip("/").split("/") if x]
            # environ["MY_PARTS"] = repr(parts)
            # environ["MY_SYS_PATH"] = repr(sys.path)

            log.debug("Analyzing URL %r with parts %r", url, parts)

            if environ.has_key('paste.registry'):
                environ['paste.registry'].register(request, Request(environ))
                environ['paste.registry'].register(response, Response())
                environ['paste.registry'].register(c, ContextObj())
                if environ.has_key('beaker.session'):
                    environ['paste.registry'].register(session, environ['beaker.session'])
                else:
                    environ['paste.registry'].register(session, None)
                environ['paste.registry'].register(config, environ.get("paste.config", {}))

            #module_parts = parts
            #module_name = ".".join(base + module_parts)
            #exec "import " + module_name
            # log.debug("CWD %r %r", os.getcwd(), sys.path)

            if 1:

                try:

                    # Handelt es sich um ein "Verzeichnis"
                    module_parts = parts
                    module_name = ".".join(self.base + module_parts)
                    exec("import " + module_name)
                    # __import__(module_name)
                    action = "index"

                    # We need to add the trailing slash so relative URL's
                    # work fine with the output
                    if not url.endswith("/"):
                        redirect(url + "/")

                except ImportError, msg:

                    # Wenn im Import selbst ein Fehler auftritt dann sieht es so aus
                    # als gäbe es die Datei nicht, das ist allerdings nicht wahr,
                    # daher nochmal dieser Check
                    log.debug("Import error %r for module name %r", msg, module_name)
                    if module_parts and (not (str(msg).endswith("." + module_parts[ - 1]) or str(msg).endswith(" " + module_parts[ - 1]))):
                        log.exception("Error in import")
                        raise

                    try:

                        # oder eine "Datei"
                        module_parts = parts[: - 1]
                        module_name = ".".join(self.base + module_parts)
                        exec("import " + module_name)
                        # __import__(module_name)
                        action = parts[ - 1]
                    except ImportError, msg:
                        # raise Exception, "Import error %r for module name %r" % (msg, module_name)
                        log.debug("Import error %r for module name %r", msg, module_name)
                        abort(404)

                # Modul nochmal aus der Liste fischen, weil __import__ nicht das
                # richtige Modul zurückgibt
                module = sys.modules[module_name]

                # XXX Nochmal laden im Debug-Modus
                module = reload(module)

                log.debug("%s", pprint.pformat(environ))

                # Does the module exist?
                if module:
                    log.debug("Module found: %r, Action: %r", module, action)

                    # Does the function exist?
                    func = getattr(module, action, None)
                    name = action

                    if not func:
                        # Test for 'default'
                        action = "default"
                        func = getattr(module, action, None)

                    if func:

                        # Is it a controller?
                        if isController(func):

                            # Calculate path of corresponding template file
                            #if module_parts:
                            #    request.template_url = "/".join(module_parts) + "/" + action + ".html"
                            #request.template_url = action + ".html"

                            request.start_response = start_response
                            request.template_url = os.path.join(os.path.dirname(module.__file__), name + ".html")

                            return func()

                        else:
                            # raise Exception, "Function %r is not a controller" % func
                            log.debug("Function %r is not a controller", func)
                    else:
                        # raise Exception, "Could not find action %r" % action
                        log.debug("Could not find action %r", action)

                # Weiter geben zum nächsten WSGI Handler
                abort(404)

        # Handle HTTPException
        except exc.HTTPException, e:
            return e(environ, start_response)
'''

# The WSGI application
class PyxerApp(Router):

    def __init__(self, base = "public"):
        Router.__init__(self, base)
        self.base = base

    def __call__(self, environ, start_response):

        try:

            path = environ["PATH_INFO"]

            # Mod Python corrections
            if environ.has_key("SCRIPT_FILENAME"):
                prefix = environ["SCRIPT_FILENAME"][len(environ['DOCUMENT_ROOT']):]
                environ["WSGI_PREFIX"] = prefix
                path = path[len(prefix):]

            log.debug("Try matching %r", path)
            obj, vars = self.match(path)
            log.debug("For %r found %r with %r", path, obj, vars)

            # No matching
            if obj is None:
                abort(404)

            # Set globals
            if environ.has_key('paste.registry'):
                environ['paste.registry'].register(request, Request(environ))
                environ['paste.registry'].register(response, Response())
                environ['paste.registry'].register(c, AttrDict())
                if environ.has_key('beaker.session'):
                    environ['paste.registry'].register(session, environ['beaker.session'])
                else:
                    environ['paste.registry'].register(session, None)
                environ['paste.registry'].register(config, environ.get("paste.config", {}))

            request.start_response = start_response
            
            # Guess template name     
            name = None       
            if vars["controller"] == "default":
                if path.endswith("/"):
                    name = "index"
                else:
                    name = vars["pyxer.match"]
            elif isinstance(vars["controller"], basestring):
                name = vars["controller"]
            
            # and path
            request.template_url = None
            if name is not None:            
                tpath =  os.path.join(vars["pyxer.path"], name + ".html")
                if os.path.isfile(tpath):
                    request.template_url = tpath
                
            request.urlvars = vars
            environ['pyxer.urlvars'] = vars
            
            environ['pyxer.urlbase'] = path[:-(len(vars["pyxer.match"]) + len(vars["pyxer.tail"]))]
            # log.info("******* %r %r %r", path, vars["pyxer.match"],  environ['pyxer.urlbase'])

            return obj()
            # obj(environ, start_response)

        # Handle HTTPException
        except exc.HTTPException, e:
            return e(environ, start_response)

# Sessions available?
SessionMiddleware = None
try:
    from beaker.middleware import SessionMiddleware
    log.debug("Beaker successfully loaded")
except ImportError:
    log.debug("Beaker NOT loaded")

# Make WSGI application, wrapping sessions etc.
def make_app(global_conf = {}, **app_conf):

    #pprint.pprint(global_conf)
    #pprint.pprint(app_conf)

    conf = AttrDict(pyxer = {
        "session": "",
        "debug": False,
        "root": "public",
        })
    root = os.getcwd()
    try:
        import ConfigParser
        filename = os.path.abspath(global_conf.get("__file__")) or os.path.abspath("pyxer.ini" )
        root = os.path.dirname(filename)
        cfile = ConfigParser.SafeConfigParser()
        cfile.read(filename)
        for section in cfile.sections():
            if not conf.has_key(section):
                conf[section] = AttrDict()
            try:
                for name, value in cfile.items(section):
                    conf[section][name] = value
            except:
                log.exception("Config items")
        log.debug("Config: %r", conf)
    except:
        log.exception("Config file not found")

    # Add current directory to sys path
    site.addsitedir(root)

    # Here we expect all data
    base = os.path.join(root, "public")

    # app = App(global_conf=None, root="public", path=None, **app_conf)
    app = PyxerApp()

    if SessionMiddleware and (conf.get("pyxer.session", "beaker") == "beaker"):
        log.debug("Beaker sessions")
        if "google.appengine" in sys.modules:
            app = SessionMiddleware(app, type = 'google', table_name = 'PyxerSession')
        else:
            app = SessionMiddleware(app, type = 'dbm', data_dir =  os.path.join(root, 'cache'))

    app = RegistryManager(app)
    app = ConfigMiddleware(app, conf.copy())

    # app = CgitbMiddleware(app)
    app = ErrorMiddleware(app, debug = True)

    #static = PyxerStatic(base)
    #app = Cascade([app, static])

    return app

# Paster EGG factory entry 
def app_factory(global_config, **local_conf):
    return make_app(global_config)

# Serve with Python on board WSGI
def serve(opt = {}):
    print "Serving on http://%s:%s" % (opt.host, opt.port)
    from wsgiref.simple_server import make_server
    server = make_server(opt.host, int(opt.port), make_app())
    server.serve_forever()

if __name__ == "__main__":
    class opt:
        host = "127.0.0.1"
        port = 8080
    serve(opt)
