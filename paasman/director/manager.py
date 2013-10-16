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
from werkzeug import secure_filename
import boto
import boto.ec2
import gevent

from paasman import config
from paasman.director.db import session_scope, session
from paasman.director import models
from paasman.director import exceptions

COREOS_IMAGE = "ami-00000003"

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
        

    def _store_instance_data(self, name, private_ip):
        node = models.Node(
            name=name,
            private_ip=private_ip
        )
        session.add(node)
        session.commit()
        return node

    def store_application(self, name, blob):
        # TODO: impl.
        #   - create folder per app name (_deployments/)
        #   - create a timestamped folder or similar, like 201309301130 + ev. random
        #   - create a symlink for current -> 201309301130
        # or: just save the file as the application-name.js instead without versioning
        return self.storage_path

    def _get_deploy_dir(self, name, blob):
        release_name = datetime.datetime.utcnow().strftime("%Y%m%d%H%M")
        return os.path.join(self.storage_path, name, release_name)

    @property
    def filename(self):
        return self.storage_path
