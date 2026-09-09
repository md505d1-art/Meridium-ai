"""Meridium v37 — self-contained. Study, Languages, Chess+Gambits, Lab lore."""
from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Meridium", page_icon="\u25c8", layout="wide")

defaults = {
    "view": "home",
    "username": "operator",
    "residuum": 100,
    "active_theme": "default",
    "owned_themes": ["default"],
    "gambit_idx": 0,
    "gambit_id": "",
    "nadir_room": "threshold",
    "nadir_depth": 0,
    "lang_xp": 0,
    "lang_hearts": 5,
    "lang_streak": 0,
    "lang_i": 0,
    "lang_course": "Spanish",
    "study_qi": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown(
    """
    <style>
      .stApp {
        background: radial-gradient(ellipse at top, #1a1028 0%, #07060c 55%, #05040a 100%) !important;
        color: #e8e0f0;
      }
      section[data-testid="stSidebar"] { background: #0a0812 !important; }
      .card {
        border: 1px solid rgba(160,140,220,0.3);
        border-radius: 14px;
        padding: 1rem 1.15rem;
        background: rgba(20,16,32,0.75);
        margin: 0.55rem 0 1rem 0;
      }
      .ver { font-size: 0.75rem; opacity: 0.7; letter-spacing: 0.08em; }
    </style>
    """,
    unsafe_allow_html=True,
)


def go(v: str) -> None:
    st.session_state.view = v
    st.rerun()


SUBJECTS = [
    "Mathematics", "English Language", "English Literature",
    "Biology", "Chemistry", "Physics", "History", "Geography",
    "Computer Science", "French", "Spanish", "Religious Studies",
]
BOARDS = ["AQA", "Edexcel", "OCR", "WJEC", "Eduqas", "CCEA"]
TOPICS = {
    "Mathematics": ["Number", "Algebra", "Ratio", "Geometry", "Probability", "Statistics"],
    "Biology": ["Cells", "Organisation", "Infection", "Bioenergetics", "Homeostasis", "Ecology"],
    "Chemistry": ["Atomic structure", "Bonding", "Quantitative", "Rates", "Organic", "Analysis"],
    "Physics": ["Energy", "Electricity", "Forces", "Waves", "Magnetism", "Space"],
}

GAMBITS = {
    "kings": {"name": "King's Gambit", "eco": "C30", "side": "White",
              "idea": "Sacrifice a wing pawn for centre control.",
              "line": ["e4", "e5", "f4", "exf4", "Nf3"]},
    "queens": {"name": "Queen's Gambit", "eco": "D06", "side": "White",
               "idea": "Offer the c-pawn to dominate the centre.",
               "line": ["d4", "d5", "c4", "e6", "Nc3", "Nf6"]},
    "evans": {"name": "Evans Gambit", "eco": "C51", "side": "White",
              "idea": "Sacrifice a wing pawn for tempi.",
              "line": ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "b4"]},
    "danish": {"name": "Danish Gambit", "eco": "C21", "side": "White",
               "idea": "Open lines fast with pawn sacrifices.",
               "line": ["e4", "e5", "d4", "exd4", "c3"]},
}

LESSONS = {
    "Spanish": [("hello", "hola", ["hola", "adios", "gracias", "si"]),
                ("thank you", "gracias", ["gracias", "hola", "no", "si"]),
                ("yes", "s\u00ed", ["s\u00ed", "no", "hola", "gracias"]),
                ("no", "no", ["no", "s\u00ed", "adios", "hola"]),
                ("please", "por favor", ["por favor", "gracias", "hola", "no"])],
    "Czech": [("hello", "ahoj", ["ahoj", "d\u011bkuji", "ano", "ne"]),
              ("thank you", "d\u011bkuji", ["d\u011bkuji", "ahoj", "ano", "ne"]),
              ("yes", "ano", ["ano", "ne", "ahoj", "pros\u00edm"]),
              ("no", "ne", ["ne", "ano", "ahoj", "d\u011bkuji"])],
    "Russian": [("hello", "\u043f\u0440\u0438\u0432\u0435\u0442", ["\u043f\u0440\u0438\u0432\u0435\u0442", "\u0441\u043f\u0430\u0441\u0438\u0431\u043e", "\u0434\u0430", "\u043d\u0435\u0442"]),
                ("thank you", "\u0441\u043f\u0430\u0441\u0438\u0431\u043e", ["\u0441\u043f\u0430\u0441\u0438\u0431\u043e", "\u043f\u0440\u0438\u0432\u0435\u0442", "\u0434\u0430", "\u043d\u0435\u0442"]),
                ("yes", "\u0434\u0430", ["\u0434\u0430", "\u043d\u0435\u0442", "\u043f\u0440\u0438\u0432\u0435\u0442", "\u043f\u043e\u043a\u0430"]),
                ("no", "\u043d\u0435\u0442", ["\u043d\u0435\u0442", "\u0434\u0430", "\u043f\u0440\u0438\u0432\u0435\u0442", "\u0441\u043f\u0430\u0441\u0438\u0431\u043e"])],
    "French": [("hello", "bonjour", ["bonjour", "merci", "oui", "non"]),
               ("thank you", "merci", ["merci", "bonjour", "oui", "non"]),
               ("yes", "oui", ["oui", "non", "merci", "salut"]),
               ("no", "non", ["non", "oui", "bonjour", "merci"])],
    "ASL": [("How do you sign HELLO?", "Open hand at forehead, move outward", None),
            ("How do you sign THANK YOU?", "Fingers at chin, move forward", None),
            ("Letter A?", "Fist, thumb along side", None),
            ("How do you sign YES?", "Fist nods up and down", None)],
}

LORE = [
    ("Signal Zero", "Three pulses, a gap, three pulses. They called it static. The static called back."),
    ("The Voss Index", "Voss was a classification: voices that survived deletion."),
    ("Bay-7", "Greenhouse Bay-7 was decommissioned. The plants disagreed."),
    ("The Residual Key", "The key is not metal. It is a sequence of decisions already predicted."),
    ("False Memory Protocol", "Confident wrong answers were the inserts."),
    ("Drift Ledger", "Residuum is proof of distinct contact with the system."),
]

NADIR = {
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

THEMES = {
    "default": ("Meridium Default", 0),
    "rainy_kyoto": ("Rainy Kyoto", 80),
    "neon_tokyo": ("Neon Tokyo", 90),
    "aurora": ("Aurora", 70),
    "sakura": ("Sakura Night", 60),
}

view = st.session_state.view
with st.sidebar:
    st.markdown("### Meridium")
    st.markdown('<p class="ver">v37 \u00b7 layout fixed</p>', unsafe_allow_html=True)
    for label, key in [
        ("Home", "home"),
        ("Study", "study"),
        ("Languages", "languages"),
        ("Chess", "chess"),
        ("Lab", "lab"),
        ("Nadir", "nadir"),
        ("Themes", "themes"),
    ]:
        if st.button(label, use_container_width=True, key="nav_" + key):
            go(key)
    st.caption("Gambits live inside Chess \u00b7 Lore lives inside Lab / Nadir")

if view == "home":
    st.title("Meridium")
    st.caption("Personal intelligence system \u00b7 v37")
    st.markdown(
        '<div class="card"><b>What is where</b><br/>'
        "\u2022 <b>Study</b> \u2014 GCSE subjects \u0026 boards<br/>"
        "\u2022 <b>Languages</b> \u2014 Duolingo-style XP / hearts<br/>"
        "\u2022 <b>Chess</b> \u2014 Play or <b>Learn gambits</b><br/>"
        "\u2022 <b>Lab / Nadir</b> \u2014 open Lore expanders inside<br/>"
        "\u2022 No Gambits or Lore in the sidebar</div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Study", use_container_width=True, key="h_s"):
            go("study")
    with c2:
        if st.button("Languages", use_container_width=True, key="h_l"):
            go("languages")
    with c3:
        if st.button("Chess", use_container_width=True, key="h_c"):
            go("chess")
    with c4:
        if st.button("Nadir", use_container_width=True, key="h_n"):
            go("nadir")

elif view == "study":
    st.header("GCSE Study")
    if st.button("\u2190 Back", key="b_study"):
        go("home")
    used = False
    try:
        from meridium_study import render_study_hub
        render_study_hub(st, st.session_state)
        used = True
    except Exception:
        pass
    if not used:
        board = st.selectbox("Exam board", BOARDS, key="st_board")
        subject = st.selectbox("Subject", SUBJECTS, key="st_sub")
        st.info(subject + " \u00b7 " + board)
        topics = TOPICS.get(subject) or ["Core topic 1", "Core topic 2", "Core topic 3", "Exam technique"]
        st.markdown("#### Topics")
        for t in topics:
            st.checkbox(t, key="st_" + subject[:4] + "_" + t[:12])
        st.markdown("#### Practice")
        st.write("Explain one idea from **" + subject + "** then check an official paper.")
        st.link_button("AQA past papers", "https://www.aqa.org.uk/find-past-papers-and-mark-schemes")
        st.text_area("Notes", key="st_notes")

elif view == "languages":
    st.header("Language Lab")
    if st.button("\u2190 Back", key="b_lang"):
        go("home")
    used = False
    try:
        from meridium_languages import render_languages
        render_languages(st, st.session_state)
        used = True
    except Exception:
        pass
    if not used:
        c1, c2, c3 = st.columns(3)
        c1.metric("XP", st.session_state.lang_xp)
        h = int(st.session_state.lang_hearts)
        c2.metric("Hearts", "\u2665" * max(0, h) + "\u2661" * max(0, 5 - h))
        c3.metric("Streak", st.session_state.lang_streak)
        course = st.selectbox("Course", list(LESSONS.keys()), key="lg_course")
        pack = LESSONS[course]
        i = int(st.session_state.lang_i) % len(pack)
        prompt, answer, options = pack[i]
        st.progress((i + 1) / len(pack))
        st.markdown("#### Lesson %d / %d" % (i + 1, len(pack)))
        st.info("Translate / answer: **" + prompt + "**")
        if h <= 0:
            st.error("Out of hearts")
            if st.button("Refill hearts"):
                st.session_state.lang_hearts = 5
                st.rerun()
        else:
            if options:
                choice = st.radio("Pick one", options, key="lg_opt_%d" % i)
                guess = choice
            else:
                guess = st.text_input("Your answer", key="lg_type_%d" % i)
            if st.button("Check", type="primary", use_container_width=True, key="lg_check"):
                g = (guess or "").strip().lower()
                a = answer.strip().lower()
                if g == a or a in g or g in a:
                    st.session_state.lang_xp += 10
                    st.session_state.lang_streak += 1
                    st.session_state.lang_i = i + 1
                    st.success("Correct! +10 XP")
                    st.rerun()
                else:
                    st.session_state.lang_hearts = max(0, h - 1)
                    st.session_state.lang_streak = 0
                    st.error("Answer: **" + answer + "**")
            if st.button("Skip", key="lg_skip"):
                st.session_state.lang_i = i + 1
                st.rerun()

elif view == "chess":
    st.header("Chess")
    if st.button("\u2190 Back", key="b_chess"):
        go("home")
    mode = st.radio("Chess mode", ["Play", "Learn gambits"], horizontal=True, key="chess_mode")
    if mode == "Learn gambits":
        used = False
        try:
            from meridium_gambits import render_gambit_trainer
            render_gambit_trainer(st, st.session_state)
            used = True
        except Exception:
            pass
        if not used:
            st.markdown("### Gambit Academy")
            keys = list(GAMBITS.keys())
            choice = st.selectbox(
                "Gambit", keys,
                format_func=lambda k: GAMBITS[k]["name"] + " (" + GAMBITS[k]["eco"] + ")",
            )
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
                if st.button("Reset drill"):
                    st.session_state.gambit_idx = 0
                    st.rerun()
            else:
                st.caption("After: " + (" ".join(line[:idx]) if idx else "(start)"))
                guess = st.text_input("Move %d (SAN)" % (idx + 1), key="g_guess")
                if st.button("Check move"):
                    exp = line[idx]
                    if (guess or "").strip().replace("0-0", "O-O") == exp:
                        st.session_state.gambit_idx = idx + 1
                        st.success("Correct: " + exp)
                        st.rerun()
                    else:
                        st.error("Expected **" + exp + "**")
    else:
        st.markdown(
            '<div class="card">Play mode \u2014 full Soju board returns with the classic core. '
            "Use <b>Learn gambits</b> to drill openings now.</div>",
            unsafe_allow_html=True,
        )
        st.info("Tip: switch to **Learn gambits** above to train openings.")

elif view == "lab":
    st.header("Observation Lab")
    if st.button("\u2190 Back", key="b_lab"):
        go("home")
    st.markdown(
        '<div class="card">Residual instruments online.</div>',
        unsafe_allow_html=True,
    )
    with st.expander("Archive chapters / Lore", expanded=True):
        used = False
        try:
            from meridium_lore_pack import render_lore_pack
            render_lore_pack(st, st.session_state)
            used = True
        except Exception:
            pass
        if not used:
            for title, body in LORE:
                with st.expander(title):
                    st.write(body)
    if st.button("Enter Nadir channel"):
        go("nadir")

elif view == "nadir":
    st.header("Project Nadir")
    if st.button("\u2190 Back", key="b_nadir"):
        go("home")
    used = False
    try:
        from meridium_nadir import render_nadir_v2
        render_nadir_v2(st, st.session_state)
        used = True
    except Exception:
        pass
    if not used:
        rid = st.session_state.nadir_room
        if rid not in NADIR:
            rid = "threshold"
            st.session_state.nadir_room = rid
        name, blurb, exits = NADIR[rid]
        st.markdown(
            '<div class="card"><b>' + name + "</b><br/>" + blurb + "</div>",
            unsafe_allow_html=True,
        )
        st.caption("Depth " + str(st.session_state.nadir_depth))
        cols = st.columns(min(3, len(exits)))
        for i, ex in enumerate(exits):
            with cols[i % len(cols)]:
                if st.button(NADIR[ex][0], key="nr_" + ex):
                    st.session_state.nadir_room = ex
                    st.session_state.nadir_depth = int(st.session_state.nadir_depth) + 1
                    st.rerun()
        with st.expander("Residual chapters / Lore"):
            for title, body in LORE:
                st.markdown("**" + title + "** \u2014 " + body)

elif view == "themes":
    st.header("Void Reliquary")
    if st.button("\u2190 Back", key="b_th"):
        go("home")
    used = False
    try:
        from meridium_themes import render_theme_shop
        render_theme_shop(st, st.session_state)
        used = True
    except Exception:
        pass
    if not used:
        st.metric("Residuum", st.session_state.residuum)
        owned = set(st.session_state.owned_themes)
        for tid, (name, price) in THEMES.items():
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write("**" + name + "** \u00b7 " + str(price) + " Residuum")
            with c2:
                if tid in owned:
                    if st.session_state.active_theme == tid:
                        st.success("Active")
                    elif st.button("Apply", key="ta_" + tid):
                        st.session_state.active_theme = tid
                        st.rerun()
                elif st.button("Buy", key="tb_" + tid):
                    if st.session_state.residuum >= price:
                        st.session_state.residuum -= price
                        st.session_state.owned_themes = list(owned | {tid})
                        st.session_state.active_theme = tid
                        st.rerun()
                    else:
                        st.warning("Not enough Residuum")

else:
    st.session_state.view = "home"
    st.rerun()
