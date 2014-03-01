from testutils.redis_server import RedisServer
import unittest
import redis
class RedisServerTest(unittest.TestCase):

    def test_redis_server_starts(self):
        server = RedisServer(1025)
        client = redis.StrictRedis(port=1025)
        self.assertTrue(client.ping())

        server.stop()
        self.assertRaises(Exception, client.ping)


