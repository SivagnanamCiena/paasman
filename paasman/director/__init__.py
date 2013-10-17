# -*- coding: utf-8 -*-
"""
    authors
    =======
    mikhln-9
    sanpet-8
"""

from flask import Flask, request, jsonify
from paasman.director.manager import DirectorManager
from paasman.director.db import session
#from paasman.director import dispatcher

import etcd

etcd_client = etcd.Etcd("172.17.42.1")

app = Flask(__name__)

@app.teardown_appcontext
def remove_db_session(exception=None):
    session.remove()

# TODO: move the filepath to director.cfg
import os
director_manager = DirectorManager("_deployments/")

def api_error(message, status=400):
    return jsonify(
        {"error": dict(
            message=message
        )}
    ), status

@app.route("/apps/", methods=["GET"])
def list_apps():
    #dispatcher.tasks.put_nowait("hello!")

    return "added to queue"

@app.route("/apps/", methods=["POST"])
def deploy_app():
    file = request.files["file"]
    appname = request.form.get("app", None)
    if not appname or not file:
        return api_error("name and file is required", 400)
    if file:
        #TODO: use manager.store_application()
        file.save(os.path.join("_deployments", file.filename))
        return file.filename
    return "No file?"

@app.route("/apps/<int:id>/", methods=["GET"])
def app_state(id):
    return ""

@app.route("/apps/<int:id>/", methods=["PUT"])
def edit_app(id):
    return ""

@app.route("/apps/<int:id>/", methods=["DELETE"])
def delete_app(id):
    return ""

@app.route("/apps/<name>/download/", methods=["GET"])
def download_appfile(name):
    # TODO: return the file for the asked app, used by a docker file that fetch the file to run
    return "No file"

@app.route("/_paasman/nodes/", methods=["GET"])
def get_cluster_nodes():
    try:
        nodes = map(lambda e: e.value, etcd_client.list("services/agents"))

        return jsonify({"nodes": nodes})
    except:
        return api_error("Error during fetching agents/nodes from etcd", 500)
