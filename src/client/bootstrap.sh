#!/bin/bash
sudo stop client

apt-get update 
export DEBIAN_FRONTEND=noninteractive

# python
apt-get install --force-yes -y python3
apt-get install --force-yes -y python3-pip

# run script
pip3 install requests

# copy contents
sudo cp client/client.conf /etc/init

sudo initctl reload-configuration
sudo start client