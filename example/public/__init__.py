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

#@controller
#def index():
#   return "Hallo, es funktioniert %r" % req.path_info

@controller
def test():
    return "Noch ein Test"

@controller
def error():
    return str(0/1 + 1/0)
