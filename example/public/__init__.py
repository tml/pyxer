# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

from pyxer.base import *

import sys
import os
import logging
import pyxer

log = logging.getLogger(__name__)
here = os.path.dirname(__file__)
base = os.path.join(here, "data")

@controller
def index():
    c.isgae =  "google.appengine" in sys.modules
    c.ispaster = not c.isgae
    c.pyxerversion = pyxer.__version__
    c.modules = sys.modules
    c.samples = []
    for name in sorted(os.listdir(here)):
        try:
            readme = os.path.join(here, name, "README.txt")
            if os.path.isfile(os.path.join(here, name, "README.txt")):
                f = open(readme, "r")
                c.samples.append((
                    f.readline().strip(),
                    name + "/",
                    f.read().strip()))
                f.close()
                log.debug("Added sample %r", c.samples[-1])
        except:
            log.exception("Error while collecting samples")
