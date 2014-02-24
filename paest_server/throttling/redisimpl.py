""" Throttling service for pae.st backed by redis """
import redis
import time
from . import Throttler
class RedisThrottler(Throttler):
    """ A PaestThrottler implemented in redis """

    def __init__(self, *args, **kwargs):
        super(RedisThrottler, self).__init__()
        self.max_interactions = 10 # 10 interactions
        self.window_size = 10 # per 10 second
        self.client = redis.StrictRedis(*args, **kwargs)

    def reject(self, request):
        """ asf"""
        uid = request.headers.get('User-Agent', '') +\
              request.remote_ip +\
              str(int(time.time()/self.window_size))

        redis_key = "throttler:{}".format(hash(uid))

        val = self.client.incr(redis_key)
        if val == 1:
            self.client.expire(redis_key, self.window_size)

        return val > self.max_interactions

