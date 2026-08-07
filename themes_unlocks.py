"""Shared secret-theme unlock helpers (no Streamlit circular imports)."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import List

import streamlit as st

SECRET_NAMES = {
    "M-119 Amber",
    "Containment Red",
    "Stabilized Meridium",
    "Voss Static",
    "Stringbean Soft",
    "Lumity Glow",
    "Soft Static",
}

DATA_DIR = Path(__file__).resolve().parent / "data"


def _user_paths(username: str) -> List[Path]:
    name = (username or "").strip().lower()
    if not name:
        return []
    key24 = hashlib.sha256(name.encode()).hexdigest()[:24]
    key16 = hashlib.sha256(name.encode()).hexdigest()[:16]
    return [
        DATA_DIR / f"{key24}.json",
        Path("/tmp") / f"meridium_{key16}.json",
    ]


def unlock_and_persist(theme_name: str, reason: str = "", apply: bool = True) -> bool:
    """Unlock theme in session + merge into on-disk user save."""
    if theme_name not in SECRET_NAMES:
        return False
    unlocked = list(st.session_state.get("unlocked_themes") or [])
    newly = theme_name not in unlocked
    if newly:
        unlocked.append(theme_name)
        st.session_state.unlocked_themes = unlocked
        st.session_state["_theme_unlock_msg"] = (
            f"Theme unlocked: **{theme_name}**" + (f" — {reason}" if reason else "")
        )
    if apply:
        st.session_state.theme = theme_name

    # Persist unlocked_themes (+ theme) into existing user JSON if present
    name = (st.session_state.get("username") or "").strip()
    if not name:
        return newly
    for fp in _user_paths(name):
        try:
            data = {}
            if fp.exists():
                data = json.loads(fp.read_text(encoding="utf-8"))
            data["username"] = data.get("username") or name
            data["unlocked_themes"] = list(
                dict.fromkeys(list(data.get("unlocked_themes") or []) + unlocked)
            )
            if apply:
                data["theme"] = theme_name
            data["saved_at"] = datetime.now().isoformat()
            # keep other keys if file existed
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            continue
    return newly
