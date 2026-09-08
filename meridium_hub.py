"""Meridium Learning + Lore + UI hub — wires Study, Gambits, Languages, Lore, UI redesign."""
from __future__ import annotations


def apply_learning_hub(code: str) -> str:
    """Inject views + nav for study, gambits, languages, lore; inject UI v2 boot."""
    if "meridium_learning_hub_v1" in code and "bm_study" in code and "drift_to_void_reliquary" in code:
        return code

    boot = (
        "\n# meridium_learning_hub_v1\n"
        "try:\n"
        "    from meridium_ui_v2 import inject_ui\n"
        "    inject_ui(st)\n"
        "except Exception:\n"
        "    pass\n"
    )
    if "meridium_learning_hub_v1" not in code:
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
        else:
            code = boot + code

    nav = (
        "\n        if st.button(\"\ud83d\udcda  Study\", use_container_width=True, key=\"bm_study\"):\n"
        "            st.session_state.view = \"study\"\n"
        "            st.rerun()\n"
        "        if st.button(\"\u265f  Gambits\", use_container_width=True, key=\"bm_gambits\"):\n"
        "            st.session_state.view = \"gambits\"\n"
        "            st.rerun()\n"
        "        if st.button(\"\ud83d\udde3\ufe0f  Languages\", use_container_width=True, key=\"bm_languages\"):\n"
        "            st.session_state.view = \"languages\"\n"
        "            st.rerun()\n"
        "        if st.button(\"\ud83d\udcd6  Lore\", use_container_width=True, key=\"bm_lore_pack\"):\n"
        "            st.session_state.view = \"lore_pack\"\n"
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

    handlers = (
        "\nif st.session_state.view == \"study\":\n"
        "    if st.button(\"\u2190 Home\", key=\"study_back\"):\n"
        "        st.session_state.view = \"home\"\n"
        "        st.rerun()\n"
        "    try:\n"
        "        from meridium_study import render_study_hub\n"
        "        render_study_hub(st, st.session_state)\n"
        "    except Exception as _e:\n"
        "        st.error(\"Study hub offline: \" + str(_e))\n"
        "    st.stop()\n"
        "\nif st.session_state.view == \"gambits\":\n"
        "    if st.button(\"\u2190 Home\", key=\"gambits_back\"):\n"
        "        st.session_state.view = \"home\"\n"
        "        st.rerun()\n"
        "    try:\n"
        "        from meridium_gambits import render_gambit_trainer\n"
        "        render_gambit_trainer(st, st.session_state)\n"
        "    except Exception as _e:\n"
        "        st.error(\"Gambit Academy offline: \" + str(_e))\n"
        "    st.stop()\n"
        "\nif st.session_state.view == \"languages\":\n"
        "    if st.button(\"\u2190 Home\", key=\"lang_back\"):\n"
        "        st.session_state.view = \"home\"\n"
        "        st.rerun()\n"
        "    try:\n"
        "        from meridium_languages import render_languages\n"
        "        render_languages(st, st.session_state)\n"
        "    except Exception as _e:\n"
        "        st.error(\"Language Lab offline: \" + str(_e))\n"
        "    st.stop()\n"
        "\nif st.session_state.view == \"lore_pack\":\n"
        "    if st.button(\"\u2190 Home\", key=\"lore_pack_back\"):\n"
        "        st.session_state.view = \"home\"\n"
        "        st.rerun()\n"
        "    try:\n"
        "        from meridium_lore_pack import render_lore_pack\n"
        "        render_lore_pack(st, st.session_state)\n"
        "    except Exception as _e:\n"
        "        st.error(\"Lore pack offline: \" + str(_e))\n"
        "    st.stop()\n"
    )
    if 'view == "study"' not in code:
        for a in (
            'if st.session_state.view == "home":',
            "if st.session_state.view == 'home':",
            'if st.session_state.view == "drift":',
        ):
            if a in code:
                code = code.replace(a, handlers + "\n" + a, 1)
                break
        else:
            code = code + handlers

    if "drift_to_void_reliquary" not in code:
        inject = (
            "\n        if st.button(\"\u25c8 Enter Void Reliquary\", key=\"drift_to_void_reliquary\", "
            "use_container_width=True):\n"
            "            st.session_state._themes_from = \"drift\"\n"
            "            st.session_state.view = \"themes\"\n"
            "            st.rerun()\n"
            "        st.caption(\"Atmospheres \u00b7 Residuum \u00b7 living themes\")\n"
            "        st.divider()\n"
        )
        needle = (
            "with t_shop:\n"
            "        st.caption(\"Spend Residuum on palettes, type, lore, and latent modules.\")"
        )
        if needle in code:
            code = code.replace(
                needle,
                "with t_shop:\n" + inject + "        st.caption(\"Spend Residuum on palettes, type, lore, and latent modules.\")",
                1,
            )

    return code
