"""Custom coaches + AI opponents with SVG avatars and iconic lines."""
from __future__ import annotations
import json
import base64 as _b64

_COACHES = {
    "Soju": {"title": "Soju · Resident Cat Coach", "tagline": "I'll sit here. You play. I'll judge.", "talks": None},
    "Gotham Chess": {
        "title": "Gotham Chess · Levy", "tagline": "THE ROOOOOOOOOOOOOOOOOOOOOK",
        "avatar_letter": "G", "avatar_bg": "#1e1b4b", "avatar_accent": "#a78bfa",
        "talks": {
            "Brilliant": ["THAT is how you play chess. Absolute cinema.", "THE ROOOOOOOOOOOOOOOOOOOOOK goes crazy here.", "I would make a whole video about this move."],
            "Great": ["Great move. This is the line I showed in the course.", "Clean. Simple. Effective.", "You actually calculated. Proud of you."],
            "Best": ["Best move. Engine agrees.", "That's the one. Don't overthink it.", "Textbook."],
            "Excellent": ["Excellent. You're learning.", "Solid improvement.", "That's the spirit."],
            "Good": ["Good. Playable.", "Good move. Now find the follow-up.", "Acceptable."],
            "Okay": ["Okay... could be better.", "It's fine. Not great, not terrible.", "Meh."],
            "Inaccuracy": ["Inaccuracy. You hung a little something.", "Slight inaccuracy.", "Not ideal."],
            "Mistake": ["Mistake. That was not the plan.", "You just gave them free stuff. Why?", "Pause. Think. Then move."],
            "Miss": ["MISS. The tactic was right there!", "You had mate in two and walked past it.", "I cannot believe you missed that."],
            "Blunder": ["BLUNDER. Absolute disaster.", "That piece was not a free gift.", "We need to talk about your calculation."],
        },
    },
    "Hikaru": {
        "title": "Hikaru · Speed Demon", "tagline": "Chat, is this real?",
        "avatar_letter": "H", "avatar_bg": "#0f172a", "avatar_accent": "#38bdf8",
        "talks": {
            "Brilliant": ["Chat is this real?? That was actually crazy.", "Okay that was clean. GG."],
            "Great": ["Great move. Speedrun any% vibes.", "Yeah that's the one."],
            "Best": ["Best. Obviously.", "Engine move. Nice."],
            "Excellent": ["Excellent. Keep it up.", "Solid."],
            "Good": ["Good enough.", "Playable."],
            "Okay": ["Okay I guess.", "Could be better chat."],
            "Inaccuracy": ["Slight inaccuracy.", "Not ideal."],
            "Mistake": ["Mistake. Come on.", "That was free."],
            "Miss": ["You missed it chat...", "The tactic was screaming."],
            "Blunder": ["BLUNDER. Chat went silent.", "That was painful."],
        },
    },
    "Magnus": {
        "title": "Magnus · Endgame God", "tagline": "I don't even try that hard.",
        "avatar_letter": "M", "avatar_bg": "#111827", "avatar_accent": "#fbbf24",
        "talks": {
            "Brilliant": ["Very nice. I might have played the same.", "Beautiful. Simple and strong."],
            "Great": ["Great. Practical and strong.", "Yes. That works."],
            "Best": ["Best. Of course.", "Correct."],
            "Excellent": ["Excellent technique.", "Clean."],
            "Good": ["Good enough.", "Playable."],
            "Okay": ["It's okay.", "A bit passive."],
            "Inaccuracy": ["Inaccuracy. Not the most precise.", "Slightly inaccurate."],
            "Mistake": ["Mistake. Now it is harder.", "That was unnecessary."],
            "Miss": ["You missed a chance.", "There was more."],
            "Blunder": ["Blunder. That loses.", "Hard to recover from this."],
        },
    },
    "Anna Cramling": {
        "title": "Anna · Positive Energy", "tagline": "You got this!!",
        "avatar_letter": "A", "avatar_bg": "#4c1d95", "avatar_accent": "#f9a8d4",
        "talks": {
            "Brilliant": ["OMG that was BRILLIANT!!", "I love this move so much!!"],
            "Great": ["Great job!! Keep going!!", "Yes!! That's it!!"],
            "Best": ["Best move!! Perfect!!", "Love it!!"],
            "Excellent": ["Excellent!! You're improving!!", "So clean!!"],
            "Good": ["Good!! Solid!!", "Keep it up!!"],
            "Okay": ["It's okay!! We learn!!", "Next one will be better!!"],
            "Inaccuracy": ["Small inaccuracy, no worries!!", "We can recover!!"],
            "Mistake": ["Mistake but it's okay!! Learn from it!!", "Don't tilt!!"],
            "Miss": ["Aww you missed it!! Next time!!", "Stay positive!!"],
            "Blunder": ["Blunder... but we keep going!!", "You'll bounce back!!"],
        },
    },
    "Botez": {
        "title": "Botez · Chaotic Fun", "tagline": "Botez gambit incoming?",
        "avatar_letter": "B", "avatar_bg": "#831843", "avatar_accent": "#fb7185",
        "talks": {
            "Brilliant": ["NO WAY that was actually brilliant.", "Okay chat that was clean."],
            "Great": ["Great move ngl.", "Yes!!"],
            "Best": ["Best. Obviously.", "Correct."],
            "Excellent": ["Excellent.", "Solid."],
            "Good": ["Good.", "Playable."],
            "Okay": ["Okay...", "Could be better."],
            "Inaccuracy": ["Inaccuracy. Classic.", "Slightly off."],
            "Mistake": ["Mistake. We love a blunder arc.", "That was free."],
            "Miss": ["You missed it!!", "The tactic was right there."],
            "Blunder": ["BLUNDER. Content.", "That was painful."],
        },
    },
    "Fabi": {
        "title": "Fabiano · Precision", "tagline": "Calculate everything.",
        "avatar_letter": "F", "avatar_bg": "#1e3a5f", "avatar_accent": "#93c5fd",
        "talks": {
            "Brilliant": ["Brilliant calculation.", "Very deep. Impressive."],
            "Great": ["Great. Precise.", "Strong practical choice."],
            "Best": ["Best. The only move.", "Correct."],
            "Excellent": ["Excellent technique.", "Clean."],
            "Good": ["Good.", "Solid."],
            "Okay": ["Okay. A bit imprecise.", "Could be sharper."],
            "Inaccuracy": ["Inaccuracy. Not the most accurate.", "Slight error."],
            "Mistake": ["Mistake. Now the evaluation shifts.", "Calculate deeper."],
            "Miss": ["You missed a strong continuation.", "Look for tactics."],
            "Blunder": ["Blunder. Hard to justify.", "That loses material."],
        },
    },
    "Naroditsky": {
        "title": "Danya · Clear Explanation", "tagline": "Let's break this down.",
        "avatar_letter": "D", "avatar_bg": "#164e63", "avatar_accent": "#67e8f9",
        "talks": {
            "Brilliant": ["Brilliant. Let me explain why this works...", "Superb calculation."],
            "Great": ["Great practical move.", "Very instructive."],
            "Best": ["Best. Textbook.", "Correct approach."],
            "Excellent": ["Excellent.", "Solid understanding."],
            "Good": ["Good.", "Playable."],
            "Okay": ["Okay. A bit passive.", "Think about the plan."],
            "Inaccuracy": ["Inaccuracy. The idea is almost right.", "Close."],
            "Mistake": ["Mistake. Let's see the issue...", "Careful."],
            "Miss": ["Missed opportunity. The tactic was there.", "Next time."],
            "Blunder": ["Blunder. Fundamental error.", "Learn from it."],
        },
    },
    "Eric Rosen": {
        "title": "Eric Rosen · Imaginative", "tagline": "Hello everyone!",
        "avatar_letter": "E", "avatar_bg": "#3f1d0b", "avatar_accent": "#fdba74",
        "talks": {
            "Brilliant": ["Hello everyone! That was a brilliant idea.", "Creative and strong."],
            "Great": ["Great practical decision.", "Nice find."],
            "Best": ["Best. Clean.", "Correct."],
            "Excellent": ["Excellent.", "Nice."],
            "Good": ["Good.", "Playable."],
            "Okay": ["Okay.", "Could be more creative."],
            "Inaccuracy": ["Slight inaccuracy.", "Not the most precise."],
            "Mistake": ["Mistake. Let's reset.", "Careful."],
            "Miss": ["Missed a fun idea there.", "Next time."],
            "Blunder": ["Blunder. Ouch.", "We move on."],
        },
    },
}

_OPPONENTS = {
    "Beginner Bot": {"depth": 1, "desc": "Simple moves. Perfect for learning."},
    "Club Player": {"depth": 2, "desc": "Solid club level. Punishes obvious mistakes."},
    "Strong Club": {"depth": 3, "desc": "Sharp and opportunistic."},
    "Master Bot": {"depth": 4, "desc": "Deep calculation. Ruthless."},
    "GothamBot": {"depth": 3, "desc": "Plays like a coach who wants you to improve."},
    "Hikaru Speed": {"depth": 2, "desc": "Quick, tricky, and annoying."},
    "Magnus Endgame": {"depth": 4, "desc": "Converts the tiniest advantages."},
    "Chaos Bot": {"depth": 2, "desc": "Unpredictable and fun."},
}

def apply_coach(code: str) -> str:
    inject_ui = (
        "\n    # === Meridium coaches + AI opponents ===\n"
        "    _MER_COACHES = " + repr(_COACHES) + "\n"
        "    _MER_OPPONENTS = " + repr(_OPPONENTS) + "\n"
        "    if \"chess_coach\" not in st.session_state:\n"
        "        st.session_state.chess_coach = \"Soju\"\n"
        "    if \"chess_opponent\" not in st.session_state:\n"
        "        st.session_state.chess_opponent = \"Club Player\"\n"
        "    _cc1, _cc2 = st.columns(2)\n"
        "    with _cc1:\n"
        "        st.session_state.chess_coach = st.selectbox(\n"
        "            \"Coach\", list(_MER_COACHES.keys()),\n"
        "            index=list(_MER_COACHES.keys()).index(st.session_state.chess_coach) if st.session_state.chess_coach in _MER_COACHES else 0,\n"
        "            key=\"mer_sel_coach\",\n"
        "        )\n"
        "    with _cc2:\n"
        "        st.session_state.chess_opponent = st.selectbox(\n"
        "            \"AI Opponent\", list(_MER_OPPONENTS.keys()),\n"
        "            index=list(_MER_OPPONENTS.keys()).index(st.session_state.chess_opponent) if st.session_state.chess_opponent in _MER_OPPONENTS else 1,\n"
        "            key=\"mer_sel_opp\",\n"
        "        )\n"
        "    _coach = _MER_COACHES[st.session_state.chess_coach]\n"
        "    _opp = _MER_OPPONENTS[st.session_state.chess_opponent]\n"
        "    st.caption(_coach[\"title\"] + \"  ·  \" + _coach.get(\"tagline\", \"\"))\n"
        "    st.caption(\"vs \" + st.session_state.chess_opponent + \" (depth \" + str(_opp[\"depth\"]) + \") — \" + _opp[\"desc\"])\n"
    )
    placed = False
    for marker in [
        'color = st.selectbox("You play", ["White", "Black"], key="chess_color_ui")',
        "color = st.selectbox('You play', ['White', 'Black'], key='chess_color_ui')",
        'if st.session_state.view == "chess":',
    ]:
        if marker in code and "mer_sel_coach" not in code:
            code = code.replace(marker, marker + inject_ui, 1)
            placed = True
            break
    if not placed and "mer_sel_coach" not in code and "Residual board" in code:
        code = code.replace("Residual board", "Residual board" + inject_ui, 1)
    code = code.replace(
        'depth = {"Soft": 1, "Steady": 2, "Sharp": 2, "Relentless": 3}.get(level, 2)',
        'depth = {"Soft": 1, "Steady": 2, "Sharp": 2, "Relentless": 3}.get(level, 2)\n'
        '    try:\n'
        '        depth = int(_opp.get("depth", depth))\n'
        '    except Exception:\n'
        '        pass',
        1,
    )
    personality = (
        "\n        # Coach personality + avatar override\n"
        "        try:\n"
        "            _c = _MER_COACHES.get(st.session_state.get(\"chess_coach\", \"Soju\"), {})\n"
        "            if _c.get(\"talks\"):\n"
        "                import json as _json\n"
        "                _talks_js = \"const TALKS = \" + _json.dumps(_c[\"talks\"]) + \";\"\n"
        "                if \"const TALKS = {\" in html:\n"
        "                    html = html.replace(\"const TALKS = {\", _talks_js + \" /*orig*/ const TALKS = {\", 1)\n"
        "            if st.session_state.get(\"chess_coach\", \"Soju\") != \"Soju\":\n"
        "                _letter = _c.get(\"avatar_letter\", \"C\")\n"
        "                _bg = _c.get(\"avatar_bg\", \"#1a1224\")\n"
        "                _ac = _c.get(\"avatar_accent\", \"#c4a7e7\")\n"
        "                _svg = (\n"
        "                    '<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"128\" height=\"128\" viewBox=\"0 0 128 128\">'\n"
        "                    f'<rect width=\"128\" height=\"128\" rx=\"28\" fill=\"{_bg}\"/>'\n"
        "                    f'<circle cx=\"64\" cy=\"48\" r=\"28\" fill=\"{_ac}\" opacity=\"0.85\"/>'\n"
        "                    f'<circle cx=\"64\" cy=\"48\" r=\"20\" fill=\"#0f0a18\"/>'\n"
        "                    f'<text x=\"64\" y=\"56\" text-anchor=\"middle\" font-family=\"system-ui,sans-serif\" font-size=\"26\" font-weight=\"700\" fill=\"{_ac}\">{_letter}</text>'\n"
        "                    f'<rect x=\"30\" y=\"84\" width=\"68\" height=\"32\" rx=\"16\" fill=\"{_ac}\" opacity=\"0.3\"/>'\n"
        "                    \"</svg>\"\n"
        "                )\n"
        "                import base64 as _b64m\n"
        "                _av = \"data:image/svg+xml;base64,\" + _b64m.b64encode(_svg.encode()).decode()\n"
        "                for _key in (\"__SOJU_IDLE__\", \"__SOJU_HAPPY__\", \"__SOJU_SHOCK__\", \"__SOJU_THINK__\"):\n"
        "                    html = html.replace(_key, _av)\n"
        "                _nm = st.session_state.get(\"chess_coach\", \"Soju\")\n"
        "                html = html.replace(\">Soju<\", f\">{_nm}<\")\n"
        "                html = html.replace(\"Soju ·\", _nm + \" ·\")\n"
        "        except Exception:\n"
        "            pass\n"
    )
    for marker in [
        'html = html.replace("__SOJU_THINK__", _b64img("soju_think.jpg"))',
        "html = html.replace('__SOJU_THINK__', _b64img('soju_think.jpg'))",
    ]:
        if marker in code and "Coach personality" not in code:
            code = code.replace(marker, marker + personality, 1)
            break
    return code
