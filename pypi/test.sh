#!/bin/bash

cd ../src
make
python setup.py register -r test
python setup.py sdist upload -r test
