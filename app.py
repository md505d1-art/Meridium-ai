"""Meridium entrypoint — full feature pack + owner/lab fixes."""
from __future__ import annotations
import urllib.request
from pathlib import Path

from chess_patches import apply_chess
from coach_patches import apply_coach
from remove_call_patches import apply_remove_call
from online_chess import apply_online
from extra_features import apply_extra_features
from owner_enhancements import apply_owner_enhancements, apply_chess_page_fixes
from arg_explore import apply_arg_explore
from meridium_polish import apply_polish

_CACHE_VER = "v23-void-reliquary"

_GOOD = (
    "https://raw.githubusercontent.com/md505d1-art/Meridium-ai/"
    "e4324e37b75bc804cbc3dd2ffe7e08021399a4d2/app.py"
)
_root = Path(__file__).resolve().parent
_cache = _root / f".meridium_app_cache_{_CACHE_VER}.py"
if _cache.exists() and _cache.stat().st_size > 100_000:
    _code = _cache.read_text(encoding="utf-8")
else:
    with urllib.request.urlopen(_GOOD, timeout=90) as r:
        _code = r.read().decode("utf-8")
    try:
        _cache.write_text(_code, encoding="utf-8")
    except Exception:
        pass

_code = apply_chess_page_fixes(
    apply_polish(
        apply_arg_explore(
            apply_owner_enhancements(
                apply_extra_features(
                    apply_online(apply_remove_call(apply_coach(apply_chess(_code))))
                )
            )
        )
    )
)
exec(compile(_code, str(_root / "app.py"), "exec"), globals())
