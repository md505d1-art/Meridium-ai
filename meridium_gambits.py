"""Meridium Gambit Trainer — coach puzzle style (like Puzzle of the Day)."""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_GAMBITS: Optional[Dict[str, Any]] = None

COACHES = {
    "Soju": {
        "style": "calm and precise",
        "correct": [
            "Yes. That is the idea — {move}. Hold the centre, keep developing.",
            "Good. {move} is the main-line continuation. You are reading this well.",
            "Exact. Soju would play {move} here without hesitation.",
        ],
        "wrong": [
            "Not that. The line wants **{expected}**. Slow down — what square is weak?",
            "Close, but the coach line is **{expected}**. Try again.",
            "That drifts. Main idea continues with **{expected}**.",
        ],
        "intro": "Soju sets the board. Find the natural developing move.",
    },
    "Voss": {
        "style": "cryptic",
        "correct": [
            "The residual agrees. {move}. The line holds.",
            "Signal clean. {move} was already written.",
            "Yes — {move}. The archive marked this square.",
        ],
        "wrong": [
            "Static. The correct continuation is **{expected}**.",
            "That path diverges. Index says **{expected}**.",
            "No. The fragment reads **{expected}**.",
        ],
        "intro": "Voss does not explain. The move either resonates or it does not.",
    },
    "Callaghan": {
        "style": "blunt",
        "correct": [
            "Fine. {move}. Next.",
            "Yes — {move}. Do not get cute.",
            "That is it. {move}. Keep going.",
        ],
        "wrong": [
            "Wrong. Play **{expected}**.",
            "No. The book move is **{expected}**.",
            "Stop guessing. **{expected}**.",
        ],
        "intro": "Callaghan waits. One clean move. No speeches.",
    },
    "Jaime": {
        "style": "warm coach",
        "correct": [
            "Nice! {move} is exactly what we wanted.",
            "Well spotted — {move}. That is the gambit idea.",
            "Yes! {move}. You are getting the pattern.",
        ],
        "wrong": [
            "Almost — the prepared line goes **{expected}**. You have this.",
            "Not quite. Look for **{expected}** — development before greed.",
            "Hmm. Main line is **{expected}**. Try once more.",
        ],
        "intro": "Jaime smiles. Puzzle mode — find the move that keeps the initiative.",
    },
}


def _load() -> Dict[str, Any]:
    global _GAMBITS
    if _GAMBITS is not None:
        return _GAMBITS
    p = Path(__file__).resolve().parent / "gambits_data.json"
    try:
        _GAMBITS = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        _GAMBITS = {
            "kings_gambit": {
                "name": "King's Gambit", "eco": "C30", "side": "White",
                "idea": "Sacrifice a wing pawn for centre control and rapid development.",
                "moves": ["e4", "e5", "f4"],
                "main_line": ["e4", "e5", "f4", "exf4", "Nf3"],
            },
            "queens_gambit": {
                "name": "Queen's Gambit", "eco": "D06", "side": "White",
                "idea": "Offer the c-pawn to dominate the centre.",
                "moves": ["d4", "d5", "c4"],
                "main_line": ["d4", "d5", "c4", "e6", "Nc3", "Nf6"],
            },
            "evans_gambit": {
                "name": "Evans Gambit", "eco": "C51", "side": "White",
                "idea": "Sacrifice a wing pawn for tempi against Black's king.",
                "moves": ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "b4"],
                "main_line": ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "b4", "Bxb4", "c3"],
            },
            "danish": {
                "name": "Danish Gambit", "eco": "C21", "side": "White",
                "idea": "Open lines fast with pawn sacrifices.",
                "moves": ["e4", "e5", "d4", "exd4", "c3"],
                "main_line": ["e4", "e5", "d4", "exd4", "c3", "dxc3", "Bc4"],
            },
        }
    return _GAMBITS


def _distractors(expected: str, line: list, rng: random.Random) -> list:
    pool = [
        "Nf3", "Nc3", "Bc4", "Bb5", "d4", "c4", "f4", "b4", "a3", "h3",
        "O-O", "Qh5", "Qf3", "d3", "c3", "e5", "exd5", "Bxf7+", "Ng5",
    ]
    opts = [expected]
    for m in pool:
        if m != expected and m not in opts:
            opts.append(m)
        if len(opts) >= 4:
            break
    for m in line:
        if m != expected and m not in opts and len(opts) < 4:
            opts.append(m)
    rng.shuffle(opts)
    if expected not in opts[:4]:
        opts = [expected] + [x for x in opts if x != expected]
    return opts[:4]


def render_gambit_trainer(st, ss) -> None:
    st.markdown("### Gambit Puzzle")
    st.caption("Coach-led \u00b7 like Puzzle of the Day \u00b7 find the move")

    data = _load()
    if not data:
        st.warning("No gambits loaded.")
        return

    coach_names = list(COACHES.keys())
    c1, c2 = st.columns(2)
    with c1:
        coach = st.selectbox("Coach", coach_names, key="gambit_coach")
    with c2:
        keys = list(data.keys())
        choice = st.selectbox(
            "Gambit",
            keys,
            format_func=lambda k: "%s (%s)" % (data[k].get("name", k), data[k].get("eco", "")),
            key="gambit_pick",
        )

    g = data[choice]
    line = list(g.get("main_line") or g.get("moves") or [])
    coach_meta = COACHES[coach]

    st.markdown("**" + g.get("name", choice) + "** \u00b7 " + str(g.get("side", "")) + " \u00b7 ECO " + str(g.get("eco", "")))
    st.info(g.get("idea") or "")
    st.caption(coach_meta["intro"])

    if "gambit_idx" not in ss:
        ss["gambit_idx"] = 0
    if "gambit_id" not in ss:
        ss["gambit_id"] = choice
    if "gambit_coach_seed" not in ss:
        ss["gambit_coach_seed"] = random.randint(1, 10**9)
    if ss.get("gambit_id") != choice:
        ss["gambit_id"] = choice
        ss["gambit_idx"] = 0
        ss["gambit_coach_seed"] = random.randint(1, 10**9)

    idx = int(ss.get("gambit_idx") or 0)
    if not line:
        st.caption("No line for this entry.")
        return

    if idx >= len(line):
        st.success(coach + ": Line complete. Well trained.")
        if st.button("New puzzle run", key="gambit_reset"):
            ss["gambit_idx"] = 0
            ss["gambit_coach_seed"] = random.randint(1, 10**9)
            st.rerun()
        return

    so_far = " ".join(line[:idx]) if idx else "(starting position)"
    expected = line[idx]
    st.markdown("**Position after:** `" + so_far + "`")
    st.markdown("**Find move " + str(idx + 1) + "** \u2014 " + coach + " is watching.")

    rng = random.Random(int(ss["gambit_coach_seed"]) + idx * 13)
    opts = _distractors(expected, line, rng)
    if opts and opts[0] == expected and len(opts) > 1:
        for _ in range(5):
            rng.shuffle(opts)
            if opts[0] != expected:
                break

    mode = st.radio("Answer mode", ["Multiple choice", "Type SAN"], horizontal=True, key="gambit_mode")
    guess = ""
    if mode == "Multiple choice":
        guess = st.radio("Candidate moves", opts, key="gambit_mc_%d_%s" % (idx, ss["gambit_coach_seed"]))
    else:
        guess = st.text_input("Your move (SAN)", key="gambit_san_%d" % idx, placeholder="e.g. Nf3")

    if st.button("Submit move", key="gambit_submit_%d" % idx, type="primary"):
        def norm(s):
            return (s or "").strip().replace("0-0-0", "O-O-O").replace("0-0", "O-O")

        if norm(guess) == norm(expected):
            msg = rng.choice(coach_meta["correct"]).format(move=expected, expected=expected)
            st.success(coach + ": " + msg)
            ss["gambit_idx"] = idx + 1
            st.rerun()
        else:
            msg = rng.choice(coach_meta["wrong"]).format(move=guess, expected=expected)
            st.error(coach + ": " + msg)

    with st.expander("Show full main line"):
        st.code(" ".join(line))
