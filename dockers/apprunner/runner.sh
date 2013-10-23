#!/bin/bash
set -e

echo "yeah"

if [ ! -d $APP_NAME ]; then
    # download file from master, place it as app.js under some folder

echo `curl http://10.0.0.11:8001/apps/${APP_NAME}/download/`  >> app.js

    node app.js
fi
