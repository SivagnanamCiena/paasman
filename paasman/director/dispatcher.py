# -*- coding: utf-8 -*-

import collections
import random
import json
import gevent
import hashlib
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
                    "remove": True,
                    "app_name": task.get("app_name"),
                    "deploy_instruction": task.get("deploy_instruction")
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
                else:
                    app.remove_process(task.get("container_id"))
            elif task_type == "upscale":
                # upscale, app_name, 
                app_name = task.get("app_name")
                app = director_manager.get_application(app_name)
                processes = app.get_processes()
                nodes = max(len(director_manager.get_nodes()), 1)

                def _wait_on_agent(app_name, ip):
                    try:
                        print "_wait_on_agent-1"
                        r = etcd_client.watch("services/agents/%s" % hashlib.sha1(ip).hexdigest(), timeout=60)
                        print "_wait_on_agent-2"
                        for x in xrange(3):
                            tasks.put_nowait({
                                "task": "add_min_instance_processes",
                                "app_name": app_name,
                                "target": ip
                            })
                    except:
                        return

                if True:#len(processes)/nodes > 10 and nodes < 4:
                    instances = director_manager.add_vm_instances(1)
                    gevent.spawn(_wait_on_agent, app_name, instances[0].private_ip_address)
                else: # TODO: fix unlimited...
                    tasks.put_nowait({
                        "task": "add_min_instance_processes",
                        "app_name": app_name,
                        "target": None,
                    })
            elif task_type == "add_min_instance_processes":
                app_name = task.get("app_name")
                deploy_target = task.get("target")

                if not deploy_target:
                    app = director_manager.get_application(app_name)
                    processes = app.get_processes()

                    nodes = {ip: 0 for ip in director_manager.get_nodes()}
                    for x in processes:
                        nodes[x.split(":")[0]] += 1
                    deploy_target=min(nodes)

                publish_queue.put_nowait({
                    "task": "deploy",
                    "remove": False,
                    "app_name": app_name,
                    "deploy_instruction": {deploy_target: 1}
                })


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
        if app and app.state == "deployed":
            socket.send(str(random.choice(app._processes)))
        else:
            socket.send("")
        gevent.sleep(0)