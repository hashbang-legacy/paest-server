from tornado.web import RequestHandler
import json

class TravisHandler(RequestHandler):
    """ Handler to listen for travis-ci webhooks"""

    def initialize(self, auth):
        # Tornado uses initialize instead of __init__
        # pylint: disable=W0201
        """ Setup the handler to accept requests from the given auth token """
        self.auth_token = auth

    def post(self):
        print "post"
        auth = self.request.headers.get("Authorization", "")
        if auth != self.auth_token:
            raise tornado.web.HTTPError(403)

        print "Travis CI triggered"

        content = self.request.body_arguments['payload'][0]
        payload = json.loads(content)
        import pprint
        pprint.pprint(payload)
        if payload.get('type','') != 'push':
            print "Travis CI not push. Quitting"
            return
        if payload.get('branch','') != 'master':
            print "Travis CI not on master. Quitting"
            return
        if payload.get('status_message','') != 'Passed':
            print "Travis CI not passing. Quitting"
            return

        print "Checks passed. Cycling server"
        # Only importing this at shutdown time
        # pylint: disable=W0404
        import subprocess
        subprocess.call(["bash", "restart.sh"])
        exit(0)


