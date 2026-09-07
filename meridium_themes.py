"""Meridium Void Reliquary — atmospheric animated themes paid with Residuum."""
from __future__ import annotations

import json
from pathlib import Path

from meridium_theme_fx import theme_engine_html, _css_for

# Stable Residuum prices. default is free forever.
THEMES = {
    "default": {
        "name": "Meridium Default",
        "desc": "Clean dark violet base · the original signal",
        "preview": "#1a1028",
        "price": 0,
        "tier": "free",
    },
    "rainy_kyoto": {
        "name": "Rainy Kyoto",
        "desc": "Lantern night · driving rain · fog · distant thunder",
        "preview": "#1a2238",
        "price": 60,
        "tier": "standard",
    },
    "neon_tokyo": {
        "name": "Neon Tokyo",
        "desc": "Magenta / cyan district · scanlines · wet asphalt glow",
        "preview": "#1a0a28",
        "price": 80,
        "tier": "standard",
    },
    "deep_ocean": {
        "name": "Deep Ocean",
        "desc": "Abyss blue · rising bubbles · pressure silence",
        "preview": "#0a2a40",
        "price": 70,
        "tier": "standard",
    },
    "aurora_north": {
        "name": "Aurora North",
        "desc": "Green-violet curtains · polar night · solar wind",
        "preview": "#0a1228",
        "price": 90,
        "tier": "premium",
    },
    "ember_sakura": {
        "name": "Ember Sakura",
        "desc": "Falling petals · warm dusk · charcoal air",
        "preview": "#4a2030",
        "price": 75,
        "tier": "standard",
    },
    "static_void": {
        "name": "Static Void",
        "desc": "CRT snow · mono · residual noise floor",
        "preview": "#111111",
        "price": 50,
        "tier": "standard",
    },
    "golden_hour": {
        "name": "Golden Hour",
        "desc": "Sun haze · amber light · long shadows",
        "preview": "#4a3020",
        "price": 65,
        "tier": "standard",
    },
    "cyber_rain": {
        "name": "Cyber Rain",
        "desc": "Matrix glyphs · green phosphor · cascading code",
        "preview": "#021a0a",
        "price": 100,
        "tier": "premium",
    },
    "paper_lantern": {
        "name": "Paper Lantern",
        "desc": "Warm floating lights · soft paper · quiet festival",
        "preview": "#2a2218",
        "price": 55,
        "tier": "standard",
    },
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


def get_owned_themes(username: str) -> list:
    prefs = load_theme_prefs().get(username) or {}
    owned = list(prefs.get("owned") or ["default"])
    if "default" not in owned:
        owned.insert(0, "default")
    return owned


def unlock_theme_purchase(username: str, theme_id: str) -> None:
    prefs = load_theme_prefs()
    u = prefs.setdefault(username, {})
    owned = list(u.get("owned") or ["default"])
    if theme_id not in owned:
        owned.append(theme_id)
    u["owned"] = owned
    save_theme_prefs(prefs)


def unlocked_themes(ss, username: str) -> list:
    return get_owned_themes(username)


def inject_theme_html(theme_id: str) -> str:
    return f'<style id="meridium-theme">{_css_for(theme_id)}</style>'


def apply_theme_to_app(st, theme_id: str) -> None:
    try:
        html = theme_engine_html(theme_id or "default")
        st.components.v1.html(html, height=0, scrolling=False)
    except Exception:
        try:
            st.markdown(f"<style id='meridium-theme'>{_css_for(theme_id)}</style>", unsafe_allow_html=True)
        except Exception:
            pass


def _get_residuum(ss) -> int:
    for key in ("residuum", "drift_residuum", "currency", "balance"):
        v = ss.get(key)
        if isinstance(v, (int, float)):
            return int(v)
    try:
        from meridium_polish import load_profile

        prof = load_profile(ss.get("username") or "anon")
        return int(prof.get("residuum") or 0)
    except Exception:
        return int(ss.get("residuum") or 0)


def _spend_residuum(ss, amount: int) -> bool:
    bal = _get_residuum(ss)
    if bal < amount:
        return False
    new_bal = bal - amount
    ss["residuum"] = new_bal
    for key in ("drift_residuum", "currency", "balance"):
        if key in ss:
            ss[key] = new_bal
    try:
        from meridium_polish import sync_session_to_profile

        sync_session_to_profile(ss)
    except Exception:
        pass
    return True


def render_theme_shop(st, ss) -> None:
    """Void Reliquary UI — atmospheres bought with Residuum."""
    user = (ss.get("username") or "anon").strip() or "anon"
    owned = set(get_owned_themes(user))
    cur = ss.get("active_theme") or get_user_theme(user)
    bal = _get_residuum(ss)

    st.markdown("### ◈ Void Reliquary")
    st.caption("Atmospheres forged from residual signal · pay in Residuum · equip one")
    st.markdown(f"**Residuum balance:** `{bal}`")

    ids = list(THEMES.keys())
    for row in range(0, len(ids), 2):
        cols = st.columns(2)
        for j, tid in enumerate(ids[row : row + 2]):
            meta = THEMES[tid]
            with cols[j]:
                color = meta.get("preview", "#222")
                price = int(meta.get("price") or 0)
                is_owned = tid in owned or price == 0
                equipped = cur == tid

                st.markdown(
                    f"<div style='height:72px;border-radius:16px;margin-bottom:8px;"
                    f"background:linear-gradient(135deg,{color} 0%,#0a0a0a 100%);"
                    f"border:1px solid rgba(255,255,255,0.14);"
                    f"box-shadow:0 0 28px {color}44;'></div>",
                    unsafe_allow_html=True,
                )
                st.markdown(f"**{meta['name']}**")
                st.caption(meta["desc"])
                if price > 0:
                    st.caption(f"◈ {price} Residuum" + (" · owned" if is_owned else ""))

                if equipped:
                    st.button(
                        "Equipped ✓",
                        key=f"theme_eq_{tid}",
                        disabled=True,
                        use_container_width=True,
                    )
                elif is_owned:
                    if st.button(
                        "Equip",
                        key=f"theme_eq_{tid}",
                        use_container_width=True,
                        type="primary",
                    ):
                        set_user_theme(user, tid)
                        ss["active_theme"] = tid
                        try:
                            from meridium_polish import sync_session_to_profile

                            sync_session_to_profile(ss)
                        except Exception:
                            pass
                        st.success(f"Atmosphere locked: {meta['name']}")
                        st.rerun()
                else:
                    can_buy = bal >= price
                    label = f"Acquire · {price} Residuum" if can_buy else f"Need {price} Residuum"
                    if st.button(
                        label,
                        key=f"theme_buy_{tid}",
                        disabled=not can_buy,
                        use_container_width=True,
                    ):
                        if _spend_residuum(ss, price):
                            unlock_theme_purchase(user, tid)
                            set_user_theme(user, tid)
                            ss["active_theme"] = tid
                            st.success(f"Acquired & equipped: {meta['name']}")
                            st.rerun()
                        else:
                            st.error("Insufficient Residuum")


def apply_theme_shop_routes(code: str) -> str:
    """Register themes view + inject Void Reliquary button inside Drift Counter only."""
    # --- 1. themes view handler (no stray buttons) ---
    if 'view == "themes"' not in code and "view == 'themes'" not in code:
        handler = (
            '\nif st.session_state.view == "themes":\n'
            '    if st.button("← Back", key="themes_back"):\n'
            '        st.session_state.view = st.session_state.get("_themes_from") or "drift"\n'
            '        st.rerun()\n'
            '    try:\n'
            '        from meridium_themes import render_theme_shop, apply_theme_to_app, get_user_theme\n'
            '        _th = st.session_state.get("active_theme") or get_user_theme(st.session_state.get("username") or "anon")\n'
            '        apply_theme_to_app(st, _th)\n'
            '        render_theme_shop(st, st.session_state)\n'
            '    except Exception as _te:\n'
            '        st.error("Void Reliquary offline: " + str(_te))\n'
            '    st.stop()\n'
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

    # --- 2. Inject entry button inside Drift Counter (render_bazaar_tab) ---
    if "drift_to_void_reliquary" not in code:
        inject = (
            '\n        if st.button("◈ Enter Void Reliquary", key="drift_to_void_reliquary", use_container_width=True):\n'
            '            st.session_state._themes_from = "drift"\n'
            '            st.session_state.view = "themes"\n'
            '            st.rerun()\n'
            '        st.caption("Atmospheres · Residuum · living themes")\n'
            '        st.divider()\n'
        )
        needle = 'with t_shop:\n        st.caption("Spend Residuum on palettes, type, lore, and latent modules.")'
        if needle in code:
            code = code.replace(
                needle,
                'with t_shop:\n'
                + inject
                + '        st.caption("Spend Residuum on palettes, type, lore, and latent modules.")',
                1,
            )
        else:
            # fallback: after tabs line
            alt = 't_shop, t_quests, t_inv = st.tabs(["Counter", "Fieldwork", "Holdings"])'
            if alt in code:
                code = code.replace(
                    alt,
                    alt
                    + '\n    # void reliquary entry injected by meridium_themes\n'
                    + '    # (button lives inside t_shop block when present)',
                    1,
                )

    # Remove any leftover old Theme atelier button if still present from prior patches
    for old in (
        'key="theme_atelier_drift_btn"',
        "key='theme_atelier_drift_btn'",
        'key="home_theme_atelier"',
        "key='home_theme_atelier'",
    ):
        if old in code:
            # soft-disable by renaming key so the button is never created with old key
            code = code.replace(old, old.replace("theme_atelier", "_retired_theme") + "_retired")

    return code
