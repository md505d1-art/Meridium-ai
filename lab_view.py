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
        "Along the gasket: a film that is not condensation. It strings when touched with a probe, "
        "then snaps back as if embarrassed to be seen. Under UV it fluoresces a wrong violet — "
        "the same band Voss marked as M-119 residual.\n\n"
        "Nobody has wiped it. Nobody wants to know if it starts again when watched.\n\n"
        "Grease pencil on the frame, hurried:\n"
        "> DO NOT CLEAN · TRACE IS THE SAMPLE",
    ),
    (
        "floor",
        "Bloodstained note (floor)",
        "**Floor note — recovered under the bench**\n\n"
        "Paper stuck to the tile with something darker than coffee. "
        "The writing starts neat and ends dragged, as if the hand was leaving before the sentence did.\n\n"
        "> If the spectrum holds, log it as M-119.\n"
        "> If the spectrum collapses, log that too — *especially* that.\n"
        "> Do not tell the committees until we know whether noticing is the cause or the cure.\n\n"
        "A second hand — shakier — added underneath:\n"
        "> it looked back\n\n"
        "There is a partial print in the stain. Ridge detail is good enough that someone, once, "
        "could have matched it. No one will.",
    ),
    (
        "bench",
        "Overturned bench",
        "**Work surface — abandoned mid-task**\n\n"
        "Tools scattered with intent, not chaos: a spectrometer cable still clipped, "
        "a notebook open to a page that was torn out. The missing page is the floor note.\n\n"
        "Chalk on the bench lip, almost rubbed away:\n"
        "> MERIDIUM holds when watched · decays when mocked\n\n"
        "Chair kicked back. Dark droplets lead from the bench toward the door, then stop "
        "as if whatever left them was lifted off the floor.\n\n"
        "Under the bench, a second mark in smaller script:\n"
        "> Voss said curiosity is the stabiliser. I hope she was right.",
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
        "A fine spatter rings the fixture. Tiny, dry, the colour of old scabs.\n"
        "The beacon has been running longer than any shift roster admits.",
    ),
    (
        "window",
        "Blacked-out window",
        "**Observation window — painted shut**\n\n"
        "Exterior paint, slapped on fast. From this side, fingernail and something harder "
        "clawed through to the glass. The scratches form a crooked **119**.\n\n"
        "At the bottom of the frame, a smear where a hand slid and slipped — "
        "skin-oil mixed with a darker streak. Someone braced here. Someone bled a little. Someone left.\n\n"
        "If you cup your eyes against the unpainted flecks, the corridor beyond "
        "does not resolve into a normal hallway. Depth goes wrong.\n\n"
        "The log only says: *do not photograph.*\n"
        "A later addendum, different ink: *do not name what you think you see.*",
    ),
    (
        "terminal",
        "Dead terminal",
        "**Terminal — last surviving lines**\n\n"
        "```\n"
        "STATUS........ METASTABLE\n"
        "REF........... M-119\n"
        "PUBLIC........ DENIED\n"
        "CASUALTY...... [REDACTED] / [REDACTED]\n"
        "NOTE.......... designation persists in shell\n"
        "NOTE.......... organic trace on sill / glass / floor\n"
        "NOTE.......... do not re-enter without observer protocol\n"
        "NOTE.......... Voss: curiosity = stabiliser\n"
        "NOTE.......... NOT for refinement / weaponisation / brand\n"
        "NOTE.......... medium ≠ commodity (ignore committees)\n"
        "CMD........... stabilize Meridium\n"
        "```\n\n"
        "The cursor still blinks in the black. "
        "A dried fingerprint sits on the spacebar — dark at the ridges, "
        "as if the operator did not wash before the final command.\n\n"
        "Scrollback (partial recovery):\n"
        "> observer present · line holding\n"
        "> observer laughing · line spiking\n"
        "> observer gone · line collapse\n"
        "> observer returned · line… soft?\n\n"
        "The rest of the disk reads as static. "
        "Whatever finished the shift did not log out cleanly.",
    ),
]




def _stop_lab_audio_html() -> None:
    """Hard-stop siren + Heartaches on the parent page."""
    st.session_state["lab_kill_audio"] = True
    st.components.v1.html(
        """
        <script>
        (function(){
          try {
            var r = window.parent || window;
            r.__mer_audio_on = false;
            if (r.__mer_song_timer) { clearTimeout(r.__mer_song_timer); r.__mer_song_timer = null; }
            function kill(a){
              if (!a) return;
              try { a.pause(); } catch(e){}
              try { a.currentTime = 0; } catch(e){}
              try { a.src = ''; a.load && a.load(); } catch(e){}
              try { a.remove(); } catch(e){}
            }
            kill(r.__mer_heartaches); r.__mer_heartaches = null;
            kill(r.__mer_siren); r.__mer_siren = null;
            var nodes = r.document.querySelectorAll('audio');
            for (var i = 0; i < nodes.length; i++) {
              try {
                var s = (nodes[i].currentSrc || nodes[i].src || '');
                if (nodes[i].getAttribute('data-meridium') === '1' ||
                    /Heartaches|bowlly|2869|mixkit|meridium/i.test(s)) {
                  kill(nodes[i]);
                }
              } catch(e){}
            }
          } catch (e) {}
        })();
        </script>
        """,
        height=1,
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
          #lab-vhs, #lab-vhs-scan, #lab-vhs-track, #lab-vhs-rgb, #lab-full-black {
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
            height=1,
        )

        # Visible enter control — works on mobile (iframe buttons are unreliable)
        st.markdown(
            """
        <style>
          /* Hide the old "press the screen..." line — button sits there */
          #lab-press-hint, #lab-press-sub { display: none !important; height: 0 !important; }

          /* Button sits under blood text / where the hint was */
          div[data-testid="stButton"] {
            position: fixed !important;
            left: 50% !important;
            top: 58% !important;
            transform: translateX(-50%) !important;
            width: min(280px, 82vw) !important;
            z-index: 1000005 !important;
            opacity: 0;
            animation: enterBtnIn 1.4s ease forwards;
            animation-delay: 3.2s;
          }
          div[data-testid="stButton"] > button {
            background: #100303 !important;
            color: #c03030 !important;
            border: 1px solid #5a1010 !important;
            border-radius: 6px !important;
            font-family: "Indie Flower", Georgia, cursive !important;
            font-size: 1.15rem !important;
            letter-spacing: 0.08em !important;
            padding: 0.85rem 1rem !important;
            width: 100% !important;
            box-shadow: 0 0 20px rgba(80,0,0,0.45) !important;
          }
          @keyframes enterBtnIn {
            from { opacity: 0; transform: translateX(-50%) translateY(14px); }
            to   { opacity: 1; transform: translateX(-50%) translateY(0); }
          }
          /* tiny hint under the button */
          .lab-enter-caption {
            position: fixed !important;
            left: 0; right: 0;
            top: calc(62% + 58px) !important;
            z-index: 1000005 !important;
            opacity: 0;
            animation: enterBtnIn 1.2s ease forwards;
            animation-delay: 3.8s;
            color: #3a1818 !important;
            font-size: 0.65rem !important;
            letter-spacing: 0.16em;
            text-align: center;
            pointer-events: none;
          }
        </style>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Enter into the lab", use_container_width=True, key="lab_enter_mobile"):
            st.session_state.lab_intro_done = True
            st.session_state.lab_flicker = True
            st.rerun()

        # Hidden form still catches Enter key on laptop via JS
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
        found_n = len(st.session_state.lab_found) if isinstance(st.session_state.lab_found, set) else len(set(st.session_state.lab_found or []))
        if focus == "floor" and found_n >= 3:
            st.markdown(
                "<p style='color:#8a7070;font-family:Georgia,serif;font-size:0.9rem;"
                "margin-top:0.75rem;font-style:italic;'>"
                "…under the stain, in smaller script:<br/>"
                "<span style='color:#c4b5fd;'>she answers to stringbean · say it kindly</span>"
                "</p>",
                unsafe_allow_html=True,
            )
        if focus == "window" and found_n >= 4:
            st.markdown(
                "<p style='color:#8a7070;font-family:Georgia,serif;font-size:0.9rem;"
                "margin-top:0.75rem;font-style:italic;'>"
                "…in the paint, two names scratched over each other — human / witch:<br/>"
                "<span style='color:#f9a8d4;'>say them together kindly · luz and amity</span>"
                "</p>",
                unsafe_allow_html=True,
            )
        if found_n >= 6:
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

    if int(st.session_state.get("lab_visits") or 0) >= 2:
        # Anomaly glitch residual in lab — clickable image
        st.markdown("---")
        st.caption("Voss: do not ignore the interference in the pane.")
        from pathlib import Path as _P
        _gpath = None
        _base = _P(__file__).resolve().parent / "assets"
        for _name in ("glitch_lab.png", "IMG_1355.jpeg", "IMG_1355.jpg"):
            _cand = _base / _name
            if _cand.exists() and _cand.stat().st_size > 500:
                _gpath = _cand
                break
        if _gpath is not None:
            st.image(str(_gpath), width=280)
        else:
            st.markdown(
                '<div style="height:72px;border-radius:10px;background:repeating-linear-gradient(90deg,#1a0505,#1a0505 3px,#2a0a0a 3px,#2a0a0a 6px);border:1px solid rgba(239,68,68,0.4);"></div>',
                unsafe_allow_html=True,
            )
        if st.button("Tap anomaly · lab", key="glitch_lab", use_container_width=True):
            found = list(st.session_state.get("glitches_found") or [])
            if "lab" not in found:
                found.append("lab")
                st.session_state.glitches_found = found
                st.session_state["_glitch_flash"] = "Voss log: lab marker secured. The pane noticed you back."
                if set(found) >= {"home", "lab", "pixel"}:
                    st.session_state.voss_file_unlocked = True
                    st.session_state["_glitch_flash"] = "All three markers secured. Dr. Voss left you a file."
                    st.session_state.voss_cutscene_stage = 0
                    st.session_state.view = "voss_file"
                try:
                    # persist via app if available
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
                                data["arg_unlocked"] = True
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

    st.stop()
