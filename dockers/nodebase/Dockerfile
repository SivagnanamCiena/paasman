# passman/nodebase

FROM ubuntu:12.04

MAINTAINER paasman

RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y curl wget build-essential libssl-dev python-software-properties

RUN add-apt-repository ppa:chris-lea/node.js --yes
RUN apt-get update
RUN apt-get install -y nodejs
RUN npm install express