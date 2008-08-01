# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

import logging
import os, os.path
import sys
import pyxer.gae.monkey
import pyxer.gae.monkey.boot as boot

log = logging.getLogger(__file__)

from pyxer.utils import call_subprocess, call_script, find_root

INDEX_HTML = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Welcome to Pyxer</title>
</head>
<body>
    <h1>Welcome!</h1>
    <p><strong>Your Pyxer installation is running!</strong></p>
    <p>Continue by adding controllers and files to the &quot;public&quot; directory as described in the documentation.</p>
    <p>Thanks for using Pyxer.</p>
</body>
</html>
""".lstrip()

INIT_PY = """
# -*- coding: UTF-8 -*-

from pyxer.base import *

#@controller
#def index():
#    c.message = "Welcome"    
""".lstrip()

def self_setup(root=None):
    if not root:
        root = find_root()    
    # Get parent directory
    dir = os.path.split(os.path.dirname(__file__))[0]
    log.debug("Pyxer setup.py dir %r", dir)
    # Do setup 
    call_script(
        ["python", "pyxer/setup.py", "install", "-f"],
        cwd=dir,
        root=root)    

def create(opt, here):

    # Change to AppEngine module replacements
    # os.chdir(os.path.join(os.path.dirname(monkey.__file__), "monkey"))
    
    # Create directory
    if not os.path.exists(here):
        os.makedirs(here)
            
    # Create gae.ini
    app_name = []
    path = os.path.join(here, "app.yaml")
    if not os.path.exists(path):        
        name = raw_input("Name of project: ")         
        app_name = ["--app-name=" + name]
           
    # Start appengine-boot.py
    sys.argv = ["XXXDUMMYXXX",
        "--paste-deploy",
        "-v",
        "--no-site-packages",
        "--unzip-setuptools",
        "--easy-install=webob",
        "--easy-install=html5lib",
        "--easy-install=beaker",
        # "--easy-install=beaker==dev",            
        ] + app_name + [
        # "--easy-install=pyxer",
        # "--easy-install=beaker==dev",
        here]
    boot.main()

    # Install appengine_monkey
    #dir = os.path.dirname(pyxer.gae.monkey.__file__)
    #log("")    
    #call_script(
    #    ["python", "setup.py", "install", "-f"], 
    #    cwd=cwd)

    # Install pyxer
    self_setup(here)

    # Create public dir    
    path = os.path.join(here, "public")
    if not os.path.exists(path):        
        os.makedirs(path)              
        open(os.path.join(path, "index.html"), "w").write(INDEX_HTML)
        open(os.path.join(path, "__init__.py"), "w").write(INIT_PY)
    
    print "Initialization completed!"
    
    # Create Pylons project    
    #os.chdir(os.path.join(root, "src"))
    #env = {"VIRTUAL_ENV": root}    
    #call_subprocess(["paster", "create", "-t", "pylons", name], extra_env=env)
    
    # Setup.py develop
    #os.chdir(os.path.join(root, "src", name))
    #env = {"VIRTUAL_ENV": root}    
    #call_subprocess(["python", "setup.py", "develop"], extra_env=env)
