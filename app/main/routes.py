from . import blueprint


@blueprint.route("/system/health", methods=["GET"])
def system_health_check():
    return Response(0, "成功").to_dict(), 200

@blueprint.route("/system/initdb", methods=["POST"])
def system_init_database():
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
