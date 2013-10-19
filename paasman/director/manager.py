# -*- coding: utf-8 -*-
"""
    authors
    =======
    mikhln-9
    sanpet-8
"""

import os
import sys
import datetime
import re
from werkzeug import secure_filename
import boto
import boto.ec2
import gevent
from gevent.queue import Queue
from werkzeug import secure_filename

from paasman import config
from paasman.director.db import session_scope, session
from paasman.director import models
from paasman.director import exceptions

COREOS_IMAGE = "ami-00000003"
name_re = re.compile("^([a-zA-Z]+)$")

tasks = Queue()

publish_queue = Queue()

class AgentNode(object):
    def __init__(self, name, ip, updated_at):
        self.name = name
        self.ip = ip
        self.updated_at = updated_at

    def __repr__(self):
        return "Agent(%s, %s, %s)" % (self.name, self.ip, self.updated_at)

class DirectorManager(object):
    """DirectorManager is responsible for handle the deployment of
    applications and manage the deployed instances.
    """

    

    def __init__(self, storage_path):
        self._nodes = {}

        self.storage_path = storage_path

        self.boto_region = boto.ec2.regioninfo.RegionInfo(name="nova", endpoint=config.EC2_ENDPOINT)
        self.boto_conn = boto.connect_ec2(
            aws_access_key_id=config.EC2_KEY_ID,
            aws_secret_access_key=config.EC2_SECRET_KEY,
            is_secure=False,
            region=self.boto_region,
            port=8773,
            path="/services/Cloud"
        )

    def add_node(self, name, ip):
        """Add node add or update a node in its list of known nodes in the cluster"""
        node = AgentNode(
            name=name,
            ip=ip,
            updated_at=datetime.datetime.utcnow()
        )
        self._nodes.update({name: node})

        print "added node, current status:", self._nodes
        return node

    def remove_node(self, name):
        if name in self._nodes:
            del self._nodes[name]
            print "removed node, current status:", self._nodes
            return True
        return False

    def add_vm_instances(self, instances_count):
        """add instances to the cluster"""
        try:
            response = self.boto_conn.run_instances(
                COREOS_IMAGE, 
                key_name="coreos", 
                instance_type="m1.tiny", 
                security_groups=["group2"],
                min_count=instances_count,
                max_count=instances_count
            )

            # TODO: we can skip all code below to wait on ip since we've changed our approach

            # wee need to run response.instances[0].update() until value is "running"
            #   to get the private ip address

            # TODO: change from creating a single instance to multiple

            for instance in response.instances:
                while instance.private_ip_address == "":
                    instance.update()
                    gevent.sleep(0.2)

            return response.instances

            if len(response.instances) > 0:
                nodes = []
                #for instance in response.instances:
                #    nodes.append(self._store_instance_data(
                #        response.instances[0].dns_name,
                #        response.instances[0].private_ip_address
                #    ))
                return nodes
        except Exception as e: # TODO: check exception type?
            raise exceptions.NodeCreationError(e.message)
        

    def deploy_application(self, name, file, processes=1, instances=1):
        """Upload the file to disk and deploys the application within the cluster"""
        try:
            file.save(os.path.join(self.storage_path, "%s.js" % name)) # store all uploads as appname.js
            # TODO: put task on the worker queue to do some logic how this app should
            #       be deployed in the cluster
            tasks.put_nowait({
                "task": "deploy",
                "app_name": name,
                # TODO: add nodes with deployment spec, like nodes: {"node_id-1": 5, "node_id-2": 3} will deploy
                #       8 processes on 2 instances
            })

            return True
        except IOError as e:
            raise exceptions.AppUploadError(e)


    def is_valid_appname(self, name):
        return True if name_re.match(name) else False

    @property
    def is_healthy(self):
        return True if self._nodes else False
