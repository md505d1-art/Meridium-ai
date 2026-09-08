"""Meridium Languages — ASL-first + multi-language scaffold."""
from __future__ import annotations

ASL_FINGERSPELL = {
    "A": "Fist, thumb along the side",
    "B": "Flat hand, fingers up, thumb tucked across palm",
    "C": "Curved hand like holding a cup",
    "D": "Index up, other fingers touch thumb (d-shape)",
    "E": "Fingertips on thumb, hand tensed",
    "F": "Index+thumb OK circle, other fingers up",
    "G": "Index and thumb horizontal, pointing sideways",
    "H": "Index+middle out together, horizontal",
    "I": "Pinky up",
    "J": "Pinky draws a J in the air",
    "K": "Index+middle up in V, thumb between",
    "L": "Index up, thumb out (L shape)",
    "M": "Thumb under first three fingers",
    "N": "Thumb under first two fingers",
    "O": "Fingers rounded to an O",
    "P": "Like K but pointing down",
    "Q": "Like G but pointing down",
    "R": "Index+middle crossed",
    "S": "Fist, thumb across fingers",
    "T": "Fist, thumb under index",
    "U": "Index+middle up together",
    "V": "Index+middle up in V",
    "W": "Index+middle+ring up",
    "X": "Index hooked",
    "Y": "Thumb and pinky out",
    "Z": "Index draws Z in the air",
}

ASL_PHRASES = [
    ("HELLO", "Open hand at forehead, move outward (like a salute)"),
    ("THANK YOU", "Fingers at chin, move forward toward the person"),
    ("PLEASE", "Flat hand circles on chest"),
    ("SORRY", "Fist circles on chest"),
    ("YES", "Fist nods up and down like a head"),
    ("NO", "Index+middle close onto thumb"),
    ("HELP", "Fist on opposite open palm, lift both"),
    ("NAME", "H-hand (index+middle) taps on other H-hand"),
    ("LEARN", "Flat hand pulls knowledge from palm to forehead"),
    ("FRIEND", "Index fingers hook together, then switch"),
    ("LOVE", "Arms cross over chest (hug yourself)"),
    ("WATER", "W-hand taps chin"),
    ("EAT", "Flattened O to mouth"),
    ("MORE", "Flattened O hands tap together"),
    ("FINISHED / DONE", "Open hands flip from palm-in to palm-out"),
]

SPOKEN = {
    "Spanish": {
        "hello": "hola", "thank you": "gracias", "yes": "s\u00ed", "no": "no",
        "please": "por favor", "goodbye": "adi\u00f3s", "my name is": "me llamo",
        "how are you?": "\u00bfc\u00f3mo est\u00e1s?",
    },
    "French": {
        "hello": "bonjour", "thank you": "merci", "yes": "oui", "no": "non",
        "please": "s'il vous pla\u00eet", "goodbye": "au revoir", "my name is": "je m'appelle",
        "how are you?": "comment \u00e7a va?",
    },
    "Japanese": {
        "hello": "\u3053\u3093\u306b\u3061\u306f (konnichiwa)",
        "thank you": "\u3042\u308a\u304c\u3068\u3046 (arigatou)",
        "yes": "\u306f\u3044 (hai)", "no": "\u3044\u3044\u3048 (iie)",
        "please": "\u304a\u9858\u3044\u3057\u307e\u3059 (onegaishimasu)",
        "goodbye": "\u3055\u3088\u3046\u306a\u3089 (sayounara)",
        "my name is": "\u79c1\u306e\u540d\u524d\u306f\u2026\u3067\u3059",
        "how are you?": "\u304a\u5143\u6c17\u3067\u3059\u304b",
    },
    "German": {
        "hello": "hallo", "thank you": "danke", "yes": "ja", "no": "nein",
        "please": "bitte", "goodbye": "auf Wiedersehen", "my name is": "ich hei\u00dfe",
        "how are you?": "wie geht's?",
    },
    "Mandarin": {
        "hello": "\u4f60\u597d (n\u01d0 h\u01ceo)", "thank you": "\u8c22\u8c22 (xi\u00e8xie)",
        "yes": "\u662f (sh\u00ec)", "no": "\u4e0d (b\u00f9)", "please": "\u8bf7 (q\u01d0ng)",
        "goodbye": "\u518d\u89c1 (z\u00e0iji\u00e0n)", "my name is": "\u6211\u53eb\u2026",
        "how are you?": "\u4f60\u597d\u5417?",
    },
    "Czech": {
        "hello": "ahoj / dobr\u00fd den",
        "thank you": "d\u011bkuji",
        "yes": "ano",
        "no": "ne",
        "please": "pros\u00edm",
        "goodbye": "na shledanou",
        "my name is": "jmenuji se\u2026",
        "how are you?": "jak se m\u00e1\u0161?",
        "good morning": "dobr\u00e9 r\u00e1no",
        "excuse me": "promi\u0148te",
        "I don't understand": "nerozum\u00edm",
        "help": "pomoc",
    },
    "Russian": {
        "hello": "\u043f\u0440\u0438\u0432\u0435\u0442 (privet) / \u0437\u0434\u0440\u0430\u0432\u0441\u0442\u0432\u0443\u0439\u0442\u0435 (zdravstvuyte)",
        "thank you": "\u0441\u043f\u0430\u0441\u0438\u0431\u043e (spasibo)",
        "yes": "\u0434\u0430 (da)",
        "no": "\u043d\u0435\u0442 (net)",
        "please": "\u043f\u043e\u0436\u0430\u043b\u0443\u0439\u0441\u0442\u0430 (pozhaluysta)",
        "goodbye": "\u0434\u043e \u0441\u0432\u0438\u0434\u0430\u043d\u0438\u044f (do svidaniya)",
        "my name is": "\u043c\u0435\u043d\u044f \u0437\u043e\u0432\u0443\u0442\u2026 (menya zovut\u2026)",
        "how are you?": "\u043a\u0430\u043a \u0434\u0435\u043b\u0430? (kak dela?)",
        "good morning": "\u0434\u043e\u0431\u0440\u043e\u0435 \u0443\u0442\u0440\u043e (dobroye utro)",
        "excuse me": "\u0438\u0437\u0432\u0438\u043d\u0438\u0442\u0435 (izvinite)",
        "I don't understand": "\u044f \u043d\u0435 \u043f\u043e\u043d\u0438\u043c\u0430\u044e (ya ne ponimayu)",
        "help": "\u043f\u043e\u043c\u043e\u0433\u0438\u0442\u0435 (pomogite)",
    },
}


def render_languages(st, ss) -> None:
    st.markdown("### \ud83d\udde3\ufe0f Language Lab")
    st.caption("ASL \u00b7 Czech \u00b7 Russian \u00b7 and more spoken starters")
    mode = st.radio("Track", ["ASL", "Spoken languages"], horizontal=True, key="lang_mode")
    if mode == "ASL":
        st.markdown("#### ASL \u00b7 American Sign Language")
        st.info("Signs described in text \u2014 pair with Handspeak / Lifeprint for motion.")
        tab1, tab2, tab3 = st.tabs(["Fingerspelling", "Phrases", "Quiz"])
        with tab1:
            letter = st.selectbox("Letter", list(ASL_FINGERSPELL.keys()))
            st.success(f"**{letter}** \u2014 {ASL_FINGERSPELL[letter]}")
            word = st.text_input("Fingerspell a word (A\u2013Z only)", key="asl_word").upper()
            if word and word.isalpha():
                for ch in word:
                    st.write(f"**{ch}**: {ASL_FINGERSPELL.get(ch, '?')}")
        with tab2:
            for en, desc in ASL_PHRASES:
                with st.expander(en):
                    st.write(desc)
        with tab3:
            import random
            q = random.Random(st.session_state.get("asl_quiz_seed", 1)).choice(ASL_PHRASES)
            st.write(f"How do you sign **{q[0]}**?")
            st.text_area("Describe the sign in your own words", key="asl_quiz_ans")
            if st.button("Reveal model description"):
                st.info(q[1])
            if st.button("New question", key="asl_new_q"):
                st.session_state.asl_quiz_seed = int(st.session_state.get("asl_quiz_seed") or 1) + 1
                st.rerun()
    else:
        lang = st.selectbox("Language", list(SPOKEN.keys()))
        vocab = SPOKEN[lang]
        st.markdown(f"#### {lang} \u00b7 core phrases")
        for en, native in vocab.items():
            st.write(f"**{en}** \u2192 `{native}`")
        st.markdown("##### Quick quiz")
        items = list(vocab.items())
        i = st.number_input("Card", 0, max(0, len(items) - 1), 0)
        en, native = items[int(i)]
        st.write(f"Translate: **{en}**")
        g = st.text_input("Your answer", key=f"sp_{lang}_{i}")
        if st.button("Check", key=f"sp_chk_{i}"):
            g_l = (g or "").strip().lower()
            n_l = native.lower()
            ok = g_l and (g_l in n_l or any(tok in g_l for tok in n_l.replace("(", " ").replace(")", " ").split() if len(tok) > 2))
            if ok:
                st.success("Nice!")
            else:
                st.warning(f"Model answer: {native}")
