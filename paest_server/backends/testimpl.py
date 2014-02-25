""" Test backend for peast """
from . import PaestDB, Paest
import logging
logging.basicConfig(level=logging.DEBUG)
LOG = logging


class TestDB(PaestDB):
    """ A Testing implementation of a paest backend """
    def __init__(self):
        super(TestDB, self).__init__()
        # Map of paestid to (key, content)
        LOG.info("__init__")
        self.backend = {}

    def create_paest(self, pid, key, content):
        LOG.info("create_paest('{}', '{}', '{}')".format(pid, key, content))
        counter = 0
        if not key:
            key = "DefaultKey"
        if not pid:
            pid = "DefaultPID"

        if pid in self.backend:
            while pid + str(counter) in self.backend:
                counter += 1
            pid = pid + str(counter)
        self.backend[pid] = (key, content)
        return Paest(pid, key, content)

    def update_paest(self, pid, key, content):
        LOG.info("update_paest('{}', '{}', '{}')".format(pid, key, content))
        if pid in self.backend:
            if self.backend[pid][0] == key:
                self.backend[pid] = (key, content)
                return True
        return False

    def get_paest(self, pid):
        LOG.info("get_paest('{}')".format(pid))
        if pid in self.backend:
            return Paest(pid, *self.backend[pid])
        return None

    def delete_paest(self, pid, key):
        LOG.info("delete_paest('{}', '{}')".format(pid, key))
        if self.update_paest(pid, key, ""):
            del self.backend[pid]
            return True
        return False
