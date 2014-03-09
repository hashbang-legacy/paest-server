""" Responses for paest server requests """
from json import dumps

# Formatters
class Format(object):
    """ Base class for various output formats"""

    def format(self, **kwargs):
        """ Formatting callback """
        raise NotImplementedError()

    def content_type(self):
        """ Content-Type header value"""
        raise NotImplementedError()


class Plain(Format):
    """ Plain text response format """
    def format(self, **arg_dict):
        """ Plain text output """
        assert(len(arg_dict) == 1)
        return arg_dict.values()[0]

    def content_type(self):
        """ Content type for the plain text output """
        return "text/plain"


class Json(Format):
    """ Json response format """
    def format(self, **arg_dict):
        """ Formatting for json output """
        return dumps(arg_dict)

    def content_type(self):
        """ Content type for a json output"""
        return "application/json"


class Jsonp(Json):
    """ Jsonp response format """

    def __init__(self, callback):
        """ Define a jsonp calback """
        super(Jsonp, self).__init__()
        self.callback = callback

    def format(self, **arg_dict):
        """ Format the args into a jsonp callback """
        return "{}({})".format(
            self.callback,
            super(Jsonp, self).format(**arg_dict))

    def content_type(self):
        """ Content type for jsonp """
        return "application/javascript"


def __get_formatter(request):
    """ Try to figure out the format that the request is using"""
    if "callback" in request.arguments:
        fmt = Jsonp(request.arguments["callback"][0])
    elif request.path.endswith(".json") or \
        request.headers.get("Content-Type","") == "application/json":
        fmt = Json()
    else:
        fmt = Plain()
    return fmt

def __simple_handler(status=200, message=""):
    """ Constructs functions for simple http responses """
    def responder(handler):
        """ Writes out a response status/header/body """
        fmt = __get_formatter(handler.request)
        handler.set_status(status)
        handler.set_header("Content-Type", fmt.content_type())
        if status != 200:
            handler.write(fmt.format(e=message))
        else:
            handler.write(fmt.format(d=message))
    return responder

# Simple responses.
# Poorly formatted names. This needs refactored anyway.
# pylint: disable=C0103
throttled = __simple_handler(403, "Requesting too fast")
not_found = __simple_handler(404, "Paest not found")
bad_id_or_key = __simple_handler(401, "Bad id or key")
paest_deleted = __simple_handler(200, "Paest deleted.")
paest_failed = __simple_handler(400, "Paest failed.")

# Not so simple responses
def raw(handler, content):
    """Raw response, used for dumping content into the response"""
    fmt = __get_formatter(handler.request)
    handler.set_header("Content-Type", fmt.content_type())
    handler.write(fmt.format(d=content))

def paest_links(handler, p_id, p_key):
    """ Response for update/create calls """
    fmt = __get_formatter(handler.request)
    handler.set_header("Content-Type", fmt.content_type())
    # Using **, I could probably fix this, but I don't wanna!
    # pylint: disable=W0142
    urls = {
        "web_pub": "http://pae.st/{}".format(p_id),
        "web_pri": "http://pae.st/{}/{}".format(p_id, p_key),
        "cli_pub": "http://a.pae.st/{}".format(p_id),
        "cli_pri": "http://a.pae.st/{}/{}".format(p_id, p_key),
        "pid": p_id,
        "key": p_key
    }

    if isinstance(fmt, Plain):
        out = ("#Fragments(#) not required in url:\n"
               "{cli_pub}#CLI-PUBLIC\n"
               "{cli_pri}#CLI-PRIVATE\n"
               "{web_pub}#WEB-PUBLIC\n"
               "{web_pri}#WEB-PRIVATE\n").format(**urls)
        handler.write(fmt.format(d=out))
    else:
        handler.write(fmt.format(p=p_id, k=p_key))

