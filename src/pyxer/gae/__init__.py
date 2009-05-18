# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

import pyxer
import os
import os.path
import sys
from shutil import * 
from pyxer.utils import find_root, call_script, call_subprocess

def normalize_py_file(name):
    if name.lower().endswith(".pyc"):
        return name[: - 1]
    return name

def serve(opt):
    global pyxer
    
    # setup(opt)    
    #os.system(r'c:\python25\python c:\Programme\Google\google_appengine\dev_appserver.py "%s"' % os.getcwd())
    #return
    
    options = []
    options.append("--show_mail_body")
    if opt.debug:
        options.append("--debug")
    if opt.host:
        options.append("--address=%s" % opt.host)
    if opt.port:
        options.append("--port=%s" % opt.port)
    if opt.clear:
        options.append("--clear_datastore")
    
    root = find_root()
    
    if sys.platform == "win32":
        
        try:
            import dev_appserver
        except ImportError:
            sys.path.append(r"C:\Programme\Google\google_appengine")
            import dev_appserver
        
        # cal_
        call_subprocess([
            sys.executable,
            normalize_py_file(dev_appserver.__file__) ] + 
            options + [     
            root
            ])
        
        #sys.path = dev_appserver.EXTRA_PATHS + sys.path    
        #script_path = os.path.join(dev_appserver.DIR_PATH, dev_appserver.DEV_APPSERVER_PATH)
        #import google.appengine.tools.dev_appserver_main as gmain
        #options = [""] + options + [os.getcwd()]
        #sys.exit(gmain.main(options))
    
    elif sys.platform == "darwin":

        call_subprocess([
            "dev_appserver.py"] + 
            options + [            
            root
            ])
    
    else:
        
        print "Please launch Google App Engine directly"
    
    # execfile(script_path, globals())

def upload(opt):
    "python c:\Programme\Google\google_appengine\appcfg.py update ."
    options = []
    if opt.debug:
        options.append("--debug")
    
    root = find_root()
    
    if sys.platform == "win32":
        
        try:
            import appcfg
        except ImportError:
            sys.path.append(r"C:\Programme\Google\google_appengine")
            import appcfg
        
        call_subprocess([
            sys.executable,
            normalize_py_file(appcfg.__file__) ] + 
            options + [     
            "update",
            root
            ])
        
        #sys.path = dev_appserver.EXTRA_PATHS + sys.path    
        #script_path = os.path.join(dev_appserver.DIR_PATH, dev_appserver.DEV_APPSERVER_PATH)
        #import google.appengine.tools.dev_appserver_main as gmain
        #options = [""] + options + [os.getcwd()]
        #sys.exit(gmain.main(options))
    
    elif sys.platform == "darwin":
        
        call_subprocess([
            "appcfg.py"] + 
            options + [
            "update",
            root
            ])
    
    else:
        
        print "Please launch Google AppEngine directly"
