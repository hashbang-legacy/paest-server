""" Test redis server
This starts an actual redis server with a test configuration
"""
import subprocess
import time

# Find redis-server binary. There should be a better way to do this.
REDIS_BIN = subprocess.check_output(["whereis", "redis-server"]).split()[1]
class RedisServer(object):
    def __init__(self, port):
        self.process = subprocess.Popen([REDIS_BIN, "--port", str(port)],
                                        stdout=subprocess.PIPE)
        running = self.waitForStartup()

    def waitForStartup(self):
        line = self.process.stdout.readline()
        while line != "":
            if "The server is now ready" in line:
                return True
            line = self.process.stdout.readline()
        return False

    def stop(self):
        self.process.kill()

