# -*- coding: utf-8 -*-

import gevent
import zmq.green as zmq
from gevent.queue import Queue
import etcd
from paasman.director import director_manager, etcd_client
from paasman.director.manager import tasks, publish_queue

import gevent.monkey
gevent.monkey.patch_socket() # make the tcp connection non-blocking

zmq_ctx = zmq.Context()

def worker():
    """Worker that needs to be a singleton worker"""
    while True:
        task = tasks.get()
        print "working: %s" % task

        task_type = task.get("task")
        if task_type:
            if task_type == "add_node":
                director_manager.add_node(
                    name=task.get("name"),
                    ip=task.get("ip")
                )
            if task_type == "delete_node":
                director_manager.remove_node(task.get("name"))
            if task_type == "deploy":
                publish_queue.put_nowait({
                    "task": "deploy",
                    "app_name": task.get("app_name")
                })
        gevent.sleep(0)

def manager():
    socket = zmq_ctx.socket(zmq.REP)
    socket.bind("tcp://*:5111")

    while True:
        r = socket.recv()
        #tasks.put_nowait(r)
        socket.send("you said %s" % r)
        gevent.sleep(0)

def test_publisher():
    publisher = zmq_ctx.socket(zmq.PUB)
    publisher.bind("tcp://*:5555")

    while True:
        #publisher.send("hallo")
        task = publish_queue.get()
        publisher.send(json.dumps(task)) # maybe we need exception handling here (yes we do)
        gevent.sleep(0)

def cluster_listener():
    while True:
        r = etcd_client.watch("services/agents") # blocking
        if r.action == "SET": # adding a node to the cluster
            tasks.put_nowait({
                "task": "add_node",
                "name": r.key.split("/")[-1],
                "ip": r.value
            })
        elif r.action == "DELETE": # a node has gone away
            pass
        gevent.sleep(0)
