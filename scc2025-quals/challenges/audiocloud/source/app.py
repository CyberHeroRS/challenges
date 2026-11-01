from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request, Response
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import uuid
import subprocess
from pydantic import BaseModel
from session import FileSystemSession

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


class Song(BaseModel):
    id: str
    name: str


@app.middleware("http")
async def session_middleware(request: Request, call_next):
    session_id = request.cookies.get("session")
    if not session_id:
        session_id = str(uuid.uuid4())

    request.state.session = FileSystemSession(session_id)
    response = await call_next(request)

    request.state.session.save()
    if "session" not in request.cookies:
        response.set_cookie("session", session_id)

    return response


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "songs": request.state.session.data["songs"]}
    )


@app.post("/")
async def upload_file(
    request: Request, file: UploadFile = File(...), name: str = Form(...)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    file_id = str(uuid.uuid4())
    filename = f"{file_id}.mp3"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    request.state.session.data["songs"].append({"id": file_id, "name": name})
    return RedirectResponse(url="/", status_code=303)


@app.get("/play_file")
async def play_file(request: Request):
    name = request.query_params.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="No file specified")

    filepath = os.path.join(UPLOAD_FOLDER, name)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        result = subprocess.run(
            ["file", "-bi", filepath], capture_output=True, text=True, check=True
        )
    except subprocess.SubprocessError:
        raise HTTPException(status_code=500, detail="Error checking file type")

    mime = result.stdout.strip()
    if not mime.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    return FileResponse(filepath)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
