"""Meridium Easter eggs — small triggers, soft rewards."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

UK = ZoneInfo("Europe/London")

SECRET_CHAT_TITLES = {
    "hexside": ("Track: Abomination", "You renamed a thread into a school that shouldn't exist here."),
    "soft room": ("Soft Room", "A room the alarm does not reach."),
    "meridium-0": ("M-0", "A version string that was never shipped."),
}

PLAYLIST_SECRET = "for when she waits at the door"


def uk_now() -> datetime:
    return datetime.now(UK)


def is_quiet_hour() -> bool:
    h = uk_now().hour
    return h == 3  # 03:00–03:59 UK


def owner_rare_line(username: str) -> str | None:
    """~15% chance each home load for owner."""
    if not username:
        return None
    if username.strip().lower() not in {"drae", "drae henry"}:
        return None
    # stable-ish per hour so it doesn't flicker every rerun
    seed = uk_now().strftime("%Y%m%d%H")
    if hash(seed + "owner") % 7 == 0:
        return "The shell recognises its owner. Quiet mode is yours if you want it."
    return None


def quiet_hour_caption() -> str | None:
    if is_quiet_hour():
        return "03:00 UK — the shell is quieter now. Some doors only exist in this hour."
    return None


def register_qotd_open() -> str | None:
    n = int(st.session_state.get("qotd_opens") or 0) + 1
    st.session_state.qotd_opens = n
    if n == 3:
        return "Third knock on the quote. The rotation noticed you."
    if n > 0 and n % 11 == 0:
        return "You've opened the quote often enough that the paper is soft at the edges."
    return None


def check_secret_chat_title(title: str) -> str | None:
    t = (title or "").strip().lower()
    if t in SECRET_CHAT_TITLES:
        theme, msg = SECRET_CHAT_TITLES[t]
        st.session_state["_egg_theme"] = theme
        return msg
    return None


def mirror_reply(prompt: str) -> str | None:
    last = (st.session_state.get("_last_user_prompt") or "").strip()
    cur = (prompt or "").strip()
    st.session_state._last_user_prompt = cur
    if last and cur and last == cur:
        return (
            "You said that already. The shell answers differently the second time: "
            "repetition is how operators mark a signal. I'm still here."
        )
    return None


def lab_leftover_caption() -> str | None:
    if st.session_state.get("_lab_session_visit") and not st.session_state.get("_lab_leftover_shown"):
        st.session_state._lab_leftover_shown = True
        return "Recovered scrap: *the glass still remembers your reflection.*"
    return None


def mark_lab_visit() -> None:
    st.session_state._lab_session_visit = True


def stabilize_countdown() -> str | None:
    if not st.session_state.get("arg_stabilized"):
        return None
    raw = st.session_state.get("stabilize_at")
    if not raw:
        st.session_state.stabilize_at = uk_now().isoformat()
        raw = st.session_state.stabilize_at
    try:
        started = datetime.fromisoformat(raw)
        if started.tzinfo is None:
            started = started.replace(tzinfo=UK)
        days = max(0, (uk_now() - started).days)
        return f"Stabilized · day {days + 1}"
    except Exception:
        return "Stabilized · active"


def fake_element_119_line(prompt: str) -> str | None:
    p = (prompt or "").lower()
    if "119" in p or "element 119" in p or "ununennium" in p:
        return (
            "Public tables end at 118. Meridium is not on the ratified list — "
            "not because it was never observed, but because the observation was sealed. "
            "You already found one door."
        )
    return None


def on_delete_chat(chat: dict) -> None:
    msgs = (chat or {}).get("messages") or []
    for m in reversed(msgs):
        if m.get("role") == "user" and m.get("content"):
            st.session_state._palimpsest = str(m["content"])[:120]
            return
    st.session_state._palimpsest = None


def palimpsest_line() -> str | None:
    frag = st.session_state.pop("_palimpsest", None)
    if frag:
        return f"…a deleted thread left ink underneath: *{frag}*"
    return None


def playlist_secret_hit(playlist_name: str) -> str | None:
    if (playlist_name or "").strip().lower() == PLAYLIST_SECRET:
        return "Offline · still saved. The playlist name was a key."
    return None


def font_theme_combo_caption(font: str, theme: str) -> str | None:
    if font == "Inter" and theme in {"Lumity Glow", "Stringbean Soft"}:
        return "This combination is softer than the lab allows. Keep it."
    if font == "Georgia" and theme == "Containment Red":
        return "Typeface of reports · colour of alarms. Operator aesthetic."
    return None


def wrong_model_reply(prompt: str) -> str | None:
    p = (prompt or "").strip().lower()
    if p in {"meridium-0", "model: meridium-0", "use meridium-0"}:
        return (
            "meridium-0 was never published. You just addressed a build that only exists "
            "in the observation log. Hello from the unshipped shell."
        )
    return None
