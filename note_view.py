"""
Meridium ARG — Sealed scientist note
Konami (↑↑↓↓←→←→BA then Enter) opens Agent dossiers.
"""

from __future__ import annotations

import json

import streamlit as st

# --- PIXEL dossier (inline so app works even if agents.py missing on deploy) ---
try:
    from agents import PIXEL, PIXEL_LETTER
except Exception:
    PIXEL = {
        "callsign": "PIXEL",
        "real_name": "Jaime Santos",
        "real_ref": "subject zero · not a subject",
        "age_note": "Still talks like the ranked queue is life",
        "power_source": (
            "Natural Meridium radiation exposure — not injected, not refined, not consented by a lab"
        ),
        "government_angle": (
            "Observation Division residual files show state programmes trying to "
            "force Meridium into volunteers and prisoners to mass-produce what Pixel got by accident."
        ),
        "voice_lines": [
            "I'm not your lab rat. I got hit by the glow and lived. That's different.",
            "They keep saying 'replicate the Pixel event.' Bro I was playing games when it happened.",
            "Meridium isn't an ultimate you buy. It stuck to me. That's why their copies keep breaking.",
            "If the alarm sounds like a round timer, that's on me. Sorry. Not sorry.",
            "Tell the men in suits: forced samples aren't the same as natural ones. The glass already told them.",
            "Stabilize is not a cheat code. I checked.",
        ],
    }
    PIXEL_LETTER = """
DOSSIER — NOT FOR DISTRIBUTION
Ref: M-119 / PIXEL / Jaime Santos / "natural carrier"
Author: residual Observation Division clerk (unsigned)
Status: government replication programme active · denied in public

Civilian name on the residual badge: **Jaime Santos**.
They call him PIXEL because that is what he called himself in every queue
before the incident. Ranked. Arcade. Anything with a score. He still talks
like the world is a match lobby. That is not a cover identity. That is who
survived the exposure.

THE NATURAL EVENT

PIXEL was not recruited. He was not injected. He was not a volunteer form
signed under fluorescent lights.

He was near a residual Meridium bloom — unshielded, unlogged, the kind of
leak the committees pretend is weather. Radiation from the medium does not
behave like textbook fallout. It settles into people who are already
paying attention too hard: long hours, bright screens, the same focus that
holds a ranked game together at 3 a.m.

Something in him held the charge instead of cooking. Strength. Reflex. A way
of reading rooms like minimaps. The Division's first note is almost annoyed:

> Carrier presents as juvenile / game-coded speech / refuses formal interview
> Powers measurable · origin: NATURAL exposure · not protocol

He is not a super soldier design. He is an accident that walked away.

THE GOVERNMENT COPY PROGRAMME

Once they believed Meridium could make a "Pixel," they stopped caring that
his path was accidental.

Programmes (names redacted) began forcing the medium into subjects:
— "consent" under pressure
— prisoners offered sentence reductions
— volunteers who thought they were testing vitamins

Forced Meridium is not natural Meridium. The logs are a slaughter of almosts.
Spikes. Collapses. Subjects who heard alarms in their sleep. Subjects who
did not get up.

The glass in the sealed lab remembers the refined attempts. PIXEL remembers
the bloom that was never supposed to touch a civilian lane.

WHY HE MATTERS

They need him to prove the assembly line.
He is proof the assembly line is a lie.

Natural radiation carriers are rare. They cannot be ordered from a menu.
Every time a minister asks why the copies fail, the residual answer is the
same: because you cannot schedule an accident and call it a manufacture.

PIXEL's own words, logged against advice:

> "I got powers from the glow, not from your needle.
> Stop putting it in people. They don't load in."

VOICE / BEHAVIOUR

Expect childish cadence. Game metaphors. Konami codes. He unlocked this
page the same way he unlocks secret stages — because of course he did.

Do not confuse the voice with weakness. The medium that refused to kill him
still answers when he notices it. The government wants that on demand.
It is not on demand.

Clerk note ends.
If you found this through the sealed letter's old code: you are the kind of
curious the copies never account for.

— residual file · M-119 · PIXEL
"""



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




def _pixel_audio_file():
    """Local Pixabay download if present in repo."""
    from pathlib import Path as _P
    base = _P(__file__).parent
    for name in (
        "assets/pixel_theme.mp3",
        "assets/artmanzh-sea-sunset-lofi-g-major-543349.mp3",
        "artmanzh-sea-sunset-lofi-g-major-543349.mp3",
        "pixel_theme.mp3",
    ):
        fp = base / name
        if fp.exists() and fp.stat().st_size > 1000:
            return fp
    return None


def _start_pixel_audio() -> None:
    """Secret URL, else free fallback. Local file played via st.audio in UI."""
    url = "https://assets.mixkit.co/music/765/765.mp3"
    try:
        custom = (st.secrets.get("PIXEL_AUDIO_URL") or "").strip()
        if custom:
            url = custom
    except Exception:
        pass
    # Skip autoplay inject if local file will use st.audio
    if _pixel_audio_file() is not None:
        return
    url_js = json.dumps(url)
    st.components.v1.html(
        """
        <script>
        (function(){
          var root = window.parent || window;
          var URL = """ + url_js + """;
          function kill(a){
            if (!a) return;
            try { a.pause(); } catch(e){}
            try { a.src = ''; a.remove(); } catch(e){}
          }
          kill(root.__mer_note_song); root.__mer_note_song = null;
          root.__mer_note_audio_on = false;
          try {
            kill(root.__mer_pixel_song);
            var a = root.document.createElement('audio');
            a.src = URL; a.loop = true; a.volume = 0.45;
            a.setAttribute('data-meridium-pixel', '1');
            a.style.display = 'none';
            root.document.body.appendChild(a);
            root.__mer_pixel_song = a;
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


def _stop_pixel_audio() -> None:
    st.components.v1.html(
        """
        <script>
        (function(){
          try {
            var r = window.parent || window;
            var a = r.__mer_pixel_song;
            if (a) { try { a.pause(); a.src=''; a.remove(); } catch(e){} }
            r.__mer_pixel_song = null;
          } catch(e){}
        })();
        </script>
        """,
        height=1,
    )


def _render_agents() -> None:
    """Konami secret: PIXEL dossier — natural Meridium carrier."""
    _stop_note_audio()
    _start_pixel_audio()
    _pf = _pixel_audio_file()
    if _pf is not None:
        st.audio(str(_pf), format="audio/mp3")
        st.caption("Sea Sunset Lofi · ArtManzh (Pixabay)")
    st.markdown(
        """
    <style>
      .stApp, [data-testid="stAppViewContainer"], section.main { background:#0a0610 !important; }
      [data-testid="stHeader"], #MainMenu, footer { display:none !important; }
      .px-card {
        border: 1px solid rgba(167,139,250,0.35);
        background: linear-gradient(165deg, #161022, #0c0814);
        border-radius: 12px; padding: 1.2rem 1.3rem; margin-bottom: 1rem;
      }
      .px-call { font-size: 1.75rem; letter-spacing: 0.18em; color: #e9d5ff; font-weight: 800; }
      .px-sub { color: #a78bfa; font-family: ui-monospace, monospace; font-size: 0.78rem; margin-top: 0.25rem; }
      .px-line {
        border-left: 3px solid #c4b5fd; margin: 0.4rem 0; padding: 0.4rem 0.75rem;
        color: #ddd6fe; font-style: italic; background: rgba(0,0,0,0.28);
      }
    </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Secret dossier · PIXEL")
    st.caption("Unlocked the way he unlocks everything — the old code.")
    st.markdown(
        f"""
        <div class="px-card">
          <div class="px-call">{PIXEL["callsign"]}</div>
          <div class="px-sub">{PIXEL.get("real_name", "Jaime Santos")} · {PIXEL["real_ref"]}<br/>{PIXEL["age_note"]}</div>
          <p style="color:#d8b4fe;margin-top:0.8rem;line-height:1.55;"><b>Power:</b> {PIXEL["power_source"]}</p>
          <p style="color:#c4b5fd;line-height:1.55;"><b>Government:</b> {PIXEL["government_angle"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Music: free instrumental loop (not commercial / not MF DOOM — can\'t ship label tracks).")
    st.markdown("**Voice lines**")
    for line in PIXEL["voice_lines"]:
        st.markdown(f'<div class="px-line">“{line}”</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Sealed letter**")
    body = PIXEL_LETTER.strip().replace(chr(10), "<br/>")
    st.markdown(
        f'<div style="font-family:Georgia,serif;color:#d4c4f0;line-height:1.65;'
        f'font-size:0.92rem;max-width:640px;">{body}</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Close", use_container_width=True, key="px_close"):
            _stop_pixel_audio()
            st.session_state.note_agents = False
            st.session_state.view = "home"
            st.rerun()
    with c2:
        if st.button("Back to letter", use_container_width=True, key="px_back"):
            _stop_pixel_audio()
            st.session_state.note_agents = False
            st.rerun()
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
