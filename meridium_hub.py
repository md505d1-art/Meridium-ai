"""Meridium hub — Study + Languages nav; Gambits in Chess; Lore in Lab/Nadir."""
from __future__ import annotations


def apply_learning_hub(code: str) -> str:
    if "meridium_learning_hub_v2" in code and "bm_study" in code:
        return code

    boot = (
        "\n# meridium_learning_hub_v2\n"
        "try:\n"
        "    from meridium_ui_v2 import inject_ui\n"
        "    inject_ui(st)\n"
        "except Exception:\n"
        "    pass\n"
    )
    if "meridium_learning_hub_v2" not in code and "meridium_learning_hub_v1" not in code:
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

    nav = (
        "\n        if st.button(\"Study\", use_container_width=True, key=\"bm_study\"):\n"
        "            st.session_state.view = \"study\"\n"
        "            st.rerun()\n"
        "        if st.button(\"Languages\", use_container_width=True, key=\"bm_languages\"):\n"
        "            st.session_state.view = \"languages\"\n"
        "            st.rerun()\n"
    )
    if "bm_study" not in code:
        for n2 in ('key="bm_chess"', "key='bm_chess'", 'key="bm_chat"'):
            if n2 in code:
                i = code.find(n2)
                k = code.find("st.rerun()", i)
                if k > 0:
                    k = code.find("\n", k) + 1
                    code = code[:k] + nav + code[k:]
                break

    for dead_key in ("bm_gambits", "bm_lore_pack"):
        if dead_key in code and "retired_" + dead_key not in code:
            code = code.replace('key="' + dead_key + '"', 'key="retired_' + dead_key + '"')

    handlers = (
        "\nif st.session_state.view == \"study\":\n"
        "    if st.button(\"Back\", key=\"study_back\"):\n"
        "        st.session_state.view = \"home\"\n"
        "        st.rerun()\n"
        "    try:\n"
        "        from meridium_study import render_study_hub\n"
        "        render_study_hub(st, st.session_state)\n"
        "    except Exception as _e:\n"
        "        st.error(\"Study offline: \" + str(_e))\n"
        "        st.exception(_e)\n"
        "    st.stop()\n"
        "\nif st.session_state.view == \"languages\":\n"
        "    if st.button(\"Back\", key=\"lang_back\"):\n"
        "        st.session_state.view = \"home\"\n"
        "        st.rerun()\n"
        "    try:\n"
        "        from meridium_languages import render_languages\n"
        "        render_languages(st, st.session_state)\n"
        "    except Exception as _e:\n"
        "        st.error(\"Languages offline: \" + str(_e))\n"
        "        st.exception(_e)\n"
        "    st.stop()\n"
    )
    if 'view == "study"' not in code:
        for a in (
            'if st.session_state.view == "home":',
            "if st.session_state.view == 'home':",
        ):
            if a in code:
                code = code.replace(a, handlers + "\n" + a, 1)
                break
        else:
            code = code + handlers

    if "chess_learn_gambits" not in code:
        chess_inject = (
            "\n    # chess_learn_gambits\n"
            "    _chess_mode = st.radio(\n"
            "        \"Chess mode\",\n"
            "        [\"Play\", \"Learn gambits\"],\n"
            "        horizontal=True,\n"
            "        key=\"chess_mode_toggle\",\n"
            "    )\n"
            "    if _chess_mode == \"Learn gambits\":\n"
            "        try:\n"
            "            from meridium_gambits import render_gambit_trainer\n"
            "            render_gambit_trainer(st, st.session_state)\n"
            "        except Exception as _ge:\n"
            "            st.error(\"Gambit trainer offline: \" + str(_ge))\n"
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

    if "lab_lore_pack" not in code:
        lab_inject = (
            "\n    # lab_lore_pack\n"
            "    with st.expander(\"Archive chapters / Lore\", expanded=False):\n"
            "        try:\n"
            "            from meridium_lore_pack import render_lore_pack\n"
            "            render_lore_pack(st, st.session_state)\n"
            "        except Exception as _le:\n"
            "            st.caption(\"Lore offline: \" + str(_le))\n"
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

    if "drift_to_void_reliquary" not in code:
        inject = (
            "\n        if st.button(\"Enter Void Reliquary\", key=\"drift_to_void_reliquary\", "
            "use_container_width=True):\n"
            "            st.session_state._themes_from = \"drift\"\n"
            "            st.session_state.view = \"themes\"\n"
            "            st.rerun()\n"
            "        st.caption(\"Atmospheres / Residuum\")\n"
            "        st.divider()\n"
        )
        needle = (
            "with t_shop:\n"
            "        st.caption(\"Spend Residuum on palettes, type, lore, and latent modules.\")"
        )
        if needle in code:
            code = code.replace(
                needle,
                "with t_shop:\n" + inject
                + "        st.caption(\"Spend Residuum on palettes, type, lore, and latent modules.\")",
                1,
            )

    code = "".join(ch for ch in code if not (0xD800 <= ord(ch) <= 0xDFFF))
    return code
