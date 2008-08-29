# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

from pyxer.base import *

import logging
log = logging.getLogger(__name__)

@controller
def index():
    c.title = "Hello World"

@controller(output="html")
def index():
    pass
