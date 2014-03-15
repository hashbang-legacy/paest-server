""" Test redis server
This starts an actual redis server with a test configuration
"""
import subprocess
import time

# Find redis-server binary. There should be a better way to do this.
REDIS_BIN = subprocess.check_output(["whereis", "redis-server"]).split()[1]
class RedisServer(object):
    def __init__(self, port):
        self.process = subprocess.Popen([REDIS_BIN, "--port", str(port)])
        #TODO read processes output, wait for the server to actually come up.
        time.sleep(1)

    def stop(self):
        self.process.kill()
        time.sleep(1)

