"""
Meridium ARG — Sealed scientist note
------------------------------------
Quote of the day door + Konami Grom note scene.
Image is embedded so GitHub upload is not required.
"""

from __future__ import annotations

import base64
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

— — —
if the shell softens, ask it about the little snake
if two lights find each other, name them
"""

NOTE_SONG_URL = (
    "https://archive.org/download/ka-104-tommy-dorsey-ill-never-smile-again/"
    "104.%20Tommy%20Dorsey%20-%20I%27ll%20Never%20Smile%20Again%20%28RCA%20Victor%2027521%29.mp3"
)

_GROM_NOTE_B64 = """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"""


def _grom_note_bytes() -> bytes:
    return base64.b64decode(_GROM_NOTE_B64)


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
            var nodes = r.document.querySelectorAll(
              'audio[data-meridium-note="1"],audio[data-meridium-konami="1"]'
            );
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
    url_js = json.dumps(NOTE_SONG_URL)
    st.components.v1.html(
        """
        <script>
        (function(){
          var root = window.parent || window;
          var URL = """ + url_js + """;
          if (root.__mer_note_audio_on && root.__mer_note_song && !root.__mer_note_song.paused) return;
          try {
            if (root.__mer_note_song) {
              try { root.__mer_note_song.pause(); root.__mer_note_song.remove(); } catch(e){}
            }
            var a = root.document.createElement('audio');
            a.src = URL; a.loop = true; a.volume = 0.5;
            a.setAttribute('data-meridium-note', '1');
            a.style.display = 'none';
            root.document.body.appendChild(a);
            root.__mer_note_song = a;
            root.__mer_note_audio_on = true;
            a.play().catch(function(){
              function once(){ a.play().catch(function(){}); }
              root.document.addEventListener('click', once, {once:true});
              root.document.addEventListener('touchstart', once, {once:true, passive:true});
            });
          } catch(e){}
        })();
        </script>
        """,
        height=1,
    )


def _start_konami_audio() -> None:
    # Chill lo-fi (Mixkit free license) — soft modern vibe for Grom note
    url = "https://assets.mixkit.co/music/765/765.mp3"
    try:
        custom = (st.secrets.get("OWL_INTRO_URL") or "").strip()
        if custom:
            url = custom
    except Exception:
        pass
    url_js = json.dumps(url)
    st.components.v1.html(
        """
        <script>
        (function(){
          var root = window.parent || window;
          function kill(a){
            if (!a) return;
            try { a.pause(); } catch(e){}
            try { a.src = ''; a.remove(); } catch(e){}
          }
          kill(root.__mer_note_song); root.__mer_note_song = null;
          root.__mer_note_audio_on = false;
          var URL = """ + url_js + """;
          if (!URL) return;
          try {
            kill(root.__mer_konami_song);
            var a = root.document.createElement('audio');
            a.src = URL; a.loop = true; a.volume = 0.55;
            a.setAttribute('data-meridium-konami', '1');
            a.style.display = 'none';
            root.document.body.appendChild(a);
            root.__mer_konami_song = a;
            a.play().catch(function(){
              function once(){ a.play().catch(function(){}); }
              root.document.addEventListener('click', once, {once:true});
              root.document.addEventListener('touchstart', once, {once:true, passive:true});
            });
          } catch(e){}
        })();
        </script>
        """,
        height=1,
    )


def _konami_listener() -> None:
    st.components.v1.html(
        """
        <script>
        (function(){
          if (window.__mer_konami_bound) return;
          window.__mer_konami_bound = true;
          var seq = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','KeyB','KeyA'];
          var i = 0;
          var ready = false;
          function clickArm(){
            try {
              var doc = window.parent.document;
              var buttons = doc.querySelectorAll('button');
              for (var b = 0; b < buttons.length; b++) {
                var t = (buttons[b].innerText || buttons[b].textContent || '').toLowerCase();
                if (t.indexOf('konami') !== -1) { buttons[b].click(); return; }
              }
              var prim = doc.querySelector('button[kind="primary"]');
              if (prim) prim.click();
            } catch(err){}
          }
          function onKey(e){
            var code = e.code || e.key;
            if (code === 'b' || code === 'B') code = 'KeyB';
            if (code === 'a' || code === 'A') code = 'KeyA';
            if (ready && (code === 'Enter' || code === 'NumpadEnter')) {
              e.preventDefault(); ready = false; i = 0; clickArm(); return;
            }
            if (code === seq[i]) {
              i++;
              if (i >= seq.length) { i = 0; ready = true; }
            } else if (code === 'Enter' || code === 'NumpadEnter') {
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
    st.markdown("### Grom note")
    st.caption("A question left where the sealed log used to be.")
    try:
        # Smaller centered note (not full page width)
        left, mid, right = st.columns([1, 1.2, 1])
        with mid:
            st.image(_grom_note_bytes(), use_container_width=True)
    except Exception:
        st.markdown(
            """
        <div style="max-width:240px;margin:18px auto;background:#f5f0e8;padding:18px 18px 28px;
          border-radius:4px;box-shadow:0 8px 28px rgba(0,0,0,0.35);">
          <div style="background:#e8d4f0;min-height:200px;display:flex;align-items:center;
            justify-content:center;padding:28px 22px;">
            <div style="font-family:Georgia,cursive;color:#4a2a6a;font-size:1.1rem;
              line-height:1.7;text-align:center;">
              LUZ,<br/>will you<br/>go to Grom<br/>with me?<br/><br/>Amity
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


def render_note() -> None:
    if "note_konami" not in st.session_state:
        st.session_state.note_konami = False

    if st.button("konami_arm", key="konami_arm", type="primary"):
        st.session_state.note_konami = True
        st.rerun()
    st.markdown(
        """
    <style>
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
      section.main, .block-container { background: #000 !important; }
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
    # fix: use real newlines
    body_html = NOTE_BODY.strip().replace(chr(10), "<br/>")
    st.markdown(
        '<div style="max-width:520px;margin:0 auto 16px;padding:0 18px 8px;'
        'font-family:Georgia,serif;font-size:0.92rem;line-height:1.65;'
        'color:#b09090;position:relative;z-index:6;">'
        + body_html
        + "</div>",
        unsafe_allow_html=True,
    )
    
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
