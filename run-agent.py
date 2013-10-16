# -*- coding: utf-8 -*-

import gevent
from paasman.agent import event_listener, agent_notifier_runner

if __name__ == "__main__":
    el = gevent.spawn(event_listener)
    notifier = gevent.spawn(agent_notifier_runner)
    gevent.joinall([el, notifier])
