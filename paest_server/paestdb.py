""" Base class for backends for paest """

class Paest(object):
    """ Paest structure for modeling individual paests. """
    __slots__ = ("pid", "key", "content")
    def __init__(self, pid="", key="", content=""):
        self.pid = pid
        self.key = key
        self.content = content

# Used by RedisDB
# pylint: disable=R0921
class PaestDB(object):
    """ An abstraction of the backend 
    allows for replacement backends (including mocks and fakes)
    """

    def create_paest(self, pid, pkey, content):
        """ Attempt to create a paest with the given id and key.
            if pid is "" a pid is generated
            if pkey is invalid, a key is generated
            Returned paest's id and key may not be the same as provided

            Returns None if unable to create a Paest
            Returns Paest is paest created.
        """
        raise NotImplementedError("create_paest not defined")
        
    def get_paest(self, pid):
        """ Fetch a paest by id
            Returns None if no paest found
            Returns Paest if found
        """
        raise NotImplementedError("get_paest not defined")

    def update_paest(self, pid, pkey, pcontent):
        """ Set a paests content
            Returns True if setting was successful
            Returns False otherwise
        """
        raise NotImplementedError("updatePaest not defined")
    
    def delete_paest(self, pid, pkey):
        """ Deletes a paest
            Returns True if deletion was successful
            Returns False otherwise
        """
        raise NotImplementedError("deletePaest not defined")


