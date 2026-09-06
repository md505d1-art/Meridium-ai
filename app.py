"""Meridium entrypoint — patches chess contrast + Jarvis call."""
from __future__ import annotations
import urllib.request
from pathlib import Path
from chess_patches import apply_chess
from call_patches import apply_call

_GOOD = (
    "https://raw.githubusercontent.com/md505d1-art/Meridium-ai/"
    "e4324e37b75bc804cbc3dd2ffe7e08021399a4d2/app.py"
)
_root = Path(__file__).resolve().parent
_cache = _root / ".meridium_app_cache.py"
if _cache.exists() and _cache.stat().st_size > 100_000:
    _code = _cache.read_text(encoding="utf-8")
else:
    with urllib.request.urlopen(_GOOD, timeout=90) as r:
        _code = r.read().decode("utf-8")
    try:
        _cache.write_text(_code, encoding="utf-8")
    except Exception:
        pass
_code = apply_call(apply_chess(_code))
exec(compile(_code, str(_root / "app.py"), "exec"), globals())
