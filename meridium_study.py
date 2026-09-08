"""Meridium GCSE Study Hub — all subjects, selectable exam boards, revision tools.
Official past-paper PDFs are copyrighted; we provide structure, topics, practice,
and links to free official sources — not scanned papers.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

BOARDS = ["AQA", "Edexcel", "OCR", "WJEC", "CCEA", "Eduqas"]

SUBJECTS = {
    "Mathematics": {"boards": ["AQA", "Edexcel", "OCR", "WJEC", "CCEA"], "tiers": ["Foundation", "Higher"],
        "topics": ["Number \u00b7 fractions decimals percentages", "Algebra \u00b7 expressions equations inequalities",
            "Algebra \u00b7 sequences graphs", "Ratio proportion rates of change", "Geometry \u00b7 angles shapes constructions",
            "Geometry \u00b7 area volume Pythagoras trig", "Probability", "Statistics \u00b7 data averages charts"]},
    "English Language": {"boards": ["AQA", "Edexcel", "OCR", "WJEC", "Eduqas", "CCEA"], "tiers": ["Single"],
        "topics": ["Reading \u00b7 inference and analysis", "Reading \u00b7 language and structure", "Reading \u00b7 comparing texts",
            "Writing \u00b7 narrative / descriptive", "Writing \u00b7 viewpoint / transactional", "SPaG \u00b7 sentence accuracy"]},
    "English Literature": {"boards": ["AQA", "Edexcel", "OCR", "WJEC", "Eduqas", "CCEA"], "tiers": ["Single"],
        "topics": ["Shakespeare \u00b7 character and theme", "19th-century novel", "Modern text \u00b7 drama or prose",
            "Poetry \u00b7 anthology comparison", "Unseen poetry"]},
    "Biology": {"boards": ["AQA", "Edexcel", "OCR", "WJEC", "CCEA"], "tiers": ["Foundation", "Higher"],
        "topics": ["Cell biology", "Organisation", "Infection and response", "Bioenergetics",
            "Homeostasis and response", "Inheritance variation evolution", "Ecology"]},
    "Chemistry": {"boards": ["AQA", "Edexcel", "OCR", "WJEC", "CCEA"], "tiers": ["Foundation", "Higher"],
        "topics": ["Atomic structure and periodic table", "Bonding structure properties", "Quantitative chemistry",
            "Chemical changes", "Energy changes", "Rate and equilibrium", "Organic chemistry",
            "Chemical analysis", "Atmosphere and resources"]},
    "Physics": {"boards": ["AQA", "Edexcel", "OCR", "WJEC", "CCEA"], "tiers": ["Foundation", "Higher"],
        "topics": ["Energy", "Electricity", "Particle model of matter", "Atomic structure", "Forces",
            "Waves", "Magnetism and electromagnetism", "Space physics"]},
    "Combined Science": {"boards": ["AQA", "Edexcel", "OCR", "WJEC"], "tiers": ["Foundation", "Higher"],
        "topics": ["Biology core topics", "Chemistry core topics", "Physics core topics", "Required practical skills"]},
    "History": {"boards": ["AQA", "Edexcel", "OCR", "WJEC", "Eduqas", "CCEA"], "tiers": ["Single"],
        "topics": ["Period study", "Thematic study", "Modern depth study", "British depth study", "Historic environment / sources"]},
    "Geography": {"boards": ["AQA", "Edexcel", "OCR", "WJEC", "Eduqas", "CCEA"], "tiers": ["Single"],
        "topics": ["Physical landscapes", "Weather climate ecosystems", "Urban issues", "Changing economic world",
            "Resource management", "Fieldwork skills"]},
    "Computer Science": {"boards": ["AQA", "Edexcel", "OCR", "WJEC"], "tiers": ["Single"],
        "topics": ["Algorithms", "Programming fundamentals", "Data representation", "Computer systems",
            "Networks", "Cyber security", "Impacts of computing", "SQL and databases"]},
    "Business": {"boards": ["AQA", "Edexcel", "OCR", "WJEC"], "tiers": ["Single"],
        "topics": ["Business activity", "Marketing", "People in business", "Operations", "Finance", "Influences on business"]},
    "Economics": {"boards": ["AQA", "Edexcel", "OCR"], "tiers": ["Single"],
        "topics": ["Introduction to economics", "Microeconomics", "Macroeconomics", "International trade"]},
    "Religious Studies": {"boards": ["AQA", "Edexcel", "OCR", "WJEC", "Eduqas"], "tiers": ["Single"],
        "topics": ["Beliefs and teachings", "Practices", "Religion and life", "Peace and conflict",
            "Crime and punishment", "Human rights"]},
    "French": {"boards": ["AQA", "Edexcel", "OCR", "WJEC"], "tiers": ["Foundation", "Higher"],
        "topics": ["Listening", "Speaking", "Reading", "Writing", "Grammar", "Themes identity culture"]},
    "Spanish": {"boards": ["AQA", "Edexcel", "OCR", "WJEC"], "tiers": ["Foundation", "Higher"],
        "topics": ["Listening", "Speaking", "Reading", "Writing", "Grammar", "Themes identity culture"]},
    "German": {"boards": ["AQA", "Edexcel", "OCR", "WJEC"], "tiers": ["Foundation", "Higher"],
        "topics": ["Listening", "Speaking", "Reading", "Writing", "Grammar"]},
    "Art & Design": {"boards": ["AQA", "Edexcel", "OCR", "WJEC"], "tiers": ["Single"],
        "topics": ["Portfolio", "Externally set assignment", "Critical studies"]},
    "Drama": {"boards": ["AQA", "Edexcel", "OCR", "WJEC"], "tiers": ["Single"],
        "topics": ["Devising", "Performance", "Theatre evaluation"]},
    "Music": {"boards": ["AQA", "Edexcel", "OCR", "WJEC"], "tiers": ["Single"],
        "topics": ["Performing", "Composing", "Appraising"]},
    "PE": {"boards": ["AQA", "Edexcel", "OCR", "WJEC"], "tiers": ["Single"],
        "topics": ["Applied anatomy", "Movement analysis", "Physical training", "Sports psychology", "Socio-cultural"]},
    "Psychology": {"boards": ["AQA", "Edexcel", "OCR"], "tiers": ["Single"],
        "topics": ["Memory", "Perception", "Development", "Research methods", "Social influence", "Language thinking"]},
    "Sociology": {"boards": ["AQA", "Edexcel", "OCR", "WJEC"], "tiers": ["Single"],
        "topics": ["Families", "Education", "Crime deviance", "Social stratification", "Research methods"]},
    "Design & Technology": {"boards": ["AQA", "Edexcel", "OCR", "WJEC"], "tiers": ["Single"],
        "topics": ["Core technical principles", "Specialist technical principles", "Designing and making"]},
    "Food Preparation": {"boards": ["AQA", "Edexcel", "OCR", "WJEC"], "tiers": ["Single"],
        "topics": ["Nutrition", "Food provenance", "Cooking techniques", "NEA skills"]},
    "Media Studies": {"boards": ["AQA", "Edexcel", "OCR", "WJEC"], "tiers": ["Single"],
        "topics": ["Media language", "Representation", "Industries", "Audiences"]},
    "Citizenship": {"boards": ["AQA", "Edexcel", "OCR"], "tiers": ["Single"],
        "topics": ["Rights responsibilities", "Democracy", "Law justice", "Identity diversity"]},
}

OFFICIAL_PAPER_LINKS = {
    "AQA": "https://www.aqa.org.uk/find-past-papers-and-mark-schemes",
    "Edexcel": "https://qualifications.pearson.com/en/support/support-topics/exams/past-papers.html",
    "OCR": "https://www.ocr.org.uk/qualifications/past-paper-finder/",
    "WJEC": "https://www.wjec.co.uk/home/student-support/",
    "Eduqas": "https://www.eduqas.co.uk/",
    "CCEA": "https://ccea.org.uk/",
}

_PRACTICE = {
    "Mathematics": [
        ("Expand and simplify (x+3)(x-2).", "x\u00b2 + x - 6"),
        ("Solve 2x + 5 = 17.", "x = 6"),
        ("A coat costs \u00a380 after 20% off. What was the original price?", "\u00a3100"),
        ("Find the gradient of the line through (1,2) and (3,8).", "3"),
    ],
    "Biology": [
        ("Name the organelle that releases energy in respiration.", "Mitochondria"),
        ("What is the function of xylem?", "Transport water / minerals up the plant"),
        ("State one difference between aerobic and anaerobic respiration in humans.", "Anaerobic produces lactic acid / less ATP / no oxygen"),
    ],
    "Chemistry": [
        ("What is the charge on a chloride ion?", "-1"),
        ("Name the bond type in NaCl.", "Ionic"),
        ("What does endothermic mean?", "Takes in energy from surroundings"),
    ],
    "Physics": [
        ("State the unit of force.", "Newton (N)"),
        ("What is the formula for kinetic energy?", "\u00bdmv\u00b2"),
        ("Name the particle with no charge in the nucleus.", "Neutron"),
    ],
    "English Language": [
        ("Define 'metaphor'.", "A comparison stating one thing is another"),
        ("What is the purpose of a topic sentence?", "Introduce the main idea of a paragraph"),
    ],
    "Computer Science": [
        ("Convert binary 1010 to decimal.", "10"),
        ("What does CPU stand for?", "Central Processing Unit"),
        ("Name a type of network topology.", "Star / Bus / Mesh / Ring"),
    ],
}


def _data() -> Path:
    d = Path(__file__).resolve().parent / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_study_progress(user: str) -> dict:
    p = _data() / f"study_{user[:32]}.json"
    try:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"done_topics": [], "quiz_scores": {}, "board": "AQA", "subject": "Mathematics"}


def save_study_progress(user: str, data: dict) -> None:
    try:
        (_data() / f"study_{user[:32]}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


def _quiz_for(subject: str, topic: str, n: int = 3) -> list:
    base = _PRACTICE.get(subject) or [
        (f"Explain a key idea in: {topic}", "(own words \u2014 mark with teacher)"),
        (f"List two facts about: {topic}", "(own words)"),
        (f"Why does {topic} matter in the exam?", "(own words)"),
    ]
    seed = int(hashlib.md5(f"{date.today()}{subject}{topic}".encode()).hexdigest()[:8], 16)
    items = sorted(list(base), key=lambda x: (seed + hash(x[0])) % 97)
    return items[:n]


def render_study_hub(st, ss) -> None:
    st.markdown("### \ud83d\udcda GCSE Study Hub")
    st.caption("Every major subject \u00b7 pick your exam board \u00b7 revise topics \u00b7 practice \u00b7 official paper links")
    user = (ss.get("username") or "anon").strip() or "anon"
    prog = load_study_progress(user)
    c1, c2, c3 = st.columns(3)
    with c1:
        keys = list(SUBJECTS.keys())
        subject = st.selectbox("Subject", keys, index=keys.index(prog["subject"]) if prog.get("subject") in SUBJECTS else 0)
    meta = SUBJECTS[subject]
    with c2:
        boards = meta.get("boards") or BOARDS
        b0 = prog.get("board") if prog.get("board") in boards else boards[0]
        board = st.selectbox("Exam board", boards, index=boards.index(b0))
    with c3:
        tier = st.selectbox("Tier", meta.get("tiers") or ["Single"])
    prog["subject"] = subject
    prog["board"] = board
    save_study_progress(user, prog)
    st.markdown(f"**{subject}** \u00b7 **{board}** \u00b7 {tier}")
    link = OFFICIAL_PAPER_LINKS.get(board)
    if link:
        st.markdown(f"Official past papers & mark schemes: [{board} finder]({link})")
        st.caption("We don't host copyrighted papers \u2014 use the board's free official portal.")
    done = set(prog.get("done_topics") or [])
    topics = meta.get("topics") or []
    st.markdown("#### Topics")
    for t in topics:
        key = f"{subject}|{board}|{t}"
        checked = key in done
        cols = st.columns([0.1, 0.9])
        with cols[0]:
            val = st.checkbox("", value=checked, key=f"topic_{hashlib.md5(key.encode()).hexdigest()[:10]}")
        with cols[1]:
            st.write(("\u2705 " if val else "\u2b1c ") + t)
        if val and not checked:
            done.add(key)
        if not val and checked:
            done.discard(key)
    prog["done_topics"] = sorted(done)
    save_study_progress(user, prog)
    st.markdown("#### Practice")
    topic = st.selectbox("Topic for quiz", topics, key="study_quiz_topic")
    qs = _quiz_for(subject, topic)
    answers = []
    for i, (q, a) in enumerate(qs):
        st.markdown(f"**Q{i+1}.** {q}")
        answers.append((st.text_input("Your answer", key=f"ans_{i}_{topic[:12]}"), a))
    if st.button("Mark practice", key="study_mark"):
        score = 0
        for gu, au in answers:
            if au.startswith("("):
                st.info(f"Open response \u2014 compare to: {au}")
            elif (gu or "").strip().lower() == au.strip().lower():
                score += 1
                st.success(f"\u2713 {au}")
            else:
                st.warning(f"Expected something like: {au}")
        st.metric("Score", f"{score}/{len(qs)}")
        prog.setdefault("quiz_scores", {})[f"{subject}:{topic}"] = score
        save_study_progress(user, prog)
    with st.expander("Revision tips"):
        st.write("1. Active recall beats re-reading \u00b7 2. Past paper under timed conditions via official links \u00b7 3. Mark schemes teach examiner language \u00b7 4. Little & often > cramming")
