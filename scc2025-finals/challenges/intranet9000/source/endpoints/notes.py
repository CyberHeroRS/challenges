import json
from functools import wraps

from bson import ObjectId
from flask import Blueprint, Response, request, send_from_directory
from bson.json_util import dumps, loads

from auth import authenticate
from db import get_db

bp = Blueprint("notes", __name__)

@bp.route("/notes", methods=["GET"])
def notes_page():
    return send_from_directory("templates", "notes.html")

@bp.route("/api/notes", methods=["GET"])
@authenticate
def get_notes(user):
    db = get_db()
    notes = list(db.notes.find({"department": user["department"]}))
    return Response(dumps(notes), status=200, mimetype="application/json")


@bp.route("/api/notes/<note_id>", methods=["GET"])
@authenticate
def get_note(user, note_id):
    db = get_db()
    note = db.notes.find_one(
        {"_id": ObjectId(note_id), "department": user["department"]}
    )

    if not note:
        return Response(
            dumps({"error": "Note not found"}),
            status=404,
            mimetype="application/json",
        )

    return Response(dumps(note), status=200, mimetype="application/json")


@bp.route("/api/notes", methods=["POST"])
@authenticate
def create_note(user):
    data = loads(request.data)
    if not data or "title" not in data or "content" not in data:
        return Response(
            dumps({"error": "Missing required fields"}),
            status=400,
            mimetype="application/json",
        )

    new_note = {
        "title": data["title"],
        "content": data["content"],
        "department": user["department"],
    }

    db = get_db()
    result = db.notes.insert_one(new_note)
    new_note["_id"] = result.inserted_id

    return Response(dumps(new_note), status=201, mimetype="application/json")
