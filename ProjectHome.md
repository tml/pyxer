**Sourcecode moved to GITHUB: http://github.com/holtwick/pyxer**

<a href='http://www.youtube.com/watch?feature=player_embedded&v=zz7TvGutSM8' target='_blank'><img src='http://img.youtube.com/vi/zz7TvGutSM8/0.jpg' width='425' height=344 /></a>

# Introduction #

Yet another Python Framework! The goal of this project to make web development
as easy as possible to enable the developer to start quickly with a new project.
This project should be distributable via PasteDeploy for normal servers and for
Google App Engine (GAE), without the need of using different technologies and approaches.

# Example #

Minimal init.py:

```
from pyxer.base import *

@controller
def index():
    return "Hello World"
```

# Templating Language #

Since Genshi does not work on GAE a new Templating Language comes with Pyxer that is very similar to the syntax of Genshi and Kid. Here is a simple example of a controller using a template:

```
from pyxer.base import *

@controller
def index():
    c.somelist=[1,2,3]
```

And the corresponding template named "index.html":

```
<ol>
  <li py:for="value in c.somelist">
   Value: $value
  </li>
</ol>
```

# Online Demo #

The most recent examples can be accessed here:
http://pyxer.appspot.com

