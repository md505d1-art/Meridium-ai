"""Meridium — stable shell. Every module is isolated."""
from __future__ import annotations

import streamlit as st

try:
    import meridium_bootstrap_fix as _bf
    _bf.apply()
except Exception:
    pass

st.set_page_config(page_title="Meridium", page_icon="\u25c8", layout="wide")

if "view" not in st.session_state:
    st.session_state.view = "home"
if "username" not in st.session_state:
    st.session_state.username = "operator"

st.markdown(
    """
    <style>
      .stApp {
        background: radial-gradient(ellipse at top, #1a1028 0%, #07060c 55%, #05040a 100%) !important;
      }
      h1, h2, h3 { letter-spacing: 0.06em; }
      .mer-card {
        border: 1px solid rgba(160,140,220,0.25);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        background: rgba(20,16,32,0.65);
        margin-bottom: 0.75rem;
      }
      section[data-testid="stSidebar"] {
        background: rgba(10,8,18,0.95);
      }
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    from meridium_themes import apply_theme_to_app, get_user_theme
    _uid = st.session_state.get("username") or "anon"
    _th = st.session_state.get("active_theme") or get_user_theme(_uid)
    st.session_state.active_theme = _th
    apply_theme_to_app(st, _th)
except Exception:
    pass


def go(v: str) -> None:
    st.session_state.view = v
    st.rerun()


view = st.session_state.get("view") or "home"

with st.sidebar:
    st.markdown("### Meridium")
    st.caption("stable v31")
    for label, key in [
        ("Home", "home"),
        ("Study", "study"),
        ("Gambits", "gambits"),
        ("Languages", "languages"),
        ("Lore", "lore"),
        ("Nadir", "nadir"),
        ("Themes", "themes"),
        ("Lab", "lab"),
        ("Chess", "chess"),
        ("Online", "online"),
    ]:
        if st.button(label, use_container_width=True, key="nav_" + key):
            go(key)

if view == "home":
    st.title("Meridium")
    st.caption("Personal intelligence system")
    st.markdown(
        '<div class="mer-card">Shell online. Pick a module from the sidebar.</div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Study", use_container_width=True, key="home_study"):
            go("study")
    with c2:
        if st.button("Languages", use_container_width=True, key="home_lang"):
            go("languages")
    with c3:
        if st.button("Nadir", use_container_width=True, key="home_nadir"):
            go("nadir")
    with c4:
        if st.button("Themes", use_container_width=True, key="home_themes"):
            go("themes")
    with st.expander("System status"):
        mods = [
            ("meridium_study", "Study"),
            ("meridium_gambits", "Gambits"),
            ("meridium_languages", "Languages"),
            ("meridium_lore_pack", "Lore"),
            ("meridium_nadir", "Nadir"),
            ("meridium_themes", "Themes"),
            ("lab_view", "Lab"),
        ]
        for mod, label in mods:
            try:
                __import__(mod)
                st.write("OK \u00b7 " + label)
            except Exception as e:
                st.write("DOWN \u00b7 " + label + " \u00b7 " + type(e).__name__)

elif view == "study":
    st.header("Study")
    if st.button("Back", key="back_study"):
        go("home")
    try:
        from meridium_study import render_study_hub
        render_study_hub(st, st.session_state)
    except Exception as e:
        st.error("Study module error")
        st.exception(e)

elif view == "gambits":
    st.header("Gambit Academy")
    if st.button("Back", key="back_gambits"):
        go("home")
    try:
        from meridium_gambits import render_gambit_trainer
        render_gambit_trainer(st, st.session_state)
    except Exception as e:
        st.error("Gambits module error")
        st.exception(e)

elif view == "languages":
    st.header("Language Lab")
    if st.button("Back", key="back_lang"):
        go("home")
    try:
        from meridium_languages import render_languages
        render_languages(st, st.session_state)
    except Exception as e:
        st.error("Languages module error")
        st.exception(e)

elif view == "lore":
    st.header("Lore")
    if st.button("Back", key="back_lore"):
        go("home")
    try:
        from meridium_lore_pack import render_lore_pack
        render_lore_pack(st, st.session_state)
    except Exception as e:
        st.error("Lore module error")
        st.exception(e)

elif view == "nadir":
    st.header("Project Nadir")
    if st.button("Back", key="back_nadir"):
        go("home")
    try:
        from meridium_nadir import render_nadir_v2
        render_nadir_v2(st, st.session_state)
    except Exception as e:
        st.error("Nadir module error")
        st.exception(e)

elif view == "themes":
    st.header("Void Reliquary")
    if st.button("Back", key="back_themes"):
        go("home")
    try:
        from meridium_themes import render_theme_shop
        render_theme_shop(st, st.session_state)
    except Exception as e:
        st.error("Themes module error")
        st.exception(e)

elif view == "lab":
    st.header("Observation Lab")
    if st.button("Back", key="back_lab"):
        go("home")
    try:
        from lab_view import render_lab
        render_lab()
    except Exception as e:
        st.error("Lab module error")
        st.exception(e)

elif view == "chess":
    st.header("Chess")
    if st.button("Back", key="back_chess"):
        go("home")
    st.info(
        "Full Soju chess board is part of the classic core. "
        "Use Gambits for openings while the classic board path is restored."
    )
    if st.button("Open Gambit Academy"):
        go("gambits")

elif view == "online":
    st.header("Online")
    if st.button("Back", key="back_online"):
        go("home")
    st.info("Online matchmaking returns with the classic core.")

else:
    st.session_state.view = "home"
    st.rerun()
