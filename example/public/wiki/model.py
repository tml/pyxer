# -*- coding: UTF-8 -*-

import elixir
from elixir import Entity, Field, Unicode, session

import os.path
uri = "sqlite:///" + os.path.dirname(os.path.abspath(__file__)) + "/wiki.sqlite"

elixir.metadata.bind = uri
elixir.metadata.bind.echo = True

class Wiki(Entity):
    title = Field(Unicode(255))
    body = Field(Unicode)

    def __repr__(self):
        return '<Wiki "%s" (%s)>' % (self.title, self.body)

elixir.setup_all(True)

commit = elixir.session.commit

if __name__=="__main__":
    a = Wiki(title="Test", body="Here goes the text")
    print a
    commit()
    print Wiki.query.all()
