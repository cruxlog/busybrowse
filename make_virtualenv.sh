#!/bin/sh

VENV=virtualenv-12.0.7/virtualenv.py
URL="https://pypi.python.org/packages/source/v/virtualenv/virtualenv-12.0.7.tar.gz#md5=e08796f79d112f3bfa6653cc10840114"

curl $URL > /tmp/virtualenv.tgz
tar xzf /tmp/virtualenv.tgz -C ./
/usr/bin/python2.7 $VENV --clear ./

rm -rf ./virtualenv*
