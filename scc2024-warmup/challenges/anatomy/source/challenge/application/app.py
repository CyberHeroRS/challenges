from flask import Flask, send_from_directory, make_response

from application.flag_parts import FLAG_PARTS

app = Flask(__name__, static_url_path="", static_folder="web/static")


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/fourth")
def lastPart():
    response_data = {
        "fourth": FLAG_PARTS[3],
        "message": "Congratz, here is the fourth part of the flag. One more ahead!",
    }
    response = make_response(response_data)
    response.headers["Last-Flag-Part"] = FLAG_PARTS[4]
    return response
