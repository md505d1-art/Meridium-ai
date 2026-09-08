"""Meridium — prebuilt runtime loader (no live patching)."""
from __future__ import annotations

import base64
import zlib
from pathlib import Path

_root = Path(__file__).resolve().parent


def _load_runtime() -> str:
    parts = []
    for i in range(64):
        p = _root / ("_rt_chunk_" + str(i) + ".txt")
        if not p.exists():
            break
        t = p.read_text(encoding="ascii").strip()
        if len(t) < 100:
            raise RuntimeError("Corrupt runtime chunk " + str(i))
        parts.append(t)
    if len(parts) < 5:
        raise RuntimeError(
            "Meridium runtime chunks missing. Expected _rt_chunk_0.txt ..."
        )
    raw = zlib.decompress(base64.b64decode("".join(parts)))
    text = raw.decode("utf-8")
    text = "".join(ch for ch in text if not (0xD800 <= ord(ch) <= 0xDFFF))
    return text


try:
    _code = _load_runtime()
except Exception as e:
    import streamlit as st
    st.set_page_config(page_title="Meridium", page_icon="\u25c8", layout="wide")
    st.error("Meridium runtime failed to load.")
    st.exception(e)
    st.info("Reboot the Streamlit app after a full redeploy from GitHub main.")
    st.stop()

try:
    compile(_code, "meridium_runtime", "exec")
except Exception as e:
    import streamlit as st
    st.set_page_config(page_title="Meridium", page_icon="\u25c8", layout="wide")
    st.error("Meridium runtime is invalid.")
    st.exception(e)
    st.stop()

exec(compile(_code, str(_root / "meridium_runtime.py"), "exec"), globals())
