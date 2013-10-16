Paasman
=======

Paasman is a proof-of-concept prototype of a Platform as a Service for deployment of simple node.js web applications created in the course D7024E, Mobile and distributed computing systems at LTU.

Installation
------------
TBA.

Setup etcd
~~~~~~~~~~
Master:
$ etcd -f -cl 0.0.0.0 -s 10.10.10.2:7001 -c 10.10.10.2:4001 -sl 10.10.10.2 -n masternode

Other nodes:
$ etcd -f -cl 0.0.0.0 -s 10.10.10.3:7001 -c 10.10.10.3:4001 -C 10.10.10.2:7001 -sl 10.10.10.3 -n node3

To fetch the instance local ip, use: http://169.254.169.254/latest/meta-data/local-ipv4

Architecture
------------
The current design of the system is like follows.
Not that this is the design for the current iteration, not the final one.

- We have one master vm that handle the director and router
    and also maintains a private docker index/registry.
- ... 

