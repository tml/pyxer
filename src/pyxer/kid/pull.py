# -*- coding: utf-8 -*-

"""Pull-style interface for ElementTree.

The pyxer.kid.pull module has been deprecated in favor of pyxer.kid.parser.

"""

__revision__ = "$Rev: 429 $"
__date__ = "$Date: 2006-10-26 15:24:33 +0200 (Do, 26 Okt 2006) $"
__author__ = "Ryan Tomayko (rtomayko@gmail.com)"
__copyright__ = "Copyright 2004-2005, Ryan Tomayko"
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"

import warnings
warnings.warn("pyxer.kid.pull has been superseded by pyxer.kid.parser", DeprecationWarning)

from pyxer.kid.parser import *