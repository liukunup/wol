# -*- coding: utf-8 -*-

from flask import render_template, request
from . import blueprint
from .response import ApiResponse
from .service import DeviceService

service = DeviceService()

@blueprint.route("/")
@blueprint.route("/index")
@blueprint.route("/index.html")
def index():
    return render_template('index.html')

@blueprint.route("/healthz", methods=["GET"])
def system_health_check():
    return ApiResponse(0, "success").to_dict()

@blueprint.route("/device/all", methods=["GET"])
def get_device_list():
    keyword = request.args.get("keyword", default=None, type=str)
    return service.get_all_devices(keyword=keyword)

@blueprint.route("/device", methods=["POST"])
def add_device():
    return service.add_device(request.json)

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
