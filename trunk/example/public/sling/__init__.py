# -*- coding: UTF-8 -*-

from pyxer.base import *
from pyxer.sling import Sling, quote

sling = Sling("127.0.0.1", 7777)

router = Router()
router.add_re("^content-(?P<title>.*?)$", controller="index", name="_content")

@expose
def index(title=None):
    result = None
    if title:
        # Get all entries with the correct title
        result = sling.xpath('wiki/*[@title="%s"]' % xpath_escape(title))
    elif title is None:
        # Get first entry
        result = sling.getNodes("wiki", rows=1)

    # New entry
    if not result:
        c.entry = dict(
            title = "",
            body = "",
            path = "")
    else:
        # Get content
        c.entry = sling.get(result[0])
        c.entry.path = result[0]["jcr:path"].split("/")[-1]

    log.debug("Query: %r", c.entry)

@expose
def commit(title, body, path):
    """
    Write form content into database and jump to index page
    to avoid that a reload of the page creates a duplicate entry.
    """
    log.debug("Wiki entry %r %r %r", path, title, body)

    if title:
        if not path:
            path = "*"
        sling.update("/wiki/" + path, dict(
            title=title,
            body=body,
            created="",
            lastModified="",
            createdBy="",
            lastModifiedBy=""))

        # Redirect to index
        # return '<a href=".">Index</a>'
        redirect(".")
    else:
        return "Title is obligatory!"
