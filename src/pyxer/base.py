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

from pyxer.utils import Dict
from pyxer.utils.jsonhelper import json
from pyxer.controller import Controller, isController, c, g, h, config, session, response, request, resp, req

import logging
log = logging.getLogger(__file__)

# Abort with error 
def abort(code=404):
    raise exc.HTTPNotFound()

# Normalize URL
def url(url):
    return request.relative_url(url)

# Redirect to other page
def redirect(location, code=301):   
    raise exc.HTTPMovedPermanently(location=url(location))

def render_pyxer(*kw):
    import pyxer.template
    path = request.template_url
    # path = os.path.join(os.getcwd(), 'public', path)
    log.debug("Loading template %r", path)
    template = pyxer.template.Template(file(path, "r").read(), path=path, html=True)
    # print template.source.encode("latin1","ignore")
    return template.render(dict(c=c), encoding="utf8")

    #tmpl = genshi_loader.load(template)
    #return tmpl.generate(c=c).render('xhtml', doctype='xhtml')


class SoupTemplateManager:
    
    cache = {}
    
    def __init__(self, root):    
        self.root = root
    
    def load(self, path):        
        import pyxer.template as pyxer_template 
        pyxer_template = reload(pyxer_template)
        #if path.startswith("/"):
        #    path = path.lstrip("/")
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
        self.cache[path] = (template, mtime)
        return template      

def render_soup(*kw):    
    path = request.template_url
    # path = os.path.join(os.getcwd(), 'public', path)
    log.debug("Loading template %r", path)
    soup_manager = SoupTemplateManager(os.path.dirname(path))
    template = soup_manager.load(path)        
    # template = pyxer_template.TemplateSoup(file(path, "r").read())
    # print template.source.encode("latin1","ignore")
    # log.debug("%s", template.sourcecode)
    soup = template.render(dict(c=c, h=Dict(
        url=url,
        redirect=redirect
        ), load=soup_manager.load), encoding="utf8")
    return str(soup)

class KidTemplateManager:
    
    cache = {}
    
    def __init__(self, root):    
        self.root = root
    
    def load(self, path):
        import  kid
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
        template = kid.load_template(
            path, cache=False,
            ns=dict(load=self.load, c=c))  
        self.cache[path] = (template, mtime)
        return template        
           
def render_kid(**kw):
    " 'c' and 'request' are global variables " 
    # import pyxer.kid as kid
    path = request.template_url    
    # Force output to be something that makes sense ;)
    if "output" not in kw:
        kw["output"] = "xhtml-strict"
    log.debug("Loading template %r with Kid and arguments %r", path, kw)
    template = KidTemplateManager(os.path.dirname(path)).load(path)    
    # template = kid.Template(source=file(path, "r").read(), c=c, load=kid_loader)
    return template.serialize(**kw)

# Make Kid the default templating language
render_default = render_soup
# render_default = render_pyxer

def render_json():
    " Render output as JSON object "
    response.headers['Content-Type'] = 'application/json'
    result = json(request.result)    
    # log.debug("JSON: %r", result)
    return result

class controller(Controller):
 
    def render(self, result, render=None, **kw):

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
    
# XXX Parameters

def getparams(*a, **kw):
    """
    a, b = getparams("a b")
    a, b = getparams("a", "b")
    # a, b = getparams(["a", "b"])
    # a, b = getparams(a=1, b=2)
    # a, b = getparams("a", b=2)
    
    But not (because of order of elements):
    a, b = getparams({"a": 1, "b": 2})    
    """
    values = []
    for name in [x.strip().split() for x in a]:
        request.params.get(name, None)

"""
from inspect import *

def f(**kw):
    locals_ = currentframe().f_back.f_locals
    for k, v in kw.items():
        locals_[k] = v

f(a=1, b=1, c=1, d=1, x=1, e=2)
print a,b,c,d,e,x
"""       