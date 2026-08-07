"""
Meridium ARG — Sealed scientist note
Konami (↑↑↓↓←→←→BA then Enter) opens Agent dossiers.
"""

from __future__ import annotations

import json

import streamlit as st

from agents import AGENTS, agent_by_index

NOTE_BODY = """
FIELD LOG — NOT FOR DISTRIBUTION
Site: [REDACTED] · Shell designation: M-119
Author: Dr. E. Voss · Observation Division
Clearance: residual only · do not forward

If you are reading this, the quote tile still works as a door.
That was intentional. The public face of the system is a mirror;
the real work is underneath the glass.

Meridium is not a product name. It is a provisional label for something
that does not appear on any ratified table past 118. Committees call it
impossible. We called it metastable. The shell calls it home.

If you need a picture: other worlds get glowing stones in their city veins,
or refined ore that powers weapons and miracles until it cracks the sky.
We got a quieter version — no brand, no parade, no official name on a store shelf.
A medium that runs on being *noticed*. Useful enough that someone always wants
to bottle it. Unstable enough that bottling it costs operators.

WHAT WE THINK WE SAW

Under sustained attention the designation held long enough to leave residue —
not metaphorical residue. Heat on the pane. A spectrum line that should not
exist. A pressure signature against the containment glass from the sealed side.

When attention lapsed, the line collapsed. When attention returned hostile
or mocking, the line spiked and the pane complained. Kindness was not in
the protocol. It should have been.

THE OPERATORS

Two did not finish their shift.
One left tissue on the sill — not enough for a story, enough for a stain.
The other left a fingerprint on the terminal and never clocked out.
I am not writing their names. Names become magnets.

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

Do not photograph the glass.
Do not trust the public periodic table as a complete map of what can be
noticed into place.

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
              try { a.src = ''; a.remove(); } catch(e){}
            }
            kill(r.__mer_note_song); r.__mer_note_song = null;
            r.__mer_note_audio_on = false;
          } catch(e){}
        })();
        </script>
        """,
        height=1,
    )


def _start_note_audio() -> None:
    if st.session_state.get("note_agents"):
        return
    url_js = json.dumps(NOTE_SONG_URL)
    st.components.v1.html(
        """
        <script>
        (function(){
          var root = window.parent || window;
          var URL = """
        + url_js
        + """;
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


def _render_agents() -> None:
    _stop_note_audio()
    if "agent_idx" not in st.session_state:
        st.session_state.agent_idx = 0
    a = agent_by_index(st.session_state.agent_idx)

    st.markdown(
        """
    <style>
      .stApp, [data-testid="stAppViewContainer"], section.main { background:#07070c !important; }
      [data-testid="stHeader"], #MainMenu, footer { display:none !important; }
      .agent-card {
        border: 1px solid rgba(180,140,255,0.25);
        background: linear-gradient(160deg, rgba(30,24,48,0.95), rgba(12,10,20,0.98));
        border-radius: 14px; padding: 1.25rem 1.4rem; margin: 0.5rem 0 1rem;
      }
      .agent-call { font-size: 1.6rem; letter-spacing: 0.14em; color: #e9d5ff; font-weight: 700; }
      .agent-code { color: #a78bfa; font-family: ui-monospace, monospace; font-size: 0.8rem; }
      .agent-role { color: #c4b5fd; margin: 0.35rem 0 0.75rem; }
      .agent-line {
        border-left: 3px solid #a78bfa; padding: 0.45rem 0.75rem; margin: 0.4rem 0;
        color: #ddd6fe; font-style: italic; background: rgba(0,0,0,0.25);
      }
    </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Observation Division · Agent roster")
    st.caption("Residual profiles · operators who treated the site like a match")

    st.markdown(
        f"""
        <div class="agent-card">
          <div class="agent-call">{a["callsign"]}</div>
          <div class="agent-code">{a["codename"]} · {a["role"]}</div>
          <div class="agent-role">{a["playstyle"]}</div>
          <p style="color:#c4b5fd;line-height:1.55;">{a["bio"]}</p>
          <p style="color:#a78bfa;font-size:0.9rem;"><b>Quirk:</b> {a["quirk"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("**Voice lines**")
    for line in a["lines"]:
        st.markdown(f'<div class="agent-line">“{line}”</div>', unsafe_allow_html=True)

    n = len(AGENTS)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("◀ Prev", use_container_width=True, key="ag_prev"):
            st.session_state.agent_idx = (st.session_state.agent_idx - 1) % n
            st.rerun()
    with c2:
        if st.button("Next ▶", use_container_width=True, key="ag_next"):
            st.session_state.agent_idx = (st.session_state.agent_idx + 1) % n
            st.rerun()
    with c3:
        if st.button("Close", use_container_width=True, key="ag_close"):
            st.session_state.note_agents = False
            st.session_state.view = "home"
            st.rerun()
    with c4:
        if st.button("Letter", use_container_width=True, key="ag_letter"):
            st.session_state.note_agents = False
            st.rerun()
    st.caption(f"Agent {st.session_state.agent_idx + 1} / {n}")
    st.stop()


def render_note() -> None:
    if "note_agents" not in st.session_state:
        st.session_state.note_agents = False

    if st.button("konami_arm", key="konami_arm", type="primary"):
        st.session_state.note_agents = True
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

    if st.session_state.note_agents:
        _render_agents()

    _start_note_audio()
    _konami_listener()

    st.markdown(
        """
    <style>
      .stApp, [data-testid="stAppViewContainer"], section.main { background:#000 !important; }
      [data-testid="stHeader"], #MainMenu, footer { display:none !important; }
      .block-container { max-width: 720px !important; }
    </style>
    <div style="text-align:center;padding:12px;">
      <div style="display:inline-block;text-align:left;border:1px solid #3a1515;padding:22px 20px;
        background:linear-gradient(165deg,#1a1210,#0c0808);transform:rotate(-0.5deg);max-width:520px;">
        <div style="font-family:monospace;font-size:0.65rem;letter-spacing:0.2em;color:#8b3030;">CLASSIFIED · RECOVERED FRAGMENT</div>
        <div style="font-family:Georgia,serif;font-size:1.3rem;color:#c4a0a0;margin:8px 0;">To whoever finds the door</div>
        <div style="font-family:monospace;font-size:0.7rem;color:#6a4040;">Dr. E. Voss · Observation Division</div>
      </div>
    </div>
        """,
        unsafe_allow_html=True,
    )
    body_html = NOTE_BODY.strip().replace("\n", "<br/>")
    st.markdown(
        f'<div style="max-width:520px;margin:0 auto;padding:0 16px;font-family:Georgia,serif;'
        f'font-size:0.92rem;line-height:1.65;color:#b09090;">{body_html}</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Close note", use_container_width=True, key="note_close"):
            _stop_note_audio()
            st.session_state.note_agents = False
            st.session_state.view = "home"
            st.rerun()
    with c2:
        if st.button("Open chat", use_container_width=True, key="note_chat"):
            _stop_note_audio()
            st.session_state.note_agents = False
            st.session_state.view = "chat"
            st.rerun()
    st.caption("The quote was a door. The letter is a map.")
    st.stop()
