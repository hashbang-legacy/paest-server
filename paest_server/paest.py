""" Pae.st server """
import tornado.ioloop
from tornado.options import define, options
from tornado.web import RequestHandler
from json import dumps

class Response:
    """ Resource for the paest responses """
    def __init__(self):
        pass

    @staticmethod
    def _format(fmt, **args):
        """ Format the error messages to json or raw """
        if fmt == ".json":
            return dumps(args)
        else:
            # Raw formats should have exactly 1 arg
            assert(len(args)==1)
            return args.values()[0]

    @staticmethod
    def content_type(rtype):
        """ Paest was not found in backend """
        if rtype == ".json":
            return "application/json"
        return "text/plain"

    @staticmethod
    def not_found(rtype):
        """ Paest was not found in backend """
        return Response._format(rtype, e="paest not found")

    @staticmethod
    def invalid_post(rtype):
        """ POST content was invalid """
        return Response._format(rtype, e="invalid post")

    @staticmethod
    def bad_id_or_key(rtype):
        """ Returning a raw block of data """
        return Response._format(rtype, e="bad id or key")

    @staticmethod
    def paest_deleted(rtype):
        """ Returning a raw block of data """
        return Response._format(rtype, e="paest deleted")

    @staticmethod
    def raw(rtype, data):
        """ Returning a raw block of data """
        return Response._format(rtype, d=data)

    @staticmethod
    def paest_failed(rtype):
        """ Creating a paest failed. """
        return Response._format(rtype, e="Paest Failed")

    @staticmethod
    def paest_links(rtype, p_id, p_key):
        """ Response for update/create calls """
        # Using **, I could probably fix this, but I don't wanna!
        # pylint: disable=W0142
        urls = {
            "web_pub": "http://pae.st/{}".format(p_id),
            "web_pri": "http://pae.st/{}/{}".format(p_id, p_key),
            "cli_pub": "http://a.pae.st/{}".format(p_id),
            "cli_pri": "http://a.pae.st/{}/{}".format(p_id, p_key)
        }

        if rtype == ".json":
            return Response._format(rtype, **urls)
        else:
            return ("#Fragments(#) not required in url:\n"
                    "{cli_pub}#CLI-PUBLIC\n"
                    "{cli_pri}#CLI-PRIVATE\n"
                    "{web_pub}#WEB-PUBLIC\n"
                    "{web_pri}#WEB-PRIVATE\n").format(**urls)

class PaestServer(RequestHandler):
    """ Paest request handler """

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin","*")

    # Tornado uses argument unpacking
    # pylint: disable=W0221
    def initialize(self, paestdb, throttler):
        # Tornado uses initialize instead of __init__
        # pylint: disable=W0201
        self.paestdb = paestdb
        self.throttler = throttler
        self.put = self.post

    def get(self, p_id, p_key, rtype):
        # p_key is not used during get requests
        # pylint: disable=W0613
        if self.throttler and self.throttler.reject(self.request):
            raise tornado.web.HTTPError(403)

        self.set_header("Content-Type", Response.content_type(rtype))
        paest = self.paestdb.get_paest(p_id)
        if paest is None:
            self.write(Response.not_found(rtype))
        else:
            self.write(Response.raw(rtype, paest.content))

    def post(self, p_id, p_key, rtype):
        if self.throttler and self.throttler.reject(self.request):
            raise tornado.web.HTTPError(403)
        self.set_header("Content-Type", Response.content_type(rtype))

        content = ""
        if len(self.request.arguments.keys()) == 1:
            content = self.request.arguments.values()[0][0]
        elif len(self.request.files.keys()) == 1:
            content = self.request.files.values()[0][0]['body']
        else:
            self.write(Response.invalid_post(rtype))
            return


        if not content: # Empty paest, treat as delete
            if self.paestdb.delete_paest(p_id, p_key):
                self.write(Response.bad_id_or_key(rtype))
            else:
                self.write(Response.paest_deleted(rtype))
            return
        else: # We have content, it's a create/update
            if p_key: # We have a key, it's an update
                self.paestdb.update_paest(p_id, p_key, content)
            else:
                paest = self.paestdb.create_paest(p_id, p_key, content)
                p_id = paest.pid
                p_key = paest.key
                if not paest: # Woah. We couldn't find a free ID
                    self.write(Response.paest_failed(rtype))
                    return
            self.write(Response.paest_links(rtype, p_id, p_key))

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
        # pylint reimport warning bug
        # pylint: disable=W0404
        from redisthrottler import RedisThrottler
        return RedisThrottler(host=options.redis_host,
                              port=options.redis_port,
                              db=options.redis_db)

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


    # Build the matcher.
    # /<paest id>
    # /<paest id>/
    # /<paest id>/<paest key>
    pattern = r"^/?({0}*)/?({0}*)(\.json)?".format("\w")

    application = tornado.web.Application([
        (pattern, PaestServer, {'paestdb':paestdb, 'throttler':throttler}),
    ])

    application.listen(options.tornado_port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
