#!/bin/bash
sudo stop sequencer

apt-get update 
export DEBIAN_FRONTEND=noninteractive

# python
apt-get install --force-yes -y python3
apt-get install --force-yes -y python3-pip

# run script
pip3 install bottle
pip3 install requests

# copy service configuration
sudo cp sequencer/sequencer.conf /etc/init

sudo initctl reload-configuration
sudo start sequencer