"""Meridium Language Lab — Duolingo-style lessons."""
from __future__ import annotations

LESSONS = {
    "ASL": [
        ("How do you sign HELLO?", "Open hand at forehead, move outward", None),
        ("How do you sign THANK YOU?", "Fingers at chin, move forward", None),
        ("Letter A handshape?", "Fist, thumb along the side", None),
        ("Letter B handshape?", "Flat hand, fingers up, thumb tucked", None),
        ("How do you sign YES?", "Fist nods like a head", None),
        ("How do you sign NO?", "Index+middle close onto thumb", None),
        ("How do you sign PLEASE?", "Flat hand circles on chest", None),
        ("Letter L handshape?", "Index up, thumb out", None),
    ],
    "Spanish": [
        ("hello", "hola", ["hola", "adios", "gracias", "por favor"]),
        ("thank you", "gracias", ["gracias", "hola", "si", "no"]),
        ("yes", "s\u00ed", ["s\u00ed", "no", "hola", "gracias"]),
        ("no", "no", ["no", "s\u00ed", "hola", "adios"]),
        ("please", "por favor", ["por favor", "gracias", "hola", "adios"]),
        ("goodbye", "adi\u00f3s", ["adi\u00f3s", "hola", "gracias", "s\u00ed"]),
    ],
    "Czech": [
        ("hello", "ahoj", ["ahoj", "d\u011bkuji", "ano", "ne"]),
        ("thank you", "d\u011bkuji", ["d\u011bkuji", "ahoj", "ano", "ne"]),
        ("yes", "ano", ["ano", "ne", "ahoj", "pros\u00edm"]),
        ("no", "ne", ["ne", "ano", "ahoj", "d\u011bkuji"]),
        ("please", "pros\u00edm", ["pros\u00edm", "d\u011bkuji", "ano", "ne"]),
        ("goodbye", "na shledanou", ["na shledanou", "ahoj", "d\u011bkuji", "ano"]),
    ],
    "Russian": [
        ("hello", "\u043f\u0440\u0438\u0432\u0435\u0442", ["\u043f\u0440\u0438\u0432\u0435\u0442", "\u0441\u043f\u0430\u0441\u0438\u0431\u043e", "\u0434\u0430", "\u043d\u0435\u0442"]),
        ("thank you", "\u0441\u043f\u0430\u0441\u0438\u0431\u043e", ["\u0441\u043f\u0430\u0441\u0438\u0431\u043e", "\u043f\u0440\u0438\u0432\u0435\u0442", "\u0434\u0430", "\u043d\u0435\u0442"]),
        ("yes", "\u0434\u0430", ["\u0434\u0430", "\u043d\u0435\u0442", "\u043f\u0440\u0438\u0432\u0435\u0442", "\u043f\u043e\u043a\u0430"]),
        ("no", "\u043d\u0435\u0442", ["\u043d\u0435\u0442", "\u0434\u0430", "\u043f\u0440\u0438\u0432\u0435\u0442", "\u0441\u043f\u0430\u0441\u0438\u0431\u043e"]),
        ("please", "\u043f\u043e\u0436\u0430\u043b\u0443\u0439\u0441\u0442\u0430", ["\u043f\u043e\u0436\u0430\u043b\u0443\u0439\u0441\u0442\u0430", "\u0441\u043f\u0430\u0441\u0438\u0431\u043e", "\u0434\u0430", "\u043d\u0435\u0442"]),
        ("goodbye", "\u0434\u043e \u0441\u0432\u0438\u0434\u0430\u043d\u0438\u044f", ["\u0434\u043e \u0441\u0432\u0438\u0434\u0430\u043d\u0438\u044f", "\u043f\u0440\u0438\u0432\u0435\u0442", "\u0441\u043f\u0430\u0441\u0438\u0431\u043e", "\u0434\u0430"]),
    ],
    "French": [
        ("hello", "bonjour", ["bonjour", "merci", "oui", "non"]),
        ("thank you", "merci", ["merci", "bonjour", "oui", "non"]),
        ("yes", "oui", ["oui", "non", "merci", "bonjour"]),
        ("no", "non", ["non", "oui", "merci", "salut"]),
        ("please", "s'il vous pla\u00eet", ["s'il vous pla\u00eet", "merci", "oui", "non"]),
        ("goodbye", "au revoir", ["au revoir", "bonjour", "merci", "oui"]),
    ],
    "Japanese": [
        ("hello", "\u3053\u3093\u306b\u3061\u306f", ["\u3053\u3093\u306b\u3061\u306f", "\u3042\u308a\u304c\u3068\u3046", "\u306f\u3044", "\u3044\u3044\u3048"]),
        ("thank you", "\u3042\u308a\u304c\u3068\u3046", ["\u3042\u308a\u304c\u3068\u3046", "\u3053\u3093\u306b\u3061\u306f", "\u306f\u3044", "\u3044\u3044\u3048"]),
        ("yes", "\u306f\u3044", ["\u306f\u3044", "\u3044\u3044\u3048", "\u3053\u3093\u306b\u3061\u306f", "\u3042\u308a\u304c\u3068\u3046"]),
        ("no", "\u3044\u3044\u3048", ["\u3044\u3044\u3048", "\u306f\u3044", "\u3053\u3093\u306b\u3061\u306f", "\u3042\u308a\u304c\u3068\u3046"]),
    ],
    "German": [
        ("hello", "hallo", ["hallo", "danke", "ja", "nein"]),
        ("thank you", "danke", ["danke", "hallo", "ja", "nein"]),
        ("yes", "ja", ["ja", "nein", "hallo", "danke"]),
        ("no", "nein", ["nein", "ja", "hallo", "bitte"]),
        ("please", "bitte", ["bitte", "danke", "ja", "nein"]),
    ],
}


def render_languages(st, ss) -> None:
    st.markdown("### Language Lab")
    st.caption("Duolingo-style practice \u00b7 XP \u00b7 hearts \u00b7 short lessons")

    if "lang_xp" not in ss:
        ss["lang_xp"] = 0
    if "lang_hearts" not in ss:
        ss["lang_hearts"] = 5
    if "lang_streak" not in ss:
        ss["lang_streak"] = 0
    if "lang_i" not in ss:
        ss["lang_i"] = 0
    if "lang_course" not in ss:
        ss["lang_course"] = "Spanish"

    top = st.columns(3)
    with top[0]:
        st.metric("XP", int(ss["lang_xp"]))
    with top[1]:
        hearts = int(ss["lang_hearts"])
        st.metric("Hearts", "\u2665" * max(0, hearts) + "\u2661" * max(0, 5 - hearts))
    with top[2]:
        st.metric("Streak", int(ss["lang_streak"]))

    course = st.selectbox(
        "Course",
        list(LESSONS.keys()),
        index=list(LESSONS.keys()).index(ss["lang_course"])
        if ss.get("lang_course") in LESSONS
        else 0,
        key="lang_course_sel",
    )
    ss["lang_course"] = course
    pack = LESSONS[course]
    i = int(ss["lang_i"]) % len(pack)
    prompt, answer, options = pack[i]

    st.progress((i + 1) / len(pack))
    st.markdown("#### Lesson " + str(i + 1) + " / " + str(len(pack)))
    st.info("Translate / answer: **" + prompt + "**")

    if int(ss["lang_hearts"]) <= 0:
        st.error("Out of hearts. Take a break, then refill.")
        if st.button("Refill hearts", key="lang_refill"):
            ss["lang_hearts"] = 5
            st.rerun()
        return

    choice = None
    typed = ""
    if options:
        choice = st.radio("Pick the answer", options, key="lang_opt_" + course + "_" + str(i))
    else:
        typed = st.text_input("Type your answer", key="lang_type_" + course + "_" + str(i))

    if st.button("Check", key="lang_check_" + str(i), type="primary", use_container_width=True):
        given = (choice or typed or "").strip().lower()
        target = answer.strip().lower()
        ok = given == target or target in given or given in target
        if ok:
            ss["lang_xp"] = int(ss["lang_xp"]) + 10
            ss["lang_streak"] = int(ss["lang_streak"]) + 1
            ss["lang_i"] = i + 1
            st.success("Correct! +10 XP")
            st.rerun()
        else:
            ss["lang_hearts"] = max(0, int(ss["lang_hearts"]) - 1)
            ss["lang_streak"] = 0
            st.error("Not quite. Answer: **" + answer + "**")

    if st.button("Skip", key="lang_skip"):
        ss["lang_i"] = i + 1
        st.rerun()

    if int(ss.get("lang_i") or 0) >= len(pack):
        st.success("Course section complete. XP: " + str(ss["lang_xp"]))
        if st.button("Restart course", key="lang_restart"):
            ss["lang_i"] = 0
            st.rerun()
