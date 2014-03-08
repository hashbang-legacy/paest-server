""" Pae.st server """
import tornado.ioloop
from tornado.options import define, options
from tornado.web import RequestHandler
from tornado_cors import CorsMixin
import response
import json

class PaestServer(CorsMixin, RequestHandler):
    """ Paest request handler """
    CORS_ORIGIN = "*"
    CORS_HEADERS = ("Content-Type, Depth, User-Agent,"
                    "X-File-Size, X-Requested-With, X-Requested-By, "
                    "If-Modified-Since, X-File-Name, Cache-Control")
    CORS_CREDENTIALS = True

    # Tornado uses argument unpacking
    # pylint: disable=W0221
    def initialize(self, paestdb, throttler):
        # Tornado uses initialize instead of __init__
        # pylint: disable=W0201
        self.paestdb = paestdb
        self.throttler = throttler
        self.put = self.post

    def request_uid(self):
        """ Create a unique id for this requester.
        This is used during throttling """
        return self.request.headers.get('User-Agent', '') +\
               self.request.remote_ip

    def get(self, p_id, p_key):
        # p_key is not used during get requests
        # pylint: disable=W0613
        if self.throttler and self.throttler.reject(self.request_uid()):
            return response.throttled(self)

        paest = self.paestdb.get_paest(p_id)

        if paest is None:
            return response.not_found(self)
        else:
            return response.raw(self, paest.content)

    def get_post_content(self):
        """Figure out the content of a post
        possibly a file, or an arg """
        content = ""
        if len(self.request.arguments.keys()) == 1:
            content = self.request.arguments.values()[0][0]
        elif len(self.request.files.keys()) == 1:
            content = self.request.files.values()[0][0]['body']
        elif self.request.headers.get("Content-Type","") == "application/json":
            content = json.loads(self.request.body).get("d","")
        return content

    def post(self, p_id, p_key):
        if self.throttler and self.throttler.reject(self.request_uid()):
            return response.throttled(self)

        content = self.get_post_content()
        if not content and p_key:  # Looks like a delete
            if not self.paestdb.delete_paest(p_id, p_key):
                return response.bad_id_or_key(self)
            else:
                return response.paest_deleted(self)
        else:  # Not a delete, try create/update

            paest = None
            updated = False
            if p_key:
                # paest updated.
                updated = self.paestdb.update_paest(p_id, p_key, content)

            if not updated:  # Wasn't an update, or at least failed to update
                # Implement the update_or_create logic
                paest = self.paestdb.create_paest(p_id, p_key, content)
                if paest:
                    p_id = paest.pid
                    p_key = paest.key

            if paest or updated:  # Create or update succeded
                return response.paest_links(self, p_id, p_key)
            else:
                return response.paest_failed(self)


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
        from backends.redisimpl import RedisDB
        return RedisDB(host=options.redis_host,
                       port=options.redis_port,
                       db=options.redis_db)
    # def use_someOtherDB():
    #   import your code
    #   create your client

    return {
        "redis": use_redis
        # Add your backend flag here. (Add your options in setup_options)
    }.get(options.backend, lambda: None)()


def get_throttler():
    """ Get a throttling backend """
    def use_redis():
        """ Configure and return a RedisThrottler """
        # pylint reimport warning bug
        # pylint: disable=W0404
        from throttling.redisimpl import RedisThrottler
        return RedisThrottler(host=options.redis_host,
                              port=options.redis_port,
                              db=options.redis_db)

    return {
        "redis": use_redis
    }.get(options.throttler, lambda: None)()


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

    application = get_paest_application(paestdb, throttler)
    application.listen(options.tornado_port)
    tornado.ioloop.IOLoop.instance().start()


def get_paest_application(backend, throttler):
    """ Build the tornado application and router. Using
    the given backend and throttler """
    # Build the matcher.
    # /<paest id>
    # /<paest id>/
    # /<paest id>/<paest key>
    pattern = r"^/?({0}*)/?({0}*).*".format("\w")
    application = tornado.web.Application([
        (pattern, PaestServer, {'paestdb': backend, 'throttler': throttler}),
    ])
    return application


if __name__ == "__main__":
    main()
