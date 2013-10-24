#!/bin/bash
set -e

echo "yeah"

if [ ! -d $APP_NAME ]; then
    # download file from master, place it as app.js under some folder

    #DIRECTOR=$(curl -s http://172.17.42.1:4001/v1/keys/services/director)
    DIRECTOR=10.0.0.11

    echo `curl http://${DIRECTOR}:8001/apps/${APP_NAME}/download/`  >> app.js

    node app.js
fi
