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
          let ctx, osc, gain, lfo, on=false;
          const btn=document.getElementById('sirenBtn');
          const st=document.getElementById('sirenSt');
          function stop(){
            try{ osc&&osc.stop(); }catch(e){}
            try{ lfo&&lfo.stop(); }catch(e){}
            try{ ctx&&ctx.close(); }catch(e){}
            ctx=osc=gain=lfo=null; on=false;
            btn.textContent='▶ Start siren';
            st.textContent='Off — visual alarm still runs above.';
          }
          function start(){
            ctx = new (window.AudioContext||window.webkitAudioContext)();
            osc = ctx.createOscillator();
            gain = ctx.createGain();
            lfo = ctx.createOscillator();
            const lfoGain = ctx.createGain();
            osc.type='sawtooth';
            osc.frequency.value=680;
            lfo.frequency.value=2.5;
            lfoGain.gain.value=180;
            gain.gain.value=0.04;
            lfo.connect(lfoGain);
            lfoGain.connect(osc.frequency);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(); lfo.start();
            on=true;
            btn.textContent='⏹ Stop siren';
            st.textContent='Siren armed — keep volume modest.';
          }
          btn.onclick=function(){ if(on) stop(); else start(); };
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
            st.rerun()
    with c2:
        if st.button("💬 Chat", use_container_width=True, key="lab_chat"):
            st.session_state.view = "chat"
            st.rerun()
    with c3:
        if st.button("↻ Reset search", use_container_width=True, key="lab_reset"):
            st.session_state.lab_found = set()
            st.session_state.lab_focus = None
            st.session_state.lab_focus_body = None
            st.rerun()

    st.caption("M-119 shell · exit when ready")
    st.stop()
