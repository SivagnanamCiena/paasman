# -*- coding: utf-8 -*-

import sys
import gevent
import requests
from paasman.agent import agent_manager, event_listener, agent_notifier_runner, docker_listener, docker_worker, subscriber_listener

if __name__ == "__main__":
    host = requests.get("http://169.254.169.254/latest/meta-data/local-ipv4").text if len(sys.argv) < 2 else sys.argv[1]
    # TODO: change from 10.0.0.10 to read openstack local-ipv4

    agent_manager.ip = host

    el = gevent.spawn(event_listener)
    notifier = gevent.spawn(agent_notifier_runner, host)
    dock_listener = gevent.spawn(docker_listener)
    dock_worker = gevent.spawn(docker_worker)
    subsc = gevent.spawn(subscriber_listener)
    gevent.joinall([el, notifier, dock_listener, dock_worker, subsc])
