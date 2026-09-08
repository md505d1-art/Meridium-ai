"""Meridium Void Reliquary — atmospheric themes."""
from __future__ import annotations

import json
from pathlib import Path

try:
    from meridium_theme_fx import theme_engine_html, _css_for
except Exception:
    def theme_engine_html(theme_id):
        return ""
    def _css_for(theme_id):
        return "body, .stApp { background: #0a0810 !important; }"

THEMES = {
    "default": {
        "name": "Meridium Default",
        "desc": "Clean dark violet base",
        "preview": "#1a1028",
        "price": 0,
        "tier": "free",
    },
    "rainy_kyoto": {
        "name": "Rainy Kyoto",
        "desc": "Rain, fog, thunder over a quiet town",
        "preview": "#1a2030",
        "price": 80,
        "tier": "premium",
    },
    "neon_tokyo": {
        "name": "Neon Tokyo",
        "desc": "Scanlines, neon pink and cyan",
        "preview": "#1a0520",
        "price": 90,
        "tier": "premium",
    },
    "aurora": {
        "name": "Aurora",
        "desc": "Northern lights wash",
        "preview": "#0a1a18",
        "price": 70,
        "tier": "standard",
    },
    "sakura": {
        "name": "Sakura Night",
        "desc": "Petals in the dark",
        "preview": "#1a1018",
        "price": 60,
        "tier": "standard",
    },
    "static_void": {
        "name": "Static Void",
        "desc": "CRT noise and deep black",
        "preview": "#050508",
        "price": 75,
        "tier": "standard",
    },
}


def _data_dir() -> Path:
    try:
        from meridium_paths import meridium_data_dir
        return meridium_data_dir()
    except Exception:
        import tempfile
        import os
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
    tid = u.get("active") or "default"
    return tid if tid in THEMES else "default"


def set_user_theme(username: str, theme_id: str) -> None:
    prefs = load_theme_prefs()
    u = prefs.get(username) or {}
    u["active"] = theme_id
    owned = list(u.get("owned") or ["default"])
    if theme_id not in owned:
        owned.append(theme_id)
    u["owned"] = owned
    prefs[username] = u
    save_theme_prefs(prefs)


def get_owned_themes(username: str) -> list:
    prefs = load_theme_prefs()
    u = prefs.get(username) or {}
    owned = list(u.get("owned") or ["default"])
    if "default" not in owned:
        owned.insert(0, "default")
    return owned


def unlock_theme_purchase(username: str, theme_id: str) -> None:
    prefs = load_theme_prefs()
    u = prefs.get(username) or {}
    owned = list(u.get("owned") or ["default"])
    if theme_id not in owned:
        owned.append(theme_id)
    u["owned"] = owned
    prefs[username] = u
    save_theme_prefs(prefs)


def unlocked_themes(ss, username: str) -> list:
    return get_owned_themes(username)


def apply_theme_to_app(st, theme_id: str) -> None:
    try:
        html = theme_engine_html(theme_id or "default")
        if html:
            import streamlit.components.v1 as components
            components.html(html, height=0, scrolling=False)
    except Exception:
        try:
            st.markdown(
                "<style id='meridium-theme'>" + _css_for(theme_id or "default") + "</style>",
                unsafe_allow_html=True,
            )
        except Exception:
            pass


def _get_residuum(ss) -> int:
    for key in ("residuum", "drift_residuum", "currency", "balance"):
        v = ss.get(key)
        if isinstance(v, (int, float)):
            return int(v)
    if "residuum" not in ss:
        ss["residuum"] = 100
    return int(ss.get("residuum") or 0)


def _spend_residuum(ss, amount: int) -> bool:
    bal = _get_residuum(ss)
    if bal < amount:
        return False
    ss["residuum"] = bal - amount
    return True


def render_theme_shop(st, ss) -> None:
    st.markdown("### Void Reliquary")
    st.caption("Atmospheric themes \u00b7 Residuum")
    user = (ss.get("username") or "anon").strip() or "anon"
    bal = _get_residuum(ss)
    st.metric("Residuum", bal)
    owned = set(get_owned_themes(user))
    active = ss.get("active_theme") or get_user_theme(user)

    ids = list(THEMES.keys())
    for i in range(0, len(ids), 2):
        cols = st.columns(2)
        for j, tid in enumerate(ids[i : i + 2]):
            meta = THEMES[tid]
            with cols[j]:
                st.markdown("**" + meta["name"] + "**")
                st.caption(meta.get("desc") or "")
                st.caption(
                    "Tier: "
                    + str(meta.get("tier"))
                    + " \u00b7 "
                    + str(meta.get("price"))
                    + " Residuum"
                )
                if tid in owned:
                    if active == tid:
                        st.success("Active")
                    elif st.button("Apply", key="theme_apply_" + tid):
                        set_user_theme(user, tid)
                        ss["active_theme"] = tid
                        apply_theme_to_app(st, tid)
                        st.rerun()
                else:
                    price = int(meta.get("price") or 0)
                    if st.button("Unlock (" + str(price) + ")", key="theme_buy_" + tid):
                        if price <= 0 or _spend_residuum(ss, price):
                            unlock_theme_purchase(user, tid)
                            set_user_theme(user, tid)
                            ss["active_theme"] = tid
                            st.success("Unlocked " + meta["name"])
                            st.rerun()
                        else:
                            st.warning("Not enough Residuum")

    try:
        apply_theme_to_app(st, active)
    except Exception:
        pass


def apply_theme_shop_routes(code: str) -> str:
    return code
