
import urllib
import urllib2

class WebClient:
    @staticmethod
    def GET(url):
        print "GET:",url
        return urllib2.urlopen(url).read()

    @staticmethod
    def POST(url, values):
        print "POST:",url,values
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        return urllib2.urlopen(req).read()


