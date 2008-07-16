#!/bin/python2.5
# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 103 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2007-10-31 17:08:54 +0100 (Mi, 31 Okt 2007) $"
__svnid__   = "$Id: pisa.py 103 2007-10-31 16:08:54Z holtwick $"

from webob import Request, Response
from webob import exc

from paste.urlparser import StaticURLParser
from paste.cascade import Cascade
from paste.cgitb_catcher import CgitbMiddleware
from paste.registry import RegistryManager
from paste.config import ConfigMiddleware, CONFIG

from paste.util.import_string import import_module

from pyxer.base import *

#from mako.template import Template
#from mako.runtime import Context

import sys
import logging
import string
import mimetypes
import imp
import os
import os.path
import types
import pprint

import logging
log = logging.getLogger(__file__)

sys.path = [os.getcwd()] + sys.path

class ContextObj(object):
    pass

# The WSGI application
class PyxerApp(object):

    def __call__(self, environ, start_response):

        try:
                            
            url = environ["PATH_INFO"]
            
            # XXX Ein Punkt wird entwedet als Dateiendung benutzt oder hat sonst im
            # Pfad auch nichts zu suchen, daher direkt weiter an die anderen 
            if "." in url:
                abort(404)
            
            # XXX Basis des Moduls
            base = ["public"]
            
            # URL aufsplitten in seine Bestandteile (ohne Slashes)
            parts = [x for x in url.strip("/").split("/") if x]
            
            log.debug("Analyzing URL %r with parts %r", url, parts)
    
            if environ.has_key('paste.registry'):
                environ['paste.registry'].register(request, Request(environ))
                environ['paste.registry'].register(response, Response())
                environ['paste.registry'].register(c, ContextObj())
                if environ.has_key('beaker.session'):                    
                    environ['paste.registry'].register(session, environ['beaker.session'])
                
            #module_parts = parts
            #module_name = ".".join(base + module_parts)            
            #exec "import " + module_name
            # log.debug("CWD %r %r", os.getcwd(), sys.path)
            try:  
                
                # Handelt es sich um ein "Verzeichnis"            
                module_parts = parts
                module_name = ".".join(base + module_parts)
                exec("import " + module_name)            
                # __import__(module_name)
                action = "index"            
                 
                # Relative Dateien bekommen Probleme wenn das "Verzeichnis" keinen
                # abschließenden Slash hat 
                if not url.endswith("/"):                
                    redirect(url + "/")
                    
            except ImportError, msg:
                
                # Wenn im Import selbst ein Fehler auftritt dann sieht es so aus
                # als gäbe es die Datei nicht, das ist allerdings nicht wahr, 
                # daher nochmal dieser Check
                log.debug("Import error %r for module name %r", msg, module_name)
                if not (str(msg).endswith("." + module_parts[-1]) or str(msg).endswith(" " + module_parts[-1])):
                    log.exception("Error in import")
                    raise 
                            
                try:
                    
                    # oder eine "Datei"
                    module_parts = parts[:-1]
                    module_name = ".".join(base + module_parts)
                    exec("import " + module_name)
                    # __import__(module_name)
                    action = parts[-1]
                except ImportError, msg:
                    log.debug("Import error %r for module name %r", msg, module_name)
                    abort(404)
            
            # Modul nochmal aus der Liste fischen, weil __import__ nicht das
            # richtige Modul zurückgibt
            module = sys.modules[module_name]
            
            # XXX Nochmal laden im Debug-Modus  
            module = reload(module)
            
            pprint.pprint(environ)

            request.template_url = "/".join(module_parts) + "/" + action + ".html"                      
            # request.template_url = "/".join(module_parts) + "/" + action + ".html" 
            #print request.template_url 
            
            # Esistiert das Modul?
            if module:
                log.debug("Module found: %r, Action: %r", module, action)
    
                # Existiert die Aktion/ Funktion?
                func = getattr(module, action, None)
                if func:
                    
                    # Handelt es sich um einen Controller?
                    if getattr(func, "controller", False) is True:
                        result = func()
                        
                        # If the result is None (same as no return in function at all)
                        # then apply the corresponding template                        
                        # XXX Maybe better test if response.body/body_file is also empty 
                        if result is None:
                            log.debug("Render with default template %r", request.template_url)    
                            vars = ContextObj()
                            vars.c = c
                            result = render(request.template_url)
                                                
                        # Consider lists and hashes as JSON data
                        elif type(result) in (types.ListType, types.DictionaryType, types.DictType, types):
                            response.headers['Content-Type'] = 'application/json'
                            try:
                                import jsonlib
                                result = jsonlib.write(result)
                            except ImportError:
                                try:
                                    import simplejson                                
                                    result = simplejson.dumps(result)
                                except ImportError:
                                    import utils.jsonhelper
                                    result = utils.jsonhelper.write(result)
                        # Ergebnisstring ausgeben
                        resp.body = result
                        return resp(environ, start_response)                    
                    else:
                        log.debug("Function %r is not a controller", func)
                else:
                    log.debug("Could not find action %r", action)
            
            # Weiter geben zum nächsten WSGI Handler      
            abort(404)
        
        # Handle HTTPException
        except exc.HTTPException, e:
            return e(environ, start_response)

# Sessions available?
try:
    from beaker.middleware import SessionMiddleware
except:
    SessionMiddleware = None

# Make WSGI application, wrapping sessions etc.
def make_app(global_conf={}, root="public", path=None, **app_conf):
    
    pprint.pprint(global_conf)
    pprint.pprint(app_conf)
    
    base = os.path.join(os.getcwd(), "public")
    # app = App(global_conf=None, root="public", path=None, **app_conf)
    app = PyxerApp()
    if SessionMiddleware:
        log.debug("Beaker sessions")
        app = SessionMiddleware(app, type='dbm', data_dir='./cache')
        
    app = RegistryManager(app)
    
    #conf = global_conf.copy()
    #conf.update(app_conf)
    #conf.update(dict(app_conf=app_conf, global_conf=global_conf))
    # CONFIG.push_process_config(conf)
    #app = ConfigMiddleware(app, conf)
    
    # app = CgitbMiddleware(app)
    static = StaticURLParser(base)
    app = Cascade([app, static])
    return app

# Paster EGG factory entry
def app_factory(global_config, **local_conf):
    return make_app(global_config)

# Serve with Python on board WSGI
def serve(opt={}):
    print "serving on http://%s:%s" % (opt.host, opt.port)
    from wsgiref.simple_server import make_server
    server = make_server(opt.host, int(opt.port), make_app())
    server.serve_forever()

if __name__=="__main__":
    class opt:
        host = "127.0.0.1"
        port = 8080
    serve(opt)
