"""Meridium Void Reliquary — free animated atmospheres (always equippable)."""
from __future__ import annotations

import json
from pathlib import Path

try:
    from meridium_theme_fx import theme_engine_html, _css_for
except Exception:
    def theme_engine_html(theme_id):
        return ""

    def _css_for(theme_id):
        return (
            "html,body,.stApp,[data-testid=\"stAppViewContainer\"]{"
            "background:#0a0810!important;}"
        )

THEMES = {
    "default": {
        "name": "Meridium Default",
        "desc": "Clean dark violet base · the original signal",
        "preview": "#1a1028",
    },
    "rainy_kyoto": {
        "name": "Rainy Kyoto",
        "desc": "Lantern night · layered rain · fog · distant thunder",
        "preview": "#1a2238",
    },
    "neon_tokyo": {
        "name": "Neon Tokyo",
        "desc": "Magenta / cyan district · scanlines · electric haze",
        "preview": "#1a0a28",
    },
    "deep_ocean": {
        "name": "Deep Ocean",
        "desc": "Abyss blue · god rays · rising plankton",
        "preview": "#0a2a40",
    },
    "aurora": {
        "name": "Aurora North",
        "desc": "Green-violet curtains · polar night · soft stars",
        "preview": "#0a1228",
    },
    "sakura": {
        "name": "Ember Sakura",
        "desc": "Falling petals · warm dusk · rising embers",
        "preview": "#4a2030",
    },
    "static_void": {
        "name": "Static Void",
        "desc": "CRT snow · phosphor bloom · signal drop",
        "preview": "#111111",
    },
    "golden_hour": {
        "name": "Golden Hour",
        "desc": "Sun haze · dust motes · long amber light",
        "preview": "#4a3020",
    },
    "cyber_rain": {
        "name": "Cyber Rain",
        "desc": "Matrix glyphs · green phosphor · cascading code",
        "preview": "#021a0a",
    },
    "paper_lantern": {
        "name": "Paper Lantern",
        "desc": "Warm floating lights · soft flicker · quiet festival",
        "preview": "#2a2218",
    },
}

_FX_ALIAS = {
    "aurora": "aurora_north",
    "sakura": "ember_sakura",
}


def _fx_id(theme_id: str) -> str:
    return _FX_ALIAS.get(theme_id or "default", theme_id or "default")


def _data_dir() -> Path:
    try:
        from meridium_paths import meridium_data_dir

        return meridium_data_dir()
    except Exception:
        import os
        import tempfile

        if os.environ.get("STREAMLIT_SERVER_HEADLESS"):
            d = Path(tempfile.gettempdir()) / "meridium_data"
        else:
            d = Path(__file__).resolve().parent / "data"
        try:
            d.mkdir(parents=True, exist_ok=True)
        except Exception:
            d = Path(tempfile.gettempdir()) / "meridium_data"
            try:
                d.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
        return d


def load_theme_prefs() -> dict:
    p = _data_dir() / "theme_prefs.json"
    try:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def save_theme_prefs(prefs: dict) -> None:
    try:
        (_data_dir() / "theme_prefs.json").write_text(
            json.dumps(prefs, indent=2), encoding="utf-8"
        )
    except Exception:
        pass


def get_user_theme(username: str) -> str:
    prefs = load_theme_prefs()
    u = prefs.get(username) or prefs.get("anon") or {}
    tid = u.get("active") or u.get("theme") or "default"
    return tid if tid in THEMES else "default"


def set_user_theme(username: str, theme_id: str) -> None:
    if theme_id not in THEMES:
        theme_id = "default"
    prefs = load_theme_prefs()
    u = prefs.get(username) or {}
    u["active"] = theme_id
    u["theme"] = theme_id
    u["owned"] = list(THEMES.keys())
    prefs[username] = u
    save_theme_prefs(prefs)


def get_owned_themes(username: str) -> list:
    return list(THEMES.keys())


def unlock_theme_purchase(username: str, theme_id: str) -> None:
    set_user_theme(username, theme_id)


def unlocked_themes(ss, username: str) -> list:
    return list(THEMES.keys())


def apply_theme_to_app(st, theme_id: str) -> None:
    tid = theme_id or "default"
    fx = _fx_id(tid)
    try:
        html = theme_engine_html(fx)
        if html:
            import streamlit.components.v1 as components

            components.html(html, height=0, scrolling=False)
            return
    except Exception:
        pass
    try:
        st.markdown(
            "<style id='meridium-theme'>" + _css_for(fx) + "</style>",
            unsafe_allow_html=True,
        )
    except Exception:
        pass


def render_theme_shop(st, ss) -> None:
    user = (ss.get("username") or "anon").strip() or "anon"
    active = ss.get("active_theme") or get_user_theme(user)
    if active not in THEMES:
        active = "default"

    st.markdown("### ◈ Void Reliquary")
    st.caption("Living atmospheres · free to equip · custom motion and chrome")

    ids = list(THEMES.keys())
    for i in range(0, len(ids), 2):
        cols = st.columns(2)
        for j, tid in enumerate(ids[i : i + 2]):
            meta = THEMES[tid]
            with cols[j]:
                color = meta.get("preview", "#222")
                st.markdown(
                    f"<div style='height:72px;border-radius:16px;margin-bottom:8px;"
                    f"background:linear-gradient(135deg,{color} 0%,#0a0a0a 100%);"
                    f"border:1px solid rgba(255,255,255,0.14);"
                    f"box-shadow:0 0 28px {color}44;'></div>",
                    unsafe_allow_html=True,
                )
                st.markdown(f"**{meta['name']}**")
                st.caption(meta.get("desc") or "")
                if active == tid:
                    st.button(
                        "Equipped ✓",
                        key=f"theme_eq_{tid}",
                        disabled=True,
                        use_container_width=True,
                    )
                else:
                    if st.button(
                        "Equip",
                        key=f"theme_eq_{tid}",
                        use_container_width=True,
                        type="primary",
                    ):
                        set_user_theme(user, tid)
                        ss["active_theme"] = tid
                        try:
                            ss["theme"] = tid
                        except Exception:
                            pass
                        try:
                            from meridium_polish import sync_session_to_profile

                            sync_session_to_profile(ss)
                        except Exception:
                            pass
                        apply_theme_to_app(st, tid)
                        st.success(f"Atmosphere: {meta['name']}")
                        st.rerun()

    try:
        apply_theme_to_app(st, active)
    except Exception:
        pass


def apply_theme_shop_routes(code: str) -> str:
    """Inject themes view + buttons on Drift and Home. Always runs."""

    # --- Themes view (idempotent) ---
    if "themes_back_v45" not in code:
        handler = (
            '\nif st.session_state.get("view") == "themes":\n'
            '    if st.button("← Back", key="themes_back_v45"):\n'
            '        st.session_state.view = st.session_state.get("_themes_from") or "home"\n'
            '        st.rerun()\n'
            '    try:\n'
            '        from meridium_themes import render_theme_shop, apply_theme_to_app, get_user_theme\n'
            '        _th = st.session_state.get("active_theme") or get_user_theme(\n'
            '            st.session_state.get("username") or "anon"\n'
            '        )\n'
            '        apply_theme_to_app(st, _th)\n'
            '        render_theme_shop(st, st.session_state)\n'
            '    except Exception as _te:\n'
            '        st.error("Void Reliquary offline: " + str(_te))\n'
            '        st.exception(_te)\n'
            '    st.stop()\n'
        )
        inserted = False
        for a in (
            'if st.session_state.view == "home":',
            "if st.session_state.view == 'home':",
            'if st.session_state.get("view") == "home":',
            'if st.session_state.view == "drift":',
        ):
            if a in code:
                code = code.replace(a, handler + "\n" + a, 1)
                inserted = True
                break
        if not inserted:
            code = code + handler

    # --- Button inside Drift Counter ---
    if "drift_to_void_reliquary" not in code:
        inject = (
            '\n        if st.button("◈ Enter Void Reliquary", key="drift_to_void_reliquary", use_container_width=True):\n'
            '            st.session_state._themes_from = "drift"\n'
            '            st.session_state.view = "themes"\n'
            '            st.rerun()\n'
            '        st.caption("Animated atmospheres · free equip")\n'
            '        st.divider()\n'
        )
        needle = 'st.caption("Spend Residuum on palettes, type, lore, and latent modules.")'
        if needle in code:
            # place just before the caption inside t_shop
            code = code.replace(needle, inject + "        " + needle, 1)
        elif 't_shop, t_quests, t_inv = st.tabs(["Counter", "Fieldwork", "Holdings"])' in code:
            code = code.replace(
                't_shop, t_quests, t_inv = st.tabs(["Counter", "Fieldwork", "Holdings"])',
                't_shop, t_quests, t_inv = st.tabs(["Counter", "Fieldwork", "Holdings"])\n'
                '    with t_shop:\n'
                + inject.replace("\n        ", "\n        "),
                1,
            )

    # --- Home shortcut (always visible) ---
    if "home_void_reliquary_v45" not in code:
        home_btn = (
            '\n    if st.button("◈ Void Reliquary", key="home_void_reliquary_v45", use_container_width=True):\n'
            '        st.session_state._themes_from = "home"\n'
            '        st.session_state.view = "themes"\n'
            '        st.rerun()\n'
        )
        for m in (
            'if st.session_state.view == "home":',
            "if st.session_state.view == 'home':",
            'if st.session_state.get("view") == "home":',
        ):
            if m in code:
                # insert after the home if line
                idx = code.find(m)
                end = code.find("\n", idx) + 1
                code = code[:end] + home_btn + code[end:]
                break

    return code
