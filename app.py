"""Meridium — classic design + working Study / Languages / Chess gambits / Lab lore."""
from __future__ import annotations

import tempfile
import urllib.request
from pathlib import Path

_CACHE_VER = "v42-welcome-fix"
_BASE = (
    "https://raw.githubusercontent.com/md505d1-art/Meridium-ai/"
    "e4324e37b75bc804cbc3dd2ffe7e08021399a4d2/app.py"
)
_CDN = (
    "https://cdn.jsdelivr.net/gh/md505d1-art/Meridium-ai@"
    "e4324e37b75bc804cbc3dd2ffe7e08021399a4d2/app.py"
)

_tmp = Path(tempfile.gettempdir()) / "meridium_cache"
try:
    _tmp.mkdir(parents=True, exist_ok=True)
except Exception:
    _tmp = Path(tempfile.gettempdir())
_cache = _tmp / ("runtime_" + _CACHE_VER + ".py")


def _strip(s: str) -> str:
    return "".join(ch for ch in s if not (0xD800 <= ord(ch) <= 0xDFFF))


def _patch(text: str) -> str:
    steps = [
        ("chess_patches", "apply_chess"),
        ("coach_patches", "apply_coach"),
        ("remove_call_patches", "apply_remove_call"),
        ("online_chess", "apply_online"),
        ("extra_features", "apply_extra_features"),
        ("owner_enhancements", "apply_owner_enhancements"),
        ("arg_explore", "apply_arg_explore"),
        ("meridium_polish", "apply_polish"),
        ("meridium_hub", "apply_learning_hub"),
        ("meridium_nadir", "apply_nadir_v2"),
        ("owner_enhancements", "apply_chess_page_fixes"),
    ]
    for mod_name, fn_name in steps:
        try:
            mod = __import__(mod_name, fromlist=[fn_name])
            new = _strip(getattr(mod, fn_name)(text))
            compile(new, "p_" + fn_name, "exec")
            new.encode("utf-8")
            text = new
        except Exception:
            pass
    return text


def _download() -> str:
    last_err = None
    for url in (_BASE, _CDN):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Meridium/42"})
            with urllib.request.urlopen(req, timeout=90) as r:
                text = r.read().decode("utf-8", errors="replace")
            if text and len(text) > 100000:
                return text
        except Exception as e:
            last_err = e
    raise RuntimeError("Could not download classic Meridium core: " + str(last_err))


def _load() -> str:
    try:
        if _cache.exists() and _cache.stat().st_size > 200000:
            cached = _strip(_cache.read_text(encoding="utf-8", errors="replace"))
            if "welcome_to_meridium_v1" in cached or 'view == "study"' in cached:
                compile(cached, "cached", "exec")
                return cached
    except Exception:
        pass
    text = _patch(_strip(_download()))
    try:
        compile(text, "runtime", "exec")
        _cache.write_text(text, encoding="utf-8")
    except Exception:
        pass
    return text


try:
    _code = _load()
except Exception as e:
    import streamlit as st
    st.set_page_config(page_title="Meridium", page_icon="\u25c8", layout="wide")
    st.error("Meridium classic core failed to start.")
    st.exception(e)
    st.info("Reboot the app on Streamlit Cloud. Branch: main \u00b7 File: app.py")
    st.stop()

try:
    compile(_code, "meridium_classic", "exec")
except Exception as e:
    import streamlit as st
    st.set_page_config(page_title="Meridium", page_icon="\u25c8", layout="wide")
    st.error("Classic runtime compile error.")
    st.exception(e)
    st.stop()

exec(compile(_code, "meridium_classic_runtime.py", "exec"), globals())
