import argparse
import shutil
import subprocess
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import quote

import aiofiles
from fastapi import FastAPI, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

BASE_DIR: Path


def validate_path(path_str: str) -> Path:
    target = (BASE_DIR / path_str).resolve()
    try:
        target.relative_to(BASE_DIR.resolve(), walk_up=False)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid path")
    return target


def get_relative(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(BASE_DIR.resolve()))
    except ValueError:
        return "."


def list_directory_contents(dir_path: Path) -> list[dict]:
    items = []
    for entry in sorted(dir_path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())):
        rel = get_relative(entry)
        items.append(
            {
                "name": entry.name,
                "path": rel,
                "is_dir": entry.is_dir(),
                "size": entry.stat().st_size if entry.is_file() else None,
            }
        )
    return items


def _filesizeformat(value):
    if value is None:
        return ""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(value) < 1024.0:
            if unit == "B":
                return f"{int(value)} B"
            return f"{value:3.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} PB"


templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
templates.env.filters["urlencode"] = lambda s: quote(str(s), safe="")
templates.env.filters["filesizeformat"] = _filesizeformat


async def _browse_partial(request: Request, path: str):
    target = validate_path(path) if path else BASE_DIR
    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=404, detail="Not found")
    items = list_directory_contents(target)
    rel = get_relative(target)
    parent = str(Path(rel).parent) if rel != "." else None
    response = templates.TemplateResponse(
        request,
        "partials/browse.html",
        {
            "items": items,
            "current_path": rel,
            "parent": parent,
            "base_name": target.name or BASE_DIR.name,
        },
    )
    response.headers["HX-Push-Url"] = f"/?path={quote(rel)}"
    return response


async def _redirect_or_htmx(request: Request, path: str):
    if request.headers.get("HX-Request"):
        return await _browse_partial(request, path)
    return RedirectResponse(url=f"/?path={quote(path)}", status_code=303)


@asynccontextmanager
async def lifespan(app: FastAPI):
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, path: str = ""):
    if request.headers.get("HX-Request"):
        return await _browse_partial(request, path)
    target = validate_path(path) if path else BASE_DIR
    if not target.exists():
        raise HTTPException(status_code=404, detail="Not found")
    if target.is_file():
        return FileResponse(target)
    items = list_directory_contents(target)
    rel = get_relative(target)
    parent = str(Path(rel).parent) if rel != "." else None
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "items": items,
            "current_path": rel,
            "parent": parent,
            "base_name": target.name or BASE_DIR.name,
        },
    )


@app.get("/browse", response_class=HTMLResponse)
async def browse(request: Request, path: str = ""):
    return await _browse_partial(request, path)


@app.get("/download")
async def download(path: str):
    target = validate_path(path)
    if not target.exists():
        raise HTTPException(status_code=404, detail="Not found")
    if target.is_dir():
        raise HTTPException(status_code=400, detail="Cannot download directory")
    return FileResponse(target, filename=target.name)


@app.post("/upload")
async def upload(request: Request, path: str = "", file: UploadFile | None = None):
    target_dir = validate_path(path) if path else BASE_DIR
    if not target_dir.is_dir():
        raise HTTPException(status_code=400, detail="Not a directory")
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    dest = target_dir / file.filename
    try:
        async with aiofiles.open(dest, "wb") as out:
            while chunk := await file.read(8192):
                await out.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    rel = get_relative(target_dir)
    return await _redirect_or_htmx(request, rel)


@app.post("/rename")
async def rename(request: Request, path: str = "", new_name: str = Form(...)):
    target = validate_path(path)
    if not target.exists():
        raise HTTPException(status_code=404, detail="Not found")
    dest = target.parent / new_name
    try:
        target.rename(dest)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    rel = get_relative(target.parent)
    return await _redirect_or_htmx(request, rel)


@app.post("/delete")
async def delete(request: Request, path: str = ""):
    target = validate_path(path)
    if not target.exists():
        raise HTTPException(status_code=404, detail="Not found")
    try:
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    rel = get_relative(target.parent)
    return await _redirect_or_htmx(request, rel)


@app.post("/mkdir")
async def mkdir(request: Request, path: str = "", name: str = Form(...)):
    target_dir = validate_path(path) if path else BASE_DIR
    if not target_dir.is_dir():
        raise HTTPException(status_code=400, detail="Not a directory")
    new_dir = target_dir / name
    try:
        new_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    rel = get_relative(target_dir)
    return await _redirect_or_htmx(request, rel)


def _archive_name(target: Path, ext: str) -> str:
    return target.name + ext if target.is_dir() else target.stem + ext


@app.post("/archive")
async def create_archive(request: Request, path: str, fmt: str = Form(...)):
    target = validate_path(path)
    if not target.exists():
        raise HTTPException(status_code=404, detail="Not found")

    archive_path = target.with_name(target.name + "." + fmt)

    try:
        if fmt == "zip":
            print(archive_path, target, target.name, target.parent)
            # zip -r <archive> <target_name> (relative to working dir)
            subprocess.run(
                ["zip", "-r", str(archive_path), target.name],
                cwd=str(target.parent),
                check=True,
            )
        elif fmt == "tar.gz":
            # tar -czf <archive> -C <target_parent> <target_name>
            subprocess.run(
                ["tar", "-czf", str(archive_path), "-C", str(target.parent), target.name],
                check=True,
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Archive creation failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    rel = get_relative(target.parent)
    return await _redirect_or_htmx(request, rel)


@app.post("/extract")
async def extract_archive(request: Request, path: str = "", dest: str = Form(...)):
    # Resolve and validate the archive and destination paths
    target = validate_path(path)
    if not target.exists():
        raise HTTPException(status_code=404, detail="Not found")
    if not target.is_file():
        raise HTTPException(status_code=400, detail="Target is not a file")

    dest_path = validate_path(dest)
    if not dest_path.is_dir():
        raise HTTPException(status_code=400, detail="Destination is not a directory")

    # Use subprocess with explicit argument lists to avoid shell injection
    try:
        if target.suffix == ".zip":
            # unzip -o <archive> -d <destination>
            subprocess.run(
                ["unzip", "-o", str(target), "-d", str(dest_path)],
                check=True,
            )
        elif target.name.endswith(".tar.gz") or target.suffixes == [".tar", ".gz"]:
            # tar -xzf <archive> -C <destination>
            subprocess.run(
                ["tar", "-xzf", str(target), "-C", str(dest_path)],
                check=True,
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported archive format")
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Extraction failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    rel = get_relative(dest_path)
    return await _redirect_or_htmx(request, rel)


@app.get("/dialog/{action}")
async def dialog(request: Request, action: str, path: str = ""):
    target = validate_path(path) if path else BASE_DIR
    if action in ("upload", "mkdir"):
        current_path = get_relative(target)
        item = None
    else:
        if not target.exists():
            raise HTTPException(status_code=404, detail="Not found")
        current_path = get_relative(target.parent)
        item = {
            "name": target.name,
            "path": get_relative(target),
            "is_dir": target.is_dir(),
        }
    template_name = f"partials/dialogs/{action}.html"
    return templates.TemplateResponse(
        request,
        template_name,
        {
            "current_path": current_path,
            "item": item,
        },
    )


def main():
    parser = argparse.ArgumentParser(description="Filepit - Web-based file manager")
    parser.add_argument("--files-dir", help="Directory to manage", required=True)
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    args = parser.parse_args()

    global BASE_DIR
    BASE_DIR = Path(args.files_dir).resolve()
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
