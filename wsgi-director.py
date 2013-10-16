# -*- coding: utf-8 -*-
"""
    authors
    =======
    mikhln-9
    sanpet-8
"""
import sys
import gevent
from gevent import wsgi
from paasman.director import app, manager

from paasman.director import dispatcher
from paasman.director.db import session, session_scope

from sqlalchemy.exc import IntegrityError

if __name__ == "__main__":
    gevent.spawn(dispatcher.worker)
    gevent.spawn(dispatcher.manager)
    gevent.spawn(dispatcher.cluster_listener)
    print "- started dispatcher worker"

    if len(sys.argv) > 1:
        from paasman.director.db import session_scope
        # add the director server to the cluster
        # (also used when we only use on instance for everything)
        
        try:
            with session_scope():
                node = manager._store_instance_data(
                    name="paasman-master",
                    private_ip=sys.argv[1] # assume the data is correct?
                )
                print "added node with name=%s and ip=%s" % (node.name, node.private_ip)
        except IntegrityError as e:
            print "The node name or private ip is already used, see following error message:"
            print e

    print "- starting wsgi-server"
    wsgi.WSGIServer(("", 8001), app).serve_forever()
