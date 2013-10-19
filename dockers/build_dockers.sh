#!/bin/bash

docker build -t paasman/base dockers/base/.

docker build -t paasman/paasman-src dockers/paasman-src/.

#docker build -t paasman/base dockers/base/.