from flask import Flask, send_from_directory, make_response

app = Flask(__name__, static_url_path="", static_folder="web/static")


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/fourth")
def lastPart():
    response_data = {
        "fourth": "3b_aPP",
        "message": "Congratz, here is the fourth part of the flag. One more ahead!",
    }
    response = make_response(response_data)
    response.headers["Last-Flag-Part"] = "_i5_fuN}"
    return response
