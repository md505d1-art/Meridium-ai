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

from arg_story import arg_match, arg_reply, is_owner, is_lab_entry
from lab_view import render_lab
from note_view import render_note
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

}




try:
    from theme_unlocks import unlock_and_persist
except Exception:
    def unlock_and_persist(theme_name: str, reason: str = "", apply: bool = True) -> bool:
        unlocked = list(st.session_state.get("unlocked_themes") or [])
        newly = theme_name not in unlocked
        if newly:
            unlocked.append(theme_name)
            st.session_state.unlocked_themes = unlocked
            st.session_state["_theme_unlock_msg"] = (
                f"Theme unlocked: **{theme_name}**" + (f" — {reason}" if reason else "")
            )
        if apply:
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
            unlock_theme("Voss Residual", "Dr. Voss's file recovered", apply=True)
        except Exception:
            u = list(st.session_state.get("unlocked_themes") or [])
            if "Voss Residual" not in u:
                u.append("Voss Residual")
                st.session_state.unlocked_themes = u
            st.session_state.theme = "Voss Residual"
        st.session_state["_glitch_flash"] = (
            "All three markers secured. Dr. Voss left you a file. Theme: Voss Residual."
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
    """Hard-stop note / pixel / lab / voss / any tagged audio."""
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
                root.__mer_note_audio_on = false;
                var nodes = root.document.querySelectorAll('audio');
                for (var i = 0; i < nodes.length; i++) {
                  var a = nodes[i];
                  var tag = a.getAttribute('data-meridium-pixel')
                    || a.getAttribute('data-meridium-note')
                    || a.getAttribute('data-meridium-lab')
                    || a.getAttribute('data-meridium-voss')
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
    if st.session_state.get("arg_unlocked"):
        return True
    unlocked = st.session_state.get("unlocked_themes") or []
    if "Containment Red" in unlocked or "Voss Static" in unlocked:
        st.session_state.arg_unlocked = True
        return True
    if st.session_state.get("_lab_session_visit"):
        st.session_state.arg_unlocked = True
        return True
    return False


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


def unlock_theme(theme_name: str, reason: str = "", apply: bool = True) -> bool:
    """Unlock a secret theme once. Returns True if newly unlocked."""
    return unlock_and_persist(theme_name, reason, apply=apply)



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

    .panel {{
        padding: 18px 18px 16px;
        margin-bottom: 14px;
        animation: fadeUp 0.45s ease both;
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
        animation: textIn 0.65s ease both;
    }}
    .hero span {{ color: {SHELL["accent"]}; }}
    .sub {{
        color: {SHELL["muted"]}; margin-bottom: 10px; font-size: 0.95rem;
        animation: textIn 0.65s ease 0.08s both;
    }}
    .ridge {{
        height: 1px; margin: 10px 0 4px;
        background: linear-gradient(90deg, transparent, {SHELL["accent"]}, transparent);
        opacity: 0.55;
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
        transition: all 0.15s ease !important;
    }}
    .stButton > button:hover {{
        border-color: {SHELL["accent"]} !important;
        background: {SHELL["accent_soft"]} !important;
        color: {SHELL["accent"]} !important;
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
        from {{ opacity: 0; transform: translateY(12px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes textIn {{
        from {{ opacity: 0; transform: translateY(12px); }}
        to {{ opacity: 1; transform: translateY(0); }}
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
}
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
        # Prefer exact get when duration known
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
            # Search fallback
            search_url = "https://lrclib.net/api/search?" + urllib.parse.urlencode(
                {"q": f"{artist} {track_name}"}
            )
            results = _get(search_url)
            if isinstance(results, list) and results:
                # Prefer closest name/artist match with synced lyrics
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
                # fetch by id
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
    """Show connect / now playing / controls / lyrics. Returns True if connected."""
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

    # Animated now playing banner
    import html as _html
    _tname = _html.escape(str(track.get("name") or "Unknown"))
    _tarts = _html.escape(str(track.get("artists") or ""))
    _status = "Now playing" if track.get("playing") else "Paused"
    st.markdown(
        f"""
        <style>
          @keyframes npPulse {{
            0%,100% {{ opacity: 0.9; }}
            50% {{ opacity: 1; }}
          }}
          .np-banner {{
            text-align: center;
            padding: 0.7rem 1rem;
            margin-bottom: 0.75rem;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.12);
            background: rgba(255,255,255,0.04);
            animation: npPulse 2.6s ease-in-out infinite;
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

    # Layout: art + controls LEFT · lyrics RIGHT (where user pointed)
    left, right = st.columns([1.05, 1.35], gap="medium")

    with left:
        art = track.get("art")
        if art:
            st.image(art, width=200)
        st.markdown(f"### {track['name']}")
        st.caption(track["artists"] + (f" · {track['device']}" if track.get("device") else ""))
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
                # force fresh lyrics + progress
                st.session_state._lyrics_key = None
                st.rerun()

    with right:
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
                        # slight lead so highlight feels on-beat (LRC often lags a bit)
                        prog_js = max(0, int(progress) + 150)
                        play_js = "true" if playing else "false"
                        st.components.v1.html(
                            f"""
                            <div id="mer-lrc-wrap" style="
                              font-family: Inter, system-ui, sans-serif;
                              color: #e8e6f0;
                              height: 340px;
                              overflow-y: auto;
                              padding: 10px 6px;
                              border-radius: 14px;
                              background: rgba(255,255,255,0.04);
                              border: 1px solid rgba(255,255,255,0.1);
                              scroll-behavior: smooth;
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
                            height=380,
                        )
                    else:
                        st.text(lyric_data.get("plain") or lyric_data.get("synced"))
                else:
                    st.text(lyric_data.get("plain") or "")
                    st.caption("Plain lyrics (not timed)")
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

    # Re-anchor Spotify progress so lyrics stay accurate while playing
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
    low = text.lower()
    # Only treat as command if it looks like one
    triggers = (
        "play ", "play the song", "play song", "pause", "stop music", "stop the music",
        "next song", "next track", "skip", "previous", "prev song", "what song",
        "what's playing", "whats playing", "now playing", "resume",
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
        # now playing
        if any(x in low for x in ("what song", "what's playing", "whats playing", "now playing")):
            track = current_track(sp)
            if not track:
                return True, "Nothing is playing right now. Start a song in Spotify, then ask again."
            return True, f"♫ **{track['name']}** — {track['artists']}" + (f" ({track['device']})" if track.get("device") else "")

        # pause / stop
        if low in ("pause", "stop", "stop music", "stop the music", "pause music") or low.startswith("pause"):
            sp.pause_playback()
            return True, "Paused."

        # resume
        if low in ("resume", "continue", "unpause") or "resume" in low:
            sp.start_playback()
            return True, "Resumed."

        # next / skip
        if any(x in low for x in ("next song", "next track", "skip", "next")):
            sp.next_track()
            time.sleep(0.4)
            track = current_track(sp)
            if track:
                return True, f"⏭ **{track['name']}** — {track['artists']}"
            return True, "Skipped to next track."

        # previous
        if any(x in low for x in ("previous", "prev song", "last song")):
            sp.previous_track()
            time.sleep(0.4)
            track = current_track(sp)
            if track:
                return True, f"⏮ **{track['name']}** — {track['artists']}"
            return True, "Went to previous track."

        # play <query>
        if low.startswith("play ") or low.startswith("play the song"):
            query = text
            for prefix in ("play the song ", "play song ", "play "):
                if low.startswith(prefix):
                    query = text[len(prefix):].strip()
                    break
            query = query.strip().strip('"').strip("'")
            if not query:
                return True, "Tell me what to play — e.g. `play Nemzzz Prince of the Scene`"
            results = sp.search(q=query, type="track", limit=1)
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
        unlock_theme(_item[0], _item[1] if len(_item) > 1 else "", apply=True)

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
                st.session_state.username = result[:32]
                st.session_state.signed_in = True
                found = load_user_data(st.session_state.username)
                if not found and not st.session_state.get("chats"):
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
        if lab_is_unlocked():
            if st.button("Open the lab", use_container_width=True, key="pop_lab"):
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
        if st.button("✕  Close menu", use_container_width=True, key="pop_close"):
            st.session_state.popup = False
            st.rerun()
        if st.button("↩  Switch user", use_container_width=True, key="pop_signout"):
            st.session_state.signed_in = False
            st.session_state.username = ""
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


# LAB first — full black, no waybar/nav chrome
if st.session_state.view == "lab":
    if not st.session_state.get("_currently_in_lab"):
        st.session_state._currently_in_lab = True
        st.session_state.lab_visits = int(st.session_state.get("lab_visits") or 0) + 1
        try:
            save_user_data()
        except Exception:
            pass
    st.session_state.arg_unlocked = True
    try:
        save_user_data()
    except Exception:
        pass
    mark_lab_visit()
    unlock_theme("Containment Red", "you entered the observation log")
    # All 6 fragments?
    found = st.session_state.get("lab_found") or set()
    if isinstance(found, (list, set)) and len(set(found)) >= 6:
        unlock_theme("Voss Static", "all fragments recovered")
    render_lab()
if st.session_state.view == "note":
    render_note()

# ===== DESIGN 1 WAYBAR + NAV (hidden in lab) =====
if st.session_state.view not in ("lab", "note", "voss_file"):
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

    n1, n2, n3 = st.columns(3)
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
    n4, n5, n6 = st.columns(3)
    with n4:
        if st.button("◎ Listen", use_container_width=True, key="n_listen"):
            st.session_state.view = "listen"
            st.rerun()
    with n5:
        if st.button("☰ Menu", use_container_width=True, key="n_menu"):
            st.session_state.popup = True
            st.rerun()
    with n6:
        if lab_is_unlocked():
            if st.button("Open the lab", use_container_width=True, key="n_lab"):
                st.session_state.view = "lab"
                st.rerun()
        else:
            st.caption("")

# MUSIC — dedicated player + Meridium playlist
if st.session_state.view == "music":
    st.session_state.show_spotify = True
    st.markdown("""
    <style>
      @keyframes musicFadeUp {
        from { opacity: 0; transform: translateY(14px); }
        to { opacity: 1; transform: translateY(0); }
      }
      @keyframes equalizer {
        0%,100% { height: 6px; }
        50% { height: 18px; }
      }
      .music-hero {
        text-align: center;
        max-width: 440px;
        margin: 0 auto 14px;
        padding: 18px 16px;
        animation: musicFadeUp 0.5s ease both;
      }
      .music-eq {
        display: flex; gap: 4px; justify-content: center; align-items: flex-end;
        height: 22px; margin-bottom: 10px;
      }
      .music-eq span {
        width: 4px; border-radius: 2px; background: #c4a7e7;
        animation: equalizer 0.9s ease-in-out infinite;
      }
      .music-eq span:nth-child(2) { animation-delay: 0.15s; }
      .music-eq span:nth-child(3) { animation-delay: 0.3s; }
      .music-eq span:nth-child(4) { animation-delay: 0.45s; }
      .music-eq span:nth-child(5) { animation-delay: 0.2s; }
    </style>
    <div class="panel music-hero">
      <div class="music-eq"><span></span><span></span><span></span><span></span><span></span></div>
      <div class="panel-label">Music</div>
      <div class="hero" style="font-size:1.35rem;">Now playing</div>
      <div class="ridge"></div>
    </div>
    """, unsafe_allow_html=True)
    render_spotify_panel("musicpage")

    st.markdown("---")
    st.markdown("### Meridium playlist")
    st.caption("Your personal queue inside Meridium — add tracks by name.")

    # Add to playlist
    add_col1, add_col2 = st.columns([3, 1])
    with add_col1:
        new_track = st.text_input("Add track", placeholder="e.g. Nemzzz - Prince of the Scene", key="pl_add", label_visibility="collapsed")
    with add_col2:
        if st.button("Add", use_container_width=True, key="pl_add_btn"):
            t = (new_track or "").strip()
            if t:
                pl = list(st.session_state.get("meridium_playlist") or [])
                pl.append({"title": t, "added": datetime.now().isoformat()})
                st.session_state.meridium_playlist = pl
                save_user_data()
                st.rerun()

    playlist = st.session_state.get("meridium_playlist") or []
    if not playlist:
        st.caption("Playlist empty — add songs above.")
    else:
        for i, item in enumerate(playlist):
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(f"**{i+1}.** {item.get('title', 'Track')}")
            with c2:
                if st.button("✕", key=f"pl_del_{i}", help="Remove"):
                    pl = list(playlist)
                    pl.pop(i)
                    st.session_state.meridium_playlist = pl
                    save_user_data()
                    st.rerun()

        # Try play via Spotify search if connected
        sp = get_spotify()
        if sp and st.button("▶ Play first track on Spotify", use_container_width=True, key="pl_play"):
            try:
                q = playlist[0].get("title", "")
                results = sp.search(q=q, type="track", limit=1)
                tracks = (results.get("tracks") or {}).get("items") or []
                if tracks:
                    uri = tracks[0]["uri"]
                    sp.start_playback(uris=[uri])
                    time.sleep(0.4)
                    st.success(f"Playing: {tracks[0]['name']}")
                    st.rerun()
                else:
                    st.warning("No Spotify match found for that title.")
            except Exception as e:
                st.error(f"Playback failed (Premium + active Spotify device required): {e}")

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


# HOME — Design 1
if st.session_state.view == "home":

    # Easter egg captions on home
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
    st.markdown(f"""
    <div class="panel">
      <div class="panel-label">Shell</div>
      <div class="hero">{greet_line(st.session_state.username)}</div>
      <div class="sub">{owner_subline(st.session_state.username)}</div>
      <div class="ridge"></div>
    </div>
    """, unsafe_allow_html=True)


    # Post-lab anomaly warning + home glitch (after 2nd lab visit)
    if lab_is_unlocked() and glitches_unlocked() and not anomalies_complete():
        st.markdown(
            """
            <div style="
              margin: 0 0 12px; padding: 12px 14px; border-radius: 12px;
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
        # Home glitch — clickable image (not a white box)
        st.markdown(
            """
            <style>
              div[data-testid="stButton"]:has(button[kind="secondary"]) button {
                background: #0a1210 !important;
                color: #5eead4 !important;
                border: 1px solid rgba(34,211,238,0.35) !important;
                border-radius: 10px !important;
              }
            </style>
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
        st.markdown(
            """
            <style>
              div[data-testid="stButton"]:has(button[kind="secondary"]) button,
              div[data-testid="stButton"] button[kind="secondary"] {
                min-height: 32px !important;
                height: 32px !important;
                padding: 0 12px !important;
                font-size: 0.78rem !important;
                border-radius: 8px !important;
              }
            </style>
            """,
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

        # All three Voss markers → open her file
        if set(st.session_state.get("glitches_found") or []) >= {"home", "lab", "pixel"}:
            st.session_state.voss_file_unlocked = True
            if st.button("Open Dr. Voss's file", use_container_width=True, key="open_voss_file", type="primary"):
                st.session_state.voss_cutscene_stage = 0
                st.session_state.view = "voss_file"
                st.rerun()


    # Re-open Voss file if already earned
    if st.session_state.get("voss_file_unlocked") and not glitches_unlocked():
        if st.button("Open Dr. Voss's file", use_container_width=True, key="open_voss_always", type="primary"):
            st.session_state.voss_cutscene_stage = 0
            st.session_state.view = "voss_file"
            st.rerun()


    # Anomalies finished — no more hunting; reopen Voss file only
    if lab_is_unlocked() and anomalies_complete():
        ensure_voss_theme()
        st.markdown(
            """
            <div style="
              margin: 0 0 12px; padding: 12px 14px; border-radius: 12px;
              background: rgba(80,20,20,0.25); border: 1px solid rgba(180,60,60,0.4);
              color: #e8b0b0; font-family: ui-monospace, monospace; font-size: 0.82rem;
            ">
              Voss markers sealed · 3 / 3<br/>
              <span style="opacity:0.85;font-size:0.75rem;">The anomalies will not return. The file remains.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Dr. Voss's file", use_container_width=True, key="open_voss_home_done", type="primary"):
            st.session_state.voss_cutscene_stage = 0
            st.session_state.view = "voss_file"
            st.rerun()

    # —— Interactive feature toggles (actually work) ——
    prov = st.session_state.provider
    wiki_on = st.session_state.use_wiki_toggle
    web_on = st.session_state.use_web_toggle
    music_on = st.session_state.show_spotify

    # Row 1: Provider cycle + Wiki + Web + Music
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        prov_label = {
            "groq": "✧ Groq · ON",
            "grok": "✧ Grok · ON",
            "openrouter": "✧ OpenRouter · ON",
        }.get(prov, "✧ Provider")
        if st.button(prov_label, use_container_width=True, key="feat_prov",
                     type="primary"):
            order = ["groq", "grok", "openrouter"]
            i = order.index(prov) if prov in order else 0
            st.session_state.provider = order[(i + 1) % len(order)]
            if st.session_state.provider == "groq":
                st.session_state.model_name = "Smart · Llama 3.3 70B"
            elif st.session_state.provider == "grok":
                st.session_state.model_name = "Grok 4.5"
            else:
                st.session_state.model_name = "meta-llama/llama-3.3-70b-instruct:free"
            save_user_data()
            st.rerun()
    with f2:
        wlabel = "◈ Wiki · ON" if wiki_on else "◈ Wiki · OFF"
        if st.button(wlabel, use_container_width=True, key="feat_wiki",
                     type="primary" if wiki_on else "secondary"):
            st.session_state.use_wiki_toggle = not wiki_on
            save_user_data()
            st.rerun()
    with f3:
        weblabel = "🌐 Web · ON" if web_on else "🌐 Web · OFF"
        if st.button(weblabel, use_container_width=True, key="feat_web",
                     type="primary" if web_on else "secondary"):
            st.session_state.use_web_toggle = not web_on
            save_user_data()
            st.rerun()
    with f4:
        mlabel = "♫ Music · ON" if music_on else "♫ Music · OFF"
        if st.button(mlabel, use_container_width=True, key="feat_music",
                     type="primary" if music_on else "secondary"):
            st.session_state.show_spotify = not music_on
            save_user_data()
            st.rerun()

    st.caption(
        f"Provider **{st.session_state.provider}** · "
        f"Model **{st.session_state.model_name}** · "
        f"Wiki {'on' if st.session_state.use_wiki_toggle else 'off'} · "
        f"Web {'on' if st.session_state.use_web_toggle else 'off'}"
    )

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        if st.button("Start chat", use_container_width=True, key="h_chat", type="primary"):
            st.session_state.view = "chat"
            st.rerun()
    with b2:
        if st.button("＋ New", use_container_width=True, key="h_new"):
            create_new_chat()
            st.session_state.view = "chat"
            st.rerun()
    with b3:
        if st.button("◎ Listen", use_container_width=True, key="h_listen"):
            st.session_state.view = "listen"
            st.rerun()
    with b4:
        if st.button("☰ Menu", use_container_width=True, key="h_menu"):
            st.session_state.popup = True
            st.rerun()

    qotd, qotd_author = quote_of_the_day()
    c1, c2 = st.columns(2)
    with c1:
        # Single box = one button (label + quote + author + date/time)
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
        if st.session_state.show_spotify:
            render_spotify_panel("home")
    with c2:
        st.markdown('<div class="panel"><div class="panel-label">Chat history</div>', unsafe_allow_html=True)
        items = sorted(st.session_state.chats.items(), key=lambda x: x[1].get("created", ""), reverse=True)[:10]
        if not items:
            st.caption("No chats yet — start one.")
        for cid, data in items:
            msgs = data.get("messages") or []
            title = data.get("title") or "Untitled"
            preview = ""
            if msgs:
                last = msgs[-1].get("content", "")
                preview = (last[:60] + "…") if len(last) > 60 else last
                preview = preview.replace("\n", " ")
            n = len(msgs)
            label = f"{title}  ·  {n} msg"
            if preview:
                label = f"{title}\n{preview}"
            cols = st.columns([5, 1])
            with cols[0]:
                if st.button(label, key=f"h_{cid}", use_container_width=True):
                    st.session_state.current_chat_id = cid
                    st.session_state.view = "chat"
                    save_user_data()
                    st.rerun()
            with cols[1]:
                if st.button("Del", key=f"hd_{cid}", use_container_width=True, help="Delete chat"):
                    delete_chat(cid)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
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
