

# Introduction 'Pyxer Python Framework' #

The Pyxer Server is a very simple [Python](http://www.python.org/) Web Framework that aims to makes starting a new project as easy as it can be. It still works respecting the MVC concept but the files can be mixed in one directory. For a high end solution you should maybe consider using [Pylons](http://pylonshq.com/),[Django](http://www.djangoproject.com/), [TurboGears](http://turbogears.org/) and similar.

This work is inspired by http://pythonpaste.org/webob/do-it-yourself.html.

### Technical background ###

The [Google App Engine (GAE)](http://code.google.com/appengine/) in version 1.1 offers a very restricted Python environment and the developer as to ship arround a lot of limitations. Pyxer helps on this point by providing solutions that also work together with the [WSGI Framework Paste](http://pythonpaste.org/) by Ian Bicking. This way you get the best from both sides: GAE and Paste. To achieve this, some other common third party tools are used like[WebOb](http://pythonpaste.org/webob/) and [VirtualEnv](http://pypi.python.org/pypi/virtualenv) also by Ian Bicking. The templating s based on [Genshi](http://genshi.edgewall.org/).

# Installation #

Install Pyxer using easy\_install from [SetupTools](http://pypi.python.org/pypi/setuptools):

```
$ easy_install pyxer  
```

If you want to use Google App Engine you have to install it separately.

# Quick tutorial #

### Create a new project ###

At first set up a new Pyxer project using the Pyxer command line tool like this:

```
$ pyxer init myexample
```
In the newly created directory myexample you will find a directory structure like the following (on Windows bin will be called Scripts):

```
bin/
public/
lib/
```

Place your files in the public directory.

### Start the server ###

To start the server you may choose between the Paster-Engine:

```
$ xpaster serve
```

Or the GAE-Engine:

```
$ xgae serve  
```

Or use Pyxer command line tool again to use the default engine (which is WSGI from Python standard lib):

```
$ pyxer serve 
```
But you may also use Pyxer without using the command line tools e.g. like this:

```
$ paster serve development.ini 
```

### "Hello World" ###

For a simple "Hello World" just put an index.html file into the public directory with the following content:

```
Hello World
```

This works just like a static server. To use a controller put the file `__init__.py` into the same directory with the following content:

```
@controller
def index():
    return "Hello World"
```

## Controllers ##

Controller, templates and static files are placed in the same directory (usually public). First Pyxer looks for a matching controller. A controller is defined in the `__init__.py` file and decorated by using @controller which is defined in pyxer.base.

```
from pyxer.base import *

@controller
def index():
    return "Hello World"
```

### @expose ###

This controller adds the GET and POST parameters as arguments to the function call (like in CherryPy):

```
from pyxer.base import *

@expose
def index(name="unknown"):
    return "Your name is " + name 
```

### default() ###

If no matching controller can be found the one named default will be called:

```
from pyxer.base import *

@controller
def default():
    return "This is path: " + request.path
```

## Templates ##

This example can be called via / or /index. To use a Pyxer template with this file you may use therender() function or just return None (that is the same as not using return) and the matching template will be used, in this case index.html. The available objects in the template are the same as used by Pylons: `c` = context, `g` = globals and `h` = helpers.

```
from pyxer.base import *

@controller
def index():
    c.title = "Hello World"
```

By default a [Genshi like templating language](http://genshi.edgewall.org/wiki/Documentation/xml-templates.html) is used and output is specified as xhtml-strict. You may want to change that for certain documents e.g. to render a plain text:

```
from pyxer.base import *

@controller(output="plain")
def index():
    c.title = "Hello World"
```

Or use another template:

```
from pyxer.base import *

@controller(template="test.html", output="html")
def index():
    c.title = "Hello World"
```

Or use your own renderer:

```
from pyxer.base import *

def myrender():
    result = request.result
    return "The result is: " + repr(result)

@controller(render=myrender)
def index():
    return 9 + 9 
```

## JSON ##

To return data as JSON just return a dict or list object from your controller:

```
from pyxer.base import *

@controller 
def index(): 
   return dict(success=True, msg="Everything ok")
```

## Response object ##

If you want to have full control and not use a renderer just return the `response` object:

```
@controller
def index():  
    response.headers['content-type'] = 'text/plain'
    response.write("Hello World!")
    return response
```

## Sessions ##

Session are realized using the [Beaker](http://beaker.groovie.org/) package. You can use the variable session to set and get values. To store the session data use session.save(). Here is a simple example of a counter:

```
from pyxer.base import *

@controller
def index():
    c.ctr = session.get("ctr", 0)
    session["ctr"] = c.ctr + 1
    session.save()
```

??? XXX

  1. Looks for a controller (!foo.bar:bar)
  1. If the controller returns a dictionary this will be applied to template (step 2)
  1. Looks for the template (foo/bar.html)

## Deployment ##

To publish your project to GAE you may also use the Pyxer command line tool. First check if the `app.yaml` file contains the right informations like the project name and version infos. Then just do like this:

```
$ pyxer push
```

# Routing #

The routing in Pyxer is based on some conventions by default but can be extended in a very flexible and easy way. By default all public project data is expected to be found in the folder public. If you just put static content there it will behave like you expect it from a normal webserver.

To add controllers to it, start by creating the `__init__.py` file. This makes the folder become a Python package and Pyxer routing will at first evaluate this one before looking for static content.

## Default behaviour ##

The easiest controller looks like this:

```
@controller
def index():
    return "Hello World"
```

This will be called with the following URLs:

```
http://<domain>/
http://<domain>/index
http://<domain>/index.html
http://<domain>/index.htm
```

If the controller has another name as index, these corresponding URLs will match:

```
http://<domain>/<controller>
http://<domain>/<controller>.html
http://<domain>/<controller>.htm
```

There is one other special controller named default. If this one exists all non matching request will be passed to this controller.

If you have sub packages in your public folder like `foo` and `foo.bar`, these will be matched by the corresponding path and in this package the rules described before will apply:

```
http://<domain>/foo/bar/...
```

Everything that does not match will be considered static content. Pyxer tries to match the path relatively to the last matched package.

## Custom routes ##

If you need more sophisticated routing or want to include external packages that are not placed under the public folder you may add your own routing. This is as simple as adding this line to your global space of your module:

```
router = Router()
```

Important! The name of this object has to be router by convention!

To add your own ...

```
router.add("content-{name}", "content")
```

This matches all URL starting with content- while the rest will be saved in req.urlvars as key called name. For example the URL `/content-myentry` will result in a call of the controller contentwhere `req.urlvars["name"]=="myentry"`.

For more complicated routes you may also use the add\_re method, which offers more flexibility. Here is an example that matches the rest of the path after "content/" and passes the value to the controller via `req.urlvars["path"]`:

```
router.add_re("^content/(?P<path>.*?)$",
  controller="index", name="_content")
```

## Relative URL ##

In your templates you should try to often use the h.url() helper. It calculates a URL relative to the matched routes base. For example if we take a look at the add\_re routing example we can see that the path component is under the content component. Let's say we have a controller called edit we like to call from the page created by index, then we can not write it like this:

```
<a href="edit?path=$c.path">Edit</a>
```

That does not always work because this page could have been called via index?path=xyz or viacontent/xyz. To make sure we are get the correct URL corresponding to our modules controller we could write it like this:

```
<a href="${h.url('edit?path=' + c.path)}>Edit</a>
```

Or even better using the feature of h.url that lets you append GET parameters as named arguments of the helper function:

```
<a href="${h.url('edit', path=c.path)}>Edit</a>
```

If you use redirect it will call the url helper too so that relative parts will be translated to absolute ones.

# Templating #

Pyxer offers yet another templating language that is very close to[Genshi](http://genshi.edgewall.org/) and [Kid](http://pypi.python.org/pypi/kid). Beause Genshi did not work with Google App Engine when ''Pyxer'' was started, the new templating tools have been implemented.

For more syntax information have a look here: http://genshi.edgewall.org/wiki/Documentation/xml-templates.html

The following sections describe the general use and the little differences to Genshi.

## Variables and expressions ##

The default templating works similar to most known other templating languages. Variables and expressions are realized like `$<varname>` (where `<varname>` may contain dots!) and `${<expression>}`:

```
Hello ${name.capitalize()}, you won $price.
$item.amount times $item.name.
```

## Commands ##

These are also known form templating languages like Genshi and Kid. They are used like this:

```
<div py:if=”name.startswith('tom')”>Welcome $name</div>
```

Or this:

```
<div py:for=”name in sorted(c.listOfNames)”>Welcome $name</div>
```

These are the available commands. They behave like the Genshi equivalents:

  * !py:if ~~... !py:else ... !py:elif~~
  * !py:for ~~... !py:else~~
  * !py:def
  * !py:match
  * !py:layout ~~/ !py:extends~~
  * ~~!py:with~~
  * !py:content
  * !py:replace
  * !py:strip
  * !py:attrs

## Comments ##

If HTML comments start with "!" they are ignored for output:

```
<!--! Invisible --> <!-- Visible in browsers --> 
```

## Layout templates ##

The implementation of layout templates is quite easy. Place the !py:layout command in the `<html>`tag and pass a Template object. For loading you can use the convenience function load().

```
<html py:layout="load('layout.html')">
  ...
</html>
```

In the template file you can then access the original template stream with the global variable top. Use CSS selection or XPATH to access elements. Example:

```
<html>
  <title py:content="top.css('title')"></title>
  <body>
    <h1><a href="/">Home</a>
        / ${top.select('//title/text()')}</h1>
    <div class="content">	 
      ${top.css('body *')}
    </div>
  </body>
</html>

```

**XPath Selectors**

XPath is supported like it is in Genshi.

**CSS Selectors**

CSS Selectors ending with  **(notice the space) return just the inner texts and elements of the matched pattern.**

# Databases #

You are free to use any database model you like. For GAE you do not have much choice. But for other engines I recommend using [Elixir](http://elixir.ematia.de/). You should try to separate your controller stuff from your database stuff by creating a Python module called model.py. For a GAE project this may look like this:

```
from google.appengine.ext import db
from google.appengine.api import users

class GuestBook(db.Model):
   name = db.StringProperty()
   date = db.DateTimeProperty(auto_now_add=True)
```

While using Elixir you can start like this:

```
xxx
```

XXX See the GuestBook example for a complete demo.

# Advanced #

### Development of Pyxer under GAE ###

If you decide to develop Pyxer you may run into the following problem: each project comes with an own virtual machine (VM) and its own installation of Pyxer in it. So if you change the development version it will have no effect on your installation. Therefore a command pyxer is added that synchronizes the Pyxer installation in the VM with the development version:

```
$ pyxer pyxer  
```

BTW: To install the development version using SetupTools do like this:

```
$ cd <Path_to_development_version_of_Pyxer>
$ python setup.py develop
```

You will have to repeat this each time the version of Pyxer changes, because otherwise the command line tools do not work.

### Writing test cases ###

Since a Pyxer project is based on Paster, writing test cases is quite the same. The most simple test looks like this. (We asume that the test file to will be placed in the root of the project. For normal testing you have do add the root directory, where app.yaml is placed, to sys.path and modify theloadapp argument.):

```
from paste.deploy import loadapp
from paste.fixture import TestApp
import os.path

app = TestApp(loadapp('config:%s' % os.path.abspath('development.ini')))
res = app.get("/")
assert ('<body' in res)
```

For more informations about testing look here http://pythonpaste.org/testing-applications.html.

### Use within Eclipse ###

xxx

### Use Google App Engine Launcher on Mac OS ###

xxx

### Pyxer on Apache ###

If you have installed mod\_python the deployment of your project is as simple as writing the following five lines. Just copy them to your sites configuration and adjust the absolute path to thedevelopment.ini:

```
<Location "/">
  SetHandler python-program
  PythonHandler paste.modpython
  PythonOption paste.ini /<absolute_path_to_ini_file>/development.ini
</Location>
```

### Configuration ###

Pyxer configuration is placed in the configuration file used by Paster or GAE respectivelydevelopment.ini or gae.ini. If both are not available Pyxer looks into pyxer.ini. Example:

```
[pyxer]
session = beaker 
```

# Engines #

XXX

Pyxer uses support different so called "engines" to publish a project. Most of them need own configurations and a well prepare environment to work fine. These are very specific to each of these engines and ''Pyxer'' tries to make the setup as easy as possible

Common options:

  * --host=HOST (default: 127.0.0.1)
  * --port=PORT (default: 8080)

## WSGI ##

```
$ pyxer serve 
```

## Paster ##

Options:

  * --reload XXX

With the virtual machine:

```
$ xpaster serve --reload
```

Without the virtual machine:

```
$ paster serve development.ini
```

## Google App Engine ##
```
$ xgae serve
```

# Utilities #

## Using reCaptcha ##

To make websites safe against abuse Pyxer integrates support for [reCaptcha](http://www.recaptcha.net/). You have to register your web sites URL for free there to get a private and public key. To use them see the following demo:

```
from pyxer import recaptcha
	
CAPTCHA_PUBLIC = "XXX"
CAPTCHA_PRIVATE = "XXX"

@expose
def myform(**kw):
    # This creates the HTML code for the captcha input field
    c.captcha = recaptcha.html(CAPTCHA_PUBLIC)
    # Do some more form stuff here
    pass
    # Test if the captcha has been correct
    if recaptcha.test(CAPTCHA_PRIVATE):
        # Do something like storing the data into the database
        pass
        # After success jump to another page
        return redirect("success_info")
```

The corresponding template myform.html could look like this:

```
<form action="">
  <!-- add more input fields here -->
  $c.captcha
  <input type="submit" />
</form>
```

## Date, time and time zone ##

Handling of timezones is tricky in Python and on GAE. Therefore I will give a little introduction how this can be done quite easy. First you should install [pytz](http://pytz.sourceforge.net/) like this:

```
$ pyxer vm
(vm)$ easy_install pytz
```

If you want to show a datetime from Googles datastore you can now do like this in your templates:

```
Local time ${h.strftime(entry.added, '%H:%M', 'Europe/Berlin')}
```

## Image upload ##

Simple upload GAE:

```
@expose
def upload(image=None):
    if image is not None:
        Images(image=db.Blob(image.file.read())).put()
```

Simple out:

```
@expose
def show():
    image = Images.all().get() #???
    if image.image:
        response.headers['Content-Type'] = 'image/jpeg'
        response.body_file.write(image.image)
    return "NO IMAGE"
```

# Appendix #

## Reserved names ##

The following names can not be used in your code to name variables, functions or
other objects, because they are reserved for Pyxer:

  * index: Name of the root controller
  * default: Name of the collecting controller
  * router: Name of the routing object
  * session: Session
  * req, request
  * resp, response
  * cache
  * c
  * g
  * h
  * config