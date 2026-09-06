"""
Meridium ARG — Interactive lab room (cinematic rebuild)
-------------------------------------------------------
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
        "Containment glass",
        "◈",
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
        "Floor note",
        "📄",
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
        "⚗️",
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
        "Alarm beacon",
        "🔴",
        "**Emergency beacon — local only**\n\n"
        "The red pulse is not on the building grid. It belongs to the shell.\n\n"
        "Interval is wrong: three quick flares, a hitch, then a long burn — "
        "like someone trying to teach a code and forgetting the pattern.\n\n"
        "Under the housing, old tape. Handwriting in grease pencil:\n\n"
        "> When the light goes solid, stop looking at the glass.\n"
        "> When the light goes dark, do not assume it left.\n\n"
        "A fine spatter rings the fixture. Tiny, dry, the colour of old scabs.\n"
        "The beacon has been running longer than any shift roster admits.",
    ),
    (
        "window",
        "Blacked-out window",
        "⬛",
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
        "💻",
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


def _ensure_state():
    if "lab_intro_done" not in st.session_state:
        st.session_state.lab_intro_done = False
    if "lab_found" not in st.session_state:
        st.session_state.lab_found = set()
    if not isinstance(st.session_state.lab_found, set):
        st.session_state.lab_found = set(st.session_state.lab_found or [])
    if "lab_focus" not in st.session_state:
        st.session_state.lab_focus = None
    if "lab_focus_body" not in st.session_state:
        st.session_state.lab_focus_body = None


def render_lab():
    """Cinematic lab: door sequence → interactive room → dossier panels."""
    _ensure_state()

    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Orbitron:wght@500;700&family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=swap');

.lab-root {
  --lab-violet: #c4a7e7;
  --lab-cyan: #67e8f9;
  --lab-red: #f87171;
  --lab-muted: #9b92b0;
}
.lab-door-stage {
  position: relative; min-height: 72vh; border-radius: 18px; overflow: hidden;
  background:
    radial-gradient(ellipse 80% 60% at 50% 40%, rgba(88,28,135,0.25), transparent 70%),
    radial-gradient(ellipse 50% 40% at 50% 100%, rgba(127,29,29,0.2), transparent 60%),
    linear-gradient(180deg, #0a0812 0%, #05040a 100%);
  border: 1px solid rgba(196,167,231,0.22);
  box-shadow: 0 0 0 1px rgba(0,0,0,0.6), 0 24px 80px rgba(0,0,0,0.55), inset 0 0 80px rgba(0,0,0,0.4);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 2rem 1.25rem 2.5rem;
  animation: labFadeIn 0.9s ease both;
}
@keyframes labFadeIn {
  from { opacity: 0; transform: translateY(10px) scale(0.985); }
  to { opacity: 1; transform: none; }
}
.lab-door-frame {
  width: min(280px, 70vw); height: min(380px, 52vh);
  position: relative; margin-bottom: 1.75rem; perspective: 900px;
}
.lab-door {
  width: 100%; height: 100%;
  background: linear-gradient(180deg, rgba(30,20,40,0.95) 0%, rgba(12,10,18,0.98) 100%);
  border: 2px solid rgba(196,167,231,0.35);
  border-radius: 8px 8px 4px 4px;
  box-shadow: inset 0 0 40px rgba(100,60,160,0.15), 0 0 30px rgba(124,58,237,0.2), 0 20px 40px rgba(0,0,0,0.5);
  position: relative; transform-origin: left center;
  animation: doorBreathe 4s ease-in-out infinite;
}
@keyframes doorBreathe {
  0%, 100% { box-shadow: inset 0 0 40px rgba(100,60,160,0.15), 0 0 30px rgba(124,58,237,0.2), 0 20px 40px rgba(0,0,0,0.5); }
  50% { box-shadow: inset 0 0 50px rgba(100,60,160,0.25), 0 0 45px rgba(124,58,237,0.35), 0 20px 40px rgba(0,0,0,0.5); }
}
.lab-door::before {
  content: ""; position: absolute; inset: 12%;
  border: 1px solid rgba(196,167,231,0.15); border-radius: 4px;
  background: radial-gradient(circle at 50% 30%, rgba(196,167,231,0.08), transparent 55%);
}
.lab-door-handle {
  position: absolute; right: 18%; top: 48%;
  width: 14px; height: 14px; border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #e9d5ff, #7c3aed);
  box-shadow: 0 0 12px rgba(167,139,250,0.8);
}
.lab-door-seal {
  position: absolute; left: 50%; top: 22%; transform: translateX(-50%);
  font-family: 'Orbitron', sans-serif; font-size: 0.65rem; letter-spacing: 0.28em;
  color: rgba(248,113,113,0.85); text-shadow: 0 0 10px rgba(248,113,113,0.5);
}
.lab-door-warning {
  position: absolute; left: 50%; bottom: 18%; transform: translateX(-50%);
  font-family: 'IBM Plex Mono', monospace; font-size: 0.58rem; letter-spacing: 0.12em;
  color: rgba(251,191,36,0.7); text-align: center; white-space: nowrap;
}
.lab-door-title {
  font-family: 'Orbitron', sans-serif; font-size: clamp(1.1rem, 3.5vw, 1.55rem);
  letter-spacing: 0.22em; color: #e9e2f8; text-align: center; margin: 0 0 0.4rem;
  text-shadow: 0 0 24px rgba(167,139,250,0.35);
}
.lab-door-sub {
  font-family: 'Cormorant Garamond', Georgia, serif; font-size: clamp(0.95rem, 2.5vw, 1.15rem);
  font-style: italic; color: var(--lab-muted); text-align: center; max-width: 28rem;
  line-height: 1.45; margin-bottom: 1.5rem;
}
.lab-door-hint {
  font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem;
  color: rgba(155,146,176,0.75); letter-spacing: 0.08em; margin-top: 0.85rem;
}
.lab-room-shell {
  position: relative; border-radius: 16px; overflow: hidden;
  border: 1px solid rgba(196,167,231,0.2);
  background:
    radial-gradient(ellipse 70% 50% at 50% 0%, rgba(88,28,135,0.18), transparent 55%),
    radial-gradient(ellipse 40% 30% at 80% 20%, rgba(220,38,38,0.08), transparent 50%),
    linear-gradient(180deg, #0c0a14 0%, #08070e 100%);
  box-shadow: 0 20px 60px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.04);
  padding: 1.25rem 1.1rem 1.4rem; animation: labFadeIn 0.7s ease both;
}
.lab-scanline {
  pointer-events: none; position: absolute; inset: 0;
  background: repeating-linear-gradient(0deg, transparent 0px, transparent 3px, rgba(0,0,0,0.08) 3px, rgba(0,0,0,0.08) 4px);
  opacity: 0.35; z-index: 2;
}
.lab-header {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem;
  margin-bottom: 1.1rem; position: relative; z-index: 3;
}
.lab-badge {
  font-family: 'Orbitron', sans-serif; font-size: 0.72rem; letter-spacing: 0.2em;
  color: #fca5a5; background: rgba(127,29,29,0.35); border: 1px solid rgba(248,113,113,0.35);
  padding: 0.35rem 0.7rem; border-radius: 999px;
  box-shadow: 0 0 20px rgba(248,113,113,0.15);
  animation: badgePulse 2.8s ease-in-out infinite;
}
@keyframes badgePulse {
  0%, 100% { box-shadow: 0 0 12px rgba(248,113,113,0.12); }
  50% { box-shadow: 0 0 22px rgba(248,113,113,0.35); }
}
.lab-room-title {
  font-family: 'Orbitron', sans-serif; font-size: clamp(1rem, 3vw, 1.35rem);
  letter-spacing: 0.14em; color: #f3eefc; margin: 0 0 0.25rem;
}
.lab-room-sub {
  font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem;
  color: var(--lab-muted); letter-spacing: 0.04em;
}
.lab-progress-wrap { margin: 0.5rem 0 1.15rem; position: relative; z-index: 3; }
.lab-progress-label {
  display: flex; justify-content: space-between;
  font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem;
  color: var(--lab-muted); margin-bottom: 0.4rem; letter-spacing: 0.06em;
}
.lab-progress-bar {
  height: 6px; border-radius: 999px; background: rgba(255,255,255,0.06);
  overflow: hidden; border: 1px solid rgba(196,167,231,0.12);
}
.lab-progress-fill {
  height: 100%; border-radius: 999px;
  background: linear-gradient(90deg, #7c3aed, #a78bfa, #67e8f9);
  box-shadow: 0 0 12px rgba(167,139,250,0.5);
  transition: width 0.55s cubic-bezier(0.22, 1, 0.36, 1);
}
.lab-dossier {
  margin-top: 1.15rem; border-radius: 14px; padding: 1.15rem 1.2rem 1.25rem;
  background: linear-gradient(165deg, rgba(18,14,28,0.97), rgba(10,8,16,0.99));
  border: 1px solid rgba(196,167,231,0.28);
  box-shadow: 0 16px 40px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04);
  animation: dossierIn 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
  position: relative; z-index: 3;
}
@keyframes dossierIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: none; }
}
.lab-dossier-tag {
  font-family: 'Orbitron', sans-serif; font-size: 0.62rem; letter-spacing: 0.18em;
  color: #a78bfa; margin-bottom: 0.55rem;
}
.lab-whisper {
  margin-top: 0.85rem; font-family: 'Cormorant Garamond', Georgia, serif;
  font-style: italic; font-size: 0.95rem; color: #a78bfa; opacity: 0.9;
  border-left: 2px solid rgba(167,139,250,0.4); padding-left: 0.75rem;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    # ---- DOOR PHASE ----
    if not st.session_state.lab_intro_done:
        st.markdown(
            """
<div class="lab-door-stage lab-root">
  <div class="lab-door-frame">
    <div class="lab-door">
      <div class="lab-door-seal">SEALED · M-119</div>
      <div class="lab-door-handle"></div>
      <div class="lab-door-warning">OBSERVER PROTOCOL REQUIRED</div>
    </div>
  </div>
  <div class="lab-door-title">OBSERVATION LAB</div>
  <div class="lab-door-sub">
    The door is warm. Not from heat — from attention.
    Something on the other side prefers to be watched.
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("▸  Enter the lab", use_container_width=True, type="primary", key="lab_enter_cinematic"):
                st.session_state.lab_intro_done = True
                st.session_state.lab_flicker = True
                st.rerun()
        st.markdown(
            '<p class="lab-door-hint" style="text-align:center;">Fragments wait inside · leave nothing unread</p>',
            unsafe_allow_html=True,
        )
        st.stop()

    # ---- TRANSITION (one-shot) ----
    if st.session_state.get("lab_flicker"):
        st.markdown(
            """
<style>
#lab-blast {
  position: fixed; inset: 0; z-index: 999998; background: #000;
  animation: labBlast 1.35s ease forwards; pointer-events: none;
}
@keyframes labBlast {
  0% { opacity: 1; }
  15% { opacity: 1; background: #1a0a0a; }
  30% { opacity: 0.85; background: #0a0010; }
  55% { opacity: 0.4; }
  100% { opacity: 0; visibility: hidden; }
}
#lab-blast-scan {
  position: fixed; left: 0; right: 0; height: 12%; z-index: 999999; pointer-events: none;
  background: linear-gradient(180deg, transparent, rgba(196,167,231,0.15), transparent);
  animation: labScanDrop 1.2s linear forwards;
}
@keyframes labScanDrop {
  from { top: -15%; opacity: 0.8; }
  to { top: 110%; opacity: 0; }
}
</style>
<div id="lab-blast"></div>
<div id="lab-blast-scan"></div>
            """,
            unsafe_allow_html=True,
        )
        st.session_state.lab_flicker = False

    # ---- ROOM ----
    found = st.session_state.lab_found
    if not isinstance(found, set):
        found = set(found or [])
        st.session_state.lab_found = found
    n_found = len(found)
    pct = int(round(100 * n_found / 6))

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

    st.markdown(
        f"""
<div class="lab-room-shell lab-root">
  <div class="lab-scanline"></div>
  <div class="lab-header">
    <div>
      <div class="lab-room-title">M-119 · OBSERVATION LOG</div>
      <div class="lab-room-sub">Lights unstable · inspect everything · leave nothing unread</div>
    </div>
    <div class="lab-badge">SEALED</div>
  </div>
  <div class="lab-progress-wrap">
    <div class="lab-progress-label">
      <span>FRAGMENTS RECOVERED</span>
      <span>{n_found} / 6 · {pct}%</span>
    </div>
    <div class="lab-progress-bar">
      <div class="lab-progress-fill" style="width:{pct}%;"></div>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#9b92b0;'
        'letter-spacing:0.08em;margin:0.85rem 0 0.5rem;">THE ROOM — choose what to examine</p>',
        unsafe_allow_html=True,
    )

    row1 = st.columns(3)
    row2 = st.columns(3)
    cols = list(row1) + list(row2)
    for col, (key, label, icon, body) in zip(cols, HOTSPOTS):
        with col:
            is_found = key in found
            prefix = "✓ " if is_found else f"{icon} "
            if st.button(f"{prefix}{label}", use_container_width=True, key=f"lab_hs_{key}"):
                st.session_state.lab_found = set(st.session_state.lab_found) | {key}
                st.session_state["lab_focus"] = key
                st.session_state["lab_focus_body"] = body
                st.rerun()

    focus = st.session_state.get("lab_focus")
    body = st.session_state.get("lab_focus_body")
    if focus and body:
        st.markdown(
            f"""
<div class="lab-dossier">
  <div class="lab-dossier-tag">DOSSIER · {focus.upper()}</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(body)

        found_n = len(st.session_state.lab_found) if isinstance(st.session_state.lab_found, set) else len(set(st.session_state.lab_found or []))
        if focus == "floor" and found_n >= 3:
            st.markdown(
                '<p class="lab-whisper">…under the stain, in smaller script:<br/>'
                '<span style="color:#c4b5fd;">she answers to stringbean · say it kindly</span></p>',
                unsafe_allow_html=True,
            )
        if focus == "window" and found_n >= 4:
            st.markdown(
                '<p class="lab-whisper">Through the scratched paint, for a fraction of a second, '
                'the corridor looks back.</p>',
                unsafe_allow_html=True,
            )
        if focus == "terminal" and found_n >= 5:
            st.markdown(
                '<p class="lab-whisper">The cursor blinks once more than it should — '
                'as if acknowledging an observer.</p>',
                unsafe_allow_html=True,
            )

    if n_found >= 6:
        st.markdown("---")
        st.success("All six fragments recovered. The room has nothing left to hide — only what it refuses to name.")
        if st.button("Mark lab complete · secure Voss signal", key="lab_complete_glitch"):
            st.components.v1.html(
                """
                <script>
                (function(){try{
                  var a=new Audio("https://raw.githubusercontent.com/md505d1-art/Meridium-ai/main/assets/artmanzh-sea-sunset-lofi-g-major-543349.mp3");
                  a.volume=0.45;a.play().catch(function(){});
                }catch(e){}})();
                </script>
                """,
                height=0,
            )
            found_l = list(st.session_state.get("glitches_found") or [])
            if "lab" not in found_l:
                found_l.append("lab")
                st.session_state.glitches_found = found_l
                st.session_state["_glitch_flash"] = "Voss log: lab marker secured. The pane noticed you back."
                if set(found_l) >= {"home", "lab", "pixel"}:
                    st.session_state.voss_file_unlocked = True
                    st.session_state["_glitch_flash"] = "All three markers secured. Dr. Voss left you a file."
                    st.session_state.voss_cutscene_stage = 0
                    st.session_state.view = "voss_file"
                try:
                    import json, hashlib
                    from pathlib import Path as _P2
                    from datetime import datetime
                    name = (st.session_state.get("username") or "").strip()
                    if name:
                        key = hashlib.sha256(name.lower().encode()).hexdigest()[:24]
                        for fp in (
                            _P2(__file__).parent / "data" / f"{key}.json",
                            _P2("/tmp") / f"meridium_{hashlib.sha256(name.lower().encode()).hexdigest()[:16]}.json",
                        ):
                            try:
                                data = {}
                                if fp.exists():
                                    data = json.loads(fp.read_text(encoding="utf-8"))
                                data["glitches_found"] = found_l
                                data["voss_file_unlocked"] = bool(st.session_state.get("voss_file_unlocked"))
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

    if st.button("← Leave the lab", key="lab_leave_home"):
        st.session_state.view = "home"
        st.rerun()

    st.stop()
