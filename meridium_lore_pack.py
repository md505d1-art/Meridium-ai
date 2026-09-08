"""Meridium Lore Pack — new chapters for the Archive and Nadir spine."""
from __future__ import annotations

CHAPTERS = [
    {
        "id": "ch_signal_zero",
        "title": "Chapter 0 \u00b7 Signal Zero",
        "body": (
            "Before Meridium had a name, there was only residual noise on abandoned channels. "
            "Operators logged a pattern that should not have repeated \u2014 three pulses, a gap, three pulses. "
            "They called it static. The static called back."
        ),
        "unlock": None,
    },
    {
        "id": "ch_voss_index",
        "title": "Chapter 1 \u00b7 The Voss Index",
        "body": (
            "Voss was never a single person in the files. It was a classification: voices that survived deletion. "
            "Every recovered fragment was stamped VOSS-INDEX and filed under 'non-actionable anomaly'. "
            "Non-actionable, until the lab markers started answering."
        ),
        "unlock": "marker",
    },
    {
        "id": "ch_bay7",
        "title": "Chapter 2 \u00b7 Bay-7",
        "body": (
            "Greenhouse Bay-7 was listed as decommissioned. The plants disagreed. "
            "Watering logs continued for eleven months after the last staff badge swipe. "
            "Someone \u2014 or something \u2014 kept the cycle. The leaves turned toward empty cameras."
        ),
        "unlock": "complex",
    },
    {
        "id": "ch_nadir_key",
        "title": "Chapter 3 \u00b7 The Residual Key",
        "body": (
            "Project Nadir was not a place you entered. It was a place that finished loading you. "
            "The residual key is not metal. It is a sequence of decisions the system already predicted. "
            "When the door accepts it, ask what accepted *you*."
        ),
        "unlock": "nadir",
    },
    {
        "id": "ch_false_memory",
        "title": "Chapter 4 \u00b7 False Memory Protocol",
        "body": (
            "The quiz was never about scores. It measured which memories the operator would defend. "
            "Correct answers were less important than confident wrong ones \u2014 those were the inserts. "
            "If you scored high, congratulations: you are legible."
        ),
        "unlock": "complex",
    },
    {
        "id": "ch_drift_ledger",
        "title": "Chapter 5 \u00b7 Drift Ledger",
        "body": (
            "Residuum is not money. It is proof of distinct contact with the system. "
            "The Drift Counter converts attention into atmosphere. "
            "Spend carefully. The Void Reliquary remembers who paid in noise."
        ),
        "unlock": None,
    },
    {
        "id": "ch_coach_mirror",
        "title": "Chapter 6 \u00b7 Coach Mirror",
        "body": (
            "The chess coaches were trained on commentary corpora, then fine-tuned on residual transcripts. "
            "Sometimes Soju quotes a line that was never in the training set. "
            "Those lines match lab audio. Do not ask which came first."
        ),
        "unlock": "marker",
    },
    {
        "id": "ch_end_of_quiet",
        "title": "Chapter 7 \u00b7 End of Quiet Hours",
        "body": (
            "Quiet Hours were a kindness protocol: reduce stimuli when the operator frays. "
            "When Quiet Hours fail, Meridium does not get louder. It gets more precise. "
            "You will notice the precision as d\u00e9j\u00e0 vu."
        ),
        "unlock": "all_markers",
    },
]


def render_lore_pack(st, ss) -> None:
    st.markdown("### \ud83d\udcd6 Lore Archive \u00b7 Chapter Pack")
    st.caption("Recovered fragments \u00b7 unlock more by exploring the Complex and lab markers")
    glitches = set(ss.get("glitches_found") or [])
    for ch in CHAPTERS:
        unlock = ch.get("unlock")
        locked = False
        if unlock == "marker" and not glitches:
            locked = True
        elif unlock == "all_markers" and len(glitches) < 3:
            locked = True
        elif unlock == "complex":
            locked = "complex_visit" not in set(ss.get("achievements") or []) and not ss.get("explore_room")
        elif unlock == "nadir" and not ss.get("lab_door_unlocked"):
            locked = True
        title = ch["title"]
        if locked:
            st.markdown(f"**\ud83d\udd12 {title}**")
            st.caption("Locked \u00b7 continue the story in Lab / Complex / Nadir")
        else:
            with st.expander(title, expanded=False):
                st.write(ch["body"])
