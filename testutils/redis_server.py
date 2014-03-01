""" Test redis server
This starts an actual redis server with a test configuration
"""
import subprocess
import time
_redis_bin = "/usr/sbin/redis-server"
class RedisServer(object):
    def __init__(self, port):
        self.process = subprocess.Popen([_redis_bin, "--port", str(port)])
        time.sleep(.1)

    def stop(self):
        self.process.kill()
        time.sleep(.1)

