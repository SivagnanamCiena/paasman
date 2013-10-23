# -*- coding: utf-8 -*-
"""
    authors
    =======
    mikhln-9
    sanpet-8
"""

import etcd
from paasman.director.manager import DirectorManager

import gevent.monkey
gevent.monkey.patch_socket()

etcd_client = etcd.Etcd("172.17.42.1")

director_manager = DirectorManager("/_deployments/")