# -*- coding: utf-8 -*-
"""
    authors
    =======
    mikhln-9
    sanpet-8
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
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
    apps = filter(lambda app: app.state == "deployed", director_manager._apps.values())
    return jsonify({
        "applications": map(lambda app: {"name": app.name, "id": app.id}, apps)
    })
    #apps = filter(lambda app: app.state == "deployed", director_manager._apps.values())
    #return jsonify(apps)

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

#@app.route("/apps/<int:id>/", methods=["DELETE"])
@app.route("/apps/<string:app_name>/", methods=["DELETE"])
def delete_app(app_name):
    #appname = request.form.get("app", "?")
    undeployment = director_manager.undeploy_application(app_name)
    if undeployment:
        return "Successfully undeployed application %s" % app_name
    return "No such application: %s" % app_name

@app.route("/apps/<name>/download/", methods=["GET"])
def download_appfile(name):
    # TODO: return the file for the asked app, used by a docker file that fetch the file to run
    return send_file(director_manager.get_application_file(name))

@app.route("/instances/", methods=["POST"])
def add_vm_instance():
    instance_count = int(request.form.get("instances"))

    instances = director_manager.add_vm_instances(instance_count)
    return jsonify({
        "instances": map(lambda instance: instance.private_ip_address, instances)
    })

@app.route("/_paasman/nodes/", methods=["GET"])
def get_cluster_nodes():
    try:
        nodes = map(lambda e: e.value, etcd_client.list("services/agents"))

        return jsonify({"nodes": nodes, "manager_nodes": map(lambda n: n.ip, director_manager.get_nodes())})
    except:
        return api_error("Error during fetching agents/nodes from etcd", 500)

@app.route("/_paasman/apps/")
def get_apps():
    return jsonify({"apps": {app_name: {"id": app.id,"state": app.state, "processes": app.get_processes()} for app_name, app in director_manager._apps.items()}})
    #return jsonify({"apps": map(lambda app: {app.name: app.get_instances()}, director_manager._apps.itervalues())})