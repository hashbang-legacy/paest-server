""" Pae.st server """
from base58 import BASE58_REGEX
import tornado.ioloop
from tornado.options import define, options
from tornado.web import RequestHandler


class PaestServer(RequestHandler):
    """ Paest request handler """

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin","*")

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
        post_contents = req.arguments.values()
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
            else:
                paest = self.paestdb.create_paest(p_id, p_key, content)
                p_id = paest.pid
                p_key = paest.key
                if not paest: # Woah. We couldn't find a free ID
                    self.write("Paest failed.")
                    return
            self.write(("#Fragments(#) not required in url:\n"
                        "http://a.pae.st/{PID}#CLI-PUBLIC\n"
                        "http://a.pae.st/{PID}/{KEY}#CLI-PRIVATE\n"
                        "http://pae.st/{PID}#WEB-PUBLIC\n"
                        "http://pae.st/{PID}/{KEY}#WEB-PRIVATE\n"
                        ).format(PID=p_id, KEY=p_key))

def setup_options():
    """ Set up all of the flags for paest (and possible backends) """
    # Various engines in paest.
    define("backend", default="redis", help="Which backend to use",
        group="paest")
    define("throttler", default="redis", help="Which throttler to use",
        group="paest")

    # Setup Tornado Server options
    define("tornado_port", default=80, help="Port to host web server on",
            group="tornado")

    # Redis options
    define("redis_host", default="localhost", help="Redis server host",
            group="redis")
    define("redis_port", default=6379, help="Redis server port", group="redis")
    define("redis_db", default=0, help="Redis DB to use", group="redis")

    options.parse_command_line()

def get_db():
    """ Get (and configure) a paest db backend """
    def use_redis():
        """ Configure and return a RedisDB instance """
        # pylint reimport warning bug
        # pylint: disable=W0404
        from redisdb import RedisDB
        return RedisDB(host=options.redis_host,
                       port=options.redis_port,
                       db=options.redis_db)
    # def use_someOtherDB():
    #   import your code
    #   create your client

    return {
        "redis":use_redis
        # Add your backend flag here. (Add your options in setup_options)
    }.get(options.backend, lambda:None)()

def get_throttler():
    """ Get a throttling backend """
    def use_redis():
        """ Configure and return a RedisThrottler """
        return None # TODO(snail): Implement throttling backend

    return {
        "redis":use_redis
    }.get(options.throttler, lambda :None)()

def main():
    """ Define routing, and start the server """
    setup_options()
    paestdb = get_db()

    if paestdb is None:
        print "Backend unavailable. Exiting."
        exit(1)

    throttler = get_throttler()
    if throttler is None:
        print "Throttling unavailable. Continuing"


    # Build the matcher. (<paest id> and <paest key> are base58 strings)
    # /<paest id>
    # /<paest id>/
    # /<paest id>/<paest key>
    pattern = r"^/?({0}*)/?({0}*)".format(BASE58_REGEX)

    application = tornado.web.Application([
        (pattern, PaestServer, {'paestdb':paestdb}),
    ])

    application.listen(options.tornado_port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
