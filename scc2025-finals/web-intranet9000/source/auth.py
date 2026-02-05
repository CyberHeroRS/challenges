from functools import wraps
from bson import ObjectId
from flask import Blueprint, Response, g, request
from bson.json_util import dumps

from db import get_db


def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(
                dumps({"error": "Unauthorized"}),
                status=403,
                mimetype="application/json",
            )

        session_id = auth_header.split(" ")[1]
        db = get_db()
        user = db.employees.find_one({"_id": ObjectId(session_id)})

        if not user:
            return Response(
                dumps({"error": "Unauthorized"}),
                status=403,
                mimetype="application/json",
            )

        return f(user, *args, **kwargs)

    return decorated_function
