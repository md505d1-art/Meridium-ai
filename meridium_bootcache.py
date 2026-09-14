"""Compile classic runtime — always re-apply patches so code updates show up."""
from __future__ import annotations

import tempfile
import urllib.request
from pathlib import Path

# Bump this any time patches change so Streamlit workers rebuild.
_CACHE_VER = "v45-force-void"
_BASE = (
    "https://raw.githubusercontent.com/md505d1-art/Meridium-ai/"
    "e4324e37b75bc804cbc3dd2ffe7e08021399a4d2/app.py"
)
_CDN = (
    "https://cdn.jsdelivr.net/gh/md505d1-art/Meridium-ai@"
    "e4324e37b75bc804cbc3dd2ffe7e08021399a4d2/app.py"
)

_CODE = None

_tmp = Path(tempfile.gettempdir()) / "meridium_cache"
try:
    _tmp.mkdir(parents=True, exist_ok=True)
except Exception:
    _tmp = Path(tempfile.gettempdir())

# Separate caches: raw base vs fully patched runtime
_raw_cache = _tmp / ("raw_" + _CACHE_VER + ".py")
_patch_cache = _tmp / ("runtime_" + _CACHE_VER + ".py")


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
            # skip broken patch, keep previous text
            pass
    return text


def _download() -> str:
    last_err = None
    for url in (_BASE, _CDN):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Meridium/45"})
            with urllib.request.urlopen(req, timeout=90) as r:
                text = r.read().decode("utf-8", errors="replace")
            if text and len(text) > 100000:
                return text
        except Exception as e:
            last_err = e
    raise RuntimeError("Could not download classic Meridium core: " + str(last_err))


def _load_raw() -> str:
    try:
        if _raw_cache.exists() and _raw_cache.stat().st_size > 100000:
            return _strip(_raw_cache.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        pass
    text = _strip(_download())
    try:
        _raw_cache.write_text(text, encoding="utf-8")
    except Exception:
        pass
    return text


def _load_source() -> str:
    """Always re-apply local patches on top of cached/raw base."""
    # Prefer existing patched cache only if it already contains this version marker
    try:
        if _patch_cache.exists() and _patch_cache.stat().st_size > 200000:
            cached = _strip(_patch_cache.read_text(encoding="utf-8", errors="replace"))
            if "meridium_polish_applied_v45" in cached and "drift_to_void_reliquary" in cached:
                return cached
    except Exception:
        pass

    raw = _load_raw()
    text = _patch(raw)
    try:
        compile(text, "runtime", "exec")
        _patch_cache.write_text(text, encoding="utf-8")
    except Exception:
        pass
    return text


def get_code():
    global _CODE
    if _CODE is None:
        _CODE = compile(_load_source(), "meridium_classic_runtime.py", "exec")
    return _CODE


def clear_runtime_cache() -> None:
    """Utility for debugging — drop compiled cache files."""
    global _CODE
    _CODE = None
    for p in (_raw_cache, _patch_cache):
        try:
            if p.exists():
                p.unlink()
        except Exception:
            pass
