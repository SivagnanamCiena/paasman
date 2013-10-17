#!/bin/bash
set -e

echo "yeah"

if [ ! -d $APP_NAME ]; then
    # download file from master, place it as app.js under some folder

echo "
var http = require('http');
//var process = require('process');
var server = http.createServer(function (request, response) {
    response.writeHead(200, {\"Content-Type\": \"text/plain\"});
    response.end(\"Hello World\n\");
});

server.listen(80);
" >> app.js

    node app.js
fi
