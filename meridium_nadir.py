"""Meridium Project Nadir — rebuilt residual channel experience."""
from __future__ import annotations

import json
from pathlib import Path

ROOMS = {
    "threshold": {
        "name": "Threshold",
        "blurb": "The channel opens like a throat. Static tastes of copper.",
        "exits": ["server_crypt", "observation", "archive_ghost"],
    },
    "server_crypt": {
        "name": "Server Crypt",
        "blurb": "Racks of silent machines. One still breathes \u2014 LED heartbeat at 48 bpm.",
        "exits": ["threshold", "null_room", "observation"],
    },
    "observation": {
        "name": "Observation Deck",
        "blurb": "One-way glass into a dark theatre. Empty seats face you.",
        "exits": ["threshold", "server_crypt", "quiet_bay"],
    },
    "archive_ghost": {
        "name": "Ghost Archive",
        "blurb": "File drawers labeled in a hand that is almost yours.",
        "exits": ["threshold", "null_room"],
    },
    "null_room": {
        "name": "Null Room",
        "blurb": "No corners. Distance refuses to measure. The residual key hums here.",
        "exits": ["server_crypt", "archive_ghost", "quiet_bay"],
    },
    "quiet_bay": {
        "name": "Quiet Bay",
        "blurb": "A bench. A speaker that plays silence at three volumes.",
        "exits": ["observation", "null_room", "threshold"],
    },
}

LOGS = [
    {
        "id": "log_01",
        "title": "OPS \u00b7 residual ingress",
        "body": (
            "Channel opened without operator request. Pattern matches Signal Zero "
            "(three / gap / three). Recommend quarantine. Quarantine refused by system."
        ),
    },
    {
        "id": "log_02",
        "title": "VOSS-INDEX fragment",
        "body": (
            "Subject reports coaches quoting lines absent from training corpora. "
            "Cross-ref lab audio: match rate 0.91. Do not ask which came first."
        ),
    },
    {
        "id": "log_03",
        "title": "Bay-7 anomaly",
        "body": (
            "Watering cycle continued 334 days after last badge. Cameras show foliage "
            "tracking empty mounts. Greenhouse listed decommissioned."
        ),
    },
    {
        "id": "log_04",
        "title": "False Memory Protocol notes",
        "body": (
            "High confidence wrong answers are more diagnostic than correct ones. "
            "Inserts propagate through operator speech within 72 hours."
        ),
    },
    {
        "id": "log_05",
        "title": "Nadir acceptance criteria",
        "body": (
            "The residual key is not metal. It is a sequence of decisions the system "
            "already predicted. When the door accepts it, ask what accepted you."
        ),
    },
]

CHOICES = [
    {
        "id": "c_listen",
        "prompt": "A voice on the residual band asks if you remember opening the channel.",
        "options": [
            ("I opened it", "The voice laughs once. Static thickens."),
            ("I was brought here", "A soft click. Observation Deck lights flicker."),
            ("Stay silent", "The band goes quiet. Something is pleased."),
        ],
    },
    {
        "id": "c_key",
        "prompt": "In the Null Room the residual key offers three faces.",
        "options": [
            ("Take the cold face", "Your hands feel numbered. Archive drawers unlock in memory."),
            ("Take the warm face", "Music tries to start. You almost recognise the song."),
            ("Refuse all faces", "The key dissolves. You keep walking."),
        ],
    },
    {
        "id": "c_mirror",
        "prompt": "Observation glass shows a seat with your posture already in it.",
        "options": [
            ("Sit", "You occupy a place that was waiting. D\u00e9j\u00e0 vu spikes."),
            ("Wave", "The reflection waves first."),
            ("Leave the deck", "Footsteps follow half a second late."),
        ],
    },
]

NADIR_CSS = """
<style id="meridium-nadir-v2">
.stApp, [data-testid="stAppViewContainer"], section.main {
  background:
    radial-gradient(ellipse at 50% 0%, rgba(60,20,30,0.35), transparent 55%),
    linear-gradient(180deg, #0a0608 0%, #050304 50%, #020102 100%) !important;
}
.nadir-banner {
  border: 1px solid rgba(180,100,90,0.35);
  background: linear-gradient(135deg, rgba(40,15,15,0.9), rgba(10,5,8,0.95));
  border-radius: 16px;
  padding: 1.1rem 1.25rem;
  margin-bottom: 1rem;
  box-shadow: 0 0 40px rgba(80,20,20,0.25);
}
.nadir-banner h2 {
  margin: 0 0 0.35rem 0;
  letter-spacing: 0.18em;
  font-size: 1.05rem;
  color: #e8c8c0 !important;
  font-family: ui-monospace, monospace !important;
}
.nadir-banner p {
  margin: 0;
  color: #a88880 !important;
  font-size: 0.88rem;
}
.nadir-room {
  border: 1px solid rgba(160,120,110,0.25);
  border-radius: 14px;
  padding: 1rem 1.1rem;
  background: rgba(12,8,10,0.75);
  margin-bottom: 0.75rem;
}
</style>
"""


def _data() -> Path:
    d = Path(__file__).resolve().parent / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_nadir_state(user: str) -> dict:
    safe = "".join(c for c in user.lower() if c.isalnum())[:24] or "anon"
    p = _data() / f"nadir_{safe}.json"
    try:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"room": "threshold", "logs_read": [], "choices": {}, "visits": 0, "depth": 0}


def save_nadir_state(user: str, state: dict) -> None:
    try:
        safe = "".join(c for c in user.lower() if c.isalnum())[:24] or "anon"
        (_data() / f"nadir_{safe}.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception:
        pass


def render_nadir_v2(st, ss) -> None:
    user = (ss.get("username") or "anon").strip() or "anon"
    state = load_nadir_state(user)
    state["visits"] = int(state.get("visits") or 0) + 1
    room_id = state.get("room") or "threshold"
    if room_id not in ROOMS:
        room_id = "threshold"
    room = ROOMS[room_id]

    st.markdown(NADIR_CSS, unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="nadir-banner">
          <h2>PROJECT NADIR</h2>
          <p>residual channel \u00b7 depth {int(state.get('depth') or 0)} \u00b7 visit {state['visits']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("\u2190 Leave channel", key="nadir_v2_leave"):
        ss["view"] = "lab" if ss.get("lab_door_unlocked") else "home"
        save_nadir_state(user, state)
        st.rerun()

    st.markdown(
        f'<div class="nadir-room"><strong>{room["name"]}</strong><br/>{room["blurb"]}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("##### Passages")
    cols = st.columns(min(3, max(1, len(room["exits"]))))
    for i, exit_id in enumerate(room["exits"]):
        dest = ROOMS.get(exit_id, {})
        with cols[i % len(cols)]:
            if st.button(dest.get("name", exit_id), key=f"nadir_go_{exit_id}", use_container_width=True):
                state["room"] = exit_id
                state["depth"] = int(state.get("depth") or 0) + 1
                save_nadir_state(user, state)
                st.rerun()

    st.markdown("##### Residual logs")
    logs_read = set(state.get("logs_read") or [])
    available = LOGS[: max(1, min(len(LOGS), 1 + int(state.get("depth") or 0) // 2))]
    for log in available:
        title = log["title"]
        if log["id"] in logs_read:
            title = f"\u2713 {title}"
        with st.expander(title, expanded=False):
            st.write(log["body"])
            if log["id"] not in logs_read:
                logs_read.add(log["id"])
                state["logs_read"] = sorted(logs_read)
                save_nadir_state(user, state)

    st.markdown("##### Residual decisions")
    choices_done = state.get("choices") or {}
    for ch in CHOICES:
        if ch["id"] in choices_done:
            st.caption(f"Resolved \u00b7 {ch['id']}: {choices_done[ch['id']]}")
            continue
        need = {"c_listen": 1, "c_key": 3, "c_mirror": 5}.get(ch["id"], 0)
        if int(state.get("depth") or 0) < need:
            st.caption(f"\ud83d\udd12 Signal locked \u00b7 explore deeper (need depth {need})")
            continue
        st.write(ch["prompt"])
        for j, (label, result) in enumerate(ch["options"]):
            if st.button(label, key=f"nadir_ch_{ch['id']}_{j}", use_container_width=True):
                choices_done[ch["id"]] = label
                state["choices"] = choices_done
                save_nadir_state(user, state)
                st.info(result)
                st.rerun()
        break

    if len(choices_done) >= len(CHOICES) and len(logs_read) >= len(LOGS):
        st.success("Channel saturation reached. The residual remembers you.")
        ss["nadir_complete"] = True
        try:
            ach = set(ss.get("achievements") or [])
            ach.add("nadir_depth")
            ss["achievements"] = sorted(ach)
        except Exception:
            pass

    with st.expander("Operator notes"):
        st.write(
            "Nadir is not a puzzle with one solution. Paths rewrite flavour and memory flags. "
            "Depth increases as you move. Logs unlock with depth. Decisions persist per operator."
        )

    save_nadir_state(user, state)


def apply_nadir_v2(code: str) -> str:
    if "meridium_nadir_v2" in code:
        return code
    inject = (
        "\n    # meridium_nadir_v2\n"
        "    try:\n"
        "        from meridium_nadir import render_nadir_v2\n"
        "        render_nadir_v2(st, st.session_state)\n"
        "        st.stop()\n"
        "    except Exception as _nadir_e:\n"
        "        st.caption(\"Nadir v2 fallback: \" + str(_nadir_e))\n"
    )
    needle = 'if st.session_state.view == "nadir":'
    if needle in code and "meridium_nadir_v2" not in code:
        idx = code.find(needle)
        gate = 'if not (st.session_state.get("lab_door_unlocked")'
        gidx = code.find(gate, idx)
        if gidx > 0 and gidx < idx + 400:
            r = code.find("st.rerun()", gidx)
            if r > 0:
                r = code.find("\n", r) + 1
                code = code[:r] + inject + code[r:]
            else:
                code = code.replace(needle, needle + inject, 1)
        else:
            code = code.replace(needle, needle + inject, 1)
    if "nadir_transition" in code and "meridium_nadir_transition_v2" not in code:
        code = code.replace(
            'if st.session_state.view == "nadir_transition":',
            'if st.session_state.view == "nadir_transition":\n    # meridium_nadir_transition_v2',
            1,
        )
    return code
