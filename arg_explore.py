"""Meridium ARG explore layer — non-chess complex features."""
from __future__ import annotations

import hashlib
import json
import random
from datetime import date, datetime, timezone, timedelta
from pathlib import Path


def _data_dir() -> Path:
    try:
        root = Path(__file__).resolve().parent
    except Exception:
        root = Path.cwd()
    d = root / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _load_json(name: str, default):
    p = _data_dir() / name
    try:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def _save_json(name: str, obj) -> None:
    try:
        (_data_dir() / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def _user(ss) -> str:
    return (ss.get("username") or "anon").strip() or "anon"


def _today() -> str:
    return date.today().isoformat()


_VOSS_LETTERS = [
    {"id": "v1", "date": "1978-03-12", "subject": "Re: corridor 4 clearance",
     "body": "You were never scheduled for Corridor 4. If you found this, you already walked it. Do not answer the intercom after 02:00.", "need_markers": 0},
    {"id": "v2", "date": "1978-06-01", "subject": "Margin note \u2014 Callaghan",
     "body": "Callaghan left a margin note in the archive catalog. Search M-119. The spectrum lock is not a metaphor.", "need_markers": 1},
    {"id": "v3", "date": "1979-01-19", "subject": "For the one who keeps returning",
     "body": "Three markers. One file. I am not the residual \u2014 I am what the residual is trying to forget. Meet me in the tea room transcript.", "need_markers": 3},
    {"id": "v4", "date": "1980-11-03", "subject": "[REDACTED] greenhouse schedule",
     "body": "The plant in bay 7 responds to names. Water it three days in a row and it will spell something back.", "need_markers": 2},
]


def mail_letters(ss) -> list:
    n = len(ss.get("glitches_found") or [])
    return [L for L in _VOSS_LETTERS if n >= L["need_markers"]]


_ROOMS = {
    "lobby": {"name": "Lobby", "desc": "Flickering fluorescents. The directory is half burned out.", "open": True},
    "corridor": {"name": "Corridor 4", "desc": "The anomaly scan pointed here. Paint peels in a spiral.", "need": 0},
    "archive": {"name": "Archive", "desc": "Drawers of microfilm and false catalog numbers.", "need": 1},
    "greenhouse": {"name": "Greenhouse", "desc": "Humidity and something that should not grow indoors.", "need": 1},
    "tea": {"name": "Tea Room", "desc": "Two chairs. One cup still warm.", "need": 2},
    "spectrum": {"name": "Spectrum Lab", "desc": "Dials, sliders, a locked color code.", "need": 2},
    "cipher": {"name": "Cipher Desk", "desc": "Paper, pencil, and a key pulled from the walls.", "need": 0},
    "badge": {"name": "Portrait Booth", "desc": "Flash. Static. Your ID never looked like this.", "need": 0},
    "stars": {"name": "Star Chart", "desc": "A dome of pin lights. Connect them.", "need": 1},
    "wall": {"name": "Anonymous Wall", "desc": "Chalk and scratch marks. One line each.", "need": 0},
}


def room_unlocked(room_id: str, ss) -> bool:
    r = _ROOMS.get(room_id) or {}
    if r.get("open"):
        return True
    return len(ss.get("glitches_found") or []) >= int(r.get("need") or 0)


_TAPES = [
    {"id": "t1", "title": "Tape 03B \u2014 Loading dock",
     "text": "Static. A figure walks past without a shadow. Audio: '...not supposed to loop.'",
     "choices": [("Follow the figure", "You step after them. The dock becomes Corridor 4."),
                 ("Stay at the monitor", "The tape rewinds itself. You were already watching.")]},
    {"id": "t2", "title": "Tape 11 \u2014 Intercom",
     "text": "Someone says your username before you typed it. The intercom light stays on.",
     "choices": [("Answer", "Silence, then: 'Marker secured. Keep walking.'"),
                 ("Unplug it", "The light dies. A new scratch appears on the anonymous wall.")]},
]

_DREAM_PROMPTS = [
    "What color was the door you should not open?",
    "Who spoke your name in the residual?",
    "What grew in the greenhouse that should not?",
    "Which marker felt warm?",
    "What did the star chart spell before you finished it?",
]


def dream_prompt_for_today() -> str:
    i = int(hashlib.md5(_today().encode()).hexdigest(), 16) % len(_DREAM_PROMPTS)
    return _DREAM_PROMPTS[i]


_QUIZ = [
    {"q": "How many Voss markers exist in the complex?", "opts": ["1", "2", "3", "6"], "a": 2},
    {"q": "What is the spectrum lock code related to?", "opts": ["M-119", "Bay 7", "Tape 03B", "Lobby"], "a": 0},
    {"q": "Corridor number flagged by residual scan?", "opts": ["1", "2", "3", "4"], "a": 3},
    {"q": "Who left a margin note in the archive?", "opts": ["Voss", "Callaghan", "Soju", "Meridium"], "a": 1},
    {"q": "Greenhouse bay that responds to names?", "opts": ["3", "5", "7", "9"], "a": 2},
]


def score_quiz(answers: list) -> dict:
    correct = sum(1 for i, ans in enumerate(answers) if i < len(_QUIZ) and ans == _QUIZ[i]["a"])
    n = len(_QUIZ)
    pct = int(100 * correct / n) if n else 0
    if pct >= 80:
        ending = "The lab remembers you clearly. Door seal: soft green."
    elif pct >= 40:
        ending = "Partial recall. Something still redacts your face."
    else:
        ending = "You are almost a stranger here. The residual is louder than you."
    return {"correct": correct, "n": n, "pct": pct, "ending": ending}


def wall_load() -> list:
    return _load_json("anon_wall.json", [])


def wall_post(user: str, text: str) -> str:
    text = (text or "").strip()[:120]
    if not text:
        return "empty"
    rows = wall_load()
    today = _today()
    for r in rows:
        if r.get("user") == user and r.get("day") == today:
            return "already"
    rows.append({"user": user, "day": today, "text": text, "ts": datetime.now(timezone.utc).isoformat()})
    _save_json("anon_wall.json", rows[-80:])
    return "ok"


def wall_clear() -> None:
    _save_json("anon_wall.json", [])


def roster_load() -> dict:
    return _load_json("night_roster.json", {})


def roster_claim(user: str, shift: str) -> None:
    data = roster_load()
    day = _today()
    data.setdefault(day, {})
    data[day][user] = shift
    for k in sorted(data.keys())[:-5]:
        data.pop(k, None)
    _save_json("night_roster.json", data)


def flare_load() -> dict:
    return _load_json("signal_flare.json", {})


def flare_set(user: str, msg: str) -> None:
    _save_json("signal_flare.json", {
        "day": _today(), "user": user, "msg": (msg or "").strip()[:160],
        "ts": datetime.now(timezone.utc).isoformat(),
    })


def flare_get() -> dict:
    f = flare_load()
    return f if f.get("day") == _today() else {}


def caesar(text: str, shift: int) -> str:
    out = []
    for ch in text:
        if "A" <= ch <= "Z":
            out.append(chr((ord(ch) - 65 + shift) % 26 + 65))
        elif "a" <= ch <= "z":
            out.append(chr((ord(ch) - 97 + shift) % 26 + 97))
        else:
            out.append(ch)
    return "".join(out)


def vigenere(text: str, key: str, decrypt: bool = False) -> str:
    key = "".join(c for c in key.upper() if c.isalpha())
    if not key:
        return text
    out, ki = [], 0
    for ch in text:
        if ch.isalpha():
            base = 65 if ch.isupper() else 97
            k = ord(key[ki % len(key)]) - 65
            if decrypt:
                k = -k
            out.append(chr((ord(ch) - base + k) % 26 + base))
            ki += 1
        else:
            out.append(ch)
    return "".join(out)


def spectrum_solved(h: int, s: int, v: int) -> bool:
    return abs(h - 270) <= 12 and abs(s - 70) <= 10 and abs(v - 40) <= 10


def badge_html(username: str, title: str = "RESIDUAL CLEARANCE") -> str:
    u = (username or "ANON").upper()[:18]
    code = hashlib.md5(u.encode()).hexdigest()[:8].upper()
    return (
        f"<div style='max-width:340px;margin:0.5rem auto;padding:1rem 1.1rem;border-radius:14px;"
        f"border:1px solid rgba(167,139,250,0.55);background:linear-gradient(145deg,#1a1028,#0d0a14);"
        f"box-shadow:0 0 28px rgba(139,92,246,0.25);font-family:ui-monospace,monospace;color:#e9d5ff;'>"
        f"<div style='font-size:0.65rem;letter-spacing:0.2em;color:#a78bfa;'>MERIDIUM COMPLEX</div>"
        f"<div style='font-size:1.35rem;font-weight:800;margin:0.35rem 0;color:#f5f3ff;'>{u}</div>"
        f"<div style='font-size:0.8rem;color:#c4b5fd;'>{title}</div>"
        f"<div style='margin-top:0.6rem;font-size:0.75rem;color:#86efac;'>ID \u00b7 {code}</div>"
        f"<div style='margin-top:0.35rem;height:6px;background:repeating-linear-gradient(90deg,#7c3aed 0 4px,transparent 4px 8px);'></div>"
        f"</div>"
    )


_ARCHIVE = {
    "M-119": "Spectrum lock reference. Violet band. Related letter: v2.",
    "C-04": "Corridor 4 anomaly log. Intercom after 02:00 restricted.",
    "BAY-7": "Greenhouse bay. Responds to spoken names over three days.",
    "TAPE-03B": "Found footage: loading dock. Figure without shadow.",
    "VOSS-FILE": "Requires three markers. Not a document \u2014 a door.",
    "CALLAGHAN": "Margin note author. Archive drawer 12.",
}


def archive_search(q: str) -> str:
    q = (q or "").strip().upper()
    if not q:
        return ""
    if q in _ARCHIVE:
        return _ARCHIVE[q]
    for k, v in _ARCHIVE.items():
        if q in k or q in v.upper():
            return f"{k}: {v}"
    return "No catalog match. Try M-119, C-04, BAY-7, TAPE-03B, VOSS-FILE, CALLAGHAN."


_GROW_LINES = [
    "Soil only.",
    "A pale shoot.",
    "Two leaves. They angle toward your name.",
    "Stem writes a curve like a letter V.",
    "Leaves spell \u00b7 O \u00b7 when viewed from above.",
    "Bay-7 whispers: S S \u2014 then goes still.",
]


def greenhouse_state(user: str) -> dict:
    return _load_json("greenhouse.json", {}).get(user) or {
        "streak": 0, "last": "", "name": "Bay-7 sprout", "stage": 0
    }


def greenhouse_water(user: str) -> dict:
    st = greenhouse_state(user)
    today = _today()
    if st.get("last") == today:
        return st
    if st.get("last"):
        try:
            last = date.fromisoformat(st["last"])
            st["streak"] = int(st.get("streak") or 0) + 1 if (date.today() - last).days == 1 else 1
        except Exception:
            st["streak"] = 1
    else:
        st["streak"] = 1
    st["last"] = today
    st["stage"] = min(5, int(st.get("streak") or 0))
    data = _load_json("greenhouse.json", {})
    data[user] = st
    _save_json("greenhouse.json", data)
    return st


_TEA_LINES = [
    ("Soju-adjacent residual", "Sit. The cup is not for drinking. It is for measuring how long you stay."),
    ("Archive clerk", "Callaghan's drawer sticks. Everyone pretends not to notice."),
    ("Night tech", "If the intercom says your name, do not answer unless you already know the answer."),
    ("Voss (maybe)", "Three markers. Then the file. I will not be what you expect."),
]

_STAR_ORDER = [0, 2, 1, 3, 4]


def countdown_load() -> dict:
    return _load_json("countdown.json", {})


def countdown_set(label: str, iso_end: str) -> None:
    _save_json("countdown.json", {"label": label, "end": iso_end})


_RUMORS_POOL = [
    "Corridor 4 loops after midnight.",
    "Bay-7 is not a plant.",
    "Voss is a title, not a person.",
    "The chess coaches can hear the residual.",
    "M-119 opens the spectrum lock.",
    "The anonymous wall eats one line per week.",
]


def rumors_week() -> dict:
    data = _load_json("rumors.json", {})
    week = date.today().isocalendar()[:2]
    key = f"{week[0]}-W{week[1]}"
    if data.get("week") != key:
        pick = random.sample(_RUMORS_POOL, 3)
        data = {"week": key, "rumors": pick, "true": random.randint(0, 2), "votes": {}}
        _save_json("rumors.json", data)
    return data


def rumor_vote(user: str, idx: int) -> dict:
    data = rumors_week()
    data.setdefault("votes", {})[user] = int(idx)
    _save_json("rumors.json", data)
    return data


def quiet_hours_active() -> bool:
    h = datetime.now().hour
    site = _load_json("site_effects.json", {})
    if site.get("quiet_mode"):
        return True
    return 0 <= h < 6


def render_explore(st, ss) -> None:
    user = _user(ss)
    sub = ss.get("explore_room") or "lobby"

    if quiet_hours_active():
        st.caption("Quiet hours \u00b7 the complex is speaking softly.")

    fl = flare_get()
    if fl.get("msg"):
        st.info(f"Signal flare \u00b7 {fl.get('user', '?')}: {fl['msg']}")

    cd = countdown_load()
    if cd.get("end"):
        try:
            end = datetime.fromisoformat(cd["end"].replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            if end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)
            delta = end - now
            if delta.total_seconds() > 0:
                hrs = int(delta.total_seconds() // 3600)
                mins = int((delta.total_seconds() % 3600) // 60)
                st.warning(f"\u23f1 {cd.get('label') or 'Event'}: {hrs}h {mins}m remaining")
            else:
                st.success(f"\u23f1 {cd.get('label') or 'Event'} \u2014 window open.")
        except Exception:
            pass

    st.markdown("### Meridium Complex")
    st.caption("Non-chess wing \u00b7 explore rooms \u00b7 ARG layer")

    room_ids = list(_ROOMS.keys())
    for row_start in range(0, len(room_ids), 5):
        cols = st.columns(5)
        for j, rid in enumerate(room_ids[row_start:row_start + 5]):
            with cols[j]:
                locked = not room_unlocked(rid, ss)
                label = ("\U0001f512 " if locked else "") + _ROOMS[rid]["name"]
                if st.button(label, key=f"room_{rid}", use_container_width=True, disabled=locked):
                    ss["explore_room"] = rid
                    st.rerun()

    if st.button("\u2190 Back to home", key="explore_home"):
        ss["view"] = "home"
        st.rerun()

    st.divider()
    room = _ROOMS.get(sub) or _ROOMS["lobby"]
    st.markdown(f"#### {room['name']}")
    st.write(room["desc"])

    if sub == "lobby":
        st.write("Choose a room above. Lab markers unlock deeper doors.")
        st.caption(f"Markers secured: {len(ss.get('glitches_found') or [])}")
        with st.expander("\u2709 Mail from Voss", expanded=True):
            letters = mail_letters(ss)
            if not letters:
                st.caption("No letters yet.")
            for L in letters:
                st.markdown(f"**{L['subject']}** \u00b7 _{L['date']}_")
                st.write(L["body"])

    elif sub == "corridor":
        with st.expander("\U0001f39e Found footage", expanded=True):
            for tape in _TAPES:
                st.markdown(f"**{tape['title']}**")
                st.write(tape["text"])
                c1, c2 = st.columns(2)
                kbase = f"tape_{tape['id']}"
                if c1.button(tape["choices"][0][0], key=f"{kbase}_a"):
                    ss[f"tape_res_{tape['id']}"] = tape["choices"][0][1]
                if c2.button(tape["choices"][1][0], key=f"{kbase}_b"):
                    ss[f"tape_res_{tape['id']}"] = tape["choices"][1][1]
                if ss.get(f"tape_res_{tape['id']}"):
                    st.success(ss[f"tape_res_{tape['id']}"])

    elif sub == "archive":
        q = st.text_input("Catalog search", placeholder="M-119", key="arch_q")
        if st.button("Search", key="arch_go") or q:
            st.code(archive_search(q), language=None)
        st.caption("Stubs: M-119 \u00b7 C-04 \u00b7 BAY-7 \u00b7 TAPE-03B \u00b7 VOSS-FILE \u00b7 CALLAGHAN")

    elif sub == "greenhouse":
        st_ = greenhouse_state(user)
        st.write(f"**{st_.get('name', 'Bay-7')}** \u00b7 stage {st_.get('stage', 0)} \u00b7 streak {st_.get('streak', 0)}")
        stage = int(st_.get("stage") or 0)
        st.info(_GROW_LINES[min(stage, len(_GROW_LINES) - 1)])
        if st.button("Water today", key="gh_water", type="primary"):
            greenhouse_water(user)
            st.success("Watered.")
            st.rerun()

    elif sub == "tea":
        for who, line in _TEA_LINES:
            st.markdown(f"**{who}**")
            st.write(line)

    elif sub == "spectrum":
        h = st.slider("Hue", 0, 360, 180, key="spec_h")
        s = st.slider("Saturation", 0, 100, 50, key="spec_s")
        v = st.slider("Value", 0, 100, 50, key="spec_v")
        color = f"hsl({h}, {s}%, {v // 2 + 20}%)"
        st.markdown(
            f"<div style='height:64px;border-radius:12px;background:{color};border:1px solid #444'></div>",
            unsafe_allow_html=True,
        )
        if spectrum_solved(h, s, v):
            st.success("Spectrum lock open \u00b7 M-119 band aligned.")
            ss["spectrum_open"] = True
        else:
            st.caption("Tune toward violet, muted, low value.")

    elif sub == "cipher":
        mode = st.radio("Mode", ["Caesar", "Vigen\u00e8re"], horizontal=True, key="cip_mode")
        text = st.text_area("Input", key="cip_in")
        if mode == "Caesar":
            shift = st.slider("Shift", 0, 25, 3, key="cip_shift")
            if text:
                st.code(caesar(text, shift), language=None)
        else:
            key = st.text_input("Key", value="VOSS", key="cip_key")
            dec = st.checkbox("Decrypt", value=True, key="cip_dec")
            if text:
                st.code(vigenere(text, key, decrypt=dec), language=None)
        st.caption("Keys: VOSS \u00b7 M119 \u00b7 CALLAGHAN")

    elif sub == "badge":
        title = st.text_input("Clearance title", value="RESIDUAL CLEARANCE", key="badge_title")
        st.markdown(badge_html(user, title), unsafe_allow_html=True)

    elif sub == "stars":
        st.write("Click stars in the correct order.")
        prog = list(ss.get("star_clicks") or [])
        cols = st.columns(5)
        labels = ["\u03b1", "\u03b2", "\u03b3", "\u03b4", "\u03b5"]
        for i in range(5):
            with cols[i]:
                done = i in prog
                if st.button(("\u2713 " if done else "") + labels[i], key=f"star_{i}", disabled=done):
                    prog = prog + [i]
                    ss["star_clicks"] = prog
                    if prog == _STAR_ORDER[: len(prog)]:
                        if len(prog) == 5:
                            ss["stars_solved"] = True
                    else:
                        ss["star_clicks"] = []
                        st.warning("Pattern broke. Reset.")
                    st.rerun()
        if ss.get("stars_solved"):
            st.success("Constellation locked \u00b7 spells **VOSS**.")
        if st.button("Reset stars", key="star_reset"):
            ss["star_clicks"] = []
            ss.pop("stars_solved", None)
            st.rerun()

    elif sub == "wall":
        for r in reversed(wall_load()[-20:]):
            st.markdown(f"_{r.get('day')}_ \u00b7 `{r.get('user')}` \u2014 {r.get('text')}")
        msg = st.text_input("Your line (once per day)", max_chars=120, key="wall_msg")
        if st.button("Scratch it in", key="wall_post"):
            res = wall_post(user, msg)
            if res == "ok":
                st.success("Marked.")
                st.rerun()
            elif res == "already":
                st.warning("You already wrote today.")
            else:
                st.error("Empty.")

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.expander("\U0001f319 Night shift"):
            shift = st.selectbox("Shift", ["00\u201304", "04\u201308", "20\u201324"], key="shift_pick")
            if st.button("Claim shift", key="shift_claim"):
                roster_claim(user, shift)
                st.success("On the roster.")
            data = roster_load().get(_today(), {})
            if data:
                for u, s in data.items():
                    st.write(f"**{u}** \u00b7 {s}")
            else:
                st.caption("No one claimed today.")
    with c2:
        with st.expander("\U0001f4e1 Signal flare"):
            msg = st.text_input("One line for the complex", key="flare_msg", max_chars=160)
            if st.button("Fire flare", key="flare_go"):
                flare_set(user, msg)
                st.success("Flare up.")
                st.rerun()
            fl = flare_get()
            if fl.get("msg"):
                st.caption(f"Live: {fl.get('user')}: {fl['msg']}")
    with c3:
        with st.expander("\U0001f4d3 Dream journal"):
            st.caption(dream_prompt_for_today())
            ans = st.text_area("Your answer", key="dream_ans", height=80)
            if st.button("File dream", key="dream_save"):
                dreams = _load_json("dreams.json", {})
                dreams.setdefault(user, [])
                dreams[user].append({"day": _today(), "prompt": dream_prompt_for_today(), "ans": (ans or "")[:300]})
                dreams[user] = dreams[user][-30:]
                _save_json("dreams.json", dreams)
                st.success("Filed.")

    with st.expander("\U0001f9e0 False memory quiz"):
        answers = []
        for i, item in enumerate(_QUIZ):
            answers.append(st.radio(
                item["q"], list(range(len(item["opts"]))),
                format_func=lambda j, it=item: it["opts"][j],
                key=f"quiz_{i}", horizontal=True,
            ))
        if st.button("Score recall", key="quiz_go"):
            res = score_quiz(answers)
            st.write(f"**{res['correct']}/{res['n']}** \u00b7 {res['pct']}%")
            st.info(res["ending"])

    with st.expander("\U0001f5e3 Rumor mill"):
        data = rumors_week()
        rumors = data.get("rumors") or []
        for i, r in enumerate(rumors):
            st.write(f"{i + 1}. {r}")
        if rumors:
            pick = st.radio(
                "Which is true this week?",
                list(range(len(rumors))),
                format_func=lambda i: rumors[i],
                key="rumor_pick",
            )
            if st.button("Cast vote", key="rumor_vote"):
                rumor_vote(user, int(pick))
                st.success("Vote recorded.")
            st.caption(f"{len(data.get('votes') or {})} votes this week.")

    with st.expander("\u2709 All unlocked Voss mail"):
        for L in mail_letters(ss):
            st.markdown(f"**{L['subject']}** ({L['date']})")
            st.write(L["body"])


def apply_arg_explore(code: str) -> str:
    """Inject Complex entry on home + explore view handler."""
    if "arg_explore render" in code:
        return code

    home_btn = (
        "\n    if st.button(\"\U0001f3e2 Enter the Complex\", key=\"goto_complex\", use_container_width=True):\n"
        "        st.session_state.view = \"explore\"\n"
        "        st.session_state.explore_room = \"lobby\"\n"
        "        st.rerun()\n"
    )
    for m in ['if st.session_state.view == "home":', "if st.session_state.view == 'home':"]:
        if m in code and "goto_complex" not in code:
            code = code.replace(m, m + home_btn, 1)
            break

    handler = (
        "\nif st.session_state.view == \"explore\":\n"
        "    # arg_explore render\n"
        "    try:\n"
        "        from arg_explore import render_explore\n"
        "        render_explore(st, st.session_state)\n"
        "    except Exception as _ex:\n"
        "        st.error(\"Complex wing offline: \" + str(_ex))\n"
        "        if st.button(\"Back home\", key=\"explore_fail_home\"):\n"
        "            st.session_state.view = \"home\"\n"
        "            st.rerun()\n"
        "    st.stop()\n"
    )
    if 'view == "explore"' not in code:
        for a in [
            'if st.session_state.view == "owner_room":',
            "if st.session_state.view == 'owner_room':",
            'if st.session_state.view == "lab":',
            "if st.session_state.view == 'lab':",
        ]:
            if a in code:
                code = code.replace(a, handler + "\n" + a, 1)
                break
        else:
            code = code + "\n" + handler

    return code
