#1/usr/bin/bash

set -e

PREV=$PWD

cd ~
mkdir dev
cd dev
git clone git@github.com:pbs/pycaption.git 
cd pyvtt
python setup.py install

cd $PREV
