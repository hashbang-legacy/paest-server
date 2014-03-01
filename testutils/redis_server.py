""" Test redis server
This starts an actual redis server with a test configuration
"""
import subprocess
import time

# Find redis-server binary. There should be a better way to do this.
TEST_REDIS_BIN = subprocess.check_output(["locate", "/redis-server"]).strip()
class RedisServer(object):
    def __init__(self, port):
        self.process = subprocess.Popen([TEST_REDIS_BIN, "--port", str(port)])
        time.sleep(.1)

    def stop(self):
        self.process.kill()
        time.sleep(.1)

