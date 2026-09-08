"""Meridium entrypoint — stable boot + safe patches."""
from __future__ import annotations

import tempfile
import urllib.request
from pathlib import Path
from typing import Optional, Callable, List, Tuple

_CACHE_VER = "v29-unicode-safe"
_GOOD = (
    "https://raw.githubusercontent.com/md505d1-art/Meridium-ai/"
    "e4324e37b75bc804cbc3dd2ffe7e08021399a4d2/app.py"
)
_CDN = (
    "https://cdn.jsdelivr.net/gh/md505d1-art/Meridium-ai@"
    "e4324e37b75bc804cbc3dd2ffe7e08021399a4d2/app.py"
)
_root = Path(__file__).resolve().parent
_tmp = Path(tempfile.gettempdir()) / "meridium_cache"
try:
    _tmp.mkdir(parents=True, exist_ok=True)
except Exception:
    _tmp = Path(tempfile.gettempdir())
_cache = _tmp / (".meridium_app_cache_" + _CACHE_VER + ".py")


def _strip_surrogates(text: str) -> str:
    return "".join(ch for ch in text if not (0xD800 <= ord(ch) <= 0xDFFF))


def _from_chunks() -> Optional[str]:
    try:
        import zlib
        import base64
        parts = []
        for i in range(32):
            p = _root / ("_base_chunk_" + str(i) + ".txt")
            if not p.exists():
                break
            t = p.read_text(encoding="utf-8").strip()
            if t.startswith("PLACEHOLDER") or t.startswith("SKIP") or len(t) < 500:
                return None
            parts.append(t)
        if len(parts) < 3:
            return None
        return zlib.decompress(base64.b64decode("".join(parts))).decode("utf-8")
    except Exception:
        return None


def _fetch(url: str) -> Optional[str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MeridiumBoot/29"})
        with urllib.request.urlopen(req, timeout=90) as r:
            text = r.read().decode("utf-8", errors="replace")
        text = _strip_surrogates(text)
        if len(text) > 100_000:
            return text
    except Exception:
        return None
    return None


def _save_cache(text: str) -> None:
    try:
        _cache.write_text(text, encoding="utf-8")
    except Exception:
        pass


def _load_base() -> str:
    try:
        if _cache.exists() and _cache.stat().st_size > 100_000:
            return _strip_surrogates(_cache.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        pass
    try:
        bundled = _root / "_meridium_base_app.py"
        if bundled.exists() and bundled.stat().st_size > 100_000:
            return _strip_surrogates(bundled.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        pass
    text = _from_chunks()
    if text and len(text) > 100_000:
        text = _strip_surrogates(text)
        _save_cache(text)
        return text
    last_err = None
    for url in (_GOOD, _CDN):
        try:
            text = _fetch(url)
            if text:
                _save_cache(text)
                return text
        except Exception as e:
            last_err = e
    try:
        caches = sorted(
            _tmp.glob(".meridium_app_cache_*.py"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for p in caches:
            if p.stat().st_size > 100_000:
                return _strip_surrogates(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        pass
    raise RuntimeError("Meridium failed to load base app. Last error: " + str(last_err))


def _apply_chain(code: str) -> str:
    steps = []

    def _add(label, import_path, attr):
        try:
            mod = __import__(import_path, fromlist=[attr])
            steps.append((label, getattr(mod, attr)))
        except Exception as e:
            steps.append((label + " (missing)", lambda c: c))

    _add("chess", "chess_patches", "apply_chess")
    _add("coach", "coach_patches", "apply_coach")
    _add("remove_call", "remove_call_patches", "apply_remove_call")
    _add("online", "online_chess", "apply_online")
    _add("extra", "extra_features", "apply_extra_features")
    _add("owner", "owner_enhancements", "apply_owner_enhancements")
    _add("arg", "arg_explore", "apply_arg_explore")
    _add("polish", "meridium_polish", "apply_polish")
    _add("hub", "meridium_hub", "apply_learning_hub")
    _add("nadir", "meridium_nadir", "apply_nadir_v2")
    _add("fixes", "owner_enhancements", "apply_chess_page_fixes")

    for label, fn in steps:
        try:
            new_code = fn(code)
            new_code = _strip_surrogates(new_code)
            compile(new_code, "after_" + label.split()[0], "exec")
            new_code.encode("utf-8")
            code = new_code
        except Exception:
            pass
    return code


try:
    _code = _load_base()
except Exception as load_err:
    import streamlit as st
    st.set_page_config(page_title="Meridium", page_icon="\u25c8", layout="wide")
    st.error("Meridium could not load its core app code.")
    st.exception(load_err)
    st.stop()

try:
    _code = _apply_chain(_code)
except Exception as patch_err:
    import streamlit as st
    st.set_page_config(page_title="Meridium", page_icon="\u25c8", layout="wide")
    st.error("Meridium patch chain failed hard.")
    st.exception(patch_err)
    st.stop()

_code = _strip_surrogates(_code)
try:
    _code.encode("utf-8")
except UnicodeEncodeError:
    _code = _code.encode("utf-8", errors="ignore").decode("utf-8")

exec(compile(_code, str(_root / "app_runtime.py"), "exec"), globals())
