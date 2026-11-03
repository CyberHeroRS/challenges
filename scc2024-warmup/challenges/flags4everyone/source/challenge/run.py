import os
import sqlite3

from application.app import app, DATABASE

# The DB used to be seeded with a hardcoded flag at image-BUILD time (see
# source/Dockerfile history); it's now (re)built here at container-START
# time instead, so the real flag (injected via challenge.yaml's env-based
# flag mechanism) ends up in the per-instance database rather than a
# baked-in placeholder.
FLAG = os.environ.get("FLAG", "SCC{placeholder_flag_not_set}")


def init_db():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    conn = sqlite3.connect(DATABASE)
    with open("application/db/schema.sql", encoding="utf-8") as f:
        conn.executescript(f.read())
    with open("application/db/data.sql", encoding="utf-8") as f:
        data_sql = f.read().replace("__FLAG__", FLAG)
    conn.executescript(data_sql)
    conn.commit()
    conn.close()


init_db()

app.run(host="0.0.0.0", port=1337, debug=True)
