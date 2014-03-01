""" Test redis server
This starts an actual redis server with a test configuration
"""
import subprocess
import time

TEST_REDIS_BIN = "/usr/bin/redis-server"

class RedisServer(object):
    def __init__(self):
        self.process = subprocess.Popen([TEST_REDIS_BIN, "--port", str(port)])
        time.sleep(.1)

    def stop(self):
        self.process.kill()
        time.sleep(.1)

