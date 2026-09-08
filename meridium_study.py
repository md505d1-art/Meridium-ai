"""Meridium GCSE Study Hub."""
from __future__ import annotations

import json
from pathlib import Path

BOARDS = ["AQA", "Edexcel", "OCR", "WJEC", "CCEA", "Eduqas"]

SUBJECTS = {
    "Mathematics": {
        "boards": ["AQA", "Edexcel", "OCR", "WJEC", "CCEA"],
        "tiers": ["Foundation", "Higher"],
        "topics": [
            "Number", "Algebra expressions", "Sequences and graphs",
            "Ratio and proportion", "Geometry angles", "Area and volume",
            "Probability", "Statistics",
        ],
    },
    "English Language": {
        "boards": BOARDS,
        "tiers": ["Single"],
        "topics": ["Inference", "Language analysis", "Comparing texts", "Creative writing", "Transactional writing", "SPaG"],
    },
    "English Literature": {
        "boards": BOARDS,
        "tiers": ["Single"],
        "topics": ["Shakespeare", "19th-century novel", "Modern text", "Poetry anthology", "Unseen poetry"],
    },
    "Biology": {
        "boards": ["AQA", "Edexcel", "OCR", "WJEC", "CCEA"],
        "tiers": ["Foundation", "Higher"],
        "topics": ["Cells", "Organisation", "Infection", "Bioenergetics", "Homeostasis", "Inheritance", "Ecology"],
    },
    "Chemistry": {
        "boards": ["AQA", "Edexcel", "OCR", "WJEC", "CCEA"],
        "tiers": ["Foundation", "Higher"],
        "topics": ["Atomic structure", "Bonding", "Quantitative", "Chemical changes", "Energy changes", "Rates", "Organic", "Analysis"],
    },
    "Physics": {
        "boards": ["AQA", "Edexcel", "OCR", "WJEC", "CCEA"],
        "tiers": ["Foundation", "Higher"],
        "topics": ["Energy", "Electricity", "Particle model", "Atomic structure", "Forces", "Waves", "Magnetism", "Space"],
    },
    "History": {
        "boards": ["AQA", "Edexcel", "OCR", "WJEC"],
        "tiers": ["Single"],
        "topics": ["Period study", "Thematic study", "Modern depth", "British depth", "Historic environment"],
    },
    "Geography": {
        "boards": ["AQA", "Edexcel", "OCR", "WJEC"],
        "tiers": ["Single"],
        "topics": ["Physical landscapes", "Weather and climate", "Ecosystems", "Urban issues", "Resource management", "Fieldwork"],
    },
    "Computer Science": {
        "boards": ["AQA", "Edexcel", "OCR", "WJEC"],
        "tiers": ["Single"],
        "topics": ["Algorithms", "Programming", "Data representation", "Computer systems", "Networks", "Cyber security", "Impacts of computing"],
    },
    "French": {
        "boards": ["AQA", "Edexcel", "OCR", "WJEC"],
        "tiers": ["Foundation", "Higher"],
        "topics": ["Identity", "Local area", "School", "Future plans", "Global issues", "Listening/Reading/Writing/Speaking"],
    },
    "Spanish": {
        "boards": ["AQA", "Edexcel", "OCR", "WJEC"],
        "tiers": ["Foundation", "Higher"],
        "topics": ["Identity", "Local area", "School", "Future plans", "Global issues", "Listening/Reading/Writing/Speaking"],
    },
    "Religious Studies": {
        "boards": ["AQA", "Edexcel", "OCR", "WJEC"],
        "tiers": ["Single"],
        "topics": ["Beliefs", "Practices", "Relationships", "Life and death", "Crime and punishment", "Human rights"],
    },
}

LINKS = {
    "AQA": "https://www.aqa.org.uk/find-past-papers-and-mark-schemes",
    "Edexcel": "https://qualifications.pearson.com/en/support/support-topics/exams/past-papers.html",
    "OCR": "https://www.ocr.org.uk/qualifications/past-paper-finder/",
    "WJEC": "https://www.wjec.co.uk/home/student-support/",
    "Eduqas": "https://www.eduqas.co.uk/",
    "CCEA": "https://ccea.org.uk/",
}

PRACTICE = {
    "Mathematics": [
        ("What is 3/4 as a percentage?", "75%"),
        ("Solve 2x + 5 = 17", "x = 6"),
        ("Area of a circle radius 3 (leave in terms of pi)", "9pi"),
    ],
    "Biology": [
        ("Where does photosynthesis mainly occur?", "chloroplasts / leaves"),
        ("What molecule carries genetic information?", "DNA"),
        ("Name the process of cell division for growth", "mitosis"),
    ],
    "Chemistry": [
        ("Atomic number counts which particles?", "protons"),
        ("pH of a strong acid is closest to?", "1"),
        ("Group 1 metals react with water to form?", "hydroxide + hydrogen"),
    ],
    "Physics": [
        ("Unit of force?", "newton / N"),
        ("Speed = distance / ?", "time"),
        ("Like charges ?", "repel"),
    ],
}


def _data() -> Path:
    try:
        from meridium_paths import meridium_data_dir
        return meridium_data_dir()
    except Exception:
        import tempfile
        d = Path(tempfile.gettempdir()) / "meridium_data"
        try:
            d.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        return d


def load_progress(user: str) -> dict:
    p = _data() / ("study_" + "".join(c for c in user if c.isalnum())[:24] + ".json")
    try:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"done": [], "board": "AQA", "subject": "Mathematics", "scores": {}}


def save_progress(user: str, data: dict) -> None:
    try:
        safe = "".join(c for c in user if c.isalnum())[:24] or "anon"
        (_data() / ("study_" + safe + ".json")).write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )
    except Exception:
        pass


def render_study_hub(st, ss) -> None:
    st.markdown("### GCSE Study Hub")
    st.caption("Pick subject and board \u00b7 tick topics \u00b7 practice \u00b7 official papers")

    user = (ss.get("username") or "anon").strip() or "anon"
    if "study_prog" not in ss:
        ss["study_prog"] = load_progress(user)
    prog = ss["study_prog"]

    subjects = list(SUBJECTS.keys())
    sub_i = subjects.index(prog["subject"]) if prog.get("subject") in SUBJECTS else 0
    subject = st.selectbox("Subject", subjects, index=sub_i, key="study_subject")
    meta = SUBJECTS[subject]
    boards = meta.get("boards") or BOARDS
    b_i = boards.index(prog["board"]) if prog.get("board") in boards else 0
    board = st.selectbox("Exam board", boards, index=b_i, key="study_board")
    tier = st.selectbox("Tier", meta.get("tiers") or ["Single"], key="study_tier")

    prog["subject"] = subject
    prog["board"] = board

    st.markdown("**" + subject + "** \u00b7 **" + board + "** \u00b7 " + str(tier))
    link = LINKS.get(board)
    if link:
        st.markdown("[Official past papers \u2014 " + board + "](" + link + ")")

    done = set(prog.get("done") or [])
    topics = meta.get("topics") or []
    st.markdown("#### Topics")
    changed = False
    for t in topics:
        key = subject + "|" + board + "|" + t
        val = st.checkbox(t, value=(key in done), key="tp_" + str(abs(hash(key)) % 10**8))
        if val and key not in done:
            done.add(key)
            changed = True
        elif not val and key in done:
            done.discard(key)
            changed = True
    if changed:
        prog["done"] = sorted(done)
        ss["study_prog"] = prog
        save_progress(user, prog)

    st.markdown("#### Quick practice")
    bank = PRACTICE.get(subject) or [
        ("Write one key fact from this subject", "(open)"),
        ("Name a common exam command word", "explain / evaluate / describe"),
        ("What should you do in the last 5 minutes of a paper?", "check answers"),
    ]
    if "study_qi" not in ss:
        ss["study_qi"] = 0
    qi = int(ss["study_qi"]) % len(bank)
    q, a = bank[qi]
    st.write("**Q:** " + q)
    guess = st.text_input("Your answer", key="study_ans")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Check", key="study_check"):
            if a.startswith("("):
                st.info("Model idea: " + a)
            elif (guess or "").strip().lower() in a.lower() or a.lower() in (guess or "").strip().lower():
                st.success("Nice \u2014 " + a)
            else:
                st.warning("Aim for: " + a)
    with c2:
        if st.button("Next question", key="study_next"):
            ss["study_qi"] = qi + 1
            st.rerun()

    with st.expander("Tips"):
        st.write(
            "Active recall \u00b7 timed official papers \u00b7 mark schemes \u00b7 short daily sessions beat cramming."
        )
