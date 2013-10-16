#!/usr/bin/env bash

#sudo -i



#echo "[Unit]
#Description=Clustered etcd
#After=docker.service

#[Service]
#Restart=always
#ExecStart=/usr/bin/etcd -f -cl 0.0.0.0 -s 10.0.0.10:7001 -c 10.0.0.10:4001 -sl 10.0.0.10 -n masternode

#[Install]
#WantedBy=local.target
#" >> /media/state/units/etcd-paasman.service

#systemctl stop etcd-cluster.service

#rm /media/state/units/etcd-cluster.service

#systemctl restart local-enable.service

# finish with logout (exit)
#exit