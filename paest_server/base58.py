""" Base58 util class """
import random

BASE58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
BASE58_REGEX = "[{}]".format(BASE58)

def random58(length):
    """ Construct a random BASE58 string the given length """
    chars = [random.choice(BASE58) for _ in xrange(length)]
    return "".join(chars)

