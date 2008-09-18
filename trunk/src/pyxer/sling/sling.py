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

class Sling(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.baseurl = "http://%s:%s" % (host, port)

    def call(self, *a):
        url = self.baseurl + "".join(a)
        print "call:", url
        return urllib2.urlopen(url)

    def getSessionInfo(self):
        obj = self.call("/system/sling/info.sessionInfo.json")
        return obj.read()

    def getContent(self, path):
        obj = self.call(path, ".json")
        return obj.read()

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
    print sling.getContent("/content")
    print sling.getSessionInfo()
    print sling.call("/content.query.json?queryType=xpath&statement=//*").read()
