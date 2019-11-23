#!/bin/bash

apt-get update 
export DEBIAN_FRONTEND=noninteractive

# python
apt-get install --force-yes -y python3
apt-get install --force-yes -y python3-pip

# mysql
echo 'mysql-server mysql-server/root_password password r00t' | debconf-set-selections
echo 'mysql-server mysql-server/root_password_again password r00t' | debconf-set-selections
apt-get install --force-yes -y mysql-server
apt-get install --force-yes -y libmysqlclient-dev python-dev

# prepare db
mysql -u root -pr00t < bank/schema.sql

# run script
pip3 install bottle
python3 bank/bank.py