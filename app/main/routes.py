# -*- coding: utf-8 -*-

from flask import render_template, request
from app.response import ApiResponse

@blueprint.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404

@blueprint.route("/system/health", methods=["GET"])
def system_health_check():
    return Response(0, "成功").to_dict(), 200

@blueprint.route("/device/all", methods=["GET"])
def get_device_list():
    return service.get_all_devices()

@blueprint.route("/device/<id>", methods=["GET"])
def get_device_by_id(id):
    return service.get_device_by_id(id)

@blueprint.route("/device/<id>", methods=["PUT"])
def update_device_by_id(id):
    return service.update_device_by_id(id, request.json)

@blueprint.route("/device/<id>", methods=["DELETE"])
def delete_device_by_id(id):
    return service.delete_device_by_id(id)

@blueprint.route("/device/<id>", methods=["POST"])
def operate_device_by_id(id):
    op = request.args.get("op", default=None, type=str)
    return service.operate_device_by_id(id, op)
