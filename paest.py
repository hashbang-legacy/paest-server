""" Pae.st server """
import random
import redis
import tornado.ioloop
from tornado.options import define, options
from tornado.web import RequestHandler

# Setup Redis
define("redis_host", default="localhost", help="Redis server host")
define("redis_port", default=6379, help="Redis server port")
define("redis_db", default=0, help="Redis DB to use")

# Setup Tornado
define("tornado_port", default=80, help="Port to host web server on")

BASE58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def random58(length):
    """ Construct a random BASE58 string the given length """
    chars = [random.choice(BASE58) for _ in xrange(length)]
    return "".join(chars)

class Paest(object):
    """ Paest structure for modeling individual paests. """
    __slots__ = ("pid", "key", "content")
    def __init__(self, pid="", key="", content=""):
        self.pid = pid
        self.key = key
        self.content = content

# TODO: remove this lint disable when other backends are implemented
# pylint: disable=R0922
class PaestDB(object):
    """ An abstraction of the backend 
    allows for replacement backends (including mocks and fakes)
    """

    def create_paest(self, pid, pkey, content):
        """ Attempt to create a paest with the given id and key.
            if pid is "" a pid is generated
            if pkey is invalid, a key is generated
            Returned paest's id and key may not be the same as provided

            Returns None if unable to create a Paest
            Returns Paest is paest created.
        """
        raise NotImplementedError("create_paest not defined")
        
    def get_paest(self, pid):
        """ Fetch a paest by id
            Returns None if no paest found
            Returns Paest if found
        """
        raise NotImplementedError("get_paest not defined")

    def update_paest(self, pid, pkey, pcontent):
        """ Set a paests content
            Returns True if setting was successful
            Returns False otherwise
        """
        raise NotImplementedError("updatePaest not defined")
    
    def delete_paest(self, pid, pkey):
        """ Deletes a paest
            Returns True if deletion was successful
            Returns False otherwise
        """
        raise NotImplementedError("deletePaest not defined")

class RedisDB(PaestDB):
    """ A PaestDB that uses Redis as the backing implementation """

    def __init__(self, redis_client):
        super(RedisDB, self).__init__()
        self.client = redis_client
        self.expire_time = 7 * 24 * 60 * 60 # 1 week
    
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

class PaestServer(RequestHandler):
    """ Paest request handler """
    # Tornado uses argument unpacking
    # pylint: disable=W0221
    def initialize(self, paestdb):
        # Tornado uses initialize instead of __init__
        # pylint: disable=W0201
        self.paestdb = paestdb

        self.put = self.post

    def get(self, p_id, p_key):
        # p_key is not used during get requests
        # pylint: disable=W0613 

        paest = self.paestdb.get_paest(p_id)
        if paest is None:
            self.write("Paest not found")
        else:
            self.write(paest.content)

    def post(self, p_id, p_key):
        req = self.request
        post_contents = req.body_arguments.values()
        #      argument names             value list
        if len(post_contents) != 1 or len(post_contents[0]) != 1:
            self.write("Invalid POST")
            return

        content = post_contents[0][0]

        if not content: # Empty paest, treat as delete
            if self.paestdb.delete_paest(p_id, p_key):
                self.write("Bad paest id or key")
            else:
                self.write("Paest deleted")
            return
        else: # We have content, it's a create/update
            if p_key: # We have a key, it's an update     
                self.paestdb.update_paest(p_id, p_key, content)
                self.write("Paest updated")
            else:
                paest = self.paestdb.create_paest(p_id, p_key, content)
                if not paest: # Woah. We couldn't find a free ID
                    self.write("Paest failed.")
                    return
                self.write("Paest created. {} {}".format(paest.pid, paest.key))
                    
def main():
    """ Define routing, and start the server """
    options.parse_command_line()
    redis_client = redis.StrictRedis(host=options.redis_host,
                                     port=options.redis_port, 
                                     db=options.redis_db)
    paestdb = RedisDB(redis_client)

    # Build the matcher. (<paest id> and <paest key> are base58 strings)
    # /<paest id>
    # /<paest id>/
    # /<paest id>/<paest key>
    base58_regex = "[{}]".format(BASE58)
    pattern = r"^/?({0}+)/?({0}*)".format(base58_regex)

    application = tornado.web.Application([
        (pattern, PaestServer, {'paestdb':paestdb}),
    ])
    
    application.listen(options.tornado_port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
