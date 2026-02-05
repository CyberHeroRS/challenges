from flask import Flask, request, render_template, g
import sqlite3

DATABASE = "application/flags.db"

app = Flask(
    __name__,
    static_url_path="",
    static_folder="web/static",
    template_folder="web/templates",
)


@app.route("/")
def index():
    search = request.args.get("search")

    db = get_db()
    db.row_factory = sqlite3.Row

    query = f"SELECT title, flag FROM flags WHERE title LIKE '%{search}%' AND is_hidden = 0;"

    try:
        cur = db.execute(query)
        flags = cur.fetchall()
    except Exception:
        return render_template("index.html", query=query)

    return render_template("index.html", query=query, flags=flags)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db
