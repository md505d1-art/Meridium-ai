"""Meridium — classic core + new features (prebuilt runtime)."""
from __future__ import annotations

import base64
import zlib
from pathlib import Path

_root = Path(__file__).resolve().parent


def _load_chunks() -> str:
    parts = []
    for i in range(64):
        p = _root / ("_rt_chunk_" + str(i) + ".txt")
        if not p.exists():
            break
        t = p.read_text(encoding="ascii").strip()
        if len(t) < 50:
            raise RuntimeError("bad chunk " + str(i))
        parts.append(t)
    if len(parts) < 5:
        raise RuntimeError("runtime chunks missing")
    raw = zlib.decompress(base64.b64decode("".join(parts)))
    text = raw.decode("utf-8")
    return "".join(ch for ch in text if not (0xD800 <= ord(ch) <= 0xDFFF))


def _load_network() -> str:
    import urllib.request

    url = (
        "https://raw.githubusercontent.com/md505d1-art/Meridium-ai/"
        "e4324e37b75bc804cbc3dd2ffe7e08021399a4d2/app.py"
    )
    cdn = (
        "https://cdn.jsdelivr.net/gh/md505d1-art/Meridium-ai@"
        "e4324e37b75bc804cbc3dd2ffe7e08021399a4d2/app.py"
    )
    text = None
    for u in (url, cdn):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Meridium/34"})
            with urllib.request.urlopen(req, timeout=90) as r:
                text = r.read().decode("utf-8", errors="replace")
            if text and len(text) > 100000:
                break
        except Exception:
            text = None
    if not text:
        raise RuntimeError("could not download classic base")

    def strip(s: str) -> str:
        return "".join(ch for ch in s if not (0xD800 <= ord(ch) <= 0xDFFF))

    text = strip(text)
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
            fn = getattr(mod, fn_name)
            text = strip(fn(text))
            compile(text, "after_" + fn_name, "exec")
            text.encode("utf-8")
        except Exception:
            pass
    return text


try:
    try:
        _code = _load_chunks()
    except Exception:
        _code = _load_network()
except Exception as e:
    import streamlit as st
    st.set_page_config(page_title="Meridium", page_icon="\u25c8", layout="wide")
    st.error("Meridium could not start the classic core.")
    st.exception(e)
    st.info("Reboot the Streamlit app. Repo: md505d1-art/Meridium-ai, branch main.")
    st.stop()

try:
    compile(_code, "meridium_classic", "exec")
except Exception as e:
    import streamlit as st
    st.set_page_config(page_title="Meridium", page_icon="\u25c8", layout="wide")
    st.error("Classic runtime failed to compile.")
    st.exception(e)
    st.stop()

exec(compile(_code, str(_root / "meridium_classic_runtime.py"), "exec"), globals())
