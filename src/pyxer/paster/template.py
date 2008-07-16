# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

"""
TODO:

- Auch Dateien mit bestimmten Endungen müssen hier durchlaufen
  können, damit z.B. auth angewendet werden kann. Datei könnte
  von backoffice.js auf backoffice_js gemappt werden
- Ganze Verzeichnisse sollten gesichert werden können
- url() sollte absolute Pfade erstellen können
- Erst in sys.modules nachsehen, dann __import__
- params = Dict(request.params, include=['name']) => params.name
- @json oder @controller(return="json") genshi, cvs, excel, file
- @auth oder @controller(auth=['admin'])
"""

from pics4nuts.lib.base import *

import sys
import types
import threading

import logging
log = logging.getLogger(__name__)

class TemplateController(BaseController):

    def view(self, url):
        """By default, the final controller tried to fulfill the request
        when no other routes match. It may be used to display a template
        when all else fails, e.g.::

            def view(self, url):
                return render('/%s' % url)

        Or if you're using Mako and want to explicitly send a 404 (Not
        Found) response code when the requested template doesn't exist::

            import mako.exceptions

            def view(self, url):
                try:
                    return render('/%s' % url)
                except mako.exceptions.TopLevelLookupException:
                    abort(404)

        By default this controller aborts the request with a 404 (Not
        Found)
        """
        
        # XXX Ein Punkt wird entwedet als Dateiendung benutzt oder hat sonst im
        # Pfad auch nichts zu suchen, daher direkt weiter an die anderen 
        if "." in url:
            abort(404)
        
        # XXX Basis des Moduls
        base = ["pics4nuts", "public"]
        
        # URL aufsplitten in seine Bestandteile (ohne Slashes)
        parts = [x for x in url.strip("/").split("/") if x]
        
        # print parts

        # Die Hardcore URL besorgen mit allem drum und dran
        url = request.environ["PATH_INFO"]
        # print request.environ, dir(request)

        log.debug("Analyzing URL %r with parts %r", url, parts)

        #module_parts = parts
        #module_name = ".".join(base + module_parts)            
        #exec "import " + module_name
        try:  
            
            # Handelt es sich um ein "Verzeichnis"            
            module_parts = parts
            module_name = ".".join(base + module_parts)            
            __import__(module_name)
            action = "index"            
             
            # Relative Dateien bekommen Probleme wenn das "Verzeichnis" keinen
            # abschließenden Slash hat 
            if not url.endswith("/"):                
                redirect(url + "/", _code=303)
                
        except ImportError, msg:
            
            # Wenn im Import selbst ein Fehler auftritt dann sieht es so aus
            # als gäbe es die Datei nicht, das ist allerdings nicht wahr, 
            # daher nochmal dieser Check
            log.debug("Import error %r for module name %r", msg, module_name)
            if not (msg[0].endswith("." + module_parts[-1]) or msg[0].endswith(" " + module_parts[-1])):
                log.exception("Error in import")
                raise 
                        
            try:
                
                # oder eine "Datei"
                module_parts = parts[:-1]
                module_name = ".".join(base + module_parts)
                __import__(module_name)
                action = parts[-1]
            except ImportError:
                # print module_name
                abort(404)
        
        # Modul nochmal aus der Liste fischen, weil __import__ nicht das
        # richtige Modul zurückgibt
        module = sys.modules[module_name]
        
        # XXX Nochmal laden im Debug-Modus  
        module = reload(module)
        #print module
                
        request.template_url = ".".join(module_parts) + "." + action  
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
                    # Wenn das Ergebnis None ist, dann das passende Template rendern
                    # XXX Besser testen ob schon was im Body ist! response.body ... .body_file
                    if result is None:
                        log.debug("Render with default template %r", request.template_url)
                        result = render(request.template_url)
                    # Listen und Hashes werden als JSON zurück gegeben
                    elif type(result) in (types.ListType, types.DictionaryType, types.DictType, types):
                        import simplejson
                        response.headers['Content-Type'] = 'application/json'
                        result = simplejson.dumps(result)                
                    # Ergebnisstring ausgeben
                    return result
                else:
                    log.debug("Function %r is not a controller", func)
            else:
                log.debug("Could not find action %r", action)
        
        # Weiter geben zum nächsten WSGI Handler      
        abort(404)
