from flask import Blueprint, request, make_response, Response

from includes.git import git_command_with_input, git_command
from main import uuid_v4_regex, get_repo_data, log
from flask_httpauth import HTTPBasicAuth

from db import validate_password

auth = HTTPBasicAuth(realm="GitBin")


@auth.verify_password
def verify_password(username, password):
    if not uuid_v4_regex.match(username):
        return False
    if not password:
        return False

    return validate_password(username, password)


git_routes = Blueprint("git", __name__)


@git_routes.route("/<string:repo_name>/git-upload-pack", methods=["POST"])
@git_routes.route("/<string:repo_name>.git/git-upload-pack", methods=["POST"])
def git_upload_pack(repo_name):

    if not uuid_v4_regex.match(repo_name):
        response = make_response("Invalid repository name.", 404)
        return response
    
    args = ["upload-pack", "--stateless-rpc", "."]
    res = git_command_with_input(repo_name, "", request.data, *args)

    if res is None:
        response = make_response("Repository not found.", 404)
        return response
    if res == b"Repo not found":
        response = make_response("Repository not found.", 404)
        return response
    
    return Response(res)



@git_routes.route("/<string:repo_name>/git-receive-pack", methods=["POST"])
@git_routes.route("/<string:repo_name>.git/git-receive-pack", methods=["POST"])
@auth.login_required
def git_receive_pack(repo_name):

    if auth.current_user() != repo_name:
        response = make_response("Invalid username.", 401)
        response.headers["WWW-Authenticate"] = (
            'Basic realm="GitBin"'
        )
        return response

    if not uuid_v4_regex.match(repo_name):
        return make_response("Invalid repository name.", 404)

    old_version = request.headers.get("Git-Protocol")
    args = ["receive-pack", "--stateless-rpc", "."]
    res = git_command_with_input(repo_name, "", request.data, *args)
    return Response(res)


@git_routes.route("/<string:repo_name>/info/refs", methods=["GET"])
@git_routes.route("/<string:repo_name>.git/info/refs", methods=["GET"])
@auth.login_required(optional=True)
def git_info_refs(repo_name):

    if not uuid_v4_regex.match(repo_name):
        return make_response("Invalid repository name.", 400)
    
    repo_data = get_repo_data(repo_name)
    if not repo_data:
        response = make_response("Repository not found.", 404)
        return response

    if repo_data["private"] == "on" and auth.current_user() != repo_name:
        response = make_response("Invalid username.", 401)
        response.headers["WWW-Authenticate"] = (
            'Basic realm="GitBin"'
        )
        return response

    version = request.headers.get("git/2.17.1")
    service = request.args.get("service")

    if service and "git-" in service:
        allowed_services = {"upload-pack", "receive-pack"}
        service_name = service[4:]
        if service_name not in allowed_services:
            return make_response("Service not allowed.", 403)
    else:
        service_name = "upload-pack"

    args = [service_name, "--stateless-rpc", "--advertise-refs", "."]

    res = git_command(repo_name, version, *args)

    first_line = "# service=git-%s\n0000" % service_name
    first_line = ("%.4x" % len(first_line)) + first_line

    resp = make_response(first_line + res.decode())
    resp.headers["Content-Type"] = "application/x-git-%s-advertisement" % service_name
    return resp
