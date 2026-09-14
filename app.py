"""Meridium — classic design, fast boot (v45)."""
from __future__ import annotations

from meridium_bootcache import get_code

try:
    _code = get_code()
except Exception as e:
    import streamlit as st

    st.set_page_config(page_title="Meridium", page_icon="\u25c8", layout="wide")
    st.error("Meridium classic core failed to start.")
    st.exception(e)
    st.info("Reboot the app on Streamlit Cloud. Branch: main · File: app.py · cache v45")
    st.stop()

exec(_code, globals())
