from gevent import monkey
from gevent.pywsgi import WSGIServer
import sys

monkey.patch_all()

from flask import Flask, g

from frontend import frontend_routes
from git_server import git_routes

from main import *
import random
import string

app = Flask(__name__)

app.register_blueprint(frontend_routes, url_prefix="/")
app.register_blueprint(git_routes, url_prefix="/git")


# Static files
app.static_folder = "static"
app.static_url_path = "/static"


if __name__ == "__main__":

    with app.app_context():

        if not os.path.exists("/data/FLAG_PLANTED"):
            # Create the marker file
            os.makedirs("/data/FLAG_PLANTED", exist_ok=True)
            FLAG = sys.argv[1] if len(sys.argv) > 1 else None
            repo_name, password = create_repo("basic", "on")

            if not repo_name:
                print("Error creating flag repo")
                sys.exit(1)

            random_filename = "".join(
                random.choice(string.ascii_letters + string.digits) for _ in range(10)
            )

            # add flag to the repo
            with open(
                f"{REPOS_DIR}/{repo_name}/{random_filename}.secret",
                "w",
            ) as f:
                f.write(FLAG)
            git(repo_name, "add", ".")
            git(repo_name, "commit", "-m", "Placed some secrets :D")

            # remove the flag from the repo
            os.remove(f"{REPOS_DIR}/{repo_name}/{random_filename}.secret")
            git(repo_name, "add", ".")
            git(repo_name, "commit", "-m", "Deleted my secrets.")


    # Start flask app
    WSGIServer(("0.0.0.0", PORT), app).serve_forever()
