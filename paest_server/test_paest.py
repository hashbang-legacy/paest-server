""" Unit tests for various classes in paest_server """
import thread
import unittest
import tornado
import tornado.web
import tornado.testing
from paest_server import paest
from paest_server.backends.testimpl import TestDB
from testutils.WebClient import WebClient
import json
import re
from urllib2 import HTTPError
class PaestTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        application = paest.get_paest_application(TestDB(), None)
        sock, port = tornado.testing.bind_unused_port()
        cls.loop = tornado.ioloop.IOLoop.instance()
        server = tornado.httpserver.HTTPServer(application,
                                               io_loop=cls.loop)
        server.add_sockets([sock])
        server.start()
        cls.port = port
        thread.start_new_thread(cls.loop.start,())

    @classmethod
    def tearDownClass(cls):
        cls.loop.stop()



class E2ETest(PaestTestCase):
    def setUp(self):
        self.url = "http://localhost:{}/".format(self.port)

    def test_no_paest_found(self):
        self.assertRaises(HTTPError, WebClient.GET,
            (self.url + "MissingKey.json"))

        self.assertRaises(HTTPError, WebClient.GET,
            (self.url + "MissingKey"))

        self.assertRaises(HTTPError, WebClient.GET,
            (self.url + "MissingKey?callback=cb"))

    def test_invalid_key_prevents_update(self):
        content = "TestContent"
        content2 = "Other content"
        #Create a paest with id: pid and key: key
        urls = json.loads( WebClient.POST( self.url + "pid/key.json",
                {"d":content}))

        WebClient.POST(self.url +"pid/bad_key", {"d": content2})

        self.assertEqual(content, WebClient.GET(self.url +"pid"))

    def test_json_CRUD(self):
        content = "TestContent"
        content2 = "Other content"

        # Create a paest
        json_output = WebClient.POST_JSON(self.url, {"d": content})

        data = json.loads(json_output)

        self.assertIn("p", data)
        self.assertIn("k", data)

        pid = data["p"]
        key = data["k"]

        # get the paest content (raw) for json append ".json"
        self.assertEqual(content, WebClient.GET(self.url + pid))

        # Update
        WebClient.POST_JSON(self.url + pid + "/" + key, {"d": content2})

        # Check that the update worked
        self.assertEqual(content2, WebClient.GET(self.url + pid))

        # Check that deleting (posting empty content) works
        WebClient.POST_JSON(self.url + pid + "/" + key, {"d": ""})

        self.assertRaises(HTTPError, WebClient.GET, self.url + pid)

    def test_cli_CRUD(self):
        content = "TestContent"
        content2 = "Other content"

        # Create
        cli_output = WebClient.POST(self.url + "", {"d":content})

        # Things that should be greppable
        self.assertIn("CLI-PUBLIC", cli_output)
        self.assertIn("CLI-PRIVATE", cli_output)
        self.assertIn("WEB-PUBLIC", cli_output)
        self.assertIn("WEB-PRIVATE", cli_output)

        pub_url = cli_output.split("#CLI-PUBLIC")[0].split("\n")[-1]
        pri_url = cli_output.split("#CLI-PRIVATE")[0].split("\n")[-1]
        # TODO paest shouldn't have hardcoded outputs here.
        pub_url = pub_url.replace("http://a.pae.st/", self.url)
        pri_url = pri_url.replace("http://a.pae.st/", self.url)

        # Read
        self.assertEqual(content, WebClient.GET(pri_url))
        self.assertEqual(content, WebClient.GET(pub_url))

        # Update
        cli_output2 = WebClient.POST(pri_url, {"d":content2})
        self.assertEqual(cli_output, cli_output2)
        # Check that the update actually happened
        self.assertEqual(content2, WebClient.GET(pub_url))

        # Delete
        WebClient.POST(pri_url, {"d":""})
        self.assertRaises(HTTPError, WebClient.GET, (pub_url))


def main():
    """ Launch unittest's main """
    unittest.main()

if __name__ == "__main__":
    main()


def main():
    """ Launch unittest's main """
    unittest.main()

if __name__ == "__main__":
    main()
