# -*- coding: UTF-8 -*-

from pyxer.base import *
import model

log = logging.getLogger(__name__)

router = Router()
router.add("^content\/(?P<name>.*?)$", action="index", name="_content")

@controller
def index():

    # Default values
    c.entry = dict(
        title = "First Page",
        body = "Enter your content here"
        )

    # Get data from database
    result = model.Wiki.query.all()
    if result:
        c.entry = result[0]

@expose
def commit(title, body):
    """
    Write form content into database and jump to index page
    to avoid that a reload of the page creates a duplicate entry.
    """

    log.debug("Wiki entry %r %r", title, body)

    # Using Elixir
    model.Wiki(title=title, body=body)
    model.commit()

    # Redirect to index
    redirect(".")
