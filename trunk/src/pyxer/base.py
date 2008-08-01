# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

# import pyxer.helpers as h
# import pyxer.model as model

from webob import Request, Response
from webob import exc

import sys
import logging
import string
import mimetypes
import imp
import os
import os.path
import types

from paste.registry import StackedObjectProxy

from pyxer.template import Template
from pyxer.utils.jsonhelper import render_json, json

c = StackedObjectProxy(name="C")
g = StackedObjectProxy(name="G")
g = StackedObjectProxy(name="H")

# cache = StackedObjectProxy(name="Cache")
request = req = StackedObjectProxy(name="Request")
response = resp = StackedObjectProxy(name="Response")
session = StackedObjectProxy(name="Session")

import logging
log = logging.getLogger(__file__)

def abort(code=404):
    raise exc.HTTPNotFound()

def url(url):
    return req.relative_url(url)

# Redirect to other page
def redirect(location, code=301):   
    raise exc.HTTPMovedPermanently(location=url(location))
    
#try:
#    from genshi.template import TemplateLoader
#    
#    genshi_loader = TemplateLoader(
#        os.path.join(os.getcwd(), 'public'),
#        auto_reload=True)
#except:
#    log.exception("Failed loading Genshi")
    
def render(path):
    # path = os.path.join(os.getcwd(), 'public', path)
    log.debug("Loading template %r", path)
    template = Template(file(path, "r").read(), path=path, html=True)
    # print template.source.encode("latin1","ignore")
    return template.render(dict(c=c), encoding="utf8")

    #tmpl = genshi_loader.load(template)
    #return tmpl.generate(c=c).render('xhtml', doctype='xhtml')

# Decorator for controllers
def controller(func):
    func.controller = True
    return func

'''
    def replacement(environ, start_response):
        req = Request(environ)

        # Execute function
        try:
            resp = func(req, **req.urlvars)
            # resp = func(req, **dict(req.params))
        except exc.HTTPException, e:
            resp = e

        # Handle template
        if  isinstance(resp, dict):
            log.debug("apply template on %r", resp)
            filename = os.path.join(
                environ["pyxer.root"],
                os.path.dirname(req.path_info).strip("/"),
                func.__name__) + ".html"

            try:
                resp = render(filename, resp)
            except:
                log.exception("render")

        # Prepare response
        if isinstance(resp, basestring):
            log.debug("create a response of %r", resp[:24])
            resp = Response(body=resp)
        return resp(environ, start_response)
    return replacement
'''

expose = controller
