# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

import logging
import os.path
import sys
import shutil
import pyxer.gae.monkey.boot as boot
import pyxer.utils as utils

log = logging.getLogger(__name__)

from pyxer.utils import call_script, find_root

INDEX_HTML = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
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

ENTRY_POINTS_TXT = """\
[paste.app_factory]
main = pyxer.app:app_factory
"""

'''
def self_setup2(root = None):
    if not root:
        root = find_root()
    # Get parent directory
    dir = os.path.dirname(__file__) #Uses setuptools instead?
    setup_py = os.path.join(dir, "setup.py")
    log.debug("Pyxer %r in dir %r", setup_py, dir)
    # Do setup
    call_script(
        ["python", setup_py, "install", "-f"],
        cwd = os.path.join(dir, os.pardir),
        root = root)
'''

def self_setup(root = None):
    " Set up Pyxer in the virtual environment "
    
    # Find VM
    if not root:
        root = find_root()    
    if not root:
        raise Error, "VirtualENV not found"
    here = os.path.dirname(__file__) 
    
    # Find site_packages folder
    site_packages = os.path.join(root, 'lib', 'python2.5', 'site-packages')
    if not os.path.isdir(site_packages):
        site_packages = os.path.join(root, 'Lib', 'site-packages')
    
    # Remove old installation 
    pyxer_dir = os.path.join(site_packages, "pyxer")
    if os.path.isdir(pyxer_dir):
        # log.info("Remove Pyxer directory %r", pyxer_dir)
        pass
    
    # Copy package
    log.info("Copy from %r to %r", here, pyxer_dir)
    utils.copy_python(here, pyxer_dir)

    # This is needed for the paster app
    egg_dir = os.path.join(site_packages, "pyxer.egg-info")
    if not os.path.isdir(egg_dir):
        os.makedirs(egg_dir)
    open(os.path.join(egg_dir, "entry_points.txt"), "w").write(ENTRY_POINTS_TXT)

    # Copy paste-deploy.py
    deploy_from = os.path.join(os.path.dirname(boot.__file__), 'paste-deploy.py')
    deploy_to = os.path.join(root, 'paste-deploy.py')
    log.info("Copy from %r to %r", deploy_from, deploy_to)
    shutil.copyfile(deploy_from, deploy_to)
        
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

    # Create public dir
    path = os.path.join(here, "public")
    if not os.path.exists(path):
        os.makedirs(path)
        open(os.path.join(path, "index.html"), "w").write(INDEX_HTML)
        open(os.path.join(path, "__init__.py"), "w").write(INIT_PY)

    # Start appengine-boot.py
    sys.argv = ["XXXDUMMYXXX",
        "--paste-deploy",
        "-v",
        "--no-site-packages",
        "--unzip-setuptools",
        "--easy-install=webob",
        # "--easy-install=beaker",
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

    print "Initialization completed!"

    # Create Pylons project
    #os.chdir(os.path.join(root, "src"))
    #env = {"VIRTUAL_ENV": root}
    #call_subprocess(["paster", "create", "-t", "pylons", name], extra_env=env)

    # Setup.py develop
    #os.chdir(os.path.join(root, "src", name))
    #env = {"VIRTUAL_ENV": root}
    #call_subprocess(["python", "setup.py", "develop"], extra_env=env)
