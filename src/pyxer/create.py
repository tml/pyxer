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
    # XXX Should be something like pyxer.pyxer or similar
    dir = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]
    log.debug("Pyxer setup.py dir %r", dir)
    call_script(
        ["python", "setup.py", "install", "-f"], 
        cwd=dir,
        root=here)

    # Create public dir    
    path = os.path.join(here, "public")
    if not os.path.exists(path):        
        os.makedirs(path)              
        open(os.path.join(path, "index.html"), "w").write(INDEX_HTML)
    
    print "Initialization completed!"
    
    # Create Pylons project    
    #os.chdir(os.path.join(root, "src"))
    #env = {"VIRTUAL_ENV": root}    
    #call_subprocess(["paster", "create", "-t", "pylons", name], extra_env=env)
    
    # Setup.py develop
    #os.chdir(os.path.join(root, "src", name))
    #env = {"VIRTUAL_ENV": root}    
    #call_subprocess(["python", "setup.py", "develop"], extra_env=env)
