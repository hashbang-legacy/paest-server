""" Test redis server
This starts an actual redis server with a test configuration
"""
import subprocess
import time

class RedisServer(object):
    def __init__(self, port):
        subprocess.Popen(['which', 'redis-server'])
        subprocess.Popen(['locate', 'redis-server'])
        self.process = subprocess.Popen(["redis-server", "--port", str(port)])
        time.sleep(.1)

    def stop(self):
        self.process.kill()
        time.sleep(.1)

