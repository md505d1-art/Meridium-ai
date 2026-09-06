"""Meridium entrypoint — loads full app from last known-good commit, applies chess/soju path fix."""
from __future__ import annotations

import urllib.request
from pathlib import Path

_GOOD = (
    "https://raw.githubusercontent.com/md505d1-art/Meridium-ai/"
    "e4324e37b75bc804cbc3dd2ffe7e08021399a4d2/app.py"
)

_OLD_SOJU = '''        soju_dirs = [
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

_NEW_SOJU = '''        soju_dirs = [
            widget.parent / "soju",
            here / "soju",
            cwd / "soju",
            here / "assets" / "soju",
        ]
        soju_dir = next((d for d in soju_dirs if d.is_dir()), None)
        def _b64img(name):
            # soju/soju_idle.jpg OR soju_idle.jpg next to app.py (root upload)
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

_cache = Path(__file__).resolve().parent / ".meridium_app_cache.py"

def _load() -> str:
    # Prefer cache when present (offline / faster cold start)
    if _cache.exists() and _cache.stat().st_size > 100_000:
        code = _cache.read_text(encoding="utf-8")
    else:
        with urllib.request.urlopen(_GOOD, timeout=60) as resp:
            code = resp.read().decode("utf-8")
        try:
            _cache.write_text(code, encoding="utf-8")
        except Exception:
            pass
    if _OLD_SOJU in code:
        code = code.replace(_OLD_SOJU, _NEW_SOJU, 1)
    # theme_unlocks filename alias
    code = code.replace(
        "from theme_unlocks import unlock_and_persist",
        "from theme_unlocks import unlock_and_persist  # preferred\n"
        "except Exception:\n"
        "    try:\n"
        "        from themes_unlocks import unlock_and_persist\n"
        "    except Exception:\n"
        "        raise\n"
        "try:\n"
        "    unlock_and_persist  # noqa\n"
        "except Exception:\n"
        "    from themes_unlocks import unlock_and_persist  # type: ignore",
        1,
    )
    return code

_code = _load()
exec(compile(_code, str(Path(__file__).resolve().parent / "app.py"), "exec"), globals())
