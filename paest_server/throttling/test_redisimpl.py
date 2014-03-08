import unittest
import redisimpl
from testutils import redis_server

class TestRedisImpl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = redis_server.RedisServer(1025)
        cls.throttler = redisimpl.RedisThrottler(port=1025)

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_rejects_within_50(self):
        # Perform 50 requests rapidly, there should be at least one rejection
        req = "UniqueString"
        self.assertTrue(any([
            self.throttler.reject(req)
            for _ in xrange(50)]))

    def test_allows_simultaneous_users(self):
        req = "UniqueString"
        self.assertFalse(any([
            self.throttler.reject( req + str(uid) )
            for uid in xrange(50)]))

