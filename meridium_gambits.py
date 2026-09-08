"""Meridium Chess Gambit Trainer."""
from __future__ import annotations
import json
from pathlib import Path

def _load():
    p = Path(__file__).resolve().parent / "gambits_data.json"
    return json.loads(p.read_text(encoding="utf-8"))

GAMBITS = _load()

def list_gambits(side=None):
    out = [(k, g) for k, g in GAMBITS.items() if not side or g.get("side") == side]
    return sorted(out, key=lambda x: x[1]["name"])

def render_gambit_trainer(st, ss) -> None:
    st.markdown("### \u265f Gambit Academy")
    st.caption("Learn the ideas, drill the main line \u00b7 major gambits catalogue")
    side = st.radio("Side", ["All", "White", "Black"], horizontal=True, key="gambit_side_f")
    items = list_gambits(None if side == "All" else side)
    names = {k: g["name"] for k, g in items}
    choice = st.selectbox("Gambit", list(names.keys()), format_func=lambda k: f"{names[k]} ({GAMBITS[k].get('eco','')})")
    g = GAMBITS[choice]
    st.markdown(f"**{g['name']}** \u00b7 {g.get('eco','')} \u00b7 **{g['side']}**")
    st.info(g["idea"])
    st.markdown("**Core moves**")
    st.code(" ".join(g.get("moves") or []), language=None)
    line = g.get("main_line") or g.get("moves") or []
    st.markdown("**Main line drill**")
    st.code(" ".join(line), language=None)
    ss.setdefault("gambit_idx", 0)
    ss.setdefault("gambit_id", choice)
    if ss.get("gambit_id") != choice:
        ss["gambit_id"] = choice
        ss["gambit_idx"] = 0
    idx = int(ss.get("gambit_idx") or 0)
    if idx >= len(line):
        st.success("Line complete.")
        if st.button("Reset drill", key="gambit_reset"):
            ss["gambit_idx"] = 0
            st.rerun()
        return
    so_far = " ".join(line[:idx]) if idx else "(start)"
    st.caption(f"After: {so_far}")
    expected = line[idx]
    guess = st.text_input(f"Move {idx+1} (SAN)", key=f"gambit_guess_{choice}_{idx}", placeholder="e.g. Nf3")
    if st.button("Check move", key=f"gambit_check_{idx}"):
        norm = lambda s: (s or "").strip().replace("0-0-0", "O-O-O").replace("0-0", "O-O")
        if norm(guess) == norm(expected):
            ss["gambit_idx"] = idx + 1
            st.success(f"Correct: {expected}")
            st.rerun()
        else:
            st.error(f"Main line continues with **{expected}**")
