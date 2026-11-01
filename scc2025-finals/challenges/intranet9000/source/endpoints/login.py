import json
from hashlib import sha1

from flask import Blueprint, Response, request, send_from_directory
from bson.json_util import dumps, loads

from db import get_db

bp = Blueprint("login", __name__)


@bp.route("/login", methods=["GET"])
def login_page():
    return send_from_directory("templates", "login.html")


@bp.route("/api/login", methods=["POST"])
def login_api():
    creds = loads(request.data)
    if not creds.get("employee_number") or not creds.get("password"):
        return Response(
            dumps({"error": "Missing employee number or password"}),
            status=400,
            mimetype="application/json",
        )

    creds["password"] = sha1(creds["password"].encode()).hexdigest()

    db = get_db()
    employee = db.employees.find_one(creds)

    if not employee:
        return Response(
            dumps({"error": "Invalid employee number or password"}),
            status=401,
            mimetype="application/json",
        )

    return Response(
        dumps({
            "session_token": str(employee["_id"]),
            "employee_number": employee["employee_number"],
            "first_name": employee["first_name"],
            "last_name": employee["last_name"],
        }),
        status=200,
        mimetype="application/json",
    )
