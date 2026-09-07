"""Meridium theme shop — atmospheric animated themes."""
from __future__ import annotations

import json
from pathlib import Path

from meridium_theme_fx import theme_engine_html, _css_for

THEMES = {
    "default": {"name": "Meridium Default", "desc": "Clean dark violet base", "preview": "#1a1028"},
    "rainy_kyoto": {"name": "Rainy Kyoto", "desc": "Lantern night \u00b7 driving rain \u00b7 fog \u00b7 thunder", "preview": "#1a2238"},
    "neon_tokyo": {"name": "Neon Tokyo", "desc": "Magenta / cyan district \u00b7 scanlines", "preview": "#1a0a28"},
    "deep_ocean": {"name": "Deep Ocean", "desc": "Abyss blue \u00b7 rising bubbles", "preview": "#0a2a40"},
    "aurora_north": {"name": "Aurora North", "desc": "Green-violet curtains \u00b7 polar night", "preview": "#0a1228"},
    "ember_sakura": {"name": "Ember Sakura", "desc": "Falling petals \u00b7 warm dusk", "preview": "#4a2030"},
    "static_void": {"name": "Static Void", "desc": "CRT snow \u00b7 mono", "preview": "#111111"},
    "golden_hour": {"name": "Golden Hour", "desc": "Sun haze \u00b7 amber light", "preview": "#4a3020"},
    "cyber_rain": {"name": "Cyber Rain", "desc": "Matrix glyphs \u00b7 green phosphor", "preview": "#021a0a"},
    "paper_lantern": {"name": "Paper Lantern", "desc": "Warm floating lights", "preview": "#2a2218"},
}


def _data_dir() -> Path:
    d = Path(__file__).resolve().parent / "data"
    d.mkdir(parents=True, exist_ok=True)
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
        (_data_dir() / "theme_prefs.json").write_text(json.dumps(prefs, indent=2), encoding="utf-8")
    except Exception:
        pass


def get_user_theme(username: str) -> str:
    return (load_theme_prefs().get(username) or {}).get("theme") or "default"


def set_user_theme(username: str, theme_id: str) -> None:
    prefs = load_theme_prefs()
    prefs.setdefault(username, {})["theme"] = theme_id
    save_theme_prefs(prefs)


def unlocked_themes(ss, username: str) -> list:
    return list(THEMES.keys())


def inject_theme_html(theme_id: str) -> str:
    return f"<style id=\"meridium-theme\">{_css_for(theme_id)}</style>"


def apply_theme_to_app(st, theme_id: str) -> None:
    try:
        html = theme_engine_html(theme_id or "default")
        st.components.v1.html(html, height=0, scrolling=False)
    except Exception:
        try:
            st.markdown(f"<style id='meridium-theme'>{_css_for(theme_id)}</style>", unsafe_allow_html=True)
        except Exception:
            pass


def render_theme_shop(st, ss) -> None:
    user = (ss.get("username") or "anon").strip() or "anon"
    st.markdown("### \u25c8 Theme atelier")
    st.caption("Living atmospheres \u00b7 rain, neon, aurora, petals \u00b7 equip one")
    cur = ss.get("active_theme") or get_user_theme(user)
    ids = list(THEMES.keys())
    for row in range(0, len(ids), 2):
        cols = st.columns(2)
        for j, tid in enumerate(ids[row:row + 2]):
            meta = THEMES[tid]
            with cols[j]:
                color = meta.get("preview", "#222")
                st.markdown(
                    f"<div style='height:56px;border-radius:14px;margin-bottom:6px;"
                    f"background:linear-gradient(135deg,{color},#0a0a0a);"
                    f"border:1px solid rgba(255,255,255,0.12);'></div>",
                    unsafe_allow_html=True,
                )
                st.markdown(f"**{meta['name']}**")
                st.caption(meta["desc"])
                equipped = cur == tid
                if st.button(
                    "Equipped \u2713" if equipped else "Equip theme",
                    key=f"theme_eq_{tid}",
                    disabled=equipped,
                    use_container_width=True,
                    type="primary" if not equipped else "secondary",
                ):
                    set_user_theme(user, tid)
                    ss["active_theme"] = tid
                    try:
                        from meridium_polish import sync_session_to_profile
                        sync_session_to_profile(ss)
                    except Exception:
                        pass
                    st.success(f"Atmosphere: {meta['name']}")
                    st.rerun()


def apply_theme_shop_routes(code: str) -> str:
    if "theme_atelier_drift_btn" in code:
        return code
    drift_btn = (
        "\n    if st.button(\"\u25c8 Theme atelier\", key=\"theme_atelier_drift_btn\", use_container_width=True):\n"
        "        st.session_state._themes_from = \"drift\"\n"
        "        st.session_state.view = \"themes\"\n"
        "        st.rerun()\n"
    )
    for needle in ('key="drift_to_menu"', "key='drift_to_menu'"):
        if needle in code and "theme_atelier_drift_btn" not in code:
            idx = code.find(needle)
            j = code.find("st.rerun()", idx)
            if j > 0:
                j = code.find("\n", j) + 1
                code = code[:j] + drift_btn + code[j:]
            break
    if 'view == "themes"' not in code:
        handler = (
            "\nif st.session_state.view == \"themes\":\n"
            "    if st.button(\"\u2190 Back\", key=\"themes_back\"):\n"
            "        st.session_state.view = st.session_state.get(\"_themes_from\") or \"home\"\n"
            "        st.rerun()\n"
            "    try:\n"
            "        from meridium_themes import render_theme_shop, apply_theme_to_app, get_user_theme\n"
            "        _th = st.session_state.get(\"active_theme\") or get_user_theme(st.session_state.get(\"username\") or \"anon\")\n"
            "        apply_theme_to_app(st, _th)\n"
            "        render_theme_shop(st, st.session_state)\n"
            "    except Exception as _te:\n"
            "        st.error(\"Theme atelier offline: \" + str(_te))\n"
            "    st.stop()\n"
        )
        for a in (
            'if st.session_state.view == "drift":',
            "if st.session_state.view == 'drift':",
            'if st.session_state.view == "home":',
        ):
            if a in code:
                code = code.replace(a, handler + "\n" + a, 1)
                break
        else:
            code = code + handler
    return code
