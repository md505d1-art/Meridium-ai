"""Custom coaches + AI opponents with SVG avatars and iconic lines."""
from __future__ import annotations
import json
import base64 as _b64

_COACHES = {
    "Soju": {
        "title": "Soju · Resident Cat Coach",
        "tagline": "I'll sit here. You play. I'll judge.",
        "talks": None,
    },
    "Gotham Chess": {
        "title": "Gotham Chess · Levy",
        "tagline": "THE ROOOOOOOOOOOOOOOOOOOOOK",
        "avatar_letter": "G",
        "avatar_bg": "#1e1b4b",
        "avatar_accent": "#a78bfa",
        "talks": {
            "Brilliant": ["THAT is how you play chess. Absolute cinema.", "THE ROOOOOOOOOOOOOOOOOOOOOK goes crazy here.", "I would make a whole video about this move."],
            "Great": ["Great move. This is the line I showed in the course.", "Clean. Simple. Effective. Like a Gotham thumbnail.", "You actually calculated. Proud of you."],
            "Best": ["Best move. Engine agrees. I agree. Everyone agrees.", "That's the one. Don't overthink it.", "Textbook. Write it down."],
            "Excellent": ["Excellent. You're learning.", "Solid improvement. Keep going.", "That's the spirit."],
            "Good": ["Good. Playable. Not a masterpiece though.", "Good move. Now find the follow-up.", "Acceptable. We can work with this."],
            "Okay": ["Okay... could be better.", "It's fine. Not great, not terrible.", "Meh. Next time look a bit deeper."],
            "Inaccuracy": ["Inaccuracy. You hung a little something.", "Slight inaccuracy. The position is still okay.", "Not ideal. Try again next time."],
            "Mistake": ["Mistake. That was not the plan.", "You just gave them free stuff. Why?", "Mistake. Pause. Think. Then move."],
            "Miss": ["MISS. The tactic was right there!", "You had mate in two and walked past it.", "I cannot believe you missed that."],
            "Blunder": ["BLUNDER. Absolute disaster.", "That piece was not a free gift.", "We need to talk about your calculation."],
        },
    },
    "Hikaru": {
        "title": "Hikaru · Speed Demon",
        "tagline": "Chat, is this real?",
        "avatar_letter": "H",
        "avatar_bg": "#0f172a",
        "avatar_accent": "#38bdf8",
        "talks": {
            "Brilliant": ["Chat is this real?? That was actually crazy.", "Okay that was clean. GG.", "I'm not even mad. That was good."],
            "Great": ["Great move. Speedrun any% vibes.", "Yeah that's the one.", "Clean calculation."],
            "Best": ["Best. Obviously.", "Engine move. Nice.", "That's just correct chess."],
            "Excellent": ["Excellent. Keep it up.", "Solid.", "Good pace."],
            "Good": ["Good enough.", "Playable.", "Fine."],
            "Okay": ["Okay I guess.", "Could be better chat.", "Meh."],
            "Inaccuracy": ["Slight inaccuracy.", "Not ideal.", "You leaked a bit."],
            "Mistake": ["Mistake. Come on.", "That was free.", "Why would you do that?"],
            "Miss": ["You missed it chat...", "The tactic was screaming.", "Oof."],
            "Blunder": ["BLUNDER. Chat went silent.", "That was painful.", "Uninstall vibes."],
        },
    },
    "Magnus": {
        "title": "Magnus · Endgame God",
        "tagline": "I don't even try that hard.",
        "avatar_letter": "M",
        "avatar_bg": "#111827",
        "avatar_accent": "#fbbf24",
        "talks": {
            "Brilliant": ["Very nice. I might have played the same.", "Beautiful. Simple and strong.", "This is how you punish."],
            "Great": ["Great. Practical and strong.", "Yes. That works.", "Good decision."],
            "Best": ["Best. Of course.", "Correct.", "Natural."],
            "Excellent": ["Excellent technique.", "Clean.", "Good."],
            "Good": ["Good enough.", "Playable.", "Fine."],
            "Okay": ["It's okay.", "A bit passive.", "Could be more precise."],
            "Inaccuracy": ["Inaccuracy. Not the most precise.", "Slightly inaccurate.", "You can do better."],
            "Mistake": ["Mistake. Now it is harder.", "That was unnecessary.", "Careful."],
            "Miss": ["You missed a chance.", "There was more.", "Look again next time."],
            "Blunder": ["Blunder. That loses.", "Unfortunately that is losing.", "Hard to recover from this."],
        },
    },
    "Anna Cramling": {
        "title": "Anna · Positive Energy",
        "tagline": "You got this!!",
        "avatar_letter": "A",
        "avatar_bg": "#4c1d95",
        "avatar_accent": "#f9a8d4",
        "talks": {
            "Brilliant": ["OMG that was BRILLIANT!!", "I love this move so much!!", "You're so good!!"],
            "Great": ["Great job!! Keep going!!", "Yes!! That's it!!", "Amazing!!"],
            "Best": ["Best move!! Perfect!!", "Exactly!!", "Love it!!"],
            "Excellent": ["Excellent!! You're improving!!", "So clean!!", "Nice!!"],
            "Good": ["Good!! Solid!!", "Nice one!!", "Keep it up!!"],
            "Okay": ["It's okay!! We learn!!", "Not bad!!", "Next one will be better!!"],
            "Inaccuracy": ["Small inaccuracy, no worries!!", "It's fine, keep fighting!!", "We can recover!!"],
            "Mistake": ["Mistake but it's okay!! Learn from it!!", "Don't tilt!!", "You got this!!"],
            "Miss": ["Aww you missed it!! Next time!!", "It happens!!", "Stay positive!!"],
            "Blunder": ["Blunder... but we keep going!!", "It's just a game!!", "You'll bounce back!!"],
        },
    },
    "Botez": {
        "title": "Botez · Chaotic Fun",
        "tagline": "Botez gambit incoming?",
        "avatar_letter": "B",
        "avatar_bg": "#831843",
        "avatar_accent": "#fb7185",
        "talks": {
            "Brilliant": ["NO WAY that was actually brilliant.", "Okay chat that was clean.", "I'm shook."],
            "Great": ["Great move ngl.", "Yes!!", "Clean."],
            "Best": ["Best. Obviously.", "Correct.", "Nice."],
            "Excellent": ["Excellent.", "Solid.", "Good."],
            "Good": ["Good.", "Playable.", "Fine."],
            "Okay": ["Okay...", "Could be better.", "Meh."],
            "Inaccuracy": ["Inaccuracy. Classic.", "Slightly off.", "Hmm."],
            "Mistake": ["Mistake. We love a blunder arc.", "That was free.", "Why."],
            "Miss": ["You missed it!!", "The tactic was right there.", "Oof."],
            "Blunder": ["BLUNDER. Content.", "That was painful.", "Chat is typing."],
        },
    },
    "Fabi": {
        "title": "Fabiano · Precision",
        "tagline": "Calculate everything.",
        "avatar_letter": "F",
        "avatar_bg": "#1e3a5f",
        "avatar_accent": "#93c5fd",
        "talks": {
            "Brilliant": ["Brilliant calculation.", "Very deep. Impressive.", "Excellent preparation."],
            "Great": ["Great. Precise.", "Strong practical choice.", "Well found."],
            "Best": ["Best. The only move.", "Correct.", "Accurate."],
            "Excellent": ["Excellent technique.", "Clean.", "Good."],
            "Good": ["Good.", "Solid.", "Playable."],
            "Okay": ["Okay. A bit imprecise.", "Acceptable.", "Could be sharper."],
            "Inaccuracy": ["Inaccuracy. Not the most accurate.", "Slight error.", "Be more precise."],
            "Mistake": ["Mistake. Now the evaluation shifts.", "Unnecessary.", "Calculate deeper."],
            "Miss": ["You missed a strong continuation.", "There was more.", "Look for tactics."],
            "Blunder": ["Blunder. Hard to justify.", "That loses material.", "Unfortunate."],
        },
    },
    "Naroditsky": {
        "title": "Danya · Clear Explanation",
        "tagline": "Let's break this down.",
        "avatar_letter": "D",
        "avatar_bg": "#164e63",
        "avatar_accent": "#67e8f9",
        "talks": {
            "Brilliant": ["Brilliant. Let me explain why this works...", "Fantastic. The idea is crystal clear.", "Superb calculation."],
            "Great": ["Great practical move.", "Very instructive.", "Nice find."],
            "Best": ["Best. Textbook.", "Correct approach.", "Clean."],
            "Excellent": ["Excellent.", "Solid understanding.", "Good."],
            "Good": ["Good.", "Playable.", "Fine."],
            "Okay": ["Okay. A bit passive.", "We can improve this.", "Think about the plan."],
            "Inaccuracy": ["Inaccuracy. The idea is almost right.", "Slightly off.", "Close."],
            "Mistake": ["Mistake. Let's see the issue...", "That allows too much.", "Careful."],
            "Miss": ["Missed opportunity. The tactic was there.", "You had something stronger.", "Next time."],
            "Blunder": ["Blunder. Fundamental error.", "This is hard to recover from.", "Learn from it."],
        },
    },
    "Eric Rosen": {
        "title": "Eric Rosen · Imaginative",
        "tagline": "Hello everyone!",
        "avatar_letter": "E",
        "avatar_bg": "#3f1d0b",
        "avatar_accent": "#fdba74",
        "talks": {
            "Brilliant": ["Hello everyone! That was a brilliant idea.", "Creative and strong. Love it.", "Very imaginative."],
            "Great": ["Great practical decision.", "Nice find.", "Good energy."],
            "Best": ["Best. Clean.", "Correct.", "Solid."],
            "Excellent": ["Excellent.", "Nice.", "Good."],
            "Good": ["Good.", "Playable.", "Fine."],
            "Okay": ["Okay.", "Could be more creative.", "Hmm."],
            "Inaccuracy": ["Slight inaccuracy.", "Not the most precise.", "Close."],
            "Mistake": ["Mistake. Let's reset.", "Unnecessary.", "Careful."],
            "Miss": ["Missed a fun idea there.", "There was something spicy.", "Next time."],
            "Blunder": ["Blunder. Ouch.", "That hurts.", "We move on."],
        },
    },
}

_OPPONENTS = {
    "Beginner Bot": {"depth": 1, "desc": "Simple moves. Perfect for learning the basics."},
    "Club Player": {"depth": 2, "desc": "Solid club level. Punishes obvious mistakes."},
    "Strong Club": {"depth": 3, "desc": "Sharp and opportunistic."},
    "Master Bot": {"depth": 4, "desc": "Deep calculation. Ruthless."},
    "GothamBot": {"depth": 3, "desc": "Plays like a coach who wants you to improve."},
    "Hikaru Speed": {"depth": 2, "desc": "Quick, tricky, and annoying."},
    "Magnus Endgame": {"depth": 4, "desc": "Converts the tiniest advantages."},
    "Chaos Bot": {"depth": 2, "desc": "Unpredictable and fun."},
}

def apply_coach(code: str) -> str:
    inject_ui = '''
    # === Meridium coaches + AI opponents ===
    _MER_COACHES = ''' + repr(_COACHES) + '''
    _MER_OPPONENTS = ''' + repr(_OPPONENTS) + '''
    if "chess_coach" not in st.session_state:
        st.session_state.chess_coach = "Soju"
    if "chess_opponent" not in st.session_state:
        st.session_state.chess_opponent = "Club Player"
    _cc1, _cc2 = st.columns(2)
    with _cc1:
        st.session_state.chess_coach = st.selectbox(
            "Coach",
            list(_MER_COACHES.keys()),
            index=list(_MER_COACHES.keys()).index(st.session_state.chess_coach) if st.session_state.chess_coach in _MER_COACHES else 0,
            key="mer_sel_coach",
        )
    with _cc2:
        st.session_state.chess_opponent = st.selectbox(
            "AI Opponent",
            list(_MER_OPPONENTS.keys()),
            index=list(_MER_OPPONENTS.keys()).index(st.session_state.chess_opponent) if st.session_state.chess_opponent in _MER_OPPONENTS else 1,
            key="mer_sel_opp",
        )
    _coach = _MER_COACHES[st.session_state.chess_coach]
    _opp = _MER_OPPONENTS[st.session_state.chess_opponent]
    st.caption(_coach["title"] + "  ·  " + _coach.get("tagline", ""))
    st.caption("vs " + st.session_state.chess_opponent + " (depth " + str(_opp["depth"]) + ") — " + _opp["desc"])
'''
    placed = False
    for marker in ['st.subheader("Chess")', "st.subheader('Chess')", 'st.title("Chess")', "st.title('Chess')"]:
        if marker in code:
            code = code.replace(marker, marker + "\n" + inject_ui, 1)
            placed = True
            break
    if not placed and "st.components.v1.html(" in code:
        code = code.replace("st.components.v1.html(", inject_ui + "\n    st.components.v1.html(", 1)
    for old, new in [
        ('html = html.replace("__DEPTH__", str(depth))', 'html = html.replace("__DEPTH__", str(_opp["depth"] if "_opp" in dir() else depth))'),
        ("html = html.replace('__DEPTH__', str(depth))", "html = html.replace('__DEPTH__', str(_opp['depth'] if '_opp' in dir() else depth))"),
    ]:
        if old in code:
            code = code.replace(old, new)
    personality = r'''
        # Coach personality + avatar override
        try:
            _c = _MER_COACHES.get(st.session_state.get("chess_coach", "Soju"), {})
            if _c.get("talks"):
                import json as _json
                _talks_js = "const TALKS = " + _json.dumps(_c["talks"]) + ";"
                if "const TALKS = {" in html:
                    html = html.replace("const TALKS = {", _talks_js + " /*orig*/ const TALKS = {", 1)
            if st.session_state.get("chess_coach", "Soju") != "Soju":
                _letter = _c.get("avatar_letter", "C")
                _bg = _c.get("avatar_bg", "#1a1224")
                _ac = _c.get("avatar_accent", "#c4a7e7")
                _svg = (
                    '<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">'
                    f'<rect width="128" height="128" rx="28" fill="{_bg}"/>'
                    f'<circle cx="64" cy="48" r="28" fill="{_ac}" opacity="0.85"/>'
                    f'<circle cx="64" cy="48" r="20" fill="#0f0a18"/>'
                    f'<text x="64" y="56" text-anchor="middle" font-family="system-ui,sans-serif" font-size="26" font-weight="700" fill="{_ac}">{_letter}</text>'
                    f'<rect x="30" y="84" width="68" height="32" rx="16" fill="{_ac}" opacity="0.3"/>'
                    "</svg>"
                )
                import base64 as _b64m
                _av = "data:image/svg+xml;base64," + _b64m.b64encode(_svg.encode()).decode()
                for _key in ("__SOJU_IDLE__", "__SOJU_HAPPY__", "__SOJU_SHOCK__", "__SOJU_THINK__"):
                    html = html.replace(_key, _av)
                _nm = st.session_state.get("chess_coach", "Soju")
                html = html.replace(">Soju<", f">{_nm}<")
                html = html.replace("Soju ·", _nm + " ·")
        except Exception:
            pass
'''
    for marker in [
        'html = html.replace("__SOJU_THINK__", _b64img("soju_think.jpg"))',
        "html = html.replace('__SOJU_THINK__', _b64img('soju_think.jpg'))",
    ]:
        if marker in code:
            code = code.replace(marker, marker + "\n" + personality, 1)
            break
    return code
