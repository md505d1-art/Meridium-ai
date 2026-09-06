"""Fully disable the call feature."""
def apply_remove_call(code: str) -> str:
    # Redirect any call view to home
    code = code.replace(
        'if view == "call_meridium":',
        'if view == "call_meridium":\n        st.session_state.view = "home"\n        st.rerun()\n    if False and view == "call_meridium":',
    )
    code = code.replace(
        "if view == 'call_meridium':",
        "if view == 'call_meridium':\n        st.session_state.view = 'home'\n        st.rerun()\n    if False and view == 'call_meridium':",
    )
    # Hide / disable call buttons
    for a, b in [
        ('"Call Meridium"', '"Chess (call retired)"'),
        ("'Call Meridium'", "'Chess (call retired)'"),
        ('label="Call"', 'label="Chess"'),
        ('key="nav_call"', 'key="nav_call_disabled"'),
        ('st.session_state.view = "call_meridium"', 'st.session_state.view = "chess"'),
        ("st.session_state.view = 'call_meridium'", "st.session_state.view = 'chess'"),
    ]:
        code = code.replace(a, b)
    return code
