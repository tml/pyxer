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

from optparse import OptionParser
from pyxer.app import serve
from pyxer.configparser import *
from pyxer.utils import system, call_subprocess, find_root

import logging
import sys
import os
import os.path

_description = """
Yet another Python framework
""".strip()

def showlog(debug):
    level = logging.WARN
    if debug:
        level = logging.DEBUG
    try:
        LOG_FORMAT_DEBUG = "%(levelname)s [%(name)s] %(pathname)s line %(lineno)d: %(message)s"
        logging.basicConfig(
            level=level,
            format=LOG_FORMAT_DEBUG)
    except:
        logging.basicConfig()

class OptParser(OptionParser):
    
    def print_help(self):
        OptionParser.print_help(self)
        # parser.print_usage()
        # print parser.format_option_help()
        print
        print """
Commands:  
  serve              Serves the project
  setup, create      Create a new project
  upload, deploy     Upload project (only gae)
  open, activate     Activate context for installs etc.
             
Daemon commands (just for paster):
  start              Start
  stop               Stop 
  status             Status 
  reload, restart    Restart  
""".strip()    
   
    #def error(self, msg):
    #    OptionParser.error(self, msg)
    #    print "Use option --help for complete help"

iswin = (sys.platform=="win32")

def command(engine=None):

    parser = OptParser(
        # "usage: %prog [options] command",
        "usage: pyxer [options] command",
        description = _description,
        version = "pyxer 1.0 (c) Dirk Holtwick <dirk.holtwick@gmail.com>, 2008",
        # epilog="Neu\n\r\n" + 20*"hallo ",
        )
    
    parser.add_option(
        "-q", 
        "--quiet",
        action="store_false", 
        dest="verbose", 
        default=True,
        help="don't print status messages to stdout")
    #parser.add_option(
    #    "-f", 
    #    "--force",
    #    action="store_false", 
    #    dest="force", 
    #    default=True,
    #    help="don't print status messages to stdout")
    parser.add_option(
        "-d", 
        "--debug",
        action="store_true", 
        dest="debug", 
        default=False,
        help="activate debug logging")
    if not engine:
        parser.add_option(
            "--engine",
            dest="engine", 
            default="",
            help="engine that will be used (wsgi, gae, paster)")
    parser.add_option(
        "--port",
        dest="port", 
        default="8080",
        help="serving on port")
    parser.add_option(
        "--host",
        dest="host", 
        default="127.0.0.1",
        help="serving on host")
    parser.add_option(
        "-r",
        "--reload",
        dest="reload",
        action="store_true",  
        help="reload on changing files")
    parser.add_option(
        "-u",
        "--update",
        dest="update",
        action="store_true",         
        help="update suplementary data and files")
        
    (opt, args) = parser.parse_args()

    config_default = {
        "pyxer.debug":              (cBOOL, False),
        "pyxer.sessions":           (cBOOL, False),
        "pyxer.engine":             (cSTRING, ""),
        "pyxer.templating":         (cSTRING, ""),
        "pyxer.host":               (cSTRING, "127.0.0.1"),
        "pyxer.port":               (cINT, 8080, 0, 65536),        
        }

    if not (1 <= len(args) <= 1):
        parser.print_help()  
        # parser.error("incorrect number of arguments")
        sys.exit(1)        

    command = args[0].lower()
    
    if engine:
        opt.engine = engine

    if opt.engine in ("gae", "google", "appengine", "googleappengine", "g"):
        print "Google AppEngine"
        opt.engine = "gae"
        import pyxer.gae as engine
    elif opt.engine in ("paster", "paste", "p"):
        print "Paster"
        opt.engine = "paster"
        import pyxer.paster as engine
    else:
        print "Python WSGI"
        engine = None
        
    # Serve
    if command=="serve":
            
        if engine:
            engine.serve(opt)
        else:
            showlog(opt.debug)
            serve(opt)

    # Setup
    elif (command=="setup" or command=="create"):
                    
        import pyxer.create
        pyxer.create.create(opt)
        
    # Activate
    elif (command=="open" or command=="activate"):
        
        root = find_root()
        if not root:
            print "No project found"
        elif iswin:            
            # call_subprocess([os.path.join(root, "scripts", "activate.bat")])
            system("start " + os.path.join(root, "scripts", "activate.bat"))
        else:
            pass                

    # Deactivate
    elif (command=="close" or command=="deactivate"):
        
        root = find_root()
        if not root:
            print "No project found"
        elif iswin:
            system(os.path.join(root, "scripts", "deactivate.bat"))
        else:
            pass                

    # Daemon
    elif command=="start" and opt.engine=="paster":        
        engine.serve(opt, daemon="start")
    elif command=="stop" and opt.engine=="paster":        
        engine.serve(opt, daemon="stop")
    elif command=="status" and opt.engine=="paster":        
        engine.serve(opt, daemon="status")
    elif (command=="reload" or command=="restart") and opt.engine=="paster":        
        engine.serve(opt, daemon="restart")
    
    # Upload
    elif (command=="upload" or command=="deploy") and opt.engine=="gae":        
        engine.upload(opt)
        
    else:
        parser.print_help()
        sys.exit(1)
        # parser.error("unsupported command")
        
    # print options, args

def command_gae():
    command("gae")

def command_paster():
    command("paster")
    