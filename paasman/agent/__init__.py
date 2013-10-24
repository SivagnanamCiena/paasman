# -*- coding: utf-8 -*-
"""
    authors
    =======
    mikhln-9
    sanpet-8
"""

import traceback
import sys
import json
import hashlib
import gevent
from gevent.queue import Queue
import etcd
import docker
import zmq.green as zmq
import requests

import gevent.monkey
gevent.monkey.patch_socket()

etcd_client = etcd.Etcd("172.17.42.1")
# we mount the coreos /var/ to /coreos_run/
docker_client = docker.Client("unix://coreos_run/docker.sock")

# tasks that should be sent to the master/director
director_tasks = Queue()
# tasks that should be performed via the docker api
docker_tasks = Queue()

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

print "agent#get_director_ip-1"
director_ip = get_director_ip()
print "agent#get_director_ip-2", director_ip

zmq_ctx = zmq.Context()
#subscriber.connect("tcp://172.17.42.1:5555") # TODO: 172.17.42.1 on a single node, change when clustering to read key in etcd

#teller.connect("tcp://172.17.42.1:5111") # 172.17.42.1 on a single node, change when clustering to to read key in etcd

class Agent(object):
    def __init__(self, ip=None):
        self.ip = ip
        self._apps = {}
        self._containers = {} # for fast lookups

    def add_container(self, app_name, container_id):
        if not app_name in self._apps: self._apps[app_name] = []
        self._apps[app_name].append(container_id)
        self._containers[container_id] = app_name

    def remove_container(self, container_id):
        app = self._containers.get(container_id)
        if app:
            self._apps.get(app).remove(container_id)
            del self._containers[container_id]

    def get_containers(self, app_name):
        return self._apps.get(app_name, [])

    def get_app_by_container_id(self, container_id):
        return self._containers.get(container_id)

agent_manager = Agent()

def event_listener():
    teller = zmq_ctx.socket(zmq.REQ)
    teller.connect("tcp://%s:5111" % director_ip)
    print "event_listener", director_ip

    #print docker_client.info()
    while True:
        try:
            print "event_listener listen for work"
            task = director_tasks.get()
            print "send to master", task
            teller.send(json.dumps(task))
            response = teller.recv() # blocking, wait on response from server
            # we may use timeout on recv and put the request to an internal queue and
            #   when the master response, we send the queued commands
            print "after response:", response
            #gevent.sleep(5) # wait 5 seconds since we doesn't want to send a flood of messages
            # but we should block on the director_tasks later
        except zmq.ZMQError as e:
            print "event_listener-error:", e
            if e.errno == zmq.EAGAIN:
                gevent.sleep(0) # this isn't neccessary anymore...TODO: remove this.
        except Exception as e:
            print "event_listener", e
            traceback.print_exc(file=sys.stdout)
        finally:
            gevent.sleep(0)

def subscriber_listener():
    subscriber = zmq_ctx.socket(zmq.SUB)
    subscriber.connect("tcp://%s:5555" % director_ip)
    subscriber.setsockopt(zmq.SUBSCRIBE, "")
    print "subscriber_listener", director_ip

    while True:
        try:
            print "subscriber_listen"
            msg = subscriber.recv()
            print msg
            task = json.loads(msg)
            task_type = task.get("task")
            if task_type == "deploy":
                docker_tasks.put_nowait(task) # just send the task dict
            elif task_type == "undeploy":
                docker_tasks.put_nowait(task) # just send the task dict
        except Exception as e:
            print "subscriber_listener", e
            traceback.print_exc(file=sys.stdout)
        finally:
            gevent.sleep(0)


def docker_listener():
    """Listening on events from docker to get notified when changes happen
    to example handle stopped containers.
    """
    while True:
        try:
            response = docker_client.get(docker_client._url("/events"), stream=True)
            builder = []
            for c in response.iter_content(1):
                builder.append(c)
                if c == "}":
                    result = json.loads("".join(builder))
                    #director_tasks.put_nowait(result)
                    docker_tasks.put_nowait({
                        "task": "docker_event",
                        "payload": result
                    })
                    print "put task in docker_tasks"
                    builder = [] # reset
        except Exception as e:
            print "ERROR: docker_listener", e
            traceback.print_exc(file=sys.stdout)
        finally:
            gevent.sleep(0)


def docker_worker():
    """Manage a queue and perform actions via the hosts docker remote api

    Note that this worker doesn't tell the director of the added or stopped/killed containers,
    instead the docker_listener is responsible for that.
    """
    while True:
        print "docker says hi!"
        task = docker_tasks.get()
        print "docker_worker received work!"
        task_type = task.get("task")

        if task_type == "deploy":
            app_name = task.get("app_name")
            remove = task.get("remove")

            if remove:
                # we remove the existing containers for this app.
                # TODO: change method when we allow cluster deploys
                for c_id in agent_manager.get_containers(app_name):
                  docker_client.kill(c_id) # or stop? probably kill?
                  agent_manager.remove_container(c_id)

            # TODO: this just create instances of new containers to test how it works
            #       and atm just create a single container
            deploy_instruction = task.get("deploy_instruction")
            print "deploy_instruction", task
            processes = deploy_instruction.get(agent_manager.ip)
            if processes:
                for x in xrange(processes):
                    try:
                        container = docker_client.create_container(
                            image="paasman/apprunner",
                            command=["./paasman-node/runner.sh"],
                            environment={
                            "APP_NAME": app_name
                        })
                        docker_client.start(container.get("Id"))
                        print "Container with id=%s started!" % container.get("Id")
                        agent_manager.add_container(app_name, container.get("Id"))
                    except Exception as e:
                        print "deploy", e
                        traceback.print_exc(file=sys.stdout)
        elif task_type == "undeploy":
            app_name = task.get("app_name")
            for c_id in agent_manager.get_containers(app_name):
                docker_client.kill(c_id) # or stop? probably kill?
            director_tasks.put_nowait({
                "task": "undeployed",
                "app_name": app_name
            })
        elif task_type == "docker_event":
            print "docker_task:", task
            docker_task = task.get("payload")
            if docker_task.get("status") == "start" and docker_task.get("from") == "paasman/apprunner:latest":
                try:
                    app_name = agent_manager.get_app_by_container_id(docker_task.get("id"))

                    exposed_port = docker_client.port(docker_task.get("id"), "80")
                    uri = "http://%s:%s" % (agent_manager.ip, exposed_port)

                    director_tasks.put_nowait({
                        "task": "add_process",
                        "app_name": app_name,
                        "uri": uri,
                        "container_id": docker_task.get("id")
                    })
                except Exception as e:
                    print "docker_event/start", e
                    traceback.print_exc(file=sys.stdout)
            elif docker_task.get("status") in ("kill", "die") and docker_task.get("from") == "paasman/apprunner:latest":
                app_name = agent_manager.get_app_by_container_id(docker_task.get("id"))
                director_tasks.put_nowait({
                    "task": "remove_process",
                    "app_name": app_name,
                    "container_id": docker_task.get("id")
                })
        #d.create_container("paasman/apprunner", [u'./paasman-node/runner.sh'], environment={"APP_NAME": "mikael"})
        gevent.sleep(0)



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
            gevent.sleep(14)
            # TODO: wrap in try-except block?
        except Exception as e:
            print "agent_notifier_runner:", e
            gevent.sleep(0)
        

