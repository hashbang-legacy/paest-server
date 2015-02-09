paest-server [![Build Status](https://travis-ci.org/hashbang/paest-server.png)](https://travis-ci.org/hashbang/paest-server)
============

This project is the backend for [pae.st](http://pae.st/).

If you run this project on its own you can use [curl](https://github.com/paest/paest-server/wiki/CLI-Usage) or [json](https://github.com/paest/paest-server/wiki/JSON-Usage) to create/read/update/delete paests.


To install paest-server:
------------------------
```bash
git clone https://github.com/paest/paest-server.git
cd paest-server
pip install -r requirements.txt
```

To run paest-server:
--------------------

There are three main ways to install and run paest. (And one more developer way)

### The docker way:

```bash
docker run --name redis -d redis
docker run --name paest-api --link redis:redis -p 80:80 hashbang/paest-server
```

### The easy way:

Starting paest this way will work just as well as the advanced way, however restarting the server is not automatic. There is no monitoring. Logs aren't kept, etc... This is much better for testing or generally non-production use.
```bash
# Port 80, using redis db number 0
./run.sh

# Or, with args
./run.sh --tornado_port=1234 --redis_db=1

# To stop paest, simply ctrl-c or kill this process
```

### The advanced way:

This will lauch paest though [supervisord](http://supervisord.org/). This will maintain your binary, logs, uptime, etc...
```bash
# Configure paest's command
$EDITOR supervisor/paest.conf

./run.sh supervisord

# To stop paest, use
./run.sh supervisorctl shutdown
```

### The active development way:

If you have a fork of paest-server, and would like to keep your binary always running your last passing (travis-ci) build.
```bash
# Configure the paest command line
$EDITOR supervisor/paest.conf

# Edit the 3 fields in this file:
$EDITOR supervisor/travis/auth

# Produce the valid auth file
bash supervisor/travis/auth

# Launch paest
./run supervisord
```
