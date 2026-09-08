"""Meridium stable shell v32 — zero boot imports beyond streamlit."""
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
      .stApp {
        background: radial-gradient(ellipse at top, #1a1028 0%, #07060c 55%, #05040a 100%) !important;
        color: #e8e0f0;
      }
      section[data-testid="stSidebar"] {
        background: #0a0812 !important;
      }
      .mer-card {
        border: 1px solid rgba(160,140,220,0.28);
        border-radius: 14px;
        padding: 1rem 1.15rem;
        background: rgba(20,16,32,0.7);
        margin: 0.5rem 0 1rem 0;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def go(v: str) -> None:
    st.session_state.view = v
    st.rerun()


def safe_render(title: str, import_name: str, fn_name: str) -> None:
    st.header(title)
    if st.button("Back to Home", key="back_" + import_name):
        go("home")
    try:
        mod = __import__(import_name, fromlist=[fn_name])
        fn = getattr(mod, fn_name)
        fn(st, st.session_state)
    except Exception as e:
        st.error(title + " failed to load.")
        st.code(type(e).__name__ + ": " + str(e))
        with st.expander("Details"):
            st.exception(e)


view = st.session_state.get("view") or "home"

with st.sidebar:
    st.markdown("### Meridium")
    st.caption("v32 stable")
    nav = [
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
    ]
    for label, key in nav:
        if st.button(label, use_container_width=True, key="nav_" + key):
            go(key)

if view == "home":
    st.title("Meridium")
    st.caption("Personal intelligence system")
    st.markdown(
        '<div class="mer-card">Shell is online. Use the sidebar to open modules.</div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    shortcuts = [("Study", "study"), ("Languages", "languages"), ("Nadir", "nadir"), ("Themes", "themes")]
    for col, (label, key) in zip(cols, shortcuts):
        with col:
            if st.button(label, use_container_width=True, key="home_" + key):
                go(key)
    with st.expander("Module health check"):
        checks = [
            "meridium_study",
            "meridium_gambits",
            "meridium_languages",
            "meridium_lore_pack",
            "meridium_nadir",
            "meridium_themes",
            "meridium_theme_fx",
            "lab_view",
            "gambits_data.json",
        ]
        for name in checks:
            try:
                if name.endswith(".json"):
                    from pathlib import Path
                    p = Path(__file__).resolve().parent / name
                    st.write(("OK \u00b7 " if p.exists() else "MISSING \u00b7 ") + name)
                else:
                    __import__(name)
                    st.write("OK \u00b7 " + name)
            except Exception as e:
                st.write("FAIL \u00b7 " + name + " \u00b7 " + type(e).__name__ + ": " + str(e)[:80])

elif view == "study":
    safe_render("Study", "meridium_study", "render_study_hub")

elif view == "gambits":
    safe_render("Gambit Academy", "meridium_gambits", "render_gambit_trainer")

elif view == "languages":
    safe_render("Language Lab", "meridium_languages", "render_languages")

elif view == "lore":
    safe_render("Lore", "meridium_lore_pack", "render_lore_pack")

elif view == "nadir":
    safe_render("Project Nadir", "meridium_nadir", "render_nadir_v2")

elif view == "themes":
    safe_render("Void Reliquary", "meridium_themes", "render_theme_shop")

elif view == "lab":
    st.header("Observation Lab")
    if st.button("Back to Home", key="back_lab"):
        go("home")
    try:
        from lab_view import render_lab
        render_lab()
    except Exception as e:
        st.error("Lab failed to load.")
        st.code(type(e).__name__ + ": " + str(e))
        st.exception(e)

elif view == "chess":
    st.header("Chess")
    if st.button("Back to Home", key="back_chess"):
        go("home")
    st.info("Full board returns with the classic core. Use Gambits for opening practice.")
    if st.button("Open Gambits"):
        go("gambits")

elif view == "online":
    st.header("Online")
    if st.button("Back to Home", key="back_online"):
        go("home")
    st.info("Online matchmaking returns with the classic core.")

else:
    st.session_state.view = "home"
    st.rerun()
