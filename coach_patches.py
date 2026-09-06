"""Custom coaches + AI opponents with illustrated portraits and iconic lines."""
from __future__ import annotations
import json
import re

try:
    from coaches_portraits import PORTRAITS as _PORTRAITS
except Exception:
    _PORTRAITS = {}

_FILE_MAP = {
    "Gotham Chess": "gotham",
    "Hikaru": "hikaru",
    "Magnus": "magnus",
    "Anna Cramling": "anna",
    "Botez": "botez",
    "Fabi": "fabi",
    "Naroditsky": "danya",
    "Eric Rosen": "eric",
}


def _load_avatar(name: str):
    key = _FILE_MAP.get(name)
    if not key:
        return None
    return _PORTRAITS.get(key)


_COACHES = {
    "Soju": {"title": "Soju · Resident Cat Coach", "tagline": "I'll sit here. You play. I'll judge.", "avatar": None, "talks": None},
    "Gotham Chess": {
        "title": "Gotham Chess · Levy", "tagline": "THE ROOOOOOOOOOOOOOOOOOOOOK", "avatar": "Gotham Chess",
        "talks": {
            "Brilliant": ["THAT is how you play chess. Absolute cinema.", "THE ROOOOOOOOOOOOOOOOOOOOOK goes crazy here."],
            "Great": ["Great move. This is the line I showed in the course.", "Clean. Simple. Effective."],
            "Best": ["Best move. Engine agrees.", "That's the one. Don't overthink it."],
            "Excellent": ["Excellent. You're learning.", "Solid improvement."],
            "Good": ["Good. Playable.", "Good move. Now find the follow-up."],
            "Okay": ["Okay... could be better.", "It's fine. Not great, not terrible."],
            "Inaccuracy": ["Inaccuracy. You hung a little something.", "Slight inaccuracy."],
            "Mistake": ["Mistake. That was not the plan.", "You just gave them free stuff. Why?"],
            "Miss": ["MISS. The tactic was right there!", "You had mate in two and walked past it."],
            "Blunder": ["BLUNDER. Absolute disaster.", "That piece was not a free gift."],
        },
    },
    "Hikaru": {
        "title": "Hikaru · Speed Demon", "tagline": "Chat, is this real?", "avatar": "Hikaru",
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
        "title": "Magnus · Endgame God", "tagline": "I don't even try that hard.", "avatar": "Magnus",
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
        "title": "Anna · Positive Energy", "tagline": "You got this!!", "avatar": "Anna Cramling",
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
        "title": "Botez · Chaotic Fun", "tagline": "Botez gambit incoming?", "avatar": "Botez",
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
        "title": "Fabiano · Precision", "tagline": "Calculate everything.", "avatar": "Fabi",
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
        "title": "Danya · Clear Explanation", "tagline": "Let's break this down.", "avatar": "Naroditsky",
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
        "title": "Eric Rosen · Imaginative", "tagline": "Hello everyone!", "avatar": "Eric Rosen",
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


def apply_coach_to_html(html: str, coach_name: str) -> str:
    c = _COACHES.get(coach_name) or _COACHES["Soju"]
    nm = coach_name or "Soju"
    if c.get("talks") and "const TALKS = {" in html:
        start = html.find("const TALKS = {")
        if start >= 0:
            i = start + len("const TALKS = {")
            depth = 1
            while i < len(html) and depth:
                if html[i] == "{":
                    depth += 1
                elif html[i] == "}":
                    depth -= 1
                i += 1
            if i < len(html) and html[i] == ";":
                i += 1
            html = html[:start] + ("const TALKS = " + json.dumps(c["talks"]) + ";") + html[i:]
    av = _load_avatar(nm) if nm != "Soju" else None
    if nm != "Soju" and av:
        av_js = json.dumps(av)
        name_js = json.dumps(nm + " · coach")
        patch = (
            "\n  SOJU.idle = SOJU.happy = SOJU.shock = SOJU.think = "
            + av_js
            + ";\n  try { sojuImg.src = SOJU.idle; } catch(e){}"
            + "\n  try { document.querySelector('.soju .name').textContent = "
            + name_js
            + "; } catch(e){}\n"
        )
        if "const SOJU = {" in html and "SOJU.idle = SOJU.happy" not in html:
            s = html.find("const SOJU = {")
            j = html.find("};", s)
            if j > 0:
                html = html[: j + 2] + patch + html[j + 2 :]
        html = re.sub(r'(id="sojuImg"[^>]*src=")[^"]*(")', r"\1" + av + r"\2", html, count=1)
        html = html.replace(">Soju · board cat<", f"{nm} · coach<", 1)
        html = html.replace("Hint from Soju:", f"Hint from {nm}:")
    return html


def apply_coach(code: str) -> str:
    inject_ui = (
        "\n    # === Meridium coaches + AI opponents ===\n"
        "    from coach_patches import _COACHES as _MER_COACHES, _OPPONENTS as _MER_OPPONENTS, apply_coach_to_html as _mer_apply_coach_html\n"
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
    if "mer_sel_coach" not in code:
        for marker in [
            'color = st.selectbox("You play", ["White", "Black"], key="chess_color_ui")',
            "color = st.selectbox('You play', ['White', 'Black'], key='chess_color_ui')",
            'if st.session_state.view == "chess":',
        ]:
            if marker in code:
                code = code.replace(marker, marker + inject_ui, 1)
                break
    old_depth = 'depth = {"Soft": 1, "Steady": 2, "Sharp": 2, "Relentless": 3}.get(level, 2)'
    new_depth = old_depth + "\n    try:\n        depth = int(_opp.get(\"depth\", depth))\n    except Exception:\n        pass"
    if old_depth in code and "depth = int(_opp.get" not in code:
        code = code.replace(old_depth, new_depth, 1)
    call = (
        "\n        # Coach personality + portrait\n"
        "        try:\n"
        "            html = _mer_apply_coach_html(html, st.session_state.get(\"chess_coach\", \"Soju\"))\n"
        "        except Exception:\n"
        "            pass\n"
    )
    for marker in [
        'html = html.replace("__SOJU_THINK__", _b64img("soju_think.jpg"))',
        "html = html.replace('__SOJU_THINK__', _b64img('soju_think.jpg'))",
    ]:
        if marker in code and "_mer_apply_coach_html" not in code:
            code = code.replace(marker, marker + call, 1)
            break
    return code
