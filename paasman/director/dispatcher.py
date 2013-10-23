# -*- coding: utf-8 -*-

import random
import json
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
            elif task_type == "delete_node":
                director_manager.remove_node(task.get("name"))
            elif task_type == "deploy":
                publish_queue.put_nowait({
                    "task": "deploy",
                    "app_name": task.get("app_name")
                })
            elif task_type == "undeploy":
                publish_queue.put_nowait({
                    "task": "undeploy",
                    "app_name": task.get("app_name")
                })
            # undeployed app
            elif task_type == "undeployed":
                print "undeployed (via agent)"
                #director_manager.
            elif task_type == "add_process":
                app = director_manager.get_application(task.get("app_name"))
                if not app:
                    print "add_process:", "The application %s doesn't exists" % task.get("app_name", "?")
                    return
                app.add_process(task.get("uri"), task.get("container_id"))
            elif task_type == "remove_process":
                app = director_manager.get_application(task.get("app_name"))
                if not app:
                    print "remove_process:", "the application %s doesn't exists" % task.get("app_name", "?")
                    return
                app.remove_process(task.get("container_id"))

        gevent.sleep(0)

def manager():
    socket = zmq_ctx.socket(zmq.REP)
    socket.bind("tcp://*:5111")

    while True:
        msg = socket.recv()
        message = json.loads(msg)
        tasks.put_nowait(message)
        socket.send("task put in director queue %s" % msg)
        gevent.sleep(0)

def cluster_publisher():
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

def router_uri_responder():
    socket = zmq_ctx.socket(zmq.REP)
    socket.bind("tcp://*:5222")

    while True:
        app_name = socket.recv()
        app = director_manager.get_application(app_name)
        if app:
            socket.send(str(random.choice(app._processes)))
        else:
            socket.send("")
        gevent.sleep(0)