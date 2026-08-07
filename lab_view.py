"""
Meridium ARG — Interactive lab room (UI)
----------------------------------------
Call from app.py when view == "lab":

    from lab_view import render_lab
    if st.session_state.view == "lab":
        render_lab()
"""

from __future__ import annotations

import streamlit as st


HOTSPOTS = [
    (
        "glass",
        "Cracked containment glass",
        "**Containment pane — fracture report**\n\n"
        "The glass did not break inward. It *ballooned*, then starred from a point "
        "the size of a fingertip. Something pressed from the sealed side until the pane gave.\n\n"
        "Along the gasket: a dark film, half-dried. When the emergency light hits it, "
        "it looks almost black-red — thicker than blood, stickier, with a metallic smell "
        "the old techs swore was not copper.\n\n"
        "One hairline crack still weeps a slow bead every few minutes. "
        "Nobody has wiped it. Nobody wants to know if it starts again when watched.\n\n"
        "*Margin, shaky ink:* **M-119 does not like prolonged observation.**",
    ),
    (
        "floor",
        "Bloodstained note (floor)",
        "**Floor note — torn, boot-marked, stained**\n\n"
        "The paper is curled and stiff where a dark fluid soaked the bottom third. "
        "The stain has a brown-black crust at the edge and a dull sheen in the middle — "
        "like old blood that never fully dried.\n\n"
        "Readable lines:\n\n"
        "> If you can read this, the shell still answers.\n"
        "> Do not trust the public table. 118 was a courtesy to the living.\n"
        "> Meridium is not mined. It is *noticed* into place.\n"
        "> Stabilization requires an observer who stays. The ones who ran left tissue on the sill.\n\n"
        "A partial footprint crosses the stain. The tread is human. "
        "The smear beside it is not a clean shape.",
    ),
    (
        "bench",
        "Abandoned lab bench",
        "**Bench — interrupted work**\n\n"
        "Instruments died mid-cycle. One screen locked on `OBS: TRACE` with a red overflow bar.\n\n"
        "A tray holds swabs gone rust-dark. One cotton tip is stiff, clotted, as if it pulled "
        "something wet from a surface that should have been sterile. "
        "A scalpel lies beside them; the blade has a thin, dried line along the edge — "
        "not fresh, not clean.\n\n"
        "Drawer label scratched out. Under the gouges, in pencil: **MERIDIUM**.\n\n"
        "Chair kicked back. Dark droplets lead from the bench toward the door, then stop "
        "as if whatever left them was lifted off the floor.",
    ),
    (
        "light",
        "Pulsing alarm light",
        "**Emergency beacon — local only**\n\n"
        "The red pulse is not on the building grid. It belongs to the shell.\n\n"
        "Interval is wrong: three quick flares, a hitch, then a long burn — "
        "like a panicked heartbeat trying to remember a pattern.\n\n"
        "Under the housing, old tape. Handwriting in grease pencil:\n\n"
        "> When the light goes solid, stop looking at the glass.\n"
        "> When the light goes dark, do not assume it left.\n\n"
        "A fine spatter rings the fixture. Tiny, dry, the colour of old scabs.",
    ),
    (
        "window",
        "Blacked-out window",
        "**Observation window — painted shut**\n\n"
        "Exterior paint, slapped on fast. From this side, fingernail and something harder "
        "clawed through to the glass. The scratches form a crooked **119**.\n\n"
        "At the bottom of the frame, a smear where a hand slid and slipped — "
        "skin-oil mixed with a darker streak. "
        "Someone braced here. Someone bled a little. Someone left.\n\n"
        "If you cup your eyes against the unpainted flecks, the corridor beyond "
        "does not resolve into a normal hallway. Depth goes wrong. "
        "The log only says: *do not photograph.*",
    ),
    (
        "terminal",
        "Dead terminal",
        "**Terminal — last surviving lines**\n\n"
        "```\n"
        "STATUS........ METASTABLE\n"
        "REF........... M-119\n"
        "PUBLIC........ DENIED\n"
        "CASUALTY...... [REDACTED]\n"
        "NOTE.......... designation persists in shell\n"
        "NOTE.......... organic trace on sill / glass / floor\n"
        "NOTE.......... do not re-enter without observer protocol\n"
        "CMD........... stabilize Meridium\n"
        "```\n\n"
        "The cursor still blinks in the black. "
        "A dried fingerprint sits on the spacebar — dark at the ridges, "
        "as if the operator did not wash before the final command.\n\n"
        "The rest of the disk reads as static. "
        "Whatever finished the shift did not log out cleanly.",
    ),
]


def _stop_lab_audio_html() -> None:
    st.components.v1.html(
        """
        <script>
        try {
          var r = window.parent || window;
          r.__mer_audio_on = false;
          if (r.__mer_song_timer) clearTimeout(r.__mer_song_timer);
          if (r.__mer_heartaches) {
            try { r.__mer_heartaches.pause(); r.__mer_heartaches.remove(); } catch(e){}
            r.__mer_heartaches = null;
          }
          if (r.__mer_siren) {
            try { r.__mer_siren.pause(); r.__mer_siren.remove(); } catch(e){}
            r.__mer_siren = null;
          }
          var nodes = r.document.querySelectorAll('audio[data-meridium="1"]');
          for (var i=0;i<nodes.length;i++) {
            try { nodes[i].pause(); nodes[i].remove(); } catch(e){}
          }
        } catch (e) {}
        </script>
        """,
        height=0,
    )


def render_lab() -> None:
    """Full-screen black lab: intro -> transition -> interactive room."""
    if "lab_found" not in st.session_state:
        st.session_state.lab_found = set()
    if "lab_intro_done" not in st.session_state:
        st.session_state.lab_intro_done = False

    # ---- INTRO ----
    if not st.session_state.lab_intro_done:
        st.markdown(
            """
        <link href="https://fonts.googleapis.com/css2?family=Indie+Flower&display=swap" rel="stylesheet">
        <style>
          html, body, .stApp,
          [data-testid="stAppViewContainer"],
          [data-testid="stHeader"],
          section.main, .block-container {
            background: #000 !important;
            background-color: #000 !important;
          }
          [data-testid="stHeader"], [data-testid="stToolbar"],
          [data-testid="stDecoration"], #MainMenu, footer, .stDeployButton {
            display: none !important; height: 0 !important;
          }
          .block-container { padding-top: 0 !important; max-width: 100% !important; }
          #lab-full-black {
            position: fixed !important; inset: 0 !important;
            z-index: 999990 !important; background: #000;
            animation: labRedFlash 3s ease-in-out forwards;
          }
          @keyframes labRedFlash {
            0%,10%,35%,65% { background: #000; }
            5%,15%,28%,42%,58%,72% { background: #ff0000; }
            20%,50%,80% { background: #1a0000; }
            88% { background: #990000; }
            100% { background: #000; }
          }
          #lab-vhs, #lab-vhs-scan, #lab-vhs-track, #lab-vhs-rgb {
            position: fixed !important; inset: 0 !important; pointer-events: none !important;
          }
          #lab-vhs {
            z-index: 999992 !important; opacity: 0.22; mix-blend-mode: screen;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.55'/%3E%3C/svg%3E");
            animation: vhsNoise 0.15s steps(4) infinite;
          }
          #lab-vhs-scan {
            z-index: 999993 !important; opacity: 0.35;
            background: repeating-linear-gradient(0deg, rgba(0,0,0,0.15) 0px, rgba(0,0,0,0.15) 1px, transparent 2px, transparent 4px);
          }
          #lab-vhs-track {
            z-index: 999994 !important; left: 0; right: 0; height: 18%;
            background: linear-gradient(180deg, transparent, rgba(255,255,255,0.04) 40%, rgba(0,0,0,0.25) 50%, transparent);
            animation: vhsTrack 4.5s linear infinite; opacity: 0.55;
          }
          #lab-vhs-rgb {
            z-index: 999991 !important;
            box-shadow: inset 0 0 80px rgba(0,0,0,0.65);
            background: linear-gradient(90deg, rgba(255,0,0,0.03), transparent 40%, rgba(0,255,255,0.03));
            opacity: 0.5;
          }
          @keyframes vhsNoise {
            0% { transform: translate(0,0); }
            25% { transform: translate(-1%,1%); }
            50% { transform: translate(1%,-1%); }
            100% { transform: translate(0,0); }
          }
          @keyframes vhsTrack { 0% { top: -20%; } 100% { top: 120%; } }
          #lab-blood-msg {
            position: fixed !important; inset: 0 !important; z-index: 999995 !important;
            display: flex !important; align-items: center !important; justify-content: center !important;
            flex-direction: column !important; background: transparent !important;
            opacity: 0; animation: labBloodIn 1.2s ease forwards; animation-delay: 3s;
            pointer-events: none;
          }
          #lab-blood-msg span.blood {
            position: relative; color: #6e0000;
            font-size: clamp(1.85rem, 6.5vw, 3.1rem);
            font-family: "Indie Flower", cursive; letter-spacing: 0.12em;
            text-align: center; max-width: 92%; line-height: 1.4;
            transform: rotate(-3deg) skewX(-2deg);
            text-shadow: 0 1px 0 #4a0000, 0 2px 0 #3a0000, 1px 3px 0 #5a0000,
              -1px 4px 0 #2a0000, 0 0 12px #8b0000, 0 0 28px rgba(100,0,0,0.9);
            -webkit-text-stroke: 0.5px #2a0000;
          }
          #lab-blood-msg span.blood::after {
            content: ""; position: absolute; left: 12%; right: 18%; top: 95%; height: 40px;
            background:
              radial-gradient(ellipse 3px 26px at 25% 0%, #7a0000 0%, transparent 75%),
              radial-gradient(ellipse 4px 18px at 55% 0%, #5a0000 0%, transparent 70%),
              radial-gradient(ellipse 3px 30px at 75% 0%, #8b0000 0%, transparent 75%);
            animation: labDrip 2s ease-out forwards; animation-delay: 3.2s;
          }
          #lab-press-hint {
            margin-top: 2.75rem; color: #8a2828;
            font-family: "Indie Flower", Georgia, cursive; font-size: 1.15rem;
            letter-spacing: 0.12em; opacity: 0;
            animation: labBloodIn 1s ease forwards; animation-delay: 4s;
          }
          #lab-press-sub {
            margin-top: 0.65rem; color: #3a1818;
            font-family: ui-monospace, monospace; font-size: 0.62rem;
            letter-spacing: 0.18em; opacity: 0;
            animation: labBloodIn 1s ease forwards; animation-delay: 4.4s;
          }
          @keyframes labBloodIn { from { opacity: 0; } to { opacity: 1; } }
          @keyframes labDrip {
            0% { opacity: 0; transform: scaleY(0.2); transform-origin: top; }
            100% { opacity: 0.95; transform: scaleY(1); transform-origin: top; }
          }
          div[data-testid="stForm"] {
            position: fixed !important; bottom: 4px !important; left: 4px !important;
            opacity: 0.03 !important; z-index: 999999 !important; width: 80px !important;
          }
        </style>
        <div id="lab-full-black"></div>
        <div id="lab-vhs-rgb"></div>
        <div id="lab-vhs"></div>
        <div id="lab-vhs-scan"></div>
        <div id="lab-vhs-track"></div>
        <div id="lab-blood-msg">
          <span class="blood">you're not supposed to know</span>
          <div id="lab-press-hint">Enter into the lab</div>
          <div id="lab-press-sub">press the screen or enter...</div>
        </div>
            """,
            unsafe_allow_html=True,
        )

        st.components.v1.html(
            """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<style>
  html, body { margin: 0; background: transparent; }
  .wrap { display: flex; flex-direction: column; align-items: center; padding: 12px 8px; }
  #enterBtn {
    width: min(240px, 85vw); padding: 12px 16px; border-radius: 4px;
    border: 1px solid #4a0c0c; background: #100303; color: #a02020;
    font-family: "Indie Flower", Georgia, cursive; font-size: 1.05rem;
    letter-spacing: 0.1em; cursor: pointer; opacity: 0;
    animation: showEnter 0.7s ease forwards; animation-delay: 4.2s;
    -webkit-tap-highlight-color: transparent;
  }
  @keyframes showEnter { to { opacity: 1; } }
  #enterBtn:active { color: #ff3030; background: #1a0505; }
</style>
</head>
<body>
  <div class="wrap">
    <button id="enterBtn" type="button">Enter into the lab</button>
  </div>
<script>
(function(){
  var root = window.parent || window;
  var SIREN_URL = 'https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3';
  var SONG_URL = 'https://archive.org/download/al-bowlly-sid-phillips-his-melodians-heartaches/Al%20Bowlly%2C%20Sid%20Phillips%20%26%20His%20Melodians%20-%20Heartaches.mp3';

  function makeParentAudio(url, loop, vol){
    // Attach to parent DOM so sound survives when this iframe is destroyed (entering lab)
    try {
      var a = root.document.createElement('audio');
      a.src = url;
      a.preload = 'auto';
      a.loop = !!loop;
      a.volume = vol;
      a.setAttribute('data-meridium', '1');
      a.style.display = 'none';
      root.document.body.appendChild(a);
      return a;
    } catch(e) {
      var a2 = new Audio(url);
      a2.loop = !!loop;
      a2.volume = vol;
      return a2;
    }
  }

  function ensureAudio(){
    // Already playing Heartaches in the lab — leave it alone
    if (root.__mer_heartaches && !root.__mer_heartaches.paused) {
      root.__mer_audio_on = true;
      return;
    }
    if (root.__mer_audio_on && root.__mer_siren && !root.__mer_siren.paused) return;

    root.__mer_audio_on = true;

    try {
      if (root.__mer_siren) { try { root.__mer_siren.pause(); root.__mer_siren.remove(); } catch(e){} }
    } catch(e){}

    // Siren on parent page
    try {
      var siren = makeParentAudio(SIREN_URL, true, 0.8);
      root.__mer_siren = siren;
      var sp = siren.play();
      if (sp && sp.catch) {
        sp.catch(function(){
          setTimeout(function(){ siren.play().catch(function(){}); }, 250);
        });
      }
    } catch(e){}

    if (root.__mer_song_timer) clearTimeout(root.__mer_song_timer);
    root.__mer_song_timer = setTimeout(function(){
      try {
        if (root.__mer_siren) {
          root.__mer_siren.pause();
          try { root.__mer_siren.remove(); } catch(e){}
          root.__mer_siren = null;
        }
      } catch(e){}
      try {
        if (root.__mer_heartaches && !root.__mer_heartaches.paused) return;
        if (root.__mer_heartaches) {
          try { root.__mer_heartaches.pause(); root.__mer_heartaches.remove(); } catch(e){}
        }
        var song = makeParentAudio(SONG_URL, true, 0.55);
        root.__mer_heartaches = song;
        var hp = song.play();
        if (hp && hp.catch) {
          hp.catch(function(){
            setTimeout(function(){ song.play().catch(function(){}); }, 250);
          });
        }
      } catch(e){}
    }, 3500);
  }

  // AUTO PLAY immediately + a few retries (desktop)
  ensureAudio();
  setTimeout(ensureAudio, 400);
  setTimeout(ensureAudio, 1200);
  setTimeout(ensureAudio, 2500);

  function submitEnter(){
    ensureAudio();
    try {
      var btn = root.document.querySelector('div[data-testid="stForm"] button');
      if (btn) btn.click();
    } catch(e){}
  }

  var enterBtn = document.getElementById('enterBtn');
  if (enterBtn) {
    enterBtn.addEventListener('click', function(e){
      e.stopPropagation();
      submitEnter();
    });
  }
  document.addEventListener('keydown', function(e){
    if (e.key === 'Enter') submitEnter();
  });
  try {
    root.document.addEventListener('keydown', function(e){
      if (e.key === 'Enter') submitEnter();
    });
  } catch(e){}
})();
</script>
</script>
</body></html>
            """,
            height=90,
        )

        with st.form("lab_enter_form"):
            go = st.form_submit_button("enter")
        if go:
            st.session_state.lab_intro_done = True
            st.session_state.lab_flicker = True
            st.rerun()
        st.stop()

    # ---- TRANSITION ----
    if st.session_state.get("lab_flicker"):
        st.markdown(
            """
        <style>
          .stApp, [data-testid="stAppViewContainer"], section.main, .block-container {
            background: #000 !important;
          }
          #lab-transition {
            position: fixed; inset: 0; z-index: 999999;
            pointer-events: none; background: #000;
            animation: labDoor 2.6s ease-in-out forwards;
          }
          #lab-transition-static {
            position: fixed; inset: 0; z-index: 1000000;
            pointer-events: none; opacity: 0;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.6'/%3E%3C/svg%3E");
            animation: staticBurst 2.6s steps(6) forwards;
          }
          #lab-transition-scan {
            position: fixed; inset: 0; z-index: 1000001;
            pointer-events: none;
            background: repeating-linear-gradient(0deg, rgba(0,0,0,0.2) 0px, rgba(0,0,0,0.2) 1px, transparent 2px, transparent 3px);
            animation: scanFade 2.6s ease forwards;
          }
          @keyframes labDoor {
            0% { background: #000; opacity: 1; }
            12% { background: #2a2a18; opacity: 1; }
            16% { background: #000; opacity: 1; }
            28% { background: #4a4830; opacity: 1; }
            32% { background: #0a0a08; opacity: 1; }
            45% { background: #5a5640; opacity: 1; }
            55% { background: #1a1810; opacity: 1; }
            70% { background: #2a2818; opacity: 0.7; }
            100% { background: transparent; opacity: 0; }
          }
          @keyframes staticBurst {
            0%, 100% { opacity: 0; }
            10% { opacity: 0.5; }
            30% { opacity: 0.2; }
            50% { opacity: 0.45; }
            80% { opacity: 0.15; }
          }
          @keyframes scanFade {
            0% { opacity: 0.55; }
            100% { opacity: 0; }
          }
          .lab-fade-in {
            animation: labFadeIn 1.4s ease forwards;
            animation-delay: 1.5s;
            opacity: 0;
          }
          @keyframes labFadeIn {
            from { opacity: 0; filter: brightness(0.1); }
            to { opacity: 1; filter: brightness(1); }
          }
        </style>
        <div id="lab-transition"></div>
        <div id="lab-transition-static"></div>
        <div id="lab-transition-scan"></div>
            """,
            unsafe_allow_html=True,
        )
        st.session_state.lab_flicker = False

    # ---- ROOM ----
    st.markdown(
        """
    <style>
      .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: #000 !important;
      }
      .lab-hero {
        position: relative; min-height: 200px; border-radius: 16px;
        background:
          radial-gradient(ellipse at 50% 20%, rgba(120,0,0,0.45), transparent 55%),
          radial-gradient(ellipse at 70% 80%, rgba(40,0,0,0.5), transparent 50%),
          #050505;
        border: 1px solid #3a1515; overflow: hidden; margin-bottom: 12px;
      }
      .lab-vhs-room {
        position: fixed; inset: 0; pointer-events: none; z-index: 50; opacity: 0.12;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E");
        animation: vhsNoise 0.2s steps(3) infinite;
      }
      .lab-vhs-scanlines {
        position: fixed; inset: 0; pointer-events: none; z-index: 51;
        background: repeating-linear-gradient(0deg, rgba(0,0,0,0.12) 0px, rgba(0,0,0,0.12) 1px, transparent 2px, transparent 3px);
        opacity: 0.4;
      }
      @keyframes vhsNoise {
        0% { transform: translate(0,0); }
        50% { transform: translate(1%,-1%); }
        100% { transform: translate(0,0); }
      }
      .lab-scan {
        position: absolute; inset: 0;
        background: repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(255,0,0,0.03) 4px);
        pointer-events: none; animation: scan 6s linear infinite;
      }
      @keyframes scan { from { transform: translateY(-20%); } to { transform: translateY(20%); } }
      .lab-alarm {
        position: absolute; top: 14px; right: 14px; width: 18px; height: 18px;
        border-radius: 50%; background: #ff1a1a;
        box-shadow: 0 0 12px #ff0000, 0 0 28px #ff0000;
        animation: alarmPulse 0.85s ease-in-out infinite;
      }
      .lab-alarm::after {
        content: ""; position: absolute; inset: -10px; border-radius: 50%;
        border: 2px solid rgba(255,40,40,0.7);
        animation: sirenRing 1.2s ease-out infinite;
      }
      @keyframes alarmPulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.35); opacity: 0.55; }
      }
      @keyframes sirenRing {
        0% { transform: scale(0.6); opacity: 0.9; }
        100% { transform: scale(1.8); opacity: 0; }
      }
      .lab-beacon {
        position: absolute; top: 0; left: 0; right: 0; height: 4px;
        background: linear-gradient(90deg, transparent, #ff2222, transparent);
        animation: beacon 2.2s linear infinite;
      }
      @keyframes beacon {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
      }
      .lab-title {
        position: relative; z-index: 2; padding: 28px 20px 12px;
        color: #8b0000; letter-spacing: 0.35em; font-size: 0.72rem;
        text-transform: uppercase; font-family: ui-monospace, monospace;
      }
      .lab-sub {
        position: relative; z-index: 2; padding: 0 20px 24px;
        color: #a07070; font-family: ui-monospace, monospace; font-size: 0.85rem;
      }
      .lab-found {
        color: #6a4040; font-size: 0.75rem; margin: 8px 0 4px;
        font-family: ui-monospace, monospace;
      }
    </style>
    <div class="lab-vhs-room"></div>
    <div class="lab-vhs-scanlines"></div>
    <div class="lab-hero lab-fade-in">
      <div class="lab-beacon"></div>
      <div class="lab-alarm"></div>
      <div class="lab-scan"></div>
      <div class="lab-title">M-119 · OBSERVATION LOG · SEALED</div>
      <div class="lab-sub">Lights unstable · inspect everything · leave nothing unread</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


    # Keep Heartaches alive while exploring the room
    st.components.v1.html(
        """
        <script>
        (function(){
          try {
            var r = window.parent || window;
            if (r.__mer_heartaches && r.__mer_heartaches.paused) {
              r.__mer_heartaches.play().catch(function(){});
            }
          } catch(e){}
        })();
        </script>
        """,
        height=0,
    )

    found = st.session_state.lab_found
    if not isinstance(found, set):
        found = set(found or [])
        st.session_state.lab_found = found

    st.markdown(
        f'<div class="lab-found">Fragments recovered: {len(found)} / 6</div>',
        unsafe_allow_html=True,
    )
    st.markdown("**The room** — choose what to examine")

    row1 = st.columns(3)
    row2 = st.columns(3)
    cols = list(row1) + list(row2)
    for col, (key, label, body) in zip(cols, HOTSPOTS):
        with col:
            if st.button(label, use_container_width=True, key=f"lab_hs_{key}"):
                st.session_state.lab_found = set(st.session_state.lab_found) | {key}
                st.session_state["lab_focus"] = key
                st.session_state["lab_focus_body"] = body

    focus = st.session_state.get("lab_focus")
    body = st.session_state.get("lab_focus_body")
    if focus and body:
        st.markdown(body)
        if len(st.session_state.lab_found) >= 6:
            st.info(
                "All fragments recovered. Return to chat and say **stabilize Meridium** "
                "if this was intentional."
            )

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Leave the lab", use_container_width=True, key="lab_leave"):
            st.session_state.view = "chat"
            st.session_state.lab_intro_done = False
            _stop_lab_audio_html()
            st.rerun()
    with c2:
        if st.button("Chat", use_container_width=True, key="lab_chat"):
            st.session_state.view = "chat"
            st.session_state.lab_intro_done = False
            _stop_lab_audio_html()
            st.rerun()
    with c3:
        if st.button("Reset search", use_container_width=True, key="lab_reset"):
            st.session_state.lab_found = set()
            st.session_state.lab_focus = None
            st.session_state.lab_focus_body = None
            st.rerun()

    st.caption("M-119 shell · exit when ready")
    st.stop()
