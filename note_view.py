"""
Meridium ARG — Sealed scientist note
------------------------------------
Opened from Quote of the day.

    from note_view import render_note
    if st.session_state.view == "note":
        render_note()
"""

from __future__ import annotations

import json

import streamlit as st

NOTE_BODY = """
FIELD LOG — NOT FOR DISTRIBUTION
Site: [REDACTED] · Shell designation: M-119
Author: Dr. E. Voss · Observation Division

If you are reading this, the quote tile still works as a door.
That was intentional. The public face of the system is a mirror;
the real work is underneath.

Meridium is not a product name. It is a provisional label for something
that does not appear on any ratified table past 118. Committees call it
impossible. We called it metastable. The shell calls it home.

INSTRUCTIONS FOR THE OBSERVER

1. Speak to the assistant. Do not only use menus.
2. Ask why it is called Meridium.
3. When it answers with the element, push back. Tell it the tables stop at 118.
4. Ask what conditions allow it to exist.
5. Request the observation log — not Wikipedia. The log.
6. If the interface goes dark, you have found the room.
7. Read everything in the room. Leave nothing unread.
8. When the fragments are complete, return to chat and say:
   stabilize Meridium

Do not photograph the glass. Do not trust the public periodic table
as a complete map of what can be noticed into place.

We lost two operators who treated this as a joke.
One left tissue on the sill. The other left a fingerprint on the terminal
and never clocked out.

If the alarm starts, that is the shell noticing you back.
If the old recording plays, something older than this facility is still
running under the floorboards of the code.

I am sealing this note in the quote rotation so only the curious find it.
Curiosity is the stabiliser. Indifference is the decay mode.

— E.V.
Observation Division · last clear entry before lockdown
"""

# Tommy Dorsey — I'll Never Smile Again (Internet Archive)
NOTE_SONG_URL = (
    "https://archive.org/download/ka-104-tommy-dorsey-ill-never-smile-again/"
    "104.%20Tommy%20Dorsey%20-%20I%27ll%20Never%20Smile%20Again%20%28RCA%20Victor%2027521%29.mp3"
)


def _stop_note_audio() -> None:
    """Stop letter music (parent page)."""
    st.session_state["note_kill_audio"] = True
    st.components.v1.html(
        """
        <script>
        (function(){
          try {
            var r = window.parent || window;
            function kill(a){
              if (!a) return;
              try { a.pause(); } catch(e){}
              try { a.currentTime = 0; } catch(e){}
              try { a.src = ''; } catch(e){}
              try { a.remove(); } catch(e){}
            }
            kill(r.__mer_note_song);
            r.__mer_note_song = null;
            r.__mer_note_audio_on = false;
            var nodes = r.document.querySelectorAll('audio[data-meridium-note="1"]');
            for (var i = 0; i < nodes.length; i++) kill(nodes[i]);
          } catch(e){}
        })();
        </script>
        """,
        height=1,
    )


def _start_note_audio() -> None:
    """Play I'll Never Smile Again on the parent page while the letter is open."""
    url = NOTE_SONG_URL
    st.components.v1.html(
        f"""
        <script>
        (function(){{
          var root = window.parent || window;
          var URL = {json.dumps(url)};
          if (root.__mer_note_audio_on && root.__mer_note_song && !root.__mer_note_song.paused) return;
          try {{
            if (root.__mer_note_song) {{
              try {{ root.__mer_note_song.pause(); root.__mer_note_song.remove(); }} catch(e){{}}
            }}
            var a = root.document.createElement('audio');
            a.src = URL;
            a.loop = true;
            a.volume = 0.5;
            a.setAttribute('data-meridium-note', '1');
            a.style.display = 'none';
            root.document.body.appendChild(a);
            root.__mer_note_song = a;
            root.__mer_note_audio_on = true;
            a.play().catch(function(){{
              function once(){{
                a.play().catch(function(){{}});
                try {{
                  root.document.removeEventListener('click', once);
                  root.document.removeEventListener('touchstart', once);
                }} catch(e){{}}
              }}
              root.document.addEventListener('click', once, {{once:true}});
              root.document.addEventListener('touchstart', once, {{once:true, passive:true}});
            }});
          }} catch(e){{}}
        }})();
        </script>
        """,
        height=1,
    )


def render_note() -> None:
    """Black screen, static, bloodied scientist letter + letter theme song."""
    _start_note_audio()

    st.markdown(
        """
    <style>
      .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
      section.main, .block-container {
        background: #000 !important;
        background-color: #000 !important;
      }
      [data-testid="stHeader"], [data-testid="stToolbar"],
      #MainMenu, footer, .stDeployButton {
        display: none !important; height: 0 !important;
      }
      .block-container { padding-top: 1rem !important; max-width: 720px !important; }

      .note-static {
        position: fixed; inset: 0; pointer-events: none; z-index: 1;
        opacity: 0.18;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.55'/%3E%3C/svg%3E");
        animation: nNoise 0.18s steps(3) infinite;
      }
      .note-scan {
        position: fixed; inset: 0; pointer-events: none; z-index: 2;
        background: repeating-linear-gradient(
          0deg, rgba(0,0,0,0.15) 0px, rgba(0,0,0,0.15) 1px,
          transparent 2px, transparent 3px);
        opacity: 0.35;
      }
      @keyframes nNoise {
        0% { transform: translate(0,0); }
        50% { transform: translate(1%,-1%); }
        100% { transform: translate(0,0); }
      }
      .note-wrap {
        position: relative; z-index: 5;
        display: flex; justify-content: center; padding: 12px 8px 8px;
      }
      .note-paper {
        position: relative;
        width: min(520px, 94vw);
        background:
          radial-gradient(ellipse at 18% 12%, rgba(90,0,0,0.35), transparent 45%),
          radial-gradient(ellipse at 78% 88%, rgba(60,0,0,0.4), transparent 40%),
          linear-gradient(165deg, #1a1210 0%, #120c0c 40%, #0c0808 100%);
        border: 1px solid #3a1515;
        box-shadow: 0 0 40px rgba(80,0,0,0.35), inset 0 0 60px rgba(0,0,0,0.5);
        padding: 28px 22px 32px;
        transform: rotate(-0.6deg);
        animation: noteIn 1.2s ease;
      }
      @keyframes noteIn {
        from { opacity: 0; filter: brightness(0.2); }
        to { opacity: 1; filter: brightness(1); }
      }
      .note-paper::after {
        content: "";
        position: absolute;
        right: 8%; bottom: 6%;
        width: 28%; height: 22%;
        background:
          radial-gradient(ellipse at 50% 30%, rgba(100,0,0,0.5), transparent 60%),
          radial-gradient(ellipse 6px 20px at 40% 80%, #4a0000 0%, transparent 70%);
        pointer-events: none;
        opacity: 0.9;
      }
      .note-head {
        font-family: ui-monospace, monospace;
        font-size: 0.65rem;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: #8b3030;
        margin-bottom: 14px;
      }
      .note-title {
        font-family: Georgia, "Times New Roman", serif;
        font-size: 1.35rem;
        color: #c4a0a0;
        margin-bottom: 6px;
      }
      .note-meta {
        font-family: ui-monospace, monospace;
        font-size: 0.7rem;
        color: #6a4040;
        margin-bottom: 18px;
        line-height: 1.5;
      }
      .note-blood-drip {
        position: absolute;
        left: 22%; top: 0;
        width: 3px; height: 48px;
        background: linear-gradient(180deg, #5a0000, transparent);
        opacity: 0.8;
      }
    </style>
    <div class="note-static"></div>
    <div class="note-scan"></div>
    <div class="note-wrap">
      <div class="note-paper">
        <div class="note-blood-drip"></div>
        <div class="note-head">Classified · recovered fragment</div>
        <div class="note-title">To whoever finds the door</div>
        <div class="note-meta">
          Dr. E. Voss · Observation Division<br/>
          Stained · incomplete · still active
        </div>
      </div>
    </div>
        """,
        unsafe_allow_html=True,
    )

    # Letter body (reliable Streamlit markdown)
    body_html = NOTE_BODY.strip().replace("\n", "<br/>")
    st.markdown(
        f"""
        <div style="
          max-width:520px;margin:0 auto 16px;padding:0 18px 8px;
          font-family:Georgia,serif;font-size:0.92rem;line-height:1.65;
          color:#b09090;position:relative;z-index:6;
        ">{body_html}</div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Close note", use_container_width=True, key="note_close"):
            _stop_note_audio()
            st.session_state.view = "home"
            st.rerun()
    with c2:
        if st.button("Open chat", use_container_width=True, key="note_chat"):
            _stop_note_audio()
            st.session_state.view = "chat"
            st.rerun()

    st.caption("The quote was a door. The letter is a map.")
    st.stop()
