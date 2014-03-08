#!/bin/bash
#To launch the test suite:
#./run test <args>
#
#To launch the server:
#./run <args>

if [ "$1" == "test" ] ; then
  shift
  echo "Running tests"
  python -m unittest discover $@
else if [ "$1" == "supervisord" ] ; then
  supervisord -c supervisor/supervisord.conf
else if [ "$1" == "supervisorctl" ] ; then
  supervisorctl -c supervisor/supervisord.conf
else
  echo "Launching paest."
  python paest_server/paest.py $@
fi fi fi
