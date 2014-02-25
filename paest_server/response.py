""" Responses for paest server requests """
from json import dumps


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


class Response:
    """ Resource for the paest responses """
    def __init__(self, request):
        if "callback" in request.arguments:
            fmt = Jsonp(request.arguments["callback"][0])
        elif request.path.endswith(".json"):
            fmt = Json()
        else:
            fmt = Plain()
        self.fmt = fmt

    def content_type(self):
        """ Content type to set on the response """
        return self.fmt.content_type()

    def not_found(self):
        """ Paest was not found in backend """
        return self.fmt.format(e="paest not found")

    def invalid_post(self):
        """ POST content was invalid """
        return self.fmt.format(e="invalid post")

    def bad_id_or_key(self):
        """ Returning a raw block of data """
        return self.fmt.format(e="bad id or key")

    def paest_deleted(self):
        """ Returning a raw block of data """
        return self.fmt.format(e="paest deleted")

    def raw(self, data):
        """ Returning a raw block of data """
        return self.fmt.format(d=data)

    def paest_failed(self):
        """ Creating a paest failed. """
        return self.fmt.format(e="Paest Failed")

    def paest_links(self, p_id, p_key):
        """ Response for update/create calls """
        # Using **, I could probably fix this, but I don't wanna!
        # pylint: disable=W0142
        urls = {
            "web_pub": "http://pae.st/{}".format(p_id),
            "web_pri": "http://pae.st/{}/{}".format(p_id, p_key),
            "cli_pub": "http://a.pae.st/{}".format(p_id),
            "cli_pri": "http://a.pae.st/{}/{}".format(p_id, p_key)
        }

        if isinstance(self.fmt, Plain):
            return ("#Fragments(#) not required in url:\n"
                    "{cli_pub}#CLI-PUBLIC\n"
                    "{cli_pri}#CLI-PRIVATE\n"
                    "{web_pub}#WEB-PUBLIC\n"
                    "{web_pri}#WEB-PRIVATE\n").format(**urls)
        else:
            return self.fmt.format(**urls)
