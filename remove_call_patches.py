"""Fully disable the call feature and hide Call buttons from home/nav."""


def apply_remove_call(code: str) -> str:
    # 1) Hide buttons FIRST (while call_meridium strings still match)

    # Main home nav Call button (nav3)
    old_nav = (
        '    with nav3:\n'
        '        if st.button("🎙 Call Meridium", key="goto_call", use_container_width=True):\n'
        '            st.session_state.view = "call_meridium"\n'
        '            st.session_state.popup = False\n'
        '            st.rerun()\n'
    )
    if old_nav in code:
        code = code.replace(old_nav, '    with nav3:\n        pass  # Call Meridium retired\n', 1)

    # Bottom-menu Call button
    old_bm = (
        '        if st.button("🎙  Call", use_container_width=True, key="bm_call"):\n'
        '            st.session_state.view = "call_meridium"\n'
        '            st.rerun()\n'
    )
    if old_bm in code:
        code = code.replace(old_bm, '        # Call button removed\n', 1)

    # Popup Call button — neuter the condition
    code = code.replace(
        'if st.button("🎙 Call", use_container_width=True, key="pop_call"):',
        'if False and st.button("🎙 Call", use_container_width=True, key="pop_call_hidden"):',
    )

    # 2) Redirect call view to home
    code = code.replace(
        'if st.session_state.view == "call_meridium":',
        'if st.session_state.view == "call_meridium":\n    st.session_state.view = "home"\n    st.rerun()\nif False and st.session_state.view == "call_meridium":',
    )
    code = code.replace(
        'if view == "call_meridium":',
        'if view == "call_meridium":\n        st.session_state.view = "home"\n        st.rerun()\n    if False and view == "call_meridium":',
    )

    # 3) Any remaining navigation into call_meridium → home
    code = code.replace('st.session_state.view = "call_meridium"', 'st.session_state.view = "home"')
    code = code.replace("st.session_state.view = 'call_meridium'", "st.session_state.view = 'home'")

    return code
