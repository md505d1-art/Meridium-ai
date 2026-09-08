"""Meridium — stable shell (always boots)."""
from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Meridium", page_icon="\u25c8", layout="wide")

if "view" not in st.session_state:
    st.session_state.view = "home"
if "username" not in st.session_state:
    st.session_state.username = "operator"

st.markdown(
    """
    <style>
      .stApp { background: radial-gradient(ellipse at top, #1a1028 0%, #07060c 55%, #05040a 100%); }
      h1, h2, h3 { letter-spacing: 0.06em; }
      .mer-card {
        border: 1px solid rgba(160,140,220,0.25);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        background: rgba(20,16,32,0.65);
        margin-bottom: 0.75rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

view = st.session_state.view


def go(v: str) -> None:
    st.session_state.view = v
    st.rerun()


with st.sidebar:
    st.markdown("### Meridium")
    st.caption("stable shell v30")
    if st.button("Home", use_container_width=True):
        go("home")
    if st.button("Study", use_container_width=True):
        go("study")
    if st.button("Gambits", use_container_width=True):
        go("gambits")
    if st.button("Languages", use_container_width=True):
        go("languages")
    if st.button("Lore", use_container_width=True):
        go("lore")
    if st.button("Nadir", use_container_width=True):
        go("nadir")
    if st.button("Themes", use_container_width=True):
        go("themes")
    if st.button("Chess", use_container_width=True):
        go("chess")
    if st.button("Online", use_container_width=True):
        go("online")

if view == "home":
    st.title("Meridium")
    st.caption("Personal intelligence system — stable recovery build")
    st.markdown(
        '<div class="mer-card">Core shell is online. Optional modules load when available.</div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Open Study", use_container_width=True):
            go("study")
    with c2:
        if st.button("Open Languages", use_container_width=True):
            go("languages")
    with c3:
        if st.button("Open Nadir", use_container_width=True):
            go("nadir")
    st.info("Errors are isolated to one module — they will not take down the whole site.")

elif view == "study":
    st.header("Study")
    if st.button("Back"):
        go("home")
    try:
        from meridium_study import render_study_hub
        render_study_hub(st, st.session_state)
    except Exception as e:
        st.error("Study module unavailable")
        st.exception(e)

elif view == "gambits":
    st.header("Gambit Academy")
    if st.button("Back"):
        go("home")
    try:
        from meridium_gambits import render_gambit_trainer
        render_gambit_trainer(st, st.session_state)
    except Exception as e:
        st.error("Gambits module unavailable")
        st.exception(e)

elif view == "languages":
    st.header("Language Lab")
    if st.button("Back"):
        go("home")
    try:
        from meridium_languages import render_languages
        render_languages(st, st.session_state)
    except Exception as e:
        st.error("Languages module unavailable")
        st.exception(e)

elif view == "lore":
    st.header("Lore")
    if st.button("Back"):
        go("home")
    try:
        from meridium_lore_pack import render_lore_pack
        render_lore_pack(st, st.session_state)
    except Exception as e:
        st.error("Lore module unavailable")
        st.exception(e)

elif view == "nadir":
    st.header("Project Nadir")
    if st.button("Back"):
        go("home")
    try:
        from meridium_nadir import render_nadir_v2
        render_nadir_v2(st, st.session_state)
    except Exception as e:
        st.error("Nadir module unavailable")
        st.exception(e)

elif view == "themes":
    st.header("Void Reliquary")
    if st.button("Back"):
        go("home")
    try:
        from meridium_themes import render_theme_shop, apply_theme_to_app, get_user_theme
        uid = st.session_state.get("username") or "anon"
        th = st.session_state.get("active_theme") or get_user_theme(uid)
        apply_theme_to_app(st, th)
        render_theme_shop(st, st.session_state)
    except Exception as e:
        st.error("Themes module unavailable")
        st.exception(e)

elif view == "chess":
    st.header("Chess")
    if st.button("Back"):
        go("home")
    st.warning(
        "Full chess board lives in the classic Meridium core. "
        "This stable shell keeps the site online while that path is repaired."
    )

elif view == "online":
    st.header("Online lobby")
    if st.button("Back"):
        go("home")
    st.info("Online chess returns with the classic core. Lobby writes are cloud-safe.")

else:
    st.session_state.view = "home"
    st.rerun()
