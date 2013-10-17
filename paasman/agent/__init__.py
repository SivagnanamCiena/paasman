# -*- coding: utf-8 -*-
"""
    authors
    =======
    mikhln-9
    sanpet-8
"""

import hashlib
import gevent
from gevent.queue import Queue
import etcd
import docker
import zmq.green as zmq
import requests

import gevent.monkey
gevent.monkey.patch_socket()

# TODO: we should start the etcd process so we can follow leader, or?
etcd_client = etcd.Etcd("172.17.42.1", follow_leader=True)
# we mount the coreos /var/ to /coreos_run/
docker_client = docker.Client("unix://coreos_run/docker.sock")

# tasks that should be sent to the master/director
director_tasks = Queue()

def get_director_ip():
    """trying to get the director address to the master server (ZeroMQ)"""
    try:
        addr = etcd_client.get("services/director")
        return addr.value
    except:
        while True:
            # we may add try-except block here aswell since either requests or etcd may raise exception
            addr = etcd_client.watch("services/director")
            gevent.sleep(0)
            return addr.value

director_ip = get_director_ip()

zmq_ctx = zmq.Context()
subscriber = zmq_ctx.socket(zmq.SUB)
subscriber.connect("tcp://%s:5555" % director_ip)
subscriber.setsockopt(zmq.SUBSCRIBE, "")
#subscriber.connect("tcp://172.17.42.1:5555") # TODO: 172.17.42.1 on a single node, change when clustering to read key in etcd

teller = zmq_ctx.socket(zmq.REQ)
teller.connect("tcp://%s:5111" % director_ip)
#teller.connect("tcp://172.17.42.1:5111") # 172.17.42.1 on a single node, change when clustering to to read key in etcd


def event_listener():
    #print docker_client.info()
    while True:
        try:
            print "send to master"
            teller.send("node is calling")
            response = teller.recv() # blocking, wait on response from server
            # we may use timeout on recv and put the request to an internal queue and
            #   when the master response, we send the queued commands
            print "after response:", response
            gevent.sleep(5) # wait 5 seconds since we doesn't want to send a flood of messages
            # but we should block on the director_tasks later
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                yield
                # gevent.sleep(0)

def subscriber_listener():
    while True:
        msg = subscriber.recv()
        print msg
        gevent.sleep(0)


def docker_listener():
    """Listen och events from docker to get notified when changes happen
    to example handle stopped containers.
    """
    while True:
        try:
            response = docker_client.get(docker_client._url("/events"), stream=True)
            builder = []
            for c in r.iter_content(1):
                builder.append(c)
                if c == "}":
                    result = json.loads("".join(builder))
                    director_tasks.put_nowait(result)
                    print "put task in director_tasks"
                    builder = [] # reset
        except:
            pass
        finally:
            gevent.sleep(0)


def docker_worker():
    """Manage a queue and perform actions via the hosts docker remote api"""
    while True:
        print "docker says hi!"
        gevent.sleep(10)



def agent_notifier_runner(host):
    """Periodically add itself to etcd to announce its existence to the cluster.
    Saved under the keyspace /services/agents/ and with a TTL set to 30 seconds
    TODO: we may use something other than 30 seconds...

    Example: curl -L 172.17.42.1:4001/v1/services/agents/15def24...ac416c0 -d value=10.0.0.10 -d ttl=15
    """
    key = hashlib.sha1(host).hexdigest() # we can of course have the ip as the key too...

    while True:
        try:
            r = etcd_client.set("services/agents/%s" % key, host, ttl=30)
            # TODO: wrap in try-except block?
            gevent.sleep(14)
        except Exception as e:
            print "agent_notifier_runner:", e

