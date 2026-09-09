"""Meridium Gambit Trainer — playable board + coach guidance."""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import chess
except Exception:
    chess = None

_GAMBITS = None

COACHES = {
    "Soju": {
        "correct": [
            "Yes — {move}. Hold the centre.",
            "Good. {move} is the idea.",
            "Exact. Continue.",
        ],
        "wrong": [
            "Not that. Look for **{expected}**.",
            "The line wants **{expected}**.",
            "Try **{expected}**.",
        ],
        "hint": "Soju highlights the key squares.",
        "intro": "Soju sets the pieces. Play the main line on the board.",
    },
    "Voss": {
        "correct": ["Residual agrees. {move}.", "Signal clean — {move}.", "Yes. {move}."],
        "wrong": ["Static. Play **{expected}**.", "Divergent. **{expected}**.", "No. **{expected}**."],
        "hint": "Voss marks the path without words.",
        "intro": "Voss watches. Make the move that resonates.",
    },
    "Callaghan": {
        "correct": ["Fine. {move}.", "Yes — {move}.", "That is it. {move}."],
        "wrong": ["Wrong. **{expected}**.", "No. **{expected}**.", "Play **{expected}**."],
        "hint": "One clean move.",
        "intro": "Callaghan waits. Play it on the board.",
    },
    "Jaime": {
        "correct": ["Nice! {move}.", "Well spotted — {move}.", "Yes! {move}."],
        "wrong": [
            "Almost — **{expected}**.",
            "Not quite. **{expected}** keeps the initiative.",
            "Try **{expected}**.",
        ],
        "hint": "Jaime points at activity over material.",
        "intro": "Jaime sets the puzzle. Make the move on the board.",
    },
}

PIECES = {
    "K": "\u2654", "Q": "\u2655", "R": "\u2656", "B": "\u2657", "N": "\u2658", "P": "\u2659",
    "k": "\u265a", "q": "\u265b", "r": "\u265c", "b": "\u265d", "n": "\u265e", "p": "\u265f",
}
FILES = "abcdefgh"
RANKS = "12345678"


def _load():
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
                "idea": "Sacrifice a wing pawn for centre control.",
                "main_line": ["e4", "e5", "f4", "exf4", "Nf3"],
            },
            "queens_gambit": {
                "name": "Queen's Gambit", "eco": "D06", "side": "White",
                "idea": "Offer the c-pawn to dominate the centre.",
                "main_line": ["d4", "d5", "c4", "e6", "Nc3", "Nf6"],
            },
            "evans_gambit": {
                "name": "Evans Gambit", "eco": "C51", "side": "White",
                "idea": "Sacrifice a wing pawn for tempi.",
                "main_line": ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "b4", "Bxb4", "c3"],
            },
            "danish": {
                "name": "Danish Gambit", "eco": "C21", "side": "White",
                "idea": "Open lines fast with pawn sacrifices.",
                "main_line": ["e4", "e5", "d4", "exd4", "c3", "dxc3", "Bc4"],
            },
        }
    return _GAMBITS


def _board_at(line, ply):
    board = chess.Board()
    for san in line[:ply]:
        try:
            board.push_san(san)
        except Exception:
            break
    return board


def _board_html(board, highlight=None):
    hl = set(highlight or [])
    rows = []
    for rank in range(7, -1, -1):
        cells = [
            '<td style="width:16px;font-size:11px;color:#9ab;text-align:center;">%s</td>'
            % RANKS[rank]
        ]
        for file in range(8):
            sq = chess.square(file, rank)
            name = chess.square_name(sq)
            light = (rank + file) % 2 == 1
            bg = "#ebecd0" if light else "#779556"
            if name in hl:
                bg = "#f6f669"
            piece = ""
            p = board.piece_at(sq)
            if p:
                piece = PIECES.get(p.symbol(), p.symbol())
            cells.append(
                '<td style="width:44px;height:44px;text-align:center;vertical-align:middle;'
                'font-size:30px;background:%s;border:1px solid #2a2a2a;">%s</td>'
                % (bg, piece)
            )
        rows.append("<tr>" + "".join(cells) + "</tr>")
    footer = (
        "<tr><td></td>"
        + "".join(
            '<td style="text-align:center;font-size:11px;color:#9ab;">%s</td>' % f
            for f in FILES
        )
        + "</tr>"
    )
    return (
        '<div style="overflow-x:auto"><table style="border-collapse:collapse;margin:8px auto;">'
        + "".join(rows)
        + footer
        + "</table></div>"
    )


def _move_squares(board, san):
    try:
        mv = board.parse_san(san)
        return [chess.square_name(mv.from_square), chess.square_name(mv.to_square)]
    except Exception:
        return []


def _legal_sans(board):
    out = []
    for mv in board.legal_moves:
        try:
            out.append(board.san(mv))
        except Exception:
            pass
    return sorted(set(out), key=lambda s: (len(s), s))


def _norm(s):
    return (s or "").strip().replace("0-0-0", "O-O-O").replace("0-0", "O-O")


def _student_side(gambit_side: str):
    return chess.WHITE if (gambit_side or "White").lower().startswith("w") else chess.BLACK


def _auto_reply(ss, line, ply, student):
    while ply < len(line):
        board = _board_at(line, ply)
        if board.turn == student:
            break
        ply += 1
        ss["gb_ply"] = ply
    return ply


def render_gambit_trainer(st, ss) -> None:
    st.markdown("### Gambit Board")
    st.caption("Playable board \u00b7 coach highlights \u00b7 follow the line")

    if chess is None:
        st.error("python-chess missing — add it to requirements and reboot.")
        return

    data = _load()
    c1, c2, c3 = st.columns(3)
    with c1:
        coach = st.selectbox("Coach", list(COACHES.keys()), key="gb_coach")
    with c2:
        keys = list(data.keys())
        choice = st.selectbox(
            "Gambit",
            keys,
            format_func=lambda k: "%s (%s)" % (data[k].get("name", k), data[k].get("eco", "")),
            key="gb_pick",
        )
    with c3:
        show_hint = st.checkbox("Highlight coach move", value=True, key="gb_hint")

    g = data[choice]
    line = list(g.get("main_line") or g.get("moves") or [])
    meta = COACHES[coach]
    student = _student_side(str(g.get("side") or "White"))

    st.markdown(
        "**%s** \u00b7 %s \u00b7 ECO %s"
        % (g.get("name", choice), g.get("side", ""), g.get("eco", ""))
    )
    st.info(g.get("idea") or "")
    st.caption(meta["intro"])

    if ss.get("gb_id") != choice:
        ss["gb_id"] = choice
        ss["gb_ply"] = 0
        ss["gb_msg"] = ""
    ply = int(ss.get("gb_ply") or 0)
    if ply < len(line):
        board_chk = _board_at(line, ply)
        if board_chk.turn != student:
            ply = _auto_reply(ss, line, ply, student)
            ply = int(ss.get("gb_ply") or ply)

    board = _board_at(line, ply)

    if ply >= len(line):
        st.success(coach + ": Line complete. Well trained.")
        st.markdown(_board_html(board), unsafe_allow_html=True)
        if st.button("Run again", key="gb_reset"):
            ss["gb_ply"] = 0
            ss["gb_msg"] = ""
            st.rerun()
        with st.expander("Full main line"):
            st.code(" ".join(line))
        return

    expected = line[ply]
    hl = _move_squares(board, expected) if show_hint else []
    st.markdown(_board_html(board, highlight=hl), unsafe_allow_html=True)

    side = "White" if board.turn == chess.WHITE else "Black"
    st.markdown(
        "**Your move %d / %d** \u00b7 %s to play \u00b7 Coach **%s**"
        % (ply + 1, len(line), side, coach)
    )
    if show_hint and hl:
        st.caption(meta["hint"] + " \u00b7 " + " \u2192 ".join(hl) + " (" + expected + ")")

    if ss.get("gb_msg"):
        st.write(ss["gb_msg"])

    def commit_correct():
        msg = random.choice(meta["correct"]).format(move=expected, expected=expected)
        ss["gb_msg"] = coach + ": " + msg
        ss["gb_ply"] = ply + 1
        _auto_reply(ss, line, int(ss["gb_ply"]), student)

    def try_san(san):
        try:
            board.parse_san(san)
        except Exception:
            st.error("Illegal move in this position.")
            return
        if _norm(san) == _norm(expected):
            commit_correct()
            st.rerun()
        else:
            msg = random.choice(meta["wrong"]).format(move=san, expected=expected)
            ss["gb_msg"] = coach + ": " + msg
            st.error(ss["gb_msg"])

    t1, t2, t3 = st.tabs(["Click squares", "Legal moves", "Type SAN"])

    with t1:
        st.caption("Choose **from** and **to** squares, then play.")
        sqs = [f + r for r in RANKS for f in FILES]
        a, b = st.columns(2)
        with a:
            fr = st.selectbox("From", [""] + sqs, key="gb_from")
        with b:
            to = st.selectbox("To", [""] + sqs, key="gb_to")
        if st.button("Play on board", key="gb_go_sq", type="primary"):
            if not fr or not to:
                st.warning("Pick both squares.")
            else:
                uci = fr + to
                try:
                    mv = chess.Move.from_uci(uci)
                    if (
                        board.piece_at(mv.from_square)
                        and board.piece_at(mv.from_square).piece_type == chess.PAWN
                        and chess.square_rank(mv.to_square) in (0, 7)
                        and mv.promotion is None
                    ):
                        mv = chess.Move(mv.from_square, mv.to_square, promotion=chess.QUEEN)
                    san = board.san(mv)
                    try_san(san)
                except Exception:
                    try:
                        mv = chess.Move.from_uci(uci + "q")
                        try_san(board.san(mv))
                    except Exception as e:
                        st.error("Cannot play that: " + str(e))

    with t2:
        legal = _legal_sans(board)
        pick = st.selectbox("Legal move", legal, key="gb_legal")
        if st.button("Play selected", key="gb_go_legal", type="primary"):
            try_san(pick)

    with t3:
        typed = st.text_input("SAN", key="gb_san", placeholder="e.g. Nf3")
        if st.button("Submit SAN", key="gb_go_san", type="primary"):
            try_san(typed)

    with st.expander("Coach demonstrates"):
        st.write("%s plays **%s** here." % (coach, expected))
        if hl:
            st.caption("Squares: " + " \u2192 ".join(hl))
        if st.button("Play coach move for me", key="gb_coach_do"):
            commit_correct()
            st.rerun()

    with st.expander("Line progress"):
        st.code(" ".join(line[:ply]) if ply else "(start)")
        st.caption("Full: " + " ".join(line))
