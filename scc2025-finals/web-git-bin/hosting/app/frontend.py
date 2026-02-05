from flask import Blueprint, request, render_template, redirect
from main import *
from urllib.parse import urlencode

from db import validate_password

frontend_routes = Blueprint("frontend", __name__)


@frontend_routes.route("/")
def index():
    return render_template("index.html", templates=get_repo_templates())


@frontend_routes.route("/repos", methods=["POST"])
def repos():
    if request.method == "POST":
        template = request.form["template"]
        if not template:
            return redirect("/?err=Missing fields")

        private = request.form.get("private", "off")

        repo_name, password = create_repo(template, private)
        if repo_name:
            query_params = urlencode(
                {"msg": "Repository created", "password": password}
            )
            return redirect(f"/repos/{repo_name}?{query_params}")
        else:
            return redirect("/?err=Repo creation failed")



@frontend_routes.route("/repos/<string:repo_name>")
def repo(repo_name):
    repo = get_repo(repo_name)

    if not repo:
        return redirect("/?err=Repo not found")

    return render_template(
        "repo.html",
        repo_name=repo_name,
        repo_data=repo,
        password=request.args.get("password", ""),
    )


@frontend_routes.route("/delete-repo/<string:repo_name>", methods=["POST"])
def delete_repo_endpoint(repo_name):
    if request.method == "POST":
        repo = get_repo(repo_name)

        if not repo:
            return redirect("/?err=Repo not found")

        # check password
        password = request.form.get("password")
        if not password:
            return redirect(f"/repos/{repo_name}?err=Missing password")
        if not validate_password(repo_name, password):
            return redirect(f"/repos/{repo_name}?err=Invalid password")

        delete_repo(repo_name)
        return redirect("/?msg=Repo deleted")
    else:
        return redirect("/?err=Invalid request method")
