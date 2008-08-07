# Modified by Dirk Holtwick for use in Pyxer

from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='pyxer-appengine-monkey',
      version=version,
      description="Monkeypatches for Google App Engine",
      long_description="""\
This project is a set of replacement modules and monkeypatches to
existing modules in the App Engine environment, to make it more like a
normal Python environment. This is to facilitate the use of existing
libraries.
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='appengine',
      author='Ian Bicking',
      author_email='google-appengine@googlegroups.com',
      url='http://code.google.com/p/appengine-monkey/',
      license='MIT',
      py_modules=['pth_relpath_fixup', 'appengine_monkey', 'fetchapp'],
      # A horrible hack to get these files installed:
      packages=['appengine_monkey_files'],
      package_dir={'appengine_monkey_files': '.'},
      package_data={'appengine_monkey_files': ['module-replacements/*.py', 'development.ini', 'app.yaml.template']},
      zip_safe=False,
      install_requires=[],
      entry_points="",
      )
