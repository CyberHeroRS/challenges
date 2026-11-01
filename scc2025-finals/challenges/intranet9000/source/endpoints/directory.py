import json

from flask import Blueprint, Response, request, send_from_directory

from db import get_db
from bson.json_util import dumps, loads

bp = Blueprint("directory", __name__)


@bp.route("/directory", methods=["GET"])
def home():
    return send_from_directory("templates", "directory.html")


@bp.route("/api/directory", methods=["GET"])
def search():
    query = {}
    for key, value in request.args.items():
        if value := value.strip():
            query[key] = value

    if not query:
        items = []
    else:
        db = get_db()
        items = list(
            db.employees.find(
                {
                    key: {"$regex": value, "$options": "i"}
                    for key, value in query.items()
                },
                {"password": 0, "employee_number": 0},
            )
        )

    for item in items:
        item.pop("_id", None)
        if not item.get("is_public"):
            item.pop("email", None)
            item.pop("phone_number", None)

    response_data = dumps({"items": items})
    return Response(response_data, mimetype="application/json")
