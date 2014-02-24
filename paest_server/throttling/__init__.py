""" Base class for throttling """
class Throttler(object):
    def reject(self, request):
        raise NotImplementedError("reject not defined")

