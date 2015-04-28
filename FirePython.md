# FirePython on Pyxer #

If you don't know that great tool hurry up and have a look ;)

http://firepython.binaryage.com/

## Installation ##

First install FirePython for your project:

```
$ pyxer install firepython
$ pyxer install jsonpickle
```

Then add the middleware. To do this create modify pyxer-app.py to look like this:

```

# -*- coding: UTF-8 -*-

""" Pyxer on Google App Engine
    http://www.pyxer.net
""" 

import os, sys

# Cleanup the Python path (mainly to circumvent the systems SetupTools)
sys.path = [path for path in sys.path if ("site-packages" not in path) and ('pyxer' not in path)]

# Add our local packages folder to the path
import site
here = os.path.dirname(__file__)
site_lib = os.path.join(here, 'site-packages')
site.addsitedir(site_lib)

# Import the stuff we need to begin serving
from google.appengine.ext.webapp.util import run_wsgi_app
from pyxer.app import make_app

# FirePython imports
import firepython.middleware
import logging

# The main function is important for GAE to know if the process can be kept
def main():
    conf = dict(__file__=os.path.abspath(os.path.join(__file__, os.pardir, 'pyxer.ini')))
    app = make_app(conf)

    # FirePython Middleware
    app = firepython.middleware.FirePythonWSGI(app)

    # Also show logging at DEBUG level
    logging.getLogger().setLevel(logging.DEBUG)

    run_wsgi_app(app)

# Initialize on first start
if __name__ == "__main__":
    main()
```

That's it. Happy coding.