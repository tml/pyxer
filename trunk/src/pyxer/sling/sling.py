# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

"""
1 Download Sling Standalone Version

2 Start like this

java -jar org.apache.sling.launchpad.app-3-incubator.jar -a 127.0.0.1 -p 7777 -f -
(Default user for writing is admin/admin)

3 Connect to Sling

Links:

http://code.google.com/p/pysolr/

Eclipse Plugin

http://www.day.com/eclipse/

RMI //localhost:1099/jackrabbit Default

"""

import base64
import urllib2

from  urllib import quote_plus, urlencode
quote = quote_plus

import simplejson
json_encode = simplejson.dumps
json_decode = simplejson.loads

import logging
log = logging.getLogger(__name__)

class SlingObject(dict):

    def __getattr__(self, name):
        try:
            return dict.__getattr__(self, name)
        except:
            return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def __repr__(self):
        return "<SlingObject %r, type %r, properties %r>" % (
            self.get("jcr:path", "???"),
            self.get("jcr:primaryType", "???"),
            ", ".join([o for o in sorted(self) if not o.startswith("jcr:")])
            )

class Sling(object):

    def __init__(self, host, port=7777, user="admin", password="admin"):
        self.host = host
        self.port = port
        self.baseurl = "http://%s:%s" % (host, port)
        self.user = user
        self.password = password
        self.authentication = base64.encodestring('%s:%s' % (user, password))[:-1]

        #auth_handler = urllib2.HTTPBasicAuthHandler()
        #auth_handler.add_password(realm=None, uri=self.baseurl, user=user, passwd=password)
        #self.opener = urllib2.build_opener(auth_handler)
        # urllib2.install_opener(opener)

    def call(self, path, post=None):
        try:
            conn = None
            url = self.baseurl + path
            log.debug("Sling request %r with params %r", url, post)
            if isinstance(post, dict):
                req = urllib2.Request(url, urlencode(post))
                # Need authentication to write data
                req.add_header("Authorization", "Basic %s" % self.authentication)
                conn = urllib2.urlopen(req)
            else:
                req = urllib2.Request(url)
                # Not needed but nice to have
                req.add_header("Authorization", "Basic %s" % self.authentication)
                conn = urllib2.urlopen(req)
        except urllib2.HTTPError, err:
            conn = err
            log.debug("HTTP error code %s", err.code)
            # print err.errno, err.code, dir(err)
            # log.exception("HTTP error\n%s", err.read())
            # raise
        return conn

    def callJSON(self, path, post=None):
        conn = self.call(path, post)
        data = conn.read()
        log.info("Request result %r", data)
        data = json_decode(data)
        if isinstance(data, list):
            data = [SlingObject(o) for o in data]
        elif isinstance(data, dict):
            data = SlingObject(data)
        return data

    def getSessionInfo(self):
        log.info("SESSION INFO")
        return self.callJSON("/system/sling/info.sessionInfo.json")

    def get(self, path):
        log.info("GET %r", path)
        return self.callJSON(path + ".json")

    def query(self, statement, mode="sql", offset=None, rows=None, property=None):
        log.info("QUERY %r, mode: %s", statement, mode)
        assert mode in ["sql", "xpath"]
        # The filename is not relevant
        return self.callJSON(
            "/.query.json?queryType=%s&statement=%s" % (
            mode,
            quote(statement)))

    def xpath(self, statement, **kw):
        return self.query(statement, mode="xpath", **kw)

    sql = query

    def create(self, path="/", data={}, order=None):
        log.info("CREATE %r, data: %r", path, data)
        #if not data.has_key("jcr:primaryType"):
        #    data["jcr:primaryType"] = "nt:unstructured"
        # Check for valid order argument
        if order and (order in ["first", "last"]
            or order.startswith("before ")
            or order.startswith("after ")
            or order.isdigit()):
            data[":order"] = order
        conn = self.call(path, data)
        # Status "created"?
        return conn.code == 201

    update = create

    def delete(self, path):
        log.info("DELETE %r", path)
        conn = self.call(path, {":operation": "delete"})
        return conn.code == 200

    # XXX Todo

    def move(self, from_, to):
        pass

    def copy(self, from_, to):
        pass

def testing():
    import pprint
    sling = Sling("127.0.0.1", 7777)
    log.debug("Connected to Sling %r", sling)

    # print sling.get("/content")
    #print sling.gt("/content")

    # Testing session
    info = sling.getSessionInfo()
    log.debug(info)
    assert info["userID"] == sling.user

    # Cleanup
    success = sling.delete("/testing")
    log.info("Cleanup %r", success)

    # Creating test Data
    success = sling.create("/testing", dict(title="Test", body="Lorem ipsum", footer="Subit"))
    assert success == True

    success = sling.create("/testing", dict(title="Test2", body="Lorem ipsum2"))
    assert success == False

    # Trailing Slash indicates sub entries
    sling.create("/testing/", dict(title="sub1", body="Lorem ipsum sub1"))
    sling.create("/testing/", dict(title="sub2", body="Lorem ipsum sub2"))
    sling.create("/testing/", dict(title="sub3", body="Lorem ipsum sub3"))

    # Content
    obj = sling.get("/testing")
    assert obj.title == "Test2"
    assert obj.body == "Lorem ipsum2"
    assert obj.footer == "Subit"

    # raw_input("WAIT")

    obj = sling.get("/testing/*")
    assert dict(obj) == dict()

    obj = sling.get("/testing/title")
    assert obj.title == "Test2"

    # Query XPATH
    result1 = sling.xpath("//*[@jcr:primaryType='nt:unstructured']")
    #for obj in result1:
    #    print obj

    result2 = sling.sql("select * from nt:base where jcr:primaryType='nt:unstructured'")
    #for obj in result2:
    #    print obj

    assert result1 == result2

    # pprint.pprint(sling.xpath("//*"))
    #for obj in sling.xpath("//*"):
    #    print repr(obj)

    # Cleanup
    success = sling.delete("/testing")
    assert success == True
    log.info("Cleanup %r", success)

    #    pprint.pprint(obj)
    # print sling.call("/content.query.json?queryType=xpath&statement=//*").read()

if __name__=="__main__":
    level = logging.DEBUG
    level = logging.INFO
    logging.basicConfig(level=level, format="%(levelname)-7s [%(name)s] %(pathname)s line %(lineno)4d: %(message)s")
    testing()
