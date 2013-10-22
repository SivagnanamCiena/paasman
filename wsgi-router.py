# -*- coding: utf-8 -*-
"""
    authors
    =======
    mikhln-9
    sanpet-8
"""

from gevent import wsgi
from paasman.router import router as app

if __name__ == "__main__":
    wsgi.WSGIServer(("", 80), app).serve_forever()
