"""Chess coaches: Soju, Gotham Chess, Hikaru, Magnus."""
from __future__ import annotations
import json, re

_COACHES = {
    "Soju": {"title": "Soju · board cat", "init": "SJ", "bg": "#7c3aed", "talks": None},
    "Gotham Chess": {
        "title": "Gotham Chess · coach", "init": "GC", "bg": "#5b21b6",
        "talks": {
            "Brilliant": ["THAT is a brilliant. Absolute cinema."],
            "Great": ["Great move — only move that holds."],
            "Best": ["Engine move. That's the one."],
            "Excellent": ["Excellent. You're learning."],
            "Good": ["Good move. Playable."],
            "Okay": ["Okay. A bit passive, but fine."],
            "Inaccuracy": ["Inaccuracy. You had better."],
            "Mistake": ["That's a mistake. Don't do that again."],
            "Miss": ["You missed the tactic! Look at the knight."],
            "Blunder": ["BLUNDER. Why would you play that?"],
        },
    },
    "Hikaru": {
        "title": "Hikaru · speed demon", "init": "HN", "bg": "#0e7490",
        "talks": {
            "Brilliant": ["Oh my god, that is SO good."],
            "Great": ["Yeah that's the only move. Easy."],
            "Best": ["Best move. Obviously."],
            "Excellent": ["Excellent. Super clean."],
            "Good": ["Good. I like that."],
            "Okay": ["It's okay I guess."],
            "Inaccuracy": ["Slightly inaccurate. Hmm."],
            "Mistake": ["Uh, that's a mistake."],
            "Miss": ["You completely missed that!"],
            "Blunder": ["What was THAT? Instant blunder."],
        },
    },
    "Magnus": {
        "title": "Magnus · world class", "init": "MC", "bg": "#1e3a5f",
        "talks": {
            "Brilliant": ["Very nice. Creative and correct."],
            "Great": ["The only move. Well calculated."],
            "Best": ["Best. Simple and strong."],
            "Excellent": ["Excellent technique."],
            "Good": ["Good enough."],
            "Okay": ["Acceptable, not more."],
            "Inaccuracy": ["Slightly inaccurate."],
            "Mistake": ["A clear mistake."],
            "Miss": ["You missed something important."],
            "Blunder": ["A serious blunder."],
        },
    },
}

def _avatar(init: str, bg: str) -> str:
    import base64
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128">'
        f'<rect width="128" height="128" rx="28" fill="{bg}"/>'
        f'<text x="64" y="76" text-anchor="middle" font-family="system-ui,sans-serif"'
        f' font-size="42" font-weight="700" fill="#f8fafc">{init}</text></svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

def apply_coach_to_html(html: str, coach_name: str) -> str:
    ci = _COACHES.get(coach_name) or _COACHES["Soju"]
    html = html.replace("Soju · board cat", ci["title"])
    if not ci.get("talks"):
        return html
    talks_js = "const TALKS = " + json.dumps(ci["talks"]) + ";"
    html = re.sub(r"const TALKS = \{[\s\S]*?\};", talks_js, html, count=1)
    av = _avatar(ci["init"], ci["bg"])
    for ph in ("__SOJU_IDLE__", "__SOJU_HAPPY__", "__SOJU_SHOCK__", "__SOJU_THINK__"):
        html = html.replace(ph, av)
    soju_js = "const SOJU = { idle: %s, happy: %s, shock: %s, think: %s };" % (
        json.dumps(av), json.dumps(av), json.dumps(av), json.dumps(av)
    )
    html = re.sub(r"const SOJU = \{[\s\S]*?\};", soju_js, html, count=1)
    return html

def apply_coach(code: str) -> str:
    code = code.replace(
        'color = st.selectbox("You play", ["White", "Black"], key="chess_color_ui")',
        'color = st.selectbox("You play", ["White", "Black"], key="chess_color_ui")\n'
        '    coach = st.selectbox("Coach", ["Soju", "Gotham Chess", "Hikaru", "Magnus"], key="chess_coach_ui")',
        1,
    )
    if "apply_coach_to_html" not in code:
        code = code.replace(
            "\n        return html\n",
            "\n"
            "        try:\n"
            "            _cn = coach\n"
            "        except NameError:\n"
            '            _cn = st.session_state.get("chess_coach_ui") or "Soju"\n'
            "        try:\n"
            "            from coach_patches import apply_coach_to_html\n"
            "            html = apply_coach_to_html(html, _cn)\n"
            "        except Exception:\n"
            "            pass\n"
            "        return html\n",
            1,
        )
    code = code.replace(
        "Click a piece, then a square. Soju grades every move",
        "Click a piece, then a square. Your coach grades every move",
        1,
    )
    return code
