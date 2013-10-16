# -*- coding: utf-8 -*-

import gevent
import zmq.green as zmq
from gevent.queue import Queue
import etcd
from paasman.director import director_manager

tasks = Queue()

zmq_ctx = zmq.Context()

etcd_client = etcd.Etcd("172.17.42.1")

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

        gevent.sleep(0)

def manager():
    socket = zmq_ctx.socket(zmq.REP)
    socket.bind("tcp://*:5111")

    while True:
        r = socket.recv()
        tasks.put_nowait(r)
        socket.send("you said %s" % r)

def cluster_listener():
    while True:
        r = etcd.watch("/services/agents") # blocking
        if r.action == "SET": # adding a node to the cluster
            tasks.put_nowait({
                "task": "add_node",
                "name": r.key.split("/")[-1],
                "ip": r.value
            })
        if r.action == "DELETE": # a node has gone away
            pass