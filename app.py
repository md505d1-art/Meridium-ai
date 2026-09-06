import gzip, base64
from pathlib import Path
_root = Path(__file__).resolve().parent
_parts = sorted(_root.glob("app.gz.b64.part*"))
if not _parts:
    raise RuntimeError("Missing app.gz.b64.part* files next to app.py — restore incomplete")
_b64 = "".join(p.read_text(encoding="ascii") for p in _parts)
_code = gzip.decompress(base64.b64decode(_b64)).decode("utf-8")
exec(compile(_code, str(_root / "app.py"), "exec"), globals())
