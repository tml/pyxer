import html5lib
from html5lib import treebuilders, serializer, treewalkers
from html5lib.filters import sanitizer
from html5lib.constants import voidElements
import StringIO
import sys
sys.path.insert(0, "C:\work\html5lib")

src = """<!DOCTYPE html>
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
f = StringIO.StringIO(src)
parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
document = parser.parse(f)
print document.toxml()
