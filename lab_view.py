"""
Meridium ARG — Interactive lab room (UI)
----------------------------------------
Call from app.py when view == "lab":

    from lab_view import render_lab
    if st.session_state.view == "lab":
        render_lab()   # ends with st.stop()
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
        "the old techs swore was “not copper.”\n\n"
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

def render_lab() -> None:
    """Full-screen black lab with animations, siren, and clickable hotspots."""
    if "lab_found" not in st.session_state:
        st.session_state.lab_found = set()
    if "lab_intro_done" not in st.session_state:
        st.session_state.lab_intro_done = False

    # —— INTRO: full-screen black · siren · blood text · enter button ——
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
            z-index: 999990 !important;
            background: #000;
            animation: labRedFlash 3s ease-in-out forwards;
          }
          @keyframes labRedFlash {
            0%,10%,35%,65% { background: #000; }
            5%,15%,28%,42%,58%,72% { background: #ff0000; }
            20%,50%,80% { background: #1a0000; }
            88% { background: #990000; }
            100% { background: #000; }
          }
          #lab-blood-msg {
            position: fixed !important; inset: 0 !important;
            z-index: 999991 !important;
            display: flex !important; align-items: center !important;
            justify-content: center !important;
            flex-direction: column !important;
            background: transparent !important;
            opacity: 0;
            animation: labBloodIn 1.2s ease forwards;
            animation-delay: 3s;
            pointer-events: none;
          }
          #lab-blood-msg span {
            position: relative;
            color: #6e0000;
            font-size: clamp(1.85rem, 6.5vw, 3.1rem);
            font-family: "Indie Flower", cursive;
            letter-spacing: 0.12em;
            text-align: center;
            max-width: 92%;
            line-height: 1.4;
            transform: rotate(-3deg) skewX(-2deg);
            text-shadow:
              0 1px 0 #4a0000, 0 2px 0 #3a0000, 1px 3px 0 #5a0000,
              -1px 4px 0 #2a0000, 2px 5px 0 #1a0000, 0 6px 2px #300000,
              0 0 12px #8b0000, 0 0 28px rgba(100,0,0,0.9);
            -webkit-text-stroke: 0.5px #2a0000;
          }
          #lab-blood-msg span::after {
            content: "";
            position: absolute; left: 12%; right: 18%; top: 95%; height: 40px;
            background:
              radial-gradient(ellipse 3px 26px at 25% 0%, #7a0000 0%, transparent 75%),
              radial-gradient(ellipse 4px 18px at 55% 0%, #5a0000 0%, transparent 70%),
              radial-gradient(ellipse 3px 30px at 75% 0%, #8b0000 0%, transparent 75%);
            animation: labDrip 2s ease-out forwards;
            animation-delay: 3.2s;
          }
          @keyframes labBloodIn { from { opacity: 0; } to { opacity: 1; } }
          #lab-press-hint {
            margin-top: 2.75rem;
            color: #4a2020;
            font-family: ui-monospace, monospace;
            font-size: 0.7rem;
            letter-spacing: 0.3em;
            text-transform: uppercase;
            opacity: 0;
            animation: labBloodIn 1s ease forwards;
            animation-delay: 4s;
            pointer-events: none;
          }
          div[data-testid="stForm"] {
            position: fixed !important;
            bottom: 4px !important;
            left: 4px !important;
            opacity: 0.04 !important;
            z-index: 999999 !important;
            width: 80px !important;
          }
          @keyframes labDrip {
            0% { opacity: 0; transform: scaleY(0.2); transform-origin: top; }
            100% { opacity: 0.95; transform: scaleY(1); transform-origin: top; }
          }

          /* Small ominous button under the text */
          .stApp [data-testid="stButton"] {
            position: fixed !important;
            left: 50% !important;
            top: 62% !important;
            transform: translateX(-50%) !important;
            z-index: 999999 !important;
            width: auto !important;
            min-width: 160px !important;
            max-width: 220px !important;
            opacity: 0;
            animation: labBloodIn 0.9s ease forwards;
            animation-delay: 3.8s;
          }
          .stApp [data-testid="stButton"] > button {
            background: #120303 !important;
            color: #a01818 !important;
            border: 1px solid #4a0a0a !important;
            border-radius: 3px !important;
            font-family: "Indie Flower", cursive !important;
            font-size: 1.05rem !important;
            letter-spacing: 0.14em !important;
            padding: 0.45rem 1.1rem !important;
            min-height: 0 !important;
            height: auto !important;
            box-shadow: 0 0 16px rgba(80,0,0,0.5) !important;
          }
          .stApp [data-testid="stButton"] > button:hover {
            color: #ff2a2a !important;
            border-color: #8b0000 !important;
            background: #1a0505 !important;
          }
        </style>
        <div id="lab-full-black"></div>
        <div id="lab-blood-msg"><span class="blood">you're not supposed to know</span>
          <div id="lab-press-hint">press enter</div></div>
        <script>
        (function(){
          if (window.__mer_lab_enter) return;
          window.__mer_lab_enter = true;
          document.addEventListener('keydown', function(e){
            if (e.key !== 'Enter') return;
            var forms = document.querySelectorAll('div[data-testid="stForm"] button');
            if (forms.length) { forms[0].click(); e.preventDefault(); }
          });
        })();
        </script>
            """,
            unsafe_allow_html=True,
        )

        # Audio iframe MUST have height > 0 or browsers kill the JS
        # Auto siren → Heartaches; Enter / tap enter to go in (no arm button)
        st.components.v1.html(
            """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  html, body { margin:0; background:transparent; }
  .wrap {
    display:flex; flex-direction:column; align-items:center;
    padding: 10px 8px; gap: 10px;
  }
  #enterBtn {
    width: min(240px, 85vw);
    padding: 12px 16px;
    border-radius: 4px;
    border: 1px solid #4a0c0c;
    background: #100303;
    color: #a02020;
    font-family: Georgia, "Indie Flower", cursive;
    font-size: 1rem;
    letter-spacing: 0.14em;
    cursor: pointer;
    opacity: 0;
    animation: fadeIn 0.8s ease forwards;
    animation-delay: 4.2s;
  }
  @keyframes fadeIn { to { opacity: 1; } }
  #enterBtn:active { color: #ff3030; background: #1a0505; }
</style>
</head>
<body>
  <div class="wrap">
    <button id="enterBtn" type="button">enter the lab…</button>
  </div>
<script>
(function(){
  var started = false;
  var ctx = null;

  function scarySiren(sec){
    // Same path as Heartaches (HTML5 Audio) — Web Audio was silent on some devices
    try{
      var urls = [
        'https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3',
        'https://assets.mixkit.co/active_storage/sfx/1626/1626-preview.mp3',
        'https://upload.wikimedia.org/wikipedia/commons/4/4a/Emergency_alarm_tone.ogg'
      ];
      var a = new Audio(urls[0]);
      a.loop = true;
      a.volume = 0.75;
      window.__mer_siren = a;
      var p = a.play();
      if (p && p.catch) {
        p.catch(function(){
          // fallback second URL
          a.src = urls[1];
          a.play().catch(function(){});
        });
      }
      setTimeout(function(){
        try {
          a.pause();
          a.currentTime = 0;
        } catch(e){}
      }, (sec || 3.4) * 1000);
      return true;
    }catch(e){ return false; }
  }

  function playHeartaches(){
    try{
      var a = new Audio('https://archive.org/download/al-bowlly-sid-phillips-his-melodians-heartaches/Al%20Bowlly%2C%20Sid%20Phillips%20%26%20His%20Melodians%20-%20Heartaches.mp3');
      a.loop = true; a.volume = 0.5;
      a.play().catch(function(){});
      window.__mer_heartaches = a;
    }catch(e){}
  }

  function startSequence(){
    if (started) return;
    started = true;
    scarySiren(3.5);
    // Heartaches only after siren window ends
    setTimeout(function(){
      try {
        if (window.__mer_siren) {
          window.__mer_siren.pause();
          window.__mer_siren.currentTime = 0;
        }
      } catch(e){}
      playHeartaches();
    }, 3600);
  }

  // Try automatic start (works on many desktops)
  startSequence();

  // If browser blocked autoplay, first touch/click anywhere restarts once (no labeled arm button)
  function unlock(){
    started = false;
    startSequence();
    try {
      document.removeEventListener('touchstart', unlock);
      document.removeEventListener('click', unlock);
      window.parent.document.removeEventListener('touchstart', unlock);
      window.parent.document.removeEventListener('click', unlock);
    } catch(e){}
  }
  document.addEventListener('touchstart', unlock, {once:true, passive:true});
  document.addEventListener('click', unlock, {once:true});
  try {
    window.parent.document.addEventListener('touchstart', unlock, {once:true, passive:true});
    window.parent.document.addEventListener('click', unlock, {once:true});
  } catch(e){}

  function clickStreamlitEnter(){
    try {
      var btn = window.parent.document.querySelector('div[data-testid="stForm"] button');
      if (btn) btn.click();
    } catch(e) {}
  }

  document.getElementById('enterBtn').addEventListener('click', function(){
    if (!started) startSequence();
    clickStreamlitEnter();
  });

  function onKey(e){
    if (e.key !== 'Enter') return;
    if (!started) startSequence();
    clickStreamlitEnter();
  }
  document.addEventListener('keydown', onKey);
  try { window.parent.document.addEventListener('keydown', onKey); } catch(e){}
})();
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





    # Light-coming-on flicker when just entered
    if st.session_state.get("lab_flicker"):
        st.markdown("""
        <style>
          .stApp, [data-testid="stAppViewContainer"], section.main, .block-container {
            background: #000 !important;
          }
          #lab-light-on {
            position: fixed; inset: 0; z-index: 999999;
            pointer-events: none;
            animation: lightOn 1.8s ease-out forwards;
          }
          @keyframes lightOn {
            0%   { background: #000; }
            8%   { background: #2a2a20; }
            14%  { background: #000; }
            22%  { background: #3a3a28; }
            28%  { background: #0a0a08; }
            38%  { background: #4a4a30; }
            45%  { background: #111; }
            55%  { background: #5a5a38; }
            62%  { background: #1a1a12; }
            75%  { background: rgba(40,40,28,0.9); }
            100% { background: transparent; }
          }
          .lab-fade-in {
            animation: labFadeIn 1.2s ease forwards;
            animation-delay: 1.4s;
            opacity: 0;
          }
          @keyframes labFadeIn {
            from { opacity: 0; filter: brightness(0.2); }
            to { opacity: 1; filter: brightness(1); }
          }
        </style>
        <div id="lab-light-on"></div>
        """, unsafe_allow_html=True)
        st.session_state.lab_flicker = False

    st.markdown(
        """
    <style>
      .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: #000 !important;
      }
      .lab-hero {
        position: relative; min-height: 220px; border-radius: 16px;
        background:
          radial-gradient(ellipse at 50% 20%, rgba(120,0,0,0.45), transparent 55%),
          radial-gradient(ellipse at 70% 80%, rgba(40,0,0,0.5), transparent 50%),
          #050505;
        border: 1px solid #3a1515; overflow: hidden; margin-bottom: 12px;
      }
      .lab-scan {
        position: absolute; inset: 0;
        background: repeating-linear-gradient(
          0deg, transparent, transparent 3px, rgba(255,0,0,0.03) 4px);
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
        animation: flick 4.5s infinite;
      }
      @keyframes flick {
        0%, 91%, 100% { opacity: 1; }
        93% { opacity: 0.25; }
        95% { opacity: 1; }
        97% { opacity: 0.4; }
      }
      .lab-sub {
        position: relative; z-index: 2; padding: 0 20px 24px;
        color: #a07070; font-family: ui-monospace, monospace; font-size: 0.85rem;
      }
      .lab-panel {
        background: #0a0505; border: 1px solid #3a1515; border-radius: 12px;
        padding: 14px 16px; color: #c4a0a0; font-family: ui-monospace, monospace;
        font-size: 0.88rem; line-height: 1.55; margin-top: 8px;
      }
      .lab-panel strong { color: #ffb0b0; }
      .lab-found {
        color: #6a4040; font-size: 0.75rem; margin: 8px 0 4px;
        font-family: ui-monospace, monospace;
      }
    </style>
    <div class="lab-hero lab-fade-in">
      <div class="lab-beacon"></div>
      <div class="lab-alarm" title="alarm"></div>
      <div class="lab-scan"></div>
      <div class="lab-title">M-119 · OBSERVATION LOG · SEALED</div>
      <div class="lab-sub">Lights unstable · inspect everything · leave nothing unread</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    with st.expander("Alarm speaker — silent until armed", expanded=False):
        st.components.v1.html(
            """
        <div style="font-family:monospace;color:#c4a0a0;">
          <button id="sirenBtn" style="width:100%;padding:12px;border:none;border-radius:10px;
            background:#5a1010;color:#ffb0b0;font-weight:700;cursor:pointer;">
            ▶ Start siren
          </button>
          <p id="sirenSt" style="font-size:12px;color:#6a4040;margin-top:8px;">Off — visual alarm still runs above.</p>
        </div>
        <script>
        (function(){
          let ctx, o1, o2, lfo, master, on=false, timer=null;
          const btn=document.getElementById('sirenBtn');
          const st=document.getElementById('sirenSt');
          function stop(){
            if(timer){ clearInterval(timer); timer=null; }
            try{ o1&&o1.stop(); }catch(e){}
            try{ o2&&o2.stop(); }catch(e){}
            try{ lfo&&lfo.stop(); }catch(e){}
            try{ ctx&&ctx.close(); }catch(e){}
            ctx=o1=o2=lfo=master=null; on=false;
            btn.textContent='▶ Start siren';
            st.textContent='Off — visual alarm still runs above.';
          }
          function arm(){
            ctx = new (window.AudioContext||window.webkitAudioContext)();
            master = ctx.createGain();
            master.gain.value = 0.1;
            master.connect(ctx.destination);
            o1 = ctx.createOscillator();
            o2 = ctx.createOscillator();
            const g1 = ctx.createGain();
            const g2 = ctx.createGain();
            o1.type = 'sawtooth';
            o2.type = 'square';
            g1.gain.value = 0.55;
            g2.gain.value = 0.4;
            o1.connect(g1); g1.connect(master);
            o2.connect(g2); g2.connect(master);
            lfo = ctx.createOscillator();
            const lfoG = ctx.createGain();
            lfo.frequency.value = 7;
            lfoG.gain.value = 0.03;
            lfo.connect(lfoG);
            lfoG.connect(master.gain);
            const now = ctx.currentTime;
            // continuous wail loop via scheduled ramps
            function scheduleWail(t) {
              o1.frequency.setValueAtTime(580, t);
              o1.frequency.linearRampToValueAtTime(1100, t+0.45);
              o1.frequency.linearRampToValueAtTime(580, t+0.9);
              o2.frequency.setValueAtTime(740, t);
              o2.frequency.linearRampToValueAtTime(1280, t+0.45);
              o2.frequency.linearRampToValueAtTime(740, t+0.9);
            }
            for (let i = 0; i < 40; i++) scheduleWail(now + i * 0.95);
            o1.start(now); o2.start(now); lfo.start(now);
            on = true;
            btn.textContent = '⏹ Stop siren';
            st.textContent = 'SIREN LIVE — lower your volume if needed.';
          }
          btn.onclick = function(){ if(on) stop(); else arm(); };
        })();
        </script>
        """,
            height=100,
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
        # markdown panel (body may contain markdown)
        st.markdown(body)
        if len(st.session_state.lab_found) >= 6:
            st.info(
                "All fragments recovered. Return to chat and say **stabilize Meridium** "
                "if this was intentional."
            )

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("↩ Leave the lab", use_container_width=True, key="lab_leave"):
            st.session_state.view = "chat"
            st.session_state.lab_intro_done = False
            st.rerun()
    with c2:
        if st.button("💬 Chat", use_container_width=True, key="lab_chat"):
            st.session_state.view = "chat"
            st.session_state.lab_intro_done = False
            st.rerun()
    with c3:
        if st.button("↻ Reset search", use_container_width=True, key="lab_reset"):
            st.session_state.lab_found = set()
            st.session_state.lab_focus = None
            st.session_state.lab_focus_body = None
            st.rerun()

    st.caption("M-119 shell · exit when ready")
    st.stop()
