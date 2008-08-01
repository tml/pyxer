# -*- coding: UTF-8 -*-

from pyxer.base import *

import os
import os.path 

@controller
def index():
    c.dir = req.params.get("dir", os.path.dirname(__file__))
    if os.path.isdir(c.dir):
        c.parent = os.path.split(c.dir)[0]
        c.files = [(name, os.path.join(c.dir, name), os.path.isdir(os.path.join(c.dir, name))) for name in os.listdir(c.dir)]
    else:
        return "Directory name required"
