""" Base class for backends for paest """

# Used by RedisDB
# pylint: disable=R0921
class PaestThrottler(object):
    """ An abstraction for throttlers"""

    def reject(self, request):
        """ Return True if the given request should be rejected """
        raise NotImplementedError("reject not defined")
