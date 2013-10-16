#!/usr/bin/env bash

sudo -i

# ifconfig enp0s8 | grep 'inet ' | cut -d: -f2 | awk '{ print $2 }' 

IP_ADDR=`ifconfig enp0s8 | grep 'inet ' | cut -d: -f2 | awk '{ print $2 }'`

MACHINE_ID=`echo $IP_ADDR | tr "." " "  | awk '{ print $4 }'`

echo "[Unit]
Description=Clustered etcd
#After=docker.service

[Service]
Restart=always
ExecStart=/usr/bin/etcd -f -cl 0.0.0.0 -s ${IP_ADDR}:7001 -c ${IP_ADDR}:4001 -C 10.0.0.10:7001 -sl ${IP_ADDR} -n node${MACHINE_ID}

[Install]
WantedBy=local.target
" >> /media/state/units/etcd-paasman.service

rm /media/state/units/etcd-cluster.service

systemctl restart local-enable.service