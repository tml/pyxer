#!/bin/python2.5
# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 103 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2007-10-31 17:08:54 +0100 (Mi, 31 Okt 2007) $"
__svnid__   = "$Id: pisa.py 103 2007-10-31 16:08:54Z holtwick $"

import logging
import os, os.path
import sys
import pyxer.gae.monkey.boot as monkey

from pyxer.utils import call_subprocess, find_root

DEVELOPMENT_INI = """
[pipeline:main]
pipeline = error the-app

[filter:error]
use = egg:Paste#error_catcher
debug = true

[app:the-app]
use = config:src/$name/development.ini
""".lstrip()

def create(opt):
     
    print
    name = raw_input("Project name: ")

    # Change to AppEngine module replacements
    # os.chdir(os.path.join(os.path.dirname(monkey.__file__), "monkey"))
    
    # Start appengine-boot.py
    sys.argv = ["appengine_monkey.py", 
        "--paste-deploy", 
        "-v", 
        "--no-site-packages", 
        "--unzip-setuptools",
        "--easy-install=pylons",
        # "--easy-install=beaker==dev",
        name]
    monkey.main()
    
    root = find_root(name)
    
    # Update development.ini
    open(os.path.join(root, "development.ini"), "w").write(DEVELOPMENT_INI.replace("$name", name))
    
    # Create Pylons project    
    os.chdir(os.path.join(root, "src"))
    env = {"VIRTUAL_ENV": root}    
    call_subprocess(["paster", "create", "-t", "pylons", name], extra_env=env)
    
    # Setup.py develop
    os.chdir(os.path.join(root, "src", name))
    env = {"VIRTUAL_ENV": root}    
    call_subprocess(["python", "setup.py", "develop"], extra_env=env)
    