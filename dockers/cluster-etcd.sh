#!/bin/bash
set -e

IP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)

MACHINE_ID=`echo $IP | tr "." " "  | awk '{ print $4 }'`

exec /usr/bin/etcd -d /var/run/etcd/ -f -cl 0.0.0.0 -s $IP:7001 -c $IP:4001 -C 10.0.0.11:7001 -sl $IP -n node-${MACHINE_ID}