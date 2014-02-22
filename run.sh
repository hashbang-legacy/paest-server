#!/bin/bash
#To launch the test suite:
#./run test <args> 
#
#To launch the server:
#./run <args>

if [ "$1" == "test" ]
then 
shift
echo "Running tests"
python paest_server/tests.py $@
else
echo "Launching paest."
python paest_server/paest.py $@
fi
