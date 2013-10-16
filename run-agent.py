# -*- coding: utf-8 -*-

import sys
import gevent
from paasman.agent import event_listener, agent_notifier_runner

if __name__ == "__main__":
    host = None if len(sys.argv) < 1 else sys.argv[1]

    el = gevent.spawn(event_listener)
    notifier = gevent.spawn(agent_notifier_runner, host)
    gevent.joinall([el, notifier])
