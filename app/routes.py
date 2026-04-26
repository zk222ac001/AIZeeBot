# API routes for controlling the AIZeeBot and accessing its features
from flask import Blueprint, request
from robot.motor_control import move, stop

control_routes = Blueprint("control", __name__)

@control_routes.route("/control")
def control():
    cmd = request.args.get("cmd")

    if cmd in ["forward", "backward", "left", "right"]:
        move(cmd)
    else:
        stop()

    return {"status": "ok", "command": cmd}