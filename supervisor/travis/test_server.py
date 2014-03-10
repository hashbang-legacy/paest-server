import unittest
import server
import hashlib
import os
import urllib2
import json
import tornado.testing
import tornado.ioloop
import tornado.httpserver
import thread

class TestServer(unittest.TestCase):

    @classmethod
    def callback(cls):
        cls.callback_called = True

    @classmethod
    def setUpClass(cls):
        cls.callback_called = False

        cls.digest = hashlib.sha256("").hexdigest()
        cls.headers = {'Authorization': cls.digest}
        authFile = file("test_auth","w")
        authFile.write(cls.digest)
        authFile.close()

        # Configure the app
        server.options.auth_file="test_auth"
        server.restart = cls.callback
        application = server.get_app()
        sock, port = tornado.testing.bind_unused_port()
        cls.loop = tornado.ioloop.IOLoop.instance()
        tserver = tornado.httpserver.HTTPServer(application,
                                               io_loop=cls.loop)
        tserver.add_sockets([sock])
        tserver.start()
        cls.port = port
        thread.start_new_thread(cls.loop.start,())
        cls.url = "http://localhost:{}/".format(cls.port)

    @classmethod
    def tearDownClass(cls):
        cls.loop.stop()
        os.unlink("test_auth")

    def post(self, payload={}, headers={}):
        urllib2.urlopen(urllib2.Request(
            self.url, 'payload='+json.dumps(payload), headers
        )).read()

    def test_should_reload(self):
        self.post({'status_message': 'Passed',
                    'branch': 'master',
                    'type': 'push'}, self.headers)
        self.assertTrue(self.callback_called)
        self.callback_called = False

        # Must pass
        self.post({'status_message': 'Failed',
                    'branch': 'master',
                    'type': 'push'}, self.headers)
        self.assertFalse(self.callback_called)

        # Must be on master
        self.post({'status_message': 'Passed',
                    'branch': 'other_branch',
                    'type': 'push'}, self.headers)
        self.assertFalse(self.callback_called)

        # Must be a push (not pull request)
        self.post({'status_message': 'Passed',
                    'branch': 'master',
                    'type': 'pull'}, self.headers)
        self.assertFalse(self.callback_called)

    def test_get_travis_auth(self):
        self.assertRaises(urllib2.HTTPError, self.post, ({
            'status_message': 'Passed',
            'branch': 'master',
            'type': 'push'}, {}))




