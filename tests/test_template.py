import unittest
from pyxer.template import *

import sys
sys.path.insert(0, "C:\work\html5lib")

_data = """<!DOCTYPE html>
<html>
 <head>
  <title>TITLE</title>
 </head>
<body>
 BODY
 <br>
</body>
</html>
"""

class TestCase(unittest.TestCase):

    def testSample(self):
        t = HTMLTemplate(_data)
        # XXX Known bug in html5lib adding whitespaces
        print t.source.encode("latin1","ignore")
        r = t.render()
        r = t.render(xhtml=True)
        print r
        self.assertEqual(_data, r)

def buildTestSuite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

def main():
    buildTestSuite()
    unittest.main()

if __name__ == "__main__":
    main()
