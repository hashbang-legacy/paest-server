""" Redis backend for peast """
import redis
from paestdb import PaestDB, Paest
from base58 import random58

_WEEK = 7 * 24 * 60 * 60 # 1 Week in seconds

class RedisDB(PaestDB):
    """ A PaestDB that uses Redis as the backing implementation """

    def __init__(self, ttl=_WEEK, *args, **kwargs):
        super(RedisDB, self).__init__()

        self.client = redis.StrictRedis(*args, **kwargs)
        self.expire_time = ttl

    @staticmethod
    def redis_id(pid):
        """ Turn a paest id to a redis key """
        return "paest:{}".format(pid)

    @staticmethod
    def serialize(key, content):
        """ Searialize a paests key and content to a redis entry """
        return "{}:{}".format(key, content)

    @staticmethod
    def unserialize(content):
        """ Break a redis entry into the paests key and content """
        return content.split(":", 1)

    def create_paest(self, p_id, p_key, content):

        # Validate the key
        if not p_key:
            p_key = random58(20)
        else:
            # Check that we can serialize/unserialize with it
            ret = self.unserialize(self.serialize(p_key, "content"))
            if ret != [p_key, "content"]:
                p_key = random58(20)

        # No id requested, or it's in use
        if (not p_id) or self.get_paest(p_id):
            # Find a new id for them.
            for length in xrange(10):
                p_id = random58(length) # Try a paestid of length 1, then 2, etc
                paest = self.get_paest(p_id)
                if not paest:
                    # Found an unused id. Use it
                    break
            else: # We didn't break. That means no luck on a paest id
                return None

        # If we get here, we have an unused p_id and a valid p_key!
        self.client.set(self.redis_id(p_id), self.serialize(p_key, content))
        self.client.expire(self.redis_id(p_id), self.expire_time)
        return Paest(p_id, p_key, content)

    def get_paest(self, pid):
        entry = self.client.get(self.redis_id(pid))
        if entry is None:
            return None
        key, content = self.unserialize(entry)
        self.client.expire(self.redis_id(pid), self.expire_time)
        return Paest(pid, key, content)

    def update_paest(self, pid, key, content):
        paest = self.get_paest(pid)

        if paest is None or paest.key != key:
            return False

        self.client.set(self.redis_id(pid), self.serialize(key, content))
        # self.client.expire(self.redis_id(p_id), self.expire_time)
        return True

    def delete_paest(self, pid, key):
        paest = self.get_paest(pid)

        if paest is None or paest.key != key:
            return False

        self.client.delete(self.redis_id(pid))
        return True


