"""Meridium entrypoint — resilient boot (bundled base chunks, cache, network)."""
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
from meridium_hub import apply_learning_hub
from meridium_nadir import apply_nadir_v2

_CACHE_VER = "v27-boot-resilient"
_GOOD = (
    "https://raw.githubusercontent.com/md505d1-art/Meridium-ai/"
    "e4324e37b75bc804cbc3dd2ffe7e08021399a4d2/app.py"
)
_root = Path(__file__).resolve().parent
_cache = _root / f".meridium_app_cache_{_CACHE_VER}.py"


def _from_chunks() -> str | None:
    try:
        import zlib, base64
        parts = []
        for i in range(32):
            p = _root / f"_base_chunk_{i}.txt"
            if not p.exists():
                break
            parts.append(p.read_text(encoding="utf-8").strip())
        if not parts:
            return None
        return zlib.decompress(base64.b64decode("".join(parts))).decode("utf-8")
    except Exception:
        return None


def _load_base() -> str:
    try:
        if _cache.exists() and _cache.stat().st_size > 100_000:
            return _cache.read_text(encoding="utf-8")
    except Exception:
        pass
    try:
        bundled = _root / "_meridium_base_app.py"
        if bundled.exists() and bundled.stat().st_size > 100_000:
            return bundled.read_text(encoding="utf-8")
    except Exception:
        pass
    text = _from_chunks()
    if text and len(text) > 100_000:
        try:
            _cache.write_text(text, encoding="utf-8")
        except Exception:
            pass
        return text
    try:
        with urllib.request.urlopen(_GOOD, timeout=90) as r:
            text = r.read().decode("utf-8")
        try:
            _cache.write_text(text, encoding="utf-8")
        except Exception:
            pass
        return text
    except Exception as net_err:
        try:
            caches = sorted(
                _root.glob(".meridium_app_cache_*.py"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            for p in caches:
                if p.stat().st_size > 100_000:
                    return p.read_text(encoding="utf-8")
        except Exception:
            pass
        raise RuntimeError(
            "Meridium failed to load base app. "
            "Missing _base_chunk_*.txt / network. "
            f"Detail: {net_err}"
        )


_code = _load_base()

try:
    _code = apply_chess_page_fixes(
        apply_nadir_v2(
            apply_learning_hub(
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
        )
    )
except Exception as patch_err:
    import streamlit as st
    st.set_page_config(page_title="Meridium", page_icon="\u25c8", layout="wide")
    st.error("Meridium patch chain failed \u2014 diagnostic below.")
    st.exception(patch_err)
    st.stop()

exec(compile(_code, str(_root / "app.py"), "exec"), globals())
