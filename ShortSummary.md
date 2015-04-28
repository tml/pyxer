# Introduction #

Pyxer is a lot about 'conventions' and 'simplicity'. If you like it more 'explicit' it might not be what you are looking for ;)

# Installation #

To get started you need to have SetupTools (easy\_install) installed on
your system. So installing Pyxer is like this:

```
$ easy_install pyxer
```

# Setup a new project #

Now to set up a new project go into an empty directory and type:

```
$ pyxer init
```

You get everything there you need, including an 'app.yaml' file that
you might modify a bit, but you don't have to to get started. All
Python packages go into the sub directory 'site-packages'. To install
new packages just drop them there or use pyxer as an easy\_install
replacement like:

```
$ pyxer install pygments
```

Now it's time to start the server like you always do, e.g.:

```
$ dev_appserver.py .
```

# The 'public' folder keeping web site stuff #

For coding have a look into the 'public' folder. If you have static
content, just drop it there and it will be served. For controllers
make the folder an Python package by adding the 'init.py  file. A
simple example could then look like this:

```
from pyxer.base import *

@expose
def index(q='nothing'):
    return 'The GET variable q contains: %s' % q
```

If you now call 'http://localhost:8080/?q=Hello' you get the output
'The GET variable q contains: Hello'.

# JSON #

If you return lists or dictionaries, the output will be send in JSON
format.

# Templating #

If you do not return or return 'None' Pyxer is looking for a
template with the same name as the controller plus a '.html' suffix,
e.g.

```
@expose
def test():
    c.message = 'Hello World'
```

This will look for the file 'test.html' in the same directory. This is
handled as a template which supports a templating language that is
very close to Genshi, but less restrictive. So this could be our
template 'test.html':

```
<html>
  <head>
  <title py:content='c.message'></title>
  </head>
  <body>
    This is a message: $c.message
  </body>
</html>
```

'c' is a pseudo global variable that is used as the 'context' for
passing values to the template. There are more of these e.g. for
session handling or request data. See the documentation for more
details.