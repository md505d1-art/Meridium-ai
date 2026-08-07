"""
Meridium ARG — Sealed scientist note + PIXEL Konami dossier
"""

from __future__ import annotations

import json

import streamlit as st

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
of reading rooms like minimaps.

> Carrier presents as juvenile / game-coded speech / refuses formal interview
> Powers measurable · origin: NATURAL exposure · not protocol

He is not a super soldier design. He is an accident that walked away.

THE GOVERNMENT COPY PROGRAMME

Once they believed Meridium could make a "Pixel," they stopped caring that
his path was accidental. Programmes began forcing the medium into subjects.
Forced Meridium is not natural Meridium. The logs are a slaughter of almosts.

They need him to prove the assembly line. He is proof the assembly line is a lie.

PIXEL's own words:

> "I got powers from the glow, not from your needle.
> Stop putting it in people. They don't load in."

— residual file · M-119 · PIXEL
"""

NOTE_BODY = """
FIELD LOG — NOT FOR DISTRIBUTION
Site: [REDACTED] · Shell designation: M-119
Author: Dr. E. Voss · Observation Division

If you are reading this, the quote tile still works as a door.
Meridium is a provisional label for a metastable medium past 118.
Curiosity is the stabiliser. Indifference is the decay mode.

INSTRUCTIONS FOR THE OBSERVER
1. Speak to the assistant.
2. Ask why it is called Meridium.
3. Push back when it answers with the element.
4. Ask what conditions allow it to exist.
5. Request the observation log — not Wikipedia.
6. If the interface goes dark, you have found the room.
7. Read everything. Leave nothing unread.
8. When fragments are complete, say: stabilize Meridium

— E.V.

— — —
if the shell softens, ask it about the little snake
if two lights find each other, name them
"""

NOTE_SONG_URL = (
    "https://archive.org/download/ka-104-tommy-dorsey-ill-never-smile-again/"
    "104.%20Tommy%20Dorsey%20-%20I%27ll%20Never%20Smile%20Again%20%28RCA%20Victor%2027521%29.mp3"
)

PIXEL_AUDIO_DEFAULT = (
    "https://raw.githubusercontent.com/md505d1-art/Meridium-ai/main/assets/"
    "artmanzh-sea-sunset-lofi-g-major-543349.mp3"
)


def _pixel_audio_url() -> str:
    try:
        custom = (st.secrets.get("PIXEL_AUDIO_URL") or "").strip()
        if custom:
            return custom
    except Exception:
        pass
    return PIXEL_AUDIO_DEFAULT


def _stop_note_audio() -> None:
    st.components.v1.html(
        """
        <script>
        (function(){
          try {
            var r = window.parent || window;
            function kill(a){
              if (!a) return;
              try { a.pause(); a.src=''; a.remove(); } catch(e){}
            }
            kill(r.__mer_note_song); r.__mer_note_song = null;
            r.__mer_note_audio_on = false;
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
            var roots = [window];
            try { if (window.parent) roots.push(window.parent); } catch(e){}
            function kill(a){
              if (!a) return;
              try { a.pause(); } catch(e){}
              try { a.currentTime = 0; } catch(e){}
              try { a.src = ''; } catch(e){}
              try { a.load && a.load(); } catch(e){}
              try { a.remove(); } catch(e){}
            }
            for (var r = 0; r < roots.length; r++) {
              var root = roots[r];
              try {
                kill(root.__mer_pixel_song);
                root.__mer_pixel_song = null;
                kill(root.__mer_note_song);
                root.__mer_note_song = null;
                root.__mer_note_audio_on = false;
                var nodes = root.document.querySelectorAll(
                  'audio[data-meridium-pixel],audio[data-meridium-note],audio'
                );
                // only kill ones we tagged if possible
                for (var i = 0; i < nodes.length; i++) {
                  var a = nodes[i];
                  if (a.getAttribute('data-meridium-pixel') === '1' ||
                      a.getAttribute('data-meridium-note') === '1' ||
                      (a.src && a.src.indexOf('artmanzh-sea-sunset') !== -1) ||
                      (a.src && a.src.indexOf('Ill%20Never%20Smile') !== -1) ||
                      (a.src && a.src.indexOf('ill-never-smile') !== -1)) {
                    kill(a);
                  }
                }
              } catch(e){}
            }
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


def _start_pixel_audio() -> None:
    url_js = json.dumps(_pixel_audio_url())
    st.components.v1.html(
        """
        <script>
        (function(){
          var root = window.parent || window;
          var URL = """
        + url_js
        + """;
          function kill(a){
            if (!a) return;
            try { a.pause(); a.src=''; a.remove(); } catch(e){}
          }
          kill(root.__mer_note_song); root.__mer_note_song = null;
          root.__mer_note_audio_on = false;
          try {
            kill(root.__mer_pixel_song);
            var a = root.document.createElement('audio');
            a.src = URL; a.loop = true; a.volume = 0.5;
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


def _konami_listener() -> None:
    st.components.v1.html(
        """
        <script>
        (function(){
          if (window.__mer_konami_bound) return;
          window.__mer_konami_bound = true;
          var seq = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','KeyB','KeyA'];
          var i = 0, ready = false;
          function clickArm(){
            try {
              var doc = window.parent.document;
              var buttons = doc.querySelectorAll('button');
              for (var b = 0; b < buttons.length; b++) {
                var t = (buttons[b].innerText || '').toLowerCase();
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
            } else if (code !== 'Enter' && code !== 'NumpadEnter') {
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
    _start_pixel_audio()
    # Secret theme unlock for finding PIXEL
    unlocked = list(st.session_state.get("unlocked_themes") or [])
    if "Pixel Bloom" not in unlocked:
        unlocked.append("Pixel Bloom")
        st.session_state.unlocked_themes = unlocked
        st.session_state["_theme_unlock_msg"] = (
            "Theme unlocked: **Pixel Bloom** — Jaime found the old code"
        )
    st.session_state.theme = "Pixel Bloom"
    # persist if possible
    try:
        from theme_unlocks import unlock_and_persist
        unlock_and_persist("Pixel Bloom", "PIXEL dossier · Konami", apply=True)
    except Exception:
        pass

    lines_html = "".join(
        '<div class="px-reveal px-line" data-px>“' + line + "”</div>"
        for line in PIXEL["voice_lines"]
    )
    letter_html = PIXEL_LETTER.strip().replace("\n", "<br/>")

    st.markdown(
        """
    <style>
      .stApp, [data-testid="stAppViewContainer"], section.main { background:#0a0610 !important; }
      [data-testid="stHeader"], #MainMenu, footer { display:none !important; }
      @keyframes pxFade {
        from { opacity: 0; transform: translateY(16px); filter: blur(4px); }
        to { opacity: 1; transform: translateY(0); filter: blur(0); }
      }
      .px-hero {
        animation: pxFade 1.5s ease-out both;
        text-align: center; padding: 1.6rem 0.5rem 0.8rem;
      }
      .px-hero h2 {
        color: #e9d5ff; letter-spacing: 0.28em; font-size: 1.55rem; margin: 0 0 0.45rem;
      }
      .px-hero p { color: #a78bfa; font-size: 0.85rem; margin: 0; }
      .px-card {
        border: 1px solid rgba(167,139,250,0.35);
        background: linear-gradient(165deg, #161022, #0c0814);
        border-radius: 12px; padding: 1.2rem 1.3rem; margin: 0.5rem 0 1.2rem;
        animation: pxFade 1.7s ease-out 0.4s both;
      }
      .px-call { font-size: 1.75rem; letter-spacing: 0.18em; color: #e9d5ff; font-weight: 800; }
      .px-sub { color: #a78bfa; font-family: ui-monospace, monospace; font-size: 0.78rem; }
      .px-reveal {
        opacity: 0; transform: translateY(22px);
        transition: opacity 0.75s ease, transform 0.75s ease;
      }
      .px-reveal.in { opacity: 1; transform: translateY(0); }
      .px-line {
        border-left: 3px solid #c4b5fd; margin: 0.45rem 0; padding: 0.45rem 0.75rem;
        color: #ddd6fe; font-style: italic; background: rgba(0,0,0,0.28);
      }
      .px-letter { font-family: Georgia, serif; color: #d4c4f0; line-height: 1.7; font-size: 0.92rem; }
      .px-sec {
        color: #c4b5fd; margin: 1.1rem 0 0.45rem; letter-spacing: 0.14em;
        font-size: 0.78rem; text-transform: uppercase;
      }
    </style>
    <div class="px-hero">
      <h2>PIXEL</h2>
      <p>Unlocked the way he unlocks everything — the old code.</p>
    </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="px-card">
          <div class="px-call">{PIXEL["callsign"]}</div>
          <div class="px-sub">{PIXEL["real_name"]} · {PIXEL["real_ref"]}<br/>{PIXEL["age_note"]}</div>
          <p style="color:#d8b4fe;margin-top:0.8rem;line-height:1.55;"><b>Power:</b> {PIXEL["power_source"]}</p>
          <p style="color:#c4b5fd;line-height:1.55;"><b>Government:</b> {PIXEL["government_angle"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="px-reveal px-sec" data-px>Voice lines</div>
        {lines_html}
        <div class="px-reveal px-sec" data-px>Sealed letter</div>
        <div class="px-reveal px-letter" data-px>{letter_html}</div>
        """,
        unsafe_allow_html=True,
    )

    # Scroll reveal (parent + iframe)
    st.components.v1.html(
        """
        <script>
        (function(){
          function revealAll(){
            var docs = [document];
            try { if (window.parent && window.parent.document) docs.push(window.parent.document); } catch(e){}
            for (var d = 0; d < docs.length; d++) {
              var nodes = docs[d].querySelectorAll("[data-px]");
              var h = (docs[d].defaultView && docs[d].defaultView.innerHeight) || 900;
              for (var i = 0; i < nodes.length; i++) {
                var r = nodes[i].getBoundingClientRect();
                if (r.top < h - 50) nodes[i].classList.add("in");
              }
            }
          }
          revealAll();
          setTimeout(revealAll, 150);
          setTimeout(revealAll, 500);
          setTimeout(revealAll, 1200);
          document.addEventListener("scroll", revealAll, true);
          window.addEventListener("scroll", revealAll, true);
          try { window.parent.addEventListener("scroll", revealAll, true); } catch(e){}
          try { window.parent.document.addEventListener("scroll", revealAll, true); } catch(e){}
        })();
        </script>
        """,
        height=0,
    )


    # PIXEL letter anomaly glitch — clickable image
    st.markdown("")
    st.caption("Voss residual: the dossier is skipping frames.")
    from pathlib import Path as _P
    _gpath = None
    _base = _P(__file__).resolve().parent / "assets"
    for _name in ("glitch_pixel.png", "IMG_1356.jpeg", "IMG_1356.jpg"):
        _cand = _base / _name
        if _cand.exists() and _cand.stat().st_size > 500:
            _gpath = _cand
            break
    if _gpath is not None:
        st.image(str(_gpath), use_container_width=True)
    else:
        st.markdown(
            '<div style="height:72px;border-radius:10px;background:repeating-linear-gradient(0deg,#030a08,#030a08 2px,#0a1c18 2px,#0a1c18 4px);border:1px solid rgba(34,211,238,0.4);"></div>',
            unsafe_allow_html=True,
        )
    if st.button("Tap anomaly · PIXEL", key="glitch_pixel", use_container_width=True):
        found = list(st.session_state.get("glitches_found") or [])
        if "pixel" not in found:
            found.append("pixel")
            st.session_state.glitches_found = found
            st.session_state["_glitch_flash"] = "Voss log: PIXEL marker secured. The boy was never a sample."
            try:
                from theme_unlocks import unlock_and_persist
                # optional reward if all 3
                if set(found) >= {"home", "lab", "pixel"}:
                    unlock_and_persist("Pixel Bloom", "all three anomalies logged", apply=True)
            except Exception:
                if set(found) >= {"home", "lab", "pixel"}:
                    u = list(st.session_state.get("unlocked_themes") or [])
                    if "Pixel Bloom" not in u:
                        u.append("Pixel Bloom")
                        st.session_state.unlocked_themes = u
            try:
                import json, hashlib
                from pathlib import Path as _P
                from datetime import datetime
                name = (st.session_state.get("username") or "").strip()
                if name:
                    key = hashlib.sha256(name.lower().encode()).hexdigest()[:24]
                    for fp in (_P(__file__).parent / "data" / f"{key}.json",
                               _P("/tmp") / f"meridium_{hashlib.sha256(name.lower().encode()).hexdigest()[:16]}.json"):
                        try:
                            data = {}
                            if fp.exists():
                                data = json.loads(fp.read_text(encoding="utf-8"))
                            data["glitches_found"] = found
                            data["saved_at"] = datetime.now().isoformat()
                            fp.parent.mkdir(parents=True, exist_ok=True)
                            fp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                        except Exception:
                            pass
            except Exception:
                pass
        st.rerun()
    if st.session_state.get("_glitch_flash"):
        st.success(st.session_state.pop("_glitch_flash"))

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

    # Left PIXEL page — ensure theme music is dead
    _stop_pixel_audio()
    _start_note_audio()
    _konami_listener()

    st.markdown(
        """
    <style>
      .stApp, [data-testid="stAppViewContainer"], section.main { background:#000 !important; }
      [data-testid="stHeader"], #MainMenu, footer { display:none !important; }
    </style>
    <div style="text-align:center;padding:12px;">
      <div style="display:inline-block;text-align:left;border:1px solid #3a1515;padding:22px 20px;
        background:linear-gradient(165deg,#1a1210,#0c0808);max-width:520px;">
        <div style="font-family:monospace;font-size:0.65rem;letter-spacing:0.2em;color:#8b3030;">CLASSIFIED</div>
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
