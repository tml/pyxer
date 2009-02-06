# -*- coding: UTF-8 -*-

import unittest
from pyxer.template import *
from pyxer.utils import Dict, AttrDict

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
 <br />
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
        result = HTMLTemplate(input).generate(data).render("xhtml")
        # print HTMLTemplate(input).source.encode("latin1","ignore")
        # print "? %r => %r " % (self.stripMeta(input), self.stripMeta(result))
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
        c = Dict()
        c.a = Dict()
        c.a.a = 999
        self.cmpRender(
            "Value ${a.a}. And $a.a",
            "Value 999. And 999",
            c)

        # Dotted variables
        c = Dict(v=(1,2,3))        
        self.cmpRender(
            'A <span py:for="x in v" py:strip>$x</span> Z',
            "A 123 Z",
            c)
        
        # Dotted variables
        c = Dict(v=(1,2,3))        
        self.cmpRender(
            'A <span py:for="x in v">$x</span> Z',
            "A <span>1</span><span>2</span><span>3</span> Z",
            c)
        
def buildTestSuite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

def main():
    buildTestSuite()
    unittest.main()

if __name__ == "__main__":
    main()
