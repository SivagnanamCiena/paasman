# -*- coding: utf-8 -*-

import sys
import gevent
from paasman.agent import event_listener, agent_notifier_runner, docker_listener, docker_worker

if __name__ == "__main__":
    host = "10.0.0.10" if len(sys.argv) < 2 else sys.argv[1]
    # TODO: change from 10.0.0.10 to read openstack local-ipv4

    el = gevent.spawn(event_listener)
    notifier = gevent.spawn(agent_notifier_runner, host)
    dock_listener = gevent.spawn(docker_listener)
    dock_worker = gevent.spawn(docker_worker)
    gevent.joinall([el, notifier, dock_listener, dock_worker])
