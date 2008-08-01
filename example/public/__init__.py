# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

from pyxer.base import *

import logging
log = logging.getLogger(__name__)
basedir = os.path.dirname(__file__)
base = os.path.join(basedir, "data")

__hide__ = ["template.html"]

import sys

@controller
def index():
    c.isgae =  "google.appengine" in sys.modules
    c.ispaster = not c.isgae
    c.modules = sys.modules    
   
@controller
def test():
    return "Noch ein Test"

@controller
def error():
    return str(0/1 + 1/0)
