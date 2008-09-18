# -*- coding: UTF-8 -*-
#############################################
## (C)opyright by Dirk Holtwick, 2008      ##
## All rights reserved                     ##
#############################################

"""
1 Download Sling Standalone Version

2 Start like this

java -jar org.apache.sling.launchpad.app-3-incubator.jar -a 127.0.0.1 -p 7777

3 Connect to Sling

Links:

http://code.google.com/p/pysolr/

Eclipse Plugin

http://www.day.com/eclipse/

RMI //localhost:1099/jackrabbit Default

"""

import urllib2

from  urllib import quote_plus, urlencode
quote = quote_plus

import simplejson
json_encode = simplejson.dumps
json_decode = simplejson.loads



class SlingObject(dict):
        
    def __getattr__(self, name):
        try:
            return dict.__getattr__(self, name)
        except:
            return self[name]

    def __setattr__(self, name, value):
        self[name] = value


class Sling(object):

    def __init__(self, host, port=7777, user="admin", password="admin"):
        self.host = host
        self.port = port
        self.baseurl = "http://%s:%s" % (host, port)
        
        import base64
        self.authentication = base64.encodestring('%s:%s' % (user, password))[:-1]
        
        #auth_handler = urllib2.HTTPBasicAuthHandler()
        #auth_handler.add_password(realm=None, uri=self.baseurl, user=user, passwd=password)
        #self.opener = urllib2.build_opener(auth_handler)
        # urllib2.install_opener(opener)

    def call(self, *a, **post):
        try:
            conn = None
            url = self.baseurl + "".join(a)
            print "call:", url, "post:", repr(post)
            if not post:
                conn = urllib2.urlopen(url)
            else:
                params = urlencode(post)
                req = urllib2.Request(url, params)                
                req.add_header("Authorization", "Basic %s" % self.authentication)
                conn = urllib2.urlopen(req)
            return conn
        except Exception, e:
            print "ERROR", e.read()
            raise
        
    def getSessionInfo(self):
        obj = self.call("/system/sling/info.sessionInfo.json")
        return json_decode(obj.read())

    def get(self, path):
        obj = self.call(path, ".json")
        return json_decode(obj.read())
    
    def xpath(self, xpath, path="/"):
        obj = self.call(path, ".query.json?queryType=xpath&statement=%s" % quote(xpath))
        return json_decode(obj.read())

    def update(self, path="/", **obj):
        if not obj.has_key("jcr:primaryType"):
            obj["jcr:primaryType"] = "nt:unstructured"
        self.call(path, **obj)

    '''
    /** Remove content by path */
	Sling.removeContent = function(path) {
		var httpcon = Sling.getXHR();
		if (httpcon) {
			var params = ":operation=delete";
			httpcon.open('POST', Sling.baseurl + path, false);

			// Send the proper header information along with the request
			httpcon.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
			httpcon.setRequestHeader("Content-length", params.length);
			httpcon.setRequestHeader("Connection", "close");
			httpcon.send(params);
			return httpcon;
		} else {
			return false;
		}
	}
        '''

if __name__=="__main__":
    sling = Sling("127.0.0.1", 7777)
    
    import pprint
    
    # print sling.get("/content")
    #print sling.get("/content")
    #print sling.getSessionInfo()
    sling.update("/wiki3", title="Title", body="budy budy")
    # pprint.pprint(sling.xpath("//*"))
    #for obj in sling.xpath("//content/test2"):
    #    print obj["jcr:path"], obj["jcr:primaryType"]
    #    pprint.pprint(obj)
    # print sling.call("/content.query.json?queryType=xpath&statement=//*").read()
