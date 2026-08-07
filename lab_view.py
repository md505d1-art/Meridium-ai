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

    # —— INTRO: 3s siren + red flash → blood text ——
    if not st.session_state.lab_intro_done:
        st.components.v1.html(
            """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  html, body {
    margin: 0; padding: 0; width: 100%; height: 100%;
    background: #000; overflow: hidden;
    font-family: Georgia, "Times New Roman", serif;
  }
  #flash {
    position: fixed; inset: 0;
    background: #000;
    animation: redFlash 3s ease-in-out forwards;
  }
  @keyframes redFlash {
    0%   { background: #000; }
    5%   { background: #ff0000; }
    10%  { background: #000; }
    15%  { background: #ff1a1a; }
    20%  { background: #1a0000; }
    28%  { background: #ff0000; }
    35%  { background: #000; }
    42%  { background: #cc0000; }
    50%  { background: #330000; }
    58%  { background: #ff0000; }
    65%  { background: #000; }
    72%  { background: #ff2222; }
    80%  { background: #1a0000; }
    88%  { background: #990000; }
    95%  { background: #200000; }
    100% { background: #000; }
  }
  #blood {
    position: fixed; inset: 0;
    display: flex; align-items: center; justify-content: center;
    opacity: 0;
    animation: bloodIn 1.4s ease forwards;
    animation-delay: 3s;
    pointer-events: none;
  }
  #blood span {
    position: relative;
    color: #6e0000;
    font-size: clamp(1.5rem, 5.5vw, 2.6rem);
    font-weight: 800;
    font-family: Georgia, "Palatino Linotype", "Times New Roman", serif;
    font-style: italic;
    letter-spacing: 0.12em;
    text-align: center;
    max-width: 92%;
    line-height: 1.4;
    transform: rotate(-3deg) skewX(-2deg);
    /* thick wet blood layers */
    text-shadow:
      0 1px 0 #4a0000,
      0 2px 0 #3a0000,
      1px 3px 0 #5a0000,
      -1px 4px 0 #2a0000,
      2px 5px 0 #1a0000,
      0 6px 2px #300000,
      3px 8px 0 #1a0505,
      -2px 7px 0 #400000,
      0 0 8px #8b0000,
      0 0 20px rgba(100,0,0,0.85),
      0 12px 18px rgba(40,0,0,0.6);
    -webkit-text-stroke: 0.5px #2a0000;
    filter: contrast(1.35) saturate(1.4);
    animation: bloodSettle 2s ease forwards;
    animation-delay: 3s;
  }
  /* dripping streaks under the words */
  #blood span::after {
    content: "";
    position: absolute;
    left: 12%;
    right: 18%;
    top: 95%;
    height: 42px;
    background:
      radial-gradient(ellipse 4px 18px at 10% 0%, #5a0000 0%, #5a0000 40%, transparent 70%),
      radial-gradient(ellipse 3px 28px at 28% 0%, #7a0000 0%, #4a0000 45%, transparent 75%),
      radial-gradient(ellipse 5px 14px at 47% 0%, #6a0000 0%, transparent 70%),
      radial-gradient(ellipse 3px 32px at 63% 0%, #8b0000 0%, #3a0000 50%, transparent 78%),
      radial-gradient(ellipse 4px 20px at 82% 0%, #5a0000 0%, transparent 72%),
      radial-gradient(ellipse 2px 12px at 92% 0%, #4a0000 0%, transparent 70%);
    opacity: 0.95;
    animation: drip 2.5s ease-out forwards;
    animation-delay: 3.3s;
    pointer-events: none;
  }
  #blood span::before {
    content: "";
    position: absolute;
    inset: -8px -12px;
    background:
      radial-gradient(ellipse at 20% 30%, rgba(90,0,0,0.35), transparent 50%),
      radial-gradient(ellipse at 70% 60%, rgba(60,0,0,0.25), transparent 45%);
    z-index: -1;
    filter: blur(1px);
  }
  @keyframes bloodSettle {
    0%   { opacity: 0; filter: contrast(1.35) saturate(1.4) blur(3px); }
    40%  { opacity: 1; filter: contrast(1.35) saturate(1.4) blur(0.5px); }
    100% { opacity: 1; filter: contrast(1.35) saturate(1.4) blur(0); }
  }
  @keyframes drip {
    0%   { opacity: 0; transform: scaleY(0.2); transform-origin: top; }
    100% { opacity: 0.95; transform: scaleY(1); transform-origin: top; }
  }
  #hint {
    position: fixed; bottom: 28px; left: 0; right: 0;
    text-align: center;
    color: #5a3030;
    font-size: 0.75rem;
    font-family: ui-monospace, monospace;
    opacity: 0;
    animation: bloodIn 0.8s ease forwards;
    animation-delay: 4.2s;
  }
  @keyframes bloodIn {
    from { opacity: 0; transform: scale(1.05); }
    to   { opacity: 1; transform: scale(1); }
  }
</style>
</head>
<body>
  <div id="flash"></div>
  <div id="blood"><span>you're not supposed to know</span></div>
  <div id="hint">alarm fading · the room remains</div>
  <script>
  
    function startScarySiren(durationSec) {
      try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const master = ctx.createGain();
        master.gain.value = 0.09;
        master.connect(ctx.destination);

        // Two dissonant oscillators for that "wrong" emergency sound
        const o1 = ctx.createOscillator();
        const o2 = ctx.createOscillator();
        const g1 = ctx.createGain();
        const g2 = ctx.createGain();
        o1.type = "sawtooth";
        o2.type = "square";
        g1.gain.value = 0.55;
        g2.gain.value = 0.35;
        o1.connect(g1); g1.connect(master);
        o2.connect(g2); g2.connect(master);

        // Classic siren wail: sweep up and down
        const now = ctx.currentTime;
        const dur = durationSec || 3;
        function wail(osc, base, amp, t0) {
          let t = t0;
          const cycles = Math.max(2, Math.floor(dur / 0.85));
          for (let i = 0; i < cycles; i++) {
            osc.frequency.setValueAtTime(base, t);
            osc.frequency.linearRampToValueAtTime(base + amp, t + 0.4);
            osc.frequency.linearRampToValueAtTime(base, t + 0.8);
            t += 0.85;
          }
        }
        wail(o1, 620, 480, now);
        wail(o2, 780, 520, now);

        // Slight tremolo on master for panic feel
        const lfo = ctx.createOscillator();
        const lfoG = ctx.createGain();
        lfo.frequency.value = 6;
        lfoG.gain.value = 0.025;
        lfo.connect(lfoG);
        lfoG.connect(master.gain);
        lfo.start(now);

        o1.start(now); o2.start(now);
        master.gain.setValueAtTime(0.09, now);
        master.gain.linearRampToValueAtTime(0.0001, now + dur);

        setTimeout(function() {
          try { o1.stop(); o2.stop(); lfo.stop(); ctx.close(); } catch (e) {}
        }, dur * 1000 + 150);
        return true;
      } catch (e) { return false; }
    }

  (function(){
    startScarySiren(3.2);
  })();
  </script>
</body>
</html>
            """,
            height=420,
        )
        st.markdown("")
        if st.button("Enter the room", type="primary", use_container_width=True, key="lab_intro_enter"):
            st.session_state.lab_intro_done = True
            st.rerun()
        st.caption("If the siren is silent, your browser blocked autoplay — the flash still counts.")
        st.stop()

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
    <div class="lab-hero">
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
