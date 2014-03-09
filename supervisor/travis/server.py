""" Web server to receive Travis-ci webhooks.
Upon receiving a valid payload, perform a git pull
then restart paest """

from tornado.web import RequestHandler
from tornado.options import define, options
import tornado.web
import subprocess
import json

# Command line flags
define("tornado_port",
    default=80,
    help="Port to host web server on")
define("auth_file",
    default="supervisor/travis/auth",
    help="File containing travis auth key")

def should_reload(payload):
    """ Given a payload from travis, should we reload the server?"""

    if payload.get('status_message','') != 'Passed':
        print "Travis CI not passing"
        return False

    if payload.get('branch','') != 'master':
        print "Travis CI not on master"
        return False

    if payload.get('type','') != 'push':
        print "Travis CI not push"
        return False

    return True

class TravisHandler(RequestHandler):
    """ Handler to listen for travis-ci webhooks"""

    def initialize(self, auth):
        # Tornado uses initialize instead of __init__
        # pylint: disable=W0201, W0221
        """ Setup the handler to accept requests from the given auth token """
        self.auth_token = auth

    def post(self):
        auth = self.request.headers.get("Authorization", "")
        if auth != self.auth_token:
            raise tornado.web.HTTPError(403)

        print "Travis CI triggered"
        content = self.request.body_arguments['payload'][0]
        if not should_reload(json.loads(content)):
            print "Check failed. Not restarting server."
            return

        print "Checks passed. Restarting server"

        subprocess.check_output(["git", "pull"])
        subprocess.check_output(["bash", "run.sh", "supervisorctl",
                                 "restart", "paest"])

def get_travis_auth():
    """ Get the travis ci auth token.
        Returns either None or a string"""
    travispath = options.auth_file
    auth = None
    with open(travispath) as travis_file:
        data = travis_file.read()
        if len(data) != 64: # Simple 'validation' check.
            print "Travis auth file '{}' is invalid".format(travispath)
        else:
            auth = data
    return auth


def main():
    """ Setup the server and run it """

    auth = get_travis_auth()
    if auth is None:
        print "Couldn't get auth token."
        return

    app = tornado.web.Application([
        ("^$", TravisHandler, {'auth': auth})
    ])
    app.listen(options.tornado_port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

