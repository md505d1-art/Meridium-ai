"""
Meridium ARG — Sealed scientist note
------------------------------------
Opened from Quote of the day.
Konami code (↑↑↓↓←→←→BA) replaces the letter with a soft Lumity scene.
"""

from __future__ import annotations

import json
from pathlib import Path

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

— — —
if the shell softens, ask it about the little snake
if two lights find each other, name them
"""

NOTE_SONG_URL = (
    "https://archive.org/download/ka-104-tommy-dorsey-ill-never-smile-again/"
    "104.%20Tommy%20Dorsey%20-%20I%27ll%20Never%20Smile%20Again%20%28RCA%20Victor%2027521%29.mp3"
)

# Optional: put a file you have rights to at assets/owl_house_intro.mp3
# or set st.secrets["OWL_INTRO_URL"] on Streamlit Cloud
LOCAL_INTRO = Path(__file__).parent / "assets" / "owl_house_intro.mp3"
# Prefer real uploads; user has IMG_1336.jpeg in repo root
_BASE = Path(__file__).parent
KONAMI_IMG = next(
    (
        p
        for p in (
            _BASE / "assets" / "grom_note.jpg",
            _BASE / "grom_note.jpg",
            _BASE / "IMG_1336.jpeg",
            _BASE / "IMG_1336.jpg",
        )
        if p.exists() and p.stat().st_size > 1000
    ),
    _BASE / "assets" / "grom_note.jpg",
)


def _stop_note_audio() -> None:
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
            kill(r.__mer_note_song); r.__mer_note_song = null;
            kill(r.__mer_konami_song); r.__mer_konami_song = null;
            r.__mer_note_audio_on = false;
            var nodes = r.document.querySelectorAll('audio[data-meridium-note="1"],audio[data-meridium-konami="1"]');
            for (var i = 0; i < nodes.length; i++) kill(nodes[i]);
          } catch(e){}
        })();
        </script>
        """,
        height=1,
    )


def _start_note_audio() -> None:
    if st.session_state.get("note_konami"):
        return
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
            a.src = URL; a.loop = true; a.volume = 0.5;
            a.setAttribute('data-meridium-note', '1');
            a.style.display = 'none';
            root.document.body.appendChild(a);
            root.__mer_note_song = a;
            root.__mer_note_audio_on = true;
            a.play().catch(function(){{
              function once(){{ a.play().catch(function(){{}}); }}
              root.document.addEventListener('click', once, {{once:true}});
              root.document.addEventListener('touchstart', once, {{once:true, passive:true}});
            }});
          }} catch(e){{}}
        }})();
        </script>
        """,
        height=1,
    )


def _start_konami_audio() -> None:
    """Play user-supplied intro if present; otherwise keep silence (no Disney rip)."""
    url = ""
    try:
        url = (st.secrets.get("OWL_INTRO_URL") or "").strip()
    except Exception:
        url = ""
    # Local file cannot be served easily on Streamlit without static hosting —
    # prefer secrets URL. Still stop the letter song.
    st.components.v1.html(
        f"""
        <script>
        (function(){{
          var root = window.parent || window;
          function kill(a){{
            if (!a) return;
            try {{ a.pause(); }} catch(e){{}}
            try {{ a.src = ''; a.remove(); }} catch(e){{}}
          }}
          kill(root.__mer_note_song); root.__mer_note_song = null;
          root.__mer_note_audio_on = false;
          var URL = {json.dumps(url)};
          if (!URL) return;
          try {{
            kill(root.__mer_konami_song);
            var a = root.document.createElement('audio');
            a.src = URL; a.loop = true; a.volume = 0.55;
            a.setAttribute('data-meridium-konami', '1');
            a.style.display = 'none';
            root.document.body.appendChild(a);
            root.__mer_konami_song = a;
            a.play().catch(function(){{
              function once(){{ a.play().catch(function(){{}}); }}
              root.document.addEventListener('click', once, {{once:true}});
              root.document.addEventListener('touchstart', once, {{once:true, passive:true}});
            }});
          }} catch(e){{}}
        }})();
        </script>
        """,
        height=1,
    )


def _konami_listener() -> None:
    """↑↑↓↓←→←→BA then Enter → arm Grom note scene."""
    st.components.v1.html(
        """
        <script>
        (function(){
          if (window.__mer_konami_bound) return;
          window.__mer_konami_bound = true;
          var seq = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','KeyB','KeyA'];
          var i = 0;
          var ready = false; // sequence complete — waiting for Enter

          function clickArm(){
            try {
              var doc = window.parent.document;
              var buttons = doc.querySelectorAll('button');
              for (var b = 0; b < buttons.length; b++) {
                var t = (buttons[b].innerText || buttons[b].textContent || '').toLowerCase();
                if (t.indexOf('konami') !== -1) {
                  buttons[b].click();
                  return;
                }
              }
              // fallback: primary hidden button
              var prim = doc.querySelector('button[kind="primary"]');
              if (prim) prim.click();
            } catch(err){}
          }

          function onKey(e){
            var code = e.code || e.key;
            if (code === 'b' || code === 'B') code = 'KeyB';
            if (code === 'a' || code === 'A') code = 'KeyA';

            // After full sequence, Enter confirms
            if (ready && (code === 'Enter' || code === 'NumpadEnter')) {
              e.preventDefault();
              ready = false;
              i = 0;
              clickArm();
              return;
            }

            if (code === seq[i]) {
              i++;
              if (i >= seq.length) {
                i = 0;
                ready = true;
                // optional: brief visual cue via title
                try { window.parent.document.title = '…'; } catch(e){}
              }
            } else if (code === 'Enter' || code === 'NumpadEnter') {
              // Enter before sequence complete — ignore for konami
            } else {
              ready = false;
              i = (code === seq[0]) ? 1 : 0;
            }
          }

          document.addEventListener('keydown', onKey);
          try { window.parent.document.addEventListener('keydown', onKey); } catch(e){}
        })();
        </script>
        """,
        height=1,
    )


def _render_konami_scene() -> None:
    _start_konami_audio()
    try:
        from app import unlock_theme
        unlock_theme("Lumity Glow", "Grom note · she asked")
    except Exception:
        unlocked = list(st.session_state.get("unlocked_themes") or [])
        if "Lumity Glow" not in unlocked:
            unlocked.append("Lumity Glow")
            st.session_state.unlocked_themes = unlocked

    st.markdown(
        """
    <style>
      .stApp, [data-testid="stAppViewContainer"], section.main, .block-container {
        background: #0a0610 !important;
      }
      [data-testid="stHeader"], #MainMenu, footer { display: none !important; }
    </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Soft interference")
    st.caption("The sealed note folded into something kinder.")
    shown = False
    if KONAMI_IMG.exists():
        try:
            st.image(str(KONAMI_IMG), use_container_width=True)
            shown = True
        except Exception:
            shown = False
    if not shown:
        # HTML fallback — always works even if jpg missing/corrupt on GitHub
        st.markdown(
            """
        <div style="max-width:340px;margin:18px auto;background:#f5f0e8;
          padding:18px 18px 28px;border-radius:4px;
          box-shadow:0 8px 28px rgba(0,0,0,0.35);">
          <div style="background:#e8d4f0;min-height:280px;display:flex;
            align-items:center;justify-content:center;padding:28px 22px;">
            <div style="font-family:Georgia,'Segoe Script',cursive;color:#4a2a6a;
              font-size:1.35rem;line-height:1.7;text-align:center;">
              LUZ,<br/>will you<br/>go to Grom<br/>with me?<br/><br/>
              <span style="font-size:1.15rem;">Amity</span>
            </div>
          </div>
        </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown(
        """
        <p style="text-align:center;color:#e9d5ff;font-family:Georgia,serif;line-height:1.7;">
        A question written carefully.<br/>
        A name signed like a heartbeat.<br/>
        <span style="color:#f9a8d4;">She said yes.</span>
        </p>
        """,
        unsafe_allow_html=True,
    )
    if not _intro_url():
        st.caption("Music: set Streamlit secret OWL_INTRO_URL to an audio file you have rights to (Owl House intro cannot be bundled).")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Close", use_container_width=True, key="konami_close"):
            _stop_note_audio()
            st.session_state.note_konami = False
            st.session_state.view = "home"
            st.rerun()
    with c2:
        if st.button("Open chat", use_container_width=True, key="konami_chat"):
            _stop_note_audio()
            st.session_state.note_konami = False
            st.session_state.view = "chat"
            st.rerun()
    st.stop()


def _intro_url() -> str:
    try:
        return (st.secrets.get("OWL_INTRO_URL") or "").strip()
    except Exception:
        return ""


def render_note() -> None:
    if "note_konami" not in st.session_state:
        st.session_state.note_konami = False

    # Hidden arm button for JS Konami success
    if st.button("konami_arm", key="konami_arm", type="primary"):
        st.session_state.note_konami = True
        st.rerun()
    st.markdown(
        """
    <style>
      /* hide the arm button — JS clicks it */
      div[data-testid="stButton"]:has(button[kind="primary"]) {
        position: fixed !important; left: -9999px !important; height: 0 !important;
        opacity: 0 !important; pointer-events: none !important;
      }
    </style>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.note_konami:
        _render_konami_scene()

    _start_note_audio()
    _konami_listener()

    st.markdown(
        """
    <style>
      .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
      section.main, .block-container {
        background: #000 !important;
      }
      [data-testid="stHeader"], [data-testid="stToolbar"],
      #MainMenu, footer, .stDeployButton { display: none !important; }
      .block-container { padding-top: 1rem !important; max-width: 720px !important; }
      .note-static {
        position: fixed; inset: 0; pointer-events: none; z-index: 1; opacity: 0.18;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.55'/%3E%3C/svg%3E");
        animation: nNoise 0.18s steps(3) infinite;
      }
      .note-scan {
        position: fixed; inset: 0; pointer-events: none; z-index: 2;
        background: repeating-linear-gradient(0deg, rgba(0,0,0,0.15) 0px, rgba(0,0,0,0.15) 1px, transparent 2px, transparent 3px);
        opacity: 0.35;
      }
      @keyframes nNoise {
        0% { transform: translate(0,0); }
        50% { transform: translate(1%,-1%); }
        100% { transform: translate(0,0); }
      }
      .note-wrap { position: relative; z-index: 5; display: flex; justify-content: center; padding: 12px 8px 8px; }
      .note-paper {
        position: relative; width: min(520px, 94vw);
        background:
          radial-gradient(ellipse at 18% 12%, rgba(90,0,0,0.35), transparent 45%),
          linear-gradient(165deg, #1a1210 0%, #120c0c 40%, #0c0808 100%);
        border: 1px solid #3a1515;
        box-shadow: 0 0 40px rgba(80,0,0,0.35);
        padding: 28px 22px 24px;
        transform: rotate(-0.6deg);
      }
      .note-head { font-family: ui-monospace, monospace; font-size: 0.65rem; letter-spacing: 0.22em;
        text-transform: uppercase; color: #8b3030; margin-bottom: 14px; }
      .note-title { font-family: Georgia, serif; font-size: 1.35rem; color: #c4a0a0; margin-bottom: 6px; }
      .note-meta { font-family: ui-monospace, monospace; font-size: 0.7rem; color: #6a4040; margin-bottom: 8px; }
    </style>
    <div class="note-static"></div>
    <div class="note-scan"></div>
    <div class="note-wrap">
      <div class="note-paper">
        <div class="note-head">Classified · recovered fragment</div>
        <div class="note-title">To whoever finds the door</div>
        <div class="note-meta">Dr. E. Voss · Observation Division<br/>Stained · incomplete · still active</div>
      </div>
    </div>
        """,
        unsafe_allow_html=True,
    )

    body_html = NOTE_BODY.strip().replace("\n", "<br/>")
    st.markdown(
        f"""
        <div style="max-width:520px;margin:0 auto 16px;padding:0 18px 8px;
          font-family:Georgia,serif;font-size:0.92rem;line-height:1.65;
          color:#b09090;position:relative;z-index:6;">{body_html}</div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Desktop: ↑↑↓↓←→←→BA then Enter")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Close note", use_container_width=True, key="note_close"):
            _stop_note_audio()
            st.session_state.note_konami = False
            st.session_state.view = "home"
            st.rerun()
    with c2:
        if st.button("Open chat", use_container_width=True, key="note_chat"):
            _stop_note_audio()
            st.session_state.note_konami = False
            st.session_state.view = "chat"
            st.rerun()

    st.caption("The quote was a door. The letter is a map.")
    st.stop()
