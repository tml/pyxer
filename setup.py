# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

long_description = """
Pyxer is a simple Python Framework for Paste and Google App Engine (GAE)
""".strip()

setup(
    name           = "pyxer",
    version        = "VERSION{0.4.1alpha}VERSION"[8:-8],
    description    = "Simple Python Framework for Paste and Google App Engine (GAE)",
    license        = "MIT",
    author         = "Dirk Holtwick",
    author_email   = "dirk.holtwick@gmail.com",
    url            = "http://code.google.com/p/pyxer/",
    download_url   = "http://code.google.com/p/pyxer/",
    keywords       = "Framework, Google App Engine, GAE, appengine, Paster, Server, Templating",

    requires       = [
        "jsonlib",
        "webob",
        "paste",
        "html5lib",
        ],

    package_dir = {
        '': 'src'
        },

    packages = [
        "pyxer",
        "pyxer.gae",
        "pyxer.paster",
        "pyxer.utils",
        "pyxer.template",
        ],

    # packages = find_packages(exclude=['ez_setup']),

    include_package_data = True,

    test_suite = "tests",

    #entry_points = {
    #    'console_scripts': ['pyxer = pyxer.command:command',]
    #    },

    long_description = long_description,

    #classifiers = [x.strip() for x in """
    #    """.strip().splitlines()],

    entry_points="""
[paste.app_factory]
main = pyxer.app:app_factory

[console_scripts]
pyxer = pyxer.command:command
xgae = pyxer.command:command_gae
xpaster = pyxer.command:command_paster
""".lstrip(),

    )
