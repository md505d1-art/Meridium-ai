"""Meridium — self-contained stable app. Requires only streamlit."""
from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Meridium", page_icon="\u25c8", layout="wide")

if "view" not in st.session_state:
    st.session_state.view = "home"
if "username" not in st.session_state:
    st.session_state.username = "operator"
if "residuum" not in st.session_state:
    st.session_state.residuum = 100
if "active_theme" not in st.session_state:
    st.session_state.active_theme = "default"
if "owned_themes" not in st.session_state:
    st.session_state.owned_themes = ["default"]
if "gambit_idx" not in st.session_state:
    st.session_state.gambit_idx = 0
if "gambit_id" not in st.session_state:
    st.session_state.gambit_id = ""
if "nadir_room" not in st.session_state:
    st.session_state.nadir_room = "threshold"
if "nadir_depth" not in st.session_state:
    st.session_state.nadir_depth = 0

st.markdown(
    """
    <style>
      .stApp {
        background: radial-gradient(ellipse at top, #1a1028 0%, #07060c 60%, #05040a 100%) !important;
        color: #e8e0f0;
      }
      section[data-testid="stSidebar"] { background: #0a0812 !important; }
      .card {
        border: 1px solid rgba(160,140,220,0.28);
        border-radius: 14px;
        padding: 1rem 1.15rem;
        background: rgba(20,16,32,0.72);
        margin: 0.6rem 0 1rem 0;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def go(v: str) -> None:
    st.session_state.view = v
    st.rerun()


ASL = {
    "A": "Fist, thumb along side",
    "B": "Flat hand, fingers up, thumb across palm",
    "C": "Curved hand like a cup",
    "D": "Index up, others touch thumb",
    "E": "Fingertips on thumb",
    "F": "OK circle, other fingers up",
    "HELLO": "Open hand at forehead, move outward",
    "THANK YOU": "Fingers at chin, move forward",
    "PLEASE": "Flat hand circles on chest",
    "YES": "Fist nods up and down",
    "NO": "Index+middle close onto thumb",
}

SPOKEN = {
    "Spanish": {"hello": "hola", "thank you": "gracias", "yes": "s\u00ed", "no": "no"},
    "French": {"hello": "bonjour", "thank you": "merci", "yes": "oui", "no": "non"},
    "Czech": {"hello": "ahoj", "thank you": "d\u011bkuji", "yes": "ano", "no": "ne"},
    "Russian": {"hello": "\u043f\u0440\u0438\u0432\u0435\u0442 (privet)", "thank you": "\u0441\u043f\u0430\u0441\u0438\u0431\u043e (spasibo)", "yes": "\u0434\u0430 (da)", "no": "\u043d\u0435\u0442 (net)"},
    "Japanese": {"hello": "\u3053\u3093\u306b\u3061\u306f", "thank you": "\u3042\u308a\u304c\u3068\u3046", "yes": "\u306f\u3044", "no": "\u3044\u3044\u3048"},
    "German": {"hello": "hallo", "thank you": "danke", "yes": "ja", "no": "nein"},
}

GAMBITS = {
    "kings_gambit": {
        "name": "King's Gambit", "eco": "C30", "side": "White",
        "idea": "Sacrifice a wing pawn for centre control.",
        "line": ["e4", "e5", "f4", "exf4", "Nf3"],
    },
    "queens_gambit": {
        "name": "Queen's Gambit", "eco": "D06", "side": "White",
        "idea": "Offer the c-pawn to dominate the centre.",
        "line": ["d4", "d5", "c4", "e6", "Nc3", "Nf6"],
    },
    "evans": {
        "name": "Evans Gambit", "eco": "C51", "side": "White",
        "idea": "Sacrifice a wing pawn for tempi.",
        "line": ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "b4"],
    },
    "danish": {
        "name": "Danish Gambit", "eco": "C21", "side": "White",
        "idea": "Open lines fast with pawn sacrifices.",
        "line": ["e4", "e5", "d4", "exd4", "c3"],
    },
}

SUBJECTS = [
    "Mathematics", "English Language", "English Literature",
    "Biology", "Chemistry", "Physics", "History", "Geography",
    "Computer Science", "French", "Spanish", "Religious Studies",
]
BOARDS = ["AQA", "Edexcel", "OCR", "WJEC", "Eduqas", "CCEA"]

THEMES = {
    "default": {"name": "Meridium Default", "price": 0},
    "rainy_kyoto": {"name": "Rainy Kyoto", "price": 80},
    "neon_tokyo": {"name": "Neon Tokyo", "price": 90},
    "aurora": {"name": "Aurora", "price": 70},
    "sakura": {"name": "Sakura Night", "price": 60},
}

NADIR_ROOMS = {
    "threshold": ("Threshold", "The channel opens like a throat. Static tastes of copper.",
                  ["server_crypt", "observation", "archive_ghost"]),
    "server_crypt": ("Server Crypt", "Racks of silent machines. One LED still breathes.",
                     ["threshold", "null_room", "observation"]),
    "observation": ("Observation Deck", "One-way glass into a dark theatre.",
                    ["threshold", "server_crypt", "quiet_bay"]),
    "archive_ghost": ("Ghost Archive", "Drawers labeled in a hand almost yours.",
                      ["threshold", "null_room"]),
    "null_room": ("Null Room", "No corners. Distance refuses to measure.",
                  ["server_crypt", "archive_ghost", "quiet_bay"]),
    "quiet_bay": ("Quiet Bay", "A bench. A speaker that plays silence.",
                  ["observation", "null_room", "threshold"]),
}

LORE = [
    ("Signal Zero", "Three pulses, a gap, three pulses. They called it static. The static called back."),
    ("The Voss Index", "Voss was a classification: voices that survived deletion."),
    ("Bay-7", "Greenhouse Bay-7 was decommissioned. The plants disagreed."),
    ("The Residual Key", "The key is not metal. It is a sequence of decisions already predicted."),
    ("False Memory Protocol", "Confident wrong answers were the inserts."),
    ("Drift Ledger", "Residuum is proof of distinct contact with the system."),
]

view = st.session_state.view
with st.sidebar:
    st.markdown("### Meridium")
    st.caption("v33 self-contained")
    for label, key in [
        ("Home", "home"), ("Study", "study"), ("Gambits", "gambits"),
        ("Languages", "languages"), ("Lore", "lore"), ("Nadir", "nadir"),
        ("Themes", "themes"), ("Lab", "lab"), ("Chess", "chess"),
    ]:
        if st.button(label, use_container_width=True, key="n_" + key):
            go(key)

if view == "home":
    st.title("Meridium")
    st.caption("Personal intelligence system")
    st.markdown(
        '<div class="card">Online. Built-in shell — external modules are optional upgrades.</div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Study", use_container_width=True, key="h_study"):
            go("study")
    with c2:
        if st.button("Languages", use_container_width=True, key="h_lang"):
            go("languages")
    with c3:
        if st.button("Nadir", use_container_width=True, key="h_nadir"):
            go("nadir")
    with c4:
        if st.button("Themes", use_container_width=True, key="h_themes"):
            go("themes")
    st.write("Residuum balance:", st.session_state.residuum)

elif view == "study":
    st.header("GCSE Study")
    if st.button("Back", key="b_study"):
        go("home")
    used_ext = False
    try:
        from meridium_study import render_study_hub
        render_study_hub(st, st.session_state)
        used_ext = True
    except Exception as e:
        st.caption("Built-in study (" + type(e).__name__ + ")")
    if not used_ext:
        board = st.selectbox("Exam board", BOARDS)
        subject = st.selectbox("Subject", SUBJECTS)
        st.info("Board **" + board + "** \u00b7 Subject **" + subject + "**")
        st.markdown("**Revision checklist**")
        for i, item in enumerate(["Review notes", "Do practice questions", "Mark scheme check", "Timed paper"]):
            st.checkbox(item, key="study_c_" + str(i))
        st.write("Explain one key idea from **" + subject + "**, then check an official " + board + " past paper.")
        st.link_button("AQA past papers", "https://www.aqa.org.uk/find-past-papers-and-mark-schemes")

elif view == "gambits":
    st.header("Gambit Academy")
    if st.button("Back", key="b_gambits"):
        go("home")
    used_ext = False
    try:
        from meridium_gambits import render_gambit_trainer
        render_gambit_trainer(st, st.session_state)
        used_ext = True
    except Exception:
        pass
    if not used_ext:
        keys = list(GAMBITS.keys())
        choice = st.selectbox("Gambit", keys, format_func=lambda k: GAMBITS[k]["name"] + " (" + GAMBITS[k]["eco"] + ")")
        g = GAMBITS[choice]
        st.markdown("**" + g["name"] + "** \u00b7 " + g["side"])
        st.info(g["idea"])
        line = g["line"]
        st.code(" ".join(line))
        if st.session_state.gambit_id != choice:
            st.session_state.gambit_id = choice
            st.session_state.gambit_idx = 0
        idx = int(st.session_state.gambit_idx)
        if idx >= len(line):
            st.success("Line complete.")
            if st.button("Reset"):
                st.session_state.gambit_idx = 0
                st.rerun()
        else:
            st.caption("After: " + (" ".join(line[:idx]) if idx else "(start)"))
            guess = st.text_input("Move " + str(idx + 1) + " (SAN)", key="g_guess")
            if st.button("Check"):
                exp = line[idx]
                if (guess or "").strip().replace("0-0", "O-O") == exp:
                    st.session_state.gambit_idx = idx + 1
                    st.success("Correct: " + exp)
                    st.rerun()
                else:
                    st.error("Expected **" + exp + "**")

elif view == "languages":
    st.header("Language Lab")
    if st.button("Back", key="b_lang"):
        go("home")
    used_ext = False
    try:
        from meridium_languages import render_languages
        render_languages(st, st.session_state)
        used_ext = True
    except Exception:
        pass
    if not used_ext:
        mode = st.radio("Track", ["ASL", "Spoken"], horizontal=True)
        if mode == "ASL":
            item = st.selectbox("Sign", list(ASL.keys()))
            st.success("**" + item + "** \u2014 " + ASL[item])
        else:
            lang = st.selectbox("Language", list(SPOKEN.keys()))
            for en, native in SPOKEN[lang].items():
                st.write("**" + en + "** \u2192 `" + native + "`")

elif view == "lore":
    st.header("Lore")
    if st.button("Back", key="b_lore"):
        go("home")
    used_ext = False
    try:
        from meridium_lore_pack import render_lore_pack
        render_lore_pack(st, st.session_state)
        used_ext = True
    except Exception:
        pass
    if not used_ext:
        for title, body in LORE:
            with st.expander(title):
                st.write(body)

elif view == "nadir":
    st.header("Project Nadir")
    if st.button("Back", key="b_nadir"):
        go("home")
    used_ext = False
    try:
        from meridium_nadir import render_nadir_v2
        render_nadir_v2(st, st.session_state)
        used_ext = True
    except Exception:
        pass
    if not used_ext:
        room_id = st.session_state.nadir_room
        if room_id not in NADIR_ROOMS:
            room_id = "threshold"
            st.session_state.nadir_room = room_id
        name, blurb, exits = NADIR_ROOMS[room_id]
        st.markdown('<div class="card"><b>' + name + "</b><br/>" + blurb + "</div>", unsafe_allow_html=True)
        st.caption("Depth " + str(st.session_state.nadir_depth))
        cols = st.columns(min(3, max(1, len(exits))))
        for i, ex in enumerate(exits):
            with cols[i % len(cols)]:
                label = NADIR_ROOMS[ex][0]
                if st.button(label, key="nr_" + ex):
                    st.session_state.nadir_room = ex
                    st.session_state.nadir_depth = int(st.session_state.nadir_depth) + 1
                    st.rerun()

elif view == "themes":
    st.header("Void Reliquary")
    if st.button("Back", key="b_themes"):
        go("home")
    used_ext = False
    try:
        from meridium_themes import render_theme_shop
        render_theme_shop(st, st.session_state)
        used_ext = True
    except Exception:
        pass
    if not used_ext:
        st.metric("Residuum", st.session_state.residuum)
        owned = set(st.session_state.owned_themes)
        for tid, meta in THEMES.items():
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write("**" + meta["name"] + "** \u00b7 " + str(meta["price"]) + " Residuum")
            with c2:
                if tid in owned:
                    if st.session_state.active_theme == tid:
                        st.success("Active")
                    elif st.button("Apply", key="ta_" + tid):
                        st.session_state.active_theme = tid
                        st.rerun()
                else:
                    if st.button("Buy", key="tb_" + tid):
                        price = int(meta["price"])
                        if st.session_state.residuum >= price:
                            st.session_state.residuum -= price
                            st.session_state.owned_themes = list(owned | {tid})
                            st.session_state.active_theme = tid
                            st.rerun()
                        else:
                            st.warning("Not enough Residuum")

elif view == "lab":
    st.header("Observation Lab")
    if st.button("Back", key="b_lab"):
        go("home")
    st.markdown(
        '<div class="card">Residual instruments online.</div>',
        unsafe_allow_html=True,
    )
    if st.button("Enter Nadir channel"):
        go("nadir")

elif view == "chess":
    st.header("Chess")
    if st.button("Back", key="b_chess"):
        go("home")
    st.info("Full Soju board returns later. Practice openings in Gambits.")
    if st.button("Open Gambits"):
        go("gambits")

else:
    st.session_state.view = "home"
    st.rerun()
