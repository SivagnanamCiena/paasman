# -*- coding: utf-8 -*-
"""
    authors
    =======
    mikhln-9
    sanpet-8
"""

# inspiration from https://github.com/rtyler/proxylet/blob/master/proxylet.py

import urlparse
import random
from gevent import wsgi
import requests

#import gevent.monkey
#gevent.monkey.patch_socket()

# TODO: sync this list via gevent and zeromq or other pub/sub
#   or call the director for a list of urls and cache them in the process?
apps = {
    "dev": [
        "http://10.10.10.25:8123",
        "http://10.10.10.25:8124"
    ]
}

proxy_headers = (
    "HTTP_USER_AGENT", "HTTP_ACCEPT_CHARSET", "HTTP_ACCEPT", "HTTP_ACCEPT_LANGUAGE"
)

def router(env, start_response):
    if env.get("REQUEST_METHOD", None) == "GET":
        return proxy(env, start_response)
    # otherwise, just return 501
    start_response("501 Not Implemented", [("Content-Type", "text/html")])
    return ["Proxy only allows GET"]

def proxy(env, start_response):
    app = apps.get(get_appname(env.get("HTTP_HOST", None)), None)
    if not app:
        start_response("404 Not Found", [("Content-Type", "text/html")])
        return ["App with name \"%s\" not found" % get_appname(env.get("HTTP_HOST", "?"))]
    # call one of the servers
    destination = random.choice(app)

    path = env.get("REQUEST_INFO", "/")
    headers = dict(((k, env[k]) for k in proxy_headers if env.has_key(k)))

    # TODO: add X-Forwared-* even if this isn't neccessary in this prototype
    rep = requests.get(destination, headers=headers)

    rep.headers.pop("transfer-encoding") # remove transfer-encoding
    rep.headers.update({"X-Local-Server": destination})
    response_headers = [(k, v) for k, v in rep.headers.iteritems()]
    start_response("200 OK", response_headers)
    return [str(rep.text)]
    

def get_appname(hostname):
    """Parse the application name for the incoming.
    """
    try:
        return hostname.split(".")[0]
    except:
        return None

#wsgi.WSGIServer(("", 8000), router).serve_forever()