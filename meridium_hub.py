"""Meridium hub v3 — Study + Languages; Gambits in Chess; Welcome popup."""
from __future__ import annotations

_STUDY = """
if st.session_state.get("view") == "study":
    if st.button("Back", key="study_back_v3"):
        st.session_state.view = "home"
        st.rerun()
    _ok = False
    try:
        from meridium_study import render_study_hub
        render_study_hub(st, st.session_state)
        _ok = True
    except Exception as _e:
        st.warning("Built-in study (" + type(_e).__name__ + ")")
    if not _ok:
        st.markdown("### GCSE Study")
        _subs = ["Mathematics", "English Language", "Biology", "Chemistry", "Physics", "History", "Geography", "Computer Science"]
        _boards = ["AQA", "Edexcel", "OCR", "WJEC", "Eduqas", "CCEA"]
        _s = st.selectbox("Subject", _subs, key="fb_study_sub")
        _b = st.selectbox("Exam board", _boards, key="fb_study_board")
        st.info(_s + " \u00b7 " + _b)
        for _t in ["Review notes", "Practice questions", "Mark scheme", "Timed paper"]:
            st.checkbox(_t, key="fb_tp_" + _t.replace(" ", "_"))
        st.markdown("[AQA past papers](https://www.aqa.org.uk/find-past-papers-and-mark-schemes)")
        st.text_area("Notes", key="fb_study_notes")
    st.stop()
"""

_LANG = """
if st.session_state.get("view") == "languages":
    if st.button("Back", key="lang_back_v3"):
        st.session_state.view = "home"
        st.rerun()
    _ok = False
    try:
        from meridium_languages import render_languages
        render_languages(st, st.session_state)
        _ok = True
    except Exception as _e:
        st.warning("Built-in languages (" + type(_e).__name__ + ")")
    if not _ok:
        st.markdown("### Language Lab")
        if "lang_xp" not in st.session_state:
            st.session_state.lang_xp = 0
        if "lang_hearts" not in st.session_state:
            st.session_state.lang_hearts = 5
        c1, c2, c3 = st.columns(3)
        c1.metric("XP", st.session_state.lang_xp)
        c2.metric("Hearts", st.session_state.lang_hearts)
        c3.metric("Streak", st.session_state.get("lang_streak") or 0)
        _course = st.selectbox("Course", ["Spanish", "Czech", "Russian", "French", "ASL"], key="fb_lang_course")
        _pack = {
            "Spanish": [("hello", "hola"), ("thanks", "gracias"), ("yes", "si"), ("no", "no")],
            "Czech": [("hello", "ahoj"), ("thanks", "dekuji"), ("yes", "ano"), ("no", "ne")],
            "Russian": [("hello", "privet"), ("thanks", "spasibo"), ("yes", "da"), ("no", "net")],
            "French": [("hello", "bonjour"), ("thanks", "merci"), ("yes", "oui"), ("no", "non")],
            "ASL": [("HELLO", "Open hand at forehead outward"), ("THANKS", "Fingers from chin forward")],
        }
        _i = int(st.session_state.get("lang_i") or 0)
        _items = _pack.get(_course) or _pack["Spanish"]
        _i = _i % len(_items)
        _p, _a = _items[_i]
        st.info("Translate: **" + _p + "**")
        import random as _r
        _opts = list({_a, "x", "y", "z"})
        _r.Random(int(st.session_state.get("lang_i") or 0) * 17 + 3).shuffle(_opts)
        _g = st.radio("Pick", _opts, key="fb_lang_ans")
        if st.button("Check", key="fb_lang_check"):
            if (_g or "").strip().lower() == _a.lower() or _a.lower() in (_g or "").lower():
                st.session_state.lang_xp = int(st.session_state.lang_xp) + 10
                st.session_state.lang_i = _i + 1
                st.success("Correct +10 XP")
                st.rerun()
            else:
                st.session_state.lang_hearts = max(0, int(st.session_state.lang_hearts) - 1)
                st.error("Answer: " + _a)
        if st.button("Next", key="fb_lang_next"):
            st.session_state.lang_i = _i + 1
            st.rerun()
    st.stop()
"""


def apply_learning_hub(code: str) -> str:
    for k in ("bm_gambits", "bm_lore_pack", "bm_lore", "sidebar_gambits", "sidebar_lore"):
        code = code.replace('key="' + k + '"', 'key="__rm_' + k + '"')
        code = code.replace("key='" + k + "'", "key='__rm_" + k + "'")

    if "meridium_learning_hub_v3" not in code:
        boot = (
            "\n# meridium_learning_hub_v3\n"
            "try:\n"
            "    from meridium_ui_v2 import inject_ui\n"
            "    inject_ui(st)\n"
            "except Exception:\n"
            "    pass\n"
        )
        idx = code.find("st.set_page_config(")
        if idx >= 0:
            depth = 0
            i = idx + len("st.set_page_config")
            while i < len(code):
                if code[i] == "(":
                    depth += 1
                elif code[i] == ")":
                    depth -= 1
                    if depth == 0:
                        j = i + 1
                        if j < len(code) and code[j] == "\n":
                            j += 1
                        code = code[:j] + boot + code[j:]
                        break
                i += 1

    if "welcome_to_meridium_v1" not in code:
        welcome = (
            "\n# welcome_to_meridium_v1\n"
            "if \"welcome_seen\" not in st.session_state:\n"
            "    st.session_state.welcome_seen = False\n"
            "if not st.session_state.welcome_seen:\n"
            "    try:\n"
            "        @st.dialog(\"Welcome to Meridium\")\n"
            "        def _meridium_welcome_dlg():\n"
            "            st.write(\"You have entered the residual channel.\")\n"
            "            st.caption(\"Chat \u00b7 Chess \u00b7 Lab \u00b7 Drift \u00b7 Study \u00b7 Languages\")\n"
            "            if st.button(\"Enter\", type=\"primary\", use_container_width=True, key=\"welcome_enter_btn\"):\n"
            "                st.session_state.welcome_seen = True\n"
            "                st.rerun()\n"
            "        _meridium_welcome_dlg()\n"
            "    except Exception:\n"
            "        st.markdown(\n"
            "            '<div style=\"padding:1rem 1.1rem;border-radius:16px;border:1px solid rgba(196,167,231,0.35);'\n"
            "            'background:rgba(20,16,32,0.95);margin:0.5rem 0 1rem;'>'\n"
            "            '<div style=\"font-size:1.25rem;font-weight:700;\">Welcome to Meridium</div>'\n"
            "            '<div style=\"opacity:0.85;margin-top:0.35rem;\">You have entered the residual channel.</div></div>',\n"
            "            unsafe_allow_html=True,\n"
            "        )\n"
            "        if st.button(\"Enter Meridium\", type=\"primary\", key=\"welcome_enter_fallback\"):\n"
            "            st.session_state.welcome_seen = True\n"
            "            st.rerun()\n"
        )
        idx = code.find("st.set_page_config(")
        if idx >= 0:
            depth = 0
            i = idx + len("st.set_page_config")
            while i < len(code):
                if code[i] == "(":
                    depth += 1
                elif code[i] == ")":
                    depth -= 1
                    if depth == 0:
                        j = i + 1
                        if j < len(code) and code[j] == "\n":
                            j += 1
                        code = code[:j] + welcome + code[j:]
                        break
                i += 1

    if 'key="bm_study"' not in code:
        nav = (
            "\n        if st.button(\"Study\", use_container_width=True, key=\"bm_study\"):\n"
            "            st.session_state.view = \"study\"\n"
            "            st.rerun()\n"
            "        if st.button(\"Languages\", use_container_width=True, key=\"bm_languages\"):\n"
            "            st.session_state.view = \"languages\"\n"
            "            st.rerun()\n"
        )
        for n2 in ('key="bm_chess"', "key='bm_chess'", 'key="bm_chat"', 'key="bm_drift"'):
            if n2 in code:
                i = code.find(n2)
                k = code.find("st.rerun()", i)
                if k > 0:
                    k = code.find("\n", k) + 1
                    code = code[:k] + nav + code[k:]
                break

    if "study_back_v3" not in code:
        block = _STUDY + "\n" + _LANG + "\n"
        placed = False
        for a in (
            'if st.session_state.view == "home":',
            "if st.session_state.view == 'home':",
            'if st.session_state.get("view") == "home":',
        ):
            if a in code:
                code = code.replace(a, block + a, 1)
                placed = True
                break
        if not placed:
            code = code + "\n" + block

    if "chess_learn_gambits_v3" not in code:
        chess_inject = (
            "\n    # chess_learn_gambits_v3\n"
            "    _chess_mode = st.radio(\n"
            "        \"Chess mode\",\n"
            "        [\"Play\", \"Learn gambits\"],\n"
            "        horizontal=True,\n"
            "        key=\"chess_mode_toggle_v3\",\n"
            "    )\n"
            "    if _chess_mode == \"Learn gambits\":\n"
            "        try:\n"
            "            from meridium_gambits import render_gambit_trainer\n"
            "            render_gambit_trainer(st, st.session_state)\n"
            "        except Exception as _ge:\n"
            "            st.error(\"Gambits offline: \" + str(_ge))\n"
            "        st.stop()\n"
        )
        for needle in (
            'if st.session_state.view == "chess":',
            "if st.session_state.view == 'chess':",
        ):
            if needle in code:
                idx = code.find(needle)
                end = code.find("\n", idx) + 1
                code = code[:end] + chess_inject + code[end:]
                break

    if "lab_lore_pack_v3" not in code:
        lab_inject = (
            "\n    # lab_lore_pack_v3\n"
            "    with st.expander(\"Archive chapters / Lore\", expanded=False):\n"
            "        try:\n"
            "            from meridium_lore_pack import render_lore_pack\n"
            "            render_lore_pack(st, st.session_state)\n"
            "        except Exception:\n"
            "            st.caption(\"Lore offline\")\n"
        )
        for needle in (
            'if st.session_state.view == "lab":',
            "if st.session_state.view == 'lab':",
        ):
            if needle in code:
                idx = code.find(needle)
                end = code.find("\n", idx) + 1
                code = code[:end] + lab_inject + code[end:]
                break

    code = "".join(ch for ch in code if not (0xD800 <= ord(ch) <= 0xDFFF))
    return code
