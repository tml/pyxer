# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Pure Python zipfile importer.

This approximates the standard zipimport module, which isn't supported
by Google App Engine.  See PEP 302 for more information about the API
for import hooks.

Usage:
  import my_zipimport
  my_zipimport.install()
"""
# TODO(guido): Write unit tests.

__author__ = ('Iain Wade', 'Guido van Rossum')

import logging
import os
import sys
import types
import zipfile


# Order in which we probe the zipfile directory.
# Try .py first since that is most common.
zip_search_order = [
  {'suffix': '.py'},
  {'suffix': '/__init__.py', 'is_package': True},
]


# Cache for opened zipfiles.
# Maps the zipfile's path to a (zipfile, files) tuple.
zip_zipfile_cache = {}


class ZipImporter:
  """A PEP-302-style importer that can import from a zipfile."""

  def __init__(self, zipfilename, prefix):
    """Constructor.

    Args:
      zipfilename: The filename of the zipfile.
      prefix: A prefix inside the zipfile; may be an empty string.
    """
    self.zipfilename = zipfilename
    self.prefix = prefix
    if zipfilename in zip_zipfile_cache:
      # Get our stuff from the cache.
      self.zipfile, self.files = zip_zipfile_cache[zipfilename]
    else:
      # Open the zip file and read the index.
      try:
        self.zipfile = zipfile.ZipFile(self.zipfilename)
        self.files = self.zipfile.namelist()
      except (EnvironmentError, zipfile.BadZipfile), err:
        # This is logged as a warning since it means we failed to open
        # what appears to be an existing zipfile.
        msg = 'Can\'t open zipfile: %s: %s' % (err.__class__.__name__, err)
        logging.warn(msg)
        raise ImportError(msg)
      else:
        # Update the cache.
        zip_zipfile_cache[zipfilename] = self.zipfile, self.files
        # This is logged as info since it represents a significant
        # result.  This log message appears only during the initial
        # process initialization, not for subsequent requests.
        logging.info('ZipImporter(%r, %r)', zipfilename, prefix)

  def _get_info(self, fullmodname):
    """Internal helper for find_module() and load_module().

    Args:
      fullmodname: The dot-separated full module name, e.g. 'django.core.mail'.

    Returns:
      A tuple (submodname, is_package, relpath) where:
        submodname: The final component of the module name, e.g. 'mail'.
        is_package: A bool indicating whether this is a package.
        relpath: The path to the module's source code within to the zipfile.

    Raises:
      ImportError if the module is not found in the archive.
    """
    submodname = fullmodname.split('.')[-1]
    subpath = os.path.join(self.prefix, submodname)
    for ent in zip_search_order:
      relpath = subpath + ent['suffix']
      if relpath in self.files:
        return submodname, ent.get('is_package', False), relpath
    msg = ('Can\'t find module %s in zipfile %s with prefix %s' %
           (fullmodname, self.zipfilename, self.prefix))
    logging.debug(msg)
    raise ImportError(msg)

  def _get_source(self, fullmodname):
    """Internal helper for load_module().

    Args:
      fullmodname: The dot-separated full module name, e.g. 'django.core.mail'.

    Returns:
      A tuple (submodname, is_package, fullpath, source) where:
        submodname: The final component of the module name, e.g. 'mail'.
        is_package: A bool indicating whether this is a package.
        fullpath: The path to the module's source code including the
          zipfile's filename.
        source: The module's source code.

    Raises:
      ImportError if the module is not found in the archive.
    """
    submodname, ispkg, relpath = self._get_info(fullmodname)
    source = self.zipfile.read(relpath)
    fullpath = '%s/%s' % (self.zipfilename, relpath)
    return submodname, ispkg, fullpath, source

  def find_module(self, fullmodname, path=None):
    """PEP-302-compliant find_module() method.

    Args:
      fullmodname: The dot-separated full module name, e.g. 'django.core.mail'.
      path: Optional search path.  Currently ignored.

    Returns:
      None if the module isn't found in the archive; self if it is found.
    """
    # TODO(guido): support the path argument.
    assert path is None, 'The path argument is not yet supported'
    try:
      submodname, ispkg, relpath = self._get_info(fullmodname)
    except ImportError:
      logging.debug('find_module(%r) -> None', fullmodname)
      return None
    else:
      logging.debug('find_module(%r) -> self', fullmodname)
      return self

  def load_module(self, fullmodname):
    """PEP-302-compliant load_module() method.

    Args:
      fullmodname: The dot-separated full module name, e.g. 'django.core.mail'.

    Returns:
      The module object constructed from the source code.

    Raises:
      SyntaxError if the module's source code is syntactically incorrect.
      ImportError if there was a problem accessing the source code.
      Whatever else can be raised by executing the module's source code.
    """
    logging.debug('load_module(%r)', fullmodname)
    submodname, ispkg, fullpath, source = self._get_source(fullmodname)
    code = compile(source, fullpath, 'exec')
    mod = sys.modules.get(fullmodname)
    if mod is None:
      mod = sys.modules[fullmodname] = types.ModuleType(fullmodname)
    mod.__loader__ = self
    mod.__file__ = fullpath
    mod.__name__ = fullmodname
    if ispkg:
      mod.__path__ = [os.path.dirname(mod.__file__)]
    exec code in mod.__dict__
    return mod


def zip_importer_factory(path_entry):
  """Try to return a zip importer for a prefix of path_entry.

  This is the factory function installed in sys.path_hooks.

  Args:
    path_entry: An element of sys.path, typically a filename,
      possibly with a suffix representing a path inside the
      archive.

  Returns:
    A ZipImporter instance if path_entry represents a valid zipfile.

  Raises:
    ImportError if path_entry doesn't exist or is not a valid zipfile.
  """
  zipfilename = path_entry
  prefix = ''
  # Strip trailing sections until an existing path is found
  while not os.path.lexists(zipfilename):
    head, tail = os.path.split(zipfilename)
    if head in ('', '/'):
      msg = 'Nothing found for %r' % path_entry
      logging.debug(msg)
      raise ImportError(msg)
    zipfilename = head
    prefix = os.path.join(tail, prefix)
  if not os.path.isfile(zipfilename):
    msg = 'Non-file %r found for %r' % (zipfilename, path_entry)
    logging.debug(msg)
    raise ImportError(msg)
  return ZipImporter(zipfilename, prefix)


def install():
  """Convenience function to install our factory in sys.path_hooks.

  We replace whatever was there before.  It is pre-initialized with
  the standard zipimporter, which we don't want, so this is expedient.

  If you want different semantics, don't call this function, but
  instead manipulate sys.path_hooks yourself.
  """
  sys.path_hooks[:] = [zip_importer_factory]
