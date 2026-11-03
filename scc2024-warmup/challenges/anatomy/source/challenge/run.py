from application.flag_parts import FLAG_PARTS
from application.app import app

# Substitute the real flag parts into the static assets once at startup
# (these files are served directly by Flask's built-in static handler, so
# this can't be done per-request without adding custom routes).
_static_dir = "application/web/static"
_substitutions = {
    "__FLAG_PART_1__": FLAG_PARTS[0],
    "__FLAG_PART_2__": FLAG_PARTS[1],
    "__FLAG_PART_3__": FLAG_PARTS[2],
}
for _filename in ("index.html", "style.css", "script.js"):
    _path = f"{_static_dir}/{_filename}"
    with open(_path, "r", encoding="utf-8") as _f:
        _content = _f.read()
    for _token, _value in _substitutions.items():
        _content = _content.replace(_token, _value)
    with open(_path, "w", encoding="utf-8") as _f:
        _f.write(_content)

app.run(host="0.0.0.0", port=1337)
