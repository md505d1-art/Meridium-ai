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
    av = _PORTRAITS.get(key)
    if av:
        return av
    try:
        from pathlib import Path
        p = Path(__file__).resolve().parent / "coaches" / f"{key}.b64"
        if p.exists():
            raw = p.read_text(encoding="utf-8").strip()
            if raw.startswith("data:"):
                return raw
            return "data:image/png;base64," + raw
    except Exception:
        pass
    return None


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
    """Replace TALKS + force coach portrait/name so Soju never sticks."""
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

    if nm != "Soju":
        av = _load_avatar(nm)
        if not av:
            label = nm.split()[0][:8].upper()
            av = (
                "data:image/svg+xml;utf8,"
                + "%3Csvg xmlns='http://www.w3.org/2000/svg' width='256' height='256'%3E"
                + "%3Crect width='256' height='256' rx='40' fill='%231e1b4b'/%3E"
                + f"%3Ctext x='128' y='140' text-anchor='middle' fill='white' font-size='28' font-family='sans-serif'%3E{label}%3C/text%3E"
                + "%3C/svg%3E"
            )

        av_js = json.dumps(av)
        name_js = json.dumps(nm + " · coach")
        tag_js = json.dumps(c.get("tagline") or "")

        if "const SOJU = {" in html:
            s = html.find("const SOJU = {")
            j = html.find("};", s)
            if j > 0:
                new_soju = (
                    "const SOJU = {\n"
                    f"    idle: {av_js},\n"
                    f"    happy: {av_js},\n"
                    f"    shock: {av_js},\n"
                    f"    think: {av_js}\n"
                    "  };"
                )
                html = html[:s] + new_soju + html[j + 2 :]

        html = re.sub(
            r'(id=["\']sojuImg["\'][^>]*src=["\'])[^"\']*(["\'])',
            lambda m: m.group(1) + av + m.group(2),
            html,
            count=1,
        )
        html = re.sub(
            r'(src=["\'])[^"\']*(["\'][^>]*id=["\']sojuImg["\'])',
            lambda m: m.group(1) + av + m.group(2),
            html,
            count=1,
        )

        html = html.replace("Soju · board cat", f"{nm} · coach")
        html = html.replace("Hint from Soju:", f"Hint from {nm}:")
        html = html.replace('alt="Soju"', f'alt="{nm}"')

        force_js = (
            "\n<script>(function(){\n"
            f"  var AV={av_js};\n"
            f"  var NM={name_js};\n"
            f"  var TG={tag_js};\n"
            "  function apply(){\n"
            "    try{\n"
            "      if(typeof SOJU!=='undefined'){ SOJU.idle=SOJU.happy=SOJU.shock=SOJU.think=AV; }\n"
            "      var img=document.getElementById('sojuImg');\n"
            "      if(img){ img.src=AV; img.alt=NM; }\n"
            "      var nameEl=document.querySelector('.soju .name');\n"
            "      if(nameEl){ nameEl.textContent=NM; }\n"
            "      var talk=document.getElementById('sojuTalk');\n"
            "      if(talk && TG){ talk.textContent=TG; }\n"
            "    }catch(e){}\n"
            "  }\n"
            "  apply();\n"
            "  setTimeout(apply, 30);\n"
            "  setTimeout(apply, 150);\n"
            "})();</script>\n"
        )
        if "</body>" in html:
            html = html.replace("</body>", force_js + "</body>", 1)
        else:
            html = html + force_js

    # Always inject SFX (Soju and other coaches)
    try:
        from chess_patches import apply_sfx_to_chess_html
        html = apply_sfx_to_chess_html(html)
    except Exception:
        pass
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
        "\n        # Coach personality + portrait (must run after Soju b64 inject)\n"
        "        try:\n"
        "            html = _mer_apply_coach_html(html, st.session_state.get(\"chess_coach\", \"Soju\"))\n"
        "        except Exception:\n"
        "            pass\n"
        "        try:\n"
        "            html = html + (\"<!-- coach:\" + str(st.session_state.get(\"chess_coach\", \"Soju\"))"
        " + \":\" + str(st.session_state.get(\"chess_opponent\", \"x\")) + \" -->\")\n"
        "        except Exception:\n"
        "            pass\n"
    )
    if "html = _mer_apply_coach_html(" not in code:
        for marker in [
            'html = html.replace("__SOJU_THINK__", _b64img("soju_think.jpg"))',
            "html = html.replace('__SOJU_THINK__', _b64img('soju_think.jpg'))",
        ]:
            if marker in code:
                code = code.replace(marker, marker + call, 1)
                break

    bad = (
        'st.components.v1.html(_chess_widget_html(), height=860, scrolling=True, '
        'key="chess_board_" + str(st.session_state.get("chess_coach","Soju")) + "_" + str(st.session_state.get("chess_opponent","x")) + "_" + str(nonce))'
    )
    good = 'st.components.v1.html(_chess_widget_html(), height=860, scrolling=True)'
    if bad in code:
        code = code.replace(bad, good, 1)

    return code
