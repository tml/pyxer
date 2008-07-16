#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2002-2008 ##
## All rights reserved                     ##
#############################################

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name           = "Pyxer",
    version        = "0.5",
    description    = "Python X Framework",
    license        = "MIT",
    author         = "Dirk Holtwick",
    author_email   = "holtwick@web.de",
    url            = "http://www.pyxer.net/",
    download_url   = "http://www.pyxer.net/",
    keywords       = "HTML, AJAX, Javascript, Server, Turbogears, Cherrypy",

    requires       = [
        "jsonlib", 
        "webob", 
        "paste",
        ],

    package_dir = {
        '': 'src'
        },

    packages = [
        "pyxer",
        "pyxer.gae",
        "pyxer.paster",
        "pyxer.utils",
        ],

    # packages = find_packages(exclude=['ez_setup']),

    include_package_data = True,

    #entry_points = {
    #    'console_scripts': ['pyxer = pyxer.command:command',]
    #    },

    long_description = """
Pyxer is a Python AJAX Server/ Framework similar to the
Jaxer project of Aptana. Instead of writing client side
code in Javascript you can  use Python. The Python code
will be translated to Javascript before send to the client.
You may also have server side code defined in the
HTML file that can asynchronously be called form the
client with seamless use of AJAX in the background.
Example for use in Turbogears included.
        """.strip(),

    #classifiers = [x.strip() for x in """
    #    """.strip().splitlines()],

    entry_points="""
    [paste.app_factory]
    main = pyxer.app:app_factory

    [console_scripts]
    pyxer = pyxer.command:command
    xgae = pyxer.command:command_gae
    xpaster = pyxer.command:command_paster
    """,

    )
