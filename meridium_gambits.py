"""Meridium Gambit Trainer — play board styled like Play mode + coach."""
from __future__ import annotations

import json
import random
from pathlib import Path

try:
    import chess
except Exception:
    chess = None

_GAMBITS = None

COACHES = {
    "Soju": {
        "correct": ["Yes — {move}. Hold the centre.", "Good. {move} is the idea.", "Exact. Continue."],
        "wrong": ["Not that. Look for **{expected}**.", "The line wants **{expected}**.", "Try **{expected}**."],
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
        "wrong": ["Almost — **{expected}**.", "Not quite. **{expected}**.", "Try **{expected}**."],
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


def _move_squares(board, san):
    try:
        mv = board.parse_san(san)
        return [chess.square_name(mv.from_square), chess.square_name(mv.to_square)]
    except Exception:
        return []


def _legal_targets(board, from_sq: str):
    out = set()
    try:
        fr = chess.parse_square(from_sq)
    except Exception:
        return out
    for mv in board.legal_moves:
        if mv.from_square == fr:
            out.add(chess.square_name(mv.to_square))
    return out


def _board_html(board, selected=None, moves=None, highlight=None):
    selected = selected or ""
    moves = set(moves or [])
    highlight = set(highlight or [])
    squares = []
    for rank in range(7, -1, -1):
        for file in range(8):
            sq = chess.square(file, rank)
            name = chess.square_name(sq)
            light = (rank + file) % 2 == 1
            cls = "sq light" if light else "sq dark"
            if name == selected:
                cls += " sel"
            if name in moves:
                cls += " mov"
            if name in highlight:
                cls += " last"
            p = board.piece_at(sq)
            glyph = PIECES.get(p.symbol(), "") if p else ""
            squares.append('<div class="%s" data-sq="%s">%s</div>' % (cls, name, glyph))

    css = """
    <style>
      .gb-wrap { max-width: 440px; margin: 10px auto 6px; }
      .gb-board {
        width: 100%;
        aspect-ratio: 1 / 1;
        display: grid;
        grid-template-columns: repeat(8, 1fr);
        grid-template-rows: repeat(8, 1fr);
        border: 2px solid rgba(167,139,250,0.4);
        border-radius: 10px;
        overflow: hidden;
        user-select: none;
        box-shadow: 0 16px 40px rgba(0,0,0,0.35);
      }
      .gb-board .sq {
        display: flex; align-items: center; justify-content: center;
        font-size: clamp(22px, 5.5vw, 34px);
        line-height: 1;
        position: relative;
      }
      .gb-board .sq.light { background: #f0d9b5; }
      .gb-board .sq.dark { background: #b58863; }
      .gb-board .sq.sel { outline: 3px solid #a78bfa; outline-offset: -3px; }
      .gb-board .sq.mov { box-shadow: inset 0 0 0 4px rgba(74,222,128,0.55); }
      .gb-board .sq.last { box-shadow: inset 0 0 0 4px rgba(250,204,21,0.75); }
      .gb-files {
        display: grid; grid-template-columns: repeat(8, 1fr);
        max-width: 440px; margin: 4px auto 0;
        font-size: 11px; color: rgba(200,190,230,0.7); text-align: center;
        font-family: ui-monospace, monospace;
      }
    </style>
    """
    files = "".join("<div>%s</div>" % f for f in FILES)
    return (
        css
        + '<div class="gb-wrap"><div class="gb-board">'
        + "".join(squares)
        + '</div><div class="gb-files">'
        + files
        + "</div></div>"
    )


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
    st.caption("Same board language as Play \u00b7 coach guided main line")

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
        "**%s** \u00b7 %s \u00b7 ECO %s" % (g.get("name", choice), g.get("side", ""), g.get("eco", ""))
    )
    st.info(g.get("idea") or "")
    st.caption(meta["intro"])

    if ss.get("gb_id") != choice:
        ss["gb_id"] = choice
        ss["gb_ply"] = 0
        ss["gb_msg"] = ""
        ss["gb_sel"] = ""
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
            ss["gb_sel"] = ""
            st.rerun()
        with st.expander("Full main line"):
            st.code(" ".join(line))
        return

    expected = line[ply]
    hl = _move_squares(board, expected) if show_hint else []
    sel = ss.get("gb_sel") or ""
    targets = _legal_targets(board, sel) if sel else set()
    st.markdown(
        _board_html(board, selected=sel, moves=targets, highlight=hl),
        unsafe_allow_html=True,
    )

    side = "White" if board.turn == chess.WHITE else "Black"
    st.markdown(
        "**Your move %d / %d** \u00b7 %s \u00b7 Coach **%s**"
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
        ss["gb_sel"] = ""
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

    st.markdown("**Select squares** (same idea as Play: piece, then destination)")
    sqs = [f + r for r in RANKS for f in FILES]
    a, b, c = st.columns([2, 2, 1])
    with a:
        fr = st.selectbox(
            "From",
            [""] + sqs,
            index=([""] + sqs).index(sel) if sel in sqs else 0,
            key="gb_from",
        )
        if fr != sel:
            ss["gb_sel"] = fr
    with b:
        to_opts = [""] + (sorted(targets) if targets else sqs)
        to = st.selectbox("To", to_opts, key="gb_to")
    with c:
        st.write("")
        st.write("")
        if st.button("Play", key="gb_go_sq", type="primary"):
            if not fr or not to:
                st.warning("Pick both squares.")
            else:
                uci = fr + to
                try:
                    mv = chess.Move.from_uci(uci)
                    piece = board.piece_at(mv.from_square)
                    if (
                        piece
                        and piece.piece_type == chess.PAWN
                        and chess.square_rank(mv.to_square) in (0, 7)
                        and mv.promotion is None
                    ):
                        mv = chess.Move(mv.from_square, mv.to_square, promotion=chess.QUEEN)
                    try_san(board.san(mv))
                except Exception:
                    try:
                        try_san(board.san(chess.Move.from_uci(uci + "q")))
                    except Exception as e:
                        st.error("Cannot play that: " + str(e))

    t2, t3 = st.tabs(["Legal moves", "Type SAN"])
    with t2:
        legal = _legal_sans(board)
        pick = st.selectbox("Legal move", legal, key="gb_legal")
        if st.button("Play selected", key="gb_go_legal"):
            try_san(pick)
    with t3:
        typed = st.text_input("SAN", key="gb_san", placeholder="e.g. Nf3")
        if st.button("Submit SAN", key="gb_go_san"):
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
