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

from pyxer.utils.jsonhelper import json
from pyxer.controller import Controller, isController, c, g, h, session, response, request, resp, req

import logging
log = logging.getLogger(__file__)

# Abort with error 
def abort(code=404):
    raise exc.HTTPNotFound()

# Normalize URL
def url(url):
    return req.relative_url(url)

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

def render_kid(**kw):
    " 'c' and 'request' are global variables " 
    import pyxer.kid as kid
    path = request.template_url    
    # Force output to be something that makes sense ;)
    if "output" not in kw:
        kw["output"] = "xhtml-strict"
    log.debug("Loading template %r with Kid and arguments %r", path, kw)
    template = kid.Template(source=file(path, "r").read(), c=c)
    return template.serialize(**kw)

# Make Kid the default templating language
render_default = render_kid

def render_json():
    " Render output as JSON object "
    response.headers['Content-Type'] = 'application/json'
    result = json(request.result)    
    log.debug("JSON: %r", result)
    return result

class controller(Controller):

    def render(self, result, render=None, **kw):

        log.debug("Render called with %r %r %r", result, render, kw)
        
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

        # Consider everything which is not a string as JSON data
        elif type(result) not in types.StringTypes:
            render_func = render_json
        
        # Execute render function
        log.debug("Render func %r", render_func)
        if render_func is not None:           
            request.result = result            
            log.debug("Render with func %r", render_func)
            result = render_func(**kw)                            

        return result

expose = controller
