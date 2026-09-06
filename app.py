"""Meridium entrypoint — loads last known-good app.py and applies soju root-path fix."""
from __future__ import annotations

import urllib.request
from pathlib import Path

_GOOD = (
    "https://raw.githubusercontent.com/md505d1-art/Meridium-ai/"
    "e4324e37b75bc804cbc3dd2ffe7e08021399a4d2/app.py"
)

_OLD = '''        soju_dirs = [
            widget.parent / "soju",
            here / "soju",
            cwd / "soju",
            here / "assets" / "soju",
        ]
        soju_dir = next((d for d in soju_dirs if d.is_dir()), None)
        if soju_dir is None:
            raise FileNotFoundError(
                "soju/ folder not found. Create soju/ next to app.py and add the four portraits."
            )
        def _b64img(name):
            p = soju_dir / name
            if not p.exists():
                raise FileNotFoundError(f"Missing Soju asset: soju/{name}")
            return "data:image/jpeg;base64," + _b64.b64encode(p.read_bytes()).decode()
        html = html.replace("__PLAYER_WHITE__", player_white)
        html = html.replace("__BASE__", str(int(base)))
        html = html.replace("__INC__", str(int(inc)))
        html = html.replace("__DEPTH__", str(int(depth)))
        html = html.replace("__NONCE__", str(nonce))
        html = html.replace("__SOJU_IDLE__", _b64img("soju_idle.jpg"))
        html = html.replace("__SOJU_HAPPY__", _b64img("soju_happy.jpg"))
        html = html.replace("__SOJU_SHOCK__", _b64img("soju_shock.jpg"))
        html = html.replace("__SOJU_THINK__", _b64img("soju_think.jpg"))
        return html'''

_NEW = '''        soju_dirs = [
            widget.parent / "soju",
            here / "soju",
            cwd / "soju",
            here / "assets" / "soju",
        ]
        soju_dir = next((d for d in soju_dirs if d.is_dir()), None)
        def _b64img(name):
            candidates = []
            if soju_dir is not None:
                candidates.append(soju_dir / name)
            for root in (widget.parent, here, cwd):
                candidates.append(root / name)
            for p in candidates:
                if p.exists() and p.is_file():
                    return "data:image/jpeg;base64," + _b64.b64encode(p.read_bytes()).decode()
            raise FileNotFoundError(
                f"Missing Soju asset: {name} (looked in soju/ and next to app.py)"
            )
        html = html.replace("__PLAYER_WHITE__", player_white)
        html = html.replace("__BASE__", str(int(base)))
        html = html.replace("__INC__", str(int(inc)))
        html = html.replace("__DEPTH__", str(int(depth)))
        html = html.replace("__NONCE__", str(nonce))
        for placeholder, fname in (
            ("__SOJU_IDLE__", "soju_idle.jpg"),
            ("__SOJU_HAPPY__", "soju_happy.jpg"),
            ("__SOJU_SHOCK__", "soju_shock.jpg"),
            ("__SOJU_THINK__", "soju_think.jpg"),
        ):
            if placeholder in html:
                html = html.replace(placeholder, _b64img(fname))
        return html'''

_root = Path(__file__).resolve().parent
_cache = _root / ".meridium_app_cache.py"

if _cache.exists() and _cache.stat().st_size > 100_000:
    _code = _cache.read_text(encoding="utf-8")
else:
    with urllib.request.urlopen(_GOOD, timeout=90) as _resp:
        _code = _resp.read().decode("utf-8")
    try:
        _cache.write_text(_code, encoding="utf-8")
    except Exception:
        pass

if _OLD in _code:
    _code = _code.replace(_OLD, _NEW, 1)

exec(compile(_code, str(_root / "app.py"), "exec"), globals())
