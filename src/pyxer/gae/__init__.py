# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

__version__ = "$Revision: 103 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2007-10-31 17:08:54 +0100 (Mi, 31 Okt 2007) $"
__svnid__   = "$Id: pisa.py 103 2007-10-31 16:08:54Z holtwick $"

import pyxer
import os
import os.path
import sys
from shutil import * 
import wsgiref.handlers
from pyxer.app import make_app

from pyxer.utils import find_root, call_script

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

def copyPyxer(src, dst, symlinks=False):    
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

    if opt.update or (not os.path.isdir("ldib")): 
        copyPyxer(
            os.path.dirname(html5lib.__file__), 
            os.path.join(os.getcwd(), "lib", "html5lib"))

def fix():
    print "Fix paths"
    call_script(["python","-m","pyxer.gae.monkey.pth_relpath_fixup"])
    
def serve(opt):
    global pyxer
    
    # setup(opt)
    #return
    
    options = []
    if opt.debug:
        options.append("-d")
    
    fix()
    
    if sys.platform=="win32":
        
        try:
            import dev_appserver
        except ImportError:
            sys.path.append(r"C:\Programme\Google\google_appengine")
            import dev_appserver
                    
        os.system('%s %s "%s"' % (
            sys.executable,
            dev_appserver.__file__,
            os.getcwd()))
        
        #sys.path = dev_appserver.EXTRA_PATHS + sys.path    
        #script_path = os.path.join(dev_appserver.DIR_PATH, dev_appserver.DEV_APPSERVER_PATH)
        #import google.appengine.tools.dev_appserver_main as gmain
        #options = [""] + options + [os.getcwd()]
        #sys.exit(gmain.main(options))
    
    elif sys.platform=="darwin":
            
        os.system("dev_appserver.py %s ." % " ".join(options))        
        # print "Please launch using GoogleAppEngineLauncher.app"
    
    else:
        
        print "Please launch Google AppEngine directly"
    
    # execfile(script_path, globals())

def upload(opt):
    pass
    
def main():    
    wsgiref.handlers.CGIHandler().run(make_app())

if __name__=="__main__":
    main()
