# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

# import pyxer.helpers as h
# import pyxer.model as model

from webob import exc

import sys
import logging
import string
import mimetypes
import imp
import os
import os.path
import types

GAE = "google.appengine" in sys.modules

from pyxer.utils import Dict, AttrDict
from pyxer.utils.jsonhelper import json
from pyxer.controller import \
    Controller, isController, c, g, h, config, \
    session, response, request, resp, req

import logging
log = logging.getLogger(__file__)

def url(url):
    " Normalize URL "
    return request.relative_url(url)

def redirect(location, code = 301):
    " Redirect to other page "   
    # .exeception for Python 2.3 compatibility
    raise exc.HTTPMovedPermanently(location = url(location)).exception

def abort(code = 404):
    " Abort with error "
    # .exeception for Python 2.3 compatibility
    raise exc.HTTPNotFound().exception

class StreamTemplateManager:
    
    cache = {}
    
    def __init__(self, root):    
        self.root = root
    
    def load(self, path):        
        import pyxer.template as pyxer_template 
        pyxer_template = reload(pyxer_template)        
        path = os.path.abspath(os.path.join(self.root, path))
        # Test if it is in cache and return if found
        mtime = os.path.getmtime(path)
        if 0 and self.cache.has_key(path):            
            template, last = self.cache.get(path)            
            if mtime <= last:                
                return template
            else:
                log.debug("Found a newer file than the one in the cache for %r", path)
        # Load the template       
        log.debug("Loading template %r in KidTemplateManager", path)
        template = pyxer_template.TemplateSoup(
            file(path, "r").read())       
        template.load = self.load         
        self.cache[path] = (template, mtime)
        return template      

def template_stream(name = None):
    " Get the template "    
    # XXX What to do with dirname? Scenarios?
    # XXX What to do with absolute url /like/this?
    path = request.template_url
    dirname = os.path.dirname(path)
    if name is not None:
        path = os.path.join(dirname, name)
        dirname = os.path.dirname(path)
    log.debug("Loading template %r", path)
    soup_manager = StreamTemplateManager(dirname)    
    return soup_manager.load(path)

template = template_default = template_stream

def render_stream(*kw):
    template = template_stream()    
    template.generate(Dict(c = c, h = Dict(
        url = url,
        redirect = redirect
        ), load = template.load))
    return template.render()

render_default = render_stream

def render_json():
    " Render output as JSON object "
    response.headers['Content-Type'] = 'application/json'
    result = json(request.result)    
    # log.debug("JSON: %r", result)
    return result

class controller(Controller):
 
    def render(self, result, render = None, **kw):

        log.debug("Render called with %r %r %r", repr(result)[:40], render, kw)
        # log.debug("Render called with %r %r", render, kw)
        
        # Choose a renderer
        render_func = None
        
        # Render is explicitly defined by @controller
        if render is not None:
            render_func = render

        # If the result is None (same as no return in function at all)
        # then apply the corresponding template
        # XXX Maybe better test if response.body/body_file is also empty
        elif result is None:
            render_func = render_default                            

        # Consider dict and list as JSON data
        elif isinstance(result, dict) or isinstance(result, list):
            render_func = render_json
        
        # Execute render function
        log.debug("Render func %r", render_func)
        if render_func is not None:           
            request.result = result            
            log.debug("Render with func %r", render_func)
            result = render_func(**kw)                            

            # Normalize output
            # if (not None) and (not isinstance(result, str)) and (not isinstance(result, str)):
            #    result = str(result)

        return result

class expose(controller):
    
    def call(self, *a, **kw):
        " Add arguments "
        log.debug("Call func with params %r", dict(request.params))
        return self.func(**dict(request.params))

# Routing

from webob import Request
from webob import exc

class Router(object):

    def __init__(self):
        self.routes = []

    def add_route(self, template, controller, **vars):
        if isinstance(controller, basestring):
            controller = load_controller(controller)
        self.routes.append((re.compile(template_to_regex(template)),
                            controller,
                            vars))

    def __call__(self, environ, start_response):
        req = Request(environ)
        for regex, controller, vars in self.routes:
            match = regex.match(req.path_info)
            if match:
                req.urlvars = match.groupdict()
                req.urlvars.update(vars)
                return controller(environ, start_response)
        return exc.HTTPNotFound()(environ, start_response)

class Permission(object):
    
    """
    @controller(permission=Permission('read'))
    """
    
    def __init__(self, permission):
        self.permission
        
    def __call__(self, permissions):
        if isinstance(permissions, basestring):
            permissions = [permissions]        
        return self.permission in permissions