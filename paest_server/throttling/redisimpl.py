""" Throttling service for pae.st backed by redis """
import redis
import time
from . import Throttler


class RedisThrottler(Throttler):
    """ A PaestThrottler implemented in redis """

    def __init__(self, actions=10, window=10, *args, **kwargs):
        """ create a throttler that uses redis during throttling.
        actions - the number of actions allowed during a given window of time
        window - the number of seconds to keep track of actions

        This throttler may allow up to 2*actions in the width of a single window
        of time. This occurs when actions cross the window boundary.

        For example window=3 seconds, actions = 2 (2 actions per 3 seconds)
        :00 -- window starts --
        :01
        :02 action
            action
        :03 -- window starts --
            action
            action
        :04
        :05

            4 actions occured during the 2 second window from :02 to :04
            This is permittable as the average over those two windows is still
            only 2 actions per 3 seconds.
        """
        super(RedisThrottler, self).__init__()
        self.max_interactions = actions
        self.window_size = window
        self.client = redis.StrictRedis(*args, **kwargs)

    def reject(self, request_uid):
        """ Returns True if the request should be rejected """
        uid = request_uid + str(int(time.time()/self.window_size))

        redis_key = "throttler:{}".format(hash(uid))

        val = self.client.incr(redis_key)
        if val == 1:
            self.client.expire(redis_key, self.window_size)

        return val > self.max_interactions
