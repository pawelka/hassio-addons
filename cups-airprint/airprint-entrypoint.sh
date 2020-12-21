#!/bin/sh

echo "Setup Cups Airprint"

mkdir -p /data/config
mkdir -p /data/services

rm -rf /config
rm -rf /services 

ln -s /data/config /config
ln -s /data/services /services

export CUPSADMIN="admin"
export CUPSPASSWORD="pass"

/root/run_cups.sh