# -*- coding: utf-8 -*-
"""
    authors
    =======
    mikhln-9
    sanpet-8
"""

from flask import Flask, request, jsonify
from paasman.director.db import session
from paasman.director import director_manager, etcd_client

app = Flask(__name__)

@app.teardown_appcontext
def remove_db_session(exception=None):
    session.remove()

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
    appfile = request.files["file"]
    appname = request.form.get("app", None)
    if not appname or not appfile:
        return api_error("name and file is required", 400)
    if appfile:
        if not director_manager.is_valid_appname(appname):
            return "Only a-z and A-Z letters are valid" # TODO: use api_error
        #TODO: use manager.store_application()
        try:
            deployment = director_manager.deploy_application(appname, appfile)
            if deployment:
                return "Successfully deployed the application %s" % appname # TOOD: tell how to visit on appname.domain...
            return "Error during upload#1"
        except Exception as e:
            print "Error during upload#2", e
            return "Error during upload#2" # TODO: use api_error
        #appfile.save(os.path.join("_deployments", appfile.filename))
        #return appfile.filename
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
