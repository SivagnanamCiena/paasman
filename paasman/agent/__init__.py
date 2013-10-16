# -*- coding: utf-8 -*-
"""
    authors
    =======
    mikhln-9
    sanpet-8
"""

import hashlib
import gevent
import etcd
import docker
import zmq.green as zmq
import requests

# TODO: we should start the etcd process so we can follow leader, or?
etcd_client = etcd.Etcd("172.17.42.1", follow_leader=True)
# we mount the coreos /var/ to /coreos_run/
docker_client = docker.Client("unix://coreos_run/docker.sock")

zmq_ctx = zmq.Context()
subscriber = zmq_ctx.socket(zmq.SUB)
subscriber.connect("tcp://172.17.42.1:5555") # TODO: 172.17.42.1 on a single node, change when clustering to read key in etcd

teller = zmq_ctx.socket(zmq.REQ)
teller.connect("tcp://172.17.42.1:5111") # 172.17.42.1 on a single node, change when clustering to to read key in etcd

try:
    # Try to fetch the directors publish address (in pub/sub)
    director_address = ec.get("services/director/host").value
except:
    director_address = None # or silent set to 172.17.42.1 ?

def director_address():
    """Listening on changes on the director address to the master server (ZeroMQ)"""
    while True:
        #addr = etcd.watch("director_publish_addr")
        #director_address = addr.value
        break

def event_listener():
    #print docker_client.info()
    while True:
        print "send to master"
        teller.send("node is calling")
        response = teller.recv() # blocking, wait on response from server
        # we may use timeout on recv and put the request to an internal queue and
        #   when the master response, we send the queued commands
        print response

        gevent.sleep(5) # wait 5 seconds since we doesn't want to send a flood of messages

def docker_worker():
    """Manage a queue and perform actions via the hosts docker remote api"""


def agent_notifier_runner():
    """Periodically add itself to etcd to announce its existence to the cluster.
    Saved under the keyspace /services/agents/ and with a TTL set to 30 seconds
    TODO: we may use something other than 30 seconds...

    Example: curl -L 172.17.42.1:4001/v1/services/agents/15def24...ac416c0 -d value=10.0.0.10 -d ttl=15
    """
    key = hashlib.sha1(host).hexdigest() # we can of course have the ip as the key too...

    while True:
        r = etcd_client.set("services/agents/%s" % key, host, ttl=30)
        # TODO: wrap in try-except block?
        gevent.sleep(14)

