"""Meridium Chess Gambit Trainer."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_GAMBITS: Optional[Dict[str, Any]] = None


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
                "name": "King's Gambit",
                "eco": "C30",
                "side": "White",
                "idea": "Sacrifice a wing pawn for centre control and rapid development.",
                "moves": ["e4", "e5", "f4"],
                "main_line": ["e4", "e5", "f4", "exf4", "Nf3"],
            },
            "queens_gambit": {
                "name": "Queen's Gambit",
                "eco": "D06",
                "side": "White",
                "idea": "Offer the c-pawn to dominate the centre.",
                "moves": ["d4", "d5", "c4"],
                "main_line": ["d4", "d5", "c4", "e6", "Nc3", "Nf6"],
            },
            "evans_gambit": {
                "name": "Evans Gambit",
                "eco": "C51",
                "side": "White",
                "idea": "Sacrifice a wing pawn for tempi against Black's king.",
                "moves": ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "b4"],
                "main_line": ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "b4", "Bxb4", "c3"],
            },
        }
    return _GAMBITS


def list_gambits(side=None) -> List[Tuple[str, dict]]:
    data = _load()
    out = [(k, g) for k, g in data.items() if not side or g.get("side") == side]
    return sorted(out, key=lambda x: x[1].get("name") or x[0])


def render_gambit_trainer(st, ss) -> None:
    st.markdown("### Gambit Academy")
    st.caption("Learn the ideas, drill the main line")
    try:
        data = _load()
    except Exception as e:
        st.error("Could not load gambit catalogue: " + str(e))
        return
    if not data:
        st.warning("No gambits available.")
        return
    side = st.radio("Side", ["All", "White", "Black"], horizontal=True, key="gambit_side_f")
    items = list_gambits(None if side == "All" else side)
    if not items:
        st.info("No gambits for that side filter.")
        return
    names = {k: g.get("name", k) for k, g in items}
    keys = list(names.keys())
    choice = st.selectbox(
        "Gambit",
        keys,
        format_func=lambda k: "%s (%s)" % (names.get(k, k), data.get(k, {}).get("eco", "")),
    )
    g = data.get(choice) or {}
    st.markdown("**%s** \u00b7 %s \u00b7 **%s**" % (g.get("name", choice), g.get("eco", ""), g.get("side", "")))
    st.info(g.get("idea") or "")
    st.markdown("**Core moves**")
    st.code(" ".join(g.get("moves") or []), language=None)
    line = g.get("main_line") or g.get("moves") or []
    st.markdown("**Main line drill**")
    st.code(" ".join(line), language=None)
    if "gambit_idx" not in ss:
        ss["gambit_idx"] = 0
    if "gambit_id" not in ss:
        ss["gambit_id"] = choice
    if ss.get("gambit_id") != choice:
        ss["gambit_id"] = choice
        ss["gambit_idx"] = 0
    idx = int(ss.get("gambit_idx") or 0)
    if not line:
        st.caption("No drill line for this entry.")
        return
    if idx >= len(line):
        st.success("Line complete.")
        if st.button("Reset drill", key="gambit_reset"):
            ss["gambit_idx"] = 0
            st.rerun()
        return
    so_far = " ".join(line[:idx]) if idx else "(start)"
    st.caption("After: " + so_far)
    expected = line[idx]
    guess = st.text_input(
        "Move %d (SAN)" % (idx + 1),
        key="gambit_guess_%s_%d" % (choice, idx),
        placeholder="e.g. Nf3",
    )
    if st.button("Check move", key="gambit_check_%d" % idx):
        def norm(s):
            return (s or "").strip().replace("0-0-0", "O-O-O").replace("0-0", "O-O")
        if norm(guess) == norm(expected):
            ss["gambit_idx"] = idx + 1
            st.success("Correct: " + expected)
            st.rerun()
        else:
            st.error("Main line continues with **%s**" % expected)
