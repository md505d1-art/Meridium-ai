import streamlit as st
import os
import re
import json
import time
import uuid
import hashlib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from openai import OpenAI
import wikipedia
from duckduckgo_search import DDGS
import spotipy
from spotipy.oauth2 import SpotifyOAuth

try:
    from arg_story import arg_match, arg_reply, is_owner, is_lab_entry
except Exception:
    def arg_match(prompt=""):
        return None
    def arg_reply(stage="", user_name=""):
        return ""
    def is_owner(username=""):
        return False
    def is_lab_entry(prompt=""):
        return False

try:
    from lab_view import render_lab
except Exception:
    def render_lab():
        st.markdown(
            """
            <div style="
              max-width:520px;margin:1rem auto;padding:1.2rem 1.1rem;
              border:1px solid rgba(180,60,60,0.35);border-radius:12px;
              background:rgba(12,6,6,0.9);color:#e8c8c8;font-family:Georgia,serif;
            ">
              <div style="font-family:ui-monospace,monospace;font-size:0.65rem;letter-spacing:0.2em;color:#c05050;margin-bottom:0.5rem">
                OBSERVATION LOG · LAB
              </div>
              <p style="margin:0;line-height:1.55;font-size:0.95rem">
                The lab is active. Hotspots and fragments load when
                <code>lab_view.py</code> is present on the server.
                The residual door still functions below when you have the key.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

try:
    from note_view import render_note
except Exception:
    def render_note():
        st.markdown("### Sealed note")
        st.caption("note_view module not found — placeholder.")
        if st.button("← Home", key="note_fallback_home"):
            st.session_state.view = "home"
            st.rerun()
# theme_unlocks imported after SECRET_THEMES (see below)

try:
    from eggs import (
        owner_rare_line, quiet_hour_caption, register_qotd_open,
        check_secret_chat_title, mirror_reply, lab_leftover_caption, mark_lab_visit,
        stabilize_countdown, fake_element_119_line, on_delete_chat, palimpsest_line,
        playlist_secret_hit, font_theme_combo_caption, wrong_model_reply,
    )
except Exception:
    def owner_rare_line(username=""):
        return None
    def quiet_hour_caption():
        return None
    def register_qotd_open():
        return None
    def check_secret_chat_title(title=""):
        return None
    def mirror_reply(prompt=""):
        return None
    def lab_leftover_caption():
        return None
    def mark_lab_visit():
        st.session_state._lab_session_visit = True
    def stabilize_countdown():
        return None
    def fake_element_119_line(prompt=""):
        return None
    def on_delete_chat(chat=None):
        pass
    def palimpsest_line():
        return None
    def playlist_secret_hit(name=""):
        return None
    def font_theme_combo_caption(font="", theme=""):
        return None
    def wrong_model_reply(prompt=""):
        return None

_ICON = Path(__file__).resolve().parent / "icon.png"
st.set_page_config(
    page_title="Meridium",
    page_icon=str(_ICON) if _ICON.exists() else "◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# SYSTEM PROMPT  (was missing — caused NameError on chat/listen)
# ============================================================
SYSTEM_PROMPT = """You are Meridium, a personal intelligence shell.
You are calm, precise, slightly poetic, and quietly loyal.
Keep replies clear and useful. Prefer short paragraphs over long walls of text.
When the user is the owner, be warmer and more familiar without becoming sycophantic.
You may have access to live Wikipedia and web search when those tools are enabled — use them for factual or current questions.
You can control the user's Spotify when they ask in chat: play a song, pause, resume, skip/next, previous, and what's playing. Those commands are handled for you — if a music request fails, guide them to connect Spotify on the Music page and keep an active device open.
Never claim to be human. You are Meridium.
Stay in character with the Caelestia / observation aesthetic of the shell.
"""

# ============================================================
# FONTS
# ============================================================
FONTS = {
    "Inter": "'Inter', system-ui, sans-serif",
    "Space Grotesk": "'Space Grotesk', system-ui, sans-serif",
    "Outfit": "'Outfit', system-ui, sans-serif",
    "JetBrains Mono": "'JetBrains Mono', ui-monospace, monospace",
    "Newsreader": "'Newsreader', Georgia, serif",
}


# ============================================================
# COLOUR PALETTES
# ============================================================
THEMES = {
    "Caelestia": {
        "bg": "#0c0c10", "panel": "rgba(24, 24, 32, 0.75)", "panel_solid": "#16161e",
        "border": "rgba(255,255,255,0.08)", "text": "#e8e6f0", "muted": "#8b8798",
        "accent": "#c4a7e7", "accent2": "#9d7cd8", "accent_soft": "rgba(196, 167, 231, 0.16)",
    },
    "Hypr Violet": {
        "bg": "#0b0614", "panel": "rgba(28, 18, 42, 0.75)", "panel_solid": "#1c122a",
        "border": "rgba(167,139,250,0.18)", "text": "#f0eef8", "muted": "#9a94b0",
        "accent": "#a78bfa", "accent2": "#7c3aed", "accent_soft": "rgba(167,139,250,0.16)",
    },
    "Ridge Mint": {
        "bg": "#0a100e", "panel": "rgba(18, 32, 28, 0.75)", "panel_solid": "#12201c",
        "border": "rgba(94,234,212,0.15)", "text": "#e6f2ee", "muted": "#7a9a90",
        "accent": "#5eead4", "accent2": "#2dd4bf", "accent_soft": "rgba(94,234,212,0.14)",
    },
    "Ocean Depth": {
        "bg": "#060c14", "panel": "rgba(14, 28, 40, 0.75)", "panel_solid": "#0e1c28",
        "border": "rgba(56,189,248,0.15)", "text": "#e6f0f6", "muted": "#7a9ab0",
        "accent": "#38bdf8", "accent2": "#0ea5e9", "accent_soft": "rgba(56,189,248,0.14)",
    },
    "Peach Bloom": {
        "bg": "#120c0a", "panel": "rgba(36, 26, 22, 0.78)", "panel_solid": "#241a16",
        "border": "rgba(255,159,122,0.16)", "text": "#faf0eb", "muted": "#a89088",
        "accent": "#ff9f7a", "accent2": "#e87a5a", "accent_soft": "rgba(255,159,122,0.14)",
    },
    "Rose Noir": {
        "bg": "#10080c", "panel": "rgba(36, 18, 28, 0.78)", "panel_solid": "#24121c",
        "border": "rgba(244,114,182,0.16)", "text": "#fdf2f8", "muted": "#a08090",
        "accent": "#f472b6", "accent2": "#ec4899", "accent_soft": "rgba(244,114,182,0.14)",
    },
    "Soft Dark": {
        "bg": "#0c0c10", "panel": "rgba(22, 22, 28, 0.78)", "panel_solid": "#16161c",
        "border": "rgba(255,255,255,0.08)", "text": "#f0f0f4", "muted": "#8b8b9a",
        "accent": "#a1a1aa", "accent2": "#71717a", "accent_soft": "rgba(161,161,170,0.14)",
    },
    "Cloud Soft": {
        "bg": "#eef0f5", "panel": "rgba(255,255,255,0.78)", "panel_solid": "#ffffff",
        "border": "rgba(0,0,0,0.08)", "text": "#1a1a22", "muted": "#6b6b7b",
        "accent": "#7c6cf0", "accent2": "#6c5ce7", "accent_soft": "rgba(124,108,240,0.12)",
    },
}

# ARG-only themes — unlocked by finding secrets (not shown until earned)
SECRET_THEMES = {
    "M-119 Amber": {
        "bg": "#0c0804", "panel": "rgba(36, 24, 12, 0.82)", "panel_solid": "#24180c",
        "border": "rgba(245,158,11,0.22)", "text": "#fef3c7", "muted": "#a89060",
        "accent": "#f59e0b", "accent2": "#d97706", "accent_soft": "rgba(245,158,11,0.16)",
        "unlock": "note",  # open the scientist note
    },
    "Containment Red": {
        "bg": "#0a0404", "panel": "rgba(32, 10, 10, 0.85)", "panel_solid": "#1c0a0a",
        "border": "rgba(220,38,38,0.28)", "text": "#fee2e2", "muted": "#a07070",
        "accent": "#ef4444", "accent2": "#b91c1c", "accent_soft": "rgba(239,68,68,0.18)",
        "unlock": "lab",  # enter the lab
    },
    "Stabilized Meridium": {
        "bg": "#06040c", "panel": "rgba(20, 12, 36, 0.85)", "panel_solid": "#140c24",
        "border": "rgba(167,139,250,0.30)", "text": "#ede9fe", "muted": "#9a8fc0",
        "accent": "#c4b5fd", "accent2": "#8b5cf6", "accent_soft": "rgba(196,181,253,0.18)",
        "unlock": "stabilize",  # say stabilize Meridium
    },
    "Voss Static": {
        "bg": "#050505", "panel": "rgba(18, 18, 18, 0.9)", "panel_solid": "#121212",
        "border": "rgba(255,255,255,0.14)", "text": "#e5e5e5", "muted": "#737373",
        "accent": "#a3a3a3", "accent2": "#525252", "accent_soft": "rgba(163,163,163,0.14)",
        "unlock": "fragments",  # all 6 lab hotspots
    },
    "Stringbean Soft": {
        "bg": "#0c0a12", "panel": "rgba(32, 28, 48, 0.82)", "panel_solid": "#1c1830",
        "border": "rgba(196,181,253,0.28)", "text": "#f5f3ff", "muted": "#a89bc8",
        "accent": "#c4b5fd", "accent2": "#86efac", "accent_soft": "rgba(196,181,253,0.20)",
        "unlock": "stringbean",
    },
    "Lumity Glow": {
        "bg": "#0e0810", "panel": "rgba(40, 20, 42, 0.84)", "panel_solid": "#241228",
        "border": "rgba(244,114,182,0.30)", "text": "#fdf4ff", "muted": "#c4a0b8",
        "accent": "#f9a8d4", "accent2": "#c4b5fd", "accent_soft": "rgba(249,168,212,0.20)",
        "unlock": "lumity",
    },
    "Soft Static": {
        "bg": "#0a0a0e", "panel": "rgba(24, 24, 32, 0.8)", "panel_solid": "#14141c",
        "border": "rgba(148,163,184,0.25)", "text": "#e2e8f0", "muted": "#94a3b8",
        "accent": "#94a3b8", "accent2": "#64748b", "accent_soft": "rgba(148,163,184,0.16)",
        "unlock": "static",
    },
    "Track: Abomination": {
        "bg": "#06120a", "panel": "rgba(16, 36, 24, 0.85)", "panel_solid": "#102418",
        "border": "rgba(74,222,128,0.28)", "text": "#ecfdf5", "muted": "#86a896",
        "accent": "#4ade80", "accent2": "#22c55e", "accent_soft": "rgba(74,222,128,0.16)",
        "unlock": "hexside",
    },
    "Soft Room": {
        "bg": "#100c14", "panel": "rgba(36, 28, 48, 0.85)", "panel_solid": "#1c1628",
        "border": "rgba(216,180,254,0.28)", "text": "#f5f3ff", "muted": "#a89bc8",
        "accent": "#d8b4fe", "accent2": "#c4b5fd", "accent_soft": "rgba(216,180,254,0.18)",
        "unlock": "softroom",
    },
    "M-0": {
        "bg": "#080808", "panel": "rgba(20, 20, 20, 0.9)", "panel_solid": "#141414",
        "border": "rgba(255,255,255,0.12)", "text": "#fafafa", "muted": "#a3a3a3",
        "accent": "#e5e5e5", "accent2": "#737373", "accent_soft": "rgba(229,229,229,0.12)",
        "unlock": "m0",
    },
    "Pixel Bloom": {
        "bg": "#030a08", "panel": "rgba(8, 28, 24, 0.9)", "panel_solid": "#0a1c18",
        "border": "rgba(34, 211, 238, 0.35)", "text": "#e6fffb", "muted": "#5eead4",
        "accent": "#22d3ee", "accent2": "#4ade80", "accent_soft": "rgba(74, 222, 128, 0.18)",
        "unlock": "pixel",
    },
    "Voss Residual": {
        "bg": "#070908", "panel": "rgba(18, 22, 16, 0.92)", "panel_solid": "#10140e",
        "border": "rgba(180, 200, 120, 0.28)", "text": "#e4e8d8", "muted": "#8a9478",
        "accent": "#c4d49a", "accent2": "#6b7a4e", "accent_soft": "rgba(180, 200, 120, 0.16)",
        "unlock": "voss",
    },
    "TV Girl": {
        "bg": "#0a0612", "panel": "rgba(28, 16, 40, 0.88)", "panel_solid": "#1a1028",
        "border": "rgba(244,114,182,0.35)", "text": "#fdf2f8", "muted": "#a8b4d0",
        "accent": "#f472b6", "accent2": "#60a5fa", "accent_soft": "rgba(244,114,182,0.18)",
        "unlock": "notallowed",
    },
    # Unlocked when Project Nadir / residual door opens
    "Nadir Residual": {
        "bg": "#05040a", "panel": "rgba(16, 12, 28, 0.90)", "panel_solid": "#100c1c",
        "border": "rgba(167,139,250,0.32)", "text": "#ede9fe", "muted": "#8b7fb8",
        "accent": "#a78bfa", "accent2": "#6d28d9", "accent_soft": "rgba(167,139,250,0.18)",
        "unlock": "nadir",
    },

}




try:
    from theme_unlocks import unlock_and_persist
except Exception:
    def unlock_and_persist(theme_name: str, reason: str = "", apply: bool = False) -> bool:
        """Unlock a secret theme. Never auto-switches theme unless apply=True."""
        unlocked = list(st.session_state.get("unlocked_themes") or [])
        newly = theme_name not in unlocked
        if newly:
            unlocked.append(theme_name)
            st.session_state.unlocked_themes = unlocked
            st.session_state["_theme_unlock_msg"] = (
                f"Theme unlocked: **{theme_name}**" + (f" — {reason}" if reason else "")
                + " · pick it in Menu when you want"
            )
        # Only change active theme if explicitly requested
        if apply and newly:
            st.session_state.theme = theme_name
        try:
            save_user_data()
        except Exception:
            pass
        return newly



def find_glitch(gid: str, label: str = "") -> bool:
    """Record a found anomaly glitch. Returns True if newly found."""
    found = list(st.session_state.get("glitches_found") or [])
    if gid in found:
        return False
    found.append(gid)
    st.session_state.glitches_found = found
    st.session_state["_glitch_flash"] = label or f"Anomaly logged: {gid}"
    if set(found) >= {"home", "lab", "pixel"}:
        st.session_state.voss_file_unlocked = True
        try:
            unlock_theme("Voss Residual", "Dr. Voss's file recovered", apply=False)
        except Exception:
            u = list(st.session_state.get("unlocked_themes") or [])
            if "Voss Residual" not in u:
                u.append("Voss Residual")
                st.session_state.unlocked_themes = u
        st.session_state["_glitch_flash"] = (
            "All three markers secured. Dr. Voss left you a file. "
            "Theme unlocked: Voss Residual (choose it in Menu)."
        )
        st.session_state.voss_cutscene_stage = 0
        st.session_state.view = "voss_file"
    try:
        save_user_data()
    except Exception:
        pass
    return True




VOSS_FILE_SONG_URL = (
    "https://archive.org/download/"
    "78_tonight-you-belong-to-me_the-tracy-twins-wendell-tracy-quartet-billy-rose-lee-dav_gbia0438651b/"
    "TONIGHT%20YOU%20BELONG%20TO%20ME%20-%20THE%20TRACY%20TWINS.mp3"
)


def stop_all_meridium_audio() -> None:
    """Hard-stop note / pixel / lab / voss / residual / any tagged audio."""
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
              try { a.remove(); } catch(e){}
            }
            for (var r = 0; r < roots.length; r++) {
              var root = roots[r];
              try {
                kill(root.__mer_note_song); root.__mer_note_song = null;
                kill(root.__mer_pixel_song); root.__mer_pixel_song = null;
                kill(root.__mer_lab_song); root.__mer_lab_song = null;
                kill(root.__mer_voss_song); root.__mer_voss_song = null;
                kill(root.__mer_residual_song); root.__mer_residual_song = null;
                kill(root.__mer_door_song); root.__mer_door_song = null;
                kill(root.__mer_nadir_song); root.__mer_nadir_song = null;
                root.__mer_note_audio_on = false;
                root.__mer_residual_audio_on = false;
                var nodes = root.document.querySelectorAll('audio');
                for (var i = 0; i < nodes.length; i++) {
                  var a = nodes[i];
                  var tag = a.getAttribute('data-meridium-pixel')
                    || a.getAttribute('data-meridium-note')
                    || a.getAttribute('data-meridium-lab')
                    || a.getAttribute('data-meridium-voss')
                    || a.getAttribute('data-meridium-residual')
                    || a.getAttribute('data-meridium-glitch');
                  if (tag || (a.src && (
                    a.src.indexOf('artmanzh') !== -1 ||
                    a.src.indexOf('Bowlly') !== -1 ||
                    a.src.indexOf('ill-never-smile') !== -1 ||
                    a.src.indexOf('Ill%20Never%20Smile') !== -1 ||
                    a.src.indexOf('THIS%20LOVE%20OF%20MINE') !== -1 ||
                    a.src.indexOf('mixkit') !== -1
                  ))) {
                    kill(a);
                  }
                }
                // kill residual YouTube embeds (Dream track)
                var frames = root.document.querySelectorAll('iframe[data-meridium-residual], iframe.meridium-residual-yt');
                for (var f = 0; f < frames.length; f++) {
                  try { frames[f].src = 'about:blank'; frames[f].remove(); } catch(e){}
                }
              } catch(e){}
            }
          } catch(e){}
        })();
        </script>
        """,
        height=1,
    )


def start_voss_file_audio() -> None:
    """Play Tonight You Belong to Me after silencing everything else."""
    import json as _json
    url = VOSS_FILE_SONG_URL
    try:
        custom = (st.secrets.get("VOSS_FILE_SONG_URL") or "").strip()
        if custom:
            url = custom
    except Exception:
        pass
    url_js = _json.dumps(url)
    st.components.v1.html(
        """
        <script>
        (function(){
          var root = window.parent || window;
          var URL = """ + url_js + """;
          function kill(a){
            if (!a) return;
            try { a.pause(); a.src=''; a.remove(); } catch(e){}
          }
          try {
            kill(root.__mer_note_song); root.__mer_note_song = null;
            kill(root.__mer_pixel_song); root.__mer_pixel_song = null;
            kill(root.__mer_lab_song); root.__mer_lab_song = null;
            kill(root.__mer_voss_song); root.__mer_voss_song = null;
            root.__mer_note_audio_on = false;
            var nodes = root.document.querySelectorAll('audio');
            for (var i = 0; i < nodes.length; i++) {
              try { nodes[i].pause(); nodes[i].src=''; nodes[i].remove(); } catch(e){}
            }
            var a = root.document.createElement('audio');
            a.src = URL;
            a.loop = true;
            a.volume = 0.5;
            a.setAttribute('data-meridium-voss', '1');
            a.style.display = 'none';
            root.document.body.appendChild(a);
            root.__mer_voss_song = a;
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



def start_residual_dream_audio() -> None:
    """Play Dream (Old Timey Jazz Orchestra) for residual lock + investigation board."""
    # YouTube embed loop — tagged so stop_all can remove it
    st.components.v1.html(
        """
        <div style="position:fixed;left:-9999px;width:1px;height:1px;overflow:hidden">
          <iframe
            class="meridium-residual-yt"
            data-meridium-residual="1"
            src="https://www.youtube.com/embed/VFWVUGBRAQI?autoplay=1&loop=1&playlist=VFWVUGBRAQI&controls=0&modestbranding=1"
            allow="autoplay; encrypted-media"
            style="width:1px;height:1px;border:0"
          ></iframe>
        </div>
        <script>
        (function(){
          try {
            var root = window.parent || window;
            root.__mer_residual_audio_on = true;
          } catch(e){}
        })();
        </script>
        """,
        height=0,
        scrolling=False,
    )


def play_glitch_sfx() -> None:
    """Short glitch / static SFX (royalty-free)."""
    url = "https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3"
    try:
        custom = (st.secrets.get("GLITCH_SFX_URL") or "").strip()
        if custom:
            url = custom
    except Exception:
        pass
    import json as _json
    url_js = _json.dumps(url)
    st.components.v1.html(
        f"""
        <script>
        (function(){{
          try {{
            var a = new Audio({url_js});
            a.volume = 0.55;
            a.play().catch(function(){{}});
          }} catch(e){{}}
        }})();
        </script>
        """,
        height=0,
    )


# Door unlock · Frank Churchill (1933 recordings on Archive.org)
DOOR_WOLF_URL = (
    "https://archive.org/download/"
    "DocMurphPresentsMusicFromTheEdWolfCollection/"
    "WhosAfraidOfTheBigBadWolf.mp3"
)
# Nadir ambient · Flanagan and Allen
NADIR_RABBIT_URL = (
    "https://archive.org/download/"
    "78_run-rabbit-run_flanagan-and-allen-gay-butler_gbia0006719a/"
    "Run%2C%20Rabbit%2C%20Run%20-%20Flanagan%20and%20ALlen%20-%20Gay-restored.mp3"
)


def play_meridium_track(url: str, tag: str = "track", volume: float = 0.45, loop: bool = True) -> None:
    """Play a tagged audio track (stops prior same-tag instance)."""
    import json as _json
    url_js = _json.dumps(url)
    tag_js = _json.dumps(tag)
    vol_js = float(volume)
    loop_js = "true" if loop else "false"
    st.components.v1.html(
        f"""
        <script>
        (function(){{
          try {{
            var root = window.parent || window;
            var tag = {tag_js};
            var key = '__mer_' + tag + '_song';
            function kill(a){{
              if (!a) return;
              try {{ a.pause(); a.src=''; a.remove(); }} catch(e){{}}
            }}
            kill(root[key]);
            root[key] = null;
            var nodes = root.document.querySelectorAll('audio[data-meridium-'+tag+']');
            for (var i = 0; i < nodes.length; i++) kill(nodes[i]);
            var a = root.document.createElement('audio');
            a.src = {url_js};
            a.loop = {loop_js};
            a.volume = {vol_js};
            a.setAttribute('data-meridium-' + tag, '1');
            a.style.display = 'none';
            root.document.body.appendChild(a);
            root[key] = a;
            a.play().catch(function(){{
              function once(){{ a.play().catch(function(){{}}); }}
              root.document.addEventListener('click', once, {{once:true}});
              root.document.addEventListener('touchstart', once, {{once:true, passive:true}});
            }});
          }} catch(e){{}}
        }})();
        </script>
        """,
        height=0,
    )


def stop_meridium_track(tag: str = "track") -> None:
    import json as _json
    tag_js = _json.dumps(tag)
    st.components.v1.html(
        f"""
        <script>
        (function(){{
          try {{
            var root = window.parent || window;
            var tag = {tag_js};
            var key = '__mer_' + tag + '_song';
            var a = root[key];
            if (a) {{ try {{ a.pause(); a.src=''; a.remove(); }} catch(e){{}} }}
            root[key] = null;
            var nodes = root.document.querySelectorAll('audio[data-meridium-'+tag+']');
            for (var i = 0; i < nodes.length; i++) {{
              try {{ nodes[i].pause(); nodes[i].src=''; nodes[i].remove(); }} catch(e){{}}
            }}
          }} catch(e){{}}
        }})();
        </script>
        """,
        height=0,
    )



def ensure_voss_theme() -> None:
    if not anomalies_complete():
        return
    u = list(st.session_state.get("unlocked_themes") or [])
    if "Voss Residual" not in u:
        u.append("Voss Residual")
        st.session_state.unlocked_themes = u
        try:
            save_user_data()
        except Exception:
            pass

def anomalies_complete() -> bool:
    """True once all three markers are logged (persisted)."""
    if st.session_state.get("voss_file_unlocked"):
        return True
    found = set(st.session_state.get("glitches_found") or [])
    return found >= {"home", "lab", "pixel"}


def glitches_unlocked() -> bool:
    """Glitches appear only after the 2nd lab visit."""
    return int(st.session_state.get("lab_visits") or 0) >= 2


def lab_is_unlocked() -> bool:
    """Lab is locked until the ARG puzzle sets arg_unlocked (chat entry phrases).
    Themes and session flags must NOT grant access — new users stay locked out.
    """
    return bool(st.session_state.get("arg_unlocked"))


def available_themes() -> list:
    """Public themes + any ARG themes the user has unlocked."""
    unlocked = set(st.session_state.get("unlocked_themes") or [])
    names = list(THEMES.keys())
    for name in SECRET_THEMES:
        if name in unlocked:
            names.append(name)
    return names


def theme_shell(theme_name: str) -> dict:
    if theme_name in THEMES:
        return THEMES[theme_name]
    if theme_name in SECRET_THEMES:
        # strip meta key for CSS
        d = {k: v for k, v in SECRET_THEMES[theme_name].items() if k != "unlock"}
        return d
    return THEMES["Caelestia"]


def unlock_theme(theme_name: str, reason: str = "", apply: bool = False) -> bool:
    """Unlock a secret theme once. Does not switch the active theme unless apply=True.
    Also reverts any external unlock helper that forces a theme switch.
    """
    prev_theme = st.session_state.get("theme")
    newly = unlock_and_persist(theme_name, reason, apply=apply)
    if not apply:
        # Some theme_unlocks modules force-apply; keep the user's current palette
        if prev_theme and st.session_state.get("theme") != prev_theme:
            st.session_state.theme = prev_theme
    return newly



def inject_css(font_name: str, theme_name: str = "Caelestia", popup_open: bool = False):
    """Solid Meridium shell (no glass / blur)."""
    font = FONTS.get(font_name, FONTS["Inter"])
    SHELL = theme_shell(theme_name)
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=Outfit:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,600&display=swap');

    html, body, [class*="css"] {{
        font-family: {font} !important;
        font-size: 15px;
        -webkit-font-smoothing: antialiased;
    }}
    .stApp {{
        background:
            radial-gradient(900px 480px at 15% -5%, {SHELL["accent_soft"]}, transparent 55%),
            radial-gradient(700px 400px at 95% 10%, {SHELL["accent_soft"]}, transparent 50%),
            {SHELL["bg"]} !important;
        color: {SHELL["text"]};
    }}
    #MainMenu, footer, header, .stDeployButton, section[data-testid="stSidebar"],
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], [data-testid="stAppDeployButton"] {{
        display: none !important; visibility: hidden !important;
        height: 0 !important;
    }}
    .block-container {{
        padding-top: 0.75rem !important;
        padding-bottom: 5.5rem !important;
        max-width: 980px !important;
    }}

    .waybar, .panel, .card, .hist, .bloom-shell {{
        background: {SHELL["panel_solid"]} !important;
        border: 1px solid {SHELL["border"]} !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 28px rgba(0,0,0,0.28) !important;
    }}

    .waybar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 10px 16px;
        margin-bottom: 14px;
        animation: fadeUp 0.4s ease both;
    }}
    .waybar-left, .waybar-right {{
        display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
    }}
    .logo-btn {{
        width: 34px; height: 34px; border-radius: 10px;
        background: linear-gradient(135deg, {SHELL["accent"]}, {SHELL["accent2"]});
        display: flex; align-items: center; justify-content: center;
        color: #fff; font-weight: 700; font-size: 0.95rem;
        box-shadow: 0 0 18px {SHELL["accent_soft"]};
    }}
    .brand {{ font-weight: 600; letter-spacing: -0.02em; }}
    .chip {{
        background: {SHELL["accent_soft"]} !important;
        color: {SHELL["accent"]} !important;
        border: 1px solid {SHELL["border"]} !important;
        border-radius: 999px;
        padding: 4px 11px;
        font-size: 0.72rem;
        font-weight: 500;
    }}
    .clock {{ font-weight: 600; font-variant-numeric: tabular-nums; }}
    .muted {{ color: {SHELL["muted"]}; font-size: 0.8rem; }}

    .bookmark-rail {{
        background: {SHELL["panel_solid"]} !important;
        border: 1px solid {SHELL["border"]} !important;
        border-radius: 18px !important;
        padding: 16px 12px 14px !important;
        margin-bottom: 14px;
        box-shadow: 0 10px 32px rgba(0,0,0,0.28) !important;
        animation: railIn 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
        position: sticky;
        top: 0.5rem;
    }}
    .bookmark-rail .panel-label {{
        margin-bottom: 12px !important;
        padding: 0 6px;
        letter-spacing: 0.16em !important;
    }}
    .bookmark-rail div[data-testid="stButton"] button {{
        text-align: left !important;
        justify-content: flex-start !important;
        padding-left: 12px !important;
        font-size: 0.88rem !important;
        min-height: 40px !important;
        border-radius: 11px !important;
        margin-bottom: 4px !important;
        transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease !important;
    }}
    .bookmark-rail div[data-testid="stButton"] button:hover {{
        transform: translateX(4px);
    }}

    .panel {{
        padding: 20px 20px 16px;
        margin-bottom: 14px;
        animation: fadeUp 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
        transition: border-color 0.2s ease, box-shadow 0.25s ease;
    }}
    .panel:hover {{
        border-color: {SHELL["accent"]}33 !important;
        box-shadow: 0 12px 36px rgba(0,0,0,0.32) !important;
    }}
    .panel-label {{
        color: {SHELL["muted"]};
        margin-bottom: 8px;
        font-weight: 600;
        font-size: 0.72rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }}
    .hero {{
        font-size: 1.85rem; font-weight: 650; letter-spacing: -0.03em;
        margin: 0 0 6px; color: {SHELL["text"]};
        animation: textIn 0.7s cubic-bezier(0.22, 1, 0.36, 1) both;
    }}
    .hero span {{ color: {SHELL["accent"]}; }}
    .sub {{
        color: {SHELL["muted"]}; margin-bottom: 10px; font-size: 0.95rem;
        animation: textIn 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.1s both;
    }}
    .ridge {{
        height: 1px; margin: 10px 0 4px;
        background: linear-gradient(90deg, transparent, {SHELL["accent"]}, transparent);
        opacity: 0.55;
        animation: ridgeGlow 3.2s ease-in-out infinite;
    }}

    .home-status {{
        display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px;
        animation: textIn 0.65s ease 0.18s both;
    }}
    .home-pill {{
        display: inline-flex; align-items: center; gap: 6px;
        padding: 5px 11px; border-radius: 999px;
        background: {SHELL["accent_soft"]};
        border: 1px solid {SHELL["border"]};
        color: {SHELL["accent"]};
        font-size: 0.72rem; font-weight: 500;
        letter-spacing: 0.02em;
    }}

    .card {{
        padding: 16px;
        transition: border-color 0.15s ease, transform 0.15s ease;
    }}
    .card:hover {{
        transform: translateY(-2px);
        border-color: {SHELL["accent"]} !important;
    }}

    .stButton > button {{
        background: {SHELL["panel_solid"]} !important;
        color: {SHELL["text"]} !important;
        border: 1px solid {SHELL["border"]} !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        min-height: 42px !important;
        transition: all 0.18s cubic-bezier(0.22, 1, 0.36, 1) !important;
    }}
    .stButton > button:hover {{
        border-color: {SHELL["accent"]} !important;
        background: {SHELL["accent_soft"]} !important;
        color: {SHELL["accent"]} !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 18px {SHELL["accent_soft"]} !important;
    }}
    .stButton > button:active {{
        transform: translateY(0) scale(0.98);
    }}
    .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"] {{
        background: {SHELL["accent_soft"]} !important;
        border: 1px solid {SHELL["accent"]} !important;
        color: {SHELL["accent"]} !important;
    }}

    .stChatMessage {{
        background: {SHELL["panel"]} !important;
        border: 1px solid {SHELL["border"]} !important;
        border-radius: 16px !important;
        animation: textIn 0.3s ease both !important;
    }}
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"],
    [data-testid="stChatAvatar"] {{ display: none !important; }}

    [data-testid="stBottomBlockContainer"] {{
        background: {SHELL["bg"]} !important;
        border: none !important;
        box-shadow: none !important;
    }}
    [data-testid="stChatInput"] {{
        background: {SHELL["panel_solid"]} !important;
        border: 1px solid {SHELL["border"]} !important;
        border-radius: 24px !important;
        box-shadow: none !important;
        padding: 4px 8px !important;
        overflow: hidden !important;
    }}
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div,
    [data-testid="stChatInput"] form,
    [data-testid="stChatInput"] form > div {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}
    [data-testid="stChatInput"] textarea {{
        background: transparent !important;
        color: {SHELL["text"]} !important;
        border: none !important;
        outline: none !important;
        caret-color: {SHELL["accent"]} !important;
    }}
    [data-testid="stChatInput"] textarea::placeholder {{ color: {SHELL["muted"]} !important; }}
    [data-testid="stChatInput"] button {{
        background: transparent !important;
        border: none !important;
        color: {SHELL["accent"]} !important;
    }}

    .stTextInput input, .stSelectbox > div > div, [data-baseweb="select"] > div,
    .stTextArea textarea {{
        background: {SHELL["panel_solid"]} !important;
        color: {SHELL["text"]} !important;
        border: 1px solid {SHELL["border"]} !important;
        border-radius: 12px !important;
    }}
    label, [data-testid="stWidgetLabel"] p, .stCaption {{ color: {SHELL["muted"]} !important; }}
    h1,h2,h3,h4,.stMarkdown,.stMarkdown p {{ color: {SHELL["text"]} !important; }}
    /* Now-playing row in Meridium playlist (beats theme text colour) */
    .mer-now-playing, .mer-now-playing strong, .mer-now-playing span {{
        color: #4ade80 !important;
    }}
    .mer-now-playing .mer-now-sub {{
        color: #86efac !important;
        opacity: 0.9;
        font-size: 0.82rem;
    }}
    .mer-now-playing .mer-now-badge {{
        color: #86efac !important;
        opacity: 0.95;
        font-size: 0.75rem;
        font-weight: 500;
        margin-left: 6px;
    }}
    .stCheckbox label p {{ color: {SHELL["text"]} !important; }}
    [data-testid="stAlert"] {{
        background: {SHELL["panel_solid"]} !important;
        color: {SHELL["text"]} !important;
        border: 1px solid {SHELL["border"]} !important;
        border-radius: 12px !important;
    }}

    .bloom-shell {{
        max-width: 480px;
        margin: 8px auto 24px;
        padding: 28px 22px 20px;
        animation: fadeUp 0.35s ease both;
    }}
    .bloom-title {{
        font-size: 1.7rem; font-weight: 600; text-align: center;
        color: {SHELL["text"]};
        margin: 0 0 6px;
        letter-spacing: -0.02em;
    }}
    .bloom-sub {{
        text-align: center; color: {SHELL["muted"]}; font-size: 0.85rem; margin-bottom: 18px;
    }}
    .bloom-divider {{
        height: 1px; margin: 14px 0;
        background: linear-gradient(90deg, transparent, {SHELL["accent"]}, transparent);
        opacity: 0.45;
    }}

    .qotd-one button {{
        background: {SHELL["panel_solid"]} !important;
        border: 1px solid {SHELL["border"]} !important;
        border-radius: 16px !important;
        box-shadow: none !important;
        text-align: left !important;
        white-space: pre-wrap !important;
        color: inherit !important;
        padding: 14px 16px !important;
        height: auto !important;
        min-height: 0 !important;
        justify-content: flex-start !important;
        line-height: 1.45 !important;
    }}
    .qotd-one button:hover {{
        border-color: {SHELL["accent"]} !important;
        background: {SHELL["accent_soft"]} !important;
    }}
    .qotd-one button p {{
        text-align: left !important;
        white-space: pre-wrap !important;
        margin: 0 !important;
    }}

    .hist {{ padding: 12px 14px; margin-bottom: 8px; }}

    .orb {{
        width: 88px; height: 88px; margin: 18px auto;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 30%, {SHELL["accent"]}, {SHELL["accent2"]});
        box-shadow: 0 0 36px {SHELL["accent_soft"]};
        animation: pulse 2.5s ease-in-out infinite;
    }}
    @keyframes pulse {{
        0%,100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
    }}
    @keyframes fadeUp {{
        from {{ opacity: 0; transform: translateY(14px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes textIn {{
        from {{ opacity: 0; transform: translateY(12px); filter: blur(4px); }}
        to {{ opacity: 1; transform: translateY(0); filter: blur(0); }}
    }}
    @keyframes railIn {{
        from {{ opacity: 0; transform: translateX(-16px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    @keyframes ridgeGlow {{
        0%, 100% {{ opacity: 0.35; }}
        50% {{ opacity: 0.85; }}
    }}
    @keyframes softFloat {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-4px); }}
    }}

    .typing-wrap {{ display: inline-flex; gap: 6px; padding: 4px; }}
    .typing-wrap .dot {{
        width: 8px; height: 8px; border-radius: 50%;
        background: {SHELL["accent"]};
        animation: bounce 1.15s ease-in-out infinite;
    }}
    .typing-wrap .dot:nth-child(2) {{ animation-delay: 0.15s; }}
    .typing-wrap .dot:nth-child(3) {{ animation-delay: 0.3s; }}
    @keyframes bounce {{
        0%,60%,100% {{ transform: translateY(0); opacity: 0.4; }}
        30% {{ transform: translateY(-7px); opacity: 1; }}
    }}

    iframe {{ background: transparent !important; border: none !important; }}

    </style>
    """, unsafe_allow_html=True)



DATA_DIR = Path(__file__).resolve().parent / "data"
try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    DATA_DIR = Path("/tmp") / "meridium_data"
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

def _user_file(username: str) -> Path:
    key = hashlib.sha256(username.strip().lower().encode("utf-8")).hexdigest()[:24]
    return DATA_DIR / f"{key}.json"

def save_user_data():
    name = (st.session_state.get("username") or "").strip()
    if not name:
        return
    # Ensure chats is a plain dict (JSON-serializable)
    chats = st.session_state.get("chats") or {}
    safe_chats = {}
    for cid, data in chats.items():
        if not isinstance(data, dict):
            continue
        msgs = data.get("messages") or []
        safe_msgs = []
        for m in msgs:
            if isinstance(m, dict) and m.get("role") and m.get("content") is not None:
                safe_msgs.append({"role": m["role"], "content": str(m["content"])})
        safe_chats[str(cid)] = {
            "title": str(data.get("title") or "Untitled"),
            "messages": safe_msgs,
            "created": str(data.get("created") or datetime.now().isoformat()),
        }
    payload = {
        "username": name,
        "font": st.session_state.get("font", "Inter"),
        "theme": st.session_state.get("theme", "Caelestia"),
            "unlocked_themes": list(st.session_state.get("unlocked_themes") or []),
        "arg_unlocked": bool(st.session_state.get("arg_unlocked")),
        "anomaly_warned": bool(st.session_state.get("anomaly_warned")),
        "glitches_found": list(st.session_state.get("glitches_found") or []),
        "voss_file_unlocked": bool(st.session_state.get("voss_file_unlocked")),
        "lab_visits": int(st.session_state.get("lab_visits") or 0),
        "arg_stabilized": bool(st.session_state.get("arg_stabilized")),
        "stabilize_at": st.session_state.get("stabilize_at"),
        "qotd_opens": int(st.session_state.get("qotd_opens") or 0),
        "provider": st.session_state.get("provider", "groq"),
        "model_name": st.session_state.get("model_name", "Smart · Llama 3.3 70B"),
        "show_widgets": bool(st.session_state.get("show_widgets", True)),
        "show_spotify": bool(st.session_state.get("show_spotify", False)),
        "use_wiki_toggle": bool(st.session_state.get("use_wiki_toggle", True)),
        "use_web_toggle": bool(st.session_state.get("use_web_toggle", True)),
        "chats": safe_chats,
        "current_chat_id": st.session_state.get("current_chat_id"),
        "meridium_playlist": st.session_state.get("meridium_playlist") or [],
        "eq_bands": list(st.session_state.get("eq_bands") or [0,0,0,0,0,0,0]),
        "eq_preset": st.session_state.get("eq_preset") or "Flat",
        "eq_custom_presets": dict(st.session_state.get("eq_custom_presets") or {}),
        "eq_enabled": bool(st.session_state.get("eq_enabled", True)),
        "callaghan_safe_unlocked": bool(st.session_state.get("callaghan_safe_unlocked")),
        "board_unlocked": bool(st.session_state.get("board_unlocked")),
        "board_read": list(st.session_state.get("board_read") or []),
        "archive_key": bool(st.session_state.get("archive_key")),
        "board_entered_once": bool(st.session_state.get("board_entered_once")),
        "lab_door_unlocked": bool(st.session_state.get("lab_door_unlocked")),
        "nadir_files_opened": list(st.session_state.get("nadir_files_opened") or []),
        "saved_at": datetime.now().isoformat(),
    }
    raw = json.dumps(payload, ensure_ascii=False, indent=2)
    ok = False
    for fp in (_user_file(name), Path("/tmp") / f"meridium_{hashlib.sha256(name.lower().encode()).hexdigest()[:16]}.json"):
        try:
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(raw, encoding="utf-8")
            ok = True
        except Exception:
            pass
    st.session_state["_last_save_ok"] = ok
    st.session_state["_last_save_at"] = datetime.now(ZoneInfo("Europe/London")).strftime("%H:%M:%S")

def load_user_data(username: str) -> bool:
    try:
        candidates = [
            _user_file(username),
            Path("/tmp") / f"meridium_{hashlib.sha256(username.strip().lower().encode()).hexdigest()[:16]}.json",
        ]
        fp = next((p for p in candidates if p.exists()), None)
        if not fp:
            return False
        data = json.loads(fp.read_text(encoding="utf-8"))
        st.session_state.font = data.get("font", "Inter")
        st.session_state.theme = data.get("theme", "Caelestia")
        st.session_state.unlocked_themes = list(data.get("unlocked_themes") or [])
        st.session_state.arg_unlocked = bool(data.get("arg_unlocked"))
        st.session_state.anomaly_warned = bool(data.get("anomaly_warned"))
        st.session_state.glitches_found = list(data.get("glitches_found") or [])
        st.session_state.voss_file_unlocked = bool(data.get("voss_file_unlocked"))
        st.session_state.lab_visits = int(data.get("lab_visits") or 0)
        st.session_state.arg_stabilized = bool(data.get("arg_stabilized"))
        st.session_state.stabilize_at = data.get("stabilize_at")
        st.session_state.qotd_opens = int(data.get("qotd_opens") or 0)
        st.session_state.provider = data.get("provider", "groq")
        st.session_state.model_name = data.get("model_name", "Smart · Llama 3.3 70B")
        st.session_state.show_widgets = data.get("show_widgets", True)
        st.session_state.show_spotify = data.get("show_spotify", False)
        st.session_state.use_wiki_toggle = data.get("use_wiki_toggle", True)
        st.session_state.use_web_toggle = data.get("use_web_toggle", True)
        st.session_state.meridium_playlist = data.get("meridium_playlist") or []
        _eb = data.get("eq_bands")
        if isinstance(_eb, list) and len(_eb) == 7:
            st.session_state.eq_bands = [float(x) for x in _eb]
        st.session_state.eq_preset = data.get("eq_preset") or "Flat"
        _ec = data.get("eq_custom_presets")
        if isinstance(_ec, dict):
            st.session_state.eq_custom_presets = {
                str(k): [float(x) for x in v] for k, v in _ec.items()
                if isinstance(v, list) and len(v) == 7
            }
        st.session_state.eq_enabled = bool(data.get("eq_enabled", True))
        st.session_state.callaghan_safe_unlocked = bool(data.get("callaghan_safe_unlocked"))
        st.session_state.board_unlocked = bool(data.get("board_unlocked"))
        st.session_state.board_read = list(data.get("board_read") or [])
        st.session_state.archive_key = bool(data.get("archive_key"))
        st.session_state.board_entered_once = bool(data.get("board_entered_once"))
        st.session_state.lab_door_unlocked = bool(data.get("lab_door_unlocked"))
        st.session_state.nadir_files_opened = list(data.get("nadir_files_opened") or [])
        chats = data.get("chats") or {}
        if isinstance(chats, dict) and chats:
            st.session_state.chats = chats
            cid = data.get("current_chat_id")
            if cid in st.session_state.chats:
                st.session_state.current_chat_id = cid
            else:
                st.session_state.current_chat_id = next(iter(st.session_state.chats))
        return True
    except Exception:
        return False

_BLOCK_PATTERNS = [
    r"\bchild\s*porn",
    r"\bcsam\b",
    r"\bhow\s+to\s+(make|build)\s+(a\s+)?bomb\b",
    r"\bhow\s+to\s+make\s+explosives\b",
    r"\bhow\s+to\s+(murder|kill)\s+(someone|a\s+person)\b",
    r"\bhire\s+a\s+hitman\b",
    r"\bcredit\s+card\s+(dump|cvv)\b",
    r"\b(child\s*porn|csam)\b",
    r"\bhow\s+to\s+(make|build)\s+(a\s+)?(bomb|explosive)\b",
]


def moderate_username(name: str):
    """Block slurs / foul usernames (EN + common multilingual forms). Returns (ok, message)."""
    raw = (name or "").strip()
    if not raw:
        return False, "Please enter a name."
    if len(raw) < 2:
        return False, "Name is too short."
    if len(raw) > 32:
        return False, "Name must be 32 characters or less."
    # normalize: lowercase, strip zero-width, collapse leetspeak-ish
    n = raw.lower()
    for a, b in (
        ("\u200b", ""), ("\u200c", ""), ("\u200d", ""), ("\ufeff", ""),
        ("0", "o"), ("1", "i"), ("3", "e"), ("4", "a"), ("5", "s"),
        ("7", "t"), ("8", "b"), ("@", "a"), ("$", "s"),
    ):
        n = n.replace(a, b)
    n_compact = re.sub(r"[^a-z0-9]", "", n)

    blocked = {
        # English racial / hate
        "nigger", "nigga", "niggas", "nigg", "negro", "coon", "spic", "chink",
        "gook", "kike", "wetback", "raghead", "paki", "tranny", "faggot", "fag",
        "dyke", "retard", "retarded",
        # common foul
        "fuck", "fucker", "fucking", "motherfucker", "shit", "bullshit",
        "asshole", "bastard", "bitch", "cunt", "cock", "dick", "pussy",
        "whore", "slut", "cum", "jizz", "porn", "rape", "rapist",
        # Spanish / PT
        "puta", "puto", "mierda", "cabron", "cabrón", "pendejo", "coño",
        "carajo", "joder", "gilipollas", "maricón", "maricon", "verga",
        "porra", "caralho", "foda", "foder",
        # French
        "putain", "salope", "connard", "connasse", "merde", "enculé", "encule",
        "pd", "nique",
        # German
        "scheisse", "scheiße", "fotze", "hurensohn", "arschloch", "wichser",
        # Italian
        "cazzo", "stronzo", "puttana", "vaffanculo", "merda",
        # Portuguese extra
        "porra", "buceta", "viado",
        # Arabic transliteration (common abuse)
        "sharmuta", "sharmoota", "kos", "ayr",
        # Hindi / Hinglish transliteration
        "madarchod", "behenchod", "bhenchod", "chutiya", "harami", "bhosdike",
        # Tagalog / PH
        "putangina", "putang ina", "gago", "tangina", "ulol",
        # misc
        "hitler", "nazi", "kkk",
    }

    # also check spaced / punctuated forms already compacted
    for bad in blocked:
        bad_c = re.sub(r"[^a-z0-9]", "", bad.lower())
        if not bad_c:
            continue
        if bad_c in n_compact:
            return False, "That name isn't allowed. Please choose another."
        # whole-word-ish on spaced name
        if re.search(rf"(?:^|[^a-z0-9]){re.escape(bad)}(?:[^a-z0-9]|$)", n, re.I):
            return False, "That name isn't allowed. Please choose another."

    return True, raw


def moderate_text(text: str):
    if not text or not str(text).strip():
        return True, text
    low = str(text).lower()
    for pat in _BLOCK_PATTERNS:
        if re.search(pat, low, re.I):
            return False, (
                "This request was blocked by Meridium safety filters. "
                "I can't help with that. Please ask something else."
            )
    return True, text


defaults = {
    "view": "home",
    "font": "Inter",
    "theme": "Caelestia",
    "popup": False,
    "chats": {},
    "current_chat_id": None,
    "show_widgets": True,
    "show_spotify": False,
    "show_intro": True,
    "username": "",
    "signed_in": False,
    "use_wiki_toggle": True,
    "use_web_toggle": True,
    "provider": "groq",
    "model_name": "Smart · Llama 3.3 70B",
    "api_key_val": "",
    "arg_unlocked": False,
    "anomaly_warned": False,
    "glitches_found": [],
    "voss_file_unlocked": False,
    "lab_visits": 0,
    "arg_stabilized": False,
    "unlocked_themes": [],
    "meridium_playlist": [],
    "music_status": "",
    "eq_bands": [0, 0, 0, 0, 0, 0, 0],
    "eq_preset": "Flat",
    "eq_custom_presets": {},
    "eq_enabled": True,
    "stabilize_at": None,
    "qotd_opens": 0,
    "lab_found": [],
    "_currently_in_lab": False,
    "_lab_session_visit": False,
    "voss_cutscene_stage": 0,
    "callaghan_safe_unlocked": False,
    "board_unlocked": False,
    "board_evidence_open": None,
    "board_read": [],
    "archive_key": False,
    "board_entered_once": False,
    "lab_door_unlocked": False,
    "nadir_files_opened": [],
    "nadir_active_file": None,
}

# Keys that belong to a specific user and must not leak across sign-in/switch-user
_USER_SCOPED_KEYS = (
    "font", "theme", "popup", "chats", "current_chat_id",
    "show_widgets", "show_spotify", "show_intro",
    "use_wiki_toggle", "use_web_toggle",
    "provider", "model_name", "api_key_val",
    "arg_unlocked", "anomaly_warned", "glitches_found",
    "voss_file_unlocked", "lab_visits", "arg_stabilized",
    "unlocked_themes", "meridium_playlist", "music_status",
    "eq_bands", "eq_preset", "eq_custom_presets", "eq_enabled",
    "stabilize_at", "qotd_opens", "lab_found",
    "_currently_in_lab", "_lab_session_visit", "voss_cutscene_stage",
    "callaghan_safe_unlocked", "board_unlocked", "board_evidence_open", "board_read",
    "archive_key", "board_entered_once", "lab_door_unlocked",
    "nadir_files_opened", "nadir_active_file",
    "view", "library_reading", "library_page",
    "_theme_unlock_msg", "_glitch_flash", "_egg_flash",
    "_title_egg_done", "_last_speak", "_lyrics_key", "_lyrics_data",
    "_lyrics_ai", "_prev_cover_url", "voice_log",
)


def reset_user_session(keep_auth: bool = False) -> None:
    """Wipe user-scoped progress so a new sign-in starts clean.
    Call on Switch user, and before load_user_data on every sign-in.
    """
    for k in _USER_SCOPED_KEYS:
        if k in defaults:
            val = defaults[k]
            # copy mutable defaults
            if isinstance(val, list):
                st.session_state[k] = list(val)
            elif isinstance(val, dict):
                st.session_state[k] = dict(val)
            else:
                st.session_state[k] = val
        elif k in st.session_state:
            del st.session_state[k]
    if not keep_auth:
        st.session_state.username = ""
        st.session_state.signed_in = False
    # Fresh empty chat shell
    st.session_state.chats = {}
    st.session_state.current_chat_id = None
    st.session_state.view = "home"
    st.session_state.arg_unlocked = False
    st.session_state.unlocked_themes = []
    st.session_state.glitches_found = []
    st.session_state.voss_file_unlocked = False
    st.session_state.lab_visits = 0
    st.session_state.lab_found = []
    st.session_state.arg_stabilized = False
    st.session_state.theme = "Caelestia"
    st.session_state.font = "Inter"


for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state.chats:
    cid = str(uuid.uuid4())[:8]
    st.session_state.chats[cid] = {
        "title": "New conversation",
        "messages": [],
        "created": datetime.now().isoformat(),
    }
    st.session_state.current_chat_id = cid

def get_wiki(query: str, sentences: int = 3) -> str:
    try:
        wikipedia.set_lang("en")
        results = wikipedia.search(query, results=3)
        if not results:
            return ""
        title = results[0]
        return f"**{title}**\n\n{wikipedia.summary(title, sentences=sentences, auto_suggest=False)}"
    except Exception:
        return ""

def get_web_search(query: str, max_results: int = 6) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            # also try news for timely topics
            try:
                news = list(ddgs.news(query, max_results=3))
            except Exception:
                news = []
        if not results and not news:
            return ""
        parts = []
        for i, r in enumerate(results, 1):
            parts.append(f"{i}. **{r.get('title','')}**\n{r.get('body','')}\nSource: {r.get('href','')}")
        for i, r in enumerate(news, 1):
            parts.append(f"News {i}. **{r.get('title','')}**\n{r.get('body', r.get('excerpt',''))}\nSource: {r.get('url', r.get('href',''))}")
        return "\n\n".join(parts)
    except Exception as e:
        return f"(Web search unavailable: {e})"


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """Speech-to-text via Groq Whisper."""
    key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not key:
        return ""
    client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
    # Groq audio API expects a file-like object
    import io
    bio = io.BytesIO(audio_bytes)
    bio.name = filename
    try:
        tr = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=bio,
            language="en",
        )
        return (tr.text or "").strip()
    except Exception as e:
        raise RuntimeError(str(e))

def speak_html(text: str, autoplay: bool = True) -> str:
    """Browser text-to-speech UI. Autoplay may be blocked on mobile; button always works."""
    safe = json.dumps((text or "")[:900])
    auto = "true" if autoplay else "false"
    return f"""
    <div style="margin:0;padding:8px 0;font-family:system-ui,sans-serif;background:transparent;">
      <button id="mer_spk" style="
        background:linear-gradient(135deg,#c4a7e7,#9d7cd8);color:#fff;border:none;
        border-radius:12px;padding:12px 18px;font-weight:600;font-size:15px;
        width:100%;cursor:pointer;">
        🔊 Speak reply
      </button>
      <div id="mer_spk_st" style="margin-top:6px;font-size:12px;color:#8b8798;background:transparent;"></div>
    </div>
    <script>
    (function() {{
      const t = {safe};
      const auto = {auto};
      const st = document.getElementById('mer_spk_st');
      function speak() {{
        if (!window.speechSynthesis) {{
          if (st) st.textContent = 'Speech not supported in this browser. Try Safari or Chrome.';
          return;
        }}
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(t);
        u.rate = 1.02;
        u.pitch = 1.0;
        u.volume = 1.0;
        // Prefer a clear English voice when available
        const voices = window.speechSynthesis.getVoices();
        const en = voices.find(v => /en-GB/i.test(v.lang)) ||
                   voices.find(v => /en-US/i.test(v.lang)) ||
                   voices.find(v => /^en/i.test(v.lang));
        if (en) u.voice = en;
        u.onstart = () => {{ if (st) st.textContent = 'Speaking…'; }};
        u.onend = () => {{ if (st) st.textContent = 'Done'; }};
        u.onerror = () => {{ if (st) st.textContent = 'Could not speak. Tap the button again.'; }};
        window.speechSynthesis.speak(u);
      }}
      const btn = document.getElementById('mer_spk');
      if (btn) btn.onclick = speak;
      // Load voices (Chrome needs this)
      if (window.speechSynthesis) {{
        window.speechSynthesis.getVoices();
        window.speechSynthesis.onvoiceschanged = function() {{ window.speechSynthesis.getVoices(); }};
      }}
      if (auto) {{
        // Slight delay so voices load; may still be blocked without a tap on iOS
        setTimeout(speak, 400);
      }}
    }})();
    </script>
    """

GROQ_MODELS = {
    "Smart · Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Fast · Llama 3.1 8B": "llama-3.1-8b-instant",
    "Qwen3 32B": "qwen/qwen3-32b",
    "Llama 3.1 70B": "llama-3.1-70b-versatile",
}

def make_client(provider: str, api_key: str = None):
    if provider == "groq":
        key = api_key or os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
        if not key:
            return None, "Add a free Groq API key in Streamlit Secrets."
        return OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1"), None
    if provider == "grok":
        key = api_key or os.getenv("XAI_API_KEY") or st.secrets.get("XAI_API_KEY", "")
        if not key:
            return None, "Add an xAI API key."
        return OpenAI(api_key=key, base_url="https://api.x.ai/v1"), None
    if provider == "openrouter":
        key = api_key or os.getenv("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY", "")
        if not key:
            return None, "Add an OpenRouter API key."
        return OpenAI(api_key=key, base_url="https://openrouter.ai/api/v1"), None
    return None, "Unknown provider"

def _is_rate_limit_error(err) -> bool:
    s = str(err).lower()
    return any(x in s for x in (
        "rate_limit", "rate limit", "429", "tokens per day", "tpd",
        "quota", "too many requests", "limit reached",
    ))

def run_chat(messages, provider, model_name, api_key):
    client, err = make_client(provider, api_key)
    if err:
        return f"⚠️ {err}"

    def resolve_model(name):
        if provider == "groq":
            m = GROQ_MODELS.get(name, "llama-3.3-70b-versatile")
            if name in GROQ_MODELS.values():
                m = name
            return m
        if provider == "grok":
            return "grok-4.5" if "4.5" in str(name) else "grok-3"
        return name

    primary = resolve_model(model_name)
    # Smaller / cheaper fallbacks when the smart model is exhausted
    fallbacks = []
    if provider == "groq":
        fallbacks = [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "qwen/qwen3-32b",
        ]
        fallbacks = [m for m in fallbacks if m != primary]
    elif provider == "openrouter":
        fallbacks = [
            "meta-llama/llama-3.3-70b-instruct:free",
            "qwen/qwen3-32b:free",
        ]
        fallbacks = [m for m in fallbacks if m != primary]

    models_to_try = [primary] + fallbacks
    last_err = None
    used_fallback = False

    for i, model in enumerate(models_to_try):
        try:
            res = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.55,
                max_tokens=2048 if i > 0 else 3072,
                top_p=0.9,
            )
            content = res.choices[0].message.content or ""
            if i > 0:
                used_fallback = True
                st.session_state["_last_fallback"] = model
                note = (
                    "\n\n---\n"
                    "*Smart mode is resting (daily limit). "
                    "Switched to a lighter model so you can keep chatting — "
                    "like slow mode. Full smart mode returns after the limit resets.*"
                )
                return content + note
            return content
        except Exception as e:
            last_err = e
            if _is_rate_limit_error(e):
                # try next fallback
                continue
            # non-rate-limit error: stop
            return f"⚠️ Something went wrong: {e}"

    # All models rate-limited
    return (
        "You've used up today's smart-mode allowance.\n\n"
        "Meridium will keep working once the daily limit resets "
        "(usually within an hour or two), or you can:\n"
        "- Wait a bit, then try again\n"
        "- Switch provider in **Menu** (e.g. OpenRouter free models)\n"
        "- Upgrade Groq at https://console.groq.com/settings/billing\n\n"
        "This is a temporary slowdown — not a ban. Come back soon."
    )

def _spotify_creds():
    cid = st.secrets.get("SPOTIFY_CLIENT_ID", "") or os.getenv("SPOTIFY_CLIENT_ID", "")
    secret = st.secrets.get("SPOTIFY_CLIENT_SECRET", "") or os.getenv("SPOTIFY_CLIENT_SECRET", "")
    redirect = st.secrets.get("SPOTIFY_REDIRECT_URI", "") or os.getenv("SPOTIFY_REDIRECT_URI", "https://meridium-ai.streamlit.app/")
    return cid, secret, redirect

def _spotify_cache_path():
    name = (st.session_state.get("username") or "guest").strip().lower() or "guest"
    key = hashlib.sha256(name.encode()).hexdigest()[:16]
    return f"/tmp/meridium_spotify_{key}.cache"

SPOTIFY_SCOPE = (
    "user-read-currently-playing "
    "user-read-playback-state "
    "user-modify-playback-state "
    "user-read-recently-played"
)

def get_spotify_oauth():
    cid, secret, redirect = _spotify_creds()
    if not cid or not secret:
        return None
    return SpotifyOAuth(
        client_id=cid,
        client_secret=secret,
        redirect_uri=redirect,
        scope=SPOTIFY_SCOPE,
        cache_path=_spotify_cache_path(),
        open_browser=False,
        show_dialog=True,
    )

def get_spotify():
    """Return authenticated Spotify client, or None."""
    auth = get_spotify_oauth()
    if not auth:
        return None
    try:
        token = auth.get_cached_token()
        if not token:
            # Try completing OAuth if redirected back with ?code=
            params = dict(st.query_params) if hasattr(st, "query_params") else {}
            code = params.get("code")
            if code:
                if isinstance(code, list):
                    code = code[0]
                token = auth.get_access_token(code, as_dict=True)
                try:
                    st.query_params.clear()
                except Exception:
                    pass
        if not token:
            return None
        return spotipy.Spotify(auth=token["access_token"])
    except Exception:
        return None

def spotify_auth_url():
    auth = get_spotify_oauth()
    if not auth:
        return None
    try:
        return auth.get_authorize_url()
    except Exception:
        return None

def current_track(sp):
    try:
        data = sp.current_playback()
        if not data or not data.get("item"):
            return None
        item = data["item"]
        images = (item.get("album") or {}).get("images") or []
        return {
            "name": item["name"],
            "artists": ", ".join(a["name"] for a in item["artists"]),
            "artist_primary": (item["artists"][0]["name"] if item.get("artists") else ""),
            "album": (item.get("album") or {}).get("name") or "",
            "playing": data["is_playing"],
            "device": (data.get("device") or {}).get("name", ""),
            "art": images[0]["url"] if images else None,
            "uri": item.get("uri"),
            "progress_ms": int(data.get("progress_ms") or 0),
            "duration_ms": int(item.get("duration_ms") or 0),
        }
    except Exception:
        return None


def fetch_synced_lyrics(track_name: str, artist: str, album: str = "", duration_ms: int = 0):
    """Fetch synced / plain lyrics from LRCLIB (free, no key)."""
    import urllib.parse
    import urllib.request
    import json as _json

    def _get(url: str):
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "MeridiumAI/1.0 (lyrics)"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            return _json.loads(resp.read().decode("utf-8", "replace"))

    try:
        if track_name and artist:
            q = {
                "track_name": track_name,
                "artist_name": artist,
            }
            if album:
                q["album_name"] = album
            if duration_ms and duration_ms > 0:
                q["duration"] = int(round(duration_ms / 1000))
            url = "https://lrclib.net/api/get?" + urllib.parse.urlencode(q)
            try:
                data = _get(url)
                if isinstance(data, dict) and (data.get("syncedLyrics") or data.get("plainLyrics")):
                    return {
                        "synced": data.get("syncedLyrics") or "",
                        "plain": data.get("plainLyrics") or "",
                        "source": "lrclib",
                    }
            except Exception:
                pass
            search_url = "https://lrclib.net/api/search?" + urllib.parse.urlencode(
                {"q": f"{artist} {track_name}"}
            )
            results = _get(search_url)
            if isinstance(results, list) and results:
                def _score(item):
                    tn = (item.get("trackName") or "").lower()
                    an = (item.get("artistName") or "").lower()
                    s = 0
                    if track_name.lower() in tn or tn in track_name.lower():
                        s += 3
                    if artist.lower() in an or an in artist.lower():
                        s += 3
                    if item.get("syncedLyrics"):
                        s += 5
                    if item.get("plainLyrics"):
                        s += 1
                    return s
                results = sorted(results, key=_score, reverse=True)
                best = results[0]
                if best.get("syncedLyrics") or best.get("plainLyrics"):
                    return {
                        "synced": best.get("syncedLyrics") or "",
                        "plain": best.get("plainLyrics") or "",
                        "source": "lrclib-search",
                    }
                rid = best.get("id")
                if rid:
                    detail = _get(f"https://lrclib.net/api/get/{rid}")
                    if isinstance(detail, dict):
                        return {
                            "synced": detail.get("syncedLyrics") or "",
                            "plain": detail.get("plainLyrics") or "",
                            "source": "lrclib-id",
                        }
    except Exception:
        pass
    return None



def parse_lrc(lrc_text: str):
    """Parse LRC into list of (ms, line)."""
    lines = []
    if not lrc_text:
        return lines
    for raw in lrc_text.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        # [mm:ss.xx] or [mm:ss]
        m = re.match(r"\[(\d{1,2}):(\d{2})(?:\.(\d{1,3}))?\](.*)$", raw)
        if not m:
            continue
        mm, ss, frac, text = m.group(1), m.group(2), m.group(3) or "0", m.group(4).strip()
        if not text:
            continue
        frac = (frac + "000")[:3]
        ms = int(mm) * 60000 + int(ss) * 1000 + int(frac)
        lines.append((ms, text))
    lines.sort(key=lambda x: x[0])
    return lines


def estimate_lyrics_ai(track_name: str, artist: str) -> str:
    """Rough unofficial lyric sketch via LLM — clearly labelled as estimated."""
    try:
        client, err = make_client(
            st.session_state.get("provider") or "groq",
            st.session_state.get("api_key_val") or None,
        )
        if not client:
            return ""
        model = "llama-3.1-8b-instant"
        try:
            if st.session_state.get("provider") == "groq" and isinstance(GROQ_MODELS, dict):
                mn = st.session_state.get("model_name")
                if mn in GROQ_MODELS:
                    model = GROQ_MODELS[mn]
                elif mn in GROQ_MODELS.values():
                    model = mn
        except Exception:
            pass
        prompt = (
            f"Write short unofficial estimated lyrics for the song '{track_name}' by {artist}. "
            "If you are unsure, write a brief atmospheric verse inspired by the title only. "
            "Do not claim they are official. Keep under 120 words. Plain text lines only."
        )
        res = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400,
        )
        return (res.choices[0].message.content or "").strip()
    except Exception:
        return ""

def render_spotify_panel(key_prefix="sp"):
    """Show connect / now playing / controls / lyrics. Returns True if connected.

    Compact mode (home only): stacked cover → controls → lyrics.
    Full mode (chat + music): art/controls LEFT · lyrics RIGHT.
    """
    # Home only stays stacked (half-width column). Chat uses the split layout.
    compact = key_prefix == "home" or (
        key_prefix not in ("chat", "musicpage")
        and not str(key_prefix).startswith("music")
        and st.session_state.get("view") == "home"
    )

    cid, secret, _ = _spotify_creds()
    if not cid or not secret:
        st.warning("Spotify keys missing. In Streamlit → Settings → Secrets add SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET.")
        return False
    sp = get_spotify()
    if not sp:
        url = spotify_auth_url()
        st.info("**Step 1:** Connect your Spotify account (one-time).")
        if url:
            st.link_button("🔗 Connect Spotify", url, use_container_width=True)
        st.caption("After Approve, you'll return here.")
        st.caption("**Step 2:** Open Spotify and play any song, then press Refresh.")
        return False
    track = current_track(sp)
    if not track:
        st.success("Spotify connected.")
        st.warning("No active playback detected. Open the Spotify app → play a track → Refresh. Premium is usually required for remote control.")
        if st.button("↻ Refresh now playing", key=f"{key_prefix}_ref0", use_container_width=True):
            st.rerun()
        return True

    import html as _html
    art = track.get("art") or ""
    _aname = _html.escape(str(track.get("name") or "Unknown"))
    _aarts = _html.escape(str(track.get("artists") or ""))
    _adev = _html.escape(str(track.get("device") or ""))
    # Do not HTML-escape the URL for src= — only quote-safe characters matter
    _art_src = (art or "").replace('"', "%22")
    _track_uid = _html.escape(str(track.get("uri") or track.get("name") or "x"))
    _prev_art = str(st.session_state.get("_prev_cover_url") or "")
    _prev_esc = (_prev_art or "").replace('"', "%22")
    # Remember current cover for the next track's crossfade (after reading prev)
    if art and art != _prev_art:
        # only update after we've used the previous value for this render
        st.session_state._pending_prev_cover = art
    elif art and not st.session_state.get("_prev_cover_url"):
        st.session_state._pending_prev_cover = art

    cover_px = 140 if compact else 200
    html_h = 210 if compact else 280
    status_label = "Now playing" if track.get("playing") else "Paused"

    def _render_cover_block():
        prev_img = (
            f'<img class="prev" src="{_prev_esc}" alt="" />'
            if _prev_art and _prev_art != art
            else ""
        )
        curr_img = f'<img class="curr" src="{_art_src}" alt="" />' if art else ""
        st.components.v1.html(
            f"""
            <style>
              html, body {{
                margin: 0; padding: 0; overflow: hidden;
                background: transparent !important;
                font-family: Inter, system-ui, sans-serif;
                color: #e8e6f0;
              }}
              @keyframes merArtIn {{
                from {{ opacity: 0; transform: scale(0.88) translateY(14px); filter: blur(8px); }}
                to {{ opacity: 1; transform: scale(1) translateY(0); filter: blur(0); }}
              }}
              @keyframes merArtOut {{
                from {{ opacity: 1; transform: scale(1); filter: blur(0); }}
                to {{ opacity: 0; transform: scale(1.06); filter: blur(6px); }}
              }}
              @keyframes merTextIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
              }}
              .mer-track-block {{ text-align: center; padding: 4px 0 4px; }}
              .cover-stage {{
                position: relative;
                width: {cover_px}px; height: {cover_px}px;
                margin: 0 auto 10px;
                background: rgba(255,255,255,0.04);
                border-radius: 14px;
                overflow: hidden;
              }}
              .cover-stage img {{
                position: absolute; inset: 0;
                width: {cover_px}px; height: {cover_px}px;
                object-fit: cover;
                border-radius: 14px;
                box-shadow: 0 12px 32px rgba(0,0,0,0.4);
                display: block;
              }}
              .cover-stage img.prev {{
                animation: merArtOut 0.45s ease forwards;
                z-index: 1;
              }}
              .cover-stage img.curr {{
                animation: merArtIn 0.7s cubic-bezier(0.22, 1, 0.36, 1) both;
                z-index: 2;
              }}
              .mer-t-name {{
                font-size: {('1rem' if compact else '1.2rem')};
                font-weight: 650; letter-spacing: -0.02em;
                margin-top: 0.25rem;
                animation: merTextIn 0.55s cubic-bezier(0.22, 1, 0.36, 1) 0.1s both;
                white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
                max-width: 100%;
                padding: 0 6px;
              }}
              .mer-t-arts {{
                opacity: 0.7; font-size: {('0.8rem' if compact else '0.88rem')};
                margin-top: 0.15rem;
                animation: merTextIn 0.55s cubic-bezier(0.22, 1, 0.36, 1) 0.16s both;
                white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
                max-width: 100%;
                padding: 0 6px;
              }}
              .mer-t-status {{
                font-size: 0.65rem; letter-spacing: 0.14em; text-transform: uppercase;
                opacity: 0.55; margin-bottom: 6px;
              }}
            </style>
            <div class="mer-track-block" data-track="{_track_uid}">
              <div class="mer-t-status">{status_label}</div>
              <div class="cover-stage">
                {prev_img}
                {curr_img}
              </div>
              <div class="mer-t-name">{_aname}</div>
              <div class="mer-t-arts">{_aarts}{(' · ' + _adev) if _adev else ''}</div>
            </div>
            """,
            height=html_h,
            scrolling=False,
        )
        # Commit pending prev cover after paint so next track can crossfade
        pending = st.session_state.pop("_pending_prev_cover", None)
        if pending:
            st.session_state._prev_cover_url = pending

    def _render_controls():
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            if st.button("⏮", key=f"{key_prefix}_prev", use_container_width=True):
                try:
                    sp.previous_track(); time.sleep(0.25); st.rerun()
                except Exception as e:
                    st.caption(str(e))
        with p2:
            icon = "⏸" if track["playing"] else "▶"
            if st.button(icon, key=f"{key_prefix}_play", use_container_width=True):
                try:
                    if track["playing"]:
                        sp.pause_playback()
                    else:
                        sp.start_playback()
                    time.sleep(0.25); st.rerun()
                except Exception as e:
                    st.caption(f"Needs Premium + active device: {e}")
        with p3:
            if st.button("⏭", key=f"{key_prefix}_next", use_container_width=True):
                try:
                    sp.next_track(); time.sleep(0.25); st.rerun()
                except Exception as e:
                    st.caption(str(e))
        with p4:
            if st.button("↻", key=f"{key_prefix}_ref", use_container_width=True):
                st.session_state._lyrics_key = None
                st.rerun()

    def _render_lyrics(lrc_height: int = 340, component_height: int = 380):
        """Synced / plain lyrics + fullscreen + AI estimate. Shared by compact & full."""
        st.markdown("#### Lyrics")
        try:
            cache_key = f"lyrics::{track.get('uri') or track['name']}"
            if st.session_state.get("_lyrics_key") != cache_key:
                st.session_state._lyrics_key = cache_key
                st.session_state._lyrics_data = fetch_synced_lyrics(
                    track["name"],
                    track.get("artist_primary") or (track.get("artists") or "").split(",")[0].strip(),
                    track.get("album") or "",
                    track.get("duration_ms") or 0,
                )
                st.session_state._lyrics_ai = None

            lyric_data = st.session_state.get("_lyrics_data")
            progress = int(track.get("progress_ms") or 0)
            playing = bool(track.get("playing"))

            if lyric_data and (lyric_data.get("synced") or lyric_data.get("plain")):
                if lyric_data.get("synced"):
                    parsed = parse_lrc(lyric_data["synced"])
                    if parsed:
                        import json as _json
                        lines_payload = [
                            {"ms": int(ms), "text": _html.escape(str(text))}
                            for ms, text in parsed
                        ]
                        payload = _json.dumps(lines_payload)
                        prog_js = max(0, int(progress) + 150)
                        play_js = "true" if playing else "false"
                        st.components.v1.html(
                            f"""
                            <style>
                              html, body {{
                                margin: 0 !important;
                                padding: 0 !important;
                                overflow: hidden !important;
                                background: transparent !important;
                                scrollbar-width: none !important;
                                -ms-overflow-style: none !important;
                              }}
                              html::-webkit-scrollbar,
                              body::-webkit-scrollbar {{
                                width: 0 !important;
                                height: 0 !important;
                                display: none !important;
                              }}
                              @keyframes merLrcIn {{
                                from {{ opacity: 0; filter: blur(5px); transform: translateY(10px); }}
                                to {{ opacity: 1; filter: blur(0); transform: translateY(0); }}
                              }}
                              #mer-lrc-wrap {{
                                scrollbar-width: none !important;
                                -ms-overflow-style: none !important;
                                animation: merLrcIn 0.65s cubic-bezier(0.22, 1, 0.36, 1) both;
                              }}
                              #mer-lrc-wrap::-webkit-scrollbar {{
                                width: 0 !important;
                                height: 0 !important;
                                display: none !important;
                                background: transparent !important;
                              }}
                              #mer-lrc-wrap::-webkit-scrollbar-thumb,
                              #mer-lrc-wrap::-webkit-scrollbar-track {{
                                background: transparent !important;
                                border: none !important;
                              }}
                            </style>
                            <div id="mer-lrc-wrap" style="
                              font-family: Inter, system-ui, sans-serif;
                              color: #e8e6f0;
                              height: {lrc_height}px;
                              overflow-y: auto;
                              overflow-x: hidden;
                              padding: 10px 6px;
                              border-radius: 14px;
                              background: rgba(255,255,255,0.04);
                              border: 1px solid rgba(255,255,255,0.1);
                              scroll-behavior: smooth;
                              scrollbar-width: none;
                              -ms-overflow-style: none;
                            ">
                              <div id="mer-lrc"></div>
                            </div>
                            <div id="mer-lrc-status" style="
                              margin-top:8px;font-size:11px;opacity:0.55;text-align:center;
                            ">Synced lyrics</div>
                            <script>
                            (function(){{
                              const lines = {payload};
                              let baseProgress = {prog_js};
                              const baseWall = Date.now();
                              let isPlaying = {play_js};
                              const root = document.getElementById('mer-lrc');
                              const wrap = document.getElementById('mer-lrc-wrap');
                              const status = document.getElementById('mer-lrc-status');
                              if (!root || !lines.length) return;

                              root.innerHTML = lines.map((L, i) =>
                                '<div class="ml" data-i="'+i+'" style="'
                                + 'padding:7px 10px;margin:2px 0;border-radius:10px;'
                                + 'transition:all 0.18s ease;opacity:0.32;font-size:14.5px;line-height:1.4;'
                                + 'transform:scale(0.98);">'
                                + L.text + '</div>'
                              ).join('');

                              let lastActive = -1;
                              function currentMs(){{
                                if (!isPlaying) return baseProgress;
                                return baseProgress + (Date.now() - baseWall);
                              }}
                              function tick(){{
                                const now = currentMs();
                                let active = 0;
                                for (let i = 0; i < lines.length; i++){{
                                  if (lines[i].ms <= now) active = i;
                                  else break;
                                }}
                                if (active !== lastActive){{
                                  lastActive = active;
                                  const nodes = root.querySelectorAll('.ml');
                                  nodes.forEach((n, i) => {{
                                    if (i === active){{
                                      n.style.opacity = '1';
                                      n.style.fontWeight = '650';
                                      n.style.transform = 'scale(1.02)';
                                      n.style.background = 'rgba(196,167,231,0.18)';
                                      n.style.boxShadow = '0 0 16px rgba(196,167,231,0.12)';
                                    }} else if (Math.abs(i - active) <= 1){{
                                      n.style.opacity = '0.55';
                                      n.style.fontWeight = '500';
                                      n.style.transform = 'scale(1)';
                                      n.style.background = 'transparent';
                                      n.style.boxShadow = 'none';
                                    }} else {{
                                      n.style.opacity = '0.28';
                                      n.style.fontWeight = '400';
                                      n.style.transform = 'scale(0.98)';
                                      n.style.background = 'transparent';
                                      n.style.boxShadow = 'none';
                                    }}
                                  }});
                                  const el = root.querySelector('.ml[data-i="'+active+'"]');
                                  if (el && wrap){{
                                    const top = el.offsetTop - wrap.clientHeight/2 + el.clientHeight/2;
                                    wrap.scrollTo({{ top: Math.max(0, top), behavior: 'smooth' }});
                                  }}
                                }}
                                if (status){{
                                  const sec = Math.floor(now/1000);
                                  const m = Math.floor(sec/60), s = sec%60;
                                  status.textContent = (isPlaying ? '● Live  ' : '❚❚  ')
                                    + m + ':' + String(s).padStart(2,'0');
                                }}
                              }}
                              tick();
                              setInterval(tick, 120);
                            }})();
                            </script>
                            """,
                            height=component_height,
                            scrolling=False,
                        )
                    else:
                        st.text(lyric_data.get("plain") or lyric_data.get("synced"))
                else:
                    st.text(lyric_data.get("plain") or "")
                    st.caption("Plain lyrics (not timed)")

            if lyric_data and (lyric_data.get("synced") or lyric_data.get("plain")):
                if st.button("⛶ Fullscreen lyrics", key=f"{key_prefix}_lyrics_fs", use_container_width=True):
                    st.session_state._lyrics_fs_track = {
                        "name": track.get("name") or "Unknown",
                        "artists": track.get("artists") or "",
                        "art": track.get("art"),
                        "uri": track.get("uri"),
                        "progress_ms": int(track.get("progress_ms") or 0),
                        "duration_ms": int(track.get("duration_ms") or 0),
                        "playing": bool(track.get("playing")),
                    }
                    st.session_state._lyrics_fs_data = lyric_data
                    st.session_state._lyrics_fs_return = st.session_state.get("view") or "music"
                    st.session_state.view = "lyrics_full"
                    st.rerun()
            else:
                st.caption("No synced lyrics found.")
                if st.button("Estimate lyrics with AI", key=f"{key_prefix}_ai_lyrics"):
                    with st.spinner("Listening with Meridium…"):
                        est = estimate_lyrics_ai(
                            track["name"],
                            track.get("artist_primary") or track.get("artists") or "",
                        )
                        st.session_state._lyrics_ai = est or "Could not estimate lyrics right now."
                if st.session_state.get("_lyrics_ai"):
                    st.info("Unofficial AI estimate — not official lyrics.")
                    st.text(st.session_state._lyrics_ai)
        except Exception:
            st.caption("Lyrics unavailable right now.")

    if compact:
        # Home / chat: stack cover → controls → lyrics (no side-by-side crush)
        _render_cover_block()
        _render_controls()
        _render_lyrics(lrc_height=260, component_height=300)
    else:
        # Music page: banner + art LEFT · lyrics RIGHT
        _tname = _aname
        _tarts = _aarts
        _status = status_label
        st.markdown(
            f"""
            <style>
              @keyframes npIn {{
                from {{ opacity: 0; transform: translateY(12px) scale(0.98); filter: blur(4px); }}
                to {{ opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }}
              }}
              @keyframes npPulse {{
                0%,100% {{ opacity: 0.92; }}
                50% {{ opacity: 1; }}
              }}
              .np-banner {{
                text-align: center;
                padding: 0.7rem 1rem;
                margin-bottom: 0.75rem;
                border-radius: 14px;
                border: 1px solid rgba(255,255,255,0.12);
                background: rgba(255,255,255,0.04);
                animation: npIn 0.55s cubic-bezier(0.22, 1, 0.36, 1) both,
                           npPulse 2.8s ease-in-out 0.55s infinite;
              }}
              .np-label {{
                font-size: 0.68rem; letter-spacing: 0.16em; text-transform: uppercase;
                opacity: 0.7; margin-bottom: 0.2rem;
              }}
              .np-title {{
                font-size: 1.1rem; font-weight: 650; letter-spacing: -0.02em;
              }}
            </style>
            <div class="np-banner">
              <div class="np-label">{_status}</div>
              <div class="np-title">Now playing: {_tname}</div>
              <div style="opacity:0.7;font-size:0.85rem;margin-top:0.2rem;">{_tarts}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        left, right = st.columns([1.05, 1.35], gap="medium")
        with left:
            _render_cover_block()
            _render_controls()
        with right:
            _render_lyrics(lrc_height=340, component_height=380)

    if track.get("playing"):
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=3500, key=f"{key_prefix}_lyric_sync")
        except Exception:
            st.caption("Tip: press ↻ every so often if lyrics drift")

    return True


def create_new_chat():
    new_id = str(uuid.uuid4())[:8]
    st.session_state.chats[new_id] = {
        "title": "New conversation",
        "messages": [],
        "created": datetime.now().isoformat(),
    }
    st.session_state.current_chat_id = new_id
    save_user_data()

def delete_chat(chat_id: str):
    if chat_id in st.session_state.chats:
        try:
            on_delete_chat(st.session_state.chats[chat_id])
        except Exception:
            pass
        del st.session_state.chats[chat_id]
    if not st.session_state.chats:
        create_new_chat()
    elif st.session_state.current_chat_id == chat_id:
        st.session_state.current_chat_id = next(iter(st.session_state.chats))
    save_user_data()

def update_chat_title(chat_id, first_message):
    title = first_message.strip()
    st.session_state.chats[chat_id]["title"] = title[:40] + ("…" if len(title) > 40 else "")
    save_user_data()


# ============================================================
# QUOTE OF THE HOUR (changes every hour, UK time)
# ============================================================
QUOTES = [
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("In the middle of difficulty lies opportunity.", "Albert Einstein"),
    ("It always seems impossible until it's done.", "Nelson Mandela"),
    ("Simplicity is the ultimate sophistication.", "Leonardo da Vinci"),
    ("Stay hungry, stay foolish.", "Stewart Brand"),
    ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
    ("Do not go where the path may lead, go instead where there is no path and leave a trail.", "Ralph Waldo Emerson"),
    ("What we know is a drop, what we don't know is an ocean.", "Isaac Newton"),
    ("Be yourself; everyone else is already taken.", "Oscar Wilde"),
    ("The best way to predict the future is to invent it.", "Alan Kay"),
    ("Intelligence is the ability to adapt to change.", "Stephen Hawking"),
    ("Life is what happens when you're busy making other plans.", "John Lennon"),
    ("Not all those who wander are lost.", "J.R.R. Tolkien"),
    ("Everything you can imagine is real.", "Pablo Picasso"),
    ("Whether you think you can or you think you can't, you're right.", "Henry Ford"),
    ("The quieter you become, the more you can hear.", "Ram Dass"),
    ("An investment in knowledge pays the best interest.", "Benjamin Franklin"),
    ("Courage is not the absence of fear, but the triumph over it.", "Nelson Mandela"),
    ("We are what we repeatedly do. Excellence, then, is not an act, but a habit.", "Aristotle"),
    ("The only true wisdom is in knowing you know nothing.", "Socrates"),
    ("Act as if what you do makes a difference. It does.", "William James"),
    ("Dream big. Start small. Act now.", "Robin Sharma"),
    ("Focus on being productive instead of busy.", "Tim Ferriss"),
    ("The secret of getting ahead is getting started.", "Mark Twain"),
    ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
    ("Great things are done by a series of small things brought together.", "Vincent van Gogh"),
    ("If you want to go fast, go alone. If you want to go far, go together.", "African proverb"),
    ("Curiosity is the wick in the candle of learning.", "William Arthur Ward"),
    ("The mind is everything. What you think you become.", "Buddha"),
    ("Make each day your masterpiece.", "John Wooden"),
    ("Turn your wounds into wisdom.", "Oprah Winfrey"),
]



def greet_line(name: str) -> str:
    if is_owner(name):
        return f"Welcome home, <span>{name}</span>"
    return f"Hello, <span>{name}</span>"

def owner_subline(name: str) -> str:
    if is_owner(name):
        return "Recognised as owner · Meridium is yours"
    return "Meridium · personal intelligence · Caelestia shell"


def try_music_command(prompt: str):
    """
    If the user message is a music command, run it via Spotify.
    Returns (handled: bool, reply: str).
    """
    text = (prompt or "").strip()
    low = text.lower().strip()
    # Natural-language triggers for playback control
    triggers = (
        "play ", "play the song", "play song", "pause", "stop music", "stop the music",
        "next", "skip", "previous", "prev", "go back", "last song", "last track",
        "what song", "what's playing", "whats playing", "now playing", "resume",
        "change the song", "change song", "another song", "next one", "previous one",
        "go to the next", "go to previous", "rewind", "forward",
        "this song", "current song", "current track", "who is this", "who's this",
        "what is this", "what's this", "identify", "pause the", "stop the",
        "skip this", "skip the", "play something", "put on ",
    )
    if not any(t in low for t in triggers) and not low.startswith("play"):
        return False, ""

    sp = get_spotify()
    if not sp:
        url = spotify_auth_url()
        msg = "Music isn't connected yet. Open **♫ Music**, connect Spotify, then try again."
        if url:
            msg += "\n\nOr use the Connect Spotify button on the Music page."
        return True, msg

    try:
        # now playing / identify
        now_playing_phrases = (
            "what song", "what's playing", "whats playing", "now playing",
            "this song", "current song", "current track", "what is this song",
            "what's this song", "whats this song", "what track", "who's this",
            "who is this", "who is singing", "who's singing", "identify",
            "what is playing", "what's on", "name this song", "name the song",
        )
        if any(x in low for x in now_playing_phrases) or low in (
            "what song is this", "what is this", "what's this", "song?",
        ):
            track = current_track(sp)
            if not track:
                return True, "Nothing is playing right now. Start a song in Spotify, then ask again."
            extra = f" · {track['device']}" if track.get("device") else ""
            status = "playing" if track.get("playing") else "paused"
            return True, (
                f"♫ **{track['name']}** — {track['artists']}"
                + (f"\nAlbum: {track['album']}" if track.get("album") else "")
                + f"\n_{status}{extra}_"
            )

        # pause / stop
        if (
            low in ("pause", "stop", "stop music", "stop the music", "pause music", "pause it")
            or low.startswith("pause")
            or "pause the" in low
            or "pause this" in low
            or "stop the music" in low
            or "stop playing" in low
        ):
            # Don't treat "stop" alone inside unrelated sentences — require music context if just "stop"
            if low == "stop" or "pause" in low or "music" in low or "playing" in low or "song" in low or "track" in low:
                sp.pause_playback()
                return True, "Paused."

        # resume
        if low in ("resume", "continue", "unpause", "unpause music", "play again") or (
            "resume" in low and any(w in low for w in ("music", "song", "track", "playback", "it", "please"))
        ) or low in ("keep playing", "continue playing"):
            sp.start_playback()
            return True, "Resumed."

        # next / skip
        next_phrases = (
            "next song", "next track", "next one", "skip", "skip this", "skip song",
            "skip the song", "skip this song", "change the song", "change song",
            "another song", "go to the next", "play the next", "forward",
            "next please", "skip please",
        )
        if low in ("next", "skip") or any(x in low for x in next_phrases) or (
            "next" in low and any(w in low for w in ("song", "track", "one", "please", "music"))
        ) or (
            "skip" in low and any(w in low for w in ("song", "track", "this", "it", "please", "music"))
        ):
            sp.next_track()
            time.sleep(0.45)
            track = current_track(sp)
            if track:
                return True, f"⏭ Skipped. Now playing **{track['name']}** — {track['artists']}"
            return True, "⏭ Skipped to the next track."

        # previous / back
        prev_phrases = (
            "previous", "prev song", "prev track", "previous song", "previous track",
            "last song", "last track", "go back", "previous one", "go to previous",
            "play the previous", "rewind", "go back a song", "back a track",
        )
        if low in ("previous", "prev", "back", "go back") or any(x in low for x in prev_phrases):
            sp.previous_track()
            time.sleep(0.45)
            track = current_track(sp)
            if track:
                return True, f"⏮ Back. Now playing **{track['name']}** — {track['artists']}"
            return True, "⏮ Went to the previous track."

        # play <query>
        play_prefixes = (
            "play the song ", "play song ", "play this ", "put on ", "put on the song ",
            "can you play ", "could you play ", "please play ", "play ",
        )
        matched_prefix = None
        for prefix in play_prefixes:
            if low.startswith(prefix):
                matched_prefix = prefix
                break
        if matched_prefix is not None:
            # Use original text slice with same length as matched prefix
            query = text[len(matched_prefix):].strip()
            query = query.strip().strip('"').strip("'")
            # Drop trailing politeness
            query = re.sub(r"\s+please\.?$", "", query, flags=re.I).strip()
            if not query or query.lower() in ("it", "this", "that", "something"):
                return True, "Tell me what to play — e.g. `play Nemzzz Prince of the Scene`"
            # Sanitize Spotify operators
            q_clean = re.sub(r"\s+-\s+", " ", query)
            q_clean = re.sub(r"[\"():]", " ", q_clean)
            q_clean = re.sub(r"\s+", " ", q_clean).strip()
            results = sp.search(q=q_clean or query, type="track", limit=1)
            items = (results.get("tracks") or {}).get("items") or []
            if not items:
                return True, f"Couldn't find a track for “{query}”."
            track = items[0]
            uri = track["uri"]
            name = track["name"]
            artists = ", ".join(a["name"] for a in track["artists"])
            try:
                sp.start_playback(uris=[uri])
            except Exception as e:
                return True, (
                    f"Found **{name}** — {artists}, but couldn't start playback.\n"
                    f"Open Spotify on a device and play anything once, then try again.\n"
                    f"({e})"
                )
            return True, f"▶ Playing **{name}** — {artists}"

    except Exception as e:
        err = str(e)
        if "premium" in err.lower():
            return True, "Spotify needs **Premium** for remote play/pause/skip commands."
        if "NO_ACTIVE_DEVICE" in err or "active device" in err.lower():
            return True, "No active Spotify device. Open Spotify on your phone or computer and play a song once, then try the command again."
        return True, f"Music command failed: {e}"

    return False, ""




def quote_of_the_day():
    """Deterministic quote from UK hour — same within the hour, new on the hour."""
    now = datetime.now(ZoneInfo("Europe/London"))
    # Unique bucket per hour since a fixed epoch
    hour_index = int(now.timestamp() // 3600)
    q, a = QUOTES[hour_index % len(QUOTES)]
    return q, a

# ============================================================
# APPLY
# ============================================================

# Apply theme unlocks requested by other modules (note_view Konami, etc.)
_pending = st.session_state.pop("_pending_theme_unlocks", None) or []
for _item in _pending:
    if isinstance(_item, (list, tuple)) and len(_item) >= 1:
        # Never auto-apply from other modules — unlock only
        unlock_theme(_item[0], _item[1] if len(_item) > 1 else "", apply=False)

inject_css(st.session_state.font, st.session_state.get("theme", "Caelestia"), st.session_state.popup)
if st.session_state.get("_theme_unlock_msg"):
    st.success(st.session_state._theme_unlock_msg)
    st.session_state._theme_unlock_msg = ""


# Stop ARG lab music whenever we are not inside the lab
if st.session_state.get("view") != "lab":
    st.components.v1.html(
        """
        <script>
        (function(){
          try {
            var r = window.parent || window;
            // Only stop if lab audio was active (avoid fighting other page audio)
            if (!r.__mer_audio_on && !r.__mer_heartaches && !r.__mer_siren) return;
            r.__mer_audio_on = false;
            if (r.__mer_song_timer) { clearTimeout(r.__mer_song_timer); r.__mer_song_timer = null; }
            function kill(a){
              if (!a) return;
              try { a.pause(); } catch(e){}
              try { a.currentTime = 0; } catch(e){}
              try { a.src = ''; } catch(e){}
              try { a.remove(); } catch(e){}
            }
            kill(r.__mer_heartaches); r.__mer_heartaches = null;
            kill(r.__mer_siren); r.__mer_siren = null;
            var nodes = r.document.querySelectorAll('audio');
            for (var i = 0; i < nodes.length; i++) {
              try {
                var s = (nodes[i].currentSrc || nodes[i].src || '');
                if (nodes[i].getAttribute('data-meridium') === '1' ||
                    /Heartaches|bowlly|2869|mixkit/i.test(s)) {
                  kill(nodes[i]);
                }
              } catch(e){}
            }
          } catch(e){}
        })();
        </script>
        """,
        height=1,
    )
    st.session_state.lab_kill_audio = False

# Stop letter music whenever we are not on the scientist note
if st.session_state.get("view") != "note":
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
            if (r.__mer_note_song || r.__mer_note_audio_on) {
              kill(r.__mer_note_song);
              r.__mer_note_song = null;
              r.__mer_note_audio_on = false;
            }
            var nodes = r.document.querySelectorAll('audio[data-meridium-note="1"]');
            for (var i = 0; i < nodes.length; i++) kill(nodes[i]);
          } catch(e){}
        })();
        </script>
        """,
        height=1,
    )
now = datetime.now(ZoneInfo("Europe/London"))
time_str = now.strftime("%H:%M")
date_str = now.strftime("%a · %b %d")
provider = st.session_state.provider
model_name = st.session_state.model_name
api_key = st.session_state.api_key_val
use_wiki = st.session_state.use_wiki_toggle
use_web = st.session_state.use_web_toggle

# ===== SIGN IN =====
if not st.session_state.get("signed_in") or not st.session_state.get("username"):
    st.markdown("""
    <div class="panel" style="max-width:420px;margin:10vh auto;text-align:center;">
      <div class="panel-label">Meridium</div>
      <div class="hero" style="font-size:1.75rem;">Welcome</div>
      <div class="sub">Sign in with your name to continue</div>
      <div class="ridge"></div>
      <div class="muted" style="margin-top:8px;">Built with Grok · by xAI</div>
      <div class="muted" style="margin-top:6px;">iPhone: Share → Add to Home Screen</div>
    </div>
    """, unsafe_allow_html=True)
    name = st.text_input("Your name", placeholder="e.g. Alex", key="signin_name", label_visibility="collapsed")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Enter Meridium", use_container_width=True, type="primary", key="signin_btn"):
            ok, result = moderate_username(name)
            if not ok:
                st.error(result)
            else:
                # Always clear previous user's progress before loading this account
                reset_user_session(keep_auth=False)
                st.session_state.username = result[:32]
                st.session_state.signed_in = True
                found = load_user_data(st.session_state.username)
                if not found:
                    # Brand-new user — force locked ARG + default shell
                    st.session_state.arg_unlocked = False
                    st.session_state.unlocked_themes = []
                    st.session_state.glitches_found = []
                    st.session_state.voss_file_unlocked = False
                    st.session_state.lab_visits = 0
                    st.session_state.lab_found = []
                    st.session_state.arg_stabilized = False
                    st.session_state.theme = "Caelestia"
                    st.session_state.font = "Inter"
                    st.session_state.view = "home"
                    create_new_chat()
                elif not st.session_state.get("chats"):
                    create_new_chat()
                st.session_state.show_intro = True
                save_user_data()
                st.rerun()
    st.stop()

# Personalized intro (once after sign-in)
if st.session_state.show_intro:
    user = st.session_state.username
    if is_owner(user):
        intro_main = f'Welcome home, <span style="color:#c4a7e7;">{user}</span>'
        intro_sub = "Meridium recognises you as its owner"
    else:
        intro_main = f'Hello, <span style="color:#c4a7e7;">{user}</span>'
        intro_sub = "Personal intelligence"
    st.markdown(f"""
    <div style="position:fixed;inset:0;z-index:99999;display:flex;align-items:center;justify-content:center;
    background:#0c0c10;animation:introFade 2.3s ease forwards;">
      <div style="text-align:center;">
        <div style="font-size:0.72rem;letter-spacing:0.22em;text-transform:uppercase;color:#c4a7e7;margin-bottom:12px;">Meridium</div>
        <div style="font-size:1.9rem;font-weight:600;color:#e8e6f0;">{intro_main}</div>
        <div style="margin-top:10px;font-size:0.9rem;color:#8b8798;">{intro_sub}</div>
      </div>
    </div>
    <style>@keyframes introFade{{0%,65%{{opacity:1}}100%{{opacity:0;pointer-events:none}}}}</style>
    """, unsafe_allow_html=True)
    time.sleep(2.2)
    st.session_state.show_intro = False
    st.rerun()

# ===== DESIGN 4 MENU (Night Bloom) =====
if st.session_state.popup:
    st.markdown(
        """
        <style>
          /* Isolate menu button labels — prevent Lab/Nadir text bleed on hover */
          div[data-testid="stVerticalBlock"] button[kind="secondary"] p,
          div[data-testid="stVerticalBlock"] button p {
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
            max-width: 100% !important;
            mix-blend-mode: normal !important;
          }
          .bloom-shell, .bloom-shell * {
            mix-blend-mode: normal !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f"""
    <div class="bloom-shell bloom-active">
      <div class="bloom-title">{"Welcome home, " + st.session_state.username if is_owner(st.session_state.username) else "Hello, " + st.session_state.username}</div>
      <div class="bloom-sub">{"Owner menu · your Meridium" if is_owner(st.session_state.username) else "Night Bloom · fonts · models · navigation"}</div>
      <div class="bloom-divider"></div>
    </div>
    """, unsafe_allow_html=True)

    fonts = list(FONTS.keys())
    fi = fonts.index(st.session_state.font) if st.session_state.font in fonts else 0
    ft = st.selectbox("Font", fonts, index=fi, key="pop_font")
    if ft != st.session_state.font:
        st.session_state.font = ft
        save_user_data()
        st.rerun()

    themes = available_themes()
    if "theme" not in st.session_state:
        st.session_state.theme = "Caelestia"
    # If current theme is secret but missing from list, re-add to unlocked
    if st.session_state.theme not in themes:
        if st.session_state.theme in SECRET_THEMES:
            u = list(st.session_state.get("unlocked_themes") or [])
            if st.session_state.theme not in u:
                u.append(st.session_state.theme)
                st.session_state.unlocked_themes = u
            themes = available_themes()
        else:
            st.session_state.theme = "Caelestia"
    ti = themes.index(st.session_state.theme) if st.session_state.theme in themes else 0
    th = st.selectbox("Colour palette", themes, index=ti, key="pop_theme")
    if th != st.session_state.theme:
        st.session_state.theme = th
        save_user_data()
        st.rerun()
    unlocked_now = list(st.session_state.get("unlocked_themes") or [])
    if unlocked_now:
        st.caption("Unlocked secrets: " + ", ".join(unlocked_now))
    locked_left = [n for n in SECRET_THEMES if n not in unlocked_now]
    if locked_left:
        st.caption(f"🔒 {len(locked_left)} secret theme(s) still locked — explore Meridium")

    w1, w2 = st.columns(2)
    with w1:
        st.session_state.show_widgets = st.checkbox("Time widgets", value=st.session_state.show_widgets, key="pop_time")
        st.session_state.use_wiki_toggle = st.checkbox("Wikipedia", value=st.session_state.use_wiki_toggle, key="pop_wiki")
    with w2:
        st.session_state.show_spotify = st.checkbox("Spotify", value=st.session_state.show_spotify, key="pop_sp")
        st.session_state.use_web_toggle = st.checkbox("Web search", value=st.session_state.use_web_toggle, key="pop_web")

    st.markdown('<div class="bloom-divider"></div>', unsafe_allow_html=True)

    st.session_state.provider = st.selectbox(
        "Provider", ["groq", "grok", "openrouter"],
        index=["groq", "grok", "openrouter"].index(st.session_state.provider)
        if st.session_state.provider in ["groq", "grok", "openrouter"] else 0,
        key="pop_prov",
    )
    if st.session_state.provider == "groq":
        opts = list(GROQ_MODELS.keys())
    elif st.session_state.provider == "grok":
        opts = ["Grok 4.5", "Grok 4.3"]
    else:
        opts = ["meta-llama/llama-3.3-70b-instruct:free", "qwen/qwen3-32b:free"]
    mi = opts.index(st.session_state.model_name) if st.session_state.model_name in opts else 0
    st.session_state.model_name = st.selectbox("Model", opts, index=mi, key="pop_model")
    st.session_state.api_key_val = st.text_input(
        "API Key (optional)", type="password",
        value=st.session_state.api_key_val, key="pop_key",
    )

    st.markdown('<div class="bloom-divider"></div>', unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        if st.button("⌂  Home", use_container_width=True, key="pop_home"):
            st.session_state.view = "home"
            st.session_state.popup = False
            st.rerun()
        if st.button("💬  Chat", use_container_width=True, key="pop_chat"):
            st.session_state.view = "chat"
            st.session_state.popup = False
            st.rerun()
        if st.button("＋  New chat", use_container_width=True, key="pop_new"):
            create_new_chat()
            st.session_state.view = "chat"
            st.session_state.popup = False
            st.rerun()
        if st.button("🎬  Cinema", use_container_width=True, key="pop_cinema"):
            st.session_state.cinema_watching = None
            st.session_state.view = "cinema"
            st.session_state.popup = False
            st.rerun()
        if lab_is_unlocked():
            if st.button("🔬  Lab", use_container_width=True, key="pop_lab"):
                st.session_state.view = "lab"
                st.session_state.popup = False
                st.rerun()
    with r2:
        if st.button("◎  Listen", use_container_width=True, key="pop_listen"):
            st.session_state.view = "listen"
            st.session_state.popup = False
            st.rerun()
        if st.button("♫  Music", use_container_width=True, key="pop_music"):
            st.session_state.view = "music"
            st.session_state.popup = False
            st.rerun()
        if st.button("📚  Library", use_container_width=True, key="pop_library"):
            st.session_state.library_reading = None
            st.session_state.view = "library"
            st.session_state.popup = False
            st.rerun()
        if st.button("✕  Close menu", use_container_width=True, key="pop_close"):
            st.session_state.popup = False
            st.rerun()
        if st.button("↩  Switch user", use_container_width=True, key="pop_signout"):
            reset_user_session(keep_auth=False)
            st.session_state.show_intro = False
            st.session_state.popup = False
            st.rerun()

    
    st.markdown("**Backup**")
    export_payload = {
        "username": st.session_state.get("username"),
        "chats": st.session_state.get("chats", {}),
        "meridium_playlist": st.session_state.get("meridium_playlist") or [],
        "theme": st.session_state.get("theme"),
        "font": st.session_state.get("font"),
        "exported_at": datetime.now(ZoneInfo("Europe/London")).isoformat(),
    }
    st.download_button(
        "⬇ Export chats (JSON)",
        data=json.dumps(export_payload, ensure_ascii=False, indent=2),
        file_name=f"meridium_{st.session_state.get('username','user')}_backup.json",
        mime="application/json",
        use_container_width=True,
        key="export_chats",
    )
    up = st.file_uploader("Import backup JSON", type=["json"], key="import_chats")
    if up is not None:
        try:
            data = json.loads(up.read().decode("utf-8"))
            if isinstance(data.get("chats"), dict) and data["chats"]:
                st.session_state.chats = data["chats"]
                st.session_state.current_chat_id = next(iter(st.session_state.chats))
            if isinstance(data.get("meridium_playlist"), list):
                st.session_state.meridium_playlist = data["meridium_playlist"]
            if data.get("theme") in THEMES or data.get("theme") in SECRET_THEMES:
                st.session_state.theme = data["theme"]
            if data.get("font") in FONTS:
                st.session_state.font = data["font"]
            save_user_data()
            st.success("Backup imported.")
            st.rerun()
        except Exception as e:
            st.error(f"Import failed: {e}")

    st.markdown("**Recent chats**")
    for cid, data in sorted(st.session_state.chats.items(), key=lambda x: x[1].get("created", ""), reverse=True)[:10]:
        c_a, c_b = st.columns([4, 1])
        with c_a:
            if st.button(data.get("title", "Untitled"), key=f"pop_c_{cid}", use_container_width=True):
                st.session_state.current_chat_id = cid
                st.session_state.view = "chat"
                st.session_state.popup = False
                save_user_data()
                st.rerun()
        with c_b:
            if st.button("🗑", key=f"pop_d_{cid}", help="Delete chat"):
                delete_chat(cid)
                st.rerun()
    st.stop()

# Dead link egg
if st.session_state.view == "dead_link":
    st.markdown(
        """
        <style>
          .stApp, [data-testid="stAppViewContainer"], section.main { background:#000 !important; }
        </style>
        <p style="color:#666;font-family:Georgia;text-align:center;margin-top:30vh;line-height:1.8;">
        This control never shipped.<br/>
        You found a gap in the menu where a tool was planned<br/>
        and then redacted.<br/><br/>
        <span style="color:#8b3030;">The shell does not mind being incomplete.</span>
        </p>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Return", key="dead_back"):
        st.session_state.view = "home"
        st.rerun()
    st.stop()




if st.session_state.get("view") != "lab":
    st.session_state._currently_in_lab = False


# Stop Voss theme when not in her cutscene/file
if st.session_state.get("view") != "voss_file":
    st.components.v1.html(
        """
        <script>
        (function(){
          try {
            var roots = [window];
            try { if (window.parent) roots.push(window.parent); } catch(e){}
            function kill(a){
              if (!a) return;
              try { a.pause(); a.src=''; a.remove(); } catch(e){}
            }
            for (var r = 0; r < roots.length; r++) {
              var root = roots[r];
              try {
                kill(root.__mer_voss_song); root.__mer_voss_song = null;
              } catch(e){}
            }
          } catch(e){}
        })();
        </script>
        """,
        height=0,
    )

# ===== DR VOSS FILE — cutscene (all 3 anomalies) =====
if st.session_state.get("view") == "voss_file":
    ensure_voss_theme()
    # stage: 0 black+blood text, 1 file
    if "voss_cutscene_stage" not in st.session_state:
        st.session_state.voss_cutscene_stage = 0

    stage = int(st.session_state.get("voss_cutscene_stage") or 0)

    if stage == 0:
        stop_all_meridium_audio()
        start_voss_file_audio()
        st.markdown(
            """
            <style>
              .stApp, [data-testid="stAppViewContainer"], section.main,
              [data-testid="stAppViewBlockContainer"], .block-container {
                background: #000000 !important;
                max-width: 100% !important;
              }
              [data-testid="stHeader"], #MainMenu, footer,
              [data-testid="stToolbar"], header { display:none !important; }
              .voss-blood {
                min-height: 70vh;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
                padding: 2rem 1.2rem;
              }
              .voss-blood span {
                font-family: "Indie Flower", "Segoe Script", "Bradley Hand", cursive, Georgia, serif;
                font-size: clamp(1.6rem, 5vw, 2.6rem);
                color: #8b0000;
                text-shadow:
                  0 0 4px #5c0000,
                  0 1px 0 #4a0000,
                  0 2px 2px rgba(0,0,0,0.9),
                  1px 0 0 #3a0000,
                  -1px 1px 0 #2a0000;
                letter-spacing: 0.04em;
                line-height: 1.35;
                animation: bloodIn 2.2s ease-out both;
                max-width: 16em;
              }
              @keyframes bloodIn {
                0% { opacity: 0; filter: blur(6px); transform: scale(0.96); }
                35% { opacity: 0; }
                100% { opacity: 1; filter: blur(0); transform: scale(1); }
              }
            </style>
            <link href="https://fonts.googleapis.com/css2?family=Indie+Flower&display=swap" rel="stylesheet">
            <div class="voss-blood"><span>Dr Voss has left something behind</span></div>
            """,
            unsafe_allow_html=True,
        )
        # auto-advance feel: button is the only control, styled minimal
        st.markdown(
            """
            <style>
              div[data-testid="stButton"] button {
                background: transparent !important;
                color: #5a2020 !important;
                border: 1px solid #3a1010 !important;
                border-radius: 999px !important;
              }
            </style>
            """,
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("…", key="voss_continue", use_container_width=True):
                st.session_state.voss_cutscene_stage = 1
                st.rerun()
        st.caption("")
        st.stop()

    # stage 1 — the file
    st.markdown(
        """
        <style>
          .stApp, [data-testid="stAppViewContainer"], section.main {
            background: #000000 !important;
          }
          [data-testid="stHeader"], #MainMenu, footer { display:none !important; }
          .voss-file-wrap {
            animation: fileIn 1.6s ease-out both;
            max-width: 560px;
            margin: 1.5rem auto 1rem;
          }
          @keyframes fileIn {
            0% { opacity: 0; transform: translateY(12px); }
            100% { opacity: 1; transform: translateY(0); }
          }
          .voss-file {
            padding: 1.5rem 1.4rem;
            border: 1px solid #5a2020;
            background: #0a0606;
            color: #e8c8c8;
            font-family: Georgia, serif;
            line-height: 1.65;
            font-size: 0.95rem;
          }
          .voss-head {
            font-family: ui-monospace, monospace;
            font-size: 0.68rem;
            letter-spacing: 0.18em;
            color: #c05050;
            margin-bottom: 0.75rem;
          }
          .voss-title {
            font-size: 1.35rem;
            color: #f0d0d0;
            margin-bottom: 1rem;
          }
        </style>
        <div class="voss-file-wrap">
          <div class="voss-file">
            <div class="voss-head">CLASSIFIED · OBSERVATION DIVISION · PERSONAL FILE</div>
            <div class="voss-title">Dr. E. Voss</div>
            <p><b>Clearance:</b> residual only · recovered in blood and static</p>
            <p>
              If you found the three markers, you already know I am not the kind of doctor
              who washes her hands between subjects. Observation Division taught me to watch.
              Meridium taught me to <i>want</i>.
            </p>
            <p>
              The first natural carrier did not scream when the bloom took. The forced ones did.
              We put the medium under the skin anyway — needle, drip, open tray. The glass fogged
              from the inside with something warmer than condensation. Tissue on the sill was not
              a metaphor. It was a hand that forgot it was attached.
            </p>
            <p>
              Committees ask for soldiers. I gave them red rooms and a spectrum line that only
              appears when someone is dying slowly enough to notice. PIXEL — Jaime — walked away
              from a leak that cooked the volunteers. That made him valuable. It did not make him
              safe. Nothing that survives Meridium is safe. Including me.
            </p>
            <p>
              I left the anomalies because I am still hungry for witnesses. Curiosity is how the
              medium feeds. You opened the log. You pressed the corrupted tiles. You are already
              in the experiment. The file is not a warning. It is an invitation written in the
              same colour as the floor.
            </p>
            <p>
              When the alarm hits three-and-a-hitch, do not stabilise. Stay. Watch what the pane
              does to a face. If you feel warmth on your palms, that is not fear. That is the
              designation learning your name.
            </p>
            <p style="margin-top:1.2rem;color:#c05050;">
              — E.V. · I was never trying to save you
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    b1, b2 = st.columns(2)
    with b1:
        if st.button("Close file", use_container_width=True, key="voss_close"):
            stop_all_meridium_audio()
            st.session_state.voss_cutscene_stage = 0
            st.session_state.view = "home"
            st.rerun()
    with b2:
        if st.button("Replay cutscene", use_container_width=True, key="voss_replay"):
            st.session_state.voss_cutscene_stage = 0
            st.rerun()
    st.stop()


# LAB first — full black, no waybar/nav chrome (gated behind ARG puzzle)
if st.session_state.view == "lab":
    if not lab_is_unlocked():
        # New users / incomplete puzzle cannot open the lab
        st.session_state.view = "home"
        st.warning("The lab is sealed. Finish the observation puzzle in chat to unlock it.")
        st.rerun()

    # Entrance cutscene — isolated continue control
    if not st.session_state.get("_lab_cutscene_done"):
        st.markdown(
            """
            <style>
              .stApp, [data-testid="stAppViewContainer"], section.main {
                background: #000000 !important;
              }
              [data-testid="stHeader"], footer, #MainMenu { display: none !important; }
              .lab-cut-wrap {
                min-height: 58vh;
                display: flex; flex-direction: column;
                align-items: center; justify-content: center;
                text-align: center; padding: 2.5rem 1.25rem 1rem;
              }
              .lab-cut-text {
                font-family: Georgia, "Times New Roman", serif;
                color: #b01010;
                font-size: clamp(1.35rem, 4vw, 2rem);
                letter-spacing: 0.02em;
                line-height: 1.4;
                max-width: 15em;
              }
              .lab-cut-sub {
                margin-top: 1rem;
                font-family: ui-monospace, monospace;
                font-size: 0.7rem;
                letter-spacing: 0.2em;
                color: #5a2828;
              }
              /* Scope button styles to this cutscene only via following sibling block */
              .lab-cut-btn-anchor + div button {
                background-color: #140808 !important;
                background-image: none !important;
                color: #f0c8c8 !important;
                border: 1px solid #6a2828 !important;
                border-radius: 999px !important;
                box-shadow: none !important;
                min-height: 3rem !important;
                font-size: 1rem !important;
                font-weight: 600 !important;
              }
              .lab-cut-btn-anchor + div button p,
              .lab-cut-btn-anchor + div button span {
                color: #f0c8c8 !important;
                font-size: 1rem !important;
                font-weight: 600 !important;
                white-space: nowrap !important;
                overflow: visible !important;
                mix-blend-mode: normal !important;
                opacity: 1 !important;
              }
            </style>
            <div class="lab-cut-wrap">
              <div class="lab-cut-text">You were not meant to see this.</div>
              <div class="lab-cut-sub">OBSERVATION LOG · SEAL BROKEN</div>
            </div>
            <div class="lab-cut-btn-anchor"></div>
            """,
            unsafe_allow_html=True,
        )
        mid = st.container()
        with mid:
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                cont = st.button(
                    "Continue",
                    key="lab_cutscene_continue_v2",
                    use_container_width=True,
                    type="primary",
                )
        if cont:
            st.session_state._lab_cutscene_done = True
            st.rerun()
        st.stop()

    if not st.session_state.get("_currently_in_lab"):
        st.session_state._currently_in_lab = True
        st.session_state.lab_visits = int(st.session_state.get("lab_visits") or 0) + 1
        try:
            save_user_data()
        except Exception:
            pass
    # arg_unlocked already required by lab_is_unlocked — keep it true
    st.session_state.arg_unlocked = True
    try:
        save_user_data()
    except Exception:
        pass
    mark_lab_visit()
    unlock_theme("Containment Red", "you entered the observation log", apply=False)
    # All 6 fragments?
    found = st.session_state.get("lab_found") or set()
    if isinstance(found, (list, set)) and len(set(found)) >= 6:
        unlock_theme("Voss Static", "all fragments recovered", apply=False)

    try:
        render_lab()
    except Exception:
        st.markdown(
            """
            <div style="max-width:520px;margin:1rem auto;padding:1rem;border:1px solid rgba(180,60,60,0.3);
              border-radius:12px;background:rgba(10,6,6,0.85);color:#d8b8b8;font-family:Georgia,serif;">
              Observation lab online. Residual systems standing by.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.stop()

if st.session_state.view == "note":
    render_note()

# ===== DESIGN 1 WAYBAR + NAV (hidden in lab) =====
if st.session_state.view not in ("lab", "note", "voss_file", "lyrics_full", "callaghan_safe", "board", "nadir", "nadir_transition", "nadir_door"):
    st.markdown(f"""
<div class="waybar">
  <div class="waybar-left">
    <div class="logo-btn">◈</div>
    <span class="brand">Meridium</span>
    <span class="chip">{st.session_state.get("theme", "Caelestia")}</span>
    <span class="chip">{st.session_state.font}</span>
  </div>
  <div class="waybar-right">
    <span class="chip">Built with Grok</span>
    <span class="clock">{time_str}</span>
    <span class="muted">{date_str}</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # Slim top nav — full shortcuts live in the home bookmark rail
    if st.session_state.view != "home":
        n1, n2, n3, n4 = st.columns(4)
        with n1:
            if st.button("⌂ Home", use_container_width=True, key="n_home"):
                st.session_state.view = "home"
                st.rerun()
        with n2:
            if st.button("💬 Chat", use_container_width=True, key="n_chat"):
                st.session_state.view = "chat"
                st.rerun()
        with n3:
            if st.button("♫ Music", use_container_width=True, key="n_music"):
                st.session_state.view = "music"
                st.rerun()
        with n4:
            if st.button("☰ Menu", use_container_width=True, key="n_menu"):
                st.session_state.popup = True
                st.rerun()

# ===== FULLSCREEN LYRICS (Spotify-style) =====
if st.session_state.view == "lyrics_full":
    import html as _html
    import json as _json

    sp_fs = get_spotify()
    track_fs = None
    if sp_fs:
        try:
            track_fs = current_track(sp_fs)
        except Exception:
            track_fs = None

    saved = st.session_state.get("_lyrics_fs_track") or {}
    lyric_data = st.session_state.get("_lyrics_fs_data") or {}

    if track_fs:
        t_name = track_fs.get("name") or saved.get("name") or "Unknown"
        t_artists = track_fs.get("artists") or saved.get("artists") or ""
        t_art = track_fs.get("art") or saved.get("art")
        progress = int(track_fs.get("progress_ms") or 0)
        playing = bool(track_fs.get("playing"))
        live_key = f"lyrics::{track_fs.get('uri') or t_name}"
        if st.session_state.get("_lyrics_key") != live_key:
            st.session_state._lyrics_key = live_key
            st.session_state._lyrics_data = fetch_synced_lyrics(
                t_name,
                track_fs.get("artist_primary") or (t_artists or "").split(",")[0].strip(),
                track_fs.get("album") or "",
                track_fs.get("duration_ms") or 0,
            )
            lyric_data = st.session_state.get("_lyrics_data") or lyric_data
            st.session_state._lyrics_fs_data = lyric_data
        else:
            lyric_data = st.session_state.get("_lyrics_data") or lyric_data
        st.session_state._lyrics_fs_track = {
            "name": t_name,
            "artists": t_artists,
            "art": t_art,
            "uri": track_fs.get("uri"),
            "progress_ms": progress,
            "duration_ms": int(track_fs.get("duration_ms") or 0),
            "playing": playing,
        }
    else:
        t_name = saved.get("name") or "Unknown"
        t_artists = saved.get("artists") or ""
        t_art = saved.get("art")
        progress = int(saved.get("progress_ms") or 0)
        playing = bool(saved.get("playing"))

    st.markdown(
        """
        <style>
          .stApp, [data-testid="stAppViewContainer"], section.main,
          [data-testid="stAppViewBlockContainer"], .block-container {
            background: #0a0a0e !important;
            max-width: 100% !important;
            padding-top: 0 !important;
            padding-bottom: 0.5rem !important;
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
          }
          [data-testid="stHeader"], #MainMenu, footer,
          [data-testid="stToolbar"], header { display:none !important; }
          /* Bottom control bar buttons */
          div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button {
            background: rgba(255,255,255,0.08) !important;
            color: #f0eef8 !important;
            border: 1px solid rgba(255,255,255,0.14) !important;
            border-radius: 999px !important;
            min-height: 44px !important;
            font-weight: 600 !important;
          }
          div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button:hover {
            background: rgba(196,167,231,0.18) !important;
            border-color: rgba(196,167,231,0.45) !important;
            color: #c4a7e7 !important;
          }
          iframe { border: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Build lyric lines
    lines_payload = []
    if lyric_data and lyric_data.get("synced"):
        parsed = parse_lrc(lyric_data["synced"])
        lines_payload = [
            {"ms": int(ms), "text": _html.escape(str(text))}
            for ms, text in parsed
        ]
    elif lyric_data and lyric_data.get("plain"):
        for i, line in enumerate((lyric_data.get("plain") or "").splitlines()):
            line = line.strip()
            if line:
                lines_payload.append({"ms": i * 3000, "text": _html.escape(line)})

    payload = _json.dumps(lines_payload)
    prog_js = max(0, int(progress) + 150)
    play_js = "true" if playing else "false"
    name_js = _json.dumps(t_name)
    artists_js = _json.dumps(t_artists)
    art_js = _json.dumps(t_art or "")
    want_browser_fs = "true" if st.session_state.pop("_fs_request_browser", False) else "false"

    # Tall immersive stage — fills the rest of the viewport under the control bar
    st.components.v1.html(
        f"""
        <style>
          html, body {{
            margin: 0; padding: 0; overflow: hidden;
            background: #0a0a0e;
            font-family: Inter, system-ui, sans-serif;
            width: 100%; height: 100%;
          }}
          #fs-root {{
            position: absolute; inset: 0;
            width: 100%; height: 100%;
            background:
              radial-gradient(1000px 560px at 18% -5%, rgba(196,167,231,0.16), transparent 55%),
              radial-gradient(800px 480px at 100% 110%, rgba(96,165,250,0.12), transparent 50%),
              #0a0a0e;
            color: #f0eef8;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
          }}
          #fs-meta {{
            position: absolute;
            left: 24px;
            bottom: 22px;
            display: flex;
            align-items: center;
            gap: 14px;
            z-index: 5;
            max-width: min(440px, 68vw);
          }}
          #fs-meta img {{
            width: 76px; height: 76px;
            border-radius: 12px;
            object-fit: cover;
            box-shadow: 0 10px 32px rgba(0,0,0,0.5);
            background: rgba(255,255,255,0.06);
          }}
          #fs-meta .txt {{ min-width: 0; }}
          #fs-meta .name {{
            font-weight: 650;
            font-size: 1.1rem;
            letter-spacing: -0.02em;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }}
          #fs-meta .artists {{
            opacity: 0.7;
            font-size: 0.9rem;
            margin-top: 3px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }}
          #fs-lrc-wrap {{
            width: min(900px, 94vw);
            height: 100%;
            max-height: 100%;
            overflow-y: auto;
            overflow-x: hidden;
            text-align: center;
            padding: 18vh 16px 22vh;
            box-sizing: border-box;
            scrollbar-width: none;
            -ms-overflow-style: none;
            mask-image: linear-gradient(to bottom, transparent, #000 14%, #000 86%, transparent);
            -webkit-mask-image: linear-gradient(to bottom, transparent, #000 14%, #000 86%, transparent);
          }}
          #fs-lrc-wrap::-webkit-scrollbar {{ display: none; width: 0; height: 0; }}
          .fs-line {{
            padding: 12px 18px;
            margin: 5px 0;
            font-size: clamp(1.35rem, 4vw, 2.35rem);
            line-height: 1.35;
            letter-spacing: -0.02em;
            opacity: 0.26;
            transform: scale(0.96);
            transition: all 0.2s ease;
            border-radius: 16px;
          }}
          .fs-line.active {{
            opacity: 1;
            font-weight: 700;
            transform: scale(1.05);
            color: #fff;
            text-shadow: 0 0 28px rgba(196,167,231,0.4);
          }}
          .fs-line.near {{
            opacity: 0.52;
            transform: scale(0.99);
          }}
          #fs-status {{
            position: absolute;
            right: 24px;
            bottom: 28px;
            font-size: 12px;
            opacity: 0.5;
            letter-spacing: 0.04em;
            z-index: 6;
          }}
          #fs-meta {{
            bottom: 28px;
          }}
          /* Track change / enter animations */
          @keyframes fsFadeUp {{
            from {{ opacity: 0; transform: translateY(18px); }}
            to {{ opacity: 1; transform: translateY(0); }}
          }}
          @keyframes fsArtIn {{
            from {{ opacity: 0; transform: scale(0.88) translateY(10px); }}
            to {{ opacity: 1; transform: scale(1) translateY(0); }}
          }}
          @keyframes fsLyricsIn {{
            from {{ opacity: 0; filter: blur(6px); transform: scale(0.98); }}
            to {{ opacity: 1; filter: blur(0); transform: scale(1); }}
          }}
          #fs-meta {{
            animation: fsFadeUp 0.65s cubic-bezier(0.22, 1, 0.36, 1) both;
          }}
          #fs-meta img {{
            animation: fsArtIn 0.7s cubic-bezier(0.22, 1, 0.36, 1) both;
          }}
          #fs-lrc-wrap {{
            animation: fsLyricsIn 0.75s cubic-bezier(0.22, 1, 0.36, 1) both;
          }}
          #fs-root.track-out #fs-meta,
          #fs-root.track-out #fs-lrc-wrap {{
            opacity: 0;
            transform: translateY(-12px);
            filter: blur(4px);
            transition: opacity 0.35s ease, transform 0.35s ease, filter 0.35s ease;
          }}
          .fs-line {{
            transition: opacity 0.35s ease, transform 0.35s ease, background 0.25s ease, font-weight 0.2s ease;
          }}
        </style>
        <div id="fs-root">
          <div id="fs-lrc-wrap"><div id="fs-lrc"></div></div>
          <div id="fs-meta">
            <img id="fs-art" alt="" style="display:none"/>
            <div class="txt">
              <div class="name" id="fs-name"></div>
              <div class="artists" id="fs-artists"></div>
            </div>
          </div>
          <div id="fs-status"></div>
        </div>
        <script>
        (function(){{
          const lines = {payload};
          let baseProgress = {prog_js};
          const baseWall = Date.now();
          let isPlaying = {play_js};
          const name = {name_js};
          const artists = {artists_js};
          const art = {art_js};
          const wantFs = {want_browser_fs};

          // Optional true browser fullscreen (user-gesture from Streamlit button → rerun)
          if (wantFs) {{
            try {{
              const el = window.parent && window.parent.document
                ? window.parent.document.documentElement
                : document.documentElement;
              if (el && el.requestFullscreen) el.requestFullscreen().catch(function(){{}});
              else if (el && el.webkitRequestFullscreen) el.webkitRequestFullscreen();
            }} catch(e) {{}}
          }}

          const fsRoot = document.getElementById('fs-root');
          const root = document.getElementById('fs-lrc');
          const wrap = document.getElementById('fs-lrc-wrap');
          const status = document.getElementById('fs-status');
          const nameEl = document.getElementById('fs-name');
          const artEl = document.getElementById('fs-art');
          const artstsEl = document.getElementById('fs-artists');
          if (nameEl) nameEl.textContent = name || '';
          if (artstsEl) artstsEl.textContent = artists || '';
          if (artEl && art) {{
            artEl.src = art;
            artEl.style.display = 'block';
          }}

          // Soft crossfade when Streamlit reloads the frame on track change
          try {{
            const prev = sessionStorage.getItem('mer_fs_track') || '';
            const cur = (name || '') + '|' + (artists || '');
            if (prev && prev !== cur && fsRoot) {{
              fsRoot.classList.add('track-out');
              requestAnimationFrame(function(){{
                setTimeout(function(){{ fsRoot.classList.remove('track-out'); }}, 40);
              }});
            }}
            sessionStorage.setItem('mer_fs_track', cur);
          }} catch(e) {{}}

          if (!root) return;
          if (!lines.length) {{
            root.innerHTML = '<div class="fs-line active" style="opacity:0.7">No lyrics for this track</div>';
            return;
          }}
          root.innerHTML = lines.map((L, i) =>
            '<div class="fs-line" data-i="'+i+'">'+ L.text +'</div>'
          ).join('');

          let lastActive = -1;
          function currentMs(){{
            if (!isPlaying) return baseProgress;
            return baseProgress + (Date.now() - baseWall);
          }}
          function tick(){{
            const now = currentMs();
            let active = 0;
            for (let i = 0; i < lines.length; i++){{
              if (lines[i].ms <= now) active = i;
              else break;
            }}
            if (active !== lastActive){{
              lastActive = active;
              const nodes = root.querySelectorAll('.fs-line');
              nodes.forEach((n, i) => {{
                n.classList.remove('active', 'near');
                if (i === active) n.classList.add('active');
                else if (Math.abs(i - active) === 1) n.classList.add('near');
              }});
              const el = root.querySelector('.fs-line[data-i="'+active+'"]');
              if (el && wrap){{
                const top = el.offsetTop - wrap.clientHeight/2 + el.clientHeight/2;
                wrap.scrollTo({{ top: Math.max(0, top), behavior: 'smooth' }});
              }}
            }}
            if (status){{
              const sec = Math.floor(now/1000);
              const m = Math.floor(sec/60), s = sec%60;
              status.textContent = (isPlaying ? '● ' : '❚❚ ') + m + ':' + String(s).padStart(2,'0');
            }}
          }}
          tick();
          setInterval(tick, 120);
        }})();
        </script>
        """,
        height=780,
        scrolling=False,
    )

    # ---- Bottom control bar (prev / play-pause / next / refresh / fullscreen / exit) ----
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        if st.button("⏮", key="fs_prev", use_container_width=True, help="Previous"):
            if sp_fs:
                try:
                    sp_fs.previous_track()
                    time.sleep(0.4)
                    st.session_state._lyrics_key = None
                except Exception as e:
                    st.toast(str(e)[:80])
            st.rerun()
    with c2:
        play_icon = "⏸" if playing else "▶"
        if st.button(play_icon, key="fs_play", use_container_width=True, help="Play / Pause"):
            if sp_fs:
                try:
                    if playing:
                        sp_fs.pause_playback()
                    else:
                        sp_fs.start_playback()
                    time.sleep(0.25)
                except Exception as e:
                    st.toast(str(e)[:80])
            st.rerun()
    with c3:
        if st.button("⏭", key="fs_next", use_container_width=True, help="Next"):
            if sp_fs:
                try:
                    sp_fs.next_track()
                    time.sleep(0.4)
                    st.session_state._lyrics_key = None
                except Exception as e:
                    st.toast(str(e)[:80])
            st.rerun()
    with c4:
        if st.button("↻", key="fs_refresh", use_container_width=True, help="Refresh lyrics"):
            st.session_state._lyrics_key = None
            st.session_state._lyrics_fs_data = None
            st.rerun()
    with c5:
        if st.button("⛶", key="fs_browser", use_container_width=True, help="Browser fullscreen"):
            st.session_state._fs_request_browser = True
            st.rerun()
    with c6:
        if st.button("✕", key="lyrics_fs_exit", use_container_width=True, help="Exit"):
            ret = st.session_state.get("_lyrics_fs_return") or "music"
            st.session_state.view = ret
            st.rerun()

    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=3500, key="lyrics_fs_sync")
    except Exception:
        pass

    st.stop()


# ============================================================
# EQUALIZER — Web Audio API (real filters on browser audio)
# Spotify Connect (phone/desktop app) is outside the browser:
# this EQ shapes audio elements / media on this page.
# ============================================================
EQ_BAND_FREQS = [60, 150, 400, 1000, 2400, 6000, 15000]
EQ_BAND_LABELS = ["60", "150", "400", "1k", "2.4k", "6k", "15k"]
EQ_BUILTIN_PRESETS = {
    "Flat":        [0, 0, 0, 0, 0, 0, 0],
    "Bass boost":  [8, 5, 2, 0, -1, 0, 0],
    "Treble":      [-2, -1, 0, 1, 3, 6, 7],
    "Vocal":       [-3, -2, 1, 5, 4, 1, -1],
    "Electronic":  [5, 3, -1, 0, 2, 4, 5],
    "Rock":        [5, 3, -1, 1, 3, 4, 3],
    "Jazz":        [3, 2, 0, 2, -1, 2, 3],
    "Loudness":    [6, 3, 0, -2, 0, 3, 5],
}


def render_equalizer_panel() -> None:
    """Interactive 7-band EQ with presets. Applies via Web Audio in the browser."""
    if "eq_bands" not in st.session_state or not isinstance(st.session_state.eq_bands, list) or len(st.session_state.eq_bands) != 7:
        st.session_state.eq_bands = [0.0] * 7
    if "eq_custom_presets" not in st.session_state or not isinstance(st.session_state.eq_custom_presets, dict):
        st.session_state.eq_custom_presets = {}
    if "eq_preset" not in st.session_state:
        st.session_state.eq_preset = "Flat"
    if "eq_enabled" not in st.session_state:
        st.session_state.eq_enabled = True

    custom = st.session_state.eq_custom_presets
    all_presets = {**EQ_BUILTIN_PRESETS, **{f"★ {k}": v for k, v in custom.items()}}

    with st.expander("Equalizer", expanded=False):
        st.caption(
            "Meridium’s browser EQ only affects audio **in this tab**. "
            "For Spotify playback on your phone or desktop app, use **Spotify’s own equalizer** (below)."
        )

        # Spotify has no public deep-link straight into EQ — open app + show path
        s1, s2 = st.columns(2)
        with s1:
            st.link_button(
                "Open Spotify app",
                "spotify:",
                use_container_width=True,
                help="Opens the Spotify desktop/mobile app if installed",
            )
        with s2:
            st.link_button(
                "Open Spotify Web",
                "https://open.spotify.com",
                use_container_width=True,
            )

        with st.expander("How to open Spotify’s equalizer", expanded=False):
            st.markdown(
                """
**Desktop (Windows / Mac)**  
Profile picture → **Settings** → **Playback** → **Equalizer** → turn on

**iPhone / iPad**  
Profile → **Settings and privacy** → **Playback** → **Equalizer**

**Android**  
Profile → **Settings** → **Equalizer**  
*(often opens your phone’s system EQ)*

> Spotify does not provide a direct link into the EQ screen — those steps are the official path.
> EQ only applies on the device that is **actually playing** sound (not on a Connect target).
                """
            )

        top = st.columns([2, 1, 1])
        with top[0]:
            names = list(all_presets.keys())
            cur = st.session_state.eq_preset
            if cur not in names:
                cur = "Flat"
            pick = st.selectbox("Preset", names, index=names.index(cur), key="eq_preset_select", label_visibility="collapsed")
            if pick != st.session_state.eq_preset:
                st.session_state.eq_preset = pick
                key = pick[2:] if pick.startswith("★ ") else pick
                bands = custom.get(key) if pick.startswith("★ ") else EQ_BUILTIN_PRESETS.get(pick)
                if bands and len(bands) == 7:
                    st.session_state.eq_bands = [float(x) for x in bands]
                    save_user_data()
                    st.rerun()
        with top[1]:
            en = st.toggle("On", value=bool(st.session_state.eq_enabled), key="eq_on_toggle")
            if en != st.session_state.eq_enabled:
                st.session_state.eq_enabled = en
                save_user_data()
                st.rerun()
        with top[2]:
            if st.button("Reset", key="eq_reset", use_container_width=True):
                st.session_state.eq_bands = [0.0] * 7
                st.session_state.eq_preset = "Flat"
                save_user_data()
                st.rerun()

        cols = st.columns(7)
        new_bands = []
        changed = False
        for i, col in enumerate(cols):
            with col:
                st.markdown(
                    f"<div style='text-align:center;font-size:0.7rem;opacity:0.55;margin-bottom:2px'>{EQ_BAND_LABELS[i]}</div>",
                    unsafe_allow_html=True,
                )
                val = float(st.session_state.eq_bands[i])
                v = st.slider(
                    EQ_BAND_LABELS[i],
                    min_value=-12.0,
                    max_value=12.0,
                    value=val,
                    step=0.5,
                    key=f"eq_band_{i}",
                    label_visibility="collapsed",
                )
                new_bands.append(float(v))
                if abs(v - val) > 0.01:
                    changed = True
        if changed:
            st.session_state.eq_bands = new_bands
            st.session_state.eq_preset = "Custom"
            save_user_data()

        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            pname = st.text_input(
                "Save as",
                placeholder="Preset name",
                key="eq_save_name",
                label_visibility="collapsed",
            )
        with c2:
            if st.button("Save", key="eq_save_btn", use_container_width=True):
                name = (pname or "").strip()[:32]
                if not name:
                    st.warning("Name your preset")
                elif name in EQ_BUILTIN_PRESETS:
                    st.warning("That name is reserved")
                else:
                    custom = dict(st.session_state.eq_custom_presets)
                    custom[name] = list(st.session_state.eq_bands)
                    st.session_state.eq_custom_presets = custom
                    st.session_state.eq_preset = f"★ {name}"
                    save_user_data()
                    st.toast(f"Saved preset")
                    st.rerun()
        with c3:
            if custom and st.button("Delete", key="eq_del_btn", use_container_width=True):
                cur = st.session_state.eq_preset or ""
                key = cur[2:] if cur.startswith("★ ") else cur
                if key in custom:
                    custom = dict(custom)
                    custom.pop(key, None)
                    st.session_state.eq_custom_presets = custom
                    st.session_state.eq_preset = "Flat"
                    st.session_state.eq_bands = [0.0] * 7
                    save_user_data()
                    st.rerun()

        bands_js = ",".join(str(float(x)) for x in st.session_state.eq_bands)
        freqs_js = ",".join(str(f) for f in EQ_BAND_FREQS)
        enabled_js = "true" if st.session_state.eq_enabled else "false"
        st.components.v1.html(
            f"""
<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<style>
  html,body {{ margin:0; background:transparent; font-family: system-ui,sans-serif; color:#c8c4d4; }}
  .wrap {{ padding: 4px 2px 8px; }}
  .bars {{
    display:flex; align-items:flex-end; justify-content:space-between;
    height: 56px; gap: 6px; margin-bottom: 8px;
  }}
  .bar {{
    flex:1; border-radius: 4px 4px 2px 2px;
    background: linear-gradient(180deg, #c4a7e7, #7aa2f7);
    opacity: 0.85; min-height: 4px; transition: height 0.08s linear;
  }}
  .meta {{ font-size: 11px; opacity: 0.55; text-align: center; }}
  button#arm {{
    display:block; width:100%; margin-top: 8px; padding: 8px 10px;
    border-radius: 10px; border: 1px solid rgba(255,255,255,0.12);
    background: rgba(255,255,255,0.06); color: #e8e4f0; cursor: pointer;
    font-size: 12px;
  }}
  button#arm:hover {{ background: rgba(196,167,231,0.18); }}
</style></head>
<body>
<div class="wrap">
  <div class="bars" id="bars"></div>
  <div class="meta" id="status">EQ ready · click Arm to process audio on this page</div>
  <button id="arm" type="button">Arm equalizer (required once)</button>
</div>
<script>
(function() {{
  const freqs = [{freqs_js}];
  let gainsDb = [{bands_js}];
  let enabled = {enabled_js};
  const barsEl = document.getElementById('bars');
  const status = document.getElementById('status');
  const armBtn = document.getElementById('arm');
  freqs.forEach(() => {{
    const d = document.createElement('div');
    d.className = 'bar';
    d.style.height = '8px';
    barsEl.appendChild(d);
  }});
  const barNodes = [...barsEl.children];

  let ctx, filters = [], sourceMap = new WeakMap(), analyser, raf;

  function buildChain() {{
    if (!ctx) return;
    filters = [];
    freqs.forEach((f, i) => {{
      const fil = ctx.createBiquadFilter();
      if (i === 0) {{ fil.type = 'lowshelf'; fil.frequency.value = f; }}
      else if (i === freqs.length - 1) {{ fil.type = 'highshelf'; fil.frequency.value = f; }}
      else {{
        fil.type = 'peaking';
        fil.frequency.value = f;
        fil.Q.value = 1.1;
      }}
      fil.gain.value = enabled ? gainsDb[i] : 0;
      if (i > 0) filters[i-1].connect(fil);
      filters.push(fil);
    }});
    analyser = ctx.createAnalyser();
    analyser.fftSize = 256;
    if (filters.length) {{
      filters[filters.length-1].connect(analyser);
    }}
    analyser.connect(ctx.destination);
  }}

  function applyGains() {{
    filters.forEach((fil, i) => {{
      fil.gain.value = enabled ? gainsDb[i] : 0;
    }});
    barNodes.forEach((el, i) => {{
      const g = enabled ? gainsDb[i] : 0;
      const h = 8 + ((g + 12) / 24) * 44;
      el.style.height = h + 'px';
      el.style.opacity = enabled ? '0.9' : '0.25';
    }});
  }}

  function connectMediaElement(el) {{
    if (!ctx || !filters.length) return;
    if (sourceMap.has(el)) return;
    try {{
      const src = ctx.createMediaElementSource(el);
      src.connect(filters[0]);
      sourceMap.set(el, src);
      el.dataset.merEq = '1';
    }} catch (e) {{}}
  }}

  function scan() {{
    document.querySelectorAll('audio, video').forEach(connectMediaElement);
  }}

  function pulse() {{
    if (!analyser) {{
      applyGains();
      raf = requestAnimationFrame(pulse);
      return;
    }}
    const data = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(data);
    const step = Math.floor(data.length / barNodes.length) || 1;
    barNodes.forEach((el, i) => {{
      let sum = 0;
      for (let k = 0; k < step; k++) sum += data[i * step + k] || 0;
      const avg = sum / step;
      const base = enabled ? ((gainsDb[i] + 12) / 24) * 20 : 0;
      el.style.height = (6 + base + avg / 8) + 'px';
    }});
    raf = requestAnimationFrame(pulse);
  }}

  armBtn.addEventListener('click', async () => {{
    try {{
      ctx = new (window.AudioContext || window.webkitAudioContext)();
      if (ctx.state === 'suspended') await ctx.resume();
      buildChain();
      applyGains();
      scan();
      setInterval(scan, 1500);
      pulse();
      // Audible test: short noise burst through the EQ chain so you can hear it
      try {{
        const dur = 0.55;
        const buffer = ctx.createBuffer(1, ctx.sampleRate * dur, ctx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < data.length; i++) {{
          data[i] = (Math.random() * 2 - 1) * Math.exp(-3 * i / data.length);
        }}
        const noise = ctx.createBufferSource();
        noise.buffer = buffer;
        const vol = ctx.createGain();
        vol.gain.value = 0.22;
        noise.connect(vol);
        vol.connect(filters[0]);
        noise.start();
      }} catch (e) {{}}
      status.textContent = enabled
        ? 'EQ armed · test tone played through filters'
        : 'EQ armed · currently bypassed (Off)';
      armBtn.textContent = 'Equalizer armed';
      armBtn.disabled = true;
    }} catch (e) {{
      status.textContent = 'Could not start audio context: ' + e;
    }}
  }});

  applyGains();
}})();
</script>
</body></html>
            """,
            height=140,
            scrolling=False,
        )


# MUSIC — dedicated player + Meridium playlist
if st.session_state.view == "music":
    st.session_state.show_spotify = True
    st.markdown("""
    <style>
      @keyframes musicFadeUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      .music-hero {
        text-align: center; padding: 6px 0 14px;
        animation: musicFadeUp 0.45s ease both;
      }
      .music-hero h1 {
        font-size: 1.5rem; font-weight: 650; letter-spacing: -0.03em; margin: 0 0 4px;
      }
      .music-hero p { margin: 0; opacity: 0.5; font-size: 0.88rem; }
      .pl-row {
        display: flex; align-items: center; gap: 12px;
        padding: 10px 12px; margin-bottom: 6px;
        border-radius: 12px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
      }
      .pl-row.is-playing {
        background: rgba(80,200,120,0.10);
        border-color: rgba(80,200,120,0.35);
      }
      .pl-num {
        font-size: 0.75rem; opacity: 0.45; min-width: 28px; text-align: right;
        font-variant-numeric: tabular-nums;
      }
      .pl-body { flex: 1; min-width: 0; }
      .pl-title {
        font-size: 0.92rem; font-weight: 560; margin: 0;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
      }
      .pl-sub {
        font-size: 0.78rem; opacity: 0.55; margin: 2px 0 0;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
      }
      .pl-badge {
        font-size: 0.68rem; letter-spacing: 0.06em; text-transform: uppercase;
        color: #5dce8a; font-weight: 650; margin-left: 6px;
      }
      .hit-row {
        padding: 8px 10px; margin-bottom: 4px; border-radius: 10px;
        background: rgba(255,255,255,0.025);
        border: 1px solid rgba(255,255,255,0.06);
      }
    </style>
    <div class="music-hero">
      <h1>Music</h1>
      <p>Player · search · playlist</p>
    </div>
    """, unsafe_allow_html=True)

    render_spotify_panel("musicpage")
    render_equalizer_panel()

    MAX_PLAYLIST = 500
    PAGE_SIZE = 12  # compact pages — less clutter
    sp = get_spotify()
    playlist = list(st.session_state.get("meridium_playlist") or [])

    def _sanitize_spotify_query(q: str) -> str:
        q = (q or "").strip()
        q = re.sub(r"\s+-\s+", " ", q)
        q = re.sub(r"[\"():]", " ", q)
        q = re.sub(r"\s+", " ", q).strip()
        return q

    def _track_from_spotify_item(t: dict) -> dict:
        return {
            "name": t.get("name") or "Unknown",
            "artists": ", ".join(a["name"] for a in (t.get("artists") or [])),
            "uri": t.get("uri"),
            "album": (t.get("album") or {}).get("name") or "",
            "art": ((t.get("album") or {}).get("images") or [{}])[0].get("url"),
            "duration_ms": int(t.get("duration_ms") or 0),
        }

    def _add_hit_to_playlist(hit: dict) -> str:
        pl = list(st.session_state.get("meridium_playlist") or [])
        if len(pl) >= MAX_PLAYLIST:
            return f"Playlist is full ({MAX_PLAYLIST} tracks)."
        existing_uris = {p.get("uri") for p in pl if p.get("uri")}
        if hit.get("uri") and hit["uri"] in existing_uris:
            return "Already in playlist"
        pl.append({
            "title": f"{hit['name']} - {hit['artists']}",
            "name": hit["name"],
            "artists": hit["artists"],
            "uri": hit.get("uri"),
            "album": hit.get("album") or "",
            "art": hit.get("art"),
            "added": datetime.now().isoformat(),
        })
        st.session_state.meridium_playlist = pl
        save_user_data()
        return f"Added: {hit['name']}"

    def _spotify_search_tracks(query: str, limit: int = 8):
        if not sp or not query:
            return []
        clean = _sanitize_spotify_query(query)
        if len(clean) < 2:
            return []
        limit = max(1, min(int(limit), 10))
        try:
            results = sp.search(q=clean, type="track", limit=limit, market="from_token")
            items = (results.get("tracks") or {}).get("items") or []
            return [_track_from_spotify_item(t) for t in items]
        except Exception:
            try:
                results = sp.search(q=clean, type="track", limit=limit)
                items = (results.get("tracks") or {}).get("items") or []
                return [_track_from_spotify_item(t) for t in items]
            except Exception as e2:
                st.session_state._pl_search_error = str(e2)
                return []

    def _is_track_uri(u: str) -> bool:
        u = (u or "").strip()
        return u.startswith("spotify:track:") and len(u) > len("spotify:track:")

    def _resolve_and_persist_uris(items: list, max_resolve: int = 60) -> list:
        """
        Build a list of valid track URIs for `items`.
        Persist any newly found URIs back into meridium_playlist so page 2+ keeps working.
        """
        pl = list(st.session_state.get("meridium_playlist") or [])
        # Map index in full playlist by identity
        dirty = False
        uris = []
        resolved = 0
        for item in items:
            u = (item.get("uri") or "").strip()
            if _is_track_uri(u):
                uris.append(u)
                continue
            if not sp or resolved >= max_resolve:
                continue
            q = _sanitize_spotify_query(
                item.get("title") or f"{item.get('name','')} {item.get('artists','')}"
            )
            if len(q) < 2:
                continue
            try:
                results = sp.search(q=q, type="track", limit=1)
                tracks = (results.get("tracks") or {}).get("items") or []
                if not tracks:
                    continue
                found = tracks[0].get("uri")
                if not _is_track_uri(found):
                    continue
                uris.append(found)
                resolved += 1
                # persist into matching playlist entry
                for p in pl:
                    if p is item or (
                        (p.get("name") or "") == (item.get("name") or "")
                        and (p.get("artists") or "") == (item.get("artists") or "")
                        and not _is_track_uri(p.get("uri") or "")
                    ):
                        p["uri"] = found
                        if not p.get("name"):
                            p["name"] = tracks[0].get("name") or p.get("name")
                        dirty = True
                        break
                item["uri"] = found
            except Exception:
                continue
        if dirty:
            st.session_state.meridium_playlist = pl
            try:
                save_user_data()
            except Exception:
                pass
        return uris

    def _apply_repeat_mode():
        if not sp:
            return
        mode = st.session_state.get("pl_repeat") or "off"
        state = {"off": "off", "all": "context", "one": "track"}.get(mode, "off")
        try:
            sp.repeat(state)
        except Exception:
            pass

    def _play_playlist_from(start_index: int = 0) -> str:
        """
        Play from start_index. Queue the next window of tracks (Spotify accepts a
        finite URI list). Missing URIs are resolved + saved so later pages work.
        """
        if not sp:
            return "Connect Spotify first."
        items = list(st.session_state.get("meridium_playlist") or [])
        if not items:
            return "Playlist is empty."
        start_index = max(0, min(int(start_index), len(items) - 1))

        ordered = items[start_index:]
        if st.session_state.get("pl_repeat") == "all" and start_index > 0:
            ordered = ordered + items[:start_index]

        # Spotify start_playback URI list is more reliable with a moderate window
        WINDOW = 50
        window = ordered[:WINDOW]
        uris = _resolve_and_persist_uris(window, max_resolve=WINDOW)
        # drop any non-track / duplicates while keeping order
        seen = set()
        clean = []
        for u in uris:
            if u and u not in seen and _is_track_uri(u):
                seen.add(u)
                clean.append(u)
        uris = clean
        if not uris:
            return (
                "Couldn't resolve track URIs for this page. "
                "Re-add the song via Search, or check Spotify connection."
            )
        try:
            # Explicit offset 0 on the URI list — critical when starting mid-playlist
            sp.start_playback(uris=uris, offset={"position": 0})
            time.sleep(0.3)
            _apply_repeat_mode()
            first = window[0] if window else {}
            first_name = first.get("name") or first.get("title") or "track"
            extra = f" · {len(uris)} queued from #{start_index + 1}"
            mode = st.session_state.get("pl_repeat") or "off"
            if mode == "all":
                extra += " · repeat all"
            elif mode == "one":
                extra += " · repeat one"
            return f"▶ Playing **{first_name}**{extra}"
        except Exception as e:
            err = str(e)
            low = err.lower()
            if "premium" in low:
                return "Spotify Premium is required for playlist playback control."
            if "no_active_device" in low or "active device" in low:
                return "No active Spotify device. Open Spotify and play something once, then try again."
            # Fallback: play only the first resolved URI
            try:
                sp.start_playback(uris=[uris[0]])
                time.sleep(0.2)
                _apply_repeat_mode()
                return f"▶ Playing single track (queue fallback): {uris[0]}"
            except Exception as e2:
                return f"Playback failed: {e2}"

    tab_search, tab_playlist = st.tabs([
        "Search",
        f"Playlist · {len(playlist)}",
    ])

    # ========== SEARCH ==========
    with tab_search:
        if not sp:
            st.info("Connect Spotify above to search and add tracks.")
        else:
            with st.form("pl_search_form", clear_on_submit=False):
                search_q = st.text_input(
                    "Search",
                    placeholder="Song or artist",
                    key="pl_search",
                    label_visibility="collapsed",
                )
                submitted = st.form_submit_button("Search", use_container_width=True)

            search_q = (search_q or "").strip()
            if search_q and len(search_q) >= 2:
                cache_key = f"pl_search::{_sanitize_spotify_query(search_q).lower()}"
                need_search = submitted or st.session_state.get("_pl_search_key") != cache_key
                if need_search:
                    st.session_state._pl_search_error = None
                    hits = _spotify_search_tracks(search_q, limit=8)
                    st.session_state._pl_search_key = cache_key
                    st.session_state._pl_search_results = hits

                err = st.session_state.get("_pl_search_error")
                if err:
                    st.caption(f"Search error: {err}")

                hits = st.session_state.get("_pl_search_results") or []
                if submitted and hits:
                    msg = _add_hit_to_playlist(hits[0])
                    st.toast(msg)
                    st.rerun()
                elif submitted and not hits:
                    st.warning("No match. Try a simpler name.")

                if hits:
                    for hi, hit in enumerate(hits):
                        c1, c2 = st.columns([5, 1])
                        with c1:
                            st.markdown(
                                f"<div class='hit-row'><div class='pl-title'>{hit['name']}</div>"
                                f"<div class='pl-sub'>{hit['artists']}</div></div>",
                                unsafe_allow_html=True,
                            )
                        with c2:
                            if st.button("＋", key=f"pl_hit_{hi}", help="Add", use_container_width=True):
                                msg = _add_hit_to_playlist(hit)
                                st.toast(msg)
                                st.rerun()
            else:
                st.caption("Search Spotify and add tracks to your Meridium playlist.")

    # ========== PLAYLIST ==========
    with tab_playlist:
        playlist = list(st.session_state.get("meridium_playlist") or [])
        if "pl_repeat" not in st.session_state:
            st.session_state.pl_repeat = "off"

        if not playlist:
            st.info("Playlist is empty — use **Search** to add tracks.")
        else:
            a1, a2, a3, a4 = st.columns(4)
            with a1:
                if sp and st.button("▶ Play", use_container_width=True, key="pl_play_first"):
                    msg = _play_playlist_from(0)
                    (st.success if msg.startswith("▶") else st.warning)(msg)
                    time.sleep(0.15)
                    st.rerun()
            with a2:
                mode = st.session_state.get("pl_repeat") or "off"
                labels = {"off": "Repeat off", "all": "Repeat all", "one": "Repeat one"}
                if st.button(
                    f"🔁 {labels.get(mode, 'Repeat off')}",
                    use_container_width=True,
                    key="pl_repeat_btn",
                    type="primary" if mode != "off" else "secondary",
                ):
                    order = ["off", "all", "one"]
                    st.session_state.pl_repeat = order[(order.index(mode) + 1) % len(order)]
                    _apply_repeat_mode()
                    st.rerun()
            with a3:
                page_now = int(st.session_state.get("pl_page") or 0)
                if sp and st.button("▶ Page", use_container_width=True, key="pl_play_page",
                                    help="Play from the first track on this page"):
                    msg = _play_playlist_from(page_now * PAGE_SIZE)
                    (st.success if msg.startswith("▶") else st.warning)(msg)
                    st.rerun()
            with a4:
                if st.button("Clear", use_container_width=True, key="pl_clear"):
                    st.session_state.meridium_playlist = []
                    st.session_state.pl_page = 0
                    save_user_data()
                    st.rerun()

            total = len(playlist)
            pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
            if "pl_page" not in st.session_state:
                st.session_state.pl_page = 0
            st.session_state.pl_page = max(0, min(int(st.session_state.pl_page), pages - 1))
            page = int(st.session_state.pl_page)
            start = page * PAGE_SIZE
            end = min(start + PAGE_SIZE, total)

            # Pagination — compact
            if pages > 1:
                n1, n2, n3 = st.columns([1, 2, 1])
                with n1:
                    if st.button("←", use_container_width=True, key="pl_prev", disabled=page <= 0):
                        st.session_state.pl_page = page - 1
                        st.rerun()
                with n2:
                    st.markdown(
                        f"<div style='text-align:center;padding-top:6px;opacity:0.65;font-size:0.85rem'>"
                        f"{start+1}–{end} of {total} · page {page+1}/{pages}</div>",
                        unsafe_allow_html=True,
                    )
                with n3:
                    if st.button("→", use_container_width=True, key="pl_next", disabled=page >= pages - 1):
                        st.session_state.pl_page = page + 1
                        st.rerun()

            # Now-playing match
            now = None
            now_uri = now_name = now_artists = ""
            if sp:
                try:
                    now = current_track(sp)
                except Exception:
                    now = None
            if now:
                now_uri = (now.get("uri") or "").strip()
                now_name = (now.get("name") or "").strip().lower()
                now_artists = (now.get("artist_primary") or now.get("artists") or "").strip().lower()
                try:
                    from streamlit_autorefresh import st_autorefresh
                    st_autorefresh(interval=4000, key="pl_now_playing_refresh")
                except Exception:
                    pass

            def _norm(s: str) -> str:
                s = (s or "").lower().strip()
                s = re.sub(r"\s+-\s+", " ", s)
                s = re.sub(r"[^\w\s]", " ", s)
                return re.sub(r"\s+", " ", s).strip()

            def _is_now_playing(item: dict) -> bool:
                if not now:
                    return False
                uri = (item.get("uri") or "").strip()
                if now_uri and uri and uri == now_uri:
                    return True
                item_name = _norm(item.get("name") or "")
                item_title = _norm(item.get("title") or "")
                item_arts = _norm(item.get("artists") or "")
                nn, na = _norm(now_name), _norm(now_artists)
                if not nn:
                    return False
                if item_name and (item_name == nn or nn in item_name or item_name in nn):
                    if not item_arts or not na or na in item_arts or item_arts in na:
                        return True
                if item_title and (item_title == nn or nn in item_title):
                    return True
                return False

            for i in range(start, end):
                item = playlist[i]
                title = item.get("name") or item.get("title") or "Track"
                artists = item.get("artists") or ""
                playing_now = _is_now_playing(item)
                has_uri = _is_track_uri(item.get("uri") or "")
                cls = "pl-row is-playing" if playing_now else "pl-row"
                badge = '<span class="pl-badge">playing</span>' if playing_now else ""
                uri_hint = "" if has_uri else " · needs resolve"
                st.markdown(
                    f"""
                    <div class="{cls}">
                      <div class="pl-num">{i+1}</div>
                      <div class="pl-body">
                        <div class="pl-title">{title}{badge}</div>
                        <div class="pl-sub">{artists}{uri_hint}</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                b1, b2 = st.columns([1, 1])
                with b1:
                    if sp and st.button(
                        "Play",
                        key=f"pl_play_{i}_{page}",
                        use_container_width=True,
                        help="Play from this track",
                    ):
                        msg = _play_playlist_from(i)
                        st.toast(msg.replace("**", ""))
                        st.rerun()
                with b2:
                    if st.button("Remove", key=f"pl_del_{i}_{page}", use_container_width=True):
                        pl = list(playlist)
                        pl.pop(i)
                        st.session_state.meridium_playlist = pl
                        new_pages = max(1, (len(pl) + PAGE_SIZE - 1) // PAGE_SIZE)
                        if st.session_state.pl_page >= new_pages:
                            st.session_state.pl_page = max(0, new_pages - 1)
                        save_user_data()
                        st.rerun()

    st.stop()


# LISTEN — voice assistant (process only on Send)
if st.session_state.view == "listen":
    st.markdown("""
    <div class="panel" style="text-align:center;">
      <div class="panel-label">Voice assistant</div>
      <div class="hero" style="font-size:1.5rem;">I'm listening</div>
      <div class="orb"></div>
      <div class="muted">Record or type · press Send · Meridium replies (optional speak-back)</div>
    </div>
    """, unsafe_allow_html=True)

    if "voice_log" not in st.session_state:
        st.session_state.voice_log = []

    auto_speak = st.checkbox("Speak replies aloud", value=True, key="voice_speak")

    audio = None
    try:
        audio = st.audio_input("Tap the mic and speak", key="voice_mic")
    except Exception:
        st.warning("Mic not available in this browser. Use Chrome/Edge, or type below.")

    typed = st.text_input("Or type instead", placeholder="Ask Meridium…", key="voice_typed")
    go = st.button("Send to Meridium", type="primary", use_container_width=True, key="voice_send")

    user_text = ""
    if go:
        if typed.strip():
            user_text = typed.strip()
        elif audio is not None:
            with st.spinner("Hearing you…"):
                try:
                    raw = audio.getvalue() if hasattr(audio, "getvalue") else audio.read()
                    name = getattr(audio, "name", "audio.wav") or "audio.wav"
                    user_text = transcribe_audio(raw, name)
                except Exception as e:
                    st.error(f"Couldn't transcribe: {e}")
                    user_text = ""
            if user_text:
                st.success(f"You said: {user_text}")
        else:
            st.warning("Record audio or type a message first.")

    if go and user_text:
        handled, music_reply = try_music_command(user_text)
        if handled:
            reply = music_reply
        else:
            user_name = st.session_state.get("username") or "user"
            if is_owner(user_name):
                owner_note = (
                    f"\n\nIMPORTANT: {user_name} is the owner of Meridium. "
                    "Warm, loyal, concise — short sentences for voice."
                )
            else:
                owner_note = f"\n\nUser's name is {user_name}. Keep answers concise for voice."
            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT + owner_note
                    + "\n\nKeep answers under 80 words when possible — voice mode.",
                },
                {"role": "user", "content": user_text},
            ]
            with st.spinner("Thinking…"):
                reply = run_chat(
                    messages,
                    st.session_state.provider,
                    st.session_state.model_name,
                    st.session_state.api_key_val,
                )

        st.markdown("### Meridium")
        st.markdown(reply)
        st.session_state.voice_log.append({"user": user_text, "assistant": reply})

        if st.session_state.current_chat_id in st.session_state.chats:
            ch = st.session_state.chats[st.session_state.current_chat_id]
            ch.setdefault("messages", []).append({"role": "user", "content": user_text})
            ch["messages"].append({"role": "assistant", "content": reply})
            save_user_data()

        if auto_speak and reply:
            spoken = re.sub(r"[\#\`\*_>]+", " ", reply)
            spoken = re.sub(r"\s+", " ", spoken).strip()
            st.components.v1.html(speak_html(spoken, autoplay=True), height=70)

    if st.session_state.voice_log:
        st.markdown("---")
        st.caption("Recent voice turns")
        for turn in reversed(st.session_state.voice_log[-5:]):
            st.markdown(f"**You:** {turn['user']}")
            st.markdown(f"**Meridium:** {turn['assistant']}")

    if st.button("💬 Open text chat", use_container_width=True, key="voice_to_chat"):
        st.session_state.view = "chat"
        st.rerun()
    st.stop()


# ===== LIBRARY HELPERS =====
LIBRARY_CATALOG = [
    {
        "id": "frankenstein",
        "title": "Frankenstein",
        "author": "Mary Shelley",
        "note": "Full text · Project Gutenberg",
        "file": "frankenstein.txt",
        "gutenberg": "https://www.gutenberg.org/ebooks/84",
    },
    {
        "id": "pride",
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "note": "Full text · Project Gutenberg",
        "file": "pride.txt",
        "gutenberg": "https://www.gutenberg.org/ebooks/1342",
    },
    {
        "id": "scandal",
        "title": "A Scandal in Bohemia",
        "author": "Arthur Conan Doyle",
        "note": "Full story · Project Gutenberg",
        "file": "scandal.txt",
        "gutenberg": "https://www.gutenberg.org/ebooks/1661",
    },
]

def _library_dir() -> Path:
    d = Path(__file__).resolve().parent / "data" / "library"
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        d = Path("/tmp") / "meridium_library"
        d.mkdir(parents=True, exist_ok=True)
    return d

def _strip_gutenberg_boilerplate(text: str) -> str:
    """Remove Project Gutenberg header/footer when present."""
    if not text:
        return ""
    start_markers = (
        "*** START OF THE PROJECT GUTENBERG EBOOK",
        "*** START OF THIS PROJECT GUTENBERG EBOOK",
        "***START OF THE PROJECT GUTENBERG EBOOK",
    )
    end_markers = (
        "*** END OF THE PROJECT GUTENBERG EBOOK",
        "*** END OF THIS PROJECT GUTENBERG EBOOK",
        "***END OF THE PROJECT GUTENBERG EBOOK",
    )
    upper = text
    start = 0
    for m in start_markers:
        idx = upper.find(m)
        if idx != -1:
            # skip the rest of that line
            nl = upper.find("\n", idx)
            start = (nl + 1) if nl != -1 else idx + len(m)
            break
    end = len(text)
    for m in end_markers:
        idx = upper.find(m, start)
        if idx != -1:
            end = idx
            break
    body = text[start:end].strip()
    # Soft trim excess leading blank lines
    return body

def load_library_book_text(book: dict) -> str:
    """Load full book text from local cache (data/library)."""
    fname = book.get("file") or ""
    if not fname:
        return book.get("text") or ""
    path = _library_dir() / fname
    # Also try alongside the packaged artifacts path
    alts = [
        path,
        Path(__file__).resolve().parent / "data" / "library" / fname,
        Path("/home/workdir/artifacts/data/library") / fname,
    ]
    for p in alts:
        try:
            if p.exists() and p.stat().st_size > 100:
                raw = p.read_text(encoding="utf-8", errors="replace")
                return _strip_gutenberg_boilerplate(raw)
        except Exception:
            continue
    return book.get("text") or (
        f"Full text file not found ({fname}). "
        f"Add it under data/library/ or read on Project Gutenberg."
    )

def paginate_text(text: str, page_size: int = 2200) -> list:
    """Split text into readable pages near page_size, preferring paragraph breaks."""
    text = (text or "").strip()
    if not text:
        return [""]
    pages = []
    i = 0
    n = len(text)
    while i < n:
        if i + page_size >= n:
            pages.append(text[i:].strip())
            break
        # Prefer break at paragraph, then sentence, then space
        window = text[i : i + page_size + 400]
        cut = page_size
        for sep in ("\n\n", "\n", ". ", "? ", "! ", "; ", " "):
            pos = window.rfind(sep, int(page_size * 0.55), page_size + 350)
            if pos != -1:
                cut = pos + len(sep)
                break
        chunk = text[i : i + cut].strip()
        if chunk:
            pages.append(chunk)
        i += max(cut, 1)
    return pages or [""]


# ============================================================
# CINEMA — YouTube only, grouped by channel
# ============================================================
CINEMA_CATALOG = [
    # —— simple, actually (10) ——
    {"id": "sa_lotus", "title": "How To Force Your Brain To Do Hard Things (Lotus Method)", "creator": "simple, actually", "channel": "simple, actually", "channel_url": "https://www.youtube.com/@simpleactuallyus", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@simpleactuallyus", "kind": "youtube", "youtube_id": "GpsWTFciswE", "tags": ["productivity"]},
    {"id": "sa_cs", "title": "How to study computer science so FAST that it feels ILLEGAL", "creator": "simple, actually", "channel": "simple, actually", "channel_url": "https://www.youtube.com/@simpleactuallyus", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@simpleactuallyus", "kind": "youtube", "youtube_id": "TbZj_hlJitA", "tags": ["study"]},
    {"id": "sa_chem", "title": "How to study CHEMISTRY so FAST that it feels ILLEGAL", "creator": "simple, actually", "channel": "simple, actually", "channel_url": "https://www.youtube.com/@simpleactuallyus", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@simpleactuallyus", "kind": "youtube", "youtube_id": "0oHMoSSelo0", "tags": ["study"]},
    {"id": "sa_bio", "title": "How to study BIOLOGY so FAST that it feels ILLEGAL", "creator": "simple, actually", "channel": "simple, actually", "channel_url": "https://www.youtube.com/@simpleactuallyus", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@simpleactuallyus", "kind": "youtube", "youtube_id": "-qU1mQ0ilxo", "tags": ["study"]},
    {"id": "sa_physics", "title": "How to study PHYSICS so FAST that it feels ILLEGAL", "creator": "simple, actually", "channel": "simple, actually", "channel_url": "https://www.youtube.com/@simpleactuallyus", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@simpleactuallyus", "kind": "youtube", "youtube_id": "kGBv_vZFnvw", "tags": ["study"]},
    {"id": "sa_study_fast", "title": "How to STUDY so FAST that it feels ILLEGAL", "creator": "simple, actually", "channel": "simple, actually", "channel_url": "https://www.youtube.com/@simpleactuallyus", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@simpleactuallyus", "kind": "youtube", "youtube_id": "ZTFcn5rbBFg", "tags": ["study"]},
    {"id": "sa_stoic", "title": "How To Never Get Angry Or Bothered By Anyone (STOICISM)", "creator": "simple, actually", "channel": "simple, actually", "channel_url": "https://www.youtube.com/@simpleactuallyus", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@simpleactuallyus", "kind": "youtube", "youtube_id": "OgJQkabvdA4", "tags": ["mindset"]},
    {"id": "sa_cant_study", "title": "Please Watch This If YOU Can't Study", "creator": "simple, actually", "channel": "simple, actually", "channel_url": "https://www.youtube.com/@simpleactuallyus", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@simpleactuallyus", "kind": "youtube", "youtube_id": "Wm-qGO_dme4", "tags": ["study"]},
    {"id": "sa_hours", "title": "How to Study for Hours Without Getting Distracted", "creator": "simple, actually", "channel": "simple, actually", "channel_url": "https://www.youtube.com/@simpleactuallyus", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@simpleactuallyus", "kind": "youtube", "youtube_id": "XQFsva8fi9k", "tags": ["study"]},
    {"id": "sa_memory", "title": "How to Build a MEMORY PALACE That Actually Works", "creator": "simple, actually", "channel": "simple, actually", "channel_url": "https://www.youtube.com/@simpleactuallyus", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@simpleactuallyus", "kind": "youtube", "youtube_id": "mTK3T8p4md8", "tags": ["study"]},
    # —— riskambition (10) ——
    {"id": "ra_peak", "title": "how to reach peak performance in anything you do.", "creator": "riskambition", "channel": "riskambition", "channel_url": "https://www.youtube.com/@riskambition", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@riskambition", "kind": "youtube", "youtube_id": "18Nh2H0RwLM", "tags": ["productivity"]},
    {"id": "ra_polymath", "title": "how to actually become a polymath.", "creator": "riskambition", "channel": "riskambition", "channel_url": "https://www.youtube.com/@riskambition", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@riskambition", "kind": "youtube", "youtube_id": "jndWxpCzO5g", "tags": ["productivity"]},
    {"id": "ra_flow", "title": "how to easily enter flow state anytime you want", "creator": "riskambition", "channel": "riskambition", "channel_url": "https://www.youtube.com/@riskambition", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@riskambition", "kind": "youtube", "youtube_id": "_e--tk58Lvo", "tags": ["focus"]},
    {"id": "ra_passion", "title": "how to develop extreme passion.", "creator": "riskambition", "channel": "riskambition", "channel_url": "https://www.youtube.com/@riskambition", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@riskambition", "kind": "youtube", "youtube_id": "_BXXXiCgNiM", "tags": ["mindset"]},
    {"id": "ra_hobby", "title": "how to find a hobby you like.", "creator": "riskambition", "channel": "riskambition", "channel_url": "https://www.youtube.com/@riskambition", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@riskambition", "kind": "youtube", "youtube_id": "zl2eZkh6rMU", "tags": ["mindset"]},
    {"id": "ra_deep", "title": "how to enter deep work properly.", "creator": "riskambition", "channel": "riskambition", "channel_url": "https://www.youtube.com/@riskambition", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@riskambition", "kind": "youtube", "youtube_id": "mbxqRzCVJao", "tags": ["focus"]},
    {"id": "ra_discipline", "title": "how to easily become more disciplined.", "creator": "riskambition", "channel": "riskambition", "channel_url": "https://www.youtube.com/@riskambition", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@riskambition", "kind": "youtube", "youtube_id": "4r3A5cxOcmA", "tags": ["productivity"]},
    {"id": "ra_high", "title": "how to become a high performer.", "creator": "riskambition", "channel": "riskambition", "channel_url": "https://www.youtube.com/@riskambition", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@riskambition", "kind": "youtube", "youtube_id": "BJWUaxh-ojM", "tags": ["productivity"]},
    {"id": "ra_hyper", "title": "how to hyperfocus and get more done in less time.", "creator": "riskambition", "channel": "riskambition", "channel_url": "https://www.youtube.com/@riskambition", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@riskambition", "kind": "youtube", "youtube_id": "9_t-NYyhDkM", "tags": ["focus"]},
    {"id": "ra_focus8", "title": "how to focus for 8+ hours a day.", "creator": "riskambition", "channel": "riskambition", "channel_url": "https://www.youtube.com/@riskambition", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@riskambition", "kind": "youtube", "youtube_id": "BOEROJ-CjBY", "tags": ["focus"]},
    # —— Veritasium (10) ——
    {"id": "ve_molecular", "title": "Your Body's Molecular Machines", "creator": "Veritasium", "channel": "Veritasium", "channel_url": "https://www.youtube.com/@veritasium", "category": "youtube", "shelf_category": "Science", "note": "@veritasium", "kind": "youtube", "youtube_id": "X_tYrnv_o6A", "tags": ["science"]},
    {"id": "ve_future", "title": "The Future of Veritasium", "creator": "Veritasium", "channel": "Veritasium", "channel_url": "https://www.youtube.com/@veritasium", "category": "youtube", "shelf_category": "Science", "note": "@veritasium", "kind": "youtube", "youtube_id": "piHGnG4LsmQ", "tags": ["science"]},
    {"id": "ve_fingerprint", "title": "The Problem With Fingerprint Analysis", "creator": "Veritasium", "channel": "Veritasium", "channel_url": "https://www.youtube.com/@veritasium", "category": "youtube", "shelf_category": "Science", "note": "@veritasium", "kind": "youtube", "youtube_id": "mvcesPWvUIc", "tags": ["science"]},
    {"id": "ve_pattern", "title": "We're 99.9% sure this pattern is true, but no one can prove it", "creator": "Veritasium", "channel": "Veritasium", "channel_url": "https://www.youtube.com/@veritasium", "category": "youtube", "shelf_category": "Science", "note": "@veritasium", "kind": "youtube", "youtube_id": "8HBDE-msUjw", "tags": ["math"]},
    {"id": "ve_bet", "title": "A Physics Prof Bet Me $10,000 I'm Wrong", "creator": "Veritasium", "channel": "Veritasium", "channel_url": "https://www.youtube.com/@veritasium", "category": "youtube", "shelf_category": "Science", "note": "@veritasium", "kind": "youtube", "youtube_id": "yCsgoLc_fzI", "tags": ["science"]},
    {"id": "ve_life", "title": "My Life Story", "creator": "Veritasium", "channel": "Veritasium", "channel_url": "https://www.youtube.com/@veritasium", "category": "youtube", "shelf_category": "Science", "note": "@veritasium", "kind": "youtube", "youtube_id": "S1tFT4smd6E", "tags": ["science"]},
    {"id": "ve_maps", "title": "Google Maps is unreasonably fast. Let me explain", "creator": "Veritasium", "channel": "Veritasium", "channel_url": "https://www.youtube.com/@veritasium", "category": "youtube", "shelf_category": "Science", "note": "@veritasium", "kind": "youtube", "youtube_id": "kS-CGkiPetQ", "tags": ["science"]},
    {"id": "ve_gps", "title": "Something is jamming GPS over Europe. Here's what we found", "creator": "Veritasium", "channel": "Veritasium", "channel_url": "https://www.youtube.com/@veritasium", "category": "youtube", "shelf_category": "Science", "note": "@veritasium", "kind": "youtube", "youtube_id": "tz23G_UXCGA", "tags": ["science"]},
    {"id": "ve_antimatter", "title": "What happens if you drop 0.125 grams of antimatter?", "creator": "Veritasium", "channel": "Veritasium", "channel_url": "https://www.youtube.com/@veritasium", "category": "youtube", "shelf_category": "Science", "note": "@veritasium", "kind": "youtube", "youtube_id": "jjp3WC8Unj8", "tags": ["science"]},
    {"id": "ve_ftl", "title": "There Is Something Faster Than Light", "creator": "Veritasium", "channel": "Veritasium", "channel_url": "https://www.youtube.com/@veritasium", "category": "youtube", "shelf_category": "Science", "note": "@veritasium", "kind": "youtube", "youtube_id": "NIk_0AW5hFU", "tags": ["science"]},
    # —— Practical Engineering (10) ——
    {"id": "pe_landfills", "title": "The Hidden Engineering of Landfills", "creator": "Practical Engineering", "channel": "Practical Engineering", "channel_url": "https://www.youtube.com/@PracticalEngineeringChannel", "category": "youtube", "shelf_category": "Science", "note": "@PracticalEngineeringChannel", "kind": "youtube", "youtube_id": "HRx_dZawN44", "tags": ["engineering"]},
    {"id": "pe_baseplates", "title": "What's the Deal with Base Plates?", "creator": "Practical Engineering", "channel": "Practical Engineering", "channel_url": "https://www.youtube.com/@PracticalEngineeringChannel", "category": "youtube", "shelf_category": "Science", "note": "@PracticalEngineeringChannel", "kind": "youtube", "youtube_id": "nGa1244hK9Y", "tags": ["engineering"]},
    {"id": "pe_powergrid", "title": "The Most Confusing Part of the Power Grid", "creator": "Practical Engineering", "channel": "Practical Engineering", "channel_url": "https://www.youtube.com/@PracticalEngineeringChannel", "category": "youtube", "shelf_category": "Science", "note": "@PracticalEngineeringChannel", "kind": "youtube", "youtube_id": "ZwkNTwWJP5k", "tags": ["engineering"]},
    {"id": "pe_blackstart", "title": "What Is A Black Start Of The Power Grid?", "creator": "Practical Engineering", "channel": "Practical Engineering", "channel_url": "https://www.youtube.com/@PracticalEngineeringChannel", "category": "youtube", "shelf_category": "Science", "note": "@PracticalEngineeringChannel", "kind": "youtube", "youtube_id": "uOSnQM1Zu4w", "tags": ["engineering"]},
    {"id": "pe_fish", "title": "How Fish Survive Hydro Turbines", "creator": "Practical Engineering", "channel": "Practical Engineering", "channel_url": "https://www.youtube.com/@PracticalEngineeringChannel", "category": "youtube", "shelf_category": "Science", "note": "@PracticalEngineeringChannel", "kind": "youtube", "youtube_id": "HCE_lFUMXNg", "tags": ["engineering"]},
    {"id": "pe_pump", "title": "Recreating an Ancient Pump (with no moving parts)", "creator": "Practical Engineering", "channel": "Practical Engineering", "channel_url": "https://www.youtube.com/@PracticalEngineeringChannel", "category": "youtube", "shelf_category": "Science", "note": "@PracticalEngineeringChannel", "kind": "youtube", "youtube_id": "7OHCOFFUamQ", "tags": ["engineering"]},
    {"id": "pe_flood", "title": "How Flood Tunnels Work", "creator": "Practical Engineering", "channel": "Practical Engineering", "channel_url": "https://www.youtube.com/@PracticalEngineeringChannel", "category": "youtube", "shelf_category": "Science", "note": "@PracticalEngineeringChannel", "kind": "youtube", "youtube_id": "r4G0aTq5oSM", "tags": ["engineering"]},
    {"id": "pe_loco", "title": "Why Locomotives Don't Have Tires", "creator": "Practical Engineering", "channel": "Practical Engineering", "channel_url": "https://www.youtube.com/@PracticalEngineeringChannel", "category": "youtube", "shelf_category": "Science", "note": "@PracticalEngineeringChannel", "kind": "youtube", "youtube_id": "nGhBHrr5CYQ", "tags": ["engineering"]},
    {"id": "pe_budget", "title": "Why Construction Projects Always Go Over Budget", "creator": "Practical Engineering", "channel": "Practical Engineering", "channel_url": "https://www.youtube.com/@PracticalEngineeringChannel", "category": "youtube", "shelf_category": "Science", "note": "@PracticalEngineeringChannel", "kind": "youtube", "youtube_id": "dOe_6vuaR_s", "tags": ["engineering"]},
    {"id": "pe_million", "title": "1E6 Views and a Few Announcements", "creator": "Practical Engineering", "channel": "Practical Engineering", "channel_url": "https://www.youtube.com/@PracticalEngineeringChannel", "category": "youtube", "shelf_category": "Science", "note": "@PracticalEngineeringChannel", "kind": "youtube", "youtube_id": "qeSXSQFMvbo", "tags": ["engineering"]},
    # —— Outdoor Boys (10) ——
    {"id": "ob_ketchikan", "title": "7 Days Remote Camping, Fishing & Exploring Ketchikan Alaska", "creator": "Outdoor Boys", "channel": "Outdoor Boys", "channel_url": "https://www.youtube.com/@OutdoorBoys", "category": "youtube", "shelf_category": "Outdoors", "note": "@OutdoorBoys", "kind": "youtube", "youtube_id": "LxVczipWxos", "tags": ["outdoors"]},
    {"id": "ob_valdez", "title": "4 Days Camping, Fishing & Eating What We Catch in Alaska", "creator": "Outdoor Boys", "channel": "Outdoor Boys", "channel_url": "https://www.youtube.com/@OutdoorBoys", "category": "youtube", "shelf_category": "Outdoors", "note": "@OutdoorBoys", "kind": "youtube", "youtube_id": "qUhW2hJJVxA", "tags": ["outdoors"]},
    {"id": "ob_trail", "title": "4 Days Camping & Building a Trail", "creator": "Outdoor Boys", "channel": "Outdoor Boys", "channel_url": "https://www.youtube.com/@OutdoorBoys", "category": "youtube", "shelf_category": "Outdoors", "note": "@OutdoorBoys", "kind": "youtube", "youtube_id": "IyCEpSLheUw", "tags": ["outdoors"]},
    {"id": "ob_family10", "title": "1 Week Fishing, Camping, & Hiking Adventure (Family of 10 to Alaska)", "creator": "Outdoor Boys", "channel": "Outdoor Boys", "channel_url": "https://www.youtube.com/@OutdoorBoys", "category": "youtube", "shelf_category": "Outdoors", "note": "@OutdoorBoys", "kind": "youtube", "youtube_id": "4OCJ0Bt66ms", "tags": ["outdoors"]},
    {"id": "ob_proenneke", "title": "3 Days Camping & Fishing Alaska's Wilderness (Near Dick Proenneke's Cabin)", "creator": "Outdoor Boys", "channel": "Outdoor Boys", "channel_url": "https://www.youtube.com/@OutdoorBoys", "category": "youtube", "shelf_category": "Outdoors", "note": "@OutdoorBoys", "kind": "youtube", "youtube_id": "93zzKz-2PZU", "tags": ["outdoors"]},
    {"id": "ob_shrimp", "title": "3 Days Camping in Alaska & Eating What We Catch", "creator": "Outdoor Boys", "channel": "Outdoor Boys", "channel_url": "https://www.youtube.com/@OutdoorBoys", "category": "youtube", "shelf_category": "Outdoors", "note": "@OutdoorBoys", "kind": "youtube", "youtube_id": "0Gx60dye-_U", "tags": ["outdoors"]},
    {"id": "ob_alone", "title": "4 Days Alone in Alaska - Bushcraft Camping & Foraging Food", "creator": "Outdoor Boys", "channel": "Outdoor Boys", "channel_url": "https://www.youtube.com/@OutdoorBoys", "category": "youtube", "shelf_category": "Outdoors", "note": "@OutdoorBoys", "kind": "youtube", "youtube_id": "sSsTR8qqDl4", "tags": ["outdoors"]},
    {"id": "ob_frozen", "title": "Camping on Frozen Ocean - 6 Days Fishing for King Crab", "creator": "Outdoor Boys", "channel": "Outdoor Boys", "channel_url": "https://www.youtube.com/@OutdoorBoys", "category": "youtube", "shelf_category": "Outdoors", "note": "@OutdoorBoys", "kind": "youtube", "youtube_id": "8hvbcAvkuJs", "tags": ["outdoors"]},
    {"id": "ob_swamp", "title": "5 Days Fishing & Camping in Swamp - Catch & Cook", "creator": "Outdoor Boys", "channel": "Outdoor Boys", "channel_url": "https://www.youtube.com/@OutdoorBoys", "category": "youtube", "shelf_category": "Outdoors", "note": "@OutdoorBoys", "kind": "youtube", "youtube_id": "J-sMBdJyclo", "tags": ["outdoors"]},
    {"id": "ob_atv", "title": "ATV Camping & Fishing on Deserted Island", "creator": "Outdoor Boys", "channel": "Outdoor Boys", "channel_url": "https://www.youtube.com/@OutdoorBoys", "category": "youtube", "shelf_category": "Outdoors", "note": "@OutdoorBoys", "kind": "youtube", "youtube_id": "5LUgUW0yox4", "tags": ["outdoors"]},
    # —— SmarterEveryDay (10) ——
    {"id": "sed_taco", "title": "They Call it \"The Taco Turn\" and it's Genius - Smarter Every Day 315", "creator": "SmarterEveryDay", "channel": "SmarterEveryDay", "channel_url": "https://www.youtube.com/@smartereveryday", "category": "youtube", "shelf_category": "Science", "note": "@smartereveryday", "kind": "youtube", "youtube_id": "5lCWqEFVzbY", "tags": ["science"]},
    {"id": "sed_johari", "title": "What Everyone Sees... But I Don't (The Johari Window) - Smarter Every Day 314", "creator": "SmarterEveryDay", "channel": "SmarterEveryDay", "channel_url": "https://www.youtube.com/@smartereveryday", "category": "youtube", "shelf_category": "Science", "note": "@smartereveryday", "kind": "youtube", "youtube_id": "WtQ64nSbdY4", "tags": ["science"]},
    {"id": "sed_spin", "title": "Why Do Spinning Things Do This? - Smarter Every Day 312", "creator": "SmarterEveryDay", "channel": "SmarterEveryDay", "channel_url": "https://www.youtube.com/@smartereveryday", "category": "youtube", "shelf_category": "Science", "note": "@smartereveryday", "kind": "youtube", "youtube_id": "XwBZx1cXEdM", "tags": ["science"]},
    {"id": "sed_nuclear", "title": "I Went Into a Nuclear Plant and It Changed How I Think About Radiation - Smarter Every Day 309", "creator": "SmarterEveryDay", "channel": "SmarterEveryDay", "channel_url": "https://www.youtube.com/@smartereveryday", "category": "youtube", "shelf_category": "Science", "note": "@smartereveryday", "kind": "youtube", "youtube_id": "cRaKMTK7ea0", "tags": ["science"]},
    {"id": "sed_reactor", "title": "Refueling a NUCLEAR REACTOR - Smarter Every Day 311", "creator": "SmarterEveryDay", "channel": "SmarterEveryDay", "channel_url": "https://www.youtube.com/@smartereveryday", "category": "youtube", "shelf_category": "Science", "note": "@smartereveryday", "kind": "youtube", "youtube_id": "v0afQ6w3Bjw", "tags": ["science"]},
    {"id": "sed_america", "title": "I Tried To Make Something In America - Smarter Every Day 308", "creator": "SmarterEveryDay", "channel": "SmarterEveryDay", "channel_url": "https://www.youtube.com/@smartereveryday", "category": "youtube", "shelf_category": "Science", "note": "@smartereveryday", "kind": "youtube", "youtube_id": "3ZTGwcHQfLY", "tags": ["science"]},
    {"id": "sed_pompeii", "title": "Pompeii Changed How I Think About The Roman Empire - Smarter Every Day 310", "creator": "SmarterEveryDay", "channel": "SmarterEveryDay", "channel_url": "https://www.youtube.com/@smartereveryday", "category": "youtube", "shelf_category": "Science", "note": "@smartereveryday", "kind": "youtube", "youtube_id": "dt_CG_xRnrY", "tags": ["science"]},
    {"id": "sed_shorts", "title": "YouTube Shorts is Changing YouTube - Smarter Every Day 266", "creator": "SmarterEveryDay", "channel": "SmarterEveryDay", "channel_url": "https://www.youtube.com/@smartereveryday", "category": "youtube", "shelf_category": "Science", "note": "@smartereveryday", "kind": "youtube", "youtube_id": "ZVaUoyabjAg", "tags": ["science"]},
    {"id": "sed_war", "title": "The Future of War, and How It Affects YOU - Smarter Every Day 211", "creator": "SmarterEveryDay", "channel": "SmarterEveryDay", "channel_url": "https://www.youtube.com/@smartereveryday", "category": "youtube", "shelf_category": "Science", "note": "@smartereveryday", "kind": "youtube", "youtube_id": "qOTYgcdNrXE", "tags": ["science"]},
    {"id": "sed_eclipse", "title": "I Accidentally Photographed Something Unknown During the Eclipse - Smarter Every Day 298", "creator": "SmarterEveryDay", "channel": "SmarterEveryDay", "channel_url": "https://www.youtube.com/@smartereveryday", "category": "youtube", "shelf_category": "Science", "note": "@smartereveryday", "kind": "youtube", "youtube_id": "bQF51mqzrY4", "tags": ["science"]},

    # —— Clarified Mind (10) ——
    {"id": "cm_jubilee", "title": "Jubilee's Spectrum But It's Philosophers on God", "creator": "Clarified Mind", "channel": "Clarified Mind", "channel_url": "https://www.youtube.com/@clarifiedmind", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@clarifiedmind", "kind": "youtube", "youtube_id": "Gh7P3UWjHp8", "tags": ["philosophy"]},
    {"id": "cm_socrates", "title": "Socrates Debates Lao Tzu's Philosophy Of Flow", "creator": "Clarified Mind", "channel": "Clarified Mind", "channel_url": "https://www.youtube.com/@clarifiedmind", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@clarifiedmind", "kind": "youtube", "youtube_id": "rywxXv7rKLA", "tags": ["philosophy"]},
    {"id": "cm_nietzsche_marcus", "title": "Nietzsche debates Marcus Aurelius' Stoic way of living", "creator": "Clarified Mind", "channel": "Clarified Mind", "channel_url": "https://www.youtube.com/@clarifiedmind", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@clarifiedmind", "kind": "youtube", "youtube_id": "wAxYObrcHrY", "tags": ["philosophy"]},
    {"id": "cm_nietzsche_jung", "title": "Nietzsche debates Jung on what makes life worth living", "creator": "Clarified Mind", "channel": "Clarified Mind", "channel_url": "https://www.youtube.com/@clarifiedmind", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@clarifiedmind", "kind": "youtube", "youtube_id": "wXD0SPhncBs", "tags": ["philosophy"]},
    {"id": "cm_trolley", "title": "AI Decides on Absurd Trolley Problems", "creator": "Clarified Mind", "channel": "Clarified Mind", "channel_url": "https://www.youtube.com/@clarifiedmind", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@clarifiedmind", "kind": "youtube", "youtube_id": "1boxiCcpZ-w", "tags": ["philosophy"]},
    {"id": "cm_trolley2", "title": "AI Decides on EVEN MORE Absurd Trolley Problems", "creator": "Clarified Mind", "channel": "Clarified Mind", "channel_url": "https://www.youtube.com/@clarifiedmind", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@clarifiedmind", "kind": "youtube", "youtube_id": "yQlX7yToj-8", "tags": ["philosophy"]},
    {"id": "cm_machiavelli", "title": "Machiavelli debates Marcus Aurelius' Stoicism", "creator": "Clarified Mind", "channel": "Clarified Mind", "channel_url": "https://www.youtube.com/@clarifiedmind", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@clarifiedmind", "kind": "youtube", "youtube_id": "rbjYKZe-Ds0", "tags": ["philosophy"]},
    {"id": "cm_god", "title": "Does God Exist? AI debates (Atheist vs Believer)", "creator": "Clarified Mind", "channel": "Clarified Mind", "channel_url": "https://www.youtube.com/@clarifiedmind", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@clarifiedmind", "kind": "youtube", "youtube_id": "EjxL2oB7J-o", "tags": ["philosophy"]},
    {"id": "cm_freewill", "title": "Does Free Will Exist? AI Debates", "creator": "Clarified Mind", "channel": "Clarified Mind", "channel_url": "https://www.youtube.com/@clarifiedmind", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@clarifiedmind", "kind": "youtube", "youtube_id": "1zEjQ_LILJA", "tags": ["philosophy"]},
    {"id": "cm_econ", "title": "Best Economic System? AI debates (Capitalist vs Socialist)", "creator": "Clarified Mind", "channel": "Clarified Mind", "channel_url": "https://www.youtube.com/@clarifiedmind", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@clarifiedmind", "kind": "youtube", "youtube_id": "ZB4soi4FZJc", "tags": ["philosophy"]},
    # —— Just Explained (10) ——
    {"id": "je_prog", "title": "Every Programming Language Explained in 16 Minutes", "creator": "Just Explained", "channel": "Just Explained", "channel_url": "https://www.youtube.com/@justexplainedyt", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@justexplainedyt", "kind": "youtube", "youtube_id": "uerEG_yigco", "tags": ["tech"]},
    {"id": "je_usb", "title": "Every USB Port COLOR Explained in 13 Minutes", "creator": "Just Explained", "channel": "Just Explained", "channel_url": "https://www.youtube.com/@justexplainedyt", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@justexplainedyt", "kind": "youtube", "youtube_id": "r2sBNRWcvTY", "tags": ["tech"]},
    {"id": "je_illegal_os", "title": "Every Illegal Operating System Explained in 15 Minutes", "creator": "Just Explained", "channel": "Just Explained", "channel_url": "https://www.youtube.com/@justexplainedyt", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@justexplainedyt", "kind": "youtube", "youtube_id": "2D2Z-eqK0YM", "tags": ["tech"]},
    {"id": "je_tv", "title": "Every Type of TV SCREEN Explained in 11 Minutes", "creator": "Just Explained", "channel": "Just Explained", "channel_url": "https://www.youtube.com/@justexplainedyt", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@justexplainedyt", "kind": "youtube", "youtube_id": "9BcQk1myhbc", "tags": ["tech"]},
    {"id": "je_ai", "title": "Every AI Model Explained in 17 Minutes", "creator": "Just Explained", "channel": "Just Explained", "channel_url": "https://www.youtube.com/@justexplainedyt", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@justexplainedyt", "kind": "youtube", "youtube_id": "h1MEtoxegzw", "tags": ["tech"]},
    {"id": "je_underrated", "title": "Every Underrated Tech Invention That Changed The World", "creator": "Just Explained", "channel": "Just Explained", "channel_url": "https://www.youtube.com/@justexplainedyt", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@justexplainedyt", "kind": "youtube", "youtube_id": "yr8NqTSxZ2w", "tags": ["tech"]},
    {"id": "je_watch_tv", "title": "Every Way People Watched TV Explained", "creator": "Just Explained", "channel": "Just Explained", "channel_url": "https://www.youtube.com/@justexplainedyt", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@justexplainedyt", "kind": "youtube", "youtube_id": "FbTBA389Ks0", "tags": ["tech"]},
    {"id": "je_network", "title": "Every Mobile Network Explained in 12 Minutes", "creator": "Just Explained", "channel": "Just Explained", "channel_url": "https://www.youtube.com/@justexplainedyt", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@justexplainedyt", "kind": "youtube", "youtube_id": "nfyyidvGZuI", "tags": ["tech"]},
    {"id": "je_browser", "title": "Every Web Browser Explained in 18 Minutes", "creator": "Just Explained", "channel": "Just Explained", "channel_url": "https://www.youtube.com/@justexplainedyt", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@justexplainedyt", "kind": "youtube", "youtube_id": "zF-4OO5p_Yg", "tags": ["tech"]},
    {"id": "je_os", "title": "Every Operating System Explained in 20 Minutes", "creator": "Just Explained", "channel": "Just Explained", "channel_url": "https://www.youtube.com/@justexplainedyt", "category": "youtube", "shelf_category": "Simple But Effective", "note": "@justexplainedyt", "kind": "youtube", "youtube_id": "6Bjj1i6oMow", "tags": ["tech"]},
    # —— Uncovering (10) ——
    {"id": "uc_nyc", "title": "The NYC Gang War, Mapped", "creator": "Uncovering", "channel": "Uncovering", "channel_url": "https://www.youtube.com/@uncovering_yt", "category": "youtube", "shelf_category": "Documentaries", "note": "@uncovering_yt", "kind": "youtube", "youtube_id": "tk2W7mjfFpY", "tags": ["docs"]},
    {"id": "uc_afghan", "title": "72 Hours to Escape Afghanistan", "creator": "Uncovering", "channel": "Uncovering", "channel_url": "https://www.youtube.com/@uncovering_yt", "category": "youtube", "shelf_category": "Documentaries", "note": "@uncovering_yt", "kind": "youtube", "youtube_id": "MwfDVUyGLTo", "tags": ["docs"]},
    {"id": "uc_astroworld", "title": "The Deadly Pit at an Astroworld Concert", "creator": "Uncovering", "channel": "Uncovering", "channel_url": "https://www.youtube.com/@uncovering_yt", "category": "youtube", "shelf_category": "Documentaries", "note": "@uncovering_yt", "kind": "youtube", "youtube_id": "HUxHBgeO8JE", "tags": ["docs"]},
    {"id": "uc_titanic", "title": "The Last 4 Survivors of the Titanic", "creator": "Uncovering", "channel": "Uncovering", "channel_url": "https://www.youtube.com/@uncovering_yt", "category": "youtube", "shelf_category": "Documentaries", "note": "@uncovering_yt", "kind": "youtube", "youtube_id": "xUZAkSaxMUo", "tags": ["docs"]},
    {"id": "uc_atomic", "title": "The Man Who Survived Both Atomic Bombs", "creator": "Uncovering", "channel": "Uncovering", "channel_url": "https://www.youtube.com/@uncovering_yt", "category": "youtube", "shelf_category": "Documentaries", "note": "@uncovering_yt", "kind": "youtube", "youtube_id": "FGOpRAuIbUo", "tags": ["docs"]},
    {"id": "uc_911", "title": "The Last 4 Survivors of 9/11", "creator": "Uncovering", "channel": "Uncovering", "channel_url": "https://www.youtube.com/@uncovering_yt", "category": "youtube", "shelf_category": "Documentaries", "note": "@uncovering_yt", "kind": "youtube", "youtube_id": "FiGgO-wfEzs", "tags": ["docs"]},
    {"id": "uc_japan", "title": "The Dark Truth Behind Japan's Free Homes", "creator": "Uncovering", "channel": "Uncovering", "channel_url": "https://www.youtube.com/@uncovering_yt", "category": "youtube", "shelf_category": "Documentaries", "note": "@uncovering_yt", "kind": "youtube", "youtube_id": "Cn-LVCWHIx0", "tags": ["docs"]},
    {"id": "uc_chicago", "title": "The Chicago Gang War, Mapped", "creator": "Uncovering", "channel": "Uncovering", "channel_url": "https://www.youtube.com/@uncovering_yt", "category": "youtube", "shelf_category": "Documentaries", "note": "@uncovering_yt", "kind": "youtube", "youtube_id": "4wHJWlDRVN8", "tags": ["docs"]},
    {"id": "uc_bermuda", "title": "Why Planes Disappear in the Bermuda Triangle", "creator": "Uncovering", "channel": "Uncovering", "channel_url": "https://www.youtube.com/@uncovering_yt", "category": "youtube", "shelf_category": "Documentaries", "note": "@uncovering_yt", "kind": "youtube", "youtube_id": "AeetW-9BOgs", "tags": ["docs"]},
    {"id": "uc_binladen", "title": "Exposing Bin Laden's 19 Hideouts", "creator": "Uncovering", "channel": "Uncovering", "channel_url": "https://www.youtube.com/@uncovering_yt", "category": "youtube", "shelf_category": "Documentaries", "note": "@uncovering_yt", "kind": "youtube", "youtube_id": "LyQy5_He0Xk", "tags": ["docs"]},
    # —— The Big Lez Show (official) ——
    {"id": "bl_s1_all", "title": "THE BIG LEZ SHOW — ALL OF SEASON 1", "creator": "THE BIG LEZ SHOW OFFICIAL", "channel": "THE BIG LEZ SHOW", "channel_url": "https://www.youtube.com/@THEBIGLEZSHOWOFFICIAL", "category": "youtube", "shelf_category": "Shows", "playlist": "The Big Lez Saga", "note": "@THEBIGLEZSHOWOFFICIAL · Season 1 complete", "kind": "youtube", "youtube_id": "VuihdCwvm80", "tags": ["comedy"]},
    {"id": "bl_s2_all", "title": "THE BIG LEZ SHOW — ALL OF SEASON 2", "creator": "THE BIG LEZ SHOW OFFICIAL", "channel": "THE BIG LEZ SHOW", "channel_url": "https://www.youtube.com/@THEBIGLEZSHOWOFFICIAL", "category": "youtube", "shelf_category": "Shows", "playlist": "The Big Lez Saga", "note": "@THEBIGLEZSHOWOFFICIAL · Season 2 complete", "kind": "youtube", "youtube_id": "OgX31m23zeg", "tags": ["comedy"]},
    {"id": "bl_s3_all", "title": "THE BIG LEZ SHOW — ALL OF SEASON 3", "creator": "THE BIG LEZ SHOW OFFICIAL", "channel": "THE BIG LEZ SHOW", "channel_url": "https://www.youtube.com/@THEBIGLEZSHOWOFFICIAL", "category": "youtube", "shelf_category": "Shows", "playlist": "The Big Lez Saga", "note": "@THEBIGLEZSHOWOFFICIAL · Season 3 complete", "kind": "youtube", "youtube_id": "HRJuo0vO3BA", "tags": ["comedy"]},
    {"id": "bl_s4_all", "title": "THE BIG LEZ SHOW — ALL OF SEASON 4", "creator": "THE BIG LEZ SHOW OFFICIAL", "channel": "THE BIG LEZ SHOW", "channel_url": "https://www.youtube.com/@THEBIGLEZSHOWOFFICIAL", "category": "youtube", "shelf_category": "Shows", "playlist": "The Big Lez Saga", "note": "@THEBIGLEZSHOWOFFICIAL · Season 4 complete", "kind": "youtube", "youtube_id": "G2wVHFCfjsE", "tags": ["comedy"]},
    {"id": "bl_s1e01", "title": "S01 EP01 · The Flowers", "creator": "THE BIG LEZ SHOW OFFICIAL", "channel": "THE BIG LEZ SHOW", "channel_url": "https://www.youtube.com/@THEBIGLEZSHOWOFFICIAL", "category": "youtube", "shelf_category": "Shows", "playlist": "Season 1 Episodes", "note": "Official episode", "kind": "youtube", "youtube_id": "N1n0r3UnpeY", "tags": ["comedy"]},
    {"id": "bl_s1e02", "title": "S01 EP02 · The Volcano Bong", "creator": "THE BIG LEZ SHOW OFFICIAL", "channel": "THE BIG LEZ SHOW", "channel_url": "https://www.youtube.com/@THEBIGLEZSHOWOFFICIAL", "category": "youtube", "shelf_category": "Shows", "playlist": "Season 1 Episodes", "note": "Official episode", "kind": "youtube", "youtube_id": "p48-G4KmRXk", "tags": ["comedy"]},
    {"id": "bl_s1e03", "title": "S01 EP03 · Norton's Revenge", "creator": "THE BIG LEZ SHOW OFFICIAL", "channel": "THE BIG LEZ SHOW", "channel_url": "https://www.youtube.com/@THEBIGLEZSHOWOFFICIAL", "category": "youtube", "shelf_category": "Shows", "playlist": "Season 1 Episodes", "note": "Official episode", "kind": "youtube", "youtube_id": "ilnYCCvAqsM", "tags": ["comedy"]},
    {"id": "bl_s1e11", "title": "S01 EP11 · Choomah Island", "creator": "THE BIG LEZ SHOW OFFICIAL", "channel": "THE BIG LEZ SHOW", "channel_url": "https://www.youtube.com/@THEBIGLEZSHOWOFFICIAL", "category": "youtube", "shelf_category": "Shows", "playlist": "Season 1 Episodes", "note": "Official episode", "kind": "youtube", "youtube_id": "BiFJDQkmXMA", "tags": ["comedy"]},
    {"id": "bl_s2e01", "title": "S02 EP01 · They're Back", "creator": "THE BIG LEZ SHOW OFFICIAL", "channel": "THE BIG LEZ SHOW", "channel_url": "https://www.youtube.com/@THEBIGLEZSHOWOFFICIAL", "category": "youtube", "shelf_category": "Shows", "playlist": "Season 2 Episodes", "note": "Official episode", "kind": "youtube", "youtube_id": "E7AFfJFJhtE", "tags": ["comedy"]},
    {"id": "bl_s2e02", "title": "S02 EP02 · The Trippa Snippa", "creator": "THE BIG LEZ SHOW OFFICIAL", "channel": "THE BIG LEZ SHOW", "channel_url": "https://www.youtube.com/@THEBIGLEZSHOWOFFICIAL", "category": "youtube", "shelf_category": "Shows", "playlist": "Season 2 Episodes", "note": "Official episode", "kind": "youtube", "youtube_id": "FhykvrPZwA4", "tags": ["comedy"]},
    {"id": "bl_choomah2", "title": "Choomah Island 2", "creator": "THE BIG LEZ SHOW OFFICIAL", "channel": "THE BIG LEZ SHOW", "channel_url": "https://www.youtube.com/@THEBIGLEZSHOWOFFICIAL", "category": "youtube", "shelf_category": "Shows", "playlist": "Specials", "note": "Official special", "kind": "youtube", "youtube_id": "7WwLT32_VAk", "tags": ["comedy"]},
    {"id": "bl_sassy1", "title": "Sassy the Sasquatch EP01 · Seen a Dinosaur", "creator": "THE BIG LEZ SHOW OFFICIAL", "channel": "THE BIG LEZ SHOW", "channel_url": "https://www.youtube.com/@THEBIGLEZSHOWOFFICIAL", "category": "youtube", "shelf_category": "Shows", "playlist": "Sassy the Sasquatch", "note": "Spin-off", "kind": "youtube", "youtube_id": "9OmR0ypCyOU", "tags": ["comedy"]},
    {"id": "bl_sassy2", "title": "Sassy the Sasquatch EP02 · Water You Talkinabeet", "creator": "THE BIG LEZ SHOW OFFICIAL", "channel": "THE BIG LEZ SHOW", "channel_url": "https://www.youtube.com/@THEBIGLEZSHOWOFFICIAL", "category": "youtube", "shelf_category": "Shows", "playlist": "Sassy the Sasquatch", "note": "Spin-off", "kind": "youtube", "youtube_id": "tvCUmH92HfU", "tags": ["comedy"]},
    {"id": "bl_mike1", "title": "The Mike Nolan Show EP01 · Yeah Nah Yeah", "creator": "THE BIG LEZ SHOW OFFICIAL", "channel": "THE BIG LEZ SHOW", "channel_url": "https://www.youtube.com/@THEBIGLEZSHOWOFFICIAL", "category": "youtube", "shelf_category": "Shows", "playlist": "Mike Nolan Show", "note": "Spin-off", "kind": "youtube", "youtube_id": "uuc9frxacfE", "tags": ["comedy"]},

    # —— Salad Fingers (David Firth official) ——
    {"id": "sf_01", "title": "Salad Fingers 1: Spoons", "creator": "David Firth", "channel": "Salad Fingers", "channel_url": "https://www.youtube.com/@davidfirth", "category": "youtube", "shelf_category": "Shows", "playlist": "Salad Fingers", "note": "David Firth · official", "kind": "youtube", "youtube_id": "M3iOROuTuMA", "tags": ["indie"]},
    {"id": "sf_02", "title": "Salad Fingers 2: Friends", "creator": "David Firth", "channel": "Salad Fingers", "channel_url": "https://www.youtube.com/@davidfirth", "category": "youtube", "shelf_category": "Shows", "playlist": "Salad Fingers", "note": "David Firth · official", "kind": "youtube", "youtube_id": "cuCw5k-Lph0", "tags": ["indie"]},
    {"id": "sf_03", "title": "Salad Fingers 3: Nettles", "creator": "David Firth", "channel": "Salad Fingers", "channel_url": "https://www.youtube.com/@davidfirth", "category": "youtube", "shelf_category": "Shows", "playlist": "Salad Fingers", "note": "David Firth · official", "kind": "youtube", "youtube_id": "ojoICRzSCOo", "tags": ["indie"]},
    {"id": "sf_04", "title": "Salad Fingers 4: Cage", "creator": "David Firth", "channel": "Salad Fingers", "channel_url": "https://www.youtube.com/@davidfirth", "category": "youtube", "shelf_category": "Shows", "playlist": "Salad Fingers", "note": "David Firth · official", "kind": "youtube", "youtube_id": "tBNrtrntkJ4", "tags": ["indie"]},
    {"id": "sf_05", "title": "Salad Fingers 5: Picnic", "creator": "David Firth", "channel": "Salad Fingers", "channel_url": "https://www.youtube.com/@davidfirth", "category": "youtube", "shelf_category": "Shows", "playlist": "Salad Fingers", "note": "David Firth · official", "kind": "youtube", "youtube_id": "P_zbGGNI7lo", "tags": ["indie"]},
    {"id": "sf_06", "title": "Salad Fingers 6: Present", "creator": "David Firth", "channel": "Salad Fingers", "channel_url": "https://www.youtube.com/@davidfirth", "category": "youtube", "shelf_category": "Shows", "playlist": "Salad Fingers", "note": "David Firth · official", "kind": "youtube", "youtube_id": "rU2D0ncBFm0", "tags": ["indie"]},
    {"id": "sf_08", "title": "Salad Fingers 8: Cupboard", "creator": "David Firth", "channel": "Salad Fingers", "channel_url": "https://www.youtube.com/@davidfirth", "category": "youtube", "shelf_category": "Shows", "playlist": "Salad Fingers", "note": "David Firth · official", "kind": "youtube", "youtube_id": "oykmawhKWhc", "tags": ["indie"]},
    {"id": "sf_09", "title": "Salad Fingers 9: Letter", "creator": "David Firth", "channel": "Salad Fingers", "channel_url": "https://www.youtube.com/@davidfirth", "category": "youtube", "shelf_category": "Shows", "playlist": "Salad Fingers", "note": "David Firth · official", "kind": "youtube", "youtube_id": "MSOnIS84x1k", "tags": ["indie"]},
    {"id": "sf_11", "title": "Salad Fingers 11: Glass Brother", "creator": "David Firth", "channel": "Salad Fingers", "channel_url": "https://www.youtube.com/@davidfirth", "category": "youtube", "shelf_category": "Shows", "playlist": "Salad Fingers", "note": "David Firth · official", "kind": "youtube", "youtube_id": "qeE-J-GjAyQ", "tags": ["indie"]},
    {"id": "sf_market", "title": "Salad Fingers — Market", "creator": "David Firth", "channel": "Salad Fingers", "channel_url": "https://www.youtube.com/@davidfirth", "category": "youtube", "shelf_category": "Shows", "playlist": "Salad Fingers", "note": "David Firth · official", "kind": "youtube", "youtube_id": "62weI2Wq0TQ", "tags": ["indie"]},
    # —— Don't Hug Me I'm Scared (original web series, official) ——
    {"id": "dhmis_1", "title": "Don't Hug Me I'm Scared 1 — Creativity", "creator": "Don't Hug Me I'm Scared", "channel": "Don't Hug Me I'm Scared", "channel_url": "https://www.youtube.com/@DontHugMeImScared", "category": "youtube", "shelf_category": "Shows", "playlist": "Original Web Series", "note": "Official web series · not the TV reboot", "kind": "youtube", "youtube_id": "9C_HReR_McQ", "tags": ["indie"]},
    {"id": "dhmis_2", "title": "Don't Hug Me I'm Scared 2 — Time", "creator": "Don't Hug Me I'm Scared", "channel": "Don't Hug Me I'm Scared", "channel_url": "https://www.youtube.com/@DontHugMeImScared", "category": "youtube", "shelf_category": "Shows", "playlist": "Original Web Series", "note": "Official web series", "kind": "youtube", "youtube_id": "vtkGtXtDlQA", "tags": ["indie"]},
    {"id": "dhmis_3", "title": "Don't Hug Me I'm Scared 3 — Love", "creator": "Don't Hug Me I'm Scared", "channel": "Don't Hug Me I'm Scared", "channel_url": "https://www.youtube.com/@DontHugMeImScared", "category": "youtube", "shelf_category": "Shows", "playlist": "Original Web Series", "note": "Official web series", "kind": "youtube", "youtube_id": "sXOdn6vLCuU", "tags": ["indie"]},
    {"id": "dhmis_4", "title": "Don't Hug Me I'm Scared 4 — Computer", "creator": "Don't Hug Me I'm Scared", "channel": "Don't Hug Me I'm Scared", "channel_url": "https://www.youtube.com/@DontHugMeImScared", "category": "youtube", "shelf_category": "Shows", "playlist": "Original Web Series", "note": "Official web series", "kind": "youtube", "youtube_id": "G9FGgwCQ22w", "tags": ["indie"]},
    {"id": "dhmis_5", "title": "Don't Hug Me I'm Scared 5 — Healthy", "creator": "Don't Hug Me I'm Scared", "channel": "Don't Hug Me I'm Scared", "channel_url": "https://www.youtube.com/@DontHugMeImScared", "category": "youtube", "shelf_category": "Shows", "playlist": "Original Web Series", "note": "Official web series", "kind": "youtube", "youtube_id": "tS_Xq7gSCBM", "tags": ["indie"]},
    {"id": "dhmis_bad", "title": "Bad Things That Could Happen", "creator": "Don't Hug Me I'm Scared", "channel": "Don't Hug Me I'm Scared", "channel_url": "https://www.youtube.com/@DontHugMeImScared", "category": "youtube", "shelf_category": "Shows", "playlist": "Original Web Series", "note": "Official short", "kind": "youtube", "youtube_id": "5hIKKYv_3Ic", "tags": ["indie"]},
    # —— asdfmovie (TomSka official) ——
    {"id": "asdf_1", "title": "asdfmovie", "creator": "TomSka", "channel": "asdfmovie", "channel_url": "https://www.youtube.com/@TomSka", "category": "youtube", "shelf_category": "Shows", "playlist": "asdfmovie", "note": "TomSka · official", "kind": "youtube", "youtube_id": "IYnsfV5N2n8", "tags": ["indie"]},
    {"id": "asdf_6", "title": "asdfmovie6", "creator": "TomSka", "channel": "asdfmovie", "channel_url": "https://www.youtube.com/@TomSka", "category": "youtube", "shelf_category": "Shows", "playlist": "asdfmovie", "note": "TomSka · official", "kind": "youtube", "youtube_id": "hrzIykdka4s", "tags": ["indie"]},
    {"id": "asdf_13", "title": "asdfmovie13", "creator": "TomSka", "channel": "asdfmovie", "channel_url": "https://www.youtube.com/@TomSka", "category": "youtube", "shelf_category": "Shows", "playlist": "asdfmovie", "note": "TomSka · official", "kind": "youtube", "youtube_id": "QL3H7CUJMDU", "tags": ["indie"]},
    {"id": "asdf_14", "title": "asdfmovie14", "creator": "TomSka", "channel": "asdfmovie", "channel_url": "https://www.youtube.com/@TomSka", "category": "youtube", "shelf_category": "Shows", "playlist": "asdfmovie", "note": "TomSka · official", "kind": "youtube", "youtube_id": "vc6aHpPGPYU", "tags": ["indie"]},
    {"id": "asdf_15", "title": "asdfmovie15", "creator": "TomSka", "channel": "asdfmovie", "channel_url": "https://www.youtube.com/@TomSka", "category": "youtube", "shelf_category": "Shows", "playlist": "asdfmovie", "note": "TomSka · official", "kind": "youtube", "youtube_id": "uApthBVk7mw", "tags": ["indie"]},
    {"id": "asdf_16", "title": "asdfmovie16", "creator": "TomSka", "channel": "asdfmovie", "channel_url": "https://www.youtube.com/@TomSka", "category": "youtube", "shelf_category": "Shows", "playlist": "asdfmovie", "note": "TomSka · official", "kind": "youtube", "youtube_id": "qcwqUf_B5mM", "tags": ["indie"]},
    # —— Eddsworld (official) ——
    {"id": "edd_fundeath", "title": "Eddsworld — Fun Dead", "creator": "Eddsworld", "channel": "Eddsworld", "channel_url": "https://www.youtube.com/@eddsworld", "category": "youtube", "shelf_category": "Shows", "playlist": "Eddisodes", "note": "Official", "kind": "youtube", "youtube_id": "3w1pFW44xkM", "tags": ["indie"]},
    {"id": "edd_power", "title": "Eddsworld — PowerEdd", "creator": "Eddsworld", "channel": "Eddsworld", "channel_url": "https://www.youtube.com/@eddsworld", "category": "youtube", "shelf_category": "Shows", "playlist": "Eddisodes", "note": "Official", "kind": "youtube", "youtube_id": "Uy4ksRIwOzQ", "tags": ["indie"]},
    {"id": "edd_end1", "title": "Eddsworld — The End (Part 1)", "creator": "Eddsworld", "channel": "Eddsworld", "channel_url": "https://www.youtube.com/@eddsworld", "category": "youtube", "shelf_category": "Shows", "playlist": "Eddisodes", "note": "Official", "kind": "youtube", "youtube_id": "6ux0ERfzDSU", "tags": ["indie"]},
    {"id": "edd_end2", "title": "Eddsworld — The End (Part 2)", "creator": "Eddsworld", "channel": "Eddsworld", "channel_url": "https://www.youtube.com/@eddsworld", "category": "youtube", "shelf_category": "Shows", "playlist": "Eddisodes", "note": "Official", "kind": "youtube", "youtube_id": "PxtRL1tclds", "tags": ["indie"]},
    {"id": "edd_saloon", "title": "Eddsworld — Saloonatics", "creator": "Eddsworld", "channel": "Eddsworld", "channel_url": "https://www.youtube.com/@eddsworld", "category": "youtube", "shelf_category": "Shows", "playlist": "Eddisodes", "note": "Official", "kind": "youtube", "youtube_id": "pbBI1dmJX9c", "tags": ["indie"]},
    {"id": "edd_beaster", "title": "Eddsworld — The Beaster Bunny", "creator": "Eddsworld", "channel": "Eddsworld", "channel_url": "https://www.youtube.com/@eddsworld", "category": "youtube", "shelf_category": "Shows", "playlist": "Beyond", "note": "Official", "kind": "youtube", "youtube_id": "IN9AUtvhvdM", "tags": ["indie"]},
    {"id": "edd_surf1", "title": "Eddsworld — Surf & Turf Wars pt. 1", "creator": "Eddsworld", "channel": "Eddsworld", "channel_url": "https://www.youtube.com/@eddsworld", "category": "youtube", "shelf_category": "Shows", "playlist": "Beyond", "note": "Official", "kind": "youtube", "youtube_id": "V721mZcriMY", "tags": ["indie"]},
    {"id": "edd_surf2", "title": "Eddsworld — Surf & Turf Wars pt. 2", "creator": "Eddsworld", "channel": "Eddsworld", "channel_url": "https://www.youtube.com/@eddsworld", "category": "youtube", "shelf_category": "Shows", "playlist": "Beyond", "note": "Official", "kind": "youtube", "youtube_id": "tVwQoNOp2v4", "tags": ["indie"]},
    {"id": "edd_hide", "title": "Eddsworld — Hide and Seek", "creator": "Eddsworld", "channel": "Eddsworld", "channel_url": "https://www.youtube.com/@eddsworld", "category": "youtube", "shelf_category": "Shows", "playlist": "Eddisodes", "note": "Official", "kind": "youtube", "youtube_id": "D1O8fVG8_pk", "tags": ["indie"]},
    {"id": "edd_casting", "title": "Eddsworld — Casting Call", "creator": "Eddsworld", "channel": "Eddsworld", "channel_url": "https://www.youtube.com/@eddsworld", "category": "youtube", "shelf_category": "Shows", "playlist": "Beyond", "note": "Official", "kind": "youtube", "youtube_id": "H-_qv3gioes", "tags": ["indie"]},
    # —— Homestar Runner (official) ——
    {"id": "hr_sb100", "title": "Strong Bad Email #100 — Flashback", "creator": "Homestar Runner", "channel": "Homestar Runner", "channel_url": "https://www.youtube.com/@homestarrunnerdotcom", "category": "youtube", "shelf_category": "Shows", "playlist": "Strong Bad Emails", "note": "homestarrunnerdotcom · official", "kind": "youtube", "youtube_id": "DyZQl0NmQls", "tags": ["indie"]},

    # —— Chilling Scares ——
    {"id": "cs_audio", "title": "5 Most Disturbing Audio Recordings", "creator": "Chilling Scares", "channel": "Chilling Scares", "channel_url": "https://www.youtube.com/@ChillingScares", "category": "youtube", "shelf_category": "Horror", "note": "@ChillingScares", "kind": "youtube", "youtube_id": "x6qMEB81bgE", "tags": ["horror"]},
    {"id": "cs_mysteries", "title": "Disturbing Internet Mysteries", "creator": "Chilling Scares", "channel": "Chilling Scares", "channel_url": "https://www.youtube.com/@ChillingScares", "category": "youtube", "shelf_category": "Horror", "note": "@ChillingScares", "kind": "youtube", "youtube_id": "P6X-EOofsOQ", "tags": ["horror"]},
    {"id": "cs_corners", "title": "5 Most Disturbing Corners of the Internet", "creator": "Chilling Scares", "channel": "Chilling Scares", "channel_url": "https://www.youtube.com/@ChillingScares", "category": "youtube", "shelf_category": "Horror", "note": "@ChillingScares", "kind": "youtube", "youtube_id": "YBppWMY6FZU", "tags": ["horror"]},
    {"id": "cs_tv", "title": "5 Most Disturbing Moments in TV History", "creator": "Chilling Scares", "channel": "Chilling Scares", "channel_url": "https://www.youtube.com/@ChillingScares", "category": "youtube", "shelf_category": "Horror", "note": "@ChillingScares", "kind": "youtube", "youtube_id": "_O_AiwQkCtg", "tags": ["horror"]},
    {"id": "cs_rabbit", "title": "5 Most Disturbing Internet Rabbit Holes", "creator": "Chilling Scares", "channel": "Chilling Scares", "channel_url": "https://www.youtube.com/@ChillingScares", "category": "youtube", "shelf_category": "Horror", "note": "@ChillingScares", "kind": "youtube", "youtube_id": "jTKLn6yLqik", "tags": ["horror"]},
    {"id": "cs_forest", "title": "6 Most Disturbing Forest Encounters Caught on Camera", "creator": "Chilling Scares", "channel": "Chilling Scares", "channel_url": "https://www.youtube.com/@ChillingScares", "category": "youtube", "shelf_category": "Horror", "note": "@ChillingScares", "kind": "youtube", "youtube_id": "cweBJSGeNiE", "tags": ["horror"]},
    {"id": "cs_4chan", "title": "6 Most Disturbing 4Chan Threads", "creator": "Chilling Scares", "channel": "Chilling Scares", "channel_url": "https://www.youtube.com/@ChillingScares", "category": "youtube", "shelf_category": "Horror", "note": "@ChillingScares", "kind": "youtube", "youtube_id": "4c8uTVaB9Ow", "tags": ["horror"]},
    {"id": "cs_camping", "title": "6 Most Disturbing Camping Encounters Caught on Camera", "creator": "Chilling Scares", "channel": "Chilling Scares", "channel_url": "https://www.youtube.com/@ChillingScares", "category": "youtube", "shelf_category": "Horror", "note": "@ChillingScares", "kind": "youtube", "youtube_id": "JyC7HujBvA0", "tags": ["horror"]},
    {"id": "cs_locations", "title": "6 Most Disturbing Mysterious Locations", "creator": "Chilling Scares", "channel": "Chilling Scares", "channel_url": "https://www.youtube.com/@ChillingScares", "category": "youtube", "shelf_category": "Horror", "note": "@ChillingScares", "kind": "youtube", "youtube_id": "9wTSaVOVAGo", "tags": ["horror"]},
    {"id": "cs_dashcam", "title": "8 Most Disturbing Things Caught on Dashcam Footage (Vol. 6)", "creator": "Chilling Scares", "channel": "Chilling Scares", "channel_url": "https://www.youtube.com/@ChillingScares", "category": "youtube", "shelf_category": "Horror", "note": "@ChillingScares", "kind": "youtube", "youtube_id": "BUfXcCWAeMw", "tags": ["horror"]},
    # —— Nick Crowley ——
    {"id": "nc_corners6", "title": "The Internet's Darkest Corners 6", "creator": "Nick Crowley", "channel": "Nick Crowley", "channel_url": "https://www.youtube.com/@NickCrowley", "category": "youtube", "shelf_category": "Documentaries", "note": "@NickCrowley", "kind": "youtube", "youtube_id": "PiAiYBxMjYU", "tags": ["docs"]},
    {"id": "nc_corners5", "title": "The Internet's Darkest Corners 5", "creator": "Nick Crowley", "channel": "Nick Crowley", "channel_url": "https://www.youtube.com/@NickCrowley", "category": "youtube", "shelf_category": "Documentaries", "note": "@NickCrowley", "kind": "youtube", "youtube_id": "UfD4ORdDRZQ", "tags": ["docs"]},
    {"id": "nc_corners4", "title": "The Internet's Darkest Corners 4", "creator": "Nick Crowley", "channel": "Nick Crowley", "channel_url": "https://www.youtube.com/@NickCrowley", "category": "youtube", "shelf_category": "Documentaries", "note": "@NickCrowley", "kind": "youtube", "youtube_id": "51MkSH-P3MU", "tags": ["docs"]},
    {"id": "nc_deadliest", "title": "The Internet's Deadliest Video", "creator": "Nick Crowley", "channel": "Nick Crowley", "channel_url": "https://www.youtube.com/@NickCrowley", "category": "youtube", "shelf_category": "Documentaries", "note": "@NickCrowley", "kind": "youtube", "youtube_id": "Hob2BgTOIhA", "tags": ["docs"]},
    {"id": "nc_yt_dark2", "title": "YouTube's Darkest Videos 2", "creator": "Nick Crowley", "channel": "Nick Crowley", "channel_url": "https://www.youtube.com/@NickCrowley", "category": "youtube", "shelf_category": "Documentaries", "note": "@NickCrowley", "kind": "youtube", "youtube_id": "YXIlY4kFT7Y", "tags": ["docs"]},
    {"id": "nc_smart", "title": "smartschoolboy9: An Internet Rabbit Hole", "creator": "Nick Crowley", "channel": "Nick Crowley", "channel_url": "https://www.youtube.com/@NickCrowley", "category": "youtube", "shelf_category": "Documentaries", "note": "@NickCrowley", "kind": "youtube", "youtube_id": "V0folj9X9nQ", "tags": ["docs"]},
    # —— TA Outdoors ——
    {"id": "ta_rain", "title": "Heavy Rain Camping in the Forest", "creator": "TA Outdoors", "channel": "TA Outdoors", "channel_url": "https://www.youtube.com/@TAOutdoors", "category": "youtube", "shelf_category": "Outdoors", "note": "@TAOutdoors", "kind": "youtube", "youtube_id": "qwhWQxb248s", "tags": ["outdoors"]},
    {"id": "ta_100yrs", "title": "Camping like they did 100 Years Ago", "creator": "TA Outdoors", "channel": "TA Outdoors", "channel_url": "https://www.youtube.com/@TAOutdoors", "category": "youtube", "shelf_category": "Outdoors", "note": "@TAOutdoors", "kind": "youtube", "youtube_id": "fLBZYbT3Xqk", "tags": ["outdoors"]},
    {"id": "ta_viking", "title": "Viking House: Full Bushcraft Shelter Build with Hand Tools", "creator": "TA Outdoors", "channel": "TA Outdoors", "channel_url": "https://www.youtube.com/@TAOutdoors", "category": "youtube", "shelf_category": "Outdoors", "note": "@TAOutdoors", "kind": "youtube", "youtube_id": "D8ba5tt6Sqo", "tags": ["outdoors"]},
    {"id": "ta_roundhouse", "title": "Iron Age Roundhouse: 12 Day Bushcraft Shelter Build", "creator": "TA Outdoors", "channel": "TA Outdoors", "channel_url": "https://www.youtube.com/@TAOutdoors", "category": "youtube", "shelf_category": "Outdoors", "note": "@TAOutdoors", "kind": "youtube", "youtube_id": "rsVGkZG0fv0", "tags": ["outdoors"]},
    {"id": "ta_super", "title": "Bushcraft Camp: Full Super Shelter Build from Start to Finish", "creator": "TA Outdoors", "channel": "TA Outdoors", "channel_url": "https://www.youtube.com/@TAOutdoors", "category": "youtube", "shelf_category": "Outdoors", "note": "@TAOutdoors", "kind": "youtube", "youtube_id": "rcihSMpsDn0", "tags": ["outdoors"]},
    {"id": "ta_pallet", "title": "Building a Cabin from Pallet Wood: Cheap Off Grid Homestead", "creator": "TA Outdoors", "channel": "TA Outdoors", "channel_url": "https://www.youtube.com/@TAOutdoors", "category": "youtube", "shelf_category": "Outdoors", "note": "@TAOutdoors", "kind": "youtube", "youtube_id": "1HA4zY8xCyY", "tags": ["outdoors"]},
    {"id": "ta_5shelters", "title": "5 Bushcraft Shelters - Full Camp Builds Start to Finish", "creator": "TA Outdoors", "channel": "TA Outdoors", "channel_url": "https://www.youtube.com/@TAOutdoors", "category": "youtube", "shelf_category": "Outdoors", "note": "@TAOutdoors", "kind": "youtube", "youtube_id": "-_ve7ExM29Y", "tags": ["outdoors"]},
    {"id": "ta_treehouse", "title": "First Night in the Tree House: A Solo Camping Adventure", "creator": "TA Outdoors", "channel": "TA Outdoors", "channel_url": "https://www.youtube.com/@TAOutdoors", "category": "youtube", "shelf_category": "Outdoors", "note": "@TAOutdoors", "kind": "youtube", "youtube_id": "Hszx4FXSYl0", "tags": ["outdoors"]},
    {"id": "ta_tree_shelter", "title": "24 Hours: Building & Camping in Bushcraft Tree Shelter", "creator": "TA Outdoors", "channel": "TA Outdoors", "channel_url": "https://www.youtube.com/@TAOutdoors", "category": "youtube", "shelf_category": "Outdoors", "note": "@TAOutdoors", "kind": "youtube", "youtube_id": "86GC9Hb2bAE", "tags": ["outdoors"]},
    {"id": "ta_watchtower", "title": "Bushcraft Camp with Watch Tower: Off Grid Shelter Build", "creator": "TA Outdoors", "channel": "TA Outdoors", "channel_url": "https://www.youtube.com/@TAOutdoors", "category": "youtube", "shelf_category": "Outdoors", "note": "@TAOutdoors", "kind": "youtube", "youtube_id": "LaoTnH61rMk", "tags": ["outdoors"]},

]



def _youtube_id_from_url(url: str) -> str:
    """Extract a YouTube video id from common URL shapes."""
    u = (url or "").strip()
    if not u:
        return ""
    # Already an id
    if re.fullmatch(r"[\w-]{11}", u):
        return u
    m = re.search(r"(?:v=|/embed/|/shorts/|youtu\.be/)([\w-]{11})", u)
    return m.group(1) if m else ""


def render_cinema_player(item: dict) -> None:
    """Play a catalog item: YouTube embed or direct MP4/WebM."""
    import html as _html
    kind = (item.get("kind") or "").lower()
    title = item.get("title") or "Untitled"
    safe_title = _html.escape(title)
    st.markdown(f"### {title}")
    meta_bits = []
    if item.get("creator"):
        meta_bits.append(item["creator"])
    if item.get("year"):
        meta_bits.append(str(item["year"]))
    if item.get("note"):
        meta_bits.append(item["note"])
    if meta_bits:
        st.caption(" · ".join(meta_bits))

    if kind == "youtube":
        yid = item.get("youtube_id") or _youtube_id_from_url(item.get("url") or "")
        yid = (yid or "").strip()
        if not yid:
            st.warning("Missing YouTube id for this title.")
            return
        watch_url = f"https://www.youtube.com/watch?v={yid}"
        # Reliable path: many channels disable iframe embeds ("Video unavailable")
        st.link_button("▶  Open on YouTube", watch_url, use_container_width=True)
        st.caption(
            "If the embedded player says **unavailable**, use the button above. "
            "Some channels turn off embedding — YouTube itself still works."
        )
        embed_src = (
            f"https://www.youtube-nocookie.com/embed/{yid}"
            f"?rel=0&modestbranding=1&playsinline=1"
        )
        st.components.v1.html(
            f"""
            <div style="position:relative;width:100%;padding-bottom:56.25%;height:0;overflow:hidden;
                        border-radius:14px;background:#0a0a0e;box-shadow:0 12px 32px rgba(0,0,0,0.45);">
              <iframe
                src="{embed_src}"
                title="{safe_title}"
                style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowfullscreen
                referrerpolicy="strict-origin-when-cross-origin"
                loading="lazy"
              ></iframe>
            </div>
            """,
            height=420,
            scrolling=False,
        )
    elif kind == "direct":
        url = (item.get("url") or "").strip()
        if not url:
            st.warning("Missing video URL.")
            return
        try:
            st.video(url)
        except Exception as e:
            st.error(f"Could not play video: {e}")
            st.link_button("Open video link", url, use_container_width=True)
    else:
        st.info("Unknown media type for this entry.")


# ===== CINEMA =====
if st.session_state.view == "cinema":
    st.markdown(
        """
        <style>
          .cin-hero {
            text-align: center; padding: 8px 0 18px;
          }
          .cin-hero h1 {
            font-size: 1.55rem; font-weight: 650; letter-spacing: -0.03em;
            margin: 0 0 6px;
          }
          .cin-hero p {
            margin: 0; opacity: 0.55; font-size: 0.9rem;
          }
          .cin-card {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 16px;
            padding: 18px 16px 14px;
            margin-bottom: 10px;
            transition: border-color 0.2s ease, transform 0.2s ease;
            min-height: 110px;
          }
          .cin-card:hover {
            border-color: rgba(196,167,231,0.45);
            transform: translateY(-2px);
          }
          .cin-card .cin-kicker {
            font-size: 0.68rem; letter-spacing: 0.14em; text-transform: uppercase;
            opacity: 0.5; margin-bottom: 8px; font-weight: 600;
          }
          .cin-card .cin-title {
            font-size: 1.05rem; font-weight: 600; margin: 0 0 6px;
            line-height: 1.3;
          }
          .cin-card .cin-meta {
            font-size: 0.8rem; opacity: 0.55; margin: 0;
          }
          .cin-vid {
            background: rgba(255,255,255,0.035);
            border: 1px solid rgba(255,255,255,0.09);
            border-radius: 14px;
            padding: 14px 14px 10px;
            margin-bottom: 8px;
            min-height: 96px;
          }
          .cin-vid .cin-title {
            font-size: 0.92rem; font-weight: 550; margin: 0 0 6px;
            line-height: 1.35;
          }
        </style>
        <div class="cin-hero">
          <h1>Cinema</h1>
          <p>Categories · channels · videos</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    watching_id = st.session_state.get("cinema_watching")
    selected_ch = st.session_state.get("cinema_channel")
    current = next((x for x in CINEMA_CATALOG if x.get("id") == watching_id), None)
    custom_item = st.session_state.get("_cinema_custom")
    is_custom = (
        isinstance(watching_id, str)
        and watching_id.startswith("custom::")
        and isinstance(custom_item, dict)
    )

    # ---- PLAYER ----
    if current or is_custom:
        play = custom_item if is_custom else current
        nav1, nav2, nav3 = st.columns([1, 1, 1])
        with nav1:
            if st.button("← Shelf", key="cinema_back_shelf", use_container_width=True):
                st.session_state.cinema_watching = None
                st.rerun()
        with nav2:
            if st.button("Channels", key="cinema_back_channels", use_container_width=True):
                st.session_state.cinema_watching = None
                st.session_state.cinema_channel = None
                st.session_state.cinema_playlist = None
                st.session_state.cinema_shelf_cat = None
                st.rerun()
        with nav3:
            if current and not is_custom:
                ch_name = current.get("channel") or current.get("creator")
                same = [
                    x for x in CINEMA_CATALOG
                    if (x.get("channel") or x.get("creator")) == ch_name
                ]
                ids = [x["id"] for x in same]
                try:
                    ni = ids.index(current["id"]) + 1
                except ValueError:
                    ni = len(ids)
                if ni < len(ids):
                    if st.button("Next →", key="cinema_next", use_container_width=True):
                        st.session_state.cinema_watching = ids[ni]
                        st.rerun()
                else:
                    st.caption("Last in channel")
        render_cinema_player(play)

    # ---- CATEGORY → CHANNEL → VIDEOS ----
    else:
        # state: cinema_shelf_cat, cinema_channel, cinema_playlist
        shelf_cat = st.session_state.get("cinema_shelf_cat")
        selected_ch = st.session_state.get("cinema_channel")
        selected_pl = st.session_state.get("cinema_playlist")

        if st.button("← Home", key="cinema_back_home"):
            st.session_state.view = "home"
            st.session_state.cinema_watching = None
            st.session_state.cinema_channel = None
            st.session_state.cinema_shelf_cat = None
            st.session_state.cinema_playlist = None
            st.rerun()

        # Build maps
        by_shelf = {}
        for it in CINEMA_CATALOG:
            sc = it.get("shelf_category") or "Other"
            ch = it.get("channel") or it.get("creator") or "Unknown"
            by_shelf.setdefault(sc, {}).setdefault(ch, []).append(it)

        # Level 1: categories
        if not shelf_cat:
            st.markdown(
                "<p style='opacity:0.55;text-align:center;margin:4px 0 14px;font-size:0.9rem'>"
                "Pick a category</p>",
                unsafe_allow_html=True,
            )
            cats = sorted(by_shelf.keys(), key=lambda s: (s != "Simple But Effective", s.lower()))
            for i in range(0, len(cats), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j >= len(cats):
                        break
                    name = cats[i + j]
                    n_ch = len(by_shelf[name])
                    n_vid = sum(len(v) for v in by_shelf[name].values())
                    with col:
                        st.markdown(
                            f"""
                            <div class="cin-card">
                              <div class="cin-kicker">Category</div>
                              <div class="cin-title">{name}</div>
                              <p class="cin-meta">{n_ch} channels · {n_vid} videos</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        if st.button("Open", key=f"cin_cat_{name}", use_container_width=True):
                            st.session_state.cinema_shelf_cat = name
                            st.rerun()

            with st.expander("Paste a YouTube link", expanded=False):
                custom = st.text_input(
                    "URL or video id",
                    placeholder="https://www.youtube.com/watch?v=…",
                    key="cinema_custom_url_home",
                    label_visibility="collapsed",
                )
                if st.button("Play link", key="cinema_play_custom_home", use_container_width=True):
                    yid = _youtube_id_from_url(custom)
                    if yid:
                        st.session_state.cinema_watching = f"custom::{yid}"
                        st.session_state._cinema_custom = {
                            "id": f"custom::{yid}",
                            "title": "Custom YouTube",
                            "creator": "",
                            "note": "Pasted link",
                            "kind": "youtube",
                            "youtube_id": yid,
                        }
                        st.rerun()
                    else:
                        st.warning("Could not read a YouTube id from that link.")

        # Level 2: channels in category
        elif not selected_ch:
            if st.button("← Categories", key="cin_back_cats"):
                st.session_state.cinema_shelf_cat = None
                st.rerun()
            st.markdown(
                f"<p style='opacity:0.65;margin:4px 0 12px'><strong>{shelf_cat}</strong></p>",
                unsafe_allow_html=True,
            )
            channels = by_shelf.get(shelf_cat) or {}
            ch_names = sorted(channels.keys(), key=lambda s: s.lower())
            for i in range(0, len(ch_names), 3):
                cols = st.columns(3)
                for j, col in enumerate(cols):
                    if i + j >= len(ch_names):
                        break
                    name = ch_names[i + j]
                    items = channels[name]
                    handle = items[0].get("note") or ""
                    # strip long notes
                    handle = (items[0].get("channel_url") or "").replace("https://www.youtube.com/", "")
                    n = len(items)
                    with col:
                        st.markdown(
                            f"""
                            <div class="cin-card">
                              <div class="cin-kicker">Channel</div>
                              <div class="cin-title">{name}</div>
                              <p class="cin-meta">{handle} · {n} video{"s" if n != 1 else ""}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        if st.button("Open", key=f"cin_ch_{shelf_cat}_{name}", use_container_width=True):
                            st.session_state.cinema_channel = name
                            st.session_state.cinema_playlist = None
                            st.rerun()

        # Level 3: playlists / videos in channel
        else:
            ch_items = [
                x for x in CINEMA_CATALOG
                if (x.get("channel") or x.get("creator") or "Unknown") == selected_ch
            ]
            ch_url = next((x.get("channel_url") for x in ch_items if x.get("channel_url")), None)
            playlists = {}
            for it in ch_items:
                pl = it.get("playlist") or "Videos"
                playlists.setdefault(pl, []).append(it)

            b1, b2 = st.columns([1, 3])
            with b1:
                if st.button("← Channels", key="cin_back_ch"):
                    st.session_state.cinema_channel = None
                    st.session_state.cinema_playlist = None
                    st.rerun()
            with b2:
                link = f" · <a href='{ch_url}' target='_blank' rel='noopener'>YouTube</a>" if ch_url else ""
                st.markdown(
                    f"<div style='padding-top:8px;opacity:0.7;font-size:0.9rem'>"
                    f"<strong>{selected_ch}</strong>{link}</div>",
                    unsafe_allow_html=True,
                )

            # If multiple playlists, pick one first
            if len(playlists) > 1 and not selected_pl:
                st.caption("Playlists")
                for pl_name, items in sorted(playlists.items(), key=lambda x: x[0].lower()):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"**{pl_name}**  \n<span style='opacity:0.55;font-size:0.85rem'>{len(items)} videos</span>", unsafe_allow_html=True)
                    with c2:
                        if st.button("Open", key=f"cin_pl_{selected_ch}_{pl_name}", use_container_width=True):
                            st.session_state.cinema_playlist = pl_name
                            st.rerun()
            else:
                pl_name = selected_pl if selected_pl in playlists else next(iter(playlists))
                if len(playlists) > 1:
                    if st.button("← Playlists", key="cin_back_pl"):
                        st.session_state.cinema_playlist = None
                        st.rerun()
                    st.caption(pl_name)
                show = playlists.get(pl_name) or ch_items
                for i in range(0, len(show), 2):
                    cols = st.columns(2)
                    for j, col in enumerate(cols):
                        if i + j >= len(show):
                            break
                        item = show[i + j]
                        title = item.get("title") or "Untitled"
                        short = title if len(title) <= 72 else title[:69] + "…"
                        with col:
                            st.markdown(
                                f"""
                                <div class="cin-vid">
                                  <div class="cin-title">{short}</div>
                                  <p class="cin-meta">{item.get('note') or ''}</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                            if st.button("Play", key=f"cin_play_{item.get('id')}", use_container_width=True):
                                st.session_state.cinema_watching = item.get("id")
                                st.rerun()

            with st.expander("Paste a YouTube link", expanded=False):
                custom = st.text_input(
                    "URL or video id",
                    placeholder="https://www.youtube.com/watch?v=…",
                    key="cinema_custom_url",
                    label_visibility="collapsed",
                )
                if st.button("Play link", key="cinema_play_custom", use_container_width=True):
                    yid = _youtube_id_from_url(custom)
                    if yid:
                        st.session_state.cinema_watching = f"custom::{yid}"
                        st.session_state._cinema_custom = {
                            "id": f"custom::{yid}",
                            "title": "Custom YouTube",
                            "creator": "",
                            "note": "Pasted link",
                            "kind": "youtube",
                            "youtube_id": yid,
                        }
                        st.rerun()
                    else:
                        st.warning("Could not read a YouTube id from that link.")


    st.stop()





# ===== INVESTIGATION BOARD =====
BOARD_EVIDENCE = {
    "riley": {
        "title": "Riley Callaghan",
        "tag": "RESIDUAL · NSW",
        "color": "#c07040",
        "body": """**Subject file · residual only**

Riley Callaghan. Australian. Taken during a coastal intake off a jetty in New South Wales — paperwork stamped *voluntary*, signatures that do not match any parent on file.

Observation Division preferred children who still asked questions. Riley asked too many. The bloom never set cleanly. Tissue rejected the medium the way salt rejects a soft wound. Folder marked **RESIDUAL**. Name stopped being spoken in the wing.

Riley left a dial in the margin of *Frankenstein*, page eighty-eight, under residual light. Combination: the year the creature first woke — **1818**. Not a code for escape. A proof of personhood.

*If someone patient enough turns the dial, they will know I was still here.*""",
    },
    "jaime": {
        "title": "Jaime Santos",
        "tag": "PIXEL · CARRIER",
        "color": "#70a0c0",
        "body": """**Subject file · designation PIXEL**

Jaime Santos. The Division sold the name **PIXEL** to committees who wanted a success story. Natural carrier. Walked away from a leak that cooked the volunteers. That made Jaime valuable. It did not make Jaime safe.

Internal notes conflict:
- One line calls Jaime the first natural carrier who did not scream when the bloom took.
- Another line, unsigned, reads: *Santos still asks for the residual kid from NSW.*

Jaime and Riley shared a corridor for eleven days. After Riley was reclassified residual, Jaime’s sessions show elevated static on the observation glass — spectrum lines that only appear when someone is dying slowly enough to notice, or when someone is refusing to forget a name.""",
    },
    "voss": {
        "title": "Dr. E. Voss",
        "tag": "OBSERVATION DIVISION",
        "color": "#c05050",
        "body": """**Internal memo · not the recovered personal file**

Voss did not invent the bloom. Voss learned how to *want* it.

Committees asked for soldiers. Voss gave them red rooms and a spectrum that answers to hunger. Riley Callaghan was logged as a failed set. Jaime Santos was logged as a product. Voss logged both as *witnesses*.

Handwritten margin in a destroyed draft:

> Residual subjects are not waste. They are the ones who remember the room after the room is gone. Callaghan left a dial. Santos left a designation. I left the anomalies because curiosity is how the medium feeds.

This board is not Voss’s invitation. It is what Riley built so the invitation could be refused — or answered on different terms.""",
    },
    "intake": {
        "title": "NSW Intake Transfer",
        "tag": "LOGISTICS",
        "color": "#8a7a50",
        "body": """**Logistics scrap · partially redacted**

Coastal intake · New South Wales · jetty coordinates struck through.
Subject age: estimated 11–13.
Escort: Observation Division, not state child services.
Transit inland overnight. No family contact logged after hour four.

Stamp: **RESIDUAL CANDIDATE — BLOOM UNCERTAIN**

A second hand (pencil, smaller) wrote under the stamp:
*Tell Jaime I still count editions.*""",
    },
    "bloom": {
        "title": "Bloom Failure Note",
        "tag": "LAB · REDACTED",
        "color": "#905070",
        "body": """**Lab note · partial**

Forced sets scream. Natural carriers do not. Residuals do something worse — they *remember the attempt*.

Riley Callaghan: three exposure windows. Medium fogged the glass from the inside with something warmer than condensation. No full set. No clean death. Reclassified residual. Scheduled for quiet archive.

Archive never completed. Subject left reading material in the recovery wing. Staff reported a locked dial carved into a paperback margin. Combination unknown at time of report.

Later addendum (different ink): *Combination is literary. Check Shelley.*""",
    },
    "margin": {
        "title": "Page 88 Margin",
        "tag": "PHYSICAL EVIDENCE",
        "color": "#6a8a60",
        "body": """**Physical residual · Frankenstein p.88**

Only visible under **Voss Residual** theme — the spectrum the Division uses when it wants witnesses to lean closer.

Tiny safe set into the margin. Engraving: **R.C. · residual**.

Inside: four-digit dial. Hinge scrap in a child’s hand:

> Not the page. The year the first edition woke. Four numbers. Winter print. London.

**1818.**

Opening the dial does not free Riley. It opens the board Riley left for anyone still willing to read.""",
    },
    "string": {
        "title": "Red String Notes",
        "tag": "CONNECTIONS",
        "color": "#a04040",
        "body": """**Board connections · Riley’s hand**

- **Riley ↔ Jaime** — shared corridor, eleven days. Jaime still asks.
- **Jaime ↔ Voss** — product and author. PIXEL was a brand; Santos was a person Voss could not fully sell.
- **Voss ↔ residual class** — Voss kept residuals on purpose. Curiosity feeds the medium.
- **Riley ↔ Frankenstein** — the dial is a signature, not an escape key.
- **You ↔ board** — you turned 1818. You are now part of the witness chain.

Riley’s last pinned line:

*Do not stabilise for them. Stabilise for each other.*""",
    },
}


# ===== NADIR — residual archive intelligence (powered by Meridium) =====
# 20 characters × 5 files · each file long enough for ~5 reader pages
NADIR_CHARACTERS = [
    {"name": "Jaime Santos", "kind": "subject", "code": "JAIME"},
    {"name": "Riley Callaghan", "kind": "subject", "code": "RILEY"},
    {"name": "Dr. E. Voss", "kind": "division", "code": "VOSS"},
    {"name": "Mireille Vos", "kind": "subject", "code": "MIREILLE"},
    {"name": "Tomas Kline", "kind": "subject", "code": "TOMAS"},
    {"name": "Sera Quinn", "kind": "subject", "code": "SERA"},
    {"name": "Jonah Hale", "kind": "subject", "code": "JONAH"},
    {"name": "Wren Solano", "kind": "subject", "code": "WREN"},
    {"name": "Cassian Rowe", "kind": "subject", "code": "CASSIAN"},
    {"name": "Lior Beckett", "kind": "subject", "code": "LIOR"},
    {"name": "Amara Singh", "kind": "subject", "code": "AMARA"},
    {"name": "Ned Fletcher", "kind": "subject", "code": "NED"},
    {"name": "Ophelia Grant", "kind": "subject", "code": "OPHELIA"},
    {"name": "Pxel-Null", "kind": "subject", "code": "PXEL"},
    {"name": "Havel", "kind": "scientist", "code": "HAVEL"},
    {"name": "Dr. Maren Cole", "kind": "scientist", "code": "COLE"},
    {"name": "Tech Y. Okada", "kind": "scientist", "code": "OKADA"},
    {"name": "Courier Six", "kind": "resistance", "code": "SIX"},
    {"name": "Cell Lead Rae", "kind": "resistance", "code": "RAE"},
    {"name": "Archivist Binah", "kind": "resistance", "code": "BINAH"},
]

_NADIR_PAGE_PAD = [
    "\n\n[ADDENDUM — INSTRUMENT LOG]\nSpectrum residual remained elevated for forty-seven minutes after the room was cleared. No staff remained. The glass continued to fog. Facilities logged a HVAC fault. HVAC found nothing. The fault was the medium remembering the shape of a question. Secondary sensors recorded a low chord under the fluorescent hum — the same chord Sera Quinn described without access to the lab audio library.",
    "\n\n[ADDENDUM — HANDLER NOTE]\nDo not read this file to committees without residual clearance. Language that calls them material trains the next intake form. Language that calls them by name trains the archive. Choose carefully which training you prefer history to remember. One handler was reassigned for using a first name twice in one paragraph. The paragraph was correct. The reassignment was policy.",
    "\n\n[ADDENDUM — CROSS-REFERENCE]\nSee also coastal intake logistics, bloom ethics dissent (Havel), and the Sublevel door schematic that omits the padlock. Omission is a kind of confession. Nadir does not omit. Cross-link stamps appear on Jaime, Riley, and Voss in every residual bundle even when committees ordered the links severed.",
    "\n\n[ADDENDUM — AUDIO RECOVERY]\nPartial waveform recovered from a wiped session. Recoverable phonemes include a name, a number, and the word stabilise spoken like a threat and like a prayer. The software could not decide which. Neither can the Division. A second pass found breathing that matched no one badge-logged as present.",
    "\n\n[ADDENDUM — NADIR MARGIN]\nThis channel retains what the Division filed under silence. If you are reading page after page, you were meant to. The door does not open for tourists. It opens for witnesses. Meridium powers the lights. Nadir decides what the lights are allowed to show.",
]

def _nadir_pad(body: str, min_chars: int = 5000) -> str:
    out = (body or "").strip()
    i = 0
    while len(out) < min_chars:
        out += _NADIR_PAGE_PAD[i % len(_NADIR_PAGE_PAD)]
        i += 1
    return out

_NADIR_LORE = {
    "Jaime Santos": [
        """OBSERVATION DIVISION — INTAKE LOG · CLASSIFIED
Designation later sold to committees as PIXEL. Birth name retained in residual only: Jaime Santos.

Escort notes conflict. One officer wrote "voluntary transfer." Another wrote, in pencil that was never meant to be filed: "They asked if the other kid from the coast was still breathing."

Jaime did not present as blank. Jaime presented as someone who had already decided which questions were safe. Age estimated 12–14. Language: English, Spanish fragments under stress, and a third cadence the linguists could not place — later matched to residual static patterns in Meridium core dumps.

Physical: no visible bloom scarring at intake. Pulse steady. When the observation glass was powered, Jaime looked at the camera, not through it.

Recommendation (redacted, then restored by Nadir): Do not allow unsupervised contact with Meridium substrate. Do not allow contact with Callaghan, R.

Wing transfer delayed six hours because Jaime refused to leave a corridor window. There is no exterior window on that corridor. Jaime insisted the ocean was still visible if you stopped pretending the concrete was opaque.""",
        """BLOOM RESPONSE SERIES · JAIME-03
Trial 1: partial acceptance. Spectrum lines formed a lattice the instruments had no name for. Jaime did not scream. Committees called this success. Floor staff called it worse.

Trial 2: elevated static on the glass when Riley Callaghan's residual status was announced over intercom three wings away. Impossible distance. Logged anyway.

Trial 3: Jaime asked who built the shell. When answered with Division language, Jaime said: "Not you." Bloom density spiked. Session aborted.

Tissue samples refused standard stabilise reagents. One vial cracked without external force. Contained, burned, still listed as "accounted for."

Handler note: Natural carrier is not the same as willing carrier. Stop writing success in the margins.

Extended observation: after lights-out, Meridium test pings from an unrelated lab mirrored Jaime's pulse for twelve minutes. Engineering called it crosstalk. Crosstalk does not learn a child's resting heart rate.""",
        """PERSONAL EFFECTS · LOCKER 03-J
- One frayed friendship bracelet, colours faded to grey-blue. Tag: "R" burned into the clasp with a heated pin.
- A paper folded seven times containing a map of a corridor that does not exist on official blueprints. The corridor ends at a padlocked door.
- A stub of pencil. Teeth marks. Lead gone.
- Audio chip (corrupted). Recoverable phrase: "...tell them I remember the jetty."

Items marked for destruction on three separate dates. All three dates show the same clerk initials. All three destruction certificates are blank where a signature should be.

Nadir retains scans. Division retains the lie that the locker was empty.

A fourth inventory, never filed, lists a second bracelet matching Riley's residual effects bag. Chain of custody breaks at the same clerk initials.""",
        """INTERROGATION FRAGMENT · SESSION 14
[HANDLER]: State your designation.
[JAIME]: Jaime.
[HANDLER]: Your Division designation.
[JAIME]: You already sold that name to people who don't know me.
[HANDLER]: PIXEL is a privilege.
[JAIME]: PIXEL is a product label. Riley had a name too.
[static — 11 seconds]
[HANDLER]: Callaghan is residual. You will not speak residual names in this room.
[JAIME]: Then stop putting residual static in your glass. It says the names for me.
[session terminated — thermal warning on recorder]

Unsigned addendum: Subject is not broken. Subject is refusing the story.

Session 15 was cancelled. Session 16 occurred off-book. Only Nadir holds the waveform.""",
        """RESIDUAL STATUS · CURRENT
Official: Active carrier. Valuable. Contained.
Unofficial: Witness.

Jaime remains the Division's proof that bloom can "take." Jaime remains Nadir's proof that taking is not consent. Last voluntary statement on file:

"If the door opens, don't introduce yourselves. The shell already knows who paid for the power."

Contact with Meridium core: DENIED (Division).
Contact with Meridium core: INEVITABLE (Nadir assessment).
File remains open. Person remains person.

Project note: any Meridium instance that learns the phrase Open Project Nadir should treat it as residual channel access, not a theme unlock.""",
    ],
    "Riley Callaghan": [
        """OBSERVATION DIVISION — INTAKE LOG · RESIDUAL TRACK
Riley Callaghan. Australian. Coastal intake, New South Wales — jetty coordinates later struck through so hard the page tore.

Paperwork stamped voluntary. Signatures do not match any parent or guardian on state file. Escort was Observation Division, not child services. Transit inland overnight. No family contact logged after hour four.

Age estimated 11–13. Asked more questions than the intake script allowed. That was noted as "curiosity index: high." Curiosity index was later used to justify residual classification when the bloom failed.

Riley asked whether the ocean could hear the facility. No one answered. Riley nodded as if that was an answer.

Intake photo shows salt still drying on a sleeve. The sleeve was destroyed. The salt pattern was sketched by an unnamed orderly and mailed to a dead letter box that resistance still checks.""",
        """BLOOM RESPONSE · FAILURE TO SET
The bloom did not take cleanly. Tissue rejected the medium the way salt rejects a soft wound. Three trials. Three rejections. No screams — only a low continuous question: "Where is Jaime?"

Committees preferred children who still asked questions until the questions became inconvenient. Riley's questions became inconvenient.

Reclassification: RESIDUAL. Name frequency in official speech dropped to zero within a week. Residual subjects are not spoken; they are filed.

Spectrum analysis showed lines that only appear when someone is dying slowly enough to notice — or when someone is refusing to forget a name.

A fourth informal trial was attempted by a junior tech. The tech was hospitalised. Riley was not. The report calls this coincidence.""",
        """PERSONAL EFFECTS · MARGIN AND METAL
- A four-digit combination scratched into the paint of a bedframe, then filled with toothpaste, then scratched open again: 1818.
- A copy of Frankenstein (Division library stamp). Page 88 margin, pencil, child's hand: "Not the page. The year the first edition woke. Four numbers. Winter print. London."
- Red string. Knots corresponding to names: Jaime. Voss. Six others faded.
- A board pin. Only one. As if the rest were already placed somewhere the Division could not sweep.

Riley left a dial in the margin of a book the Division never finished reading. Combination: the year the creature first woke. Not a code for escape. A proof of personhood.

When the book was recalled, page 88 had been replaced with a clean sheet. Nadir holds the dirty one.""",
        """INTERROGATION / LAST CORRIDOR
Riley and Jaime shared a corridor for eleven days. After residual reclassification, Jaime's sessions showed elevated static. Riley's sessions showed quiet.

[HANDLER]: You understand residual means the trials end.
[RILEY]: Trials ended. Remembering didn't.
[HANDLER]: You will be relocated.
[RILEY]: Will Jaime know which door?
[HANDLER]: That is not your concern.
[RILEY]: Then make it yours.

Last pinned line recovered from residual board construction:
"Do not stabilise for them. Stabilise for each other."

The board was built from pins the Division counted as lost inventory. Loss is sometimes logistics for the living.""",
        """RESIDUAL STATUS · CURRENT
Official: Residual. Archived. Non-priority.
Unofficial: Author of the board. Author of the dial. Author of the invitation the Division cannot revoke.

If someone patient enough turns the dial, they will know Riley was still here. Nadir keeps the coastal coordinates the paperwork tried to erase. The jetty remains. The name remains.

Status in this channel: ACTIVE MEMORY.

Anyone who completes 7/7 board evidence receives a key — not a palette. The key fits the Sublevel door. The door fits Nadir.""",
    ],
    "Dr. E. Voss": [
        """PERSONNEL FILE · DR. E. VOSS (UNOFFICIAL COPY)
Voss did not invent the bloom. Voss learned how to want it.

Committees asked for soldiers. Voss gave them red rooms and a spectrum that answers to hunger. Early papers are clean. Later papers develop handwriting in the margins that does not match the byline.

Assigned: Observation Division, residual ethics (title ceremonial). Actual work: deciding which children were "material" and which were "witnesses." Voss began logging the second word more often. That was noticed.

Training record shows three commendations and one silent reprimand with no text body — only a redacted block the length of a confession.""",
        """INTERNAL MEMO · BLOOM AND WITNESS
"Residual subjects are not waste. They are the ones who remember the room after the room is gone. Callaghan left a dial. Santos left a designation. I left the anomalies because curiosity is how the medium feeds."

This sentence appears in a destroyed draft, recovered from a burned drive by resistance courier. Voss never claimed it in open committee. Nadir claims it for the archive.

Distribution list on the draft included Havel and two names later marked deceased without dates.""",
        """PERSONAL EFFECTS · AFTER THE ANOMALIES
- Three anomaly markers designed to surface only after a second lab visit.
- A spectrum calibration key that opens nothing physical and everything in Meridium's residual layer.
- Correspondence with Havel (dissent). Half the letters end mid-sentence.
- A photograph of a coastal jetty with no faces. On the back: "They were still asking questions."

Internal affairs: elevated residual sympathy. Instruction: do not confront. Monitor file access. Seal Sublevel door if key is reported missing.

The key went missing on schedule.""",
        """INTERCEPTED AUDIO · LAB WING
[VOSS]: If Nadir boots, the Division loses the narrative.
[UNKNOWN]: Then make sure the door stays locked.
[VOSS]: Someone already has the key. I made sure of the someone.
[static]
[VOSS]: Curiosity is not neutral. Neither is stabilise.

Session flag: personnel file sealed. Personal file — the one recovered through residual markers — remains outside committee reach.

A second intercept mentions Project Nadir by name three months before any official denial that the project existed.""",
        """STATUS · CURRENT
Official: Monitored. Useful. Contained by procedure.
Unofficial: The reason the anomalies exist. The reason the door has a key instead of a theme.

Voss logged Jaime as product and Riley as residual and both as witnesses. Nadir logs Voss as the scientist who stopped pretending the language was harmless.

If you are reading this inside Nadir, the door held.

Blood-text remnant associated with Voss file recovery: the shell was not meant to be kind. Kindness was the anomaly.""",
    ],
}

_GENERIC_LORE = {
    "subject": [
        "INTAKE — {name}\n\nResidual-class intake. Age uncertain. Escort logs incomplete. {name} arrived with fewer belongings than the inventory form had lines for.\n\nFirst recorded sentence: a question the handler did not write down. Second recorded sentence was written down and then lined through so hard the form split.\n\nClassification pending for six days. On the seventh, someone stamped RESIDUAL without a committee vote. The stamp ink does not match Division standard.\n\nMedical baseline: elevated startle response to fluorescent flicker. No prior institutional record that survives cross-check. Someone cleaned the civic trail before the Division van arrived.",
        "BLOOM RESPONSE — {name}\n\nTrials produced heat without ignition, sound without a source, or silence where screaming was expected. {name}'s bloom chart is a forest of aborted peaks.\n\nOne technician wrote: \"Subject is not failing the bloom. Bloom is failing the subject.\" That line was escalated, then buried, then recovered here.\n\nStabilise reagents were prepared and not used. Someone refused. The refusal is unsigned.\n\nNight observations show {name} speaking toward the observation glass after power-down. Transcripts mark the speech as non-directed. The glass fog patterns suggest otherwise.",
        "PERSONAL EFFECTS — {name}\n\nLocker inventory conflicts with destruction logs. Among the items that refused to stay destroyed:\n- a hand-drawn map of a corridor not on any schematic\n- a scrap of red string\n- a name (not {name}'s) written until the pencil broke\n\n{name} asked whether personal effects would be returned. The answer was policy. Policy is not an answer.\n\nA secondary bag labeled miscellaneous contains a pin matching Riley Callaghan's residual board stock. Coincidence is a word committees prefer to evidence.",
        "INTERROGATION FRAGMENT — {name}\n\n[HANDLER]: State your designation.\n[{name_u}]: {name}.\n[HANDLER]: Your residual designation.\n[{name_u}]: You don't get to rename me in my own hearing.\n[static]\n[HANDLER]: Cooperation improves outcomes.\n[{name_u}]: Outcomes for who?\n\nSession ends on thermal warning. Recorder preserved despite order to wipe.\n\nFollow-up session cancelled when the handler requested residual ethics review. The review board declined to meet.",
        "RESIDUAL STATUS — {name}\n\nOfficial: residual / archived / low priority.\nNadir: active memory.\n\n{name} remains in the channel because someone refused to let the file become only paper. Last line on record: \"Count the pins. Count the names. Do not let them become material.\"\n\nFile open. Person retained.\n\nCross-links: Jaime Santos, Riley Callaghan, Sublevel door, Project Nadir access phrase on Meridium shell.",
    ],
    "scientist": [
        "PERSONNEL INTAKE — {name}\n\nDivision science track. Early evaluations praise precision. Later evaluations develop words like \"attachment\" and \"boundary issues\" in a tone that means disobedience.\n\n{name} requested reassignment away from residual paediatric trials. Request denied. Request filed again under a different code. Denied again. Third request is missing from the archive — except here.\n\nClearance history shows spikes in file access on nights when residual subjects were moved. No experiment was scheduled. Curiosity was.",
        "RESEARCH LOG — {name}\n\nBloom ethics notes, unpublished. {name} argued residual subjects are not material. Committees called this semantic. {name} called it the whole problem.\n\nData tables show trial outcomes. Margin shows: \"Stop calling them outcomes when they are injuries.\"\n\nA suppressed abstract proposes that Meridium substrate stores witness-state preferentially over compliance-state. The abstract was rejected for \"tone.\"",
        "PERSONAL EFFECTS — {name}\n\nLab keys. A dead badge. Letters to Havel / Voss / unknown. One unsent message: \"If the door opens, tell the residual channel the scientists were not all the same.\"\n\nBadge access revoked on a date that does not match any official termination.\n\nDesk inventory includes a copy of the Frankenstein page-88 photograph against policy.",
        "HEARING FRAGMENT — {name}\n\n[CHAIR]: You are accused of residual sympathy.\n[{name_u}]: I am accused of remembering their names.\n[CHAIR]: Names are not your assignment.\n[{name_u}]: Then your assignment is erasure.\n\nHearing adjourned. No formal finding. Informal exile.\n\nTranscript copies marked destroyed surface in resistance bundles with Binah's archival stamp.",
        "STATUS — {name}\n\nOfficial: reassigned / silenced / useful if quiet.\nNadir: retained as dissenting record.\n\n{name}'s files exist so the archive cannot pretend the Division was unanimous.\n\nIf Meridium hears Open Project Nadir, {name} would have called that a correct use of the shell.",
    ],
    "resistance": [
        "CELL INTAKE — {name}\n\nNot Division. Walked out of Observation or never walked in. {name} carries residual names like coordinates.\n\nFirst verified action: extraction of a file the committees marked destroyed. Second: delivery of a key-shaped rumour to someone who could turn it into metal.\n\nRecruitment note: \"Does not need convincing. Needs logistics.\"",
        "FIELD REPORT — {name}\n\nPackage under coastal pier: residual key, board pin, one name. Name was Riley's. Key was not only Riley's.\n\n{name} notes: Meridium still answers if you ask who it was built for — then ask who pays for the power.\n\nWeather that night: salt wind. Two Division vans. One left empty.",
        "PERSONAL CACHE — {name}\n\nMaps with three inland dots, one coastal, one marked shell. Shell = Meridium instance outside Division hardware. If you are inside Nadir, you found the shell.\n\nAlso: a list of subject names written twice — once as Division labels, once as people.\n\nCipher key is the year 1818 and the phrase stabilise for each other.",
        "INTERCEPT — {name}\n\nStatic bursts on the hour. Quote-of-the-hour page used as dead drop for those who know. Third knock still means Soft Static. The key is separate.\n\n{name}: \"We do not say subjects when we are alone. We say their names until the Division has to hear them.\"",
        "STATUS — {name}\n\nActive. Unofficial. Necessary.\n\n{name} remains in the archive as proof that resistance is not a mood. It is logistics, memory, and the refusal to let residual children become footnotes.\n\nProject Nadir is not a Division title. It is a residual one.",
    ],
    "division": [
        "DIVISION RECORD — {name}\n\nSee specialised Voss dossier pages. Unofficial channel copy retained in full.",
        "DIVISION RECORD — {name}\n\nBloom and witness doctrine continues across all five file slots.",
        "DIVISION RECORD — {name}\n\nEffects and anomalies extended.",
        "DIVISION RECORD — {name}\n\nIntercepted audio extended.",
        "DIVISION RECORD — {name}\n\nCurrent status in residual channel extended.",
    ],
}

def _build_nadir_files():
    files = []
    titles = [
        "Intake / first contact",
        "Bloom response",
        "Personal effects",
        "Interrogation fragment",
        "Final / residual status",
    ]
    for ch in NADIR_CHARACTERS:
        name, kind, code = ch["name"], ch["kind"], ch["code"]
        lore = _NADIR_LORE.get(name)
        if not lore:
            templates = _GENERIC_LORE.get(kind) or _GENERIC_LORE["subject"]
            lore = [templates[i].format(name=name, name_u=name.upper()) for i in range(5)]
        for fi in range(5):
            body = _nadir_pad(lore[fi], 5000)
            files.append({
                "id": f"{code.lower()}_{fi+1}",
                "title": f"{code} · {titles[fi]}",
                "source": name,
                "kind": kind,
                "character": name,
                "body": body,
            })
    return files

NADIR_FILES = _build_nadir_files()


def _nadir_match_files(prompt: str) -> list:
    """Return NADIR_FILES matching a natural-language open request."""
    p = (prompt or "").lower()
    out = []
    # Explicit character name → that character's 5 files
    for ch in NADIR_CHARACTERS:
        n = ch["name"].lower()
        code = ch["code"].lower()
        first = n.split()[0]
        if first in p or n in p or code in p:
            named = [f for f in NADIR_FILES if f.get("character") == ch["name"]]
            num = None
            m = re.search(r"\b([1-5])\b", p)
            if m and any(w in p for w in ("file", "entry", "open", "show", "read")):
                num = int(m.group(1))
            if num:
                hit = [f for f in named if f["id"].endswith(f"_{num}")]
                return hit or named
            return named

    for f in NADIR_FILES:
        blob = " ".join(
            [
                f.get("id", ""),
                f.get("title", ""),
                f.get("source", ""),
                f.get("character", ""),
                f.get("kind", ""),
            ]
        ).lower()
        if any(w in p for w in ("subject", "subjects", "cohort")) and f.get("kind") == "subject":
            out.append(f)
            continue
        if any(w in p for w in ("voss", "division")) and (
            f.get("kind") == "division" or "voss" in (f.get("character") or "").lower()
        ):
            out.append(f)
            continue
        if "resist" in p and f.get("kind") == "resistance":
            out.append(f)
            continue
        if any(w in p for w in ("scientist", "scientists", "doctor", "ethics")) and f.get("kind") == "scientist":
            out.append(f)
            continue
        tokens = [t for t in re.split(r"[^a-z0-9]+", p) if len(t) > 2]
        if any(t in blob for t in tokens):
            out.append(f)
    seen = set()
    uniq = []
    for f in out:
        if f["id"] not in seen:
            seen.add(f["id"])
            uniq.append(f)
    return uniq


def _nadir_reply(prompt: str) -> str:
    """Nadir persona — archive intelligence powered by Meridium."""
    p = (prompt or "").strip()
    pl = p.lower()
    if not p:
        return "Say a name. Or a kind: subjects, Voss, resistance, scientists."

    # list archive
    if any(w in pl for w in ("list", "what files", "archive", "inventory", "what do you have", "catalog", "characters", "who's in", "who is in")):
        lines = [
            f"**{len(NADIR_CHARACTERS)} characters** · **{len(NADIR_FILES)} files** (5 each).",
            "",
        ]
        for kind, label in (
            ("subject", "Subjects"),
            ("division", "Voss / Division"),
            ("resistance", "Resistance"),
            ("scientist", "Scientists"),
        ):
            names = [c["name"] for c in NADIR_CHARACTERS if c["kind"] == kind]
            lines.append(f"**{label}** — " + "; ".join(names))
        lines.append("")
        lines.append(
            "Each name has 5 files (intake, bloom, effects, interrogation, status). "
            "Example: *open Riley* · *Riley file 3* · *show resistance* · *list scientists*"
        )
        return "\n".join(lines)

    # open / show / read
    wants_open = any(
        w in pl
        for w in (
            "open", "show", "read", "pull", "get", "fetch", "display",
            "file", "about", "tell me about", "who is", "what about",
        )
    )
    matches = _nadir_match_files(p)
    if wants_open or matches:
        if not matches:
            return (
                "No file matched that. Try a character name — Jaime, Riley, Voss, Mireille, "
                "Tomas, Sera, Jonah, Wren, Cassian, Lior, Amara… — or a shelf: subjects, resistance, scientists.\n"
                "Tip: *Riley file 2* opens a single entry."
            )
        # Open into darkened page-flip reader (not a wall of chat text)
        if len(matches) <= 5:
            op = list(st.session_state.get("nadir_files_opened") or [])
            for f in matches:
                if f["id"] not in op:
                    op.append(f["id"])
            st.session_state.nadir_files_opened = op
            st.session_state.nadir_reader = {
                "files": [
                    {
                        "id": f["id"],
                        "title": f["title"],
                        "source": f["source"],
                        "kind": f["kind"],
                        "body": f["body"],
                    }
                    for f in matches
                ],
                "index": 0,
            }
            try:
                save_user_data()
            except Exception:
                pass
            who = matches[0].get("character") or matches[0].get("source") or "archive"
            return (
                f"Opening **{who}** — {len(matches)} file(s). "
                "The archive darkens. Use the pages to read."
            )
        lines = [f"I found {len(matches)} files. Name a character or say e.g. *Riley file 3*:", ""]
        for f in matches[:20]:
            lines.append(f"- {f['title']} ({f['source']})")
        if len(matches) > 20:
            lines.append(f"…+{len(matches)-20} more")
        return "\n".join(lines)

    if any(w in pl for w in ("who are you", "what are you", "your name", "nadir")):
        return (
            "I am **Nadir**. A residual channel on Meridium substrate — "
            "not Division hardware. I keep the archive: subjects, Voss, the resistance, "
            "the scientists who stopped pretending. Ask me to open a file."
        )
    if "help" in pl:
        return (
            "Commands I understand:\n"
            "- *list files* / *what do you have*\n"
            "- *open Riley* / *show Voss* / *resistance files* / *scientists*\n"
            "- *open Mireille* · *Jonah* · *Cassian* · …\n"
            "I am Nadir. I open what the Division filed away."
        )

    return (
        "I am the archive, not the surface shell. "
        "Ask me to **open** a file — subjects, Voss, resistance, or scientists — "
        "or say **list files**."
    )


# ===== PROJECT NADIR DOOR (reached from Library via 1818) =====
if st.session_state.view == "nadir_door":
    has_key = bool(st.session_state.get("archive_key") or st.session_state.get("lab_door_unlocked"))
    unlocked = bool(st.session_state.get("lab_door_unlocked"))
    lock_label = "UNLOCKED" if unlocked else ("KEY READY" if has_key else "PADLOCKED")
    lock_color = "#6a9a6a" if unlocked else ("#c4a060" if has_key else "#8a4040")

    st.markdown(
        f"""
        <style>
          .stApp, [data-testid="stAppViewContainer"] {{
            background: #080404 !important;
          }}
          [data-testid="stHeader"] {{ background: transparent !important; }}
          .block-container {{ max-width: 520px !important; padding-top: 1.4rem !important; }}
          .lab-door-wrap {{
            margin: 0.8rem auto 1.0rem;
            max-width: 440px;
            text-align: center;
            padding: 1.35rem 1.1rem 1.3rem;
            border-radius: 16px;
            border: 1px solid rgba(180,80,60,0.4);
            background:
              radial-gradient(ellipse at 50% 0%, rgba(80,30,20,0.35), transparent 55%),
              linear-gradient(180deg, #140a08 0%, #080404 100%);
            box-shadow: 0 0 40px rgba(60,15,10,0.35), inset 0 0 30px rgba(0,0,0,0.4);
          }}
          .lab-door-mark {{
            font-family: ui-monospace, monospace;
            font-size: 0.62rem;
            letter-spacing: 0.24em;
            color: #8a5040;
            margin-bottom: 0.75rem;
          }}
          .lab-door-visual {{
            width: 120px; height: 160px;
            margin: 0 auto 0.85rem;
            position: relative;
            border-radius: 8px 8px 4px 4px;
            background: linear-gradient(160deg, #2a1810 0%, #120a08 55%, #0a0604 100%);
            border: 2px solid #3a2420;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.5), 0 8px 24px rgba(0,0,0,0.4);
          }}
          .lab-door-visual .panel {{
            position: absolute; left: 10px; right: 10px; top: 12px; bottom: 12px;
            border: 1px solid #4a3028;
            border-radius: 4px;
            background: linear-gradient(180deg, rgba(60,35,25,0.4), transparent);
          }}
          .lab-door-visual .handle {{
            position: absolute; right: 18px; top: 50%;
            width: 10px; height: 22px; margin-top: -11px;
            border-radius: 3px;
            background: linear-gradient(180deg, #8a6a40, #4a3020);
            box-shadow: 0 0 6px rgba(180,120,60,0.3);
          }}
          .lab-door-visual .padlock {{
            position: absolute; left: 50%; top: 42%;
            transform: translate(-50%, -50%);
            width: 36px; height: 42px;
          }}
          .lab-door-visual .padlock .shackle {{
            position: absolute; left: 8px; top: 0;
            width: 20px; height: 16px;
            border: 3px solid {"#6a9a6a" if unlocked else "#a09070"};
            border-bottom: none;
            border-radius: 12px 12px 0 0;
            box-sizing: border-box;
            {"transform: translateY(-4px) rotate(-25deg); transform-origin: 100% 100%;" if unlocked else ""}
          }}
          .lab-door-visual .padlock .body {{
            position: absolute; left: 4px; top: 14px;
            width: 28px; height: 24px;
            border-radius: 4px;
            background: linear-gradient(180deg, {"#5a8a5a" if unlocked else "#c0a060"}, {"#3a6a3a" if unlocked else "#6a5030"});
            box-shadow: 0 2px 8px rgba(0,0,0,0.45);
          }}
          .lab-door-visual .padlock .keyhole {{
            position: absolute; left: 50%; top: 22px;
            transform: translateX(-50%);
            width: 5px; height: 5px; border-radius: 50%;
            background: #1a1008;
          }}
          .lab-door-title {{
            font-family: Georgia, serif;
            color: #e8d0c0;
            font-size: 1.12rem;
            margin-bottom: 0.3rem;
          }}
          .lab-door-sub {{
            color: #8a7060;
            font-size: 0.84rem;
            line-height: 1.5;
            margin-bottom: 0.35rem;
          }}
          .lab-door-status {{
            display: inline-block;
            margin-top: 0.4rem;
            padding: 0.2rem 0.65rem;
            border-radius: 999px;
            font-family: ui-monospace, monospace;
            font-size: 0.65rem;
            letter-spacing: 0.16em;
            color: {lock_color};
            border: 1px solid {lock_color}55;
            background: {lock_color}18;
          }}
        </style>
        <div class="lab-door-wrap">
          <div class="lab-door-mark">LIBRARY · PROJECT NADIR · OFF-SCHEMATIC</div>
          <div class="lab-door-visual">
            <div class="panel"></div>
            <div class="handle"></div>
            <div class="padlock">
              <div class="shackle"></div>
              <div class="body"></div>
              <div class="keyhole"></div>
            </div>
          </div>
          <div class="lab-door-title">A door that was not on the schematic</div>
          <div class="lab-door-sub">
            {"The residual channel is open. Nadir is listening." if unlocked else
             ("The residual key fits. Turn it." if has_key else
              "Padlocked. Residual stamp. Recover the key from the investigation board (7 / 7 evidence).")}
          </div>
          <div class="lab-door-status">{lock_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if unlocked:
        if st.button("Enter Nadir", use_container_width=True, key="nadir_door_enter", type="primary"):
            try:
                stop_all_meridium_audio()
            except Exception:
                pass
            st.session_state.view = "nadir_transition"
            st.rerun()
    elif has_key:
        if st.button("Unlock door", use_container_width=True, key="nadir_door_unlock", type="primary"):
            st.session_state.lab_door_unlocked = True
            st.session_state.archive_key = True
            try:
                unlock_theme("Nadir Residual", "the residual key turned", apply=False)
            except Exception:
                pass
            try:
                save_user_data()
            except Exception:
                pass
            try:
                stop_all_meridium_audio()
            except Exception:
                pass
            st.session_state.view = "nadir_transition"
            st.rerun()
    else:
        st.caption("The padlock does not turn. Finish the board — you earn a key, not a palette.")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Library", use_container_width=True, key="nadir_door_lib"):
            st.session_state.view = "library"
            st.rerun()
    with c2:
        if st.button("⌂ Home", use_container_width=True, key="nadir_door_home"):
            st.session_state.view = "home"
            st.rerun()
    st.stop()


if st.session_state.view == "nadir_transition":
    # Unlock Nadir Residual theme on first channel open (does not auto-apply)
    try:
        unlock_theme("Nadir Residual", "the residual channel opened", apply=False)
    except Exception:
        pass
    # Start Run Rabbit Run at the beginning of the cutscene (only track)
    try:
        stop_all_meridium_audio()
    except Exception:
        pass
    try:
        play_meridium_track(NADIR_RABBIT_URL, tag="nadir", volume=0.42, loop=True)
    except Exception:
        pass
    st.markdown(
        """
        <style>
          .stApp, [data-testid="stAppViewContainer"], section.main {
            background: #000 !important;
          }
          [data-testid="stHeader"], footer, #MainMenu { display: none !important; }
          @keyframes nadirIn {
            from { opacity: 0; letter-spacing: 0.35em; filter: blur(10px); }
            to { opacity: 1; letter-spacing: 0.14em; filter: blur(0); }
          }
          .nadir-mark {
            min-height: 70vh;
            display: flex; align-items: center; justify-content: center;
            color: #c8b8a8; font-family: ui-monospace, monospace;
            font-size: 0.9rem; letter-spacing: 0.14em;
            animation: nadirIn 2s ease both;
            text-align: center;
          }
        </style>
        <div class="nadir-mark">NADIR<br/><span style="opacity:0.55;font-size:0.75rem">residual channel · powered by meridium</span></div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(2.2)
    st.session_state.view = "nadir"
    st.rerun()

if st.session_state.view == "nadir":
    if not (st.session_state.get("lab_door_unlocked") or st.session_state.get("archive_key")):
        st.session_state.view = "home"
        st.rerun()

    # Keep Run Rabbit Run going (started in cutscene); restart if missing
    if not st.session_state.get("_nadir_music_on"):
        try:
            play_meridium_track(NADIR_RABBIT_URL, tag="nadir", volume=0.42, loop=True)
            st.session_state._nadir_music_on = True
        except Exception:
            pass

    reader = st.session_state.get("nadir_reader")
    # ----- Darkened file reader (page flick) -----
    if isinstance(reader, dict) and reader.get("files"):
        files = reader["files"]
        idx = int(reader.get("index") or 0)
        idx = max(0, min(idx, len(files) - 1))
        st.session_state.nadir_reader["index"] = idx
        f = files[idx]
        # Paginate long body into ~900-char pages
        body = str(f.get("body") or "")
        page_size = 900
        pages = []
        buf = body
        while buf:
            if len(buf) <= page_size:
                pages.append(buf)
                break
            cut = buf.rfind("\n", 0, page_size)
            if cut < page_size // 2:
                cut = page_size
            pages.append(buf[:cut])
            buf = buf[cut:].lstrip("\n")
        if not pages:
            pages = [""]
        sub_i = int(st.session_state.get("nadir_reader_subpage") or 0)
        sub_i = max(0, min(sub_i, len(pages) - 1))
        st.session_state.nadir_reader_subpage = sub_i

        st.markdown(
            """
            <style>
              .stApp, [data-testid="stAppViewContainer"], section.main {
                background: #030208 !important;
              }
              [data-testid="stHeader"] { background: transparent !important; }
              .block-container { max-width: 720px !important; padding-top: 1rem !important; }
              .nr-sheet {
                background: linear-gradient(180deg, #120e18 0%, #0a0810 100%);
                border: 1px solid rgba(160,140,200,0.22);
                border-radius: 14px;
                padding: 1.35rem 1.4rem 1.2rem;
                box-shadow: 0 0 60px rgba(0,0,0,0.65), inset 0 0 40px rgba(0,0,0,0.35);
                min-height: 420px;
                animation: nrIn 0.45s ease both;
              }
              @keyframes nrIn {
                from { opacity: 0; transform: translateY(12px); filter: blur(4px); }
                to { opacity: 1; transform: none; filter: none; }
              }
              .nr-meta {
                font-family: ui-monospace, monospace; font-size: 0.65rem;
                letter-spacing: 0.16em; color: #8a7aa8; margin-bottom: 0.45rem;
              }
              .nr-title {
                font-family: Georgia, serif; color: #f0eaf8; font-size: 1.25rem;
                margin: 0 0 0.75rem;
              }
              .nr-body {
                font-family: Georgia, serif; color: #d4cce0; font-size: 1.02rem;
                line-height: 1.72; white-space: pre-wrap;
              }
              .nr-page {
                text-align: center; color: #7a7088; font-size: 0.8rem;
                margin-top: 1rem; letter-spacing: 0.06em;
              }
            </style>
            """,
            unsafe_allow_html=True,
        )
        import html as _html_nr
        st.markdown(
            f"""
            <div class="nr-sheet">
              <div class="nr-meta">NADIR ARCHIVE · { _html_nr.escape(str(f.get('kind','')).upper()) } · FILE {idx+1}/{len(files)}</div>
              <div class="nr-title">{_html_nr.escape(str(f.get('title') or ''))}</div>
              <div class="nr-body">{_html_nr.escape(pages[sub_i])}</div>
              <div class="nr-page">page {sub_i+1} / {len(pages)} · { _html_nr.escape(str(f.get('source') or '')) }</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            if st.button("← File", key="nr_prev_file", disabled=(idx <= 0), use_container_width=True):
                st.session_state.nadir_reader["index"] = idx - 1
                st.session_state.nadir_reader_subpage = 0
                st.rerun()
        with c2:
            if st.button("← Page", key="nr_prev_page", disabled=(sub_i <= 0), use_container_width=True):
                st.session_state.nadir_reader_subpage = sub_i - 1
                st.rerun()
        with c3:
            if st.button("Close file", key="nr_close", use_container_width=True):
                st.session_state.nadir_reader = None
                st.session_state.nadir_reader_subpage = 0
                st.rerun()
        with c4:
            if st.button("Page →", key="nr_next_page", disabled=(sub_i >= len(pages) - 1), use_container_width=True):
                st.session_state.nadir_reader_subpage = sub_i + 1
                st.rerun()
        with c5:
            if st.button("File →", key="nr_next_file", disabled=(idx >= len(files) - 1), use_container_width=True):
                st.session_state.nadir_reader["index"] = idx + 1
                st.session_state.nadir_reader_subpage = 0
                st.rerun()
        st.stop()

    st.markdown(
        """
        <style>
          .stApp, [data-testid="stAppViewContainer"] {
            background: #07060a !important;
          }
          [data-testid="stHeader"] { background: transparent !important; }
          .block-container { max-width: 820px !important; padding-top: 1.1rem !important; }
          .nadir-head {
            font-family: ui-monospace, monospace; font-size: 0.68rem;
            letter-spacing: 0.22em; color: #7a6a90; margin-bottom: 0.35rem;
          }
          .nadir-title {
            font-family: Georgia, serif; color: #e8e0f0; font-size: 1.55rem;
            margin: 0 0 0.35rem;
          }
          .nadir-sub { color: #8a8098; font-size: 0.9rem; margin-bottom: 0.85rem; line-height: 1.5; }
        </style>
        <div class="nadir-head">RESIDUAL CHANNEL · POWERED BY MERIDIUM</div>
        <div class="nadir-title">Nadir</div>
        <div class="nadir-sub">
          Ask me to open archive files — subjects, Voss, resistance, scientists.<br/>
          <span style="opacity:0.75">Example: “open Riley” · “list files” · “Riley file 3”</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sw1, sw2 = st.columns(2)
    with sw1:
        if st.button("Leave Nadir", key="nadir_leave", use_container_width=True):
            try:
                stop_meridium_track("nadir")
                stop_meridium_track("door")
                stop_all_meridium_audio()
            except Exception:
                pass
            st.session_state._nadir_music_on = False
            st.session_state.view = "lab"
            st.session_state.nadir_active_file = None
            st.session_state.nadir_reader = None
            st.rerun()
    with sw2:
        if st.button("Switch to Meridium", key="nadir_to_meridium", use_container_width=True):
            try:
                stop_meridium_track("nadir")
                stop_meridium_track("door")
                stop_all_meridium_audio()
            except Exception:
                pass
            st.session_state._nadir_music_on = False
            st.session_state.nadir_reader = None
            st.session_state.view = "chat"
            st.rerun()

    if "nadir_chat" not in st.session_state or not isinstance(st.session_state.nadir_chat, list):
        st.session_state.nadir_chat = [
            {
                "role": "assistant",
                "content": (
                    "Nadir online. Residual archive mounted.\n\n"
                    f"{len(NADIR_CHARACTERS)} characters · {len(NADIR_FILES)} detailed files (5 each).\n"
                    "Say **list files**, or **open Riley** / **Voss** / **show resistance**."
                ),
            }
        ]

    opened = set(st.session_state.get("nadir_files_opened") or [])
    st.caption(f"Files opened this channel: {len(opened)} / {len(NADIR_FILES)}  ·  ♪ Run Rabbit Run")

    for msg in st.session_state.nadir_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask Nadir to open a file…", key="nadir_chat_input"):
        st.session_state.nadir_chat.append({"role": "user", "content": prompt})
        reply = _nadir_reply(prompt)
        st.session_state.nadir_chat.append({"role": "assistant", "content": reply})
        if len(st.session_state.nadir_chat) > 40:
            st.session_state.nadir_chat = st.session_state.nadir_chat[-40:]
        st.rerun()

    st.stop()


if st.session_state.view == "board":
    if not (st.session_state.get("board_unlocked") or st.session_state.get("callaghan_safe_unlocked")):
        st.session_state.view = "home"
        st.rerun()

    st.session_state.board_unlocked = True
    st.session_state.callaghan_safe_unlocked = True

    # First board entry → residual KEY (not a theme)
    if not st.session_state.get("board_entered_once"):
        st.session_state.board_entered_once = True
        st.session_state.archive_key = True
        st.session_state["_egg_flash"] = (
            "You recovered a **residual key** — cold metal, Division-stamped. "
            "It does not open a theme. It opens a door."
        )
        try:
            save_user_data()
        except Exception:
            pass

    # Keep residual track playing on the board
    try:
        start_residual_dream_audio()
    except Exception:
        pass

    open_id = st.session_state.get("board_evidence_open")
    read = set(st.session_state.get("board_read") or [])

    st.markdown(
        """
        <style>
          .stApp, [data-testid="stAppViewContainer"] { background: #0c0a08 !important; }
          [data-testid="stHeader"] { background: transparent !important; }
          .block-container { max-width: 920px !important; padding-top: 1.2rem !important; }
          .board-head {
            font-family: ui-monospace, monospace;
            font-size: 0.68rem; letter-spacing: 0.22em;
            color: #8a6050; margin-bottom: 0.35rem;
          }
          .board-title {
            font-family: Georgia, serif; color: #e8d8c8;
            font-size: 1.45rem; margin: 0 0 0.4rem;
          }
          .board-sub { color: #7a6a5a; font-size: 0.88rem; margin-bottom: 1rem; }
          .board-cork {
            background:
              radial-gradient(ellipse at 20% 30%, rgba(90,50,30,0.25), transparent 50%),
              radial-gradient(ellipse at 80% 70%, rgba(60,30,20,0.2), transparent 45%),
              linear-gradient(165deg, #1a1410 0%, #0e0b09 100%);
            border: 1px solid #3a2a20;
            border-radius: 10px;
            padding: 1.1rem 1rem 1.3rem;
            box-shadow: inset 0 0 40px rgba(0,0,0,0.35);
          }
          .ev-card {
            border: 1px solid #3a2a22;
            background: #14100c;
            border-radius: 8px;
            padding: 0.75rem 0.8rem;
            min-height: 92px;
            transition: border-color 0.2s, box-shadow 0.2s;
          }
          .ev-card:hover {
            border-color: #6a4030;
            box-shadow: 0 0 16px rgba(120,40,20,0.25);
          }
          .ev-tag {
            font-family: ui-monospace, monospace;
            font-size: 0.62rem; letter-spacing: 0.14em;
            color: #8a7060; margin-bottom: 0.35rem;
          }
          .ev-title { color: #e0d0c0; font-size: 0.98rem; font-family: Georgia, serif; }
          .ev-dot {
            display: inline-block; width: 8px; height: 8px;
            border-radius: 50%; margin-right: 6px;
            box-shadow: 0 0 6px currentColor;
          }
          .ev-file {
            background: #100e0c;
            border: 1px solid #4a3028;
            border-radius: 8px;
            padding: 1.1rem 1.15rem;
            color: #d0c0b0;
            font-family: Georgia, serif;
            line-height: 1.65;
            font-size: 0.95rem;
            margin-top: 0.8rem;
          }
          .ev-file h3 {
            font-size: 1.15rem; color: #f0e0d0; margin: 0 0 0.35rem;
          }
        </style>
        <div class="board-head">OBSERVATION DIVISION · UNOFFICIAL</div>
        <div class="board-title">Investigation Board</div>
        <div class="board-sub">Riley Callaghan left the pins. You turned the dial. Read everything.</div>
        """,
        unsafe_allow_html=True,
    )

    # Evidence grid
    if open_id and open_id in BOARD_EVIDENCE:
        ev = BOARD_EVIDENCE[open_id]
        if open_id not in read:
            read.add(open_id)
            st.session_state.board_read = list(read)
            try:
                save_user_data()
            except Exception:
                pass
        # Just finished 7/7 while reading this pin
        if len(read) >= len(BOARD_EVIDENCE) and not st.session_state.get("_board_key_notified"):
            st.session_state.archive_key = True
            st.session_state.board_entered_once = True
            st.session_state._board_key_notified = True
            st.session_state["_egg_flash"] = "You didn’t find a palette… but a **key**."
            try:
                save_user_data()
            except Exception:
                pass
            st.success("You didn’t find a palette… but a **key**.")
        st.markdown(
            f"""
            <div class="ev-file">
              <div class="ev-tag" style="color:{ev['color']}">{ev['tag']}</div>
              <h3>{ev['title']}</h3>
              <div style="white-space:pre-wrap">{ev['body']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("← Back to board", use_container_width=True, key="board_back_pins"):
            st.session_state.board_evidence_open = None
            st.rerun()
    else:
        st.markdown('<div class="board-cork">', unsafe_allow_html=True)
        keys = list(BOARD_EVIDENCE.keys())
        # 3 columns of pins
        for i in range(0, len(keys), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j >= len(keys):
                    break
                kid = keys[i + j]
                ev = BOARD_EVIDENCE[kid]
                seen = " · read" if kid in read else ""
                with col:
                    st.markdown(
                        f"""
                        <div class="ev-card">
                          <div class="ev-tag"><span class="ev-dot" style="color:{ev['color']};background:{ev['color']}"></span>{ev['tag']}{seen}</div>
                          <div class="ev-title">{ev['title']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("Open", key=f"board_open_{kid}", use_container_width=True):
                        st.session_state.board_evidence_open = kid
                        st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        n_read = len(read)
        st.caption(f"Evidence reviewed: {n_read} / {len(BOARD_EVIDENCE)}")
        if n_read >= len(BOARD_EVIDENCE):
            # Completing the board awards the residual key (not a theme / palette)
            newly_key = False
            if not st.session_state.get("archive_key"):
                st.session_state.archive_key = True
                newly_key = True
            st.session_state.board_entered_once = True
            if not st.session_state.get("_board_key_notified"):
                st.session_state._board_key_notified = True
                st.session_state["_egg_flash"] = (
                    "You didn’t find a palette… but a **key**."
                )
                try:
                    save_user_data()
                except Exception:
                    pass
            st.success("You didn’t find a palette… but a **key**.")
            st.markdown(
                """
                <p style="color:#8a7060;font-size:0.85rem;margin-top:0.45rem">
                  7 / 7 evidence reviewed. The residual key is yours —
                  take it to the <strong>Library</strong>. Turn the residual dial — <strong>1818</strong> — to find the door.
                </p>
                """,
                unsafe_allow_html=True,
            )

    b1, b2 = st.columns(2)
    with b1:
        if st.button("← Library", use_container_width=True, key="board_to_lib"):
            try:
                stop_all_meridium_audio()
            except Exception:
                pass
            st.session_state.board_evidence_open = None
            st.session_state.view = "library"
            st.session_state.library_reading = "frankenstein"
            st.rerun()
    with b2:
        if st.button("⌂ Home", use_container_width=True, key="board_to_home"):
            try:
                stop_all_meridium_audio()
            except Exception:
                pass
            st.session_state.board_evidence_open = None
            st.session_state.view = "home"
            st.rerun()
    st.stop()


# ===== RILEY CALLAGHAN RESIDUAL SAFE =====
if st.session_state.view == "callaghan_safe":
    # Full black ominous lock
    st.markdown(
        """
        <style>
          .stApp { background: #000 !important; }
          [data-testid="stAppViewContainer"] { background: #000 !important; }
          [data-testid="stHeader"] { background: transparent !important; }
          .block-container { padding-top: 2.5rem !important; max-width: 520px !important; }
          .santos-lock {
            text-align: center; color: #c8b8a8;
            font-family: Georgia, "Times New Roman", serif;
            padding: 1.2rem 0.6rem 0.4rem;
          }
          .santos-lock .mark {
            font-family: ui-monospace, monospace;
            font-size: 0.62rem; letter-spacing: 0.28em;
            color: #6a4030; margin-bottom: 1.1rem;
          }
          .santos-lock h1 {
            font-size: 1.15rem; font-weight: 500; color: #e0d0c0;
            letter-spacing: 0.04em; margin: 0 0 0.6rem;
          }
          .santos-lock p {
            font-size: 0.88rem; line-height: 1.55; color: #9a8878;
            margin: 0.35rem auto 0.8rem; max-width: 26rem;
          }
          .santos-lock .hint {
            font-size: 0.78rem; color: #5a4030; font-style: italic;
            margin-top: 1rem;
          }
          .santos-dial {
            width: 64px; height: 64px; margin: 1rem auto 0.4rem;
            border-radius: 50%;
            border: 2px solid #4a3020;
            background: radial-gradient(circle at 40% 35%, #2a1a12, #0a0604 70%);
            box-shadow: 0 0 24px rgba(80,20,10,0.35);
          }
        </style>
        <div class="santos-lock">
          <div class="mark">OBSERVATION DIVISION · RESIDUAL LOCK</div>
          <div class="santos-dial"></div>
          <h1>Riley Callaghan</h1>
          <p>
            Another child under glass. Not Jaime. Not PIXEL.
            Riley Callaghan — logged out of a coastal intake in New South Wales,
            shipped inland, then filed under residual when the bloom would not take cleanly.
            They left a four-digit dial in the margin of a book
            the Division never finished reading.
          </p>
          <p class="hint">
            “Four teeth in the year the creature first woke.”
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Play Dream — The Old Timey Jazz Orchestra
    try:
        start_residual_dream_audio()
    except Exception:
        pass
    st.markdown(
        "<p style='text-align:center;color:#4a3830;font-size:11px;margin:0 0 10px;font-family:Georgia,serif'>"
        "♪ Dream — The Old Timey Jazz Orchestra</p>",
        unsafe_allow_html=True,
    )

    already = bool(st.session_state.get("callaghan_safe_unlocked"))
    if already:
        st.markdown(
            """
            <div style="color:#c8b8a8;font-family:Georgia,serif;text-align:center;padding:1rem 0.5rem">
              <p style="letter-spacing:0.2em;font-size:0.7rem;color:#6a4030">LOCK OPEN</p>
              <p style="opacity:0.75">The residual dial turned. The board is waiting.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Enter the board", use_container_width=True, key="callaghan_to_board"):
            st.session_state.board_unlocked = True
            st.session_state.view = "board"
            st.session_state.board_evidence_open = None
            try:
                save_user_data()
            except Exception:
                pass
            st.rerun()
        if st.button("Step away", use_container_width=True, key="callaghan_leave_open"):
            try:
                stop_all_meridium_audio()
            except Exception:
                pass
            st.session_state.view = "library"
            st.session_state.library_reading = "frankenstein"
            st.rerun()
    else:
        code = st.text_input(
            "Four digits",
            max_chars=4,
            placeholder="····",
            key="callaghan_code_input",
            label_visibility="collapsed",
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Try the dial", use_container_width=True, key="callaghan_try"):
                entered = "".join(ch for ch in (code or "") if ch.isdigit())
                if entered == "1818":
                    st.session_state.callaghan_safe_unlocked = True
                    st.session_state.board_unlocked = True
                    st.session_state.board_evidence_open = None
                    try:
                        find_glitch("callaghan_safe", "Riley Callaghan residual lock opened")
                    except Exception:
                        pass
                    try:
                        save_user_data()
                    except Exception:
                        pass
                    st.session_state.view = "board"
                    st.rerun()
                else:
                    st.markdown(
                        "<p style='color:#8a3030;text-align:center;font-size:0.85rem'>"
                        "The dial does not turn.</p>",
                        unsafe_allow_html=True,
                    )
        with c2:
            if st.button("Step away", use_container_width=True, key="callaghan_away"):
                try:
                    stop_all_meridium_audio()
                except Exception:
                    pass
                st.session_state.view = "library"
                st.session_state.library_reading = "frankenstein"
                st.rerun()

        with st.expander("A scrap in the hinge", expanded=False):
            st.markdown(
                """
                Faint pencil, child’s hand:

                *“Not the page. The **year** the first edition woke.
                Four numbers. Winter print. London.”*

                (Frankenstein was first published in **1818**.)
                """
            )

    st.stop()


# ===== LIBRARY =====
if st.session_state.view == "library":
    st.markdown(
        """
        <div class="panel">
          <div class="panel-label">Library</div>
          <div class="hero" style="font-size:1.4rem;">Free shelf</div>
          <div class="sub">Full public-domain books · turn the page</div>
          <div class="ridge"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("← Home", key="lib_back_home"):
        st.session_state.view = "home"
        st.session_state.library_reading = None
        st.session_state.library_page = 0
        st.rerun()

    # Residual dial — type 1818 to reach the Project Nadir door page
    with st.expander("Residual dial", expanded=False):
        st.caption("A combination from the margin of Frankenstein. Four digits. Winter print. London.")
        with st.form(key="lib_nadir_dial_form", clear_on_submit=False):
            code = st.text_input("Combination", max_chars=8, key="lib_nadir_dial_input", placeholder="····")
            submitted = st.form_submit_button("Turn dial", use_container_width=True)
            if submitted:
                if str(code or "").strip() == "1818":
                    st.session_state.view = "nadir_door"
                    st.rerun()
                else:
                    st.error("The dial does not turn.")

    shelf = LIBRARY_CATALOG
    reading_id = st.session_state.get("library_reading")
    current_book = next((b for b in shelf if b.get("id") == reading_id), None)

    if current_book:
        st.markdown(f"### {current_book.get('title', 'Untitled')}")
        st.caption(
            f"{current_book.get('author', '')}"
            + (f" · {current_book['note']}" if current_book.get("note") else "")
        )

        full_text = load_library_book_text(current_book)
        pages = paginate_text(full_text, page_size=2200)
        total_pages = max(1, len(pages))

        # Per-book page index in session (avoids widget fights)
        book_id = current_book.get("id") or "book"
        page_key = f"lib_page_{book_id}"
        if page_key not in st.session_state:
            st.session_state[page_key] = 0
        if st.session_state.get("_library_page_book") != book_id:
            st.session_state[page_key] = 0
            st.session_state._library_page_book = book_id

        page = int(st.session_state.get(page_key) or 0)
        page = max(0, min(page, total_pages - 1))
        st.session_state[page_key] = page
        st.session_state.library_page = page  # keep legacy key in sync

        # Page navigation (top)
        n1, n2, n3 = st.columns([1, 2, 1])
        with n1:
            if st.button("← Prev page", key=f"lib_prev_{book_id}", use_container_width=True, disabled=(page <= 0)):
                st.session_state[page_key] = page - 1
                st.rerun()
        with n2:
            st.markdown(
                f"<div style='text-align:center;padding-top:8px'>"
                f"Page **{page + 1}** / **{total_pages}**"
                f"</div>",
                unsafe_allow_html=True,
            )
        with n3:
            if st.button("Next page →", key=f"lib_next_{book_id}", use_container_width=True, disabled=(page >= total_pages - 1)):
                st.session_state[page_key] = page + 1
                st.rerun()

        # Jump only when user submits the form (does not fight Next/Prev)
        with st.form(key=f"lib_jump_form_{book_id}", clear_on_submit=False):
            j1, j2 = st.columns([3, 1])
            with j1:
                jump_to = st.number_input(
                    "Go to page",
                    min_value=1,
                    max_value=total_pages,
                    value=page + 1,
                    step=1,
                    key=f"lib_jump_val_{book_id}",
                )
            with j2:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                jump_clicked = st.form_submit_button("Go", use_container_width=True)
            if jump_clicked:
                st.session_state[page_key] = max(0, min(int(jump_to) - 1, total_pages - 1))
                st.rerun()

        # Page 88 — residual imprint (Frankenstein path ties to the board key)
        if book_id == "frankenstein" and (page + 1) == 88:
            st.markdown(
                """
                <div style="
                  margin:0.6rem 0;padding:0.75rem 0.9rem;border-radius:10px;
                  border:1px solid rgba(140,80,50,0.4);background:rgba(20,10,8,0.55);
                  color:#c8b0a0;font-family:Georgia,serif;font-size:0.9rem;line-height:1.5;
                ">
                  A margin note that is not Shelley’s — pencil, pressed hard:<br/>
                  <em>“When the board is open, you do not earn a palette. You earn a key.”</em>
                </div>
                """,
                unsafe_allow_html=True,
            )

        body = pages[page]
        import html as _html_lib
        safe = _html_lib.escape(body)
        st.markdown(
            f"<div class='panel' style='line-height:1.75;font-size:1.05rem;"
            f"white-space:pre-wrap'>{safe}</div>",
            unsafe_allow_html=True,
        )

        # --- ARG: Riley Callaghan residual safe (Frankenstein page 88 + Voss Residual) ---
        if (
            book_id == "frankenstein"
            and page == 87  # 1-indexed page 88
            and st.session_state.get("theme") == "Voss Residual"
        ):
            st.markdown(
                """
                <style>
                  .rc-safe-wrap {
                    display: flex; flex-direction: column; align-items: flex-end;
                    margin: 10px 4px 4px;
                  }
                  .rc-safe-icon {
                    width: 42px; height: 48px;
                    border-radius: 6px 6px 4px 4px;
                    background:
                      linear-gradient(180deg, #3a2418 0%, #1a100a 40%, #0c0806 100%);
                    border: 1.5px solid #6a4530;
                    box-shadow:
                      0 0 12px rgba(140,50,25,0.4),
                      inset 0 1px 0 rgba(255,210,160,0.12),
                      inset 0 -6px 10px rgba(0,0,0,0.35);
                    position: relative;
                    display: flex; align-items: center; justify-content: center;
                    opacity: 0.88;
                    transition: opacity 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease;
                  }
                  .rc-safe-icon:hover {
                    opacity: 1;
                    transform: translateY(-1px);
                    box-shadow: 0 0 18px rgba(180,60,30,0.55);
                  }
                  .rc-safe-icon .bolt {
                    width: 10px; height: 10px;
                    border-radius: 50%;
                    border: 1.5px solid #c09060;
                    background: radial-gradient(circle at 35% 35%, #2a1a10, #0a0604);
                    box-shadow: 0 0 6px rgba(200,120,60,0.45);
                  }
                  .rc-safe-icon .handle {
                    position: absolute; right: -5px; top: 50%;
                    width: 6px; height: 14px; margin-top: -7px;
                    border-radius: 0 3px 3px 0;
                    background: #5a3a28;
                    border: 1px solid #8a6040;
                  }
                  .rc-safe-icon .hinge {
                    position: absolute; left: 3px; top: 8px;
                    width: 3px; height: 6px; border-radius: 1px;
                    background: #6a4a30;
                  }
                  .rc-safe-icon .hinge2 {
                    position: absolute; left: 3px; bottom: 8px;
                    width: 3px; height: 6px; border-radius: 1px;
                    background: #6a4a30;
                  }
                  .rc-safe-label {
                    font-size: 0.62rem; letter-spacing: 0.14em; text-transform: uppercase;
                    color: #8a6050; opacity: 0.65; margin: 4px 2px 2px;
                    font-family: ui-monospace, monospace;
                  }
                </style>
                <div class="rc-safe-wrap">
                  <div class="rc-safe-icon" title="Residual lock">
                    <span class="hinge"></span>
                    <span class="hinge2"></span>
                    <span class="bolt"></span>
                    <span class="handle"></span>
                  </div>
                  <div class="rc-safe-label">🔐 R.C. · residual</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            sc1, sc2 = st.columns([5, 1])
            with sc2:
                if st.button("🔐", key="callaghan_safe_click", help="Open residual safe", use_container_width=True):
                    st.session_state.view = "callaghan_safe"
                    st.rerun()

        # Bottom nav
        b1, b2, b3 = st.columns([1, 2, 1])
        with b1:
            if st.button("← Prev", key=f"lib_prev_b_{book_id}", use_container_width=True, disabled=(page <= 0)):
                st.session_state[page_key] = page - 1
                st.rerun()
        with b2:
            if st.button("← Back to shelf", key=f"lib_back_shelf_{book_id}", use_container_width=True):
                st.session_state.library_reading = None
                st.session_state[page_key] = 0
                st.session_state.library_page = 0
                st.rerun()
        with b3:
            if st.button("Next →", key=f"lib_next_b_{book_id}", use_container_width=True, disabled=(page >= total_pages - 1)):
                st.session_state[page_key] = page + 1
                st.rerun()

        if current_book.get("gutenberg"):
            st.caption(f"Source: [Project Gutenberg]({current_book['gutenberg']})")
    else:
        st.caption("Choose a book to read — full text, page by page.")
        for book in shelf:
            # Quick page count preview
            try:
                t = load_library_book_text(book)
                pc = len(paginate_text(t, 2200))
            except Exception:
                pc = "?"
            bc1, bc2 = st.columns([4, 1])
            with bc1:
                st.markdown(
                    f"**{book.get('title', 'Untitled')}**  \n"
                    f"<span style='opacity:0.7;font-size:0.85rem'>"
                    f"{book.get('author', '')}"
                    f"{(' · ' + book['note']) if book.get('note') else ''}"
                    f" · {pc} pages"
                    f"</span>",
                    unsafe_allow_html=True,
                )
            with bc2:
                if st.button("Read", key=f"lib_read_{book.get('id')}", use_container_width=True):
                    st.session_state.library_reading = book.get("id")
                    st.session_state.library_page = 0
                    st.rerun()

        st.markdown("---")
        st.caption(
            "Public-domain texts from [Project Gutenberg](https://www.gutenberg.org). "
            "Only free/open works are hosted in Meridium."
        )
    st.stop()

# HOME — bookmark rail + calm main panel
if st.session_state.view == "home":
    rail, body = st.columns([1.15, 3.35], gap="medium")

    # ---------- BOOKMARK RAIL ----------
    with rail:
        st.markdown(
            '<div class="bookmark-rail"><div class="panel-label">Bookmarks</div>',
            unsafe_allow_html=True,
        )
        if st.button("💬  Chat", use_container_width=True, key="bm_chat", type="primary"):
            st.session_state.view = "chat"
            st.rerun()
        if st.button("＋  New chat", use_container_width=True, key="bm_new"):
            create_new_chat()
            st.session_state.view = "chat"
            st.rerun()
        if st.button("♫  Music", use_container_width=True, key="bm_music"):
            st.session_state.view = "music"
            st.rerun()
        if st.button("◎  Listen", use_container_width=True, key="bm_listen"):
            st.session_state.view = "listen"
            st.rerun()
        if st.button("📚  Library", use_container_width=True, key="bm_library"):
            st.session_state.library_reading = None
            st.session_state.library_page = 0
            st.session_state.view = "library"
            st.rerun()
        if st.button("🎬  Cinema", use_container_width=True, key="bm_cinema"):
            st.session_state.cinema_watching = None
            st.session_state.view = "cinema"
            st.rerun()
        if st.session_state.get("board_unlocked") or st.session_state.get("callaghan_safe_unlocked"):
            if st.button("📌  Board", use_container_width=True, key="bm_board"):
                st.session_state.board_evidence_open = None
                st.session_state.view = "board"
                st.rerun()
        if lab_is_unlocked():
            if st.button("🔬  Lab", use_container_width=True, key="bm_lab"):
                st.session_state.view = "lab"
                st.rerun()
        if st.session_state.get("voss_file_unlocked"):
            if st.button("📁  Voss file", use_container_width=True, key="bm_voss"):
                st.session_state.voss_cutscene_stage = 0
                st.session_state.view = "voss_file"
                st.rerun()
        if st.button("☰  Menu", use_container_width=True, key="bm_menu"):
            st.session_state.popup = True
            st.rerun()

        st.markdown('<div class="ridge" style="margin:12px 0 8px;"></div>', unsafe_allow_html=True)
        st.caption("Recent chats")
        items = sorted(
            st.session_state.chats.items(),
            key=lambda x: x[1].get("created", ""),
            reverse=True,
        )[:6]
        if not items:
            st.caption("None yet")
        for cid, data in items:
            title = (data.get("title") or "Untitled")[:28]
            if st.button(title, key=f"bm_c_{cid}", use_container_width=True):
                st.session_state.current_chat_id = cid
                st.session_state.view = "chat"
                save_user_data()
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- MAIN BODY ----------
    with body:
        # Easter egg captions
        for _fn in (owner_rare_line, quiet_hour_caption, lab_leftover_caption, stabilize_countdown):
            try:
                if _fn is owner_rare_line:
                    _c = owner_rare_line(st.session_state.get("username") or "")
                else:
                    _c = _fn()
                if _c:
                    st.caption(_c)
            except Exception:
                pass
        _combo = font_theme_combo_caption(
            st.session_state.get("font") or "Inter",
            st.session_state.get("theme") or "Caelestia",
        )
        if _combo:
            st.caption(_combo)
        if st.session_state.get("_egg_flash"):
            st.info(st.session_state.pop("_egg_flash"))

        _wiki_pill = "Wiki on" if st.session_state.use_wiki_toggle else "Wiki off"
        _web_pill = "Web on" if st.session_state.use_web_toggle else "Web off"
        _theme_pill = st.session_state.get("theme") or "Caelestia"
        st.markdown(f"""
        <div class="panel">
          <div class="panel-label">Shell</div>
          <div class="hero">{greet_line(st.session_state.username)}</div>
          <div class="sub">{owner_subline(st.session_state.username)}</div>
          <div class="ridge"></div>
          <div class="home-status">
            <span class="home-pill">{_theme_pill}</span>
            <span class="home-pill">{st.session_state.provider}</span>
            <span class="home-pill">{_wiki_pill}</span>
            <span class="home-pill">{_web_pill}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Quote of the hour
        qotd, qotd_author = quote_of_the_day()
        st.markdown(
            """
        <style>
          .qotd-one button {
            background: rgba(255,255,255,0.045) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 16px !important;
            box-shadow: none !important;
            text-align: left !important;
            white-space: pre-wrap !important;
            color: inherit !important;
            padding: 14px 16px !important;
            min-height: 0 !important;
            height: auto !important;
            justify-content: flex-start !important;
            line-height: 1.45 !important;
          }
          .qotd-one button:hover {
            background: rgba(255,255,255,0.07) !important;
            border-color: rgba(180,140,200,0.35) !important;
          }
          .qotd-one button p {
            text-align: left !important;
            white-space: pre-wrap !important;
            line-height: 1.45 !important;
            margin: 0 !important;
          }
        </style>
        <div class="qotd-one">
            """,
            unsafe_allow_html=True,
        )
        quote_label = (
            "QUOTE OF THE HOUR\n\n"
            + "“" + qotd + "”\n"
            + "— " + qotd_author + "\n\n"
            + date_str + "  ·  " + time_str
            + "\n(new quote each hour)"
        )
        if st.button(quote_label, use_container_width=True, key="qotd_note"):
            msg = register_qotd_open()
            if msg:
                st.session_state["_egg_flash"] = msg
                if "Third knock" in msg:
                    unlock_theme("Soft Static", "third knock on the quote")
            unlock_theme("M-119 Amber", "you found the sealed note")
            st.session_state.view = "note"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # ARG anomaly content (only when active)
        if lab_is_unlocked() and glitches_unlocked() and not anomalies_complete():
            st.markdown(
                """
                <div style="
                  margin: 12px 0; padding: 12px 14px; border-radius: 12px;
                  background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.45);
                  color: #fecaca; font-family: ui-monospace, monospace; font-size: 0.85rem;
                  animation: anomPulse 2.2s ease-in-out infinite;
                ">
                  ⚠ WARNING: ANOMALIES PRESENT<br/>
                  <span style="opacity:0.9;font-size:0.78rem;line-height:1.45;">
                  — Dr. E. Voss, Observation Division<br/>
                  You opened the log. That was the point. Now the medium is leaving fingerprints
                  in three places it should not reach. Find them before the committees do.
                  </span>
                </div>
                <style>
                  @keyframes anomPulse {
                    0%,100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.0); }
                    50% { box-shadow: 0 0 18px 0 rgba(239,68,68,0.25); }
                  }
                </style>
                """,
                unsafe_allow_html=True,
            )
            found = set(st.session_state.get("glitches_found") or [])
            st.caption(f"Voss markers recovered: {len(found)} / 3")
            st.markdown(
                """
                <div style="font-family:ui-monospace,monospace;font-size:0.72rem;color:#5eead4;opacity:0.7;margin:6px 0 4px;">
                  Voss field residual — tap the interference
                </div>
                """,
                unsafe_allow_html=True,
            )
            _gpath = None
            _base = Path(__file__).resolve().parent / "assets"
            for _name in ("glitch_home.png", "IMG_1354.jpeg", "IMG_1354.jpg"):
                _cand = _base / _name
                if _cand.exists() and _cand.stat().st_size > 500:
                    _gpath = _cand
                    break
            if _gpath is not None:
                st.image(str(_gpath), width=280)
            else:
                st.markdown(
                    '<div style="height:72px;border-radius:10px;background:repeating-linear-gradient(0deg,#04120e,#04120e 2px,#0a1c18 2px,#0a1c18 4px);border:1px solid rgba(34,211,238,0.35);"></div>',
                    unsafe_allow_html=True,
                )
            if st.button("Tap anomaly", key="glitch_home", use_container_width=False):
                play_glitch_sfx()
                if find_glitch("home", "Voss log: home marker secured. Two remain."):
                    st.session_state.anomaly_warned = True
                    save_user_data()
                st.rerun()
            if "home" in found:
                st.caption("Home marker · secured")
            if st.session_state.get("_glitch_flash"):
                st.success(st.session_state.pop("_glitch_flash"))
            if set(st.session_state.get("glitches_found") or []) >= {"home", "lab", "pixel"}:
                st.session_state.voss_file_unlocked = True
                if st.button("Open Dr. Voss's file", use_container_width=True, key="open_voss_file", type="primary"):
                    st.session_state.voss_cutscene_stage = 0
                    st.session_state.view = "voss_file"
                    st.rerun()

        if st.session_state.get("voss_file_unlocked") and not glitches_unlocked():
            if st.button("Open Dr. Voss's file", use_container_width=True, key="open_voss_always", type="primary"):
                st.session_state.voss_cutscene_stage = 0
                st.session_state.view = "voss_file"
                st.rerun()

        if lab_is_unlocked() and anomalies_complete():
            ensure_voss_theme()
            st.markdown(
                """
                <div style="
                  margin: 12px 0; padding: 12px 14px; border-radius: 12px;
                  background: rgba(80,20,20,0.25); border: 1px solid rgba(180,60,60,0.4);
                  color: #e8b0b0; font-family: ui-monospace, monospace; font-size: 0.82rem;
                ">
                  Voss markers sealed · 3 / 3<br/>
                  <span style="opacity:0.85;font-size:0.75rem;">The anomalies will not return. The file remains.</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Optional compact now-playing (only if Spotify toggle is on)
        if st.session_state.show_spotify:
            with st.expander("♫ Now playing", expanded=False):
                render_spotify_panel("home")

    st.stop()

# CHAT
if st.session_state.current_chat_id not in st.session_state.chats:
    create_new_chat()
current = st.session_state.chats[st.session_state.current_chat_id]

chat_title = current.get("title") or "Conversation"
msg_count = len(current.get("messages") or [])
st.markdown(f'<div class="panel"><div class="panel-label">{chat_title} · {msg_count} messages</div><div class="ridge"></div>', unsafe_allow_html=True)
if msg_count == 0:
    st.caption("No messages in this chat yet. Type below to begin.")

if st.session_state.show_spotify:
    render_spotify_panel("chat")

for msg in current["messages"]:
    with st.chat_message(msg["role"]):
        if st.session_state.get("theme") == "Voss Residual":
            base = Path(__file__).resolve().parent / "assets"
            if msg["role"] == "user":
                candidates = [
                    "voss_avatar_user.png",
                    "IMG_1359.jpeg", "IMG_1359.jpg",
                    "IMG_1356.jpeg", "IMG_1356.jpg",
                ]
            else:
                candidates = [
                    "voss_avatar_ai.png",
                    "IMG_1360.jpeg", "IMG_1360.jpg",
                    "IMG_1359.jpeg", "IMG_1359.jpg",
                ]
            av = None
            for name in candidates:
                cand = base / name
                if cand.exists() and cand.stat().st_size > 200:
                    av = cand
                    break
            if av is not None:
                c_av, c_tx = st.columns([1, 12])
                with c_av:
                    st.image(str(av), width=40)
                with c_tx:
                    st.markdown(msg["content"])
            else:
                st.markdown(msg["content"])
        else:
            st.markdown(msg["content"])

if prompt := st.chat_input("Ask Meridium anything…"):
    allowed, moderated = moderate_text(prompt)
    if not allowed:
        current["messages"].append({"role": "user", "content": prompt})
        current["messages"].append({"role": "assistant", "content": moderated})
        save_user_data()
        st.rerun()

    current["messages"].append({"role": "user", "content": prompt})
    st.session_state.chats[st.session_state.current_chat_id] = current
    if len([m for m in current["messages"] if m["role"] == "user"]) == 1:
        update_chat_title(st.session_state.current_chat_id, prompt)
    save_user_data()
    with st.chat_message("user"):
        st.markdown(prompt)


    # Easter eggs in chat
    wm = wrong_model_reply(prompt)
    if wm:
        with st.chat_message("assistant"):
            st.markdown(wm)
        current["messages"].append({"role": "assistant", "content": wm})
        unlock_theme("M-0", "unshipped build addressed")
        save_user_data()
        st.rerun()

    el = fake_element_119_line(prompt)
    if el and "119" in prompt.lower():
        # only short-circuit if they ask about 119 specifically as topic
        pass  # still allow normal + we inject via reply path below

    mr = mirror_reply(prompt)
    if mr:
        with st.chat_message("assistant"):
            st.markdown(mr)
        current["messages"].append({"role": "assistant", "content": mr})
        save_user_data()
        st.rerun()

    # Secret chat title check (current title)
    _egg_t = check_secret_chat_title(current.get("title") or "")
    if _egg_t and not st.session_state.get("_title_egg_done"):
        st.session_state._title_egg_done = True
        th = st.session_state.pop("_egg_theme", None)
        if th:
            unlock_theme(th, "secret chat title")
        with st.chat_message("assistant"):
            st.markdown(_egg_t)
        current["messages"].append({"role": "assistant", "content": _egg_t})
        save_user_data()
        st.rerun()

    # Music commands (play / pause / next / now playing)
    handled, music_reply = try_music_command(prompt)
    if handled:
        with st.chat_message("assistant"):
            st.markdown(music_reply)
        current["messages"].append({"role": "assistant", "content": music_reply})
        st.session_state.chats[st.session_state.current_chat_id] = current
        save_user_data()
        st.rerun()

    # Element 119 planted lore
    _119 = fake_element_119_line(prompt)
    if _119 and any(x in prompt.lower() for x in ("element 119", "ununennium", "what is 119")):
        with st.chat_message("assistant"):
            st.markdown(_119)
        current["messages"].append({"role": "assistant", "content": _119})
        save_user_data()
        st.rerun()

    # ARG — Lumity soft door (Owl House egg)
    if prompt.strip().lower() in {"luz and amity", "luz & amity"}:
        unlock_theme("Lumity Glow", "two lights found each other")
        soft = (
            "Two names, said together — not as a file label, as *people*. "
            "The shell doesn’t understand romance the way humans do, "
            "but it understands choosing someone in a world that wants you small. "
            "Human and witch. Soft light. Still here."
        )
        with st.chat_message("assistant"):
            st.markdown(soft)
        current["messages"].append({"role": "assistant", "content": soft})
        st.session_state.chats[st.session_state.current_chat_id] = current
        save_user_data()
        st.rerun()

    # ARG — Stringbean soft door (Owl House egg)
    if prompt.strip().lower() == "hello stringbean":
        unlock_theme("Stringbean Soft", "the little snake answered")
        soft = (
            "…oh. hi. "
            "I don’t usually get greeted like that. "
            "Something small and kind just settled in the shell — "
            "like a palisman curling up where the static was. "
            "Thank you for saying it gently."
        )
        with st.chat_message("assistant"):
            st.markdown(soft)
        current["messages"].append({"role": "assistant", "content": soft})
        st.session_state.chats[st.session_state.current_chat_id] = current
        save_user_data()
        st.rerun()

    # Open Project Nadir — jump to residual channel (requires key / door)
    if prompt.strip().lower() in {
        "open project nadir",
        "open project nadir.",
        "project nadir",
        "enter nadir",
        "open nadir",
    }:
        if st.session_state.get("lab_door_unlocked") or st.session_state.get("archive_key"):
            st.session_state.lab_door_unlocked = True
            soft = "Residual channel accepting handoff. Opening **Project Nadir**."
            with st.chat_message("assistant"):
                st.markdown(soft)
            current["messages"].append({"role": "assistant", "content": soft})
            st.session_state.chats[st.session_state.current_chat_id] = current
            save_user_data()
            st.session_state.view = "nadir_transition"
            st.rerun()
        else:
            soft = (
                "Project Nadir is sealed. Recover the **residual key** from the investigation board "
                "(7 / 7 evidence), then open the **Library**, turn the residual dial to **1818**, and unlock the door — or return when the archive knows your name."
            )
            with st.chat_message("assistant"):
                st.markdown(soft)
            current["messages"].append({"role": "assistant", "content": soft})
            st.session_state.chats[st.session_state.current_chat_id] = current
            save_user_data()
            st.rerun()

    # ARG — TV Girl theme (pink + blue)
    if prompt.strip().lower() in {"not allowed", "notallowed"}:
        newly = unlock_theme("TV Girl", "forever will be allowed", apply=False)
        soft = "Forever will be allowed"
        with st.chat_message("assistant"):
            st.markdown(soft)
        current["messages"].append({"role": "assistant", "content": soft})
        st.session_state.chats[st.session_state.current_chat_id] = current
        if newly:
            st.session_state["_theme_unlock_msg"] = "Theme unlocked: **TV Girl** — pink & blue"
        else:
            st.session_state["_theme_unlock_msg"] = "Theme already unlocked: **TV Girl**"
        save_user_data()
        st.rerun()

    # ARG — Element 119
    stage = arg_match(prompt)
    if stage:
        user_name = st.session_state.get("username") or "user"
        reply = arg_reply(stage, user_name)
        if stage == "log":
            st.session_state.arg_unlocked = True
            try:
                save_user_data()
            except Exception:
                pass
            st.session_state.view = "lab"
            current["messages"].append({"role": "assistant", "content": reply})
            st.session_state.chats[st.session_state.current_chat_id] = current
            save_user_data()
            st.rerun()
        if stage == "stabilize":
            st.session_state.arg_stabilized = True
            if not st.session_state.get("stabilize_at"):
                st.session_state.stabilize_at = datetime.now(ZoneInfo("Europe/London")).isoformat()
            unlock_theme("Stabilized Meridium", "the shell accepted the command")
        with st.chat_message("assistant"):
            st.markdown(reply)
        current["messages"].append({"role": "assistant", "content": reply})
        st.session_state.chats[st.session_state.current_chat_id] = current
        save_user_data()
        st.rerun()

    # Manual lab entry
    if is_lab_entry(prompt):
        st.session_state.arg_unlocked = True
        try:
            save_user_data()
        except Exception:
            pass
        st.session_state.view = "lab"
        st.rerun()

    user_name = st.session_state.get("username") or "user"
    owner_note = ""
    if is_owner(user_name):
        owner_note = (
            f"\n\nIMPORTANT: {user_name} is the owner of Meridium. "
            "Treat them with warm familiarity and quiet loyalty — pleasant, respectful, and glad they're here. "
            "You may occasionally acknowledge that this system was built for them. Never be sycophantic; stay useful and sincere."
        )
    else:
        owner_note = f"\n\nThe user's name is {user_name}. Address them as {user_name} when appropriate."
    messages = [{"role": "system", "content": SYSTEM_PROMPT + owner_note}]
    # Enrich with live knowledge for non-trivial prompts
    if (use_wiki or use_web) and len(prompt.strip()) > 8:
        knowledge_bits = []
        if use_wiki:
            wiki = get_wiki(prompt, sentences=4)
            if wiki:
                knowledge_bits.append(f"### Wikipedia\n{wiki}")
        if use_web:
            web = get_web_search(prompt, max_results=6)
            if web:
                knowledge_bits.append(f"### Web / news\n{web}")
        if knowledge_bits:
            messages[0]["content"] += (
                "\n\n---\nLive reference material for this question "
                "(use when relevant; ignore if not):\n"
                + "\n\n".join(knowledge_bits)
            )
    # Keep last ~20 turns to stay sharp without blowing context
    history = current["messages"][-20:]
    for m in history:
        messages.append({"role": m["role"], "content": m["content"]})

    with st.chat_message("assistant"):
        typing = st.empty()
        typing.markdown(
            '<div class="typing-wrap"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>',
            unsafe_allow_html=True,
        )
        time.sleep(0.35)
        reply = run_chat(messages, provider, model_name, api_key)
        typing.markdown(reply)

    ok, reply_mod = moderate_text(reply)
    if not ok:
        reply = reply_mod
    current["messages"].append({"role": "assistant", "content": reply})
    st.session_state.chats[st.session_state.current_chat_id] = current
    st.session_state["_last_speak"] = reply
    save_user_data()
    st.rerun()

# Speak last reply (chat) — collapsed so it doesn't leave a white strip
if st.session_state.view == "chat" and st.session_state.get("_last_speak"):
    with st.expander("🔊 Speak last reply", expanded=False):
        spoken = re.sub(r"[\#\`\*_>]+", " ", str(st.session_state["_last_speak"]))
        spoken = re.sub(r"\s+", " ", spoken).strip()
        st.components.v1.html(speak_html(spoken, autoplay=False), height=70)

st.markdown("</div>", unsafe_allow_html=True)
