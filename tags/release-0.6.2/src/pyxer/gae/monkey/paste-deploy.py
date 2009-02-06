#!/usr/bin/env python

CONF_FILE = 'gae.ini'

import sys
import os
##if getattr(sys, 'real_prefix', None):
##    # This is a sign that a virtualenv python is being used, and that causes problems
##    print >> sys.stderr, (
##        "This appears to be a virtualenv python; please start dev_appserver.py with the system python interpreter")
##    sys.exit(2)
if os.environ.get('PYTHONPATH'):
    print >> sys.stderr, (
        "$PYTHONPATH is set.  This may cause import problems; it is best to unset PYTHONPATH before starting the appserver")

def _test():
    print "sys.path = ["
    for dir in sys.path:
        print "    %r," % (dir,)
    print "]"
    print "sys.modules = ["
    for dir in sorted(sys.modules):
        try:
            f = sys.modules[dir].__file__
        except:
            f = None
        print "    %r, # -> %r " % (dir, f)
    print "]"

try:
    here = os.path.dirname(__file__)
    
    try:
        import site
    except:
        site_lib = os.path.join(here, 'lib', 'python2.5')
        if not os.path.isdir(site_lib):
            site_lib = os.path.join(here, 'Lib')
        sys.path.insert(0, site_lib)
        import site

    # Test for correct site-packages directory, because if developed on
    # Windows we have different paths as everywhere else. And this has also
    # to work on the Google machine too!
    site_packages = os.path.join(here, 'lib', 'python2.5', 'site-packages')
    if not os.path.isdir(site_packages):
        site_packages = os.path.join(here, 'Lib', 'site-packages')
    site.addsitedir(site_packages)

    # In this phase GAE does just be able to load modules on the very first level, is it a bug?
    site.addsitedir(os.path.join(site_packages, "pyxer", "gae", "monkey"))
    import appengine_monkey

    ## If you want to use httplib but get socket errors, you should uncomment this line:
    #appengine_monkey.install_httplib()

    ## This portion is the "Paste Deploy" part; it loads the application from a config file using
    ## Paste Deploy (http://pythonpaste.org/deploy/).  If you want to load your application in a
    ## different way (e.g., construct it in Python code) you can change these next three lines
    ## and just make sure that `app` is your WSGI application:
    CONF_FILE = 'config:' + os.path.join(here, CONF_FILE)
    from paste.deploy import loadapp
    app = loadapp(CONF_FILE)

except:
    import traceback
    print 'Content-type: text/plain'
    print
    print 'Error loading application:'
    traceback.print_exc(file=sys.stdout)
    print
    # exc_value = sys.exc_info()[1]
    if 1: #isinstance(exc_value, ImportError):
        _test()
        print        
        #print
        #print "PTH files"
        #for fn in os.listdir(site_packages):
        #    print fn

else:
    def main():
        ## FIXME: set multiprocess based on whether this is the dev/SDK server
        import wsgiref.handlers
        wsgiref.handlers.BaseCGIHandler(sys.stdin, sys.stdout, sys.stderr, os.environ,
                                        multithread=False, multiprocess=False).run(app)

    if __name__ == '__main__':
        main()
