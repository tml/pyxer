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
# from pyxer.app import make_app

from pyxer.utils import find_root, call_script, call_subprocess

_app_yaml = """
application: %s
version: 1
runtime: python
api_version: 1
handlers:
- url: /.*
  script: gae.py
- url: /admin/.*
  script: $PYTHON_LIB/google/appengine/ext/admin
  login: admin
""".lstrip()

_gae_py = """
# -*- coding: UTF-8 -*-
import sys, os.path,logging
log = logging.getLogger("pyxer.gae")
np = os.path.join(os.path.dirname(__file__), "lib")
sys.path.insert(1, np)
log.info("use pyxer on path %r", np)
from pyxer.gae import main
if __name__ == "__main__": main()
""".lstrip()

'''
def copyPyxer(src, dst, symlinks = False):    
    names = os.listdir(src)
    try:
        os.makedirs(dst)
    except:
        pass
    errors = []
    for name in names:        
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                if name <> ".svn":
                    copyPyxer(srcname, dstname, symlinks)
            else:
                if name.endswith(".py"):
                    print "create", dstname
                    copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error, err:
            errors.extend(err.args[0])
    try:
        copystat(src, dst)
    except WindowsError:
        # can't copy file access times on Windows
        pass
    except OSError, why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise Error, errors

def setup(opt):
    import html5lib
    
    # Create an app.yaml
    if opt.update or (not os.path.isfile("app.yaml")):
        print "create app.yaml"
        open("app.yaml", "w").write(_app_yaml % ("test"))
    
    # Create a starter script
    if opt.update or (not os.path.isfile("gae.py")):
        print "create gae.py"
        open("gae.py", "w").write(_gae_py)
    
    # Copy Pyxer to working directory
    if opt.update or (not os.path.isdir("lib")): 
        copyPyxer(
            os.path.dirname(pyxer.__file__),
            os.path.join(os.getcwd(), "lib", "pyxer"))

    if opt.update or (not os.path.isdir("lib")): 
        copyPyxer(
            os.path.dirname(html5lib.__file__),
            os.path.join(os.getcwd(), "lib", "html5lib"))
''' 

def fix():
    print "Fix paths"
    call_script(["python", "-m", "pyxer.gae.monkey.pth_relpath_fixup"])

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
    
    fix()    
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
    
    fix()
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

#def main():    
#    wsgiref.handlers.CGIHandler().run(make_app())

#if __name__ == "__main__":
#    main()
