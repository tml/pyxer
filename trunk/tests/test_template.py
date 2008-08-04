# -*- coding: UTF-8 -*-

import unittest
from pyxer.template import *

import re
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

_sample_begin = """<!DOCTYPE html>
<html>
 <head>
  <title>TITLE</title>
 </head>
<body>
 """

_sample_end = """
</body>
</html>
"""

class Context: pass

class PyxerTemplateTestCase(unittest.TestCase):

    rxbody = re.compile(u"\<body.*?\>(.*)\<\/body\>", re.M|re.DOTALL)

    def stripMeta(self, value):
        """
        Due to a speciality of html5lib just the stuff between <body>...</body>
        without whitespaces seems to be equal to the original source.
        """
        if "<body" in value:
            value = self.rxbody.findall(value)[0]
        return " ".join(value.strip().split())

    def cmpHTML(self, a, b):
        self.assertEqual(self.stripMeta(a), self.stripMeta(b))

    def cmpRender(self, input, output, data={}):
        if "<body" not in input:
            input = _sample_begin + input + _sample_end
        result = HTMLTemplate(input).render(data)
        # print HTMLTemplate(input).source.encode("latin1","ignore")
        print "? %r => %r " % (self.stripMeta(input), self.stripMeta(result))
        self.cmpHTML(output, result)

    def testSample(self):
        # Simple self test without any functionality
        self.cmpRender(_data, _data)

        # Variable
        self.cmpRender(
            "Value $a",
            "Value 999",
            dict(a=999))

        # Dotted variables
        #c = Context()
        #c.a = Context()
        #c.a.a = 999
        #self.cmpRender(
        #    "Value ${a.a}. And ${a.a}",
        #    "Value 999. And 999",
        #    c)

def buildTestSuite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

def main():
    buildTestSuite()
    unittest.main()

if __name__ == "__main__":
    main()
