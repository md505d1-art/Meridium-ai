"""Meridium polish: profile, achievements, onboarding, mobile, PWA, analytics, pulses."""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

ACHIEVEMENTS = {
    "first_boot": {"name": "First light", "desc": "Opened Meridium"},
    "first_marker": {"name": "Glitch touch", "desc": "Secured a Voss marker"},
    "all_markers": {"name": "Triangulated", "desc": "All three markers"},
    "complex_visit": {"name": "Beyond the board", "desc": "Entered the Complex"},
    "spectrum": {"name": "Violet aligned", "desc": "Opened the spectrum lock"},
    "stars": {"name": "Constellation", "desc": "Star chart spelled VOSS"},
    "plant_3": {"name": "Bay-7 caretaker", "desc": "3-day greenhouse streak"},
    "puzzle_1": {"name": "Daily mind", "desc": "Solved a daily puzzle"},
    "online_1": {"name": "Across the wire", "desc": "Joined or created an online match"},
    "theme_1": {"name": "Skin deep", "desc": "Equipped a custom theme"},
    "wall_1": {"name": "Chalk mark", "desc": "Wrote on the anonymous wall"},
    "quiz_80": {"name": "Clear recall", "desc": "80%+ false memory quiz"},
}


def _data() -> Path:
    d = Path(__file__).resolve().parent / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _profile_path(user: str) -> Path:
    safe = "".join(c for c in (user or "anon").lower() if c.isalnum() or c in "-_")[:32] or "anon"
    return _data() / f"profile_{safe}.json"


def load_profile(user: str) -> dict:
    p = _profile_path(user)
    try:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"user": user, "achievements": [], "glitches_found": [], "theme": "default", "onboarded": False, "stats": {}}


def save_profile(user: str, prof: dict) -> None:
    try:
        prof["user"] = user
        prof["updated"] = datetime.now(timezone.utc).isoformat()
        _profile_path(user).write_text(json.dumps(prof, indent=2), encoding="utf-8")
    except Exception:
        pass


def sync_session_to_profile(ss) -> None:
    user = (ss.get("username") or "anon").strip() or "anon"
    prof = load_profile(user)
    g = list(dict.fromkeys((prof.get("glitches_found") or []) + list(ss.get("glitches_found") or [])))
    prof["glitches_found"] = g
    ss["glitches_found"] = g
    ach = set(prof.get("achievements") or []) | set(ss.get("achievements") or [])
    ach.add("first_boot")
    if g:
        ach.add("first_marker")
    if len(g) >= 3:
        ach.add("all_markers")
    if ss.get("view") == "explore" or ss.get("explore_room"):
        ach.add("complex_visit")
    if ss.get("spectrum_open"):
        ach.add("spectrum")
    if ss.get("stars_solved"):
        ach.add("stars")
    if ss.get("puzzle_solved_day"):
        ach.add("puzzle_1")
    if ss.get("online_code"):
        ach.add("online_1")
    if ss.get("active_theme") and ss.get("active_theme") != "default":
        ach.add("theme_1")
    if ss.get("quiz_result") and ss["quiz_result"].get("pct", 0) >= 80:
        ach.add("quiz_80")
    try:
        from arg_explore import greenhouse_state
        st = greenhouse_state(user)
        if int(st.get("streak") or 0) >= 3:
            ach.add("plant_3")
    except Exception:
        pass
    new = ach - set(prof.get("achievements") or [])
    prof["achievements"] = sorted(ach)
    ss["achievements"] = prof["achievements"]
    if ss.get("active_theme"):
        prof["theme"] = ss["active_theme"]
    save_profile(user, prof)
    if new and "first_boot" not in new:
        ss["_pulse_ach"] = sorted(new)


def restore_profile_to_session(ss) -> None:
    user = (ss.get("username") or "anon").strip() or "anon"
    prof = load_profile(user)
    if not ss.get("glitches_found"):
        ss["glitches_found"] = list(prof.get("glitches_found") or [])
    ss["achievements"] = list(prof.get("achievements") or [])
    if not ss.get("active_theme"):
        ss["active_theme"] = prof.get("theme") or "default"
    if prof.get("onboarded"):
        ss["onboarded"] = True


def mark_onboarded(ss) -> None:
    user = (ss.get("username") or "anon").strip() or "anon"
    prof = load_profile(user)
    prof["onboarded"] = True
    save_profile(user, prof)
    ss["onboarded"] = True


def export_save(ss) -> str:
    user = (ss.get("username") or "anon").strip() or "anon"
    return json.dumps(load_profile(user), indent=2)


def import_save(ss, raw: str) -> str:
    try:
        data = json.loads(raw)
    except Exception:
        return "invalid"
    user = (ss.get("username") or "anon").strip() or "anon"
    data["user"] = user
    save_profile(user, data)
    restore_profile_to_session(ss)
    return "ok"


def analytics_hit(event: str, user: str = "") -> None:
    try:
        with (_data() / "analytics.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"t": datetime.now(timezone.utc).isoformat(), "e": event, "u": user}) + "\n")
    except Exception:
        pass


def analytics_summary(limit: int = 200) -> dict:
    counts = {}
    try:
        lines = (_data() / "analytics.jsonl").read_text(encoding="utf-8").strip().splitlines()[-limit:]
        for ln in lines:
            try:
                o = json.loads(ln)
                counts[o.get("e") or "?"] = counts.get(o.get("e") or "?", 0) + 1
            except Exception:
                pass
    except Exception:
        pass
    return counts


def daily_seed() -> str:
    seeds = [
        "Search the archive for M-119.",
        "Water Bay-7 in the greenhouse.",
        "Tune the spectrum toward violet.",
        "Leave one line on the anonymous wall.",
        "File a dream journal entry.",
        "Create or join an open online match.",
        "Equip a theme from the shop.",
        "Click the star chart in order.",
    ]
    return seeds[int(date.today().strftime("%Y%m%d")) % len(seeds)]


MOBILE_CSS = """
<style id=\"meridium-mobile\">
@media (max-width: 768px) {
  .stApp [data-testid=\"stHorizontalBlock\"] { flex-wrap: wrap !important; }
  .stButton > button { min-height: 2.6rem; font-size: 1rem !important; }
  .block-container { padding: 0.8rem 0.7rem 5rem !important; max-width: 100% !important; }
  h1 { font-size: 1.45rem !important; }
  h2 { font-size: 1.2rem !important; }
  iframe { max-width: 100% !important; }
}
@media (prefers-reduced-motion: reduce) {
  .stApp::before, .stApp::after, body { animation: none !important; }
}
</style>
"""

PWA_HTML = """
<meta name=\"apple-mobile-web-app-capable\" content=\"yes\" />
<meta name=\"apple-mobile-web-app-status-bar-style\" content=\"black-translucent\" />
<meta name=\"theme-color\" content=\"#7c3aed\" />
"""


def apply_polish(code: str) -> str:
    if "meridium_polish_applied" in code and "theme_atelier_drift_btn" in code:
        return code

    boot = (
        "\n# meridium_polish_applied\n"
        "try:\n"
        "    from meridium_polish import restore_profile_to_session, analytics_hit, MOBILE_CSS, PWA_HTML\n"
        "    from meridium_themes import apply_theme_to_app, get_user_theme\n"
        "    restore_profile_to_session(st.session_state)\n"
        "    _uid = (st.session_state.get(\"username\") or \"anon\")\n"
        "    _th = st.session_state.get(\"active_theme\") or get_user_theme(_uid)\n"
        "    st.session_state.active_theme = _th\n"
        "    st.markdown(MOBILE_CSS + PWA_HTML, unsafe_allow_html=True)\n"
        "    apply_theme_to_app(st, _th)\n"
        "    analytics_hit(\"boot\", _uid)\n"
        "except Exception:\n"
        "    pass\n"
    )
    if "meridium_polish_applied" not in code:
        placed = False
        idx = code.find("st.set_page_config(")
        if idx >= 0:
            depth = 0
            i = idx + len("st.set_page_config")
            while i < len(code):
                ch = code[i]
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        j = i + 1
                        if j < len(code) and code[j] == "\n":
                            j += 1
                        code = code[:j] + boot + code[j:]
                        placed = True
                        break
                i += 1
        if not placed:
            code = boot + code

    home_extra = (
        "\n    # polish home\n"
        "    try:\n"
        "        from meridium_polish import (\n"
        "            sync_session_to_profile, mark_onboarded, daily_seed, export_save, import_save, ACHIEVEMENTS,\n"
        "        )\n"
        "        from meridium_themes import render_theme_shop\n"
        "        sync_session_to_profile(st.session_state)\n"
        "        if not st.session_state.get(\"onboarded\"):\n"
        "            with st.expander(\"Welcome to Meridium\", expanded=True):\n"
        "                st.write(\"1) Set a name if you can  \u00b7  2) Secure a lab marker  \u00b7  3) Enter the Complex\")\n"
        "                st.write(\"Chess is optional. The Complex is the other half of the site.\")\n"
        "                if st.button(\"Got it \u2014 enter\", key=\"onboard_ok\"):\n"
        "                    mark_onboarded(st.session_state)\n"
        "                    st.rerun()\n"
        "        st.caption(\"Daily seed \u00b7 \" + daily_seed())\n"
        "        if st.session_state.get(\"_pulse_ach\"):\n"
        "            for _a in st.session_state.pop(\"_pulse_ach\", []):\n"
        "                _meta = ACHIEVEMENTS.get(_a, {})\n"
        "                st.toast(\"Achievement: \" + str(_meta.get(\"name\") or _a), icon=\"\u2728\")\n"
        "                st.success(\"Achievement unlocked: \" + str(_meta.get(\"name\") or _a))\n"
        "        with st.expander(\"Achievements\", expanded=False):\n"
        "            _have = set(st.session_state.get(\"achievements\") or [])\n"
        "            for _aid, _am in ACHIEVEMENTS.items():\n"
        "                st.write((\"\u2705 \" if _aid in _have else \"\u2b1c \") + _am[\"name\"] + \" \u2014 \" + _am[\"desc\"])\n"
        "        with st.expander(\"Theme shop\", expanded=False):\n"
        "            render_theme_shop(st, st.session_state)\n"
        "        if st.button(\"\u25c8 Open Theme atelier\", key=\"home_theme_atelier\", use_container_width=True):\n"
        "            st.session_state._themes_from = \"home\"\n"
        "            st.session_state.view = \"themes\"\n"
        "            st.rerun()\n"
        "        with st.expander(\"Save \u00b7 export / import\", expanded=False):\n"
        "            st.code(export_save(st.session_state), language=\"json\")\n"
        "            _imp = st.text_area(\"Paste save JSON\", key=\"save_import_raw\", height=100)\n"
        "            if st.button(\"Import save\", key=\"save_import_btn\"):\n"
        "                _r = import_save(st.session_state, _imp)\n"
        "                st.success(\"Imported\" if _r == \"ok\" else \"Invalid JSON\")\n"
        "                if _r == \"ok\":\n"
        "                    st.rerun()\n"
        "    except Exception:\n"
        "        pass\n"
    )
    if "Open Theme atelier" not in code and "Theme shop" not in code:
        for m in ['if st.session_state.view == "home":', "if st.session_state.view == 'home':"]:
            if m in code:
                code = code.replace(m, m + home_extra, 1)
                break
    elif "home_theme_atelier" not in code:
        for m in ['if st.session_state.view == "home":', "if st.session_state.view == 'home':"]:
            if m in code:
                extra_btn = (
                    "\n    if st.button(\"\u25c8 Open Theme atelier\", key=\"home_theme_atelier\", use_container_width=True):\n"
                    "        st.session_state._themes_from = \"home\"\n"
                    "        st.session_state.view = \"themes\"\n"
                    "        st.rerun()\n"
                )
                code = code.replace(m, m + extra_btn, 1)
                break

    try:
        from meridium_themes import apply_theme_shop_routes
        code = apply_theme_shop_routes(code)
    except Exception:
        pass
    return code
