from genshi import XML, Stream, QName, Attrs
from genshi.core import START, END, TEXT
from genshi.template import Context

#c = Context(a=1)
#print c.a

if 0:
    stream = XML(
        '<html xmlns:py="some">'
        '<p class="intro" py:if="0">Some text and '
        '<a href="http://example.org/">a link</a>.'
        '<br/></p></html>')

    for a in stream:
        print a

    #for output in stream.serialize():
    #    print `output`

    substream = stream.select('//a')
    print substream

    #substream = Stream(list(stream.select('a')))
    #print repr(substream)

    #print stream.render('html')

my = Stream([])
l = [
    (START, (QName(u'a'), Attrs([(QName(u'href'), u'http://example.org/')])), (None, 1, 63)),
    (TEXT, u'a link', (None, 1, 93)),
    (END, QName(u'a'), (None, 1, 99)),
    (TEXT, u'.', (None, 1, 103)),
    ]

def do(my):
    for ev in l:
        my.events.append(ev)

do(my)
# print "STREAM", repr(my)

#for x in my:
#    print "x", x

print my.select("//a").render("html")
