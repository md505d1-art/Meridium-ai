"""Meridium visual theme shop — atmospheric animated themes."""
from __future__ import annotations
from pathlib import Path
import json

THEMES = {
    "default": {"name": "Meridium Default", "desc": "Clean dark violet base", "css": ""},
    "rainy_kyoto": {
        "name": "Rainy Kyoto",
        "desc": "Night rain over lantern-lit town · fog · thunder · cloud bubbles",
        "css": (
            ".stApp{background:linear-gradient(180deg,rgba(15,18,30,.55),rgba(20,24,40,.72)),"
            "radial-gradient(ellipse at 30% 80%,rgba(80,100,140,.35),transparent 55%),"
            "linear-gradient(180deg,#0b1020 0%,#1a2238 40%,#2a3348 100%)!important}"
            ".stApp::before{content:'';pointer-events:none;position:fixed;inset:0;z-index:9998;"
            "background-image:repeating-linear-gradient(180deg,transparent 0 12px,rgba(180,200,255,.08) 12px 13px),"
            "repeating-linear-gradient(170deg,transparent 0 18px,rgba(180,200,255,.05) 18px 19px);"
            "animation:merRain .7s linear infinite;opacity:.85}"
            ".stApp::after{content:'';pointer-events:none;position:fixed;inset:0;z-index:9997;"
            "background:radial-gradient(ellipse at 50% 100%,rgba(200,210,230,.18),transparent 55%);"
            "animation:merFog 8s ease-in-out infinite alternate}"
            "@keyframes merRain{from{background-position:0 0,0 0}to{background-position:0 40px,0 50px}}"
            "@keyframes merFog{from{opacity:.5}to{opacity:.9}}"
            "div[data-testid='stNotification'],.stAlert,[data-testid='stExpander']{"
            "background:rgba(230,235,245,.12)!important;border:1px solid rgba(200,210,230,.35)!important;"
            "border-radius:24px!important;backdrop-filter:blur(8px);box-shadow:0 8px 24px rgba(0,0,0,.25)}"
            "h1,h2,h3{text-shadow:0 1px 8px rgba(120,140,180,.35)}"
            "body{animation:merThunder 14s ease-in-out infinite}"
            "@keyframes merThunder{0%,92%,100%{filter:brightness(1)}93%{filter:brightness(1.35)}"
            "94%{filter:brightness(1.05)}96%{filter:brightness(1.4)}97%{filter:brightness(1)}}"
        ),
    },
    "neon_tokyo": {
        "name": "Neon Tokyo",
        "desc": "Magenta / cyan signage · scanlines · night district",
        "css": (
            ".stApp{background:linear-gradient(180deg,rgba(10,5,20,.75),rgba(20,8,30,.85)),"
            "repeating-linear-gradient(0deg,transparent 0 3px,rgba(255,0,128,.03) 3px 4px),"
            "linear-gradient(135deg,#0a0614 0%,#1a0a28 50%,#0a1828 100%)!important}"
            ".stApp::before{content:'';pointer-events:none;position:fixed;inset:0;z-index:9998;"
            "background:radial-gradient(circle at 20% 30%,rgba(255,0,128,.15),transparent 40%),"
            "radial-gradient(circle at 80% 70%,rgba(0,255,220,.12),transparent 40%);"
            "animation:merNeonPulse 4s ease-in-out infinite alternate}"
            "@keyframes merNeonPulse{from{opacity:.7}to{opacity:1}}"
            "h1,h2,h3{color:#ff4dc4!important;text-shadow:0 0 12px #ff4dc4,0 0 24px #00f5d4}"
            ".stButton>button{border:1px solid #00f5d4!important;box-shadow:0 0 12px rgba(0,245,212,.35)}"
            "[data-testid='stExpander']{border:1px solid rgba(255,0,128,.4)!important;"
            "box-shadow:0 0 20px rgba(255,0,128,.15)}"
        ),
    },
    "deep_ocean": {
        "name": "Deep Ocean",
        "desc": "Slow caustics · deep blue · floating bubbles",
        "css": (
            ".stApp{background:radial-gradient(ellipse at 50% 0%,rgba(40,120,180,.35),transparent 50%),"
            "linear-gradient(180deg,#021018 0%,#0a2a40 45%,#031520 100%)!important}"
            ".stApp::before{content:'';pointer-events:none;position:fixed;inset:0;z-index:9998;"
            "background-image:radial-gradient(circle at 20% 30%,rgba(120,200,255,.08) 0 2px,transparent 3px),"
            "radial-gradient(circle at 70% 60%,rgba(120,200,255,.1) 0 3px,transparent 4px),"
            "radial-gradient(circle at 40% 80%,rgba(120,200,255,.07) 0 2px,transparent 3px);"
            "background-size:200px 200px,280px 280px,160px 160px;animation:merBubbles 12s linear infinite}"
            "@keyframes merBubbles{from{background-position:0 100%,40px 100%,80px 100%}"
            "to{background-position:0 -100%,40px -120%,80px -80%}}"
            "h1,h2,h3{color:#7dd3fc!important}"
        ),
    },
    "aurora_north": {
        "name": "Aurora North",
        "desc": "Green / violet sky curtains · cold night",
        "css": (
            ".stApp{background:linear-gradient(180deg,#050814 0%,#0a1228 40%,#0c1a20 100%)!important}"
            ".stApp::before{content:'';pointer-events:none;position:fixed;top:0;left:0;right:0;height:45vh;z-index:9998;"
            "background:linear-gradient(110deg,transparent 0%,rgba(50,255,160,.18) 25%,"
            "rgba(120,80,255,.2) 50%,rgba(50,255,200,.15) 75%,transparent 100%);"
            "background-size:200% 100%;animation:merAurora 10s ease-in-out infinite alternate;filter:blur(12px)}"
            "@keyframes merAurora{from{background-position:0% 0%;opacity:.7}to{background-position:100% 0%;opacity:1}}"
            "h1,h2,h3{color:#a7f3d0!important;text-shadow:0 0 20px rgba(50,255,160,.4)}"
        ),
    },
    "ember_sakura": {
        "name": "Ember Sakura",
        "desc": "Petals falling · warm dusk · soft pink",
        "css": (
            ".stApp{background:linear-gradient(180deg,rgba(40,20,30,.5),rgba(30,15,25,.7)),"
            "linear-gradient(180deg,#2a1520 0%,#4a2030 50%,#1a1018 100%)!important}"
            ".stApp::before{content:'';pointer-events:none;position:fixed;inset:0;z-index:9998;"
            "background-image:radial-gradient(circle,rgba(255,180,200,.55) 0 3px,transparent 4px),"
            "radial-gradient(circle,rgba(255,150,180,.4) 0 2px,transparent 3px),"
            "radial-gradient(circle,rgba(255,200,210,.5) 0 2.5px,transparent 3.5px);"
            "background-size:120px 120px,180px 180px,90px 90px;animation:merPetals 14s linear infinite;opacity:.7}"
            "@keyframes merPetals{from{background-position:0 -20px,40px -40px,80px -10px}"
            "to{background-position:30px 100vh,10px 100vh,60px 100vh}}"
            "h1,h2,h3{color:#fecdd3!important}"
            "[data-testid='stExpander']{background:rgba(60,30,40,.45)!important;border-radius:18px!important;"
            "border:1px solid rgba(249,168,212,.3)!important}"
        ),
    },
    "static_void": {
        "name": "Static Void",
        "desc": "CRT noise · monochrome · glitch flicker",
        "css": (
            ".stApp{background:#080808!important;filter:contrast(1.05)}"
            ".stApp::before{content:'';pointer-events:none;position:fixed;inset:0;z-index:9998;"
            "background-image:url(\"data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.12'/%3E%3C/svg%3E\");"
            "animation:merStatic .4s steps(2) infinite;opacity:.35}"
            "@keyframes merStatic{0%{transform:translate(0,0)}100%{transform:translate(-2%,1%)}}"
            "h1,h2,h3,p,label{color:#d4d4d4!important;font-family:ui-monospace,monospace!important}"
            ".stButton>button{background:#111!important;color:#e5e5e5!important;border:1px solid #525252!important;border-radius:0!important}"
        ),
    },
    "golden_hour": {
        "name": "Golden Hour",
        "desc": "Warm sun haze · long shadows · soft grain",
        "css": (
            ".stApp{background:radial-gradient(ellipse at 80% 10%,rgba(255,180,80,.35),transparent 45%),"
            "linear-gradient(180deg,#2a1a10 0%,#4a3020 40%,#1a120c 100%)!important}"
            ".stApp::before{content:'';pointer-events:none;position:fixed;inset:0;z-index:9998;"
            "background:linear-gradient(180deg,rgba(255,200,100,.08),transparent 40%);"
            "animation:merHaze 6s ease-in-out infinite alternate}"
            "@keyframes merHaze{from{opacity:.6}to{opacity:1}}"
            "h1,h2,h3{color:#fcd34d!important;text-shadow:0 2px 12px rgba(251,191,36,.35)}"
            ".stButton>button{background:linear-gradient(180deg,#b45309,#78350f)!important;border:none!important;color:#fffbeb!important}"
        ),
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
    prefs = load_theme_prefs()
    return (prefs.get(username) or {}).get("theme") or "default"


def set_user_theme(username: str, theme_id: str) -> None:
    prefs = load_theme_prefs()
    prefs.setdefault(username, {})["theme"] = theme_id
    save_theme_prefs(prefs)


def unlocked_themes(ss, username: str) -> list:
    out = ["default", "rainy_kyoto", "golden_hour"]
    if ss.get("_wins") or ss.get("feat_chess_analysis"):
        out.append("neon_tokyo")
    if ss.get("puzzle_solved_day") or ss.get("rush_score"):
        out.append("deep_ocean")
    if len(ss.get("glitches_found") or []) >= 1 or ss.get("view") == "explore":
        out.append("ember_sakura")
    if len(ss.get("achievements") or []) >= 3:
        out.append("aurora_north")
    if ss.get("is_owner") or ss.get("view") == "owner_room":
        out.append("static_void")
    seen, uniq = set(), []
    for t in out:
        if t in THEMES and t not in seen:
            seen.add(t)
            uniq.append(t)
    return uniq


def theme_css(theme_id: str) -> str:
    t = THEMES.get(theme_id) or THEMES["default"]
    return t.get("css") or ""


def inject_theme_html(theme_id: str) -> str:
    css = theme_css(theme_id)
    if not css:
        return ""
    return f"<style id=\"meridium-theme\">\\n{css}\\n</style>"


def render_theme_shop(st, ss) -> None:
    user = (ss.get("username") or "anon").strip() or "anon"
    st.markdown("### Theme shop")
    st.caption("Atmospheric skins · animated layers · not ARG-locked")
    have = set(unlocked_themes(ss, user))
    cur = ss.get("active_theme") or get_user_theme(user)
    cols = st.columns(2)
    for i, (tid, meta) in enumerate(THEMES.items()):
        with cols[i % 2]:
            locked = tid not in have and tid != "default"
            st.markdown(f"**{meta['name']}" + (" 🔒" if locked else "") + "**")
            st.caption(meta["desc"])
            if locked:
                st.caption("Keep playing to unlock")
            else:
                if st.button(
                    "Equip" if cur != tid else "Equipped \u2713",
                    key=f"theme_eq_{tid}",
                    disabled=(cur == tid),
                    use_container_width=True,
                ):
                    set_user_theme(user, tid)
                    ss["active_theme"] = tid
                    st.success(f"Theme: {meta['name']}")
                    st.rerun()
