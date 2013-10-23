# -*- coding: utf-8 -*-
"""
    authors
    =======
    mikhln-9
    sanpet-8
"""
import sys
import gevent
import requests
from gevent import wsgi
from paasman.director import manager, dispatcher
from paasman.director.web import app

if __name__ == "__main__":
    # TODO: just tempororary, register the director in etcd under services/director.
    import etcd
    etcd_client = etcd.Etcd("172.17.42.1")
    etcd_client.set("services/director", requests.get("http://169.254.169.254/latest/meta-data/local-ipv4").text)

    wrker = gevent.spawn(dispatcher.worker)
    mangr = gevent.spawn(dispatcher.manager)
    clstr = gevent.spawn(dispatcher.cluster_listener)
    router_uri = gevent.spawn(dispatcher.router_uri_responder)
    # tmp
    t = gevent.spawn(dispatcher.cluster_publisher)
    #gevent.joinall([wrker, mangr, clstr])
    print "- started dispatcher worker"

    print "- starting wsgi-server"
    wsgi.WSGIServer(("", 8001), app).serve_forever()
