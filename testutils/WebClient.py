""" Helper class to make sending http requests easier"""
import urllib
import urllib2
import json

class WebClient:
    @staticmethod
    def GET(url):
        print "GET:", url
        return urllib2.urlopen(url).read()

    @staticmethod
    def POST(url, values):
        print "POST:", url, values
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        return urllib2.urlopen(req).read()

    @staticmethod
    def POST_JSON(url, data):
        print "POST JSON:", url, data
        data = json.dumps(data)
        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        return urllib2.urlopen(req).read()
