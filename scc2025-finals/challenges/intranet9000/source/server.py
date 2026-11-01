from flask import Flask, redirect

from endpoints import directory, login, notes

app = Flask(__name__)

# Register blueprints
app.register_blueprint(directory.bp)
app.register_blueprint(login.bp)
app.register_blueprint(notes.bp)


@app.route("/")
def index():
    return redirect("/directory")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
