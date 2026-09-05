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
    from arg_story import arg_match, arg_reply, is_owner as _arg_is_owner, is_lab_entry
except Exception:
    def arg_match(prompt=""):
        return None
    def arg_reply(stage="", user_name=""):
        return ""
    def _arg_is_owner(username=""):
        return False
    def is_lab_entry(prompt=""):
        return False

def _owner_names() -> set:
    """Owner usernames. Handles are public; the password is never stored in source."""
    names = {"drae"}
    try:
        raw = ""
        try:
            raw = st.secrets.get("OWNER_NAMES", "") or ""
        except Exception:
            raw = ""
        if not raw:
            raw = os.getenv("OWNER_NAMES", "") or ""
        for part in str(raw).replace(";", ",").split(","):
            p = part.strip().lower()
            if p:
                names.add(p)
    except Exception:
        pass
    return names


def _owner_password() -> str:
    """Owner password from Streamlit secrets or env — never hardcoded in source."""
    try:
        pw = st.secrets.get("OWNER_PASSWORD", "")
        if isinstance(pw, str) and pw.strip():
            return pw.strip()
    except Exception:
        pass
    try:
        pw = os.getenv("OWNER_PASSWORD", "")
        if isinstance(pw, str) and pw.strip():
            return pw.strip()
    except Exception:
        pass
    return ""


# Public handle list (not a secret). Password lives only in secrets/env.
OWNER_NAMES = _owner_names()


def is_owner(username="") -> bool:
    """Owner is password-gated at sign-in. Also honor arg_story owner if present."""
    n = (username or "").strip().lower()
    if n in _owner_names():
        return True
    try:
        return bool(_arg_is_owner(username))
    except Exception:
        return False

try:
    from lab_view import render_lab as _external_render_lab
    def render_lab():
        try:
            return _external_render_lab()
        except Exception as _lab_err:
            return _render_lab_builtin(error=str(_lab_err))
except Exception:
    def render_lab():
        return _render_lab_builtin()


def _render_lab_builtin(error: str = ""):
    """Self-contained observation lab — hotspots, fragments, residual door."""
    if "lab_found" not in st.session_state or not isinstance(st.session_state.lab_found, list):
        st.session_state.lab_found = list(st.session_state.get("lab_found") or [])

    found = set(st.session_state.lab_found or [])

    LAB_HOTSPOTS = [
        ("hs_glass", "Observation glass", "Condensation on the inside. A palm print that is not yours."),
        ("hs_tray", "Open tray", "Needle, drip line, residual bloom sample — still warm."),
        ("hs_logbook", "Logbook", "Pages torn out. One margin: “do not separate the pair.”"),
        ("hs_locker", "Subject locker", "A red string. A name written until the pencil broke."),
        ("hs_speaker", "Dead speaker", "Static resolves into a breath pattern. Two signatures."),
        ("hs_door", "Residual door panel", "Key-slot cold. Archive channel waits for the right residual."),
    ]

    st.markdown(
        """
        <style>
          .lab-shell {
            max-width: 640px; margin: 0 auto 1rem;
            padding: 1.25rem 1.2rem 1.1rem;
            border-radius: 16px;
            border: 1px solid rgba(220,60,60,0.35);
            background:
              radial-gradient(ellipse at 20% 0%, rgba(180,40,40,0.18), transparent 55%),
              linear-gradient(165deg, rgba(18,8,8,0.95), rgba(8,4,4,0.98));
            box-shadow: 0 20px 50px rgba(0,0,0,0.45);
          }
          .lab-kicker {
            font-family: ui-monospace, monospace;
            font-size: 0.62rem; letter-spacing: 0.22em;
            color: #c05050; text-transform: uppercase; margin-bottom: 0.4rem;
          }
          .lab-title {
            font-family: Georgia, serif;
            font-size: 1.55rem; color: #f0d0d0;
            margin: 0 0 0.35rem; letter-spacing: -0.02em;
          }
          .lab-sub { color: #a08080; font-size: 0.9rem; line-height: 1.45; margin-bottom: 0.85rem; }
          .lab-frag {
            font-family: ui-monospace, monospace;
            font-size: 0.72rem; color: #e8a0a0; letter-spacing: 0.06em;
            margin-bottom: 0.75rem;
          }
          .lab-card {
            border: 1px solid rgba(180,60,60,0.28);
            background: rgba(20,8,8,0.65);
            border-radius: 12px;
            padding: 0.75rem 0.9rem;
            margin-bottom: 0.45rem;
            color: #e8c8c8;
            font-size: 0.9rem;
            line-height: 1.45;
          }
          .lab-card.found { border-color: rgba(94,234,212,0.35); }
          .lab-card .nm {
            font-family: ui-monospace, monospace;
            font-size: 0.65rem; letter-spacing: 0.14em;
            text-transform: uppercase; color: #c07070; margin-bottom: 0.2rem;
          }
        </style>
        <div class="lab-shell">
          <div class="lab-kicker">Observation Division · Lab</div>
          <div class="lab-title">Containment floor</div>
          <div class="lab-sub">
            Six residual hotspots. Touch each one. The Division is still listening.
          </div>
          <div class="lab-frag">Fragments secured: """
        + f"{len(found)} / 6</div></div>",
        unsafe_allow_html=True,
    )

    if error:
        st.caption(f"External lab module failed — builtin lab active. ({error[:120]})")

    top_l, top_r = st.columns(2)
    with top_l:
        if st.button("← Home", key="lab_builtin_home", use_container_width=True):
            st.session_state._currently_in_lab = False
            st.session_state.view = "home"
            st.rerun()
    with top_r:
        if st.button("Open board", key="lab_builtin_board", use_container_width=True):
            st.session_state.view = "board"
            st.rerun()

    for hid, name, blurb in LAB_HOTSPOTS:
        is_found = hid in found
        st.markdown(
            f"""
            <div class="lab-card {'found' if is_found else ''}">
              <div class="nm">{'Secured' if is_found else 'Unscanned'} · {name}</div>
              {blurb if is_found else 'Residual interference — scan to reveal.'}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not is_found:
            if st.button(f"Scan · {name}", key=f"lab_scan_{hid}", use_container_width=True):
                found.add(hid)
                st.session_state.lab_found = list(found)
                try:
                    play_glitch_sfx()
                except Exception:
                    pass
                if hid == "hs_glass":
                    try:
                        find_glitch("lab", "Voss log: lab marker secured.")
                    except Exception:
                        pass
                if len(found) >= 6:
                    try:
                        unlock_theme("Voss Static", "all fragments recovered", apply=False)
                    except Exception:
                        pass
                    st.session_state["_egg_flash"] = "All six lab fragments secured. Theme unlocked: Voss Static."
                try:
                    save_user_data()
                except Exception:
                    pass
                st.rerun()

    st.markdown("---")
    st.markdown("**Residual door**")
    has_key = bool(st.session_state.get("archive_key") or st.session_state.get("lab_door_unlocked"))
    if has_key:
        st.success("Door panel accepts residual key.")
        if st.button("Enter Project Nadir channel", key="lab_nadir_door", type="primary", use_container_width=True):
            st.session_state.lab_door_unlocked = True
            st.session_state.view = "nadir_door"
            st.rerun()
    else:
        st.caption("Door sealed. Recover the archive key from the investigation board (7/7), or the residual dial path.")

    # Lab glitch marker (2nd visit+)
    try:
        if glitches_unlocked() and "lab" not in set(st.session_state.get("glitches_found") or []):
            st.markdown(
                """
                <div style="margin-top:0.75rem;padding:0.65rem 0.8rem;border-radius:10px;
                  border:1px solid rgba(34,211,238,0.35);background:rgba(4,18,16,0.5);
                  font-family:ui-monospace,monospace;font-size:0.75rem;color:#5eead4;">
                  Voss field residual — interference in the glass
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Tap lab anomaly", key="glitch_lab_builtin"):
                try:
                    play_glitch_sfx()
                except Exception:
                    pass
                try:
                    find_glitch("lab", "Voss log: lab marker secured.")
                except Exception:
                    pass
                st.rerun()
    except Exception:
        pass

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

# Owner-only typefaces — not listed for regular users
OWNER_FONTS = {
    "Orbitron": "'Orbitron', system-ui, sans-serif",
    "Cinzel Decorative": "'Cinzel Decorative', Georgia, serif",
    "Press Start 2P": "'Press Start 2P', monospace",
    "Syncopate": "'Syncopate', system-ui, sans-serif",
    "Special Elite": "'Special Elite', Georgia, serif",
    "Audiowide": "'Audiowide', system-ui, sans-serif",
    "Monoton": "'Monoton', system-ui, sans-serif",
    "Bungee Shade": "'Bungee Shade', system-ui, sans-serif",
    "Silkscreen": "'Silkscreen', monospace",
    "UnifrakturMaguntia": "'UnifrakturMaguntia', Georgia, serif",
}

# Owner-exclusive palettes (not grantable to public; only owner picker)
OWNER_THEMES = {
    "Obsidian Crown": {
        "bg": "#050308", "panel": "rgba(18, 8, 28, 0.92)", "panel_solid": "#12081c",
        "border": "rgba(250, 204, 21, 0.35)", "text": "#fef9c3", "muted": "#a8a29e",
        "accent": "#facc15", "accent2": "#eab308", "accent_soft": "rgba(250,204,21,0.14)",
        "font": "Cinzel Decorative",
    },
    "Neon Abyss": {
        "bg": "#02010a", "panel": "rgba(8, 6, 30, 0.94)", "panel_solid": "#0a0820",
        "border": "rgba(34, 211, 238, 0.45)", "text": "#a5f3fc", "muted": "#67e8f9",
        "accent": "#22d3ee", "accent2": "#f0abfc", "accent_soft": "rgba(34,211,238,0.16)",
        "font": "Orbitron",
    },
    "Voidscript": {
        "bg": "#000000", "panel": "rgba(12, 12, 12, 0.95)", "panel_solid": "#0c0c0c",
        "border": "rgba(74, 222, 128, 0.4)", "text": "#86efac", "muted": "#4ade80",
        "accent": "#4ade80", "accent2": "#22c55e", "accent_soft": "rgba(74,222,128,0.14)",
        "font": "Press Start 2P",
    },
    "Architect Gold": {
        "bg": "#0c0904", "panel": "rgba(32, 24, 10, 0.9)", "panel_solid": "#1c1608",
        "border": "rgba(251, 191, 36, 0.4)", "text": "#fde68a", "muted": "#d6c08a",
        "accent": "#fbbf24", "accent2": "#f59e0b", "accent_soft": "rgba(251,191,36,0.15)",
        "font": "Syncopate",
    },
    "Typewriter Residual": {
        "bg": "#0a0a08", "panel": "rgba(28, 26, 20, 0.92)", "panel_solid": "#1a1814",
        "border": "rgba(214, 211, 209, 0.28)", "text": "#e7e5e4", "muted": "#a8a29e",
        "accent": "#d6d3d1", "accent2": "#a8a29e", "accent_soft": "rgba(214,211,209,0.12)",
        "font": "Special Elite",
    },
    "Synthwave Owner": {
        "bg": "#0b0214", "panel": "rgba(36, 10, 48, 0.9)", "panel_solid": "#200a2c",
        "border": "rgba(244, 114, 182, 0.45)", "text": "#fce7f3", "muted": "#e879f9",
        "accent": "#f472b6", "accent2": "#c084fc", "accent_soft": "rgba(244,114,182,0.16)",
        "font": "Audiowide",
    },
    "Monolith": {
        "bg": "#030303", "panel": "rgba(16, 16, 16, 0.96)", "panel_solid": "#101010",
        "border": "rgba(255,255,255,0.2)", "text": "#ffffff", "muted": "#a1a1aa",
        "accent": "#ffffff", "accent2": "#d4d4d8", "accent_soft": "rgba(255,255,255,0.08)",
        "font": "Monoton",
    },
    "Carnival Shade": {
        "bg": "#12040c", "panel": "rgba(40, 12, 28, 0.9)", "panel_solid": "#240c18",
        "border": "rgba(251, 113, 133, 0.4)", "text": "#ffe4e6", "muted": "#fda4af",
        "accent": "#fb7185", "accent2": "#fbbf24", "accent_soft": "rgba(251,113,133,0.15)",
        "font": "Bungee Shade",
    },
    "Terminal Green": {
        "bg": "#001400", "panel": "rgba(0, 24, 8, 0.94)", "panel_solid": "#001808",
        "border": "rgba(34, 197, 94, 0.45)", "text": "#bbf7d0", "muted": "#4ade80",
        "accent": "#22c55e", "accent2": "#16a34a", "accent_soft": "rgba(34,197,94,0.14)",
        "font": "Silkscreen",
    },
    "Gothic Residual": {
        "bg": "#08060a", "panel": "rgba(22, 16, 28, 0.94)", "panel_solid": "#140e1c",
        "border": "rgba(196, 181, 253, 0.35)", "text": "#ede9fe", "muted": "#c4b5fd",
        "accent": "#c4b5fd", "accent2": "#a78bfa", "accent_soft": "rgba(196,181,253,0.14)",
        "font": "UnifrakturMaguntia",
    },
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
    # Palisman soft — mint leaf / little green snake (not Caelestia purple)
    "Stringbean Soft": {
        "bg": "#06140c", "panel": "rgba(12, 36, 24, 0.88)", "panel_solid": "#0c2418",
        "border": "rgba(134,239,172,0.32)", "text": "#ecfdf5", "muted": "#86a896",
        "accent": "#86efac", "accent2": "#4ade80", "accent_soft": "rgba(134,239,172,0.18)",
        "unlock": "stringbean",
    },
    # Luz + Amity — dual glow: warm gold light + lilac witch fire
    "Lumity Glow": {
        "bg": "#12061a", "panel": "rgba(42, 16, 48, 0.90)", "panel_solid": "#2a1030",
        "border": "rgba(251,191,36,0.28)", "text": "#fff7ed", "muted": "#c4a0c8",
        "accent": "#f9a8d4", "accent2": "#fbbf24", "accent_soft": "rgba(249,168,212,0.20)",
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
    # Unlocked when Project Nadir / residual door opens — cold archive teal
    "Nadir Residual": {
        "bg": "#030806", "panel": "rgba(8, 22, 20, 0.92)", "panel_solid": "#0a1614",
        "border": "rgba(45, 212, 191, 0.28)", "text": "#e6fffa", "muted": "#6a9a90",
        "accent": "#2dd4bf", "accent2": "#0f766e", "accent_soft": "rgba(45, 212, 191, 0.16)",
        "unlock": "nadir",
    },
    # Drift Counter exclusive — copper dusk / archival bronze
    "Copper Vespers": {
        "bg": "#0c0806", "panel": "rgba(36, 22, 14, 0.88)", "panel_solid": "#1c120c",
        "border": "rgba(251, 146, 60, 0.32)", "text": "#ffedd5", "muted": "#c4a484",
        "accent": "#fb923c", "accent2": "#e11d48", "accent_soft": "rgba(251, 146, 60, 0.16)",
        "unlock": "drift",
    },
    # Drift Counter exclusive — deep indigo rain / wet glass
    "Indigo Rain": {
        "bg": "#060712", "panel": "rgba(14, 18, 40, 0.88)", "panel_solid": "#0c1020",
        "border": "rgba(129, 140, 248, 0.35)", "text": "#e0e7ff", "muted": "#94a3b8",
        "accent": "#818cf8", "accent2": "#38bdf8", "accent_soft": "rgba(129, 140, 248, 0.16)",
        "unlock": "drift",
    },
    # Shady Bazaar exclusive
    "Blood Archive": {
        "bg": "#0a0406", "panel": "rgba(36, 10, 14, 0.9)", "panel_solid": "#1c080c",
        "border": "rgba(239, 68, 68, 0.4)", "text": "#fee2e2", "muted": "#a87878",
        "accent": "#ef4444", "accent2": "#b91c1c", "accent_soft": "rgba(239,68,68,0.18)",
        "unlock": "bazaar",
    },
    "Queer Static": {
        "bg": "#0c0614", "panel": "rgba(32, 16, 48, 0.9)", "panel_solid": "#1a0e28",
        "border": "rgba(196, 167, 231, 0.4)", "text": "#faf5ff", "muted": "#c4a0d8",
        "accent": "#c4a7e7", "accent2": "#fbbf24", "accent_soft": "rgba(196,167,231,0.18)",
        "unlock": "bazaar",
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
                    || a.getAttribute('data-meridium-nadir')
                    || a.getAttribute('data-meridium-door')
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
            var roots = [window];
            try {{ if (window.parent && window.parent !== window) roots.push(window.parent); }} catch(e){{}}
            try {{ if (window.top && window.top !== window) roots.push(window.top); }} catch(e){{}}
            var tag = {tag_js};
            var key = '__mer_' + tag + '_song';
            function kill(a){{
              if (!a) return;
              try {{ a.pause(); }} catch(e){{}}
              try {{ a.currentTime = 0; }} catch(e){{}}
              try {{ a.src = ''; }} catch(e){{}}
              try {{ a.removeAttribute('src'); }} catch(e){{}}
              try {{ a.load(); }} catch(e){{}}
              try {{ a.remove(); }} catch(e){{}}
            }}
            for (var r = 0; r < roots.length; r++) {{
              var root = roots[r];
              try {{
                kill(root[key]);
                root[key] = null;
                var nodes = root.document.querySelectorAll(
                  'audio[data-meridium-' + tag + '], audio[data-meridium-nadir], audio[data-meridium-door]'
                );
                for (var i = 0; i < nodes.length; i++) kill(nodes[i]);
                // Nuke any audio whose src looks like Run Rabbit / Nadir archive track
                var all = root.document.querySelectorAll('audio');
                for (var j = 0; j < all.length; j++) {{
                  var s = (all[j].src || '') + '';
                  if (
                    s.indexOf('Run') !== -1 ||
                    s.indexOf('Rabbit') !== -1 ||
                    s.indexOf('RABBIT') !== -1 ||
                    s.indexOf('gbia0006719') !== -1 ||
                    s.indexOf('Flanagan') !== -1
                  ) kill(all[j]);
                }}
              }} catch(e){{}}
            }}
            var a = null; // silence leftover binding
            // legacy single-root path kept below for safety
            var root = window.parent || window;
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
    """Public themes + ARG unlocks + owner palettes (owner always; others if granted)."""
    unlocked = set(st.session_state.get("unlocked_themes") or [])
    names = list(THEMES.keys())
    for name in SECRET_THEMES:
        if name in unlocked:
            names.append(name)
    # Owner themes: architect always has them; others only if unlocked via grant
    for name in OWNER_THEMES:
        try:
            if is_owner(st.session_state.get("username") or "") or name in unlocked:
                if name not in names:
                    names.append(name)
        except Exception:
            if name in unlocked and name not in names:
                names.append(name)
    return names


def available_fonts() -> list:
    """Public fonts + owner display faces (owner, or user granted an owner theme)."""
    names = list(FONTS.keys())
    unlocked = set(st.session_state.get("unlocked_themes") or [])
    has_owner_theme = any(n in OWNER_THEMES for n in unlocked)
    try:
        if is_owner(st.session_state.get("username") or "") or has_owner_theme:
            for n in OWNER_FONTS:
                if n not in names:
                    names.append(n)
    except Exception:
        if has_owner_theme:
            for n in OWNER_FONTS:
                if n not in names:
                    names.append(n)
    return names


def theme_shell(theme_name: str) -> dict:
    if theme_name in THEMES:
        return dict(THEMES[theme_name])
    if theme_name in SECRET_THEMES:
        d = {k: v for k, v in SECRET_THEMES[theme_name].items() if k not in ("unlock", "font")}
        return d
    if theme_name in OWNER_THEMES:
        d = {k: v for k, v in OWNER_THEMES[theme_name].items() if k not in ("unlock", "font")}
        return d
    return dict(THEMES["Caelestia"])


def resolve_font_css(font_name: str, theme_name: str = "") -> str:
    """CSS font-family stack. Owner themes can pin a unique face."""
    unlocked = set(st.session_state.get("unlocked_themes") or [])
    can_owner_face = False
    try:
        can_owner_face = is_owner(st.session_state.get("username") or "") or any(
            n in OWNER_THEMES for n in unlocked
        )
    except Exception:
        can_owner_face = any(n in OWNER_THEMES for n in unlocked)

    if theme_name in OWNER_THEMES and (
        can_owner_face or theme_name in unlocked
    ):
        pinned = OWNER_THEMES[theme_name].get("font")
        if pinned and pinned in OWNER_FONTS:
            return OWNER_FONTS[pinned]
        if pinned and pinned in FONTS:
            return FONTS[pinned]
    if font_name in OWNER_FONTS and can_owner_face:
        return OWNER_FONTS[font_name]
    return FONTS.get(font_name, FONTS["Inter"])


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
    """Meridium Codex — total visual rewrite. Kinetic glass, signal fields, unique motion language."""
    try:
        unlocked = set(st.session_state.get("unlocked_themes") or [])
        is_own = is_owner(st.session_state.get("username") or "")
        if theme_name in OWNER_THEMES and not is_own and theme_name not in unlocked:
            theme_name = "Caelestia"
            st.session_state.theme = "Caelestia"
        if font_name in OWNER_FONTS and not is_own and not any(n in OWNER_THEMES for n in unlocked):
            font_name = "Inter"
            st.session_state.font = "Inter"
    except Exception:
        pass
    font = resolve_font_css(font_name, theme_name)
    SHELL = theme_shell(theme_name)

    A = SHELL["accent"]
    A2 = SHELL.get("accent2", A)
    soft = SHELL.get("accent_soft", "rgba(196,167,231,0.16)")
    border = SHELL.get("border", "rgba(255,255,255,0.12)")
    text = SHELL["text"]
    muted = SHELL["muted"]
    bg = SHELL["bg"]
    glass = SHELL.get("panel") or "rgba(22,22,30,0.68)"
    solid = SHELL.get("panel_solid") or bg

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=Outfit:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,600&family=Orbitron:wght@400;600;700&family=Cinzel+Decorative:wght@400;700&family=Press+Start+2P&family=Syncopate:wght@400;700&family=Special+Elite&family=Audiowide&family=Monoton&family=Bungee+Shade&family=Silkscreen&family=UnifrakturMaguntia&family=Syne:wght@600;700;800&family=Cormorant+Garamond:ital,wght@0,500;1,500;1,600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

    /* ════════════════════════════════════════════════════════════
       CODEX FOUNDATION — unique geometry + kinetic field
       ════════════════════════════════════════════════════════════ */
    :root {{
      --mer-a: {A};
      --mer-a2: {A2};
      --mer-soft: {soft};
      --mer-border: {border};
      --mer-text: {text};
      --mer-muted: {muted};
      --mer-bg: {bg};
      --mer-glass: {glass};
      --mer-solid: {solid};
      --mer-ease: cubic-bezier(0.22, 1, 0.36, 1);
      --mer-spring: cubic-bezier(0.34, 1.4, 0.64, 1);
    }}

    html, body, [class*="css"] {{
        font-family: {font} !important;
        font-size: 15px;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
    }}

    .stApp {{
        background:
            radial-gradient(ellipse 900px 520px at 8% -4%, {soft}, transparent 60%),
            radial-gradient(ellipse 700px 440px at 96% 4%, {soft}, transparent 55%),
            radial-gradient(ellipse 500px 300px at 50% 100%, {soft}, transparent 50%),
            linear-gradient(180deg, {bg} 0%, {bg} 100%) !important;
        color: {text};
        overflow-x: hidden;
    }}

    /* Animated signal mesh behind content */
    .stApp::before {{
        content: "";
        pointer-events: none;
        position: fixed;
        inset: 0;
        z-index: 0;
        opacity: 0.045;
        background-image:
            linear-gradient({A}33 1px, transparent 1px),
            linear-gradient(90deg, {A}33 1px, transparent 1px);
        background-size: 48px 48px;
        animation: codexGridDrift 28s linear infinite;
        mask-image: radial-gradient(ellipse at center, black 30%, transparent 85%);
        -webkit-mask-image: radial-gradient(ellipse at center, black 30%, transparent 85%);
    }}

    /* Floating orb field */
    .stApp::after {{
        content: "";
        pointer-events: none;
        position: fixed;
        width: 420px; height: 420px;
        border-radius: 50%;
        top: -120px; right: -100px;
        z-index: 0;
        background: radial-gradient(circle, {soft}, transparent 68%);
        animation: codexOrbFloat 14s ease-in-out infinite;
        filter: blur(2px);
    }}

    #MainMenu, footer, header, .stDeployButton, section[data-testid="stSidebar"],
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], [data-testid="stAppDeployButton"] {{
        display: none !important; visibility: hidden !important;
        height: 0 !important; opacity: 0 !important; pointer-events: none !important;
    }}

    .block-container {{
        position: relative;
        z-index: 1;
        padding-top: 1.05rem !important;
        padding-bottom: 6.2rem !important;
        max-width: 1000px !important;
        animation: codexBoot 0.7s var(--mer-ease) both;
    }}

    /* ════════════════════════════════════════════════════════════
       TYPE — sharper editorial scale
       ════════════════════════════════════════════════════════════ */
    h1, h2, h3, h4 {{
        letter-spacing: -0.04em !important;
        font-weight: 700 !important;
        line-height: 1.18 !important;
        color: {text} !important;
    }}
    p, li, label, .stMarkdown {{ line-height: 1.6 !important; }}
    .stMarkdown, .stMarkdown p {{ color: {text} !important; }}
    label, [data-testid="stWidgetLabel"] p, .stCaption, .muted {{
        color: {muted} !important;
    }}

    /* ════════════════════════════════════════════════════════════
       SURFACE SYSTEM — cut glass + beveled frames
       ════════════════════════════════════════════════════════════ */
    .panel, .waybar, .bookmark-rail, .hist, .bloom-shell, .card,
    .own-stat, .own-card, .codex-tile {{
        background: linear-gradient(155deg, {glass}, rgba(0,0,0,0.15)) !important;
        border: 1px solid {border} !important;
        border-radius: 20px !important;
        box-shadow:
            0 1px 0 rgba(255,255,255,0.08) inset,
            0 0 0 1px rgba(0,0,0,0.2) inset,
            0 22px 50px rgba(0,0,0,0.32),
            0 8px 18px rgba(0,0,0,0.18) !important;
        backdrop-filter: blur(26px) saturate(1.45) !important;
        -webkit-backdrop-filter: blur(26px) saturate(1.45) !important;
        position: relative;
    }}

    .panel {{
        padding: 1.35rem 1.45rem 1.2rem !important;
        margin-bottom: 1.05rem;
        overflow: hidden;
        animation: codexRise 0.65s var(--mer-ease) both;
        transition:
            transform 0.35s var(--mer-ease),
            border-color 0.3s ease,
            box-shadow 0.35s ease;
    }}
    .panel::before {{
        content: "";
        position: absolute;
        left: 12%; right: 12%; top: 0;
        height: 2px;
        border-radius: 2px;
        background: linear-gradient(90deg, transparent, {A}, {A2}, transparent);
        opacity: 0.75;
        animation: codexScanX 5.5s ease-in-out infinite;
    }}
    .panel::after {{
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(115deg, transparent 40%, rgba(255,255,255,0.045) 50%, transparent 60%);
        background-size: 220% 100%;
        animation: codexSheen 7s ease-in-out infinite;
        pointer-events: none;
    }}
    .panel:hover {{
        transform: translateY(-3px) scale(1.005);
        border-color: {A}66 !important;
        box-shadow:
            0 1px 0 rgba(255,255,255,0.1) inset,
            0 28px 60px rgba(0,0,0,0.38),
            0 0 40px {soft} !important;
    }}

    .panel-label {{
        font-family: ui-monospace, "JetBrains Mono", monospace !important;
        font-size: 0.62rem !important;
        letter-spacing: 0.24em !important;
        text-transform: uppercase !important;
        color: {muted} !important;
        margin-bottom: 0.6rem !important;
        font-weight: 600 !important;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    .panel-label::before {{
        content: "";
        width: 6px; height: 6px;
        border-radius: 50%;
        background: {A};
        box-shadow: 0 0 10px {A};
        animation: codexPulseDot 2.2s ease-in-out infinite;
        flex-shrink: 0;
    }}

    .ridge {{
        height: 1px !important;
        border: 0 !important;
        margin: 1rem 0 !important;
        background: linear-gradient(90deg, transparent, {A}, {A2}, transparent) !important;
        opacity: 0.55;
        animation: codexRidge 3.8s ease-in-out infinite;
        position: relative;
    }}

    /* ════════════════════════════════════════════════════════════
       HERO / STATUS
       ════════════════════════════════════════════════════════════ */
    .hero {{
        font-size: clamp(1.65rem, 3.8vw, 2.15rem);
        font-weight: 750;
        letter-spacing: -0.042em;
        margin: 0 0 0.45rem;
        color: {text};
        animation: codexTypeIn 0.8s var(--mer-ease) both;
        line-height: 1.15;
    }}
    .hero span {{
        background: linear-gradient(110deg, {A}, {A2}, {A});
        background-size: 200% auto;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: codexGradientShift 4s linear infinite;
    }}
    .sub {{
        color: {muted};
        margin-bottom: 0.85rem;
        font-size: 0.95rem;
        line-height: 1.55;
        animation: codexTypeIn 0.8s var(--mer-ease) 0.1s both;
    }}
    .home-status {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.35rem;
        animation: codexTypeIn 0.75s var(--mer-ease) 0.18s both;
    }}
    .pill, .home-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 0.32rem 0.85rem;
        border-radius: 999px;
        background: {soft} !important;
        border: 1px solid {border};
        color: {A} !important;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        transition: all 0.28s var(--mer-spring);
        animation: codexPop 0.5s var(--mer-spring) both;
    }}
    .pill:nth-child(1) {{ animation-delay: 0.2s; }}
    .pill:nth-child(2) {{ animation-delay: 0.28s; }}
    .pill:nth-child(3) {{ animation-delay: 0.36s; }}
    .pill:nth-child(4) {{ animation-delay: 0.44s; }}
    .pill:hover, .home-pill:hover {{
        transform: translateY(-3px) scale(1.06);
        border-color: {A};
        box-shadow: 0 8px 22px {soft}, 0 0 20px {soft};
    }}

    /* ════════════════════════════════════════════════════════════
       WAYBAR / RAIL
       ════════════════════════════════════════════════════════════ */
    .waybar {{
        display: flex; align-items: center; justify-content: space-between;
        gap: 12px; padding: 12px 18px; margin-bottom: 14px;
        animation: codexRise 0.55s var(--mer-ease) both;
    }}
    .waybar-left, .waybar-right {{
        display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
    }}
    .logo-btn {{
        width: 38px; height: 38px; border-radius: 12px;
        background: linear-gradient(135deg, {A}, {A2});
        display: flex; align-items: center; justify-content: center;
        color: #0a0a0e; font-weight: 800; font-size: 1rem;
        box-shadow: 0 0 28px {soft};
        animation: codexLogoSpin 8s linear infinite, codexGlow 2.8s ease-in-out infinite;
        position: relative;
    }}
    .logo-btn::after {{
        content: "";
        position: absolute; inset: -4px;
        border-radius: 14px;
        border: 1px solid {A}44;
        animation: codexRing 2.8s ease-in-out infinite;
    }}
    .brand {{ font-weight: 700; letter-spacing: -0.025em; }}
    .chip {{
        background: {soft} !important; color: {A} !important;
        border: 1px solid {border} !important; border-radius: 999px;
        padding: 4px 12px; font-size: 0.72rem; font-weight: 600;
        backdrop-filter: blur(10px);
    }}
    .clock {{ font-weight: 650; font-variant-numeric: tabular-nums; }}

    .bookmark-rail {{
        padding: 18px 13px 15px !important;
        margin-bottom: 14px;
        position: sticky; top: 0.5rem;
        animation: codexRailIn 0.7s var(--mer-ease) both;
        overflow: hidden;
    }}
    .bookmark-rail::before {{
        content: "";
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, {A}, {A2}, transparent);
        animation: codexRailBar 3s ease-in-out infinite;
        border-radius: 0 2px 2px 0;
    }}
    .bookmark-rail .panel-label {{
        margin-bottom: 14px !important;
        padding: 0 8px;
    }}
    .bookmark-rail div[data-testid="stButton"] button {{
        text-align: left !important;
        justify-content: flex-start !important;
        padding-left: 14px !important;
        font-size: 0.88rem !important;
        min-height: 44px !important;
        border-radius: 14px !important;
        margin-bottom: 6px !important;
        background: rgba(255,255,255,0.025) !important;
        position: relative;
        overflow: hidden;
        transition: all 0.3s var(--mer-ease) !important;
    }}
    .bookmark-rail div[data-testid="stButton"] button::before {{
        content: "";
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 0;
        background: {soft};
        transition: width 0.3s var(--mer-ease);
        z-index: 0;
    }}
    .bookmark-rail div[data-testid="stButton"] button:hover {{
        transform: translateX(8px) !important;
        border-color: {A} !important;
        color: {A} !important;
        box-shadow: 0 10px 28px {soft} !important;
    }}
    .bookmark-rail div[data-testid="stButton"] button:hover::before {{
        width: 100%;
    }}

    /* ════════════════════════════════════════════════════════════
       CARDS / BUTTONS / INPUTS
       ════════════════════════════════════════════════════════════ */
    .card {{
        padding: 17px;
        transition: all 0.35s var(--mer-ease);
        animation: codexRise 0.6s var(--mer-ease) both;
    }}
    .card:hover {{
        transform: translateY(-5px) rotate(-0.3deg);
        border-color: {A} !important;
        box-shadow: 0 24px 52px rgba(0,0,0,0.35), 0 0 32px {soft} !important;
    }}

    .stButton > button {{
        background: linear-gradient(160deg, {glass}, rgba(0,0,0,0.12)) !important;
        color: {text} !important;
        border: 1px solid {border} !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        min-height: 44px !important;
        letter-spacing: -0.01em;
        backdrop-filter: blur(16px) saturate(1.3) !important;
        -webkit-backdrop-filter: blur(16px) saturate(1.3) !important;
        position: relative;
        overflow: hidden;
        transition: all 0.28s var(--mer-spring) !important;
    }}
    .stButton > button::after {{
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(120deg, transparent, rgba(255,255,255,0.08), transparent);
        transform: translateX(-120%);
        transition: transform 0.5s ease;
    }}
    .stButton > button:hover {{
        border-color: {A} !important;
        background: {soft} !important;
        color: {A} !important;
        transform: translateY(-3px) scale(1.015);
        box-shadow: 0 14px 32px {soft} !important;
    }}
    .stButton > button:hover::after {{
        transform: translateX(120%);
    }}
    .stButton > button:active {{
        transform: translateY(0) scale(0.97);
    }}
    .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"] {{
        background: linear-gradient(135deg, {soft}, rgba(0,0,0,0.15)) !important;
        border: 1px solid {A} !important;
        color: {A} !important;
        box-shadow: 0 0 0 0 {soft}, 0 10px 28px {soft} !important;
        animation: codexPrimaryPulse 3.2s ease-in-out infinite;
        font-weight: 650 !important;
    }}
    .stButton > button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover {{
        filter: brightness(1.1);
        box-shadow: 0 0 24px {soft}, 0 14px 36px {soft} !important;
    }}

    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox > div > div,
    [data-baseweb="select"] > div {{
        background: {glass} !important;
        color: {text} !important;
        border: 1px solid {border} !important;
        border-radius: 14px !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        transition: all 0.25s ease !important;
    }}
    .stTextInput input:focus,
    .stTextArea textarea:focus {{
        border-color: {A} !important;
        box-shadow: 0 0 0 3px {soft}, 0 0 24px {soft} !important;
        outline: none !important;
        animation: codexFocusFlash 0.4s ease;
    }}
    .stCheckbox label p {{ color: {text} !important; }}

    /* ════════════════════════════════════════════════════════════
       CHAT — kinetic messages
       ════════════════════════════════════════════════════════════ */
    [data-testid="stChatMessage"],
    .stChatMessage {{
        background: linear-gradient(160deg, {glass}, rgba(0,0,0,0.1)) !important;
        border: 1px solid {border} !important;
        border-radius: 20px !important;
        padding: 0.55rem 0.35rem !important;
        backdrop-filter: blur(20px) saturate(1.35) !important;
        -webkit-backdrop-filter: blur(20px) saturate(1.35) !important;
        animation: codexMsgIn 0.45s var(--mer-spring) both !important;
        transition: all 0.3s ease !important;
        overflow: hidden;
    }}
    [data-testid="stChatMessage"]::before {{
        content: "";
        position: absolute;
        left: 0; top: 15%; bottom: 15%;
        width: 3px;
        border-radius: 2px;
        background: linear-gradient(180deg, {A}, {A2});
        opacity: 0.5;
    }}
    [data-testid="stChatMessage"]:hover {{
        border-color: {A}50 !important;
        transform: translateX(3px);
        box-shadow: 0 14px 36px rgba(0,0,0,0.25), 0 0 20px {soft} !important;
    }}
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"],
    [data-testid="stChatAvatar"] {{ display: none !important; }}

    [data-testid="stBottomBlockContainer"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}
    [data-testid="stChatInput"] {{
        background: {glass} !important;
        border: 1px solid {border} !important;
        border-radius: 26px !important;
        box-shadow: 0 16px 40px rgba(0,0,0,0.32), 0 0 0 1px rgba(255,255,255,0.04) inset !important;
        padding: 7px 14px !important;
        overflow: hidden !important;
        backdrop-filter: blur(28px) saturate(1.5) !important;
        -webkit-backdrop-filter: blur(28px) saturate(1.5) !important;
        transition: all 0.3s var(--mer-ease) !important;
        animation: codexComposerIn 0.6s var(--mer-ease) both;
    }}
    [data-testid="stChatInput"]:focus-within {{
        border-color: {A} !important;
        box-shadow: 0 0 0 3px {soft}, 0 18px 48px rgba(0,0,0,0.35), 0 0 40px {soft} !important;
        transform: translateY(-2px);
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
        color: {text} !important;
        border: none !important;
        outline: none !important;
        caret-color: {A} !important;
    }}
    [data-testid="stChatInput"] textarea::placeholder {{ color: {muted} !important; }}
    [data-testid="stChatInput"] button {{
        background: transparent !important;
        border: none !important;
        color: {A} !important;
        transition: transform 0.2s var(--mer-spring) !important;
    }}
    [data-testid="stChatInput"] button:hover {{
        transform: scale(1.15) rotate(-8deg);
    }}

    /* ════════════════════════════════════════════════════════════
       ALERTS / BLOOM / QOTD
       ════════════════════════════════════════════════════════════ */
    [data-testid="stAlert"] {{
        background: {glass} !important;
        color: {text} !important;
        border: 1px solid {border} !important;
        border-radius: 16px !important;
        backdrop-filter: blur(18px) !important;
        animation: codexShakeIn 0.5s var(--mer-spring) both;
    }}

    .bloom-shell {{
        max-width: 480px;
        margin: 12px auto 26px;
        padding: 34px 28px 26px;
        animation: codexRise 0.55s var(--mer-ease) both;
    }}
    .bloom-title {{
        font-size: 1.85rem; font-weight: 750; text-align: center;
        color: {text}; margin: 0 0 8px; letter-spacing: -0.035em;
        animation: codexTypeIn 0.7s var(--mer-ease) both;
    }}
    .bloom-sub {{
        text-align: center; color: {muted}; font-size: 0.88rem; margin-bottom: 20px;
        animation: codexTypeIn 0.7s var(--mer-ease) 0.1s both;
    }}
    .bloom-divider {{
        height: 1px; margin: 14px 0;
        background: linear-gradient(90deg, transparent, {A}, transparent);
        opacity: 0.55;
        animation: codexRidge 3s ease-in-out infinite;
    }}

    .qotd-one button {{
        background: linear-gradient(160deg, {glass}, rgba(0,0,0,0.1)) !important;
        border: 1px solid {border} !important;
        border-radius: 20px !important;
        box-shadow: 0 16px 40px rgba(0,0,0,0.24) !important;
        text-align: left !important;
        white-space: pre-wrap !important;
        color: inherit !important;
        padding: 18px 20px !important;
        height: auto !important;
        min-height: 0 !important;
        justify-content: flex-start !important;
        line-height: 1.52 !important;
        backdrop-filter: blur(22px) saturate(1.4) !important;
        -webkit-backdrop-filter: blur(22px) saturate(1.4) !important;
        transition: all 0.35s var(--mer-ease) !important;
        animation: codexRise 0.6s var(--mer-ease) 0.15s both;
        position: relative;
        overflow: hidden;
    }}
    .qotd-one button::before {{
        content: "";
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, {A}, {A2});
        opacity: 0.7;
    }}
    .qotd-one button:hover {{
        border-color: {A} !important;
        background: {soft} !important;
        transform: translateY(-4px) scale(1.01);
        box-shadow: 0 22px 50px rgba(0,0,0,0.32), 0 0 36px {soft} !important;
    }}
    .qotd-one button p {{
        text-align: left !important;
        white-space: pre-wrap !important;
        margin: 0 !important;
    }}

    .hist {{ padding: 13px 15px; margin-bottom: 8px; }}

    /* ════════════════════════════════════════════════════════════
       ORB / TYPING
       ════════════════════════════════════════════════════════════ */
    .orb {{
        width: 100px; height: 100px;
        margin: 24px auto;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 28%, {A}, {A2} 55%, transparent 72%);
        box-shadow: 0 0 50px {soft}, 0 0 100px {soft};
        animation: codexOrb 2.6s ease-in-out infinite, codexOrbSpin 12s linear infinite;
        position: relative;
    }}
    .orb::before {{
        content: "";
        position: absolute; inset: -8px;
        border-radius: 50%;
        border: 1px dashed {A}55;
        animation: codexOrbSpin 8s linear infinite reverse;
    }}
    .orb::after {{
        content: "";
        position: absolute; inset: -16px;
        border-radius: 50%;
        border: 1px solid {A}22;
        animation: codexRing 2.6s ease-in-out infinite;
    }}

    .typing-wrap {{ display: inline-flex; gap: 8px; padding: 8px 4px; }}
    .typing-wrap .dot {{
        width: 9px; height: 9px;
        border-radius: 50%;
        background: {A};
        animation: codexBounce 1.15s ease-in-out infinite;
        box-shadow: 0 0 12px {A};
    }}
    .typing-wrap .dot:nth-child(2) {{ animation-delay: 0.15s; }}
    .typing-wrap .dot:nth-child(3) {{ animation-delay: 0.3s; }}

    /* ════════════════════════════════════════════════════════════
       OWNER DESK — command theater
       ════════════════════════════════════════════════════════════ */
    .drae-desk {{
        position: relative;
        padding: 1.65rem 1.55rem 1.35rem !important;
        border-radius: 24px !important;
        overflow: hidden;
        border: 1px solid rgba(196,167,231,0.4) !important;
        background:
            radial-gradient(ellipse at 0% 0%, rgba(244,114,182,0.2), transparent 50%),
            radial-gradient(ellipse at 100% 0%, rgba(167,139,250,0.24), transparent 52%),
            radial-gradient(ellipse at 50% 120%, rgba(45,212,191,0.1), transparent 45%),
            linear-gradient(165deg, rgba(18,10,28,0.85) 0%, rgba(8,6,14,0.9) 100%) !important;
        box-shadow:
            0 1px 0 rgba(255,255,255,0.08) inset,
            0 32px 70px rgba(0,0,0,0.48) !important;
        backdrop-filter: blur(32px) saturate(1.5) !important;
        -webkit-backdrop-filter: blur(32px) saturate(1.5) !important;
        margin-bottom: 1.1rem !important;
        animation: codexRise 0.65s var(--mer-ease) both;
    }}
    .drae-desk::before {{
        content: "";
        position: absolute;
        left: 0; right: 0; top: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #c4a7e7, #f472b6, #a78bfa, transparent);
        animation: codexScanX 4s ease-in-out infinite;
    }}
    .drae-desk::after {{
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(105deg, transparent 30%, rgba(255,255,255,0.04) 48%, transparent 65%);
        background-size: 200% 100%;
        animation: codexSheen 6s ease-in-out infinite;
        pointer-events: none;
    }}
    .drae-desk .kicker {{
        font-family: ui-monospace, monospace;
        font-size: 0.62rem;
        letter-spacing: 0.3em;
        color: #c4a7e7;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
        font-weight: 650;
        animation: codexTypeIn 0.6s var(--mer-ease) both;
    }}
    .drae-desk .title {{
        font-family: Syne, system-ui, sans-serif;
        font-weight: 800;
        font-size: clamp(1.65rem, 4.2vw, 2.15rem);
        color: #faf5ff;
        letter-spacing: -0.03em;
        margin: 0 0 0.45rem;
        line-height: 1.12;
        animation: codexTypeIn 0.7s var(--mer-ease) 0.08s both;
    }}
    .drae-desk .line {{
        font-family: "Cormorant Garamond", Georgia, serif;
        font-style: italic;
        font-size: 1.1rem;
        color: rgba(230,220,250,0.8);
        line-height: 1.45;
        max-width: 40rem;
        animation: codexTypeIn 0.7s var(--mer-ease) 0.16s both;
    }}
    .drae-desk .sig {{
        margin-top: 0.9rem;
        font-family: ui-monospace, monospace;
        font-size: 0.64rem;
        letter-spacing: 0.16em;
        color: rgba(196,167,231,0.48);
        text-transform: uppercase;
        animation: codexTypeIn 0.6s var(--mer-ease) 0.24s both;
    }}

    .own-stat {{
        padding: 1.1rem 0.95rem !important;
        border-radius: 18px !important;
        text-align: center;
        transition: all 0.35s var(--mer-spring);
        animation: codexPop 0.55s var(--mer-spring) both;
        overflow: hidden;
    }}
    .own-stat:hover {{
        transform: translateY(-5px) scale(1.03);
        border-color: rgba(196,167,231,0.5) !important;
        box-shadow: 0 18px 40px rgba(0,0,0,0.3), 0 0 28px rgba(167,139,250,0.15) !important;
    }}
    .own-stat .n {{
        font-family: Syne, system-ui, sans-serif;
        font-size: 1.7rem;
        font-weight: 800;
        color: #f5edff;
        letter-spacing: -0.03em;
        line-height: 1.05;
        background: linear-gradient(120deg, #faf5ff, #c4a7e7);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .own-stat .l {{
        font-size: 0.66rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        opacity: 0.55;
        margin-top: 5px;
        color: #c4b5fd;
        font-weight: 600;
    }}
    .own-section-label {{
        font-family: ui-monospace, monospace;
        font-size: 0.62rem;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: rgba(196,167,231,0.72);
        margin: 1.15rem 0 0.6rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    .own-section-label::before {{
        content: "";
        width: 8px; height: 8px;
        border: 1.5px solid #c4a7e7;
        border-radius: 2px;
        transform: rotate(45deg);
        animation: codexDiamond 3s ease-in-out infinite;
        flex-shrink: 0;
    }}

    [data-testid="stTabs"] [data-baseweb="tab-list"] {{
        gap: 6px !important;
        background: transparent !important;
        border-bottom: 1px solid {border} !important;
        padding-bottom: 8px !important;
        margin-bottom: 0.85rem !important;
    }}
    [data-testid="stTabs"] [data-baseweb="tab"] {{
        border-radius: 12px !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        color: {muted} !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        transition: all 0.25s var(--mer-ease) !important;
    }}
    [data-testid="stTabs"] [data-baseweb="tab"]:hover {{
        color: {text} !important;
        background: {soft} !important;
        transform: translateY(-2px);
    }}
    [data-testid="stTabs"] [aria-selected="true"] {{
        color: {A} !important;
        background: {soft} !important;
        border-color: {A}55 !important;
        box-shadow: 0 0 20px {soft};
    }}

    .mer-now-playing, .mer-now-playing strong, .mer-now-playing span {{ color: #4ade80 !important; }}
    .mer-now-playing .mer-now-sub {{ color: #86efac !important; opacity: 0.9; font-size: 0.82rem; }}
    .mer-now-playing .mer-now-badge {{ color: #86efac !important; font-size: 0.75rem; font-weight: 500; margin-left: 6px; }}

    /* ════════════════════════════════════════════════════════════
       KEYFRAMES — dense motion library
       ════════════════════════════════════════════════════════════ */
    @keyframes codexBoot {{
        from {{ opacity: 0; transform: translateY(16px) scale(0.99); filter: blur(4px); }}
        to   {{ opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }}
    }}
    @keyframes codexRise {{
        from {{ opacity: 0; transform: translateY(22px) scale(0.96); }}
        to   {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}
    @keyframes codexTypeIn {{
        from {{ opacity: 0; transform: translateY(14px); filter: blur(6px); }}
        to   {{ opacity: 1; transform: translateY(0); filter: blur(0); }}
    }}
    @keyframes codexRailIn {{
        from {{ opacity: 0; transform: translateX(-28px) scale(0.97); }}
        to   {{ opacity: 1; transform: translateX(0) scale(1); }}
    }}
    @keyframes codexMsgIn {{
        from {{ opacity: 0; transform: translateY(16px) scale(0.96) rotate(-0.5deg); }}
        to   {{ opacity: 1; transform: translateY(0) scale(1) rotate(0); }}
    }}
    @keyframes codexPop {{
        from {{ opacity: 0; transform: scale(0.85); }}
        to   {{ opacity: 1; transform: scale(1); }}
    }}
    @keyframes codexComposerIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes codexShakeIn {{
        0% {{ opacity: 0; transform: translateX(-8px); }}
        40% {{ transform: translateX(4px); }}
        70% {{ transform: translateX(-2px); }}
        100% {{ opacity: 1; transform: translateX(0); }}
    }}
    @keyframes codexFocusFlash {{
        0% {{ box-shadow: 0 0 0 0 {soft}; }}
        50% {{ box-shadow: 0 0 0 6px {soft}; }}
        100% {{ box-shadow: 0 0 0 3px {soft}; }}
    }}
    @keyframes codexScanX {{
        0%, 100% {{ opacity: 0.35; transform: scaleX(0.6); }}
        50% {{ opacity: 1; transform: scaleX(1); }}
    }}
    @keyframes codexSheen {{
        0% {{ background-position: 120% 0; }}
        100% {{ background-position: -20% 0; }}
    }}
    @keyframes codexRidge {{
        0%, 100% {{ opacity: 0.25; filter: brightness(0.9); }}
        50% {{ opacity: 0.85; filter: brightness(1.3); }}
    }}
    @keyframes codexPulseDot {{
        0%, 100% {{ opacity: 0.5; transform: scale(1); box-shadow: 0 0 6px {A}; }}
        50% {{ opacity: 1; transform: scale(1.35); box-shadow: 0 0 16px {A}; }}
    }}
    @keyframes codexGlow {{
        0%, 100% {{ box-shadow: 0 0 22px {soft}; }}
        50% {{ box-shadow: 0 0 40px {soft}, 0 0 60px {soft}; }}
    }}
    @keyframes codexRing {{
        0%, 100% {{ opacity: 0.3; transform: scale(1); }}
        50% {{ opacity: 0.8; transform: scale(1.08); }}
    }}
    @keyframes codexLogoSpin {{
        from {{ filter: hue-rotate(0deg); }}
        to {{ filter: hue-rotate(20deg); }}
    }}
    @keyframes codexOrb {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.08); }}
    }}
    @keyframes codexOrbSpin {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    @keyframes codexOrbFloat {{
        0%, 100% {{ transform: translate(0, 0); }}
        50% {{ transform: translate(-40px, 30px); }}
    }}
    @keyframes codexBounce {{
        0%, 60%, 100% {{ transform: translateY(0); opacity: 0.35; }}
        30% {{ transform: translateY(-10px); opacity: 1; }}
    }}
    @keyframes codexGradientShift {{
        0% {{ background-position: 0% center; }}
        100% {{ background-position: 200% center; }}
    }}
    @keyframes codexPrimaryPulse {{
        0%, 100% {{ box-shadow: 0 0 0 0 {soft}, 0 10px 28px {soft}; }}
        50% {{ box-shadow: 0 0 0 6px transparent, 0 12px 32px {soft}; }}
    }}
    @keyframes codexRailBar {{
        0%, 100% {{ opacity: 0.4; }}
        50% {{ opacity: 1; }}
    }}
    @keyframes codexGridDrift {{
        from {{ background-position: 0 0; }}
        to {{ background-position: 48px 48px; }}
    }}
    @keyframes codexDiamond {{
        0%, 100% {{ transform: rotate(45deg) scale(1); opacity: 0.6; }}
        50% {{ transform: rotate(45deg) scale(1.25); opacity: 1; }}
    }}
    @keyframes codexFloat {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-7px); }}
    }}

    .panel:nth-child(1) {{ animation-delay: 0.03s; }}
    .panel:nth-child(2) {{ animation-delay: 0.1s; }}
    .panel:nth-child(3) {{ animation-delay: 0.17s; }}
    .panel:nth-child(4) {{ animation-delay: 0.24s; }}
    .own-stat:nth-child(1) {{ animation-delay: 0.08s; }}
    .own-stat:nth-child(2) {{ animation-delay: 0.14s; }}
    .own-stat:nth-child(3) {{ animation-delay: 0.2s; }}
    .own-stat:nth-child(4) {{ animation-delay: 0.26s; }}
    .own-stat:nth-child(5) {{ animation-delay: 0.32s; }}

    * {{ scrollbar-width: thin; scrollbar-color: {A}55 transparent; }}
    ::selection {{ background: {A}55; color: {text}; }}
    iframe {{ background: transparent !important; border: none !important; }}

    @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }}
    }}
    @media (max-width: 720px) {{
        .block-container {{
            padding-top: 0.8rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }}
        .hero {{ font-size: 1.45rem; }}
        .bookmark-rail {{ position: relative; top: 0; }}
        .drae-desk {{ padding: 1.25rem 1.1rem !important; }}
        .own-stat .n {{ font-size: 1.35rem; }}
        .stApp::before {{ opacity: 0.03; }}
    }}
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


PRESENCE_FILE = DATA_DIR / "presence.json"
OWNER_GRANTS_FILE = DATA_DIR / "owner_grants.json"


def _presence_load() -> dict:
    try:
        if PRESENCE_FILE.exists():
            data = json.loads(PRESENCE_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def _presence_save(data: dict) -> None:
    try:
        PRESENCE_FILE.write_text(json.dumps(data, indent=0), encoding="utf-8")
    except Exception:
        pass


def presence_heartbeat() -> None:
    """Record this session as online (shared JSON)."""
    name = (st.session_state.get("username") or "").strip()
    if not name or not st.session_state.get("signed_in"):
        return
    sid = st.session_state.get("_presence_sid")
    if not sid:
        sid = uuid.uuid4().hex[:12]
        st.session_state._presence_sid = sid
    data = _presence_load()
    data[sid] = {
        "username": name,
        "view": st.session_state.get("view") or "home",
        "last_seen": datetime.now().isoformat(),
        "title": st.session_state.get("owner_title") or "",
        "theme": st.session_state.get("theme") or "Caelestia",
        "is_owner": bool(is_owner(name)),
    }
    # Drop stale sessions (> 90s)
    now = datetime.now()
    cleaned = {}
    for k, v in data.items():
        try:
            ts = datetime.fromisoformat(str(v.get("last_seen")))
            if (now - ts).total_seconds() <= 90:
                cleaned[k] = v
        except Exception:
            pass
    _presence_save(cleaned)


def presence_online(max_age_sec: int = 75) -> list:
    """Return list of online presence records (newest activity first)."""
    data = _presence_load()
    now = datetime.now()
    rows = []
    for sid, v in data.items():
        if not isinstance(v, dict):
            continue
        try:
            ts = datetime.fromisoformat(str(v.get("last_seen")))
            age = (now - ts).total_seconds()
        except Exception:
            continue
        if age <= max_age_sec:
            rows.append({**v, "session_id": sid, "age_sec": int(age)})
    rows.sort(key=lambda r: r.get("age_sec", 999))
    return rows


def owner_grants_load() -> dict:
    try:
        if OWNER_GRANTS_FILE.exists():
            d = json.loads(OWNER_GRANTS_FILE.read_text(encoding="utf-8"))
            if isinstance(d, dict):
                return d
    except Exception:
        pass
    return {}


def owner_grants_save(data: dict) -> None:
    try:
        OWNER_GRANTS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


def apply_owner_grants_for_user(username: str) -> None:
    """Pull any owner-granted theme/title/residuum into this session."""
    name = (username or "").strip().lower()
    if not name:
        return
    all_grants = owner_grants_load()
    grants = all_grants.get(name) or {}
    if not isinstance(grants, dict):
        return
    title = grants.get("title")
    if title:
        st.session_state.owner_title = str(title)[:48]
    themes = grants.get("themes") or []
    if isinstance(themes, list) and themes:
        unlocked = list(st.session_state.get("unlocked_themes") or [])
        for th in themes:
            if th and th not in unlocked:
                unlocked.append(th)
        st.session_state.unlocked_themes = unlocked
    if grants.get("force_theme") and grants.get("force_theme") in {**THEMES, **SECRET_THEMES}:
        # Only apply force once per session unless owner re-grants
        if not st.session_state.get("_owner_force_theme_applied"):
            st.session_state.theme = grants["force_theme"]
            st.session_state._owner_force_theme_applied = True
    # Pending Residuum gifts — claim once, then clear from grants file
    pending = grants.get("residuum_pending")
    try:
        pending_n = int(pending or 0)
    except Exception:
        pending_n = 0
    if pending_n:
        try:
            _ensure_economy()
        except Exception:
            if "residuum" not in st.session_state:
                st.session_state.residuum = 0
        st.session_state.residuum = int(st.session_state.get("residuum") or 0) + pending_n
        grants = dict(grants)
        grants.pop("residuum_pending", None)
        # Drop empty grant entries
        if not grants.get("themes") and not grants.get("force_theme") and not grants.get("title") and not grants.get("residuum_pending"):
            all_grants.pop(name, None)
        else:
            all_grants[name] = grants
        try:
            owner_grants_save(all_grants)
        except Exception:
            pass
        st.session_state["_egg_flash"] = (
            f"Owner gift received: **+{pending_n} Residuum**"
        )
        try:
            save_user_data()
        except Exception:
            pass


def owner_gift_residuum(username: str, amount: int) -> str:
    """Queue Residuum for a user (applied on their next load). If they are this session, apply now."""
    name = (username or "").strip().lower()
    if not name:
        return "empty"
    try:
        amount = int(amount)
    except Exception:
        return "bad_amount"
    if amount == 0:
        return "zero"
    # Cap single gifts to avoid accidents
    if amount > 10000:
        amount = 10000
    if amount < -10000:
        amount = -10000
    grants = owner_grants_load()
    entry = dict(grants.get(name) or {})
    try:
        pending = int(entry.get("residuum_pending") or 0)
    except Exception:
        pending = 0
    entry["residuum_pending"] = pending + amount
    grants[name] = entry
    owner_grants_save(grants)
    # Live apply if gifting the current signed-in user
    me = (st.session_state.get("username") or "").strip().lower()
    if me == name and st.session_state.get("signed_in"):
        apply_owner_grants_for_user(name)
    return "ok"


CHATROOM_FILE = DATA_DIR / "owner_chatroom.json"


def chatroom_load() -> dict:
    try:
        if CHATROOM_FILE.exists():
            d = json.loads(CHATROOM_FILE.read_text(encoding="utf-8"))
            if isinstance(d, dict):
                d.setdefault("members", [])
                d.setdefault("pending", [])
                d.setdefault("messages", [])
                return d
    except Exception:
        pass
    return {"members": [], "pending": [], "messages": [], "updated": None}


def chatroom_save(data: dict) -> None:
    try:
        data["updated"] = datetime.now().isoformat()
        CHATROOM_FILE.write_text(json.dumps(data, indent=0), encoding="utf-8")
    except Exception:
        pass


def chatroom_ensure_owner(owner_name: str) -> dict:
    room = chatroom_load()
    members = [m.lower() for m in (room.get("members") or []) if m]
    on = (owner_name or "").strip().lower()
    if on and on not in members:
        members.insert(0, on)
        room["members"] = members
        chatroom_save(room)
    return room


def chatroom_invite(username: str) -> str:
    """Create a pending invite. Returns status: invited | already_member | already_pending | empty."""
    room = chatroom_load()
    members = [m.lower() for m in (room.get("members") or []) if m]
    pending = [m.lower() for m in (room.get("pending") or []) if m]
    u = (username or "").strip().lower()
    if not u:
        return "empty"
    if u in members:
        return "already_member"
    if u in pending:
        return "already_pending"
    pending.append(u)
    room["pending"] = pending[:40]
    chatroom_save(room)
    return "invited"


def chatroom_has_pending(username: str) -> bool:
    u = (username or "").strip().lower()
    if not u:
        return False
    room = chatroom_load()
    pending = [m.lower() for m in (room.get("pending") or []) if m]
    return u in pending


def chatroom_accept(username: str) -> bool:
    room = chatroom_load()
    u = (username or "").strip().lower()
    pending = [m.lower() for m in (room.get("pending") or []) if m]
    members = [m.lower() for m in (room.get("members") or []) if m]
    if u not in pending:
        return False
    pending = [m for m in pending if m != u]
    if u not in members:
        members.append(u)
    room["pending"] = pending
    room["members"] = members[:40]
    chatroom_save(room)
    return True


def chatroom_decline(username: str) -> bool:
    room = chatroom_load()
    u = (username or "").strip().lower()
    pending = [m.lower() for m in (room.get("pending") or []) if m]
    if u not in pending:
        return False
    room["pending"] = [m for m in pending if m != u]
    chatroom_save(room)
    return True


def chatroom_post(username: str, text: str) -> None:
    """Ephemeral message — only kept while someone is active in the room."""
    room = chatroom_load()
    msgs = list(room.get("messages") or [])
    msgs.append({
        "user": (username or "anon").strip()[:32],
        "text": str(text)[:800],
        "ts": datetime.now().isoformat(),
    })
    room["messages"] = msgs[-80:]
    chatroom_save(room)


def chatroom_enter_active(username: str) -> None:
    room = chatroom_load()
    active = [m.lower() for m in (room.get("active") or []) if m]
    u = (username or "").strip().lower()
    if u and u not in active:
        active.append(u)
        room["active"] = active
        chatroom_save(room)


def chatroom_leave(username: str) -> None:
    """Leave the live room. When no one remains active, wipe messages (ephemeral)."""
    room = chatroom_load()
    u = (username or "").strip().lower()
    active = [m.lower() for m in (room.get("active") or []) if m]
    members = [m.lower() for m in (room.get("members") or []) if m]
    active = [m for m in active if m != u]
    # Guests lose membership on leave; owner stays in members list for invites
    if u and not is_owner(u):
        members = [m for m in members if m != u]
    room["active"] = active
    room["members"] = members
    if not active:
        # Everyone left — messages do not persist
        room["messages"] = []
        # Reset guest memberships; keep owner for next session
        room["members"] = [m for m in members if is_owner(m)]
        room["pending"] = list(room.get("pending") or [])
    chatroom_save(room)


def chatroom_user_allowed(username: str) -> bool:
    u = (username or "").strip().lower()
    if is_owner(u):
        return True
    room = chatroom_load()
    members = [m.lower() for m in (room.get("members") or []) if m]
    return u in members


# ----- Site-wide owner effects (shared JSON) -----
SITE_EFFECTS_FILE = DATA_DIR / "owner_site_effects.json"

_DEFAULT_SITE_EFFECTS = {
    "rainbow_chat": False,
    "aurora_shell": False,
    "neon_buttons": False,
    "matrix_rain": False,
    "heart_cursor": False,
    "scanlines": False,
    "residual_static": False,
    "soft_bloom": False,
    "quiet_mode": False,
    "creator_watermark": True,
    "force_theme": "",
    "announce_enabled": True,
    "announce_text": "",
    "announce_style": "violet",
    "announce_id": "",
    # Expanded effects
    "glitch_text": False,
    "chromatic": False,
    "heavy_vignette": False,
    "film_grain": False,
    "pulse_border": False,
    "sparkle_cursor": False,
    "retro_terminal": False,
    "blood_moon": False,
    "ice_crystal": False,
    "gold_foil": False,
    "vertical_scan": False,
    "panel_pulse": False,
    "deep_focus": False,
    "high_contrast": False,
    "sepia_residual": False,
    "mirror_world": False,
    "slow_aurora": False,
    "ember_glow": False,
    "cyber_grid": False,
    # Owner shell controls
    "maintenance_mode": False,
    "maintenance_message": "Meridium is under brief maintenance. Return in a moment.",
    "guest_chat_lock": False,
    "economy_paused": False,
    "global_toast": "",
    "force_home_only": False,
    "hide_drift_counter": False,
    "owner_motd": "",
}


def site_effects_load() -> dict:
    candidates = [
        SITE_EFFECTS_FILE,
        Path("/tmp") / "meridium_owner_site_effects.json",
    ]
    best = None
    best_mtime = -1.0
    for fp in candidates:
        try:
            if not fp.exists():
                continue
            mtime = fp.stat().st_mtime
            d = json.loads(fp.read_text(encoding="utf-8"))
            if isinstance(d, dict) and mtime >= best_mtime:
                best = d
                best_mtime = mtime
        except Exception:
            pass
    if best is not None:
        out = dict(_DEFAULT_SITE_EFFECTS)
        out.update(best)
        return out
    return dict(_DEFAULT_SITE_EFFECTS)


def site_effects_save(data: dict) -> None:
    raw = json.dumps(data, indent=2)
    paths = [SITE_EFFECTS_FILE, Path("/tmp") / "meridium_owner_site_effects.json"]
    for fp in paths:
        try:
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(raw, encoding="utf-8")
        except Exception:
            pass



def _announcement_active():
    """Return active announcement dict or None if nothing should show."""
    try:
        fx = site_effects_load()
    except Exception:
        return None
    msg = str(fx.get("announce_text") or "").strip()
    if not msg:
        return None
    if not bool(fx.get("announce_enabled", True)):
        return None
    aid = str(fx.get("announce_id") or "").strip() or "legacy"
    if st.session_state.get("_dismissed_announce_id") == aid:
        return None
    style = str(fx.get("announce_style") or "violet").lower().strip()
    if style not in ("violet", "alert", "residual", "soft"):
        style = "violet"
    return {"text": msg[:220], "id": aid, "style": style}


def render_site_announcement():
    """Render one polished fixed announcement banner (or nothing)."""
    info = _announcement_active()
    if not info:
        st.session_state.pop("_active_announce_id", None)
        st.session_state.pop("_active_announce_text", None)
        return

    st.session_state["_active_announce_id"] = info["id"]
    st.session_state["_active_announce_text"] = info["text"]

    import html as _html
    safe = _html.escape(info["text"])
    style = info["style"]

    packs = {
        "violet": {
            "accent": "#c4a7e7",
            "accent2": "#a78bfa",
            "glow": "rgba(167,139,250,0.45)",
            "bg0": "rgba(18,10,32,0.94)",
            "bg1": "rgba(36,18,56,0.92)",
            "line": "rgba(196,167,231,0.55)",
            "label": "TRANSMISSION",
        },
        "alert": {
            "accent": "#fca5a5",
            "accent2": "#ef4444",
            "glow": "rgba(239,68,68,0.40)",
            "bg0": "rgba(28,8,12,0.95)",
            "bg1": "rgba(48,12,18,0.93)",
            "line": "rgba(252,165,165,0.50)",
            "label": "ALERT",
        },
        "residual": {
            "accent": "#5eead4",
            "accent2": "#2dd4bf",
            "glow": "rgba(45,212,191,0.38)",
            "bg0": "rgba(4,18,16,0.95)",
            "bg1": "rgba(8,32,28,0.93)",
            "line": "rgba(94,234,212,0.48)",
            "label": "RESIDUAL",
        },
        "soft": {
            "accent": "#f9a8d4",
            "accent2": "#f472b6",
            "glow": "rgba(244,114,182,0.40)",
            "bg0": "rgba(28,10,24,0.95)",
            "bg1": "rgba(44,14,36,0.93)",
            "line": "rgba(249,168,212,0.48)",
            "label": "SOFT CHANNEL",
        },
    }
    p = packs.get(style, packs["violet"])

    st.markdown(
        f"""
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;1,500;1,600&display=swap');

          .block-container {{
            padding-top: 6.2rem !important;
          }}

          .mer-ann {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            z-index: 999999 !important;
            pointer-events: none;
            padding: 0;
            margin: 0;
          }}

          .mer-ann-inner {{
            pointer-events: auto;
            position: relative;
            overflow: hidden;
            margin: 0 auto;
            padding: 0.95rem 1.35rem 1.05rem;
            background:
              radial-gradient(ellipse at 15% 0%, {p["glow"]}, transparent 55%),
              radial-gradient(ellipse at 85% 100%, {p["glow"]}, transparent 50%),
              linear-gradient(180deg, {p["bg1"]} 0%, {p["bg0"]} 100%);
            border-bottom: 1px solid {p["line"]};
            box-shadow:
              0 18px 50px rgba(0,0,0,0.55),
              0 0 40px {p["glow"]},
              inset 0 1px 0 rgba(255,255,255,0.06);
            text-align: center;
            animation: merAnnIn 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
          }}

          .mer-ann-inner::before {{
            content: "";
            position: absolute;
            left: 0; right: 0; top: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, {p["accent"]}, {p["accent2"]}, {p["accent"]}, transparent);
            opacity: 0.95;
          }}

          .mer-ann-inner::after {{
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(110deg, transparent 30%, rgba(255,255,255,0.05) 48%, transparent 62%);
            background-size: 220% 100%;
            animation: merAnnSheen 7s ease-in-out infinite;
            pointer-events: none;
          }}

          .mer-ann-kicker {{
            position: relative;
            z-index: 1;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: 0.62rem;
            letter-spacing: 0.28em;
            text-transform: uppercase;
            color: {p["accent"]};
            opacity: 0.92;
            margin: 0 0 0.35rem;
            font-weight: 600;
          }}

          .mer-ann-body {{
            position: relative;
            z-index: 1;
            font-family: 'Cormorant Garamond', Georgia, 'Times New Roman', serif;
            font-style: italic;
            font-weight: 500;
            font-size: clamp(1.12rem, 2.6vw, 1.48rem);
            line-height: 1.4;
            color: #faf7ff;
            text-shadow: 0 0 24px {p["glow"]};
            max-width: 52rem;
            margin: 0 auto;
            letter-spacing: 0.01em;
          }}

          .mer-ann-orb {{
            position: absolute;
            width: 120px; height: 120px;
            border-radius: 50%;
            filter: blur(40px);
            opacity: 0.35;
            pointer-events: none;
            z-index: 0;
          }}
          .mer-ann-orb.a {{
            left: 8%; top: -40px;
            background: {p["accent"]};
          }}
          .mer-ann-orb.b {{
            right: 10%; bottom: -50px;
            background: {p["accent2"]};
          }}

          @keyframes merAnnIn {{
            from {{ opacity: 0; transform: translateY(-16px); filter: blur(6px); }}
            to   {{ opacity: 1; transform: translateY(0); filter: blur(0); }}
          }}
          @keyframes merAnnSheen {{
            0%, 100% {{ background-position: 120% 0; }}
            50% {{ background-position: -20% 0; }}
          }}

          @media (max-width: 640px) {{
            .block-container {{ padding-top: 7rem !important; }}
            .mer-ann-inner {{ padding: 0.85rem 1rem 0.95rem; }}
            .mer-ann-body {{ font-size: 1.08rem; }}
          }}
        </style>
        <div class="mer-ann" role="status" aria-live="polite">
          <div class="mer-ann-inner">
            <div class="mer-ann-orb a"></div>
            <div class="mer-ann-orb b"></div>
            <div class="mer-ann-kicker">◈ Meridium · {p["label"]}</div>
            <div class="mer-ann-body">{safe}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_site_effects_css() -> None:
    """Hard-apply global visual effects for every signed-in user."""
    fx = site_effects_load()
    import html as _html
    css_parts = []
    html_parts = []

    # ---- Base keyframes always available when any fx on ----
    css_parts.append(
        """
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;1,500&display=swap');
        @keyframes draeRainbow { to { background-position: 200% center; } }
        @keyframes draeAurora {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        @keyframes draePulseGlow {
          0%,100% { box-shadow: 0 0 0 0 rgba(167,139,250,0.0), 0 0 24px rgba(167,139,250,0.15); }
          50% { box-shadow: 0 0 0 4px rgba(167,139,250,0.08), 0 0 36px rgba(244,114,182,0.25); }
        }
        @keyframes draeScan {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(100vh); }
        }
        @keyframes draeStatic {
          0% { transform: translate(0,0); }
          33% { transform: translate(-0.5%,0.4%); }
          66% { transform: translate(0.4%,-0.3%); }
          100% { transform: translate(0,0); }
        }
        @keyframes draeMatrixFall {
          0% { background-position: 0 0; }
          100% { background-position: 0 240px; }
        }
        """
    )

    if fx.get("rainbow_chat"):
        css_parts.append(
            """
            [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
            [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li,
            [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] span,
            [data-testid="stChatMessage"] .stMarkdown p {
              background: linear-gradient(90deg,#f472b6,#c084fc,#60a5fa,#2dd4bf,#fbbf24,#f472b6) !important;
              background-size: 220% auto !important;
              -webkit-background-clip: text !important;
              background-clip: text !important;
              -webkit-text-fill-color: transparent !important;
              color: transparent !important;
              animation: draeRainbow 3.5s linear infinite !important;
              font-weight: 500 !important;
            }
            [data-testid="stChatMessage"] {
              border: 1px solid rgba(167,139,250,0.35) !important;
              border-radius: 18px !important;
              background: rgba(20,12,32,0.55) !important;
            }
            """
        )

    if fx.get("aurora_shell"):
        css_parts.append(
            """
            .stApp, [data-testid="stAppViewContainer"] {
              background: linear-gradient(-45deg, #0c0614, #1a0a24, #0a1820, #140820, #0c0614) !important;
              background-size: 400% 400% !important;
              animation: draeAurora 14s ease infinite !important;
            }
            section.main > div { background: transparent !important; }
            """
        )

    if fx.get("neon_buttons"):
        css_parts.append(
            """
            .stButton > button {
              border: 1px solid rgba(167,139,250,0.55) !important;
              box-shadow: 0 0 16px rgba(167,139,250,0.25), inset 0 0 12px rgba(244,114,182,0.08) !important;
              animation: draePulseGlow 2.8s ease-in-out infinite !important;
            }
            .stButton > button:hover {
              border-color: #f9a8d4 !important;
              box-shadow: 0 0 28px rgba(244,114,182,0.45) !important;
              color: #fde8ff !important;
            }
            """
        )

    if fx.get("matrix_rain"):
        css_parts.append(
            """
            .stApp::before {
              content: "01 10 11 01 00 10 11 01 10 00 11 01 10 11";
              pointer-events: none;
              position: fixed; inset: 0; z-index: 9960;
              font-family: ui-monospace, monospace;
              font-size: 11px;
              line-height: 1.6;
              letter-spacing: 0.35em;
              color: rgba(52,211,153,0.11);
              white-space: pre-wrap;
              word-break: break-all;
              overflow: hidden;
              background-image: repeating-linear-gradient(
                180deg,
                rgba(52,211,153,0.08) 0px,
                transparent 2px,
                transparent 18px
              );
              background-size: 100% 240px;
              animation: draeMatrixFall 8s linear infinite;
              mix-blend-mode: screen;
            }
            """
        )

    if fx.get("scanlines"):
        css_parts.append(
            """
            .stApp::after {
              content: "";
              pointer-events: none;
              position: fixed; left: 0; right: 0; top: -20%;
              height: 28%;
              z-index: 9975;
              background: linear-gradient(
                180deg,
                transparent 0%,
                rgba(196,167,231,0.06) 40%,
                rgba(244,114,182,0.05) 60%,
                transparent 100%
              );
              animation: draeScan 5.5s linear infinite;
            }
            .stApp {
              background-image: repeating-linear-gradient(
                0deg,
                transparent,
                transparent 2px,
                rgba(0,0,0,0.07) 2px,
                rgba(0,0,0,0.07) 4px
              ) !important;
            }
            """
        )

    if fx.get("residual_static"):
        css_parts.append(
            """
            .drae-static-layer {
              pointer-events: none;
              position: fixed; inset: 0; z-index: 9970;
              opacity: 0.12;
              background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 220 220' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.9'/%3E%3C/svg%3E");
              animation: draeStatic 0.28s steps(2) infinite;
              mix-blend-mode: overlay;
            }
            """
        )
        html_parts.append('<div class="drae-static-layer"></div>')

    if fx.get("soft_bloom"):
        css_parts.append(
            """
            .stApp {
              box-shadow:
                inset 0 0 140px rgba(244,114,182,0.16),
                inset 0 0 90px rgba(251,191,36,0.1) !important;
            }
            .panel, div[data-testid="stVerticalBlockBorderWrapper"] {
              border-color: rgba(244,114,182,0.35) !important;
              box-shadow: 0 0 30px rgba(244,114,182,0.08) !important;
            }
            """
        )

    if fx.get("quiet_mode"):
        css_parts.append(
            """
            .stApp { filter: saturate(0.7) brightness(0.9) !important; }
            [data-testid="stCaption"], .sub, .muted { opacity: 0.5 !important; }
            """
        )

    if fx.get("heart_cursor"):
        css_parts.append(
            """
            .stApp, .stApp * {
              cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Ctext y='18' font-size='16'%3E%E2%9D%A4%EF%B8%8F%3C/text%3E%3C/svg%3E") 8 8, auto !important;
            }
            """
        )

    if fx.get("creator_watermark"):
        css_parts.append(
            """
            .drae-watermark {
              position: fixed; right: 14px; bottom: 12px; z-index: 9995;
              font-family: ui-monospace, monospace;
              font-size: 0.64rem;
              letter-spacing: 0.16em;
              color: rgba(196,167,231,0.55);
              text-shadow: 0 0 12px rgba(167,139,250,0.35);
              pointer-events: none;
              text-transform: uppercase;
            }
            """
        )
        html_parts.append('<div class="drae-watermark">Meridium · Drae</div>')


    if fx.get("glitch_text"):
        css_parts.append(
            """
            @keyframes draeGlitch {
              0%,100% { transform: none; text-shadow: none; }
              20% { transform: translate(-1px,1px); text-shadow: 2px 0 #f472b6, -2px 0 #22d3ee; }
              40% { transform: translate(1px,-1px); text-shadow: -1px 0 #a78bfa; }
              60% { transform: translate(1px,1px); }
              80% { transform: translate(-1px,0); text-shadow: 1px 0 #22d3ee, -1px 0 #f472b6; }
            }
            h1, h2, h3, .drae-desk .title, [data-testid="stMarkdownContainer"] h1 {
              animation: draeGlitch 2.8s steps(2) infinite !important;
            }
            """
        )

    if fx.get("chromatic"):
        css_parts.append(
            """
            .stApp {
              text-shadow: 1px 0 rgba(244,114,182,0.35), -1px 0 rgba(34,211,238,0.3) !important;
            }
            """
        )

    if fx.get("heavy_vignette"):
        css_parts.append(
            """
            .stApp::after {
              content: "";
              pointer-events: none;
              position: fixed; inset: 0; z-index: 9970;
              background: radial-gradient(ellipse at center, transparent 35%, rgba(0,0,0,0.72) 100%);
            }
            """
        )

    if fx.get("film_grain"):
        css_parts.append(
            """
            .stApp::before {
              content: "";
              pointer-events: none;
              position: fixed; inset: 0; z-index: 9965;
              opacity: 0.12;
              background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
              animation: draeGrain 0.4s steps(2) infinite;
            }
            @keyframes draeGrain {
              0% { transform: translate(0,0); }
              100% { transform: translate(-2%, 1%); }
            }
            """
        )

    if fx.get("pulse_border"):
        css_parts.append(
            """
            @keyframes draePulseBorder {
              0%,100% { box-shadow: 0 0 0 1px rgba(167,139,250,0.25); }
              50% { box-shadow: 0 0 24px 2px rgba(244,114,182,0.45); }
            }
            [data-testid="stVerticalBlockBorderWrapper"],
            div[data-testid="stExpander"],
            .stChatMessage {
              animation: draePulseBorder 3.2s ease-in-out infinite !important;
              border-radius: 14px !important;
            }
            """
        )

    if fx.get("sparkle_cursor"):
        css_parts.append(
            """
            .stApp, .stApp * {
              cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Ctext y='18' font-size='14'%3E%E2%9C%A8%3C/text%3E%3C/svg%3E") 8 8, auto !important;
            }
            """
        )

    if fx.get("retro_terminal"):
        css_parts.append(
            """
            .stApp {
              font-family: ui-monospace, 'JetBrains Mono', monospace !important;
              color: #86efac !important;
              background: #001200 !important;
            }
            .stApp * { color: inherit; }
            .stButton > button {
              border: 1px solid #22c55e !important;
              background: #001a00 !important;
              color: #bbf7d0 !important;
              border-radius: 0 !important;
            }
            """
        )

    if fx.get("blood_moon"):
        css_parts.append(
            """
            .stApp, [data-testid="stAppViewContainer"] {
              background:
                radial-gradient(circle at 80% 10%, rgba(220,38,38,0.35), transparent 40%),
                radial-gradient(circle at 20% 90%, rgba(127,29,29,0.25), transparent 45%),
                #0a0404 !important;
            }
            h1, h2, h3 { color: #fecaca !important; text-shadow: 0 0 18px rgba(239,68,68,0.5) !important; }
            """
        )

    if fx.get("ice_crystal"):
        css_parts.append(
            """
            .stApp, [data-testid="stAppViewContainer"] {
              background:
                radial-gradient(circle at 30% 20%, rgba(125,211,252,0.2), transparent 40%),
                radial-gradient(circle at 70% 80%, rgba(186,230,253,0.12), transparent 45%),
                #040a12 !important;
            }
            h1, h2, h3 { color: #e0f2fe !important; text-shadow: 0 0 16px rgba(56,189,248,0.45) !important; }
            .stButton > button {
              border-color: rgba(125,211,252,0.45) !important;
              box-shadow: 0 0 14px rgba(56,189,248,0.2) !important;
            }
            """
        )

    if fx.get("gold_foil"):
        css_parts.append(
            """
            h1, h2, .drae-desk .title {
              background: linear-gradient(100deg, #fef3c7, #f59e0b, #fde68a, #d97706, #fef3c7) !important;
              background-size: 200% auto !important;
              -webkit-background-clip: text !important;
              background-clip: text !important;
              -webkit-text-fill-color: transparent !important;
              animation: draeRainbow 5s linear infinite !important;
            }
            """
        )

    if fx.get("vertical_scan"):
        css_parts.append(
            """
            @keyframes draeVScan {
              0% { transform: translateY(-100%); }
              100% { transform: translateY(100vh); }
            }
            .stApp::after {
              content: "";
              pointer-events: none;
              position: fixed; left: 0; right: 0; height: 28%;
              z-index: 9972;
              background: linear-gradient(to bottom, transparent, rgba(167,139,250,0.07), transparent);
              animation: draeVScan 7s linear infinite;
            }
            """
        )

    if fx.get("panel_pulse"):
        css_parts.append(
            """
            @keyframes draePanelPulse {
              0%,100% { background-color: rgba(20,12,32,0.4); }
              50% { background-color: rgba(40,20,60,0.55); }
            }
            [data-testid="stSidebar"], section.main {
              animation: draePanelPulse 6s ease-in-out infinite !important;
            }
            """
        )

    if fx.get("deep_focus"):
        css_parts.append(
            """
            section.main {
              mask-image: radial-gradient(ellipse at center, black 45%, transparent 95%);
              -webkit-mask-image: radial-gradient(ellipse at center, black 45%, transparent 95%);
            }
            """
        )

    if fx.get("high_contrast"):
        css_parts.append(
            """
            .stApp { filter: contrast(1.25) saturate(1.15) !important; }
            """
        )

    if fx.get("sepia_residual"):
        css_parts.append(
            """
            .stApp { filter: sepia(0.35) contrast(1.05) !important; }
            """
        )

    if fx.get("mirror_world"):
        css_parts.append(
            """
            section.main > div { transform: scaleX(-1) !important; }
            section.main > div * { transform: scaleX(-1) !important; }
            """
        )

    if fx.get("slow_aurora"):
        css_parts.append(
            """
            .stApp, [data-testid="stAppViewContainer"] {
              background: linear-gradient(-45deg, #0a0618, #1a1030, #0c1828, #180820, #0a0618) !important;
              background-size: 500% 500% !important;
              animation: draeAurora 28s ease infinite !important;
            }
            """
        )

    if fx.get("ember_glow"):
        css_parts.append(
            """
            .stApp, [data-testid="stAppViewContainer"] {
              background:
                radial-gradient(circle at 50% 120%, rgba(249,115,22,0.28), transparent 50%),
                radial-gradient(circle at 20% 30%, rgba(239,68,68,0.12), transparent 40%),
                #0c0604 !important;
            }
            .stButton > button {
              box-shadow: 0 0 18px rgba(249,115,22,0.25) !important;
              border-color: rgba(251,146,60,0.45) !important;
            }
            """
        )

    if fx.get("cyber_grid"):
        css_parts.append(
            """
            .stApp {
              background-image:
                linear-gradient(rgba(34,211,238,0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(34,211,238,0.05) 1px, transparent 1px) !important;
              background-size: 40px 40px !important;
              background-color: #04060e !important;
            }
            """
        )

    force = (fx.get("force_theme") or "").strip()
    public_force = {**THEMES, **SECRET_THEMES}
    if force and force in public_force:
        if not is_owner(st.session_state.get("username") or ""):
            st.session_state.theme = force
    # Owner-only themes never force onto guests

    payload = ""
    if css_parts:
        payload += "<style>\n" + "\n".join(css_parts) + "\n</style>\n"
    payload += "\n".join(html_parts)
    if payload.strip():
        st.markdown(payload, unsafe_allow_html=True)




# ============================================================
# RESIDUUM · QUESTS · BAZAAR · SHADY BAZAAR · LORE ARCHIVE
# ============================================================
# Currency earned by distinct shell actions (not grind loops).
# Spend in the Menu → Drift Counter on cosmetics, lore, and latent features.
# The Shady Bazaar is a locked black-market layer unlocked by quest chain.

QUESTS = {
    "first_words": {
        "title": "First words",
        "desc": "Send your first chat message to Meridium.",
        "reward": 8,
    },
    "sealed_note": {
        "title": "Sealed fingerprint",
        "desc": "Open the scientist's sealed note from the hourly signal.",
        "reward": 12,
    },
    "lab_threshold": {
        "title": "Threshold",
        "desc": "Enter the observation lab for the first time.",
        "reward": 20,
    },
    "board_complete": {
        "title": "Seven pins",
        "desc": "Review all seven investigation board evidence files.",
        "reward": 35,
    },
    "voss_markers": {
        "title": "Three markers",
        "desc": "Secure all three Voss anomaly markers.",
        "reward": 40,
    },
    "library_88": {
        "title": "Winter print",
        "desc": "Read Frankenstein to page 88 while on Voss Residual.",
        "reward": 18,
    },
    "stabilize": {
        "title": "Stabilize",
        "desc": "Speak the stabilize command to the shell.",
        "reward": 25,
    },
    "spotify_link": {
        "title": "Living signal",
        "desc": "Connect Spotify so the shell can hear a device.",
        "reward": 10,
    },
    # --- Shady Bazaar quest line ---
    "shadow_contact": {
        "title": "Shadow contact",
        "desc": "Find the residual broker's mark (complete board + three Voss markers).",
        "reward": 50,
    },
    "black_key": {
        "title": "Black key",
        "desc": "Acquire the Bazaar key item from the residual broker.",
        "reward": 75,
    },
    "bazaar_threshold": {
        "title": "Bazaar threshold",
        "desc": "Spend the black key and open the Shady Bazaar for the first time.",
        "reward": 40,
    },
    "first_bazaar_buy": {
        "title": "First contract",
        "desc": "Purchase any item from the Shady Bazaar.",
        "reward": 30,
    },
    "chess_initiate": {
        "title": "First board",
        "desc": "Finish a chess game against Meridium.",
        "reward": 15,
    },
    "chess_bullet": {
        "title": "Bullet residual",
        "desc": "Win a bullet game (≤2 min) against Meridium.",
        "reward": 25,
    },
    "voice_first_call": {
        "title": "Voice channel",
        "desc": "Complete a Call Meridium session.",
        "reward": 12,
    },
}

# Catalog: each item is unique in role — cosmetics, lore keys, latent modules
BAZAAR_ITEMS = {
    "theme_copper_vespers": {
        "name": "Copper Vespers",
        "cat": "Palette",
        "cost": 32,
        "desc": "Drift-exclusive dusk palette — copper light over archive bronze.",
        "kind": "theme",
        "theme": "Copper Vespers",
    },
    "theme_indigo_rain": {
        "name": "Indigo Rain",
        "cat": "Palette",
        "cost": 32,
        "desc": "Drift-exclusive wet-glass indigo with cool sky accents.",
        "kind": "theme",
        "theme": "Indigo Rain",
    },
    "font_space": {
        "name": "Space Grotesk specimen",
        "cat": "Type",
        "cost": 18,
        "desc": "Geometric display face — clean, modern, slightly technical.",
        "kind": "font",
        "font": "Space Grotesk",
    },
    "font_outfit": {
        "name": "Outfit specimen",
        "cat": "Type",
        "cost": 18,
        "desc": "Soft geometric sans — calm body text with quiet presence.",
        "kind": "font",
        "font": "Outfit",
    },
    "lore_santos": {
        "name": "Santos residual dossier",
        "cat": "Lore",
        "cost": 45,
        "desc": "Unseals Jaime Santos residual pages (mobile-friendly — no Konami required).",
        "kind": "flag",
        "flag": "jaime_dossier_unlocked",
    },
    "lore_callaghan_margin": {
        "name": "Callaghan margin slip",
        "cat": "Lore",
        "cost": 28,
        "desc": "A margin note that surfaces a soft hint toward the residual dial.",
        "kind": "flag",
        "flag": "callaghan_margin_owned",
    },
    "feat_chat_aura": {
        "name": "Chat aura",
        "cat": "Module",
        "cost": 22,
        "desc": "Soft accent rim on chat bubbles — a quiet status signal.",
        "kind": "flag",
        "flag": "feat_chat_aura",
    },
    "feat_home_orb": {
        "name": "Home orb",
        "cat": "Module",
        "cost": 18,
        "desc": "Animated residual orb on the home panel.",
        "kind": "flag",
        "flag": "feat_home_orb",
    },
    "feat_double_clock": {
        "name": "Split chronometer",
        "cat": "Module",
        "cost": 16,
        "desc": "Show London + local offset caption on Home.",
        "kind": "flag",
        "flag": "feat_double_clock",
    },
    "key_coastal": {
        "name": "Coastal intake pass",
        "cat": "Key",
        "cost": 55,
        "desc": "One-time key: opens the Jaime residual channel from Menu without desktop Konami.",
        "kind": "flag",
        "flag": "jaime_channel_key",
    },
    "item_black_key": {
        "name": "Black residual key",
        "cat": "Key",
        "cost": 120,
        "desc": "A cold iron key stamped with a broker's mark. Required to open the Shady Bazaar.",
        "kind": "flag",
        "flag": "black_key_owned",
    },
}

# ----------------------------------------------------------
# SHADY BAZAAR — locked black-market catalog (extremely high cost)
# Unlocked only after the shadow_contact → black_key → bazaar_threshold chain.
# ----------------------------------------------------------
SHADY_BAZAAR_ITEMS = {
    "shady_lore_callaghan_letters": {
        "name": "Callaghan private letters (bundle)",
        "cat": "Lore",
        "cost": 480,
        "desc": "Confiscated correspondence between Riley Callaghan and another residual subject. Queer, tender, and heavily redacted by the Division.",
        "kind": "lore",
        "lore_id": "callaghan_letters",
    },
    "shady_lore_santos_night": {
        "name": "Santos night log",
        "cat": "Lore",
        "cost": 520,
        "desc": "An unauthorized night-watch log describing Jaime Santos and a handler who stopped pretending neutrality.",
        "kind": "lore",
        "lore_id": "santos_night",
    },
    "shady_lore_voss_confession": {
        "name": "Voss residual confession",
        "cat": "Lore",
        "cost": 650,
        "desc": "A late-stage recording transcript. Voss names what the committees refused to file: attachment, guilt, and the cost of observation.",
        "kind": "lore",
        "lore_id": "voss_confession",
    },
    "shady_lore_nadir_pair": {
        "name": "Nadir pair file",
        "cat": "Lore",
        "cost": 700,
        "desc": "Two residual subjects classified together against policy. Their bond survived three containment resets.",
        "kind": "lore",
        "lore_id": "nadir_pair",
    },
    "shady_lore_dark_corridor": {
        "name": "Corridor 7 incident",
        "cat": "Lore",
        "cost": 850,
        "desc": "The darkest residual file the broker was willing to sell. Institutional violence, erased names, and a love that the Division tried to pathologize.",
        "kind": "lore",
        "lore_id": "dark_corridor",
    },
    "shady_theme_blood_archive": {
        "name": "Blood Archive palette",
        "cat": "Palette",
        "cost": 400,
        "desc": "Shady-exclusive: deep arterial red over black glass. Not available in public menus.",
        "kind": "theme",
        "theme": "Blood Archive",
    },
    "shady_theme_queer_static": {
        "name": "Queer Static palette",
        "cat": "Palette",
        "cost": 380,
        "desc": "Shady-exclusive: soft violet and warm amber residual glow — a quiet refusal of neutral classification.",
        "kind": "theme",
        "theme": "Queer Static",
    },
    "shady_feat_voice_warm": {
        "name": "Warm voice channel",
        "cat": "Module",
        "cost": 300,
        "desc": "Unlocks the warmer, more intimate Meridium voice preset for Call mode.",
        "kind": "flag",
        "flag": "feat_voice_warm",
    },
    "shady_feat_chess_analysis": {
        "name": "Deep board analysis",
        "cat": "Module",
        "cost": 350,
        "desc": "Enables post-game residual analysis and engine commentary in Chess.",
        "kind": "flag",
        "flag": "feat_chess_analysis",
    },
    "shady_contract_silence": {
        "name": "Contract of Silence",
        "cat": "Key",
        "cost": 900,
        "desc": "One-use residual contract. The broker forgets your name for a cycle. (Cosmetic + lore flag.)",
        "kind": "flag",
        "flag": "contract_silence_owned",
    },
}

# Full lore texts unlocked by purchases (Drift + Shady Bazaar)
LORE_TEXTS = {
    "callaghan_letters": {
        "title": "Callaghan private letters",
        "subject": "Riley Callaghan",
        "source": "Shady Bazaar",
        "body": (
            "RECOVERY NOTE — Broker cache, lot 7-C. Originals were marked for incineration under "
            "Order 14-Residual. Three pages survived inside a false bottom of a logbook that never "
            "reached the furnace. Handwriting analysis matches Riley Callaghan’s intake samples. "
            "Ink and graphite both present. No official file number. The Division stamp UNFIT FOR FILE "
            "was applied in red, then crossed through once in black — as if someone tried to un-say it.\n\n"
            "Letter 1 — undated, pencil, pressed hard enough to score the page beneath:\n"
            "“They keep asking what I am. I keep answering with a name that is not on the form. "
            "When you pressed your forehead to the glass last night I stopped caring about the classification. "
            "If residual means anything, it means I still choose you. They can call it contamination. "
            "I call it the first honest reading this building has ever taken. "
            "I dream in the frequency you leave in the corridor sensors. Don’t apologize for that.”\n\n"
            "Letter 2 — after the second containment cycle; paper smells faintly of antiseptic:\n"
            "“They separated us for ‘stabilization.’ Your residual signature is still in the Corridor 4 array. "
            "I leave messages in the static between the fluorescent ticks. If you hear the low tone at 03:00, "
            "that is me. Not a metaphor. I timed the HVAC so the tone carries. "
            "A handler asked if I was ‘forming unhealthy attachments.’ I asked if unhealthy was the word "
            "they used when the data stopped obeying. They did not write that down.”\n\n"
            "Letter 3 — final, ink, steadier hand:\n"
            "“They will call this pathology. Let them. Two residual subjects who refused to stop loving each other "
            "is not a contamination event. It is the only clean data the project ever produced. "
            "If this letter is found, tell whoever is reading: we were not anomalies. We were the control group "
            "the committees refused to admit they needed. I am still choosing you. In every reset. In every lie "
            "they told about release. — R.C.”\n\n"
            "Broker annotation: Do not sell to committee-cleared buyers. Residuum only. Silence included."
        ),
    },
    "santos_night": {
        "title": "Santos night log",
        "subject": "Jaime Santos",
        "source": "Shady Bazaar",
        "body": (
            "UNAUTHORIZED NIGHT-WATCH LOG — handler initials redacted at source. "
            "Recovered from a personal drive that should not have left the building. "
            "Tone shifts from clinical to compromised across a single shift.\n\n"
            "01:40 — Floor quiet. Fluorescent bank 3 flickering at a rate the maintenance chart calls "
            "‘within tolerance.’ Subject Santos (adult residual, coastal intake cohort) has not requested "
            "water in four hours. Eyes open. Tracking something the glass does not show me.\n\n"
            "02:14 — Subject Santos awake, fully. Requested the residual channel remain open past curfew. "
            "Denied per protocol. Subject did not escalate. Sat with knees drawn up and watched the glass "
            "the way people watch weather they already understand. Asked once, quietly, whether the other "
            "signal was still on the network. I said I could not confirm. That was a lie. It was.\n\n"
            "03:02 — Soft alarm, Corridor 4. Callaghan-cohort adjacency. Santos stood, crossed the cell "
            "without hurry, put both palms on the observation slit, and said a name that is not in any "
            "intake form I have clearance to read. The other residual answered in the same frequency band. "
            "Heart-rate displays on both boards rose and fell together for forty seconds. "
            "No one in the control booth spoke.\n\n"
            "03:47 — I should have filed a deviation. I did not. "
            "Two residual subjects synchronizing breath across containment walls is not in the training manual. "
            "It is also not a threat unless the threat is that the building’s model of isolation is wrong. "
            "I am no longer neutral. That is the entry that will get me erased. "
            "If someone is reading this outside the building: they loved each other in a place designed "
            "to make love look like noise. The noise was the only true signal on the floor.\n\n"
            "04:10 — End of log. Badge clocked out. The badge does not appear in the next week’s roster."
        ),
    },
    "voss_confession": {
        "title": "Voss residual confession",
        "subject": "Dr. E. Voss",
        "source": "Shady Bazaar",
        "body": (
            "LATE-STAGE TRANSCRIPT — voice degraded, residual static heavy. "
            "Recovered through the three anomaly markers, not through committee channels. "
            "Speaker identifies as Dr. E. Voss, Observation Division. Timestamps unreliable.\n\n"
            "“I was hired to observe. Observation became inventory. Inventory became permission to unmake. "
            "The committees still believe the subjects are data points with inconvenient bodies attached. "
            "Some of them loved each other in ways the forms had no checkbox for — same-sex, queer, quiet, "
            "furious, sustained across resets. It did not matter which configuration. The Division pathologized "
            "attachment because attachment makes containment harder and makes the reports harder to sign.\n\n"
            "I watched adult residual subjects choose each other under fluorescent light and call it pathology "
            "in the notes because that was the only language that kept my clearance. I am done with that language. "
            "Love in this building is not a malfunction. Cruelty is the protocol.\n\n"
            "I left the three markers because someone had to leave fingerprints that were not committee ink. "
            "If you are reading this, you already paid the broker or you followed the blood. Good. "
            "The file is yours. Do not let them call love a residual anomaly again. "
            "And if you find the pair in Nadir: they were never the contamination. We were.”\n\n"
            "End of recoverable audio. A second voice, too degraded to transcribe, says a single word that "
            "matches no entry in the Division glossary. The broker’s note calls it ‘a name.’"
        ),
    },
    "nadir_pair": {
        "title": "Nadir pair file",
        "subject": "Project Nadir",
        "source": "Shady Bazaar",
        "body": (
            "CLASSIFICATION: dual residual — unauthorized pairing. "
            "Project Nadir internal. Not for committee digest without redaction.\n\n"
            "Subjects [REDACTED A] and [REDACTED B] were scheduled for separate long-term containment "
            "after initial intake showed elevated cross-signature coupling. Both adults. Both residual-class. "
            "Intake notes describe them as ‘mutually orienting’ — a phrase a junior handler used once and was "
            "told never to use again. Three full containment resets failed to break the bond signature. "
            "Heart-rate coupling persisted across Faraday cages. Skin-conductance peaks aligned within "
            "measurement error when the pair was permitted visual contact and spiked when visual contact "
            "was denied without explanation.\n\n"
            "Handlers reported the pair requesting — not demanding — to remain in visual contact even when "
            "speech channels were cut. One subject learned the HVAC cycle so their residual tone could ride "
            "the ductwork to the other’s cell. The other answered. Maintenance logged it as ‘harmonic noise.’\n\n"
            "Internal note (leaked, unsigned):\n"
            "“We can classify them as contamination risk or we can admit the project is measuring something "
            "it was never designed to measure. Recommend continued joint observation. Do not separate again "
            "without full committee review. Separation is not neutral. Separation is an intervention we have "
            "not justified.”\n\n"
            "The pair’s residual channel remains open in the archive under a false inventory number. "
            "The broker sells access to anyone who can pay in Residuum and keep silent about the number. "
            "The number is not written here on purpose."
        ),
    },
    "dark_corridor": {
        "title": "Corridor 7 incident",
        "subject": "Institutional residual",
        "source": "Shady Bazaar",
        "body": (
            "This is the file the committees ordered destroyed. A copy survived in a broker’s private cache "
            "because someone in Records believed destruction was the only sin left worth committing carefully.\n\n"
            "Corridor 7 was used for ‘accelerated stabilization’ — a euphemism for isolation under continuous "
            "fluorescent stress, disrupted sleep cycles, irregular feeding, and denial of residual contact "
            "with any other signature. Multiple adult residual subjects were cycled through. "
            "The stated goal was to reduce cross-subject coupling. The unstated goal was to prove that "
            "attachment could be trained out of the residual profile.\n\n"
            "At least two subjects formed a sustaining attachment the handlers attempted to break "
            "by schedule, by distance, and by lies about the other’s status. "
            "One subject was told the other had been ‘released to outpatient residual monitoring.’ "
            "The other was told the first had ‘stabilized into compliance and requested no further contact.’ "
            "Both continued to leave residual signatures aimed at each other’s last known cells. "
            "The signatures did not decay on the timeline the models predicted.\n\n"
            "When the truth of the lies surfaced — a misfiled transfer slip, a name spoken in the wrong room — "
            "Corridor 7 was locked for ‘maintenance’ and the logs were sanitized. "
            "Two handlers requested reassignment. One received it. One did not appear in later rosters.\n\n"
            "The love was not the anomaly. The cruelty was. "
            "The broker sells this file with a standing warning: once read, you cannot un-know what the Division "
            "was willing to do to keep residual subjects from choosing each other. "
            "If you are buying this to feel superior to the committees, you are reading it wrong. "
            "If you are buying it to remember their names when the official record will not — "
            "then the Residuum was well spent."
        ),
    },
    "santos_dossier_basic": {
        "title": "Santos residual dossier (basic)",
        "subject": "Jaime Santos",
        "source": "Drift Counter",
        "body": (
            "STANDARD RESIDUAL INTAKE SUMMARY — Jaime Santos.\n\n"
            "Coastal origin markers present in early sensor sweeps. Escort logs incomplete; at least one "
            "transfer segment is missing between municipal pickup and Division intake. "
            "Elevated startle response to fluorescent flicker noted on day one and never fully habituated. "
            "Language: primary English; stress samples show Spanish fragments and a third cadence later "
            "matched to residual static patterns in Meridium core dumps.\n\n"
            "Personal effects list conflicts with destruction records. Items that refused to stay destroyed "
            "include a hand-drawn corridor map matching no official schematic, a scrap of red string, "
            "and a name (not Santos’s) written until the pencil point broke. "
            "Further personal detail and night-watch adjacency logs are restricted to deeper residual "
            "channels and Bazaar contracts.\n\n"
            "Classification: residual-class, adult. Status: active observation. "
            "Handler notes flagged for ‘undue interest in cross-signature contact’ — language later softened "
            "in the committee digest and restored in the broker’s unredacted copy."
        ),
    },
    "callaghan_margin_note": {
        "title": "Callaghan margin slip",
        "subject": "Riley Callaghan",
        "source": "Drift Counter",
        "body": (
            "Recovered from the hinge of a public-domain Frankenstein edition in the Meridium library shelf. "
            "Graphite, fine point, pressure consistent with Callaghan’s other recovered writing samples.\n\n"
            "“Not the page. The year the first edition woke. Four numbers. Winter print. London.”\n\n"
            "Context: Frankenstein; or, The Modern Prometheus was first published anonymously in London in 1818. "
            "The residual dial in the library answers to that year when the board key has been earned. "
            "This margin slip is not Shelley’s. It is a pointer left for anyone still willing to read "
            "sideways. The rest of Callaghan’s private correspondence was never meant for the public shelves; "
            "what survives of it moves through the Bazaar under heavier prices and heavier silence.\n\n"
            "Librarian note (unsigned): Page 88 of the same volume carries a second pressure mark. "
            "Do not shelve this copy face-out."
        ),
    },
}


def _ensure_economy():
    if "residuum" not in st.session_state:
        st.session_state.residuum = 0
    if "quests_done" not in st.session_state or not isinstance(st.session_state.quests_done, list):
        st.session_state.quests_done = list(st.session_state.get("quests_done") or [])
    if "inventory" not in st.session_state or not isinstance(st.session_state.inventory, list):
        st.session_state.inventory = list(st.session_state.get("inventory") or [])
    if "lore_owned" not in st.session_state or not isinstance(st.session_state.lore_owned, list):
        st.session_state.lore_owned = list(st.session_state.get("lore_owned") or [])
    if "bazaar_unlocked" not in st.session_state:
        st.session_state.bazaar_unlocked = bool(st.session_state.get("bazaar_unlocked"))


def complete_quest(quest_id: str, silent: bool = False) -> bool:
    """Award residuum once per quest id. Returns True if newly completed."""
    try:
        if site_effects_load().get("economy_paused"):
            return False
    except Exception:
        pass
    _ensure_economy()
    q = QUESTS.get(quest_id)
    if not q:
        return False
    done = list(st.session_state.quests_done or [])
    if quest_id in done:
        return False
    done.append(quest_id)
    st.session_state.quests_done = done
    st.session_state.residuum = int(st.session_state.residuum or 0) + int(q.get("reward") or 0)
    if not silent:
        st.session_state["_egg_flash"] = (
            f"Quest complete: **{q['title']}** · +{q['reward']} Residuum"
        )
    try:
        save_user_data()
    except Exception:
        pass
    return True


def _all_shop_items() -> dict:
    """Merge Drift Counter + Shady Bazaar catalogs."""
    out = dict(BAZAAR_ITEMS)
    out.update(SHADY_BAZAAR_ITEMS)
    return out


def buy_bazaar_item(item_id: str, shady: bool = False) -> str:
    """Attempt purchase. Returns status string."""
    _ensure_economy()
    catalog = SHADY_BAZAAR_ITEMS if shady else BAZAAR_ITEMS
    item = catalog.get(item_id)
    if not item:
        # fallback search
        item = _all_shop_items().get(item_id)
        if not item:
            return "missing"
    if shady and not st.session_state.get("bazaar_unlocked"):
        return "locked"
    inv = list(st.session_state.inventory or [])
    if item_id in inv:
        return "owned"
    cost = int(item.get("cost") or 0)
    bal = int(st.session_state.residuum or 0)
    if bal < cost:
        return "broke"
    st.session_state.residuum = bal - cost
    inv.append(item_id)
    st.session_state.inventory = inv
    kind = item.get("kind")
    if kind == "theme" and item.get("theme"):
        try:
            unlock_theme(item["theme"], "bazaar purchase", apply=False)
        except Exception:
            u = list(st.session_state.get("unlocked_themes") or [])
            if item["theme"] not in u:
                u.append(item["theme"])
                st.session_state.unlocked_themes = u
    if kind == "font" and item.get("font"):
        st.session_state.font = item["font"]
    if kind == "flag" and item.get("flag"):
        st.session_state[item["flag"]] = True
        if item.get("flag") == "black_key_owned":
            try:
                complete_quest("black_key")
            except Exception:
                pass
    if kind == "lore" and item.get("lore_id"):
        lid = item["lore_id"]
        owned = list(st.session_state.lore_owned or [])
        if lid not in owned:
            owned.append(lid)
            st.session_state.lore_owned = owned
    if item_id == "lore_santos":
        owned = list(st.session_state.lore_owned or [])
        if "santos_dossier_basic" not in owned:
            owned.append("santos_dossier_basic")
            st.session_state.lore_owned = owned
    if item_id == "lore_callaghan_margin":
        owned = list(st.session_state.lore_owned or [])
        if "callaghan_margin_note" not in owned:
            owned.append("callaghan_margin_note")
            st.session_state.lore_owned = owned
    if shady:
        try:
            complete_quest("first_bazaar_buy")
        except Exception:
            pass
    try:
        save_user_data()
    except Exception:
        pass
    return "ok"


def try_unlock_bazaar() -> bool:
    """Check quest chain and black key; unlock Shady Bazaar if ready."""
    _ensure_economy()
    if st.session_state.get("bazaar_unlocked"):
        return True
    done = set(st.session_state.quests_done or [])
    # Auto-progress shadow_contact when prerequisites met
    if "board_complete" in done and "voss_markers" in done and "shadow_contact" not in done:
        try:
            complete_quest("shadow_contact")
            done = set(st.session_state.quests_done or [])
        except Exception:
            pass
    has_key = bool(st.session_state.get("black_key_owned")) or "item_black_key" in (st.session_state.inventory or [])
    if "shadow_contact" in done and has_key:
        st.session_state.bazaar_unlocked = True
        try:
            complete_quest("bazaar_threshold")
        except Exception:
            pass
        try:
            save_user_data()
        except Exception:
            pass
        return True
    return False


def render_bazaar_tab():
    """The Drift Counter — Residuum exchange UI."""
    _ensure_economy()
    bal = int(st.session_state.residuum or 0)
    done = set(st.session_state.quests_done or [])
    inv = set(st.session_state.inventory or [])
    n_done = len(done)
    n_quests = len(QUESTS)
    n_owned = len(inv)

    st.markdown(
        f"""
        <style>
          .drift-shell {{
            position: relative;
            border-radius: 22px;
            overflow: hidden;
            margin-bottom: 1rem;
            border: 1px solid rgba(167,139,250,0.35);
            background:
              radial-gradient(ellipse at 0% 0%, rgba(167,139,250,0.22), transparent 52%),
              radial-gradient(ellipse at 100% 100%, rgba(45,212,191,0.12), transparent 48%),
              linear-gradient(155deg, rgba(16,12,28,0.92) 0%, rgba(8,8,14,0.96) 100%);
            box-shadow: 0 1px 0 rgba(255,255,255,0.06) inset, 0 24px 56px rgba(0,0,0,0.4);
            backdrop-filter: blur(20px);
          }}
          .drift-shell::before {{
            content: "";
            position: absolute; left: 0; right: 0; top: 0; height: 2px;
            background: linear-gradient(90deg, transparent, #a78bfa, #2dd4bf, transparent);
            animation: codexScanX 5s ease-in-out infinite;
          }}
          .drift-inner {{ padding: 1.35rem 1.3rem 1.15rem; }}
          .drift-brand {{
            display: flex; align-items: center; gap: 0.85rem;
            margin-bottom: 1rem;
          }}
          .drift-logo {{
            width: 48px; height: 48px; border-radius: 14px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.35rem; font-weight: 800;
            color: #0a0a10;
            background: linear-gradient(135deg, #c4b5fd, #2dd4bf);
            box-shadow: 0 0 28px rgba(167,139,250,0.35);
            flex-shrink: 0;
          }}
          .drift-name {{
            font-family: Syne, system-ui, sans-serif;
            font-weight: 800; font-size: 1.35rem;
            letter-spacing: -0.03em; color: #faf5ff; line-height: 1.15;
          }}
          .drift-tag {{
            font-family: ui-monospace, monospace;
            font-size: 0.62rem; letter-spacing: 0.2em;
            text-transform: uppercase; color: rgba(196,181,253,0.7);
            margin-top: 0.2rem;
          }}
          .drift-stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.55rem;
          }}
          .drift-stat {{
            text-align: center;
            padding: 0.7rem 0.4rem;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.04);
          }}
          .drift-stat .n {{
            font-family: Syne, system-ui, sans-serif;
            font-weight: 800; font-size: 1.25rem;
            letter-spacing: -0.02em; color: #f5edff;
          }}
          .drift-stat .l {{
            font-size: 0.62rem; letter-spacing: 0.12em;
            text-transform: uppercase; color: rgba(180,170,210,0.55);
            margin-top: 0.15rem;
          }}
          .drift-stat.bal .n {{
            background: linear-gradient(120deg, #c4b5fd, #5eead4);
            -webkit-background-clip: text; background-clip: text;
            -webkit-text-fill-color: transparent;
          }}
          .drift-card {{
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.09);
            background: linear-gradient(160deg, rgba(24,20,36,0.75), rgba(12,12,18,0.85));
            padding: 0.95rem 1rem;
            margin-bottom: 0.55rem;
            transition: border-color 0.2s ease, transform 0.2s ease;
          }}
          .drift-card:hover {{
            border-color: rgba(167,139,250,0.35);
            transform: translateY(-1px);
          }}
          .drift-card .cat {{
            font-family: ui-monospace, monospace;
            font-size: 0.6rem; letter-spacing: 0.16em;
            text-transform: uppercase; color: rgba(167,139,250,0.75);
            margin-bottom: 0.25rem;
          }}
          .drift-card .title {{
            font-weight: 700; font-size: 0.98rem;
            letter-spacing: -0.02em; color: #f4f0ff;
            margin-bottom: 0.25rem;
          }}
          .drift-card .desc {{
            font-size: 0.84rem; line-height: 1.45;
            color: rgba(200,195,220,0.72);
          }}
          .drift-price {{
            font-family: ui-monospace, monospace;
            font-size: 0.78rem; font-weight: 600;
            color: #5eead4; letter-spacing: 0.04em;
          }}
          .drift-owned {{
            font-family: ui-monospace, monospace;
            font-size: 0.72rem; color: rgba(167,139,250,0.8);
            letter-spacing: 0.08em; text-transform: uppercase;
          }}
          .drift-sec {{
            font-family: ui-monospace, monospace;
            font-size: 0.62rem; letter-spacing: 0.2em;
            text-transform: uppercase; color: rgba(196,181,253,0.65);
            margin: 0.85rem 0 0.5rem;
          }}
        </style>
        <div class="drift-shell">
          <div class="drift-inner">
            <div class="drift-brand">
              <div class="drift-logo">◈</div>
              <div>
                <div class="drift-name">The Drift Counter</div>
                <div class="drift-tag">Meridium exchange · Residuum market</div>
              </div>
            </div>
            <div class="drift-stats">
              <div class="drift-stat bal"><div class="n">{bal}</div><div class="l">Residuum</div></div>
              <div class="drift-stat"><div class="n">{n_done}/{n_quests}</div><div class="l">Quests</div></div>
              <div class="drift-stat"><div class="n">{n_owned}</div><div class="l">Owned</div></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    t_shop, t_quests, t_inv = st.tabs(["Counter", "Fieldwork", "Holdings"])

    with t_shop:
        st.caption("Spend Residuum on palettes, type, lore, and latent modules.")
        cats = []
        for it in BAZAAR_ITEMS.values():
            if it["cat"] not in cats:
                cats.append(it["cat"])
        for cat in cats:
            st.markdown(f'<div class="drift-sec">{cat}</div>', unsafe_allow_html=True)
            for iid, it in BAZAAR_ITEMS.items():
                if it["cat"] != cat:
                    continue
                owned = iid in inv
                st.markdown(
                    f"""
                    <div class="drift-card">
                      <div class="cat">{it['cat']}</div>
                      <div class="title">{it['name']}</div>
                      <div class="desc">{it['desc']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                b1, b2 = st.columns([3, 1.2])
                with b1:
                    if owned:
                        st.markdown('<div class="drift-owned">In holdings</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="drift-price">{it["cost"]} ◆</div>', unsafe_allow_html=True)
                with b2:
                    if owned:
                        st.caption("—")
                    else:
                        if st.button("Acquire", key=f"baz_buy_{iid}", use_container_width=True):
                            status = buy_bazaar_item(iid)
                            if status == "ok":
                                st.success(f"Acquired {it['name']}")
                                st.rerun()
                            elif status == "broke":
                                st.warning("Not enough Residuum.")
                            elif status == "owned":
                                st.info("Already owned.")

    with t_quests:
        st.caption("One-time fieldwork. Each action pays Residuum once.")
        for qid, q in QUESTS.items():
            got = qid in done
            mark = "DONE" if got else "OPEN"
            col = "rgba(94,234,212,0.85)" if got else "rgba(196,181,253,0.75)"
            st.markdown(
                f"""
                <div class="drift-card">
                  <div class="cat" style="color:{col}">{mark} · +{q['reward']} ◆</div>
                  <div class="title">{q['title']}</div>
                  <div class="desc">{q['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with t_inv:
        st.caption("What the shell already knows you carry.")
        if not inv:
            st.markdown(
                """
                <div class="drift-card">
                  <div class="title">Empty holdings</div>
                  <div class="desc">Complete fieldwork, then acquire goods at the Counter.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for iid in st.session_state.inventory:
                it = _all_shop_items().get(iid) or {"name": iid, "desc": "", "cat": "Item"}
                st.markdown(
                    f"""
                    <div class="drift-card">
                      <div class="cat">{it.get('cat','Item')}</div>
                      <div class="title">{it.get('name', iid)}</div>
                      <div class="desc">{it.get('desc','')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        if st.session_state.get("jaime_channel_key") or st.session_state.get("jaime_dossier_unlocked"):
            if st.button("Open Jaime residual channel", use_container_width=True, key="baz_open_jaime", type="primary"):
                st.session_state.view = "jaime_residual"
                st.session_state.popup = False
                st.rerun()

    # ---- Shady Bazaar section ----
    st.markdown('<div class="drift-sec">Shady Bazaar · black market</div>', unsafe_allow_html=True)
    try_unlock_bazaar()
    unlocked = bool(st.session_state.get("bazaar_unlocked"))
    has_key = bool(st.session_state.get("black_key_owned")) or "item_black_key" in (st.session_state.inventory or [])
    done_set = set(st.session_state.quests_done or [])

    if not unlocked:
        st.markdown(
            """
            <div class="drift-card" style="border-color:rgba(220,38,38,0.35);">
              <div class="cat" style="color:#fca5a5">LOCKED</div>
              <div class="title">The Bazaar</div>
              <div class="desc">
                A residual broker operates off the public ledger. Complete the shadow contact chain,
                acquire the <b>Black residual key</b> from the Drift Counter, then return.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(
            f"Progress · shadow_contact: {'✓' if 'shadow_contact' in done_set else '—'} · "
            f"black key: {'✓' if has_key else '—'} · "
            f"bazaar open: {'✓' if unlocked else '—'}"
        )
        if "shadow_contact" in done_set and not has_key:
            st.info("Buy the **Black residual key** from the Catalog tab (high cost), then refresh.")
        if has_key and "shadow_contact" in done_set:
            if st.button("Turn the black key — open the Bazaar", key="open_shady_bazaar", type="primary", use_container_width=True):
                st.session_state.bazaar_unlocked = True
                try:
                    complete_quest("bazaar_threshold")
                except Exception:
                    pass
                try:
                    save_user_data()
                except Exception:
                    pass
                st.success("The Bazaar accepts the key. Contracts are now available.")
                st.rerun()
    else:
        st.markdown(
            """
            <div class="drift-card" style="border-color:rgba(220,38,38,0.4);background:linear-gradient(160deg,rgba(40,10,12,0.7),rgba(12,8,10,0.9));">
              <div class="cat" style="color:#fca5a5">OPEN · BROKER ONLINE</div>
              <div class="title">The Bazaar</div>
              <div class="desc">Extremely high-cost residual contracts. Lore sold here does not appear in public files. Payment is final.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        inv_set = set(st.session_state.inventory or [])
        for iid, it in SHADY_BAZAAR_ITEMS.items():
            owned = iid in inv_set
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(
                    f"""
                    <div class="drift-card" style="border-color:rgba(220,38,38,0.22);">
                      <div class="cat" style="color:#fca5a5">{it.get('cat','Item')} · {it.get('cost',0)} ◆</div>
                      <div class="title">{it.get('name', iid)}</div>
                      <div class="desc">{it.get('desc','')}</div>
                      {"<div class='drift-owned'>Owned</div>" if owned else ""}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c2:
                if owned:
                    st.caption("—")
                else:
                    if st.button("Contract", key=f"shady_buy_{iid}", use_container_width=True):
                        status = buy_bazaar_item(iid, shady=True)
                        if status == "ok":
                            st.success(f"Contract sealed: {it['name']}")
                            st.rerun()
                        elif status == "broke":
                            st.warning("Not enough Residuum for this contract.")
                        elif status == "locked":
                            st.error("Bazaar still locked.")
                        elif status == "owned":
                            st.info("Already held.")

    st.markdown('<div class="drift-sec">Residual tools</div>', unsafe_allow_html=True)
    nav1, nav2, nav3 = st.columns(3)
    with nav1:
        if st.button("📜 Lore Archive", key="goto_lore_archive", use_container_width=True):
            st.session_state.view = "lore_archive"
            st.session_state.popup = False
            st.rerun()
    with nav2:
        if st.button("♟ Chess", key="goto_chess", use_container_width=True):
            st.session_state.view = "chess"
            st.session_state.popup = False
            st.rerun()
    with nav3:
        if st.button("🎙 Call Meridium", key="goto_call", use_container_width=True):
            st.session_state.view = "call_meridium"
            st.session_state.popup = False
            st.rerun()


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
        "lab_found": list(st.session_state.get("lab_found") or []),
        "arg_stabilized": bool(st.session_state.get("arg_stabilized")),
        "stabilize_at": st.session_state.get("stabilize_at"),
        "qotd_opens": int(st.session_state.get("qotd_opens") or 0),
        "provider": st.session_state.get("provider", "groq"),
        "model_name": st.session_state.get("model_name", "Smart · GPT-OSS 120B"),
        "show_widgets": bool(st.session_state.get("show_widgets", True)),
        "show_spotify": bool(st.session_state.get("show_spotify", False)),
        "use_wiki_toggle": bool(st.session_state.get("use_wiki_toggle", True)),
        "use_web_toggle": bool(st.session_state.get("use_web_toggle", True)),
        "owner_title": st.session_state.get("owner_title") or "",
        "chats": safe_chats,
        "current_chat_id": st.session_state.get("current_chat_id"),
        "meridium_playlist": st.session_state.get("meridium_playlist") or [],
        "shorts_custom": list(st.session_state.get("shorts_custom") or []),
        "shorts_liked": list(st.session_state.get("shorts_liked") or []),
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
        "residuum": int(st.session_state.get("residuum") or 0),
        "quests_done": list(st.session_state.get("quests_done") or []),
        "inventory": list(st.session_state.get("inventory") or []),
        "lore_owned": list(st.session_state.get("lore_owned") or []),
        "bazaar_unlocked": bool(st.session_state.get("bazaar_unlocked")),
        "black_key_owned": bool(st.session_state.get("black_key_owned")),
        "jaime_dossier_unlocked": bool(st.session_state.get("jaime_dossier_unlocked")),
        "jaime_channel_key": bool(st.session_state.get("jaime_channel_key")),
        "callaghan_margin_owned": bool(st.session_state.get("callaghan_margin_owned")),
        "feat_chat_aura": bool(st.session_state.get("feat_chat_aura")),
        "feat_home_orb": bool(st.session_state.get("feat_home_orb")),
        "feat_double_clock": bool(st.session_state.get("feat_double_clock")),
        "feat_voice_warm": bool(st.session_state.get("feat_voice_warm")),
        "feat_chess_analysis": bool(st.session_state.get("feat_chess_analysis")),
        "contract_silence_owned": bool(st.session_state.get("contract_silence_owned")),
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
        st.session_state.lab_found = list(data.get("lab_found") or [])
        st.session_state.arg_stabilized = bool(data.get("arg_stabilized"))
        st.session_state.stabilize_at = data.get("stabilize_at")
        st.session_state.qotd_opens = int(data.get("qotd_opens") or 0)
        st.session_state.provider = data.get("provider", "groq")
        st.session_state.model_name = data.get("model_name", "Smart · GPT-OSS 120B")
        st.session_state.show_widgets = data.get("show_widgets", True)
        st.session_state.show_spotify = data.get("show_spotify", False)
        st.session_state.use_wiki_toggle = data.get("use_wiki_toggle", True)
        st.session_state.use_web_toggle = data.get("use_web_toggle", True)
        st.session_state.meridium_playlist = data.get("meridium_playlist") or []
        st.session_state.shorts_custom = list(data.get("shorts_custom") or [])
        st.session_state.shorts_liked = list(data.get("shorts_liked") or [])
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
        st.session_state.owner_title = str(data.get("owner_title") or "")
        st.session_state.archive_key = bool(data.get("archive_key"))
        st.session_state.board_entered_once = bool(data.get("board_entered_once"))
        st.session_state.lab_door_unlocked = bool(data.get("lab_door_unlocked"))
        st.session_state.nadir_files_opened = list(data.get("nadir_files_opened") or [])
        st.session_state.residuum = int(data.get("residuum") or 0)
        st.session_state.quests_done = list(data.get("quests_done") or [])
        st.session_state.inventory = list(data.get("inventory") or [])
        st.session_state.lore_owned = list(data.get("lore_owned") or [])
        st.session_state.bazaar_unlocked = bool(data.get("bazaar_unlocked"))
        st.session_state.black_key_owned = bool(data.get("black_key_owned"))
        st.session_state.jaime_dossier_unlocked = bool(data.get("jaime_dossier_unlocked"))
        st.session_state.jaime_channel_key = bool(data.get("jaime_channel_key"))
        st.session_state.callaghan_margin_owned = bool(data.get("callaghan_margin_owned"))
        st.session_state.feat_chat_aura = bool(data.get("feat_chat_aura"))
        st.session_state.feat_home_orb = bool(data.get("feat_home_orb"))
        st.session_state.feat_double_clock = bool(data.get("feat_double_clock"))
        st.session_state.feat_voice_warm = bool(data.get("feat_voice_warm"))
        st.session_state.feat_chess_analysis = bool(data.get("feat_chess_analysis"))
        st.session_state.contract_silence_owned = bool(data.get("contract_silence_owned"))
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


def moderate_chat_message(text: str):
    """Chatroom filter — block disallowed content; light scrub for excess."""
    raw = str(text or "").strip()
    if not raw:
        return False, "empty"
    ok, _ = moderate_text(raw)
    if not ok:
        return False, "blocked"
    # Soft length + control-char scrub
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", raw)
    cleaned = cleaned[:800]
    if not cleaned.strip():
        return False, "empty"
    return True, cleaned


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
    "model_name": "Smart · GPT-OSS 120B",
    "api_key_val": "",
    "arg_unlocked": False,
    "anomaly_warned": False,
    "glitches_found": [],
    "voss_file_unlocked": False,
    "lab_visits": 0,
    "arg_stabilized": False,
    "unlocked_themes": [],
    "meridium_playlist": [],
    "shorts_custom": [],
    "shorts_liked": [],
    "shorts_index": 0,
    "music_status": "",
    "eq_bands": [0, 0, 0, 0, 0, 0, 0],
    "eq_preset": "Flat",
    "eq_custom_presets": {},
    "eq_enabled": True,
    "stabilize_at": None,
    "qotd_opens": 0,
    "residuum": 0,
    "quests_done": [],
    "inventory": [],
    "lore_owned": [],
    "bazaar_unlocked": False,
    "black_key_owned": False,
    "feat_voice_warm": False,
    "feat_chess_analysis": False,
    "contract_silence_owned": False,

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
    "unlocked_themes", "meridium_playlist", "shorts_custom", "shorts_liked", "shorts_index", "music_status",
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

def speak_html(text: str, autoplay: bool = True, rate: float = 1.0, pitch: float = 1.0) -> str:
    """Browser text-to-speech. Uses parent window when embedded; retries voices."""
    safe = json.dumps((text or "")[:1200])
    auto = "true" if autoplay else "false"
    rate_js = float(rate) if rate else 1.0
    pitch_js = float(pitch) if pitch else 1.0
    uid = uuid.uuid4().hex[:8]
    return f"""
    <div style="margin:0;padding:6px 0;font-family:system-ui,sans-serif;background:transparent;">
      <button id="mer_spk_{uid}" style="
        background:linear-gradient(135deg,#c4a7e7,#9d7cd8);color:#fff;border:none;
        border-radius:12px;padding:10px 16px;font-weight:600;font-size:14px;
        width:100%;cursor:pointer;">
        🔊 Speak
      </button>
      <div id="mer_spk_st_{uid}" style="margin-top:4px;font-size:12px;color:#8b8798;"></div>
    </div>
    <script>
    (function() {{
      const t = {safe};
      const auto = {auto};
      const st = document.getElementById('mer_spk_st_{uid}');
      const btn = document.getElementById('mer_spk_{uid}');
      function pickVoice(synth) {{
        const voices = synth.getVoices() || [];
        return voices.find(v => /en-GB/i.test(v.lang) && /female|google|natural|samantha|moira|zira/i.test(v.name))
          || voices.find(v => /en-GB/i.test(v.lang))
          || voices.find(v => /en-US/i.test(v.lang) && /female|google|natural|samantha|zira/i.test(v.name))
          || voices.find(v => /en-US/i.test(v.lang))
          || voices.find(v => /^en/i.test(v.lang))
          || null;
      }}
      function speak() {{
        const synth = window.speechSynthesis || (window.parent && window.parent.speechSynthesis);
        if (!synth) {{
          if (st) st.textContent = 'Speech not supported — use Chrome or Edge.';
          return;
        }}
        try {{ synth.cancel(); }} catch(e){{}}
        const u = new SpeechSynthesisUtterance(t);
        u.rate = {rate_js};
        u.pitch = {pitch_js};
        u.volume = 1.0;
        const v = pickVoice(synth);
        if (v) u.voice = v;
        u.onstart = () => {{ if (st) st.textContent = 'Speaking…'; }};
        u.onend = () => {{ if (st) st.textContent = ''; }};
        u.onerror = () => {{ if (st) st.textContent = 'Tap Speak if audio was blocked.'; }};
        synth.speak(u);
      }}
      if (btn) btn.onclick = function(ev) {{ ev.preventDefault(); speak(); }};
      const synth0 = window.speechSynthesis || (window.parent && window.parent.speechSynthesis);
      if (synth0) {{
        synth0.getVoices();
        synth0.onvoiceschanged = function() {{ synth0.getVoices(); }};
      }}
      if (auto) {{
        setTimeout(speak, 250);
        setTimeout(function() {{
          try {{
            const s = window.speechSynthesis || (window.parent && window.parent.speechSynthesis);
            if (s && !s.speaking) speak();
          }} catch(e){{}}
        }}, 700);
      }}
    }})();
    </script>
    """

GROQ_MODELS = {
    # Post Aug 2026 deprecation map (llama-3.3-70b-versatile / llama-3.1-8b-instant retired for free/dev)
    "Smart · GPT-OSS 120B": "openai/gpt-oss-120b",
    "Fast · GPT-OSS 20B": "openai/gpt-oss-20b",
    "Qwen3.6 27B": "qwen/qwen3.6-27b",
    "Compound": "groq/compound",
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
            # migrate retired display names / ids
            legacy = {
                "Smart · Llama 3.3 70B": "openai/gpt-oss-120b",
                "Fast · Llama 3.1 8B": "openai/gpt-oss-20b",
                "Qwen3 32B": "qwen/qwen3.6-27b",
                "Llama 3.1 70B": "openai/gpt-oss-120b",
                "llama-3.3-70b-versatile": "openai/gpt-oss-120b",
                "llama-3.1-8b-instant": "openai/gpt-oss-20b",
                "llama-3.1-70b-versatile": "openai/gpt-oss-120b",
                "qwen/qwen3-32b": "qwen/qwen3.6-27b",
            }
            if name in legacy:
                return legacy[name]
            m = GROQ_MODELS.get(name, "openai/gpt-oss-120b")
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
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b",
            "qwen/qwen3.6-27b",
            "groq/compound-mini",
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
            err_s = str(e).lower()
            if _is_rate_limit_error(e) or "model_not_found" in err_s or "does not exist" in err_s or "404" in err_s:
                # rate limit or retired model id — try next fallback
                continue
            # non-recoverable error: stop
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
        model = "openai/gpt-oss-20b"
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
try:
    if st.session_state.get("signed_in"):
        render_site_announcement()
        apply_site_effects_css()
except Exception:
    pass

# Session-local dismiss — compact, only when a banner is live
try:
    _aid = st.session_state.get("_active_announce_id")
    if (
        st.session_state.get("signed_in")
        and _aid
        and st.session_state.get("_dismissed_announce_id") != _aid
        and st.session_state.get("view") not in ("nadir_transition",)
    ):
        _d1, _d2, _d3 = st.columns([5, 2, 5])
        with _d2:
            if st.button("Dismiss", key="dismiss_site_announce", use_container_width=True):
                st.session_state["_dismissed_announce_id"] = _aid
                st.session_state.pop("_active_announce_id", None)
                st.session_state.pop("_active_announce_text", None)
                st.rerun()
except Exception:
    pass

# Hard-stop Nadir ambient (Run Rabbit Run) when leaving the channel
if st.session_state.get("_force_stop_nadir_audio") and st.session_state.get("view") not in (
    "nadir", "nadir_transition"
):
    try:
        stop_meridium_track("nadir")
        stop_meridium_track("door")
        stop_all_meridium_audio()
    except Exception:
        pass
    st.session_state._force_stop_nadir_audio = False
    st.session_state._nadir_music_on = False
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
    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500;1,600&family=Syne:wght@600;700;800&display=swap');

          html, body, .stApp, [data-testid="stAppViewContainer"],
          section.main, [data-testid="stAppViewBlockContainer"] {
            min-height: 100vh !important;
            background:
              radial-gradient(ellipse 900px 600px at 15% -10%, rgba(167,139,250,0.28), transparent 55%),
              radial-gradient(ellipse 700px 500px at 95% 10%, rgba(94,234,212,0.12), transparent 50%),
              radial-gradient(ellipse 600px 400px at 50% 110%, rgba(196,167,231,0.12), transparent 45%),
              linear-gradient(180deg, #08070e 0%, #0c0b14 50%, #0a0910 100%) !important;
          }
          .block-container {
            max-width: 520px !important;
            padding-top: 6vh !important;
            padding-bottom: 3rem !important;
          }
          [data-testid="stHeader"], footer, #MainMenu, [data-testid="stToolbar"] { display: none !important; }

          .si-orbit {
            position: fixed; inset: 0; pointer-events: none; overflow: hidden; z-index: 0;
          }
          .si-orbit span {
            position: absolute; border-radius: 50%;
            border: 1px solid rgba(196,167,231,0.08);
            animation: siFloat 14s ease-in-out infinite;
          }
          .si-orbit span:nth-child(1) { width: 280px; height: 280px; top: -60px; left: -40px; }
          .si-orbit span:nth-child(2) { width: 180px; height: 180px; bottom: 10%; right: -30px; animation-delay: -4s; }
          .si-orbit span:nth-child(3) { width: 100px; height: 100px; top: 40%; left: 8%; animation-delay: -7s; border-color: rgba(94,234,212,0.1); }

          .si-wrap {
            position: relative; z-index: 1;
            margin: 0 auto;
            padding: 2.35rem 1.7rem 1.6rem;
            border-radius: 26px;
            overflow: hidden;
            border: 1px solid rgba(196,167,231,0.32);
            background:
              radial-gradient(ellipse at 18% 0%, rgba(196,167,231,0.22), transparent 52%),
              radial-gradient(ellipse at 92% 100%, rgba(94,234,212,0.1), transparent 48%),
              linear-gradient(165deg, rgba(30,24,44,0.94) 0%, rgba(12,10,18,0.97) 100%);
            box-shadow:
              0 36px 90px rgba(0,0,0,0.55),
              0 0 80px rgba(167,139,250,0.14),
              inset 0 1px 0 rgba(255,255,255,0.07);
            text-align: center;
            animation: siIn 0.85s cubic-bezier(0.22, 1, 0.36, 1) both;
            backdrop-filter: blur(20px);
          }
          .si-wrap::before {
            content: "";
            position: absolute; left: 0; right: 0; top: 0; height: 2px;
            background: linear-gradient(90deg, transparent, #c4a7e7, #5eead4, #c4a7e7, transparent);
            opacity: 0.95;
            animation: siScan 4.5s ease-in-out infinite;
          }
          .si-wrap::after {
            content: "";
            position: absolute; inset: 0;
            background: linear-gradient(115deg, transparent 35%, rgba(255,255,255,0.045) 50%, transparent 65%);
            background-size: 220% 100%;
            animation: siSheen 9s ease-in-out infinite;
            pointer-events: none;
          }

          .si-mark {
            position: relative; z-index: 1;
            width: 72px; height: 72px; margin: 0 auto 1.1rem;
            border-radius: 22px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.85rem; font-weight: 800; color: #0a0a10;
            background: linear-gradient(135deg, #c4b5fd 0%, #a78bfa 45%, #5eead4 100%);
            box-shadow: 0 0 36px rgba(167,139,250,0.45), 0 14px 28px rgba(0,0,0,0.35);
            animation: siPulse 3.2s ease-in-out infinite;
          }
          .si-kicker {
            position: relative; z-index: 1;
            font-family: ui-monospace, monospace;
            font-size: 0.68rem; letter-spacing: 0.28em; text-transform: uppercase;
            color: rgba(196,167,231,0.8); margin-bottom: 0.55rem;
          }
          .si-title {
            position: relative; z-index: 1;
            font-family: Syne, system-ui, sans-serif;
            font-size: clamp(2.1rem, 7vw, 2.75rem);
            font-weight: 800; letter-spacing: -0.04em;
            color: #faf7ff; margin: 0 0 0.55rem;
            background: linear-gradient(120deg, #faf7ff 20%, #c4a7e7 55%, #5eead4 100%);
            -webkit-background-clip: text; background-clip: text;
            -webkit-text-fill-color: transparent;
          }
          .si-sub {
            position: relative; z-index: 1;
            font-family: "Cormorant Garamond", Georgia, serif;
            font-style: italic; font-size: 1.12rem;
            color: rgba(210,200,230,0.82); line-height: 1.45;
            margin: 0 auto 1.15rem; max-width: 20rem;
          }
          .si-ridge {
            position: relative; z-index: 1;
            height: 1px; margin: 0.4rem auto 1rem; max-width: 200px;
            background: linear-gradient(90deg, transparent, rgba(196,167,231,0.45), transparent);
          }
          .si-pills {
            position: relative; z-index: 1;
            display: flex; flex-wrap: wrap; gap: 0.4rem;
            justify-content: center;
          }
          .si-pill {
            font-family: ui-monospace, monospace;
            font-size: 0.62rem; letter-spacing: 0.1em; text-transform: uppercase;
            padding: 0.35rem 0.65rem; border-radius: 999px;
            color: rgba(220,210,240,0.85);
            border: 1px solid rgba(196,167,231,0.22);
            background: rgba(255,255,255,0.04);
          }
          .si-owner-note {
            text-align: center;
            font-family: ui-monospace, monospace;
            font-size: 0.68rem; letter-spacing: 0.16em;
            color: #c4a7e7; margin: 0.6rem 0 0.35rem;
          }

          div[data-testid="stTextInput"] input {
            border-radius: 14px !important;
            border: 1px solid rgba(196,167,231,0.28) !important;
            background: rgba(16,14,24,0.85) !important;
            color: #f0eef8 !important;
            padding: 0.85rem 1rem !important;
            font-size: 1rem !important;
          }
          div[data-testid="stTextInput"] input:focus {
            border-color: rgba(196,167,231,0.55) !important;
            box-shadow: 0 0 0 3px rgba(167,139,250,0.18) !important;
          }
          div[data-testid="stButton"] button[kind="primary"] {
            border-radius: 14px !important;
            min-height: 3rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.02em !important;
            background: linear-gradient(135deg, #a78bfa, #7c3aed) !important;
            border: 1px solid rgba(196,167,231,0.45) !important;
            box-shadow: 0 8px 28px rgba(124,58,237,0.35) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
          }
          div[data-testid="stButton"] button[kind="primary"]:hover {
            border-color: #c4a7e7 !important;
            box-shadow: 0 12px 40px rgba(167,139,250,0.4) !important;
            transform: translateY(-2px);
          }

          @keyframes siIn {
            from { opacity: 0; transform: translateY(22px) scale(0.97); filter: blur(8px); }
            to   { opacity: 1; transform: none; filter: none; }
          }
          @keyframes siSheen {
            0%, 100% { background-position: 130% 0; }
            50% { background-position: -30% 0; }
          }
          @keyframes siPulse {
            0%, 100% { box-shadow: 0 0 28px rgba(167,139,250,0.4), 0 12px 28px rgba(0,0,0,0.35); }
            50% { box-shadow: 0 0 48px rgba(196,167,231,0.6), 0 12px 28px rgba(0,0,0,0.35); }
          }
          @keyframes siScan {
            0%, 100% { opacity: 0.55; filter: brightness(1); }
            50% { opacity: 1; filter: brightness(1.25); }
          }
          @keyframes siFloat {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(18px); }
          }
        </style>
        <div class="si-orbit"><span></span><span></span><span></span></div>
        <div class="si-wrap">
          <div class="si-mark">◈</div>
          <div class="si-kicker">Quiet intelligence shell</div>
          <div class="si-title">Meridium</div>
          <div class="si-sub">A calm room for thought. Enter your name to open the shell.</div>
          <div class="si-ridge"></div>
          <div class="si-pills">
            <span class="si-pill">Caelestia</span>
            <span class="si-pill">Chat · Media · Library</span>
            <span class="si-pill">Private by design</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    name = st.text_input(
        "Your name",
        placeholder="Your name",
        key="signin_name",
        label_visibility="collapsed",
    )
    name_l = (name or "").strip().lower()
    needs_owner_pw = name_l in _owner_names()
    owner_pw = ""
    if needs_owner_pw:
        st.markdown(
            '<div class="si-owner-note">◈ OWNER CHANNEL · password required</div>',
            unsafe_allow_html=True,
        )
        owner_pw = st.text_input(
            "Owner password",
            type="password",
            key="signin_owner_pw",
            placeholder="Owner password",
            label_visibility="collapsed",
        )

    st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([0.6, 2.8, 0.6])
    with c2:
        if st.button("Enter Meridium", use_container_width=True, type="primary", key="signin_btn"):
            ok, result = moderate_username(name)
            owner_ok = True
            if not ok:
                st.error(result)
                owner_ok = False
            elif needs_owner_pw:
                expected = _owner_password()
                given = (owner_pw or "").strip()
                if not expected:
                    st.error(
                        "Owner login is locked on this deploy. "
                        "Add OWNER_PASSWORD in Streamlit Secrets "
                        "(Manage app → Settings → Secrets)."
                    )
                    owner_ok = False
                elif not given or given != expected:
                    st.error("Owner password incorrect.")
                    owner_ok = False
            if ok and owner_ok:
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
                    st.session_state.owner_title = ""
                    create_new_chat()
                elif not st.session_state.get("chats"):
                    create_new_chat()
                try:
                    apply_owner_grants_for_user(st.session_state.username)
                except Exception:
                    pass
                st.session_state.show_intro = True
                save_user_data()
                st.rerun()

    st.markdown(
        """
        <div class="si-foot">
          Built with care · Grok · xAI<br/>
          iPhone · Share → Add to Home Screen
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# Live presence heartbeat (shared JSON — owner panel reads this)
try:
    presence_heartbeat()
except Exception:
    pass
try:
    apply_owner_grants_for_user(st.session_state.get("username") or "")
except Exception:
    pass

# Creator invite notification — global (any page except already in room)
_inv_user = (st.session_state.get("username") or "").strip()
if (
    _inv_user
    and st.session_state.get("signed_in")
    and not is_owner(_inv_user)
    and st.session_state.get("view") != "owner_room"
    and chatroom_has_pending(_inv_user)
):
    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=swap');
          .creator-invite-banner {
            margin: 0.5rem 0 0.85rem;
            padding: 1.1rem 1.2rem 0.95rem;
            border-radius: 16px;
            border: 1px solid rgba(196,167,231,0.5);
            background:
              radial-gradient(ellipse at 15% 0%, rgba(196,167,231,0.22), transparent 50%),
              linear-gradient(165deg, #1a1428 0%, #0e0c16 100%);
            box-shadow: 0 10px 32px rgba(0,0,0,0.4);
            text-align: center;
          }
          .creator-invite-banner .ci-mark {
            font-family: ui-monospace, SFMono-Regular, monospace !important;
            font-size: 0.62rem !important;
            letter-spacing: 0.22em;
            color: #c4a7e7 !important;
            margin-bottom: 0.5rem;
            opacity: 0.9;
          }
          .creator-invite-banner .ci-title {
            font-family: 'Cormorant Garamond', Georgia, 'Times New Roman', serif !important;
            font-size: clamp(1.4rem, 3.5vw, 1.85rem) !important;
            font-weight: 600 !important;
            font-style: italic !important;
            color: #f5f0ff !important;
            line-height: 1.3 !important;
          }
          .creator-invite-banner .ci-sub {
            margin-top: 0.4rem;
            font-family: 'Cormorant Garamond', Georgia, serif !important;
            font-size: 1rem !important;
            color: #c8bddc !important;
          }
        </style>
        <div class="creator-invite-banner">
          <div class="ci-mark">MERIDIUM · CREATOR CHANNEL</div>
          <div class="ci-title">The creator has invited you to chat.</div>
          <div class="ci-sub">Accept to join the observation desk with Drae.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _ia, _ib = st.columns(2)
    with _ia:
        if st.button("Accept", key="chat_invite_accept_global", use_container_width=True, type="primary"):
            if chatroom_accept(_inv_user):
                st.session_state.view = "owner_room"
                st.rerun()
    with _ib:
        if st.button("Decline", key="chat_invite_decline_global", use_container_width=True):
            chatroom_decline(_inv_user)
            st.rerun()

# Personalized intro (once after sign-in) — true fullscreen veil
if st.session_state.show_intro:
    user = st.session_state.username
    if is_owner(user):
        intro_main = f'Welcome home, <span>{user}</span>'
        intro_sub = "Meridium recognises you as its owner"
    else:
        intro_main = f'Hello, <span>{user}</span>'
        intro_sub = "Personal intelligence · Caelestia shell"
    st.markdown(f"""
    <style>
      html, body, .stApp, [data-testid="stAppViewContainer"],
      section.main, [data-testid="stAppViewBlockContainer"],
      .block-container, [data-testid="stMain"] {{
        margin: 0 !important; padding: 0 !important;
        max-width: 100% !important; width: 100% !important;
        min-height: 100vh !important; height: 100% !important;
        background: #07060c !important;
        overflow: hidden !important;
      }}
      [data-testid="stHeader"], footer, #MainMenu, [data-testid="stToolbar"],
      [data-testid="stDecoration"], [data-testid="stStatusWidget"] {{
        display: none !important;
      }}
      @keyframes introVeil {{
        0%   {{ opacity: 0; }}
        12%  {{ opacity: 1; }}
        72%  {{ opacity: 1; }}
        100% {{ opacity: 0; }}
      }}
      @keyframes introRise {{
        from {{ opacity: 0; transform: translateY(16px); filter: blur(8px); }}
        to   {{ opacity: 1; transform: none; filter: none; }}
      }}
      @keyframes introScan {{
        0%, 100% {{ transform: translateX(-30%); opacity: 0.4; }}
        50% {{ transform: translateX(30%); opacity: 1; }}
      }}
      .intro-veil {{
        position: fixed !important;
        inset: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        min-height: 100dvh !important;
        z-index: 2147483647 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background:
          radial-gradient(ellipse 80% 50% at 50% 40%, rgba(167,139,250,0.16), transparent 60%),
          radial-gradient(ellipse 60% 40% at 80% 80%, rgba(45,212,191,0.08), transparent 50%),
          #07060c !important;
        animation: introVeil 2.4s ease forwards;
        pointer-events: none;
      }}
      .intro-inner {{ text-align: center; padding: 1.5rem; animation: introRise 0.85s cubic-bezier(0.22,1,0.36,1) 0.15s both; }}
      .intro-k {{
        font-family: ui-monospace, monospace;
        font-size: 0.7rem; letter-spacing: 0.28em; text-transform: uppercase;
        color: #c4a7e7; margin-bottom: 1rem;
      }}
      .intro-k::after {{
        content: ""; display: block; width: 48px; height: 2px; margin: 0.75rem auto 0;
        background: linear-gradient(90deg, transparent, #c4a7e7, transparent);
        animation: introScan 2s ease-in-out infinite;
      }}
      .intro-main {{
        font-family: Syne, system-ui, sans-serif;
        font-size: clamp(1.6rem, 5vw, 2.35rem);
        font-weight: 700; letter-spacing: -0.03em;
        color: #f4f0ff; line-height: 1.2;
      }}
      .intro-main span {{
        background: linear-gradient(120deg, #c4a7e7, #5eead4);
        -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent;
      }}
      .intro-sub {{
        margin-top: 0.85rem;
        font-size: 0.95rem; color: rgba(180,170,200,0.72);
        letter-spacing: 0.02em;
      }}
    </style>
    <div class="intro-veil">
      <div class="intro-inner">
        <div class="intro-k">Meridium</div>
        <div class="intro-main">{intro_main}</div>
        <div class="intro-sub">{intro_sub}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(2.3)
    st.session_state.show_intro = False
    st.rerun()

# ===== SEALED NOTE (query param → open note; must run before home) =====
try:
    if st.session_state.get("signed_in") and str(st.query_params.get("sealed") or "") == "1":
        try:
            del st.query_params["sealed"]
        except Exception:
            try:
                st.query_params.from_dict({})
            except Exception:
                pass
        msg = register_qotd_open()
        if msg:
            st.session_state["_egg_flash"] = msg
            if "Third knock" in str(msg):
                unlock_theme("Soft Static", "third knock on the quote")
        unlock_theme("M-119 Amber", "you found the sealed note")
        try:
            complete_quest("sealed_note", silent=True)
        except Exception:
            pass
        st.session_state.view = "note"
except Exception:
    pass

# Maintenance mode — guests blocked from shell (owner always passes)
try:
    _fx_gate = site_effects_load()
    if (
        st.session_state.get("signed_in")
        and _fx_gate.get("maintenance_mode")
        and not is_owner(st.session_state.get("username") or "")
    ):
        _mm = str(_fx_gate.get("maintenance_message") or "Meridium is under maintenance.").strip()
        st.markdown(
            f"""
            <style>
              .stApp, [data-testid="stAppViewContainer"] {{
                background: #07060a !important;
              }}
              [data-testid="stHeader"], footer, #MainMenu {{ display:none !important; }}
              .maint-wrap {{
                min-height: 70vh; display:flex; align-items:center; justify-content:center;
                text-align:center; padding: 2rem 1.25rem;
              }}
              .maint-card {{
                max-width: 420px; padding: 2rem 1.5rem; border-radius: 22px;
                border: 1px solid rgba(196,167,231,0.28);
                background: linear-gradient(160deg, rgba(28,22,40,0.95), rgba(10,10,16,0.98));
                box-shadow: 0 24px 60px rgba(0,0,0,0.45);
              }}
              .maint-card .k {{
                font-family: ui-monospace, monospace; font-size: 0.65rem;
                letter-spacing: 0.22em; color: #c4a7e7; text-transform: uppercase;
                margin-bottom: 0.75rem;
              }}
              .maint-card h1 {{
                font-size: 1.45rem; color: #f0eef8; margin: 0 0 0.6rem;
                letter-spacing: -0.02em;
              }}
              .maint-card p {{ color: #9a94a8; line-height: 1.55; margin: 0; }}
            </style>
            <div class="maint-wrap"><div class="maint-card">
              <div class="k">Meridium · maintenance</div>
              <h1>Shell paused</h1>
              <p>{_mm.replace('<','&lt;')}</p>
            </div></div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Sign out", key="maint_signout", use_container_width=True):
            reset_user_session(keep_auth=False)
            st.rerun()
        st.stop()
except Exception:
    pass

# Force guests to Home only
try:
    _fx_fh = site_effects_load()
    if (
        st.session_state.get("signed_in")
        and _fx_fh.get("force_home_only")
        and not is_owner(st.session_state.get("username") or "")
        and st.session_state.get("view") not in ("home", None, "")
    ):
        st.session_state.view = "home"
except Exception:
    pass

# Owner MOTD / global toast (one-shot style banner)
try:
    _fx_toast = site_effects_load()
    _toast = str(_fx_toast.get("global_toast") or "").strip()
    _motd = str(_fx_toast.get("owner_motd") or "").strip()
    if st.session_state.get("signed_in") and _toast and st.session_state.get("_seen_global_toast") != _toast:
        st.info(_toast)
        st.session_state["_seen_global_toast"] = _toast
    if st.session_state.get("signed_in") and _motd and is_owner(st.session_state.get("username") or ""):
        st.caption(f"Owner MOTD · {_motd}")
except Exception:
    pass

# ===== MENU (Codex shell) =====
if st.session_state.popup:
    st.markdown(
        """
        <style>
          div[data-testid="stVerticalBlock"] button p {
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
            max-width: 100% !important;
          }
          .menu-hero {
            position: relative; overflow: hidden;
            padding: 1.35rem 1.3rem 1.15rem;
            border-radius: 22px;
            border: 1px solid rgba(196,167,231,0.28);
            background:
              radial-gradient(ellipse at 0% 0%, rgba(167,139,250,0.22), transparent 55%),
              radial-gradient(ellipse at 100% 100%, rgba(244,114,182,0.12), transparent 50%),
              linear-gradient(155deg, rgba(22,16,36,0.96), rgba(10,8,16,0.98));
            margin-bottom: 0.85rem;
            box-shadow: 0 20px 48px rgba(0,0,0,0.35);
          }
          .menu-hero::before {
            content: ""; position: absolute; left: 0; right: 0; top: 0; height: 2px;
            background: linear-gradient(90deg, transparent, #c4a7e7, #f472b6, transparent);
          }
          .menu-hero .kicker {
            font-family: ui-monospace, monospace; font-size: 0.6rem;
            letter-spacing: 0.24em; text-transform: uppercase;
            color: rgba(196,167,231,0.75); margin-bottom: 0.4rem;
          }
          .menu-hero .hi {
            font-size: 1.4rem; font-weight: 700; letter-spacing: -0.03em;
            margin: 0 0 0.3rem; color: #faf5ff;
          }
          .menu-hero .lo {
            opacity: 0.65; font-size: 0.88rem; margin: 0; color: #d4c8e8;
          }
          .menu-sec {
            font-family: ui-monospace, monospace; font-size: 0.6rem;
            letter-spacing: 0.18em; text-transform: uppercase;
            color: rgba(196,167,231,0.55); margin: 0.65rem 0 0.4rem;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    _uname = st.session_state.get("username") or "friend"
    _own = is_owner(_uname)
    _bal = int(st.session_state.get("residuum") or 0)
    st.markdown(
        f"""
        <div class="menu-hero">
          <div class="kicker">{"Owner channel" if _own else "Meridium · shell menu"}</div>
          <div class="hi">{"Welcome home, " + _uname if _own else "Hello, " + _uname}</div>
          <div class="lo">Navigate · appearance · model · ◆ {_bal} Residuum</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m_nav, m_look, m_model, m_bazaar, m_more = st.tabs(["Go", "Look", "Model", "Drift", "More"])

    with m_nav:
        st.markdown('<div class="menu-sec">Core</div>', unsafe_allow_html=True)
        g1, g2, g3 = st.columns(3)
        with g1:
            if st.button("⌂ Home", use_container_width=True, key="pop_home"):
                st.session_state.view = "home"
                st.session_state.popup = False
                st.rerun()
            if st.button("💬 Chat", use_container_width=True, key="pop_chat", type="primary"):
                st.session_state.view = "chat"
                st.session_state.popup = False
                st.rerun()
            if st.button("＋ New chat", use_container_width=True, key="pop_new"):
                create_new_chat()
                st.session_state.view = "chat"
                st.session_state.popup = False
                st.rerun()
        with g2:
            if st.button("🎙 Call", use_container_width=True, key="pop_call"):
                st.session_state.view = "call_meridium"
                st.session_state.call_phase = st.session_state.get("call_phase") or "idle"
                st.session_state.popup = False
                st.rerun()
            if st.button("♟ Chess", use_container_width=True, key="pop_chess"):
                st.session_state.view = "chess"
                st.session_state.popup = False
                st.rerun()
            if st.button("◈ Drift", use_container_width=True, key="pop_drift"):
                st.session_state.view = "drift"
                st.session_state.popup = False
                st.rerun()
        with g3:
            if st.button("📚 Library", use_container_width=True, key="pop_library"):
                st.session_state.library_reading = None
                st.session_state.view = "library"
                st.session_state.popup = False
                st.rerun()
            if st.button("♫ Music", use_container_width=True, key="pop_music"):
                st.session_state.view = "music"
                st.session_state.popup = False
                st.rerun()
            if st.button("🎬 Cinema", use_container_width=True, key="pop_cinema"):
                st.session_state.cinema_watching = None
                st.session_state.view = "cinema"
                st.session_state.popup = False
                st.rerun()

        st.markdown('<div class="menu-sec">Media</div>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        with m1:
            if st.button("◎ Listen", use_container_width=True, key="pop_listen"):
                st.session_state.view = "listen"
                st.session_state.popup = False
                st.rerun()
        with m2:
            if st.button("▶ Shorts", use_container_width=True, key="pop_shorts"):
                st.session_state.shorts_index = st.session_state.get("shorts_index") or 0
                st.session_state.view = "shorts"
                st.session_state.popup = False
                st.rerun()

        # Conditional ARG / owner
        extra = []
        if lab_is_unlocked():
            extra.append(("🔬 Lab", "lab", "pop_lab"))
        if st.session_state.get("board_unlocked") or st.session_state.get("callaghan_safe_unlocked"):
            extra.append(("📌 Board", "board", "pop_board"))
        if st.session_state.get("voss_file_unlocked"):
            extra.append(("📁 Voss", "voss_file", "pop_voss"))
        if st.session_state.get("lore_owned"):
            extra.append(("📜 Archive", "lore_archive", "pop_lore"))
        if _own:
            extra.append(("👑 Owner", "owner", "pop_owner"))
        elif chatroom_user_allowed(_uname):
            extra.append(("💬 Room", "owner_room", "pop_room"))
        if extra:
            st.markdown('<div class="menu-sec">Unlocked</div>', unsafe_allow_html=True)
            cols = st.columns(min(len(extra), 4))
            for i, (label, view_name, key) in enumerate(extra):
                with cols[i % len(cols)]:
                    if st.button(label, use_container_width=True, key=key):
                        if view_name == "board":
                            st.session_state.board_evidence_open = None
                        if view_name == "voss_file":
                            st.session_state.voss_cutscene_stage = 0
                        if view_name == "lab":
                            st.session_state.lab_transition = True
                        st.session_state.view = view_name
                        st.session_state.popup = False
                        st.rerun()

        st.markdown("---")
        if st.button("✕ Close menu", use_container_width=True, key="pop_close"):
            st.session_state.popup = False
            st.rerun()

    with m_look:
        fonts = available_fonts()
        fi = fonts.index(st.session_state.font) if st.session_state.font in fonts else 0
        ft = st.selectbox("Font", fonts, index=fi, key="pop_font")
        if ft != st.session_state.font:
            st.session_state.font = ft
            save_user_data()
            st.rerun()

        themes = available_themes()
        if "theme" not in st.session_state:
            st.session_state.theme = "Caelestia"
        if st.session_state.theme not in themes:
            if st.session_state.theme in SECRET_THEMES or st.session_state.theme in OWNER_THEMES:
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
            st.caption("Unlocked: " + ", ".join(unlocked_now[:8]) + ("…" if len(unlocked_now) > 8 else ""))
        locked_left = [n for n in SECRET_THEMES if n not in unlocked_now]
        if locked_left:
            st.caption(f"🔒 {len(locked_left)} secret theme(s) still locked")

        w1, w2 = st.columns(2)
        with w1:
            st.session_state.show_widgets = st.checkbox("Time widgets", value=st.session_state.show_widgets, key="pop_time")
            st.session_state.use_wiki_toggle = st.checkbox("Wikipedia", value=st.session_state.use_wiki_toggle, key="pop_wiki")
        with w2:
            st.session_state.show_spotify = st.checkbox("Spotify", value=st.session_state.show_spotify, key="pop_sp")
            st.session_state.use_web_toggle = st.checkbox("Web search", value=st.session_state.use_web_toggle, key="pop_web")

    with m_model:
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
        if st.button("Save model settings", key="pop_save_model", use_container_width=True):
            save_user_data()
            st.success("Saved.")

    with m_bazaar:
        try:
            render_bazaar_tab()
        except Exception as _baz_err:
            st.warning(f"Bazaar unavailable: {_baz_err}")

    with m_more:
        st.caption("Account & data")
        if st.button("↩  Switch user", use_container_width=True, key="pop_signout"):
            reset_user_session(keep_auth=False)
            st.rerun()

        # Backup export/import if present in old menu - keep lightweight
        try:
            payload = {
                "username": st.session_state.get("username"),
                "chats": st.session_state.get("chats") or {},
                "theme": st.session_state.get("theme"),
                "font": st.session_state.get("font"),
                "meridium_playlist": st.session_state.get("meridium_playlist"),
            }
            import json as _json
            st.download_button(
                "Download backup",
                data=_json.dumps(payload, indent=2),
                file_name="meridium_backup.json",
                mime="application/json",
                use_container_width=True,
                key="pop_backup_dl",
            )
        except Exception:
            pass
        up = st.file_uploader("Import backup", type=["json"], key="pop_backup_up")
        if up is not None:
            try:
                import json as _json
                data = _json.loads(up.getvalue().decode("utf-8"))
                if isinstance(data.get("chats"), dict):
                    st.session_state.chats = data["chats"]
                if data.get("meridium_playlist"):
                    st.session_state.meridium_playlist = data["meridium_playlist"]
                if data.get("theme") in THEMES or data.get("theme") in SECRET_THEMES or data.get("theme") in OWNER_THEMES:
                    st.session_state.theme = data["theme"]
                if data.get("font") in FONTS or data.get("font") in OWNER_FONTS:
                    st.session_state.font = data["font"]
                save_user_data()
                st.success("Backup imported.")
                st.rerun()
            except Exception as e:
                st.error(f"Import failed: {e}")

        st.markdown("**Recent chats**")
        for cid, data in sorted(st.session_state.chats.items(), key=lambda x: x[1].get("created", ""), reverse=True)[:8]:
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
          .stApp, [data-testid="stAppViewContainer"], section.main {
            background: radial-gradient(ellipse at 50% 30%, #1a0a12 0%, #050308 55%, #000 100%) !important;
          }
          .dead-wrap {
            max-width: 420px; margin: 12vh auto 0; text-align: center;
            padding: 2rem 1.5rem; border-radius: 24px;
            border: 1px solid rgba(196,80,100,0.25);
            background: linear-gradient(160deg, rgba(28,10,18,0.9), rgba(8,4,10,0.95));
            box-shadow: 0 30px 80px rgba(0,0,0,0.55), 0 0 40px rgba(180,40,60,0.08);
            animation: deadIn 0.7s cubic-bezier(0.22,1,0.36,1) both;
          }
          @keyframes deadIn {
            from { opacity: 0; transform: translateY(16px) scale(0.98); filter: blur(4px); }
            to { opacity: 1; transform: none; filter: none; }
          }
          .dead-kicker {
            font-family: ui-monospace, monospace; font-size: 0.62rem;
            letter-spacing: 0.28em; color: #c05060; text-transform: uppercase;
            margin-bottom: 0.85rem;
          }
          .dead-title {
            font-family: Georgia, 'Times New Roman', serif;
            font-size: 1.45rem; color: #f0d8de; letter-spacing: -0.02em;
            margin: 0 0 0.75rem; line-height: 1.25;
          }
          .dead-body {
            font-family: Georgia, serif; font-style: italic;
            color: rgba(220,190,200,0.72); font-size: 0.98rem;
            line-height: 1.55; margin: 0 0 1.25rem;
          }
          .dead-bar {
            height: 2px; width: 48%; margin: 0 auto 1.25rem;
            background: linear-gradient(90deg, transparent, #a04050, transparent);
            opacity: 0.7;
          }
        </style>
        <div class="dead-wrap">
          <div class="dead-kicker">Redacted control · residual gap</div>
          <div class="dead-title">This surface was never meant to load.</div>
          <div class="dead-bar"></div>
          <p class="dead-body">
            A menu entry pointed here before the tool was pulled.
            The shell kept the address. The Division did not keep the feature.
          </p>
          <p class="dead-body" style="opacity:0.65;font-size:0.88rem;">
            Finding gaps is still observation. Return when you are ready.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Return to Meridium", key="dead_back", use_container_width=True, type="primary"):
            st.session_state.view = "home"
            st.rerun()
    st.stop()




if st.session_state.get("view") != "lab":
    st.session_state._currently_in_lab = False
    st.session_state._lab_entered_ok = False


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
        st.session_state.view = "home"
        st.warning("The lab is sealed. Finish the observation puzzle in chat to unlock it.")
        st.rerun()

    # Cinematic transition gate (once per entry)
    if st.session_state.get("lab_transition") or not st.session_state.get("_lab_entered_ok"):
        st.markdown(
            """
            <style>
              .stApp, [data-testid="stAppViewContainer"], section.main {
                background: #050204 !important;
              }
              .lab-trans {
                max-width: 480px; margin: 14vh auto 0; text-align: center;
                padding: 2rem 1.4rem; border-radius: 20px;
                border: 1px solid rgba(200,60,60,0.35);
                background:
                  radial-gradient(ellipse at 50% 0%, rgba(180,40,40,0.2), transparent 60%),
                  linear-gradient(165deg, rgba(20,6,8,0.96), rgba(6,2,4,0.99));
                animation: labFade 1.1s ease both;
              }
              @keyframes labFade {
                from { opacity: 0; filter: blur(8px); transform: scale(0.97); }
                to { opacity: 1; filter: none; transform: none; }
              }
              .lab-trans .k {
                font-family: ui-monospace, monospace; font-size: 0.62rem;
                letter-spacing: 0.28em; color: #c05050; text-transform: uppercase;
                margin-bottom: 0.75rem;
              }
              .lab-trans .t {
                font-family: Georgia, serif; font-size: 1.5rem; color: #f0d0d0;
                margin: 0 0 0.6rem; letter-spacing: -0.02em;
              }
              .lab-trans .b {
                font-family: Georgia, serif; font-style: italic;
                color: rgba(220,180,180,0.75); line-height: 1.5; font-size: 0.95rem;
              }
            </style>
            <div class="lab-trans">
              <div class="k">Observation Division · airlock</div>
              <div class="t">You were not cleared for this floor.</div>
              <p class="b">
                The residual signature already opened the lock.
                Fluorescent hum. Cold glass. Something on the tray is still warm.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("Step through", use_container_width=True, type="primary", key="lab_trans_enter"):
                st.session_state.lab_transition = False
                st.session_state._lab_entered_ok = True
                st.rerun()
            if st.button("Turn back", use_container_width=True, key="lab_trans_back"):
                st.session_state.lab_transition = False
                st.session_state._lab_entered_ok = False
                st.session_state.view = "home"
                st.rerun()
        st.stop()

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
    try:
        mark_lab_visit()
    except Exception:
        pass
    try:
        unlock_theme("Containment Red", "you entered the observation log", apply=False)
    except Exception:
        pass
    found = st.session_state.get("lab_found") or []
    try:
        if isinstance(found, (list, set)) and len(set(found)) >= 6:
            unlock_theme("Voss Static", "all fragments recovered", apply=False)
    except Exception:
        pass

    try:
        render_lab()
    except Exception as _lab_render_err:
        st.error(f"Lab render error: {_lab_render_err}")
        try:
            _render_lab_builtin(error=str(_lab_render_err))
        except Exception as _lab2:
            st.error(f"Builtin lab also failed: {_lab2}")
            if st.button("← Home", key="lab_fatal_home"):
                st.session_state.view = "home"
                st.rerun()

    st.stop()

if st.session_state.view == "note":
    render_note()
    # Mobile-friendly path to Jaime (Konami is desktop-only in note_view)
    st.markdown("---")
    with st.expander("Residual contact (touch devices)", expanded=False):
        st.caption(
            "Desktop note_view listens for the Konami sequence. "
            "On phones, use the phrase pad below — or buy the Coastal intake pass / Santos dossier in **Menu → Drift Counter**."
        )
        phrase = st.text_input(
            "Phrase",
            key="jaime_mobile_phrase",
            placeholder="hello jaime / open pixel / coastal intake",
            label_visibility="collapsed",
        )
        if st.button("Transmit phrase", key="jaime_mobile_send", use_container_width=True):
            p = (phrase or "").strip().lower()
            if p in {
                "hello jaime", "hello, jaime", "open jaime", "open pixel",
                "coastal intake", "jaime santos", "show jaime",
            } or st.session_state.get("jaime_channel_key") or st.session_state.get("jaime_dossier_unlocked"):
                st.session_state.jaime_dossier_unlocked = True
                st.session_state.view = "jaime_residual"
                st.rerun()
            else:
                st.markdown(
                    "<p style='color:#a08090;font-size:0.88rem'>The channel does not answer that phrase.</p>",
                    unsafe_allow_html=True,
                )
    # Prevent falling through into home / chat routes
    st.stop()

if st.session_state.view == "jaime_residual":
    if not (
        st.session_state.get("jaime_dossier_unlocked")
        or st.session_state.get("jaime_channel_key")
        or st.session_state.get("arg_unlocked")
    ):
        st.session_state.view = "home"
        st.rerun()
    st.markdown(
        """
        <style>
          .jaime-hero {
            padding: 1.4rem 1.3rem 1.15rem; border-radius: 20px; margin-bottom: 1rem;
            border: 1px solid rgba(94,234,212,0.28);
            background:
              radial-gradient(ellipse at 10% 0%, rgba(94,234,212,0.12), transparent 50%),
              linear-gradient(160deg, rgba(8,20,18,0.9), rgba(6,10,12,0.95));
            animation: codexRise 0.55s cubic-bezier(0.22,1,0.36,1) both;
          }
          .jaime-hero .k {
            font-family: ui-monospace, monospace; font-size: 0.62rem;
            letter-spacing: 0.22em; color: #5eead4; text-transform: uppercase;
            margin-bottom: 0.45rem;
          }
          .jaime-hero h1 {
            font-size: 1.55rem; font-weight: 700; letter-spacing: -0.03em;
            color: #ecfdf5; margin: 0 0 0.4rem;
          }
          .jaime-hero p { color: rgba(200,230,220,0.78); line-height: 1.55; margin: 0; font-size: 0.95rem; }
        </style>
        <div class="jaime-hero">
          <div class="k">Residual channel · Santos</div>
          <h1>Jaime Santos</h1>
          <p>
            The Division sold the name PIXEL. Residual still keeps Jaime.
            This channel does not require a keyboard sequence — only proof
            you found a way in (phrase, dossier, or coastal pass).
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
**File posture.** Natural carrier. Walked away from a leak that cooked the volunteers.  
Committees called that *success*. Floor staff called it worse.

**Eleven days.** Jaime and Riley shared a corridor. After residual reclassification, Jaime’s sessions showed elevated static on the glass — spectrum lines that only appear when someone is dying slowly enough to notice, or when someone refuses to forget a name.

**Last voluntary line on file.**  
*“Not you.”* — when asked who built the shell.
        """
    )
    b1, b2 = st.columns(2)
    with b1:
        if st.button("← Sealed note", use_container_width=True, key="jaime_to_note"):
            st.session_state.view = "note"
            st.rerun()
    with b2:
        if st.button("⌂ Home", use_container_width=True, key="jaime_to_home"):
            st.session_state.view = "home"
            st.rerun()
    st.stop()

# ===== DESIGN 1 WAYBAR + NAV (hidden in lab) =====
if st.session_state.view not in (
    "lab", "note", "voss_file", "lyrics_full", "callaghan_safe", "board",
    "nadir", "nadir_transition", "nadir_door", "jaime_residual",
    "chess", "call_meridium", "lore_archive", "drift",
):
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





# ===== SHORTS — vertical short-form feed (YouTube Shorts style) =====
SHORTS_CATALOG = [
    {"id": "sh_Bl0WZvAeDik", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "Bl0WZvAeDik", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_h2KFNdLqAiU", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "h2KFNdLqAiU", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_kh9OmFBg8qI", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "kh9OmFBg8qI", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_2_Z7FB3vfFg", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "2_Z7FB3vfFg", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_uPGBcVCrdg8", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "uPGBcVCrdg8", "shelf": "Science", "tags": ["science"]},
    {"id": "sh__1G8nrmBKeY", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "_1G8nrmBKeY", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_7F4pY8Td9QQ", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "7F4pY8Td9QQ", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_Xr2yp8JA9LU", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "Xr2yp8JA9LU", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_MVFd0qFB9TE", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "MVFd0qFB9TE", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_za_HO2E3JEU", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "za_HO2E3JEU", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_HVySQLuxLkI", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "HVySQLuxLkI", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_zP5uhMpH4mE", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "zP5uhMpH4mE", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_Bb0uDpvitoE", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "Bb0uDpvitoE", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_49NikeBCzWo", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "49NikeBCzWo", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_w2TLv30F6UU", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "w2TLv30F6UU", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_R8oiho_gKSo", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "R8oiho_gKSo", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_h1YeIE0vEIs", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "h1YeIE0vEIs", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_RmHcX5oVzvs", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "RmHcX5oVzvs", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_b8XVCsXyIZs", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "b8XVCsXyIZs", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_UKfnXd3x-rw", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "UKfnXd3x-rw", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_zQ2ZJuUJeyo", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "zQ2ZJuUJeyo", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_3HQkVfZ4DNY", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "3HQkVfZ4DNY", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_BU5HwNyE4mk", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "BU5HwNyE4mk", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_gGtuw7Rejtk", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "gGtuw7Rejtk", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_q6WlXhtVvkg", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "q6WlXhtVvkg", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_OgFf_J1CP0g", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "OgFf_J1CP0g", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_2GUah9xHVto", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "2GUah9xHVto", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_kP7l1agsTzQ", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "kP7l1agsTzQ", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_2_VB-oc_pmk", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "2_VB-oc_pmk", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_fkxoaD47-Vo", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "fkxoaD47-Vo", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_OW9Mq3wrEqY", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "OW9Mq3wrEqY", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_S7xvqDUPoJo", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "S7xvqDUPoJo", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_Bt3boxwRF84", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "Bt3boxwRF84", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_iRach9lpIlg", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "iRach9lpIlg", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_nMqWWO6p7-c", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "nMqWWO6p7-c", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_itSkBESLZeY", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "itSkBESLZeY", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_RxIsjweAAdE", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "RxIsjweAAdE", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_y2y8ME02lX4", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "y2y8ME02lX4", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_qtPPfM7Tz1o", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "qtPPfM7Tz1o", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_AUmHqD0lGHo", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "AUmHqD0lGHo", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_Xhl5TzKZbpw", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "Xhl5TzKZbpw", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_dquI8khH1Zk", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "dquI8khH1Zk", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_tWRyiCP17do", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "tWRyiCP17do", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_fF32B_sOVHA", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "fF32B_sOVHA", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_b_SZC8oIsBw", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "b_SZC8oIsBw", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_zXvygWE3Ess", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "zXvygWE3Ess", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_DJ_5_JS9_Rs", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "DJ_5_JS9_Rs", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_h830G5mkTF4", "title": "Veritasium Short", "creator": "Veritasium", "youtube_id": "h830G5mkTF4", "shelf": "Science", "tags": ["science"]},
    {"id": "sh_ufe55fG5zVA", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "ufe55fG5zVA", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_loFzNec3kS8", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "loFzNec3kS8", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_2qOya17le0A", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "2qOya17le0A", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_za2isHAgefY", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "za2isHAgefY", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_Avr5K6tX1x4", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "Avr5K6tX1x4", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_1_Qsx71NL7w", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "1_Qsx71NL7w", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_I21BSP_LgRg", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "I21BSP_LgRg", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_UrM6ugyzeC8", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "UrM6ugyzeC8", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_PNbgHdDQ1fc", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "PNbgHdDQ1fc", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_fLmdtn8w7fk", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "fLmdtn8w7fk", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_dyzzvenwOgc", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "dyzzvenwOgc", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_tFvmwsQgvwc", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "tFvmwsQgvwc", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_-UgtKlbzers", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "-UgtKlbzers", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_PspOovsehhM", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "PspOovsehhM", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_RzJb-oo8D9k", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "RzJb-oo8D9k", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_QbbYXZHwTdw", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "QbbYXZHwTdw", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_4HbYUB1J1io", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "4HbYUB1J1io", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_3Yqu30QHkro", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "3Yqu30QHkro", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_hqSL5V9yXBM", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "hqSL5V9yXBM", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_cdu6sOgI9Dc", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "cdu6sOgI9Dc", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_m8KIGvOcEEo", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "m8KIGvOcEEo", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_vPwGmFUAr88", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "vPwGmFUAr88", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_d4xzmMuJTWs", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "d4xzmMuJTWs", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_7MfvZuCXVMQ", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "7MfvZuCXVMQ", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_y-TQq6sQ4Z0", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "y-TQq6sQ4Z0", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh__Nr4mvdkEVw", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "_Nr4mvdkEVw", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_pd3r93I5DNw", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "pd3r93I5DNw", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_l5aVdFu9ZQI", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "l5aVdFu9ZQI", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_ti8ZdImveB0", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "ti8ZdImveB0", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_iYwufaWCZbQ", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "iYwufaWCZbQ", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_cDotce_yZAI", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "cDotce_yZAI", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_Qpv89g-861M", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "Qpv89g-861M", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_kZAbaAfkluc", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "kZAbaAfkluc", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_QaFTwJPKLuo", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "QaFTwJPKLuo", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_vDtqOjpknSU", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "vDtqOjpknSU", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_laSCmjoYQdM", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "laSCmjoYQdM", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_P1vOlK_Ccfk", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "P1vOlK_Ccfk", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_EupTKqL3f1E", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "EupTKqL3f1E", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_M7hX6117E6E", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "M7hX6117E6E", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_4DaETxhoAxg", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "4DaETxhoAxg", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_Oa3k7RLZCUE", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "Oa3k7RLZCUE", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_u11hmGy-eP8", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "u11hmGy-eP8", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_jIwsHATFc9M", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "jIwsHATFc9M", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_543gNct7rXc", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "543gNct7rXc", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_qUALUK3hXu0", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "qUALUK3hXu0", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_tgyZwxPHdgY", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "tgyZwxPHdgY", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_C4-uK6OTR8g", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "C4-uK6OTR8g", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_d9PKYi0l1oo", "title": "Vsauce Short", "creator": "Vsauce", "youtube_id": "d9PKYi0l1oo", "shelf": "Vsauce", "tags": ["vsauce"]},
    {"id": "sh_PKqBmM0gbEY", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "PKqBmM0gbEY", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_iDFpA1VtIXg", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "iDFpA1VtIXg", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_cr-Zb4yiBd4", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "cr-Zb4yiBd4", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_J7rDVfBbRhQ", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "J7rDVfBbRhQ", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_zmTiqcN2CsM", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "zmTiqcN2CsM", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_gkUXbdJCDoA", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "gkUXbdJCDoA", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh__nRY0-hGmhY", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "_nRY0-hGmhY", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_pc36k0tNIZY", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "pc36k0tNIZY", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_rSNiZgF52kc", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "rSNiZgF52kc", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_ANLw8Kit4UA", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "ANLw8Kit4UA", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_R7a7jO6d3HU", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "R7a7jO6d3HU", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_Qn6CsV7zKYE", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "Qn6CsV7zKYE", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_5ksnGA5Jan0", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "5ksnGA5Jan0", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_pPJnIdMD0ZM", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "pPJnIdMD0ZM", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_b8bMkLaaM4c", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "b8bMkLaaM4c", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_C1vQz-FuOBU", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "C1vQz-FuOBU", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_hZvMkFbWQNA", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "hZvMkFbWQNA", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_n6HK4F7wNK4", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "n6HK4F7wNK4", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_Py9eD_B0vt0", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "Py9eD_B0vt0", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_TZxOiJHUpyA", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "TZxOiJHUpyA", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_JLPnrSSWHhs", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "JLPnrSSWHhs", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_kk_6hXuGQX4", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "kk_6hXuGQX4", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_Sd5Pt-XbRsg", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "Sd5Pt-XbRsg", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_4tGRDpXlJvY", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "4tGRDpXlJvY", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_frsTCJwyM64", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "frsTCJwyM64", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_II5Fca0osD8", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "II5Fca0osD8", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_Tt2IHrB6WiQ", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "Tt2IHrB6WiQ", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_oYCBXsoBpt8", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "oYCBXsoBpt8", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_03FweLupDsg", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "03FweLupDsg", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_CW6T9BDiX_w", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "CW6T9BDiX_w", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_9LTX9PqoXBI", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "9LTX9PqoXBI", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_eXrn44hiFx8", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "eXrn44hiFx8", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_Bgvj0yQlEp4", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "Bgvj0yQlEp4", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_sxcOvRMcets", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "sxcOvRMcets", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_s5UqtL1Rh1U", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "s5UqtL1Rh1U", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_hXlTTbyP0ts", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "hXlTTbyP0ts", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_-VNCQeO6poo", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "-VNCQeO6poo", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_ERS8n62sLgo", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "ERS8n62sLgo", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_BvJ89J9YBW4", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "BvJ89J9YBW4", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_fB8xwMeUsTA", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "fB8xwMeUsTA", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_w_3xpGqlwpA", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "w_3xpGqlwpA", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_ktfF8u3ESrI", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "ktfF8u3ESrI", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_MgDKBoQ6MH4", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "MgDKBoQ6MH4", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_8Md7h2OhqIw", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "8Md7h2OhqIw", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_otyX97LLNWU", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "otyX97LLNWU", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_2TV6_6jmy8I", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "2TV6_6jmy8I", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_DE0tMImxybs", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "DE0tMImxybs", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_LmgtLifiDQU", "title": "ATHLEAN-X Short", "creator": "ATHLEAN-X", "youtube_id": "LmgtLifiDQU", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_82vgdGcQPDM", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "82vgdGcQPDM", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_goHCtsfhz0o", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "goHCtsfhz0o", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_YAFjtSV-Tlk", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "YAFjtSV-Tlk", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_wyQUqOyzNdg", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "wyQUqOyzNdg", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_2AbV6S1wzZ0", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "2AbV6S1wzZ0", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_a4j6oA0ebAg", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "a4j6oA0ebAg", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_wPY3nVM8jrE", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "wPY3nVM8jrE", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_Iccukd-Ohdw", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "Iccukd-Ohdw", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_3XO9gYV21QI", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "3XO9gYV21QI", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_-IAECmsHSts", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "-IAECmsHSts", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_1EAjYPQbFxM", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "1EAjYPQbFxM", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_4zdCtdtErcc", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "4zdCtdtErcc", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_TEsAwLlw-eI", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "TEsAwLlw-eI", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_veOR7ut3GHk", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "veOR7ut3GHk", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_Di2yhUTOWx0", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "Di2yhUTOWx0", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_Lnz2T1ikAI0", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "Lnz2T1ikAI0", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_j6qtl7z8fVo", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "j6qtl7z8fVo", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_qC4DxKPEiqU", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "qC4DxKPEiqU", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_jA6DTlrMRRA", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "jA6DTlrMRRA", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_BlYh9LmM0yY", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "BlYh9LmM0yY", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_RhdxdBmq_Rs", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "RhdxdBmq_Rs", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_Sw07ESwfqIg", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "Sw07ESwfqIg", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_ee5x_E1PaUs", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "ee5x_E1PaUs", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_bTVOaTrJVHc", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "bTVOaTrJVHc", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_q9hczWDkfpI", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "q9hczWDkfpI", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_Z0PLBXy23do", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "Z0PLBXy23do", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_uy5QdiCFXpI", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "uy5QdiCFXpI", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_sByk6lnFaLc", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "sByk6lnFaLc", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_BFI-SsHcwH4", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "BFI-SsHcwH4", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_XG2P8FDheHw", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "XG2P8FDheHw", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_97IElJ51p8s", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "97IElJ51p8s", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_TY6D9ROt2BU", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "TY6D9ROt2BU", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_tejkgipQx9I", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "tejkgipQx9I", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_nv0Vuw2Z1CI", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "nv0Vuw2Z1CI", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_F4iKVTP9IyA", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "F4iKVTP9IyA", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_YtVMwBJuya0", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "YtVMwBJuya0", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_SY77i4vUQk8", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "SY77i4vUQk8", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_rQksaYtwLsE", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "rQksaYtwLsE", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_ZYB53drPrvM", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "ZYB53drPrvM", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_IMiOxrj3ykQ", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "IMiOxrj3ykQ", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_RRPTfcKOy1Y", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "RRPTfcKOy1Y", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_IHH6d4hCRFU", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "IHH6d4hCRFU", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_CK8tfE3qGcw", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "CK8tfE3qGcw", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_466NhjDqvTQ", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "466NhjDqvTQ", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh__GzrmBv0-NY", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "_GzrmBv0-NY", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_rW8ibM2_6TI", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "rW8ibM2_6TI", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_GdAYu3mzIg0", "title": "Stronger By Science Short", "creator": "Stronger By Science", "youtube_id": "GdAYu3mzIg0", "shelf": "Working Out", "tags": ["working-out"]},
    {"id": "sh_4ENmZBnBNts", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "4ENmZBnBNts", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_T-DYwNR_e2o", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "T-DYwNR_e2o", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_xu3L32j8aeo", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "xu3L32j8aeo", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_YWqvhPhPwrI", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "YWqvhPhPwrI", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_Uf5bmb-AKKI", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "Uf5bmb-AKKI", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_oO1dNgIx4Q8", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "oO1dNgIx4Q8", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_qWlaSU7M-J4", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "qWlaSU7M-J4", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_YkYFaDzsod0", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "YkYFaDzsod0", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_mqumOsfkY9A", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "mqumOsfkY9A", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_DXtJ1ZCXAgQ", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "DXtJ1ZCXAgQ", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_EcliNSDg3ss", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "EcliNSDg3ss", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_ogbSXxGoV3o", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "ogbSXxGoV3o", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_3l8w4lwRfCA", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "3l8w4lwRfCA", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_BT-ThPEuxfM", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "BT-ThPEuxfM", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_8Sj37GMZTFU", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "8Sj37GMZTFU", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_5e_wLkPoGHw", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "5e_wLkPoGHw", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_t6vXOvtYKTY", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "t6vXOvtYKTY", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_oG9k2V-G15Q", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "oG9k2V-G15Q", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_QzaZfKzwhCw", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "QzaZfKzwhCw", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_J4hYWh7jDJ8", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "J4hYWh7jDJ8", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_UUZmvv3vGLM", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "UUZmvv3vGLM", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_PHUAVjFibns", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "PHUAVjFibns", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_RlNK0FXXbi8", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "RlNK0FXXbi8", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_72lrpwSkljs", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "72lrpwSkljs", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_7BwmQEFLgnI", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "7BwmQEFLgnI", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_E6aXkHJMC60", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "E6aXkHJMC60", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_Xa98byCqiAE", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "Xa98byCqiAE", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_XiI7yOiywI0", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "XiI7yOiywI0", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_kniEC_z9Xis", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "kniEC_z9Xis", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_NWVxL3fOYnc", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "NWVxL3fOYnc", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_StsKLhWSd8g", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "StsKLhWSd8g", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_gvOaNUBf5w0", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "gvOaNUBf5w0", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_747npZcbsn4", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "747npZcbsn4", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_dXQZ6X6sNIk", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "dXQZ6X6sNIk", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_sDE7wmTlYWA", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "sDE7wmTlYWA", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_Uet6Gt2Jh_M", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "Uet6Gt2Jh_M", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_0vTcMLLMKwI", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "0vTcMLLMKwI", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_dtOcfMoQHss", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "dtOcfMoQHss", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_AJnfS4UezaM", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "AJnfS4UezaM", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_P90ZISh-jqw", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "P90ZISh-jqw", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_6f6YlX-WFQ4", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "6f6YlX-WFQ4", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_VSpSthRBvK8", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "VSpSthRBvK8", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_djRLw04fMK8", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "djRLw04fMK8", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_f6s8FR3R0c0", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "f6s8FR3R0c0", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_4e-EKJwXP2I", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "4e-EKJwXP2I", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_PGQ5bSy-3BY", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "PGQ5bSy-3BY", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_428HE_zOlgk", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "428HE_zOlgk", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_trKWIJCGuo4", "title": "Rise Above Reality Short", "creator": "Rise Above Reality", "youtube_id": "trKWIJCGuo4", "shelf": "Rise Above Reality", "tags": ["rise-above-reality"]},
    {"id": "sh_ZgcDyJsoq3M", "title": "Science Short", "creator": "The Rest Is Science", "youtube_id": "ZgcDyJsoq3M", "shelf": "Rabbit Holes", "tags": ["rabbit-hole"]},
    {"id": "sh_dGaRmMJ04r0", "title": "Science Short", "creator": "The Rest Is Science", "youtube_id": "dGaRmMJ04r0", "shelf": "Rabbit Holes", "tags": ["rabbit-hole"]},
    {"id": "sh_2bzMVDQjGtg", "title": "Science Short", "creator": "The Rest Is Science", "youtube_id": "2bzMVDQjGtg", "shelf": "Rabbit Holes", "tags": ["rabbit-hole"]},
    {"id": "sh_TEmFGb-vUMA", "title": "Science Short", "creator": "The Rest Is Science", "youtube_id": "TEmFGb-vUMA", "shelf": "Rabbit Holes", "tags": ["rabbit-hole"]},
    {"id": "sh_g6ofyzaqVKU", "title": "Science Short", "creator": "The Rest Is Science", "youtube_id": "g6ofyzaqVKU", "shelf": "Rabbit Holes", "tags": ["rabbit-hole"]},
    {"id": "sh_BWabXmvTvZw", "title": "Science Short", "creator": "The Rest Is Science", "youtube_id": "BWabXmvTvZw", "shelf": "Rabbit Holes", "tags": ["rabbit-hole"]},
    {"id": "sh_xc9-9teM8yA", "title": "Science Short", "creator": "The Rest Is Science", "youtube_id": "xc9-9teM8yA", "shelf": "Rabbit Holes", "tags": ["rabbit-hole"]},
    {"id": "sh_c7tsWLhsFpw", "title": "Science Short", "creator": "The Rest Is Science", "youtube_id": "c7tsWLhsFpw", "shelf": "Rabbit Holes", "tags": ["rabbit-hole"]},
    {"id": "sh_-jgXHJx98i4", "title": "Science Short", "creator": "The Rest Is Science", "youtube_id": "-jgXHJx98i4", "shelf": "Rabbit Holes", "tags": ["rabbit-hole"]},
    {"id": "sh_urSzU0VFxu8", "title": "Science Short", "creator": "The Rest Is Science", "youtube_id": "urSzU0VFxu8", "shelf": "Rabbit Holes", "tags": ["rabbit-hole"]},
    {"id": "sh_L0nmxIQWefA", "title": "Science Short", "creator": "The Rest Is Science", "youtube_id": "L0nmxIQWefA", "shelf": "Rabbit Holes", "tags": ["rabbit-hole"]},
]


def _shorts_feed() -> list:
    """Built-in catalog + session custom shorts (pasted links)."""
    feed = list(SHORTS_CATALOG)
    custom = list(st.session_state.get("shorts_custom") or [])
    # customs first so new pastes show up immediately
    return custom + feed


def _shorts_liked() -> set:
    liked = st.session_state.get("shorts_liked")
    if not isinstance(liked, (set, list)):
        liked = []
        st.session_state.shorts_liked = liked
    return set(liked) if not isinstance(liked, set) else liked


def render_shorts_player(item: dict, height: int = 640) -> None:
    """Vertical 9:16 YouTube embed — Shorts-style frame."""
    import html as _html
    yid = (item.get("youtube_id") or _youtube_id_from_url(item.get("url") or "") or "").strip()
    title = item.get("title") or "Short"
    safe_title = _html.escape(title)
    if not yid:
        st.warning("Missing video id.")
        return
    embed_src = (
        f"https://www.youtube-nocookie.com/embed/{yid}"
        f"?rel=0&modestbranding=1&playsinline=1&loop=1&playlist={yid}"
    )
    # Tall vertical frame, centered
    st.components.v1.html(
        f"""
        <div style="display:flex;justify-content:center;width:100%;">
          <div style="
            position:relative;
            width:min(100%, 360px);
            aspect-ratio: 9 / 16;
            max-height: {height}px;
            border-radius: 18px;
            overflow: hidden;
            background: #0a0a0e;
            box-shadow: 0 16px 48px rgba(0,0,0,0.55), 0 0 0 1px rgba(196,167,231,0.18);
          ">
            <iframe
              src="{embed_src}"
              title="{safe_title}"
              style="position:absolute;inset:0;width:100%;height:100%;border:0;"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowfullscreen
              referrerpolicy="strict-origin-when-cross-origin"
            ></iframe>
          </div>
        </div>
        """,
        height=height + 24,
        scrolling=False,
    )


if st.session_state.view == "shorts":
    st.markdown(
        """
        <style>
          .shorts-hero {
            text-align: center; padding: 4px 0 10px;
          }
          .shorts-hero h1 {
            font-size: 1.35rem; font-weight: 650; letter-spacing: -0.03em; margin: 0 0 2px;
          }
          .shorts-hero p { margin: 0; opacity: 0.5; font-size: 0.82rem; }
          .shorts-meta {
            text-align: center; margin: 8px auto 4px; max-width: 360px;
          }
          .shorts-meta .t {
            font-size: 0.95rem; font-weight: 600; margin: 0;
          }
          .shorts-meta .c {
            font-size: 0.78rem; opacity: 0.55; margin: 2px 0 0;
          }
          .shorts-dots {
            text-align: center; letter-spacing: 0.15em;
            font-size: 0.7rem; opacity: 0.45; margin: 6px 0 2px;
          }
        </style>
        <div class="shorts-hero">
          <h1>Shorts</h1>
          <p>250 shorts · Gym · Science · Vsauce · Rise Above · more</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    feed = _shorts_feed()
    if not feed:
        st.info("No shorts yet — paste a YouTube or Shorts link below.")
    else:
        # clamp index
        idx = int(st.session_state.get("shorts_index") or 0)
        if idx < 0:
            idx = 0
        if idx >= len(feed):
            idx = len(feed) - 1
        st.session_state.shorts_index = idx
        item = feed[idx]

        render_shorts_player(item, height=620)

        title = item.get("title") or "Short"
        creator = item.get("creator") or item.get("note") or ""
        shelf = item.get("shelf") or ""
        sub = " · ".join(x for x in (creator, shelf) if x)
        st.markdown(
            f"""
            <div class="shorts-meta">
              <p class="t">{title}</p>
              <p class="c">{sub}</p>
            </div>
            <div class="shorts-dots">{idx + 1} / {len(feed)}</div>
            """,
            unsafe_allow_html=True,
        )

        # Controls: prev / like / next
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
        with c1:
            if st.button("↑ Prev", use_container_width=True, key="shorts_prev", disabled=(idx <= 0)):
                st.session_state.shorts_index = max(0, idx - 1)
                st.rerun()
        with c2:
            liked = _shorts_liked()
            sid = item.get("id") or item.get("youtube_id") or str(idx)
            is_liked = sid in liked
            label = "♥ Liked" if is_liked else "♡ Like"
            if st.button(label, use_container_width=True, key="shorts_like"):
                cur = list(st.session_state.get("shorts_liked") or [])
                if is_liked:
                    cur = [x for x in cur if x != sid]
                else:
                    cur.append(sid)
                st.session_state.shorts_liked = cur
                try:
                    save_user_data()
                except Exception:
                    pass
                st.rerun()
        with c3:
            if st.button("↓ Next", use_container_width=True, key="shorts_next", disabled=(idx >= len(feed) - 1)):
                st.session_state.shorts_index = min(len(feed) - 1, idx + 1)
                st.rerun()
        with c4:
            yid = item.get("youtube_id") or ""
            if yid:
                st.link_button("YT", f"https://www.youtube.com/shorts/{yid}", use_container_width=True)

        # Open on YouTube full watch as fallback
        yid = (item.get("youtube_id") or "").strip()
        if yid:
            st.caption(
                "If the embed is blocked by the channel, open on YouTube — "
                "some creators disable embedding."
            )

    with st.expander("Add a Short (YouTube / Shorts link)", expanded=False):
        custom = st.text_input(
            "Paste link",
            placeholder="https://www.youtube.com/shorts/… or watch?v=…",
            key="shorts_custom_url",
            label_visibility="collapsed",
        )
        title_in = st.text_input("Title (optional)", key="shorts_custom_title", placeholder="My short")
        if st.button("Add to feed", key="shorts_add_custom", use_container_width=True):
            yid = _youtube_id_from_url(custom)
            if not yid:
                st.warning("Could not read a YouTube id from that link.")
            else:
                entry = {
                    "id": f"custom::{yid}",
                    "title": (title_in or "").strip() or "Custom short",
                    "creator": "You",
                    "youtube_id": yid,
                    "tags": ["custom"],
                }
                cur = list(st.session_state.get("shorts_custom") or [])
                # dedupe by youtube id
                cur = [x for x in cur if x.get("youtube_id") != yid]
                cur.insert(0, entry)
                st.session_state.shorts_custom = cur[:40]
                st.session_state.shorts_index = 0
                try:
                    save_user_data()
                except Exception:
                    pass
                st.rerun()

    b1, b2 = st.columns(2)
    with b1:
        if st.button("← Home", key="shorts_home", use_container_width=True):
            st.session_state.view = "home"
            st.rerun()
    with b2:
        if st.button("🎬 Cinema", key="shorts_to_cinema", use_container_width=True):
            st.session_state.cinema_watching = None
            st.session_state.view = "cinema"
            st.rerun()

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
            st.session_state._nadir_music_on = False
            st.session_state._force_stop_nadir_audio = True
            try:
                stop_meridium_track("nadir")
                stop_meridium_track("door")
                stop_all_meridium_audio()
            except Exception:
                pass
            st.session_state.view = "library"
            st.session_state.nadir_active_file = None
            st.session_state.nadir_reader = None
            st.rerun()
    with sw2:
        if st.button("Switch to Meridium", key="nadir_to_meridium", use_container_width=True):
            st.session_state._nadir_music_on = False
            st.session_state._force_stop_nadir_audio = True
            try:
                stop_meridium_track("nadir")
                stop_meridium_track("door")
                stop_all_meridium_audio()
            except Exception:
                pass
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
            try:
                complete_quest("board_complete")
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

        # Residual dial — only after board key (Frankenstein path); bottom of shelf
        if st.session_state.get("archive_key") or st.session_state.get("lab_door_unlocked"):
            st.markdown("---")
            with st.expander("Residual dial", expanded=False):
                st.caption(
                    "A combination from the margin of Frankenstein. Four digits. Winter print. London."
                )
                with st.form(key="lib_nadir_dial_form", clear_on_submit=False):
                    code = st.text_input(
                        "Combination",
                        max_chars=8,
                        key="lib_nadir_dial_input",
                        placeholder="····",
                    )
                    submitted = st.form_submit_button("Turn dial", use_container_width=True)
                    if submitted:
                        if str(code or "").strip() == "1818":
                            st.session_state.view = "nadir_door"
                            st.rerun()
                        else:
                            st.error("The dial does not turn.")
        else:
            st.caption("")  # dial stays hidden until residual key is earned
    st.stop()

# ===== OWNER DESK (drae only) + shared chatroom =====
if st.session_state.view == "owner":
    if not is_owner(st.session_state.get("username") or ""):
        st.session_state.view = "home"
        st.rerun()

    st.markdown(
        """
        <style>
          /* Owner desk — local refinements on top of global glass */
          .own-toolbar {
            display: flex; gap: 0.5rem; flex-wrap: wrap;
            margin: 0.15rem 0 1rem;
          }
          .own-section-label {
            font-family: ui-monospace, monospace;
            font-size: 0.62rem;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            color: rgba(196,167,231,0.7);
            margin: 1.1rem 0 0.55rem;
          }
          .own-card {
            padding: 1rem 1.1rem;
            margin-bottom: 0.75rem;
          }
          .own-card h4 {
            margin: 0 0 0.35rem;
            font-size: 0.95rem;
            letter-spacing: -0.02em;
          }
          .own-card .hint {
            font-size: 0.82rem;
            opacity: 0.7;
            margin-bottom: 0.65rem;
            line-height: 1.45;
          }
          /* Cleaner metric row spacing */
          div[data-testid="stHorizontalBlock"]:has(.own-stat) {
            margin-bottom: 0.85rem;
          }
        </style>
        <div class="drae-desk">
          <div class="kicker">Creator channel · Owner only</div>
          <div class="title">Architect’s desk</div>
          <div class="line">
            Presence, broadcasts, residual keys, grants, chatroom, ARG levers —
            the shell answers from here.
          </div>
          <div class="sig">Meridium · Owner control · Not a committee</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top1, top2, top3, top4 = st.columns([1, 1, 1, 1])
    with top1:
        if st.button("← Home", key="owner_back_home", use_container_width=True):
            st.session_state.view = "home"
            st.rerun()
    with top2:
        if st.button("💬 Room", key="owner_jump_room", use_container_width=True):
            st.session_state.view = "owner_room"
            st.rerun()
    with top3:
        if st.button("Lab", key="owner_jump_lab", use_container_width=True):
            st.session_state.arg_unlocked = True
            st.session_state.view = "lab"
            st.rerun()
    with top4:
        if st.button("↻ Refresh", key="owner_refresh", use_container_width=True):
            st.rerun()

    # Live metrics
    try:
        _online = presence_online()
    except Exception:
        _online = []
    try:
        _fx = site_effects_load()
    except Exception:
        _fx = dict(_DEFAULT_SITE_EFFECTS)
    try:
        _grants = owner_grants_load()
    except Exception:
        _grants = {}
    try:
        _room = chatroom_load()
    except Exception:
        _room = {}
    _ann_on = bool(_fx.get("announce_enabled")) and bool(str(_fx.get("announce_text") or "").strip())
    _fx_on = sum(1 for k, v in _fx.items() if k not in ("announce_text", "announce_id", "announce_style", "force_theme", "announce_enabled") and v is True)
    if _fx.get("force_theme"):
        _fx_on += 1

    st.markdown('<div class="own-section-label">Live pulse</div>', unsafe_allow_html=True)
    s1, s2, s3, s4, s5 = st.columns(5)
    with s1:
        st.markdown(f'<div class="own-stat"><div class="n">{len(_online)}</div><div class="l">Online</div></div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div class="own-stat"><div class="n">{len((_room.get("members") or []))}</div><div class="l">Room</div></div>', unsafe_allow_html=True)
    with s3:
        st.markdown(f'<div class="own-stat"><div class="n">{len(_grants)}</div><div class="l">Grants</div></div>', unsafe_allow_html=True)
    with s4:
        st.markdown(f'<div class="own-stat"><div class="n">{_fx_on}</div><div class="l">Effects</div></div>', unsafe_allow_html=True)
    with s5:
        st.markdown(f'<div class="own-stat"><div class="n">{"ON" if _ann_on else "—"}</div><div class="l">Broadcast</div></div>', unsafe_allow_html=True)

    tab_dash, tab_live, tab_room, tab_fx, tab_ann, tab_grants, tab_arg, tab_bazaar, tab_tools = st.tabs(
        ["Dashboard", "Online", "Chatroom", "Site effects", "Broadcast", "Grants", "ARG", "Bazaar", "Tools"]
    )

    # ---------- DASHBOARD ----------
    with tab_dash:
        st.markdown('<div class="own-section-label">Command surface</div>', unsafe_allow_html=True)
        st.caption("Quick actions that hit the whole shell.")
        d1, d2, d3 = st.columns(3)
        with d1:
            if st.button("Publish quick alert", key="dash_alert", use_container_width=True):
                cur = dict(site_effects_load())
                cur["announce_enabled"] = True
                cur["announce_text"] = "Owner online. The residual channel is live."
                cur["announce_style"] = "alert"
                cur["announce_id"] = uuid.uuid4().hex[:10]
                site_effects_save(cur)
                st.success("Alert published.")
                st.rerun()
            if st.button("Clear broadcast", key="dash_clear_ann", use_container_width=True):
                cur = dict(site_effects_load())
                cur["announce_enabled"] = False
                cur["announce_text"] = ""
                cur["announce_id"] = ""
                site_effects_save(cur)
                st.success("Broadcast cleared.")
                st.rerun()
        with d2:
            if st.button("Aurora + neon ON", key="dash_pretty", use_container_width=True):
                cur = dict(site_effects_load())
                cur["aurora_shell"] = True
                cur["neon_buttons"] = True
                cur["soft_bloom"] = True
                site_effects_save(cur)
                st.success("Pretty mode on.")
                st.rerun()
            if st.button("Quiet mode ON", key="dash_quiet", use_container_width=True):
                cur = dict(site_effects_load())
                cur["quiet_mode"] = True
                site_effects_save(cur)
                st.success("Quiet mode on.")
                st.rerun()
        with d3:
            if st.button("Clear all visual FX", key="dash_clear_fx", use_container_width=True):
                cur = dict(_DEFAULT_SITE_EFFECTS)
                # keep announcement if any
                old = site_effects_load()
                cur["announce_enabled"] = old.get("announce_enabled", True)
                cur["announce_text"] = old.get("announce_text", "")
                cur["announce_style"] = old.get("announce_style", "violet")
                cur["announce_id"] = old.get("announce_id", "")
                site_effects_save(cur)
                st.success("Visual effects cleared (broadcast kept).")
                st.rerun()
            if st.button("Open chatroom →", key="dash_room", use_container_width=True, type="primary"):
                st.session_state.view = "owner_room"
                st.rerun()

        st.markdown("#### Jump")
        j1, j2, j3, j4, j5 = st.columns(5)
        jumps = [
            (j1, "Home", "home"),
            (j2, "Chat", "chat"),
            (j3, "Library", "library"),
            (j4, "Cinema", "cinema"),
            (j5, "Shorts", "shorts"),
        ]
        for col, label, view_name in jumps:
            with col:
                if st.button(label, key=f"own_jump_{view_name}", use_container_width=True):
                    if view_name == "library":
                        st.session_state.library_reading = None
                    if view_name == "cinema":
                        st.session_state.cinema_watching = None
                    if view_name == "shorts":
                        st.session_state.shorts_index = 0
                    st.session_state.view = view_name
                    st.rerun()

        st.markdown("#### Live snapshot")
        if _online:
            for row in _online[:12]:
                st.markdown(
                    f"· **{row.get('username') or '?'}** · `{row.get('view') or '?'}` · "
                    f"{row.get('age_sec', '?')}s · {row.get('theme') or '—'}"
                )
        else:
            st.caption("Only you on the line.")

    # ---------- ONLINE ----------
    with tab_live:
        online = presence_online()
        st.markdown(f"**{len(online)}** session(s) active")
        st.caption("Heartbeat on each page load · online if seen within ~75s")
        filter_q = st.text_input("Filter username", key="own_online_filter", placeholder="optional")
        if not online:
            st.info("No other sessions right now.")
        else:
            for row in online:
                u = row.get("username") or "?"
                if filter_q and filter_q.strip().lower() not in u.lower():
                    continue
                v = row.get("view") or "?"
                age = row.get("age_sec", "?")
                th = row.get("theme") or "—"
                title = row.get("title") or ""
                badge = " · owner" if row.get("is_owner") else ""
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(
                        f"**{u}**{badge}  \n"
                        f"<span style='opacity:0.75;font-size:0.85rem'>"
                        f"`{v}` · {age}s ago · {th}"
                        + (f" · {title}" if title else "")
                        + "</span>",
                        unsafe_allow_html=True,
                    )
                with c2:
                    if not row.get("is_owner"):
                        if st.button("Invite", key=f"own_inv_{row.get('session_id')}", use_container_width=True):
                            status = chatroom_invite(u)
                            if status == "invited":
                                st.success(f"Invite sent to **{u}**")
                            elif status == "already_pending":
                                st.info(f"**{u}** already pending.")
                            elif status == "already_member":
                                st.info(f"**{u}** already in room.")
                            st.rerun()
                with c3:
                    if not row.get("is_owner"):
                        if st.button("Gift", key=f"own_gift_{row.get('session_id')}", use_container_width=True):
                            st.session_state.owner_grant_user = u
                            st.info(f"Username filled for grants → **{u}** (open Grants tab).")

    # ---------- CHATROOM ----------
    with tab_room:
        me = st.session_state.get("username") or "drae"
        room = chatroom_ensure_owner(me)
        members = list(room.get("members") or [])
        pending = list(room.get("pending") or [])
        active = list(room.get("active") or [])
        st.markdown(f"**Members** ({len(members)})")
        st.caption(", ".join(members) if members else "—")
        if pending:
            st.markdown(f"**Pending** ({len(pending)})")
            st.caption(", ".join(pending))
        if active:
            st.markdown(f"**Active now** ({len(active)})")
            st.caption(", ".join(active))

        inv = st.text_input("Invite username", key="owner_room_invite", placeholder="exact name")
        r1, r2, r3 = st.columns(3)
        with r1:
            if st.button("Send invite", key="owner_room_add", use_container_width=True):
                if (inv or "").strip():
                    status = chatroom_invite(inv)
                    if status == "invited":
                        st.success(f"Invite sent to **{inv.strip()}**")
                    elif status == "already_pending":
                        st.info("Already pending.")
                    elif status == "already_member":
                        st.info("Already a member.")
                    st.rerun()
        with r2:
            if st.button("Open room →", key="owner_open_room", type="primary", use_container_width=True):
                st.session_state.view = "owner_room"
                st.rerun()
        with r3:
            if st.button("Clear messages", key="owner_room_clear_msgs", use_container_width=True):
                room = chatroom_load()
                room["messages"] = []
                try:
                    chatroom_save(room)
                    st.success("Chatroom messages cleared.")
                except Exception as e:
                    st.error(str(e))
                st.rerun()

        kick_name = st.text_input("Remove member", key="owner_kick_user", placeholder="username to remove")
        if st.button("Remove from room", key="owner_kick_btn"):
            kn = (kick_name or "").strip().lower()
            if not kn:
                st.error("Enter a username.")
            elif is_owner(kn):
                st.error("Cannot remove owner.")
            else:
                room = chatroom_load()
                room["members"] = [m for m in (room.get("members") or []) if (m or "").strip().lower() != kn]
                room["pending"] = [m for m in (room.get("pending") or []) if (m or "").strip().lower() != kn]
                room["active"] = [m for m in (room.get("active") or []) if (m or "").strip().lower() != kn]
                try:
                    chatroom_save(room)
                    st.success(f"Removed **{kn}**.")
                except Exception as e:
                    st.error(str(e))
                st.rerun()

        msgs = list(room.get("messages") or [])[-12:]
        if msgs:
            st.markdown("**Recent**")
            for m in msgs:
                st.markdown(f"**{m.get('user','?')}**: {m.get('text','')}")
        else:
            st.caption("No messages yet.")

    # ---------- SITE EFFECTS ----------
    with tab_fx:
        st.markdown('<div class="own-section-label">Reality dial</div>', unsafe_allow_html=True)
        st.caption("These rewrite Meridium for **everyone** signed in. Flip switches → Apply.")
        fx = site_effects_load()

        st.markdown("**Core atmosphere**")
        c1, c2, c3 = st.columns(3)
        with c1:
            rainbow = st.toggle("🌈 Rainbow chat", value=bool(fx.get("rainbow_chat")), key="fx_rainbow")
            aurora = st.toggle("🌌 Aurora shell", value=bool(fx.get("aurora_shell")), key="fx_aurora")
            neon = st.toggle("💜 Neon buttons", value=bool(fx.get("neon_buttons")), key="fx_neon")
            matrix = st.toggle("💚 Matrix rain", value=bool(fx.get("matrix_rain")), key="fx_matrix")
            scan = st.toggle("📺 CRT scanlines", value=bool(fx.get("scanlines")), key="fx_scan")
            static = st.toggle("📼 Residual static", value=bool(fx.get("residual_static")), key="fx_static")
            bloom = st.toggle("✨ Soft bloom", value=bool(fx.get("soft_bloom")), key="fx_bloom")
        with c2:
            quiet = st.toggle("🤫 Quiet mode", value=bool(fx.get("quiet_mode")), key="fx_quiet")
            heart = st.toggle("💗 Heart cursor", value=bool(fx.get("heart_cursor")), key="fx_heart")
            mark = st.toggle("♔ Creator watermark", value=bool(fx.get("creator_watermark")), key="fx_mark")
            glitch = st.toggle("🗯 Glitch titles", value=bool(fx.get("glitch_text")), key="fx_glitch")
            chromatic = st.toggle("🟣 Chromatic fringing", value=bool(fx.get("chromatic")), key="fx_chromatic")
            vignette = st.toggle("🌑 Heavy vignette", value=bool(fx.get("heavy_vignette")), key="fx_vignette")
            grain = st.toggle("🎞 Film grain", value=bool(fx.get("film_grain")), key="fx_grain")
        with c3:
            pulse_b = st.toggle("💓 Pulse borders", value=bool(fx.get("pulse_border")), key="fx_pulse_b")
            sparkle = st.toggle("✨ Sparkle cursor", value=bool(fx.get("sparkle_cursor")), key="fx_sparkle")
            retro = st.toggle("🖥 Retro terminal", value=bool(fx.get("retro_terminal")), key="fx_retro")
            blood = st.toggle("🩸 Blood moon", value=bool(fx.get("blood_moon")), key="fx_blood")
            ice = st.toggle("❄️ Ice crystal", value=bool(fx.get("ice_crystal")), key="fx_ice")
            gold = st.toggle("🥇 Gold foil titles", value=bool(fx.get("gold_foil")), key="fx_gold")
            vscan = st.toggle("📡 Vertical scan", value=bool(fx.get("vertical_scan")), key="fx_vscan")

        st.markdown("**Advanced**")
        a1, a2, a3 = st.columns(3)
        with a1:
            panel_p = st.toggle("📟 Panel pulse", value=bool(fx.get("panel_pulse")), key="fx_panel_p")
            deep = st.toggle("🎯 Deep focus", value=bool(fx.get("deep_focus")), key="fx_deep")
            hicon = st.toggle("⬛ High contrast", value=bool(fx.get("high_contrast")), key="fx_hicon")
        with a2:
            sepia = st.toggle("📜 Sepia residual", value=bool(fx.get("sepia_residual")), key="fx_sepia")
            mirror = st.toggle("🪞 Mirror world", value=bool(fx.get("mirror_world")), key="fx_mirror")
            slow_a = st.toggle("🌊 Slow aurora", value=bool(fx.get("slow_aurora")), key="fx_slow_a")
        with a3:
            ember = st.toggle("🔥 Ember glow", value=bool(fx.get("ember_glow")), key="fx_ember")
            grid = st.toggle("▦ Cyber grid", value=bool(fx.get("cyber_grid")), key="fx_grid")

        theme_opts = ["(off)"] + list(THEMES.keys()) + list(SECRET_THEMES.keys()) + (list(OWNER_THEMES.keys()) if is_owner(st.session_state.get("username") or "") else [])
        cur_force = fx.get("force_theme") or "(off)"
        if cur_force not in theme_opts:
            cur_force = "(off)"
        force_all = st.selectbox(
            "Force everyone's theme",
            theme_opts,
            index=theme_opts.index(cur_force),
            key="fx_force_theme",
        )

        a1, a2, a3 = st.columns(3)
        with a1:
            if st.button("Apply visual effects", key="fx_apply", type="primary", use_container_width=True):
                new_fx = dict(site_effects_load())
                new_fx.update({
                    "rainbow_chat": bool(rainbow),
                    "aurora_shell": bool(aurora),
                    "neon_buttons": bool(neon),
                    "matrix_rain": bool(matrix),
                    "scanlines": bool(scan),
                    "residual_static": bool(static),
                    "soft_bloom": bool(bloom),
                    "quiet_mode": bool(quiet),
                    "heart_cursor": bool(heart),
                    "creator_watermark": bool(mark),
                    "glitch_text": bool(glitch),
                    "chromatic": bool(chromatic),
                    "heavy_vignette": bool(vignette),
                    "film_grain": bool(grain),
                    "pulse_border": bool(pulse_b),
                    "sparkle_cursor": bool(sparkle),
                    "retro_terminal": bool(retro),
                    "blood_moon": bool(blood),
                    "ice_crystal": bool(ice),
                    "gold_foil": bool(gold),
                    "vertical_scan": bool(vscan),
                    "panel_pulse": bool(panel_p),
                    "deep_focus": bool(deep),
                    "high_contrast": bool(hicon),
                    "sepia_residual": bool(sepia),
                    "mirror_world": bool(mirror),
                    "slow_aurora": bool(slow_a),
                    "ember_glow": bool(ember),
                    "cyber_grid": bool(grid),
                    "force_theme": "" if force_all == "(off)" else force_all,
                })
                site_effects_save(new_fx)
                st.success("Visual effects updated for everyone.")
                st.rerun()
        with a2:
            if st.button("Clear visuals only", key="fx_clear_vis", use_container_width=True):
                new_fx = dict(site_effects_load())
                for k in (
                    "rainbow_chat", "aurora_shell", "neon_buttons", "matrix_rain",
                    "scanlines", "residual_static", "soft_bloom", "quiet_mode",
                    "heart_cursor", "glitch_text", "chromatic", "heavy_vignette",
                    "film_grain", "pulse_border", "sparkle_cursor", "retro_terminal",
                    "blood_moon", "ice_crystal", "gold_foil", "vertical_scan",
                    "panel_pulse", "deep_focus", "high_contrast", "sepia_residual",
                    "mirror_world", "slow_aurora", "ember_glow", "cyber_grid",
                ):
                    new_fx[k] = False
                new_fx["force_theme"] = ""
                site_effects_save(new_fx)
                st.success("Visuals cleared.")
                st.rerun()
        with a3:
            if st.button("Clear ALL effects", key="fx_clear", use_container_width=True):
                site_effects_save(dict(_DEFAULT_SITE_EFFECTS))
                st.session_state.pop("_active_announce_id", None)
                st.session_state.pop("_active_announce_text", None)
                st.session_state.pop("_dismissed_announce_id", None)
                st.success("All site effects cleared.")
                st.rerun()

        st.markdown(
            """
            <div style="margin-top:0.75rem;padding:0.75rem 0.9rem;border-radius:12px;
              border:1px solid rgba(196,167,231,0.25);background:rgba(20,12,32,0.5);
              font-size:0.82rem;color:rgba(220,210,240,0.75);line-height:1.45;">
              <b>Rainbow</b> paints chat · <b>Aurora</b> shifts the whole shell ·
              <b>Matrix / Scanlines / Static</b> are residual textures ·
              Use the <b>Broadcast</b> tab for site-wide announcements.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---------- BROADCAST ----------
    with tab_ann:
        st.markdown('<div class="own-section-label">Site-wide announcement</div>', unsafe_allow_html=True)
        st.caption("Sticky banner for every signed-in user. They can dismiss once per message id.")
        _fx = site_effects_load()
        _live = _announcement_active()
        if _live:
            st.success(f"Live: “{_live.get('text','')}” · style `{_live.get('style')}`")
        else:
            st.caption("No announcement is broadcasting.")

        _cur_on = bool(_fx.get("announce_enabled", True))
        _cur_text = str(_fx.get("announce_text") or "")
        _cur_style = _fx.get("announce_style") if _fx.get("announce_style") in ("violet", "alert", "residual", "soft") else "violet"

        with st.form("owner_announce_form"):
            ann_enabled = st.checkbox("Broadcast announcement", value=_cur_on)
            ann_text = st.text_area(
                "Message",
                value=_cur_text,
                placeholder="The residual door is open. Library dial: 1818.",
                height=100,
                max_chars=220,
            )
            ann_style = st.selectbox(
                "Style",
                ["violet", "alert", "residual", "soft"],
                index=["violet", "alert", "residual", "soft"].index(_cur_style),
            )
            presets = st.selectbox(
                "Insert preset",
                [
                    "(none)",
                    "Owner online. The residual channel is live.",
                    "Maintenance in a few minutes — save your chats.",
                    "New Shorts in the feed. Swipe the residual lane.",
                    "The residual door is open. Library dial: 1818.",
                ],
                key="ann_preset",
            )
            c_apply, c_off = st.columns(2)
            with c_apply:
                submitted = st.form_submit_button("Publish announcement", use_container_width=True, type="primary")
            with c_off:
                turn_off = st.form_submit_button("Turn off announcement", use_container_width=True)

        if submitted:
            new_text = str(ann_text or "").strip()[:220]
            if presets and presets != "(none)" and not new_text:
                new_text = presets[:220]
            cur = dict(site_effects_load())
            cur["announce_enabled"] = bool(ann_enabled)
            cur["announce_text"] = new_text
            cur["announce_style"] = str(ann_style or "violet")
            if new_text and ann_enabled:
                if new_text != str(_fx.get("announce_text") or "").strip() or not _fx.get("announce_id"):
                    cur["announce_id"] = uuid.uuid4().hex[:10]
                else:
                    cur["announce_id"] = _fx.get("announce_id") or uuid.uuid4().hex[:10]
            else:
                cur["announce_id"] = ""
            site_effects_save(cur)
            st.session_state.pop("_dismissed_announce_id", None)
            st.session_state.pop("_active_announce_id", None)
            st.session_state.pop("_active_announce_text", None)
            st.success("Announcement saved.")
            st.rerun()

        if turn_off:
            cur = dict(site_effects_load())
            cur["announce_enabled"] = False
            cur["announce_text"] = ""
            cur["announce_id"] = ""
            site_effects_save(cur)
            st.session_state.pop("_dismissed_announce_id", None)
            st.session_state.pop("_active_announce_id", None)
            st.session_state.pop("_active_announce_text", None)
            st.success("Announcement off.")
            st.rerun()

    # ---------- GRANTS ----------
    with tab_grants:
        st.markdown('<div class="own-section-label">Grants</div>', unsafe_allow_html=True)
        st.markdown("Gift themes, titles, or **Residuum** to any username.")
        target = st.text_input(
            "Username",
            key="owner_grant_user",
            placeholder="exact name",
            value=st.session_state.get("owner_grant_user") or "",
        )

        st.markdown("##### Residuum gift")
        st.caption("Queued until they next load Meridium · applied instantly if they are you / already online in this session.")
        rc1, rc2, rc3 = st.columns([2, 1, 1])
        with rc1:
            gift_amount = st.number_input(
                "Amount (◆)",
                min_value=-10000,
                max_value=10000,
                value=25,
                step=5,
                key="owner_residuum_amount",
            )
        with rc2:
            if st.button("Gift Residuum", key="owner_residuum_gift", type="primary", use_container_width=True):
                tname = (target or "").strip().lower()
                if not tname:
                    st.error("Enter a username.")
                else:
                    status = owner_gift_residuum(tname, int(gift_amount))
                    if status == "ok":
                        sign = "+" if int(gift_amount) >= 0 else ""
                        st.success(f"Queued **{sign}{int(gift_amount)} ◆** for **{tname}**.")
                        st.rerun()
                    elif status == "zero":
                        st.info("Amount is zero — nothing queued.")
                    else:
                        st.error("Could not gift Residuum.")
        with rc3:
            if st.button("Clear pending ◆", key="owner_residuum_clear", use_container_width=True):
                tname = (target or "").strip().lower()
                if not tname:
                    st.error("Enter a username.")
                else:
                    grants = owner_grants_load()
                    entry = dict(grants.get(tname) or {})
                    if "residuum_pending" in entry:
                        entry.pop("residuum_pending", None)
                        if not entry.get("themes") and not entry.get("force_theme") and not entry.get("title"):
                            grants.pop(tname, None)
                        else:
                            grants[tname] = entry
                        owner_grants_save(grants)
                        st.success(f"Cleared pending Residuum for **{tname}**.")
                    else:
                        st.info("No pending Residuum for that user.")
                    st.rerun()

        st.markdown("##### Theme & title")
        all_themes = list(THEMES.keys()) + list(SECRET_THEMES.keys()) + list(OWNER_THEMES.keys())
        grant_theme = st.selectbox("Unlock theme", ["(none)"] + all_themes, key="owner_grant_theme")
        force_theme = st.checkbox("Force their active theme to this", key="owner_force_theme")
        grant_title = st.text_input("Custom title / badge", key="owner_grant_title", placeholder="e.g. Residual Witness")
        clear_title = st.checkbox("Remove title / badge from user", key="owner_clear_title")
        g1, g2, g3 = st.columns(3)
        with g1:
            if st.button("Apply grant", key="owner_grant_btn", type="primary", use_container_width=True):
                tname = (target or "").strip().lower()
                if not tname:
                    st.error("Enter a username.")
                else:
                    grants = owner_grants_load()
                    entry = dict(grants.get(tname) or {})
                    themes = list(entry.get("themes") or [])
                    if grant_theme and grant_theme != "(none)":
                        if grant_theme not in themes:
                            themes.append(grant_theme)
                        entry["themes"] = themes
                        if force_theme:
                            entry["force_theme"] = grant_theme
                    if clear_title:
                        entry.pop("title", None)
                    elif (grant_title or "").strip():
                        entry["title"] = grant_title.strip()[:48]
                    if not entry.get("themes") and not entry.get("force_theme") and not entry.get("title"):
                        grants.pop(tname, None)
                    else:
                        grants[tname] = entry
                    owner_grants_save(grants)
                    if tname == (st.session_state.get("username") or "").strip().lower():
                        apply_owner_grants_for_user(tname)
                        if clear_title:
                            st.session_state.owner_title = ""
                        save_user_data()
                    st.success(f"Grant saved for **{tname}**.")
                    st.rerun()
        with g2:
            if st.button("Remove title only", key="owner_title_remove", use_container_width=True):
                tname = (target or "").strip().lower()
                if not tname:
                    st.error("Enter a username.")
                else:
                    grants = owner_grants_load()
                    entry = dict(grants.get(tname) or {})
                    if "title" in entry:
                        entry.pop("title", None)
                        if not entry.get("themes") and not entry.get("force_theme"):
                            grants.pop(tname, None)
                        else:
                            grants[tname] = entry
                        owner_grants_save(grants)
                        if tname == (st.session_state.get("username") or "").strip().lower():
                            st.session_state.owner_title = ""
                            try:
                                save_user_data()
                            except Exception:
                                pass
                        st.success(f"Title removed for **{tname}**.")
                    else:
                        st.info("No title on file.")
                    st.rerun()
        with g3:
            if st.button("Revoke all for user", key="owner_grant_revoke", use_container_width=True):
                tname = (target or "").strip().lower()
                if not tname:
                    st.error("Enter a username.")
                else:
                    grants = owner_grants_load()
                    if tname in grants:
                        del grants[tname]
                        owner_grants_save(grants)
                        st.success(f"Revoked grants for **{tname}**.")
                    else:
                        st.info("No grants on file for that name.")
                    st.rerun()

        st.markdown("#### Existing grants")
        grants = owner_grants_load()
        if not grants:
            st.caption("None yet.")
        else:
            for uname, entry in sorted(grants.items()):
                themes = entry.get("themes") or []
                title = entry.get("title") or ""
                force = entry.get("force_theme") or ""
                try:
                    pending_r = int(entry.get("residuum_pending") or 0)
                except Exception:
                    pending_r = 0
                st.markdown(
                    f"**{uname}** · themes: `{', '.join(themes) if themes else '—'}`"
                    + (f" · title: *{title}*" if title else "")
                    + (f" · force: `{force}`" if force else "")
                    + (f" · pending ◆: `{pending_r}`" if pending_r else "")
                )

    # ---------- ARG ----------
    with tab_arg:
        st.markdown('<div class="own-section-label">Residual controls · this session</div>', unsafe_allow_html=True)
        st.caption("Unlock ARG surfaces on this account for testing, or reset local residual flags.")
        a1, a2 = st.columns(2)
        with a1:
            if st.button("Unlock Lab (session)", key="arg_unlock_lab", use_container_width=True):
                st.session_state.arg_unlocked = True
                st.session_state.lab_door_unlocked = True
                try:
                    save_user_data()
                except Exception:
                    pass
                st.success("Lab unlocked for your account.")
                st.rerun()
            if st.button("Unlock Board + Safe", key="arg_unlock_board", use_container_width=True):
                st.session_state.callaghan_safe_unlocked = True
                st.session_state.board_unlocked = True
                try:
                    save_user_data()
                except Exception:
                    pass
                st.success("Board + residual safe unlocked.")
                st.rerun()
            if st.button("Unlock Voss file", key="arg_unlock_voss", use_container_width=True):
                st.session_state.voss_file_unlocked = True
                try:
                    save_user_data()
                except Exception:
                    pass
                st.success("Voss file unlocked.")
                st.rerun()
        with a2:
            if st.button("Grant archive key", key="arg_archive_key", use_container_width=True):
                st.session_state.archive_key = True
                try:
                    save_user_data()
                except Exception:
                    pass
                st.success("Archive key set.")
                st.rerun()
            if st.button("Open Lab now", key="arg_go_lab", use_container_width=True):
                st.session_state.arg_unlocked = True
                st.session_state.view = "lab"
                st.rerun()
            if st.button("Open Board now", key="arg_go_board", use_container_width=True):
                st.session_state.board_unlocked = True
                st.session_state.view = "board"
                st.rerun()

        st.markdown("#### Status")
        st.code(
            "\n".join([
                f"arg_unlocked: {bool(st.session_state.get('arg_unlocked'))}",
                f"lab_door_unlocked: {bool(st.session_state.get('lab_door_unlocked'))}",
                f"callaghan_safe_unlocked: {bool(st.session_state.get('callaghan_safe_unlocked'))}",
                f"board_unlocked: {bool(st.session_state.get('board_unlocked'))}",
                f"voss_file_unlocked: {bool(st.session_state.get('voss_file_unlocked'))}",
                f"archive_key: {bool(st.session_state.get('archive_key'))}",
                f"glitches_found: {len(st.session_state.get('glitches_found') or [])}",
            ]),
            language="text",
        )

    # ---------- BAZAAR (owner full access) ----------
    with tab_bazaar:
        st.markdown('<div class="own-section-label">Drift Counter · Shady Bazaar</div>', unsafe_allow_html=True)
        st.caption("Owner shortcut — same economy surface as Menu → Drift, including the locked Bazaar.")
        o1, o2, o3 = st.columns(3)
        with o1:
            if st.button("Unlock Bazaar (session)", key="owner_unlock_bazaar", use_container_width=True):
                st.session_state.bazaar_unlocked = True
                st.session_state.black_key_owned = True
                try:
                    complete_quest("shadow_contact", silent=True)
                    complete_quest("black_key", silent=True)
                    complete_quest("bazaar_threshold", silent=True)
                except Exception:
                    pass
                try:
                    save_user_data()
                except Exception:
                    pass
                st.success("Bazaar unlocked for your account.")
                st.rerun()
        with o2:
            if st.button("Open full Drift page", key="owner_goto_drift", use_container_width=True):
                st.session_state.view = "drift"
                st.rerun()
        with o3:
            if st.button("Open Lore Archive", key="owner_goto_lore", use_container_width=True):
                st.session_state.view = "lore_archive"
                st.rerun()
        try:
            render_bazaar_tab()
        except Exception as _obaz:
            st.warning(f"Bazaar render issue: {_obaz}")

    # ---------- TOOLS ----------
    with tab_tools:
        st.markdown('<div class="own-section-label">System tools</div>', unsafe_allow_html=True)

        st.markdown("##### Shell command")
        st.caption("Site-wide controls that affect every signed-in guest. Owner always bypasses maintenance.")
        _sfx = site_effects_load()
        with st.form("owner_shell_command"):
            sc1, sc2 = st.columns(2)
            with sc1:
                maint = st.checkbox("Maintenance mode", value=bool(_sfx.get("maintenance_mode")), key="sc_maint")
                guest_lock = st.checkbox("Lock guest chat", value=bool(_sfx.get("guest_chat_lock")), key="sc_gchat")
                econ_pause = st.checkbox("Pause Residuum economy", value=bool(_sfx.get("economy_paused")), key="sc_econ")
                hide_drift = st.checkbox("Hide Drift Counter", value=bool(_sfx.get("hide_drift_counter")), key="sc_drift")
            with sc2:
                force_home = st.checkbox("Force guests to Home only", value=bool(_sfx.get("force_home_only")), key="sc_fhome")
            maint_msg = st.text_area(
                "Maintenance message",
                value=str(_sfx.get("maintenance_message") or ""),
                max_chars=280,
                key="sc_maint_msg",
            )
            global_toast = st.text_input(
                "Global toast (shown once per user)",
                value=str(_sfx.get("global_toast") or ""),
                max_chars=180,
                key="sc_toast",
            )
            owner_motd = st.text_input(
                "Owner MOTD (only you see this)",
                value=str(_sfx.get("owner_motd") or ""),
                max_chars=160,
                key="sc_motd",
            )
            saved_shell = st.form_submit_button("Save shell command", type="primary", use_container_width=True)
        if saved_shell:
            cur = dict(site_effects_load())
            cur["maintenance_mode"] = bool(maint)
            cur["maintenance_message"] = str(maint_msg or "").strip()[:280]
            cur["guest_chat_lock"] = bool(guest_lock)
            cur["economy_paused"] = bool(econ_pause)
            cur["hide_drift_counter"] = bool(hide_drift)
            cur["force_home_only"] = bool(force_home)
            cur["global_toast"] = str(global_toast or "").strip()[:180]
            cur["owner_motd"] = str(owner_motd or "").strip()[:160]
            site_effects_save(cur)
            st.success("Shell command saved — live for all sessions on next load.")
            st.rerun()

        qk1, qk2, qk3 = st.columns(3)
        with qk1:
            if st.button("All clear (open shell)", key="sc_allclear", use_container_width=True):
                cur = dict(site_effects_load())
                cur["maintenance_mode"] = False
                cur["guest_chat_lock"] = False
                cur["force_home_only"] = False
                cur["economy_paused"] = False
                cur["global_toast"] = ""
                site_effects_save(cur)
                st.success("Shell fully open.")
                st.rerun()
        with qk2:
            if st.button("Flash maintenance 5m note", key="sc_flash_maint", use_container_width=True):
                cur = dict(site_effects_load())
                cur["maintenance_mode"] = True
                cur["maintenance_message"] = "Brief residual maintenance — back in a few minutes."
                site_effects_save(cur)
                st.success("Maintenance on.")
                st.rerun()
        with qk3:
            if st.button("Gift 50◆ to yourself", key="sc_self_residuum", use_container_width=True):
                me = (st.session_state.get("username") or "").strip().lower()
                if me:
                    owner_gift_residuum(me, 50)
                    st.success("+50 Residuum queued for you.")
                    st.rerun()

        st.markdown("---")
        t1, t2 = st.columns(2)
        with t1:
            st.markdown("**Presence**")
            st.caption(f"{len(presence_online())} online · grants file · site effects file")
            if st.button("Reload site effects from disk", key="tools_reload_fx", use_container_width=True):
                st.success("Next read will use disk state.")
                st.rerun()
            if st.button("Reset your dismiss flags", key="tools_reset_dismiss", use_container_width=True):
                st.session_state.pop("_dismissed_announce_id", None)
                st.session_state.pop("_active_announce_id", None)
                st.success("Dismiss flags cleared for this session.")
                st.rerun()
        with t2:
            st.markdown("**Exports (read-only)**")
            with st.expander("Site effects JSON"):
                st.code(json.dumps(site_effects_load(), indent=2), language="json")
            with st.expander("Grants JSON"):
                st.code(json.dumps(owner_grants_load(), indent=2), language="json")
            with st.expander("Chatroom meta"):
                room = chatroom_load()
                meta = {
                    "members": room.get("members"),
                    "pending": room.get("pending"),
                    "active": room.get("active"),
                    "message_count": len(room.get("messages") or []),
                }
                st.code(json.dumps(meta, indent=2), language="json")

        st.markdown("#### Danger zone")
        st.caption("Destructive actions — cannot be undone from the UI.")
        if st.checkbox("I understand these wipe shared state", key="tools_danger_ack"):
            if st.button("Wipe chatroom (members + messages)", key="tools_wipe_room"):
                try:
                    chatroom_save({
                        "members": [st.session_state.get("username") or "drae"],
                        "pending": [],
                        "active": [],
                        "messages": [],
                    })
                    st.success("Chatroom wiped.")
                except Exception as e:
                    st.error(str(e))
                st.rerun()
            if st.button("Wipe all grants", key="tools_wipe_grants"):
                owner_grants_save({})
                st.success("All grants wiped.")
                st.rerun()
            if st.button("Factory-reset site effects", key="tools_wipe_fx"):
                site_effects_save(dict(_DEFAULT_SITE_EFFECTS))
                st.success("Site effects factory reset.")
                st.rerun()

    st.stop()


if st.session_state.view == "owner_room":
    me = (st.session_state.get("username") or "").strip()
    if not chatroom_user_allowed(me):
        st.warning("You are not in the owner chatroom.")
        if st.button("← Home", key="room_denied_home"):
            st.session_state.view = "home"
            st.rerun()
        st.stop()

    try:
        chatroom_enter_active(me)
    except Exception:
        pass

    room = chatroom_load()
    active = room.get("active") or []
    members = room.get("members") or []
    active_label = ", ".join(active) if active else "—"

    st.markdown(
        f"""
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Syne:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
          .room-shell {{
            max-width: 720px; margin: 0 auto 0.5rem;
          }}
          .room-hero {{
            position: relative;
            padding: 1.5rem 1.45rem 1.25rem;
            border-radius: 24px;
            overflow: hidden;
            border: 1px solid rgba(167,139,250,0.4);
            background:
              radial-gradient(ellipse at 0% 0%, rgba(167,139,250,0.25), transparent 52%),
              radial-gradient(ellipse at 100% 100%, rgba(244,114,182,0.16), transparent 48%),
              linear-gradient(145deg, rgba(16,10,26,0.84) 0%, rgba(8,6,16,0.9) 100%);
            box-shadow:
              0 1px 0 rgba(255,255,255,0.08) inset,
              0 26px 60px rgba(0,0,0,0.45);
            backdrop-filter: blur(28px) saturate(1.45);
            -webkit-backdrop-filter: blur(28px) saturate(1.45);
            animation: codexRise 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
          }}
          .room-hero::after {{
            content: "";
            position: absolute;
            left: 0; right: 0; top: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, #a78bfa, #f472b6, transparent);
            animation: codexScanX 4.5s ease-in-out infinite;
          }}
          .room-hero::before {{
            content: "";
            position: absolute; inset: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.04), transparent);
            animation: roomShimmer 6s ease-in-out infinite;
            pointer-events: none;
          }}
          @keyframes roomShimmer {{
            0%,100% {{ opacity: 0.3; transform: translateX(-30%); }}
            50% {{ opacity: 0.7; transform: translateX(30%); }}
          }}
          .room-kicker {{
            font-family: ui-monospace, monospace;
            font-size: 0.65rem;
            letter-spacing: 0.28em;
            color: #c4b5fd;
            margin-bottom: 0.45rem;
            text-transform: uppercase;
          }}
          .room-title {{
            font-family: Syne, system-ui, sans-serif;
            font-weight: 700;
            font-size: clamp(1.55rem, 4vw, 2rem);
            color: #faf5ff;
            letter-spacing: -0.02em;
            margin: 0 0 0.35rem;
            line-height: 1.15;
          }}
          .room-sub {{
            font-family: "IBM Plex Sans", system-ui, sans-serif;
            font-size: 0.88rem;
            color: rgba(220,210,245,0.72);
            line-height: 1.45;
          }}
          .room-live-pill {{
            display: inline-flex; align-items: center; gap: 0.4rem;
            margin-top: 0.75rem;
            padding: 0.28rem 0.7rem;
            border-radius: 999px;
            background: rgba(34,197,94,0.12);
            border: 1px solid rgba(34,197,94,0.35);
            color: #86efac;
            font-family: ui-monospace, monospace;
            font-size: 0.68rem;
            letter-spacing: 0.08em;
          }}
          .room-live-dot {{
            width: 7px; height: 7px; border-radius: 50%;
            background: #22c55e;
            box-shadow: 0 0 10px #22c55e;
            animation: livePulse 1.4s ease-in-out infinite;
          }}
          @keyframes livePulse {{
            0%,100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.45; transform: scale(0.85); }}
          }}
          .room-msg {{
            margin: 0.55rem 0;
            padding: 0.75rem 0.95rem;
            border-radius: 16px;
            font-family: "IBM Plex Sans", system-ui, sans-serif;
            line-height: 1.45;
            max-width: 92%;
          }}
          .room-msg.mine {{
            margin-left: auto;
            background: linear-gradient(135deg, rgba(167,139,250,0.32), rgba(124,58,237,0.22));
            border: 1px solid rgba(196,181,253,0.38);
            color: #f5f3ff;
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.18);
          }}
          .room-msg.theirs {{
            margin-right: auto;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.12);
            color: #e8e4f5;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
          }}
          .room-msg.owner {{
            background: linear-gradient(135deg, rgba(244,114,182,0.2), rgba(167,139,250,0.18));
            border: 1px solid rgba(244,114,182,0.32);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
          }}
          .room-msg .who {{
            font-size: 0.72rem;
            letter-spacing: 0.04em;
            opacity: 0.7;
            margin-bottom: 0.2rem;
            font-weight: 600;
          }}
          .room-msg .body {{ white-space: pre-wrap; word-break: break-word; }}
          .room-empty {{
            text-align: center; padding: 2rem 1rem;
            color: rgba(200,190,230,0.55);
            font-family: Syne, system-ui, sans-serif;
            font-size: 0.95rem;
          }}
        </style>
        <div class="room-shell">
          <div class="room-hero">
            <div class="room-kicker">Codex channel · ephemeral</div>
            <div class="room-title">Signal desk</div>
            <div class="room-sub">
              Live · moderated · messages vanish when everyone leaves
            </div>
            <div class="room-live-pill">
              <span class="room-live-dot"></span>
              LIVE · {active_label}
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Leave room", key="room_leave", use_container_width=True):
            try:
                chatroom_leave(me)
            except Exception:
                pass
            st.session_state.view = "home"
            st.rerun()
    with c2:
        if is_owner(me):
            if st.button("Owner desk", key="room_to_owner", use_container_width=True):
                st.session_state.view = "owner"
                st.rerun()
        else:
            st.caption("")
    with c3:
        if st.button("↻", key="room_refresh", use_container_width=True, help="Refresh"):
            st.rerun()

    def _render_room_messages():
        r = chatroom_load()
        msgs = list(r.get("messages") or [])[-50:]
        me_l = (me or "").strip().lower()
        if not msgs:
            st.markdown(
                '<div class="room-empty">Quiet channel — say something.</div>',
                unsafe_allow_html=True,
            )
            return
        import html as _html
        for m in msgs:
            who = m.get("user") or "?"
            text = _html.escape(m.get("text") or "")
            ts = (m.get("ts") or "")[11:16]
            who_l = who.strip().lower()
            if who_l == me_l:
                cls = "room-msg mine"
            elif is_owner(who):
                cls = "room-msg theirs owner"
            else:
                cls = "room-msg theirs"
            st.markdown(
                f'<div class="{cls}"><div class="who">{_html.escape(who)} · {ts}</div>'
                f'<div class="body">{text}</div></div>',
                unsafe_allow_html=True,
            )

    try:
        from datetime import timedelta as _td

        @st.fragment(run_every=_td(seconds=2))
        def _live_room_feed():
            try:
                chatroom_enter_active(me)
            except Exception:
                pass
            _render_room_messages()

        _live_room_feed()
    except Exception:
        _render_room_messages()
        st.components.v1.html(
            """
            <script>
            (function(){
              try {
                if (window.__mer_room_timer) return;
                window.__mer_room_timer = setTimeout(function(){
                  try {
                    var doc = window.parent.document;
                    var btns = doc.querySelectorAll('button');
                    for (var i=0;i<btns.length;i++){
                      var t = (btns[i].innerText || '').trim();
                      if (t === '↻') { btns[i].click(); break; }
                    }
                  } catch(e){}
                }, 3000);
              } catch(e){}
            })();
            </script>
            """,
            height=0,
        )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    with st.form(key="owner_room_send", clear_on_submit=True):
        msg = st.text_input("Message", key="owner_room_msg", placeholder="Message the desk…", label_visibility="collapsed")
        sent = st.form_submit_button("Send", use_container_width=True, type="primary")
        if sent:
            ok, cleaned = moderate_chat_message(msg)
            if not ok:
                if cleaned == "blocked":
                    st.error("Message blocked by Meridium safety filters.")
                else:
                    st.error("Empty message.")
            else:
                chatroom_post(me, cleaned)
                st.rerun()
    st.caption("Ephemeral — when you and Drae both leave, the transcript is wiped.")
    st.stop()


# HOME — bookmark rail + calm main panel

# Retired views
if st.session_state.get("view") in ("character_ai", "web"):
    st.session_state.view = "home"


# ===== LORE ARCHIVE =====
if st.session_state.view == "lore_archive":
    if st.button("← Back", key="lore_arch_back"):
        st.session_state.view = "drift"
        st.rerun()
    st.markdown(
        """
        <div class="panel">
          <div class="panel-label">Residual ledger</div>
          <div class="hero" style="font-size:1.45rem;">Lore Archive</div>
          <div class="sub">Everything you bought from the Drift Counter and the Bazaar — readable, permanent, yours.</div>
          <div class="ridge"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _ensure_economy()
    # Auto-grant basic lore if related flags/items owned
    owned_lore = list(st.session_state.lore_owned or [])
    inv = set(st.session_state.inventory or [])
    if ("lore_santos" in inv or st.session_state.get("jaime_dossier_unlocked")) and "santos_dossier_basic" not in owned_lore:
        owned_lore.append("santos_dossier_basic")
    if ("lore_callaghan_margin" in inv or st.session_state.get("callaghan_margin_owned")) and "callaghan_margin_note" not in owned_lore:
        owned_lore.append("callaghan_margin_note")
    st.session_state.lore_owned = owned_lore

    if not owned_lore:
        st.info("No lore fragments yet. Acquire dossiers at the Drift Counter or contracts at the Bazaar.")
    else:
        # Group by subject
        by_subj = {}
        for lid in owned_lore:
            entry = LORE_TEXTS.get(lid)
            if not entry:
                continue
            subj = entry.get("subject") or "Unknown"
            by_subj.setdefault(subj, []).append((lid, entry))
        for subj, items in sorted(by_subj.items()):
            st.markdown(f"#### {subj}")
            for lid, entry in items:
                with st.expander(f"{entry.get('title', lid)} · {entry.get('source', '')}", expanded=False):
                    st.markdown(entry.get("body", "_No text._"))
    st.stop()


# ===== CALL MERIDIUM (voice channel) =====
if st.session_state.view == "call_meridium":
    # Phone-call state machine: idle → ringing → connected → ended
    if "call_phase" not in st.session_state:
        st.session_state.call_phase = "idle"
    if "call_history" not in st.session_state:
        st.session_state.call_history = []
    if "call_started_at" not in st.session_state:
        st.session_state.call_started_at = None
    if "call_muted" not in st.session_state:
        st.session_state.call_muted = False

    phase = st.session_state.call_phase
    warm = bool(st.session_state.get("feat_voice_warm"))
    uname = st.session_state.get("username") or "you"

    # ---- IDLE: dial screen ----
    if phase == "idle":
        st.markdown(
            """
            <style>
              .call-dial {
                max-width: 360px; margin: 2rem auto; text-align: center;
                padding: 2rem 1.5rem 1.5rem; border-radius: 28px;
                border: 1px solid rgba(167,139,250,0.35);
                background:
                  radial-gradient(ellipse at 50% 0%, rgba(167,139,250,0.25), transparent 60%),
                  linear-gradient(165deg, rgba(18,12,32,0.96), rgba(8,6,16,0.98));
                box-shadow: 0 28px 70px rgba(0,0,0,0.45);
              }
              .call-avatar {
                width: 110px; height: 110px; margin: 0 auto 1.1rem;
                border-radius: 50%;
                background: radial-gradient(circle at 35% 30%, #c4a7e7, #7c3aed 55%, #1e1030 100%);
                box-shadow: 0 0 40px rgba(167,139,250,0.45), 0 0 80px rgba(124,58,237,0.2);
                display: flex; align-items: center; justify-content: center;
                font-size: 2.4rem; color: #faf5ff; font-weight: 700;
                animation: callPulse 2.8s ease-in-out infinite;
              }
              @keyframes callPulse {
                0%,100% { transform: scale(1); box-shadow: 0 0 40px rgba(167,139,250,0.4); }
                50% { transform: scale(1.04); box-shadow: 0 0 56px rgba(167,139,250,0.6); }
              }
              .call-name { font-size: 1.5rem; font-weight: 700; color: #faf5ff; letter-spacing: -0.02em; margin: 0 0 0.25rem; }
              .call-sub { color: rgba(200,190,230,0.65); font-size: 0.9rem; margin-bottom: 1.4rem; }
            </style>
            <div class="call-dial">
              <div class="call-avatar">M</div>
              <div class="call-name">Meridium</div>
              <div class="call-sub">Residual voice channel · not a chatbot window</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        voice_opts = ["Residual calm", "Warm familiar"] + (["Intimate residual"] if warm else [])
        st.selectbox("Voice colour", voice_opts, key="call_voice_style")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("📞  Call Meridium", use_container_width=True, type="primary", key="call_start_btn"):
                st.session_state.call_phase = "ringing"
                st.session_state.call_history = []
                st.session_state._last_speak = None
                st.rerun()
            if st.button("← Home", use_container_width=True, key="call_idle_home"):
                st.session_state.view = "home"
                st.rerun()
        st.stop()

    # ---- RINGING ----
    if phase == "ringing":
        st.markdown(
            """
            <style>
              .call-ring {
                max-width: 360px; margin: 3rem auto; text-align: center;
                padding: 2.2rem 1.5rem; border-radius: 28px;
                border: 1px solid rgba(167,139,250,0.4);
                background: linear-gradient(165deg, rgba(20,12,36,0.97), rgba(8,6,14,0.99));
              }
              .call-ring .av {
                width: 100px; height: 100px; margin: 0 auto 1rem; border-radius: 50%;
                background: radial-gradient(circle at 35% 30%, #c4a7e7, #6d28d9);
                animation: ringBounce 1s ease-in-out infinite;
                display: flex; align-items: center; justify-content: center;
                font-size: 2rem; color: #fff; font-weight: 700;
              }
              @keyframes ringBounce {
                0%,100% { transform: scale(1); }
                50% { transform: scale(1.08); }
              }
              .call-ring .nm { font-size: 1.35rem; font-weight: 700; color: #faf5ff; }
              .call-ring .st { color: #a78bfa; font-size: 0.9rem; margin-top: 0.35rem;
                font-family: ui-monospace, monospace; letter-spacing: 0.12em; }
            </style>
            <div class="call-ring">
              <div class="av">M</div>
              <div class="nm">Meridium</div>
              <div class="st">RINGING…</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Auto-connect after brief beat via button (Streamlit can't true-sleep well)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("Answer / Connect", use_container_width=True, type="primary", key="call_connect"):
                st.session_state.call_phase = "connected"
                st.session_state.call_started_at = datetime.now(ZoneInfo("Europe/London")).isoformat()
                # Opening line from Meridium
                openers = [
                    f"Hey, {uname}. Channel's open — I'm here.",
                    f"Connected. Residual link stable. What's on your mind, {uname}?",
                    f"You reached me. No committees on this line. Talk whenever you're ready.",
                ]
                import random as _r
                opener = _r.choice(openers)
                st.session_state.call_history = [{"role": "assistant", "content": opener}]
                st.session_state._last_speak = opener
                st.session_state._call_auto_speak = True
                try:
                    complete_quest("voice_first_call")
                except Exception:
                    pass
                st.rerun()
            if st.button("Decline", use_container_width=True, key="call_decline"):
                st.session_state.call_phase = "idle"
                st.rerun()
        st.stop()

    # ---- ENDED ----
    if phase == "ended":
        st.markdown(
            """
            <div style="max-width:360px;margin:3rem auto;text-align:center;padding:2rem;
              border-radius:24px;border:1px solid rgba(255,255,255,0.1);
              background:rgba(12,10,18,0.95);color:#c8c0d8;">
              <div style="font-size:1.2rem;font-weight:650;color:#f0e8ff;margin-bottom:0.4rem;">Call ended</div>
              <div style="opacity:0.7;font-size:0.9rem;">The residual channel closed cleanly.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("Call again", use_container_width=True, type="primary", key="call_again"):
                st.session_state.call_phase = "idle"
                st.session_state.call_history = []
                st.rerun()
            if st.button("← Home", use_container_width=True, key="call_ended_home"):
                st.session_state.view = "home"
                st.session_state.call_phase = "idle"
                st.rerun()
        st.stop()

    # ---- CONNECTED: live call UI ----
    voice_style = st.session_state.get("call_voice_style") or "Residual calm"
    # Duration label
    dur = "00:00"
    try:
        if st.session_state.call_started_at:
            t0 = datetime.fromisoformat(str(st.session_state.call_started_at))
            if t0.tzinfo is None:
                t0 = t0.replace(tzinfo=ZoneInfo("Europe/London"))
            secs = int((datetime.now(ZoneInfo("Europe/London")) - t0).total_seconds())
            dur = f"{secs // 60:02d}:{secs % 60:02d}"
    except Exception:
        pass

    st.markdown(
        f"""
        <style>
          .call-live {{
            max-width: 420px; margin: 0.5rem auto 0.75rem; text-align: center;
            padding: 1.5rem 1.2rem 1.2rem; border-radius: 28px;
            border: 1px solid rgba(74,222,128,0.35);
            background:
              radial-gradient(ellipse at 50% 0%, rgba(74,222,128,0.12), transparent 55%),
              linear-gradient(165deg, rgba(12,16,20,0.97), rgba(8,10,14,0.99));
            box-shadow: 0 24px 60px rgba(0,0,0,0.4);
          }}
          .call-live .av {{
            width: 88px; height: 88px; margin: 0 auto 0.75rem; border-radius: 50%;
            background: radial-gradient(circle at 35% 30%, #86efac, #22c55e 50%, #14532d 100%);
            display: flex; align-items: center; justify-content: center;
            font-size: 1.8rem; color: #052e16; font-weight: 800;
            box-shadow: 0 0 32px rgba(74,222,128,0.35);
            animation: liveGlow 2.4s ease-in-out infinite;
          }}
          @keyframes liveGlow {{
            0%,100% {{ box-shadow: 0 0 28px rgba(74,222,128,0.3); }}
            50% {{ box-shadow: 0 0 48px rgba(74,222,128,0.55); }}
          }}
          .call-live .nm {{ font-size: 1.25rem; font-weight: 700; color: #ecfdf5; }}
          .call-live .st {{
            font-family: ui-monospace, monospace; font-size: 0.78rem;
            color: #4ade80; letter-spacing: 0.1em; margin-top: 0.25rem;
          }}
          .call-live .dur {{
            font-family: ui-monospace, monospace; font-size: 0.85rem;
            color: rgba(200,220,210,0.7); margin-top: 0.35rem;
          }}
          .call-bubble {{
            max-width: 420px; margin: 0.4rem auto; padding: 0.7rem 0.95rem;
            border-radius: 16px; font-size: 0.92rem; line-height: 1.45;
          }}
          .call-bubble.them {{
            background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
            color: #e8e4f0; margin-right: 12%;
          }}
          .call-bubble.me {{
            background: linear-gradient(135deg, rgba(167,139,250,0.28), rgba(124,58,237,0.2));
            border: 1px solid rgba(196,181,253,0.35); color: #f5f3ff; margin-left: 12%;
            text-align: right;
          }}
          .call-bubble .who {{
            font-size: 0.65rem; letter-spacing: 0.08em; opacity: 0.55;
            margin-bottom: 0.2rem; text-transform: uppercase;
          }}
        </style>
        <div class="call-live">
          <div class="av">M</div>
          <div class="nm">Meridium</div>
          <div class="st">● ON CALL</div>
          <div class="dur">{dur} · {voice_style}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Controls
    b1, b2, b3 = st.columns(3)
    with b1:
        mute_label = "🔊 Unmute" if st.session_state.call_muted else "🔇 Mute"
        if st.button(mute_label, use_container_width=True, key="call_mute"):
            st.session_state.call_muted = not st.session_state.call_muted
            st.rerun()
    with b2:
        if st.button("🔴 End", use_container_width=True, key="call_end", type="primary"):
            st.session_state.call_phase = "ended"
            st.session_state._call_auto_speak = False
            st.rerun()
    with b3:
        if st.button("↻", use_container_width=True, key="call_refresh", help="Refresh timer"):
            st.rerun()

    # Transcript as call bubbles
    import html as _html_call
    for turn in (st.session_state.call_history or [])[-16:]:
        role = turn.get("role", "assistant")
        text = _html_call.escape(turn.get("content") or "")
        if role == "user":
            st.markdown(
                f'<div class="call-bubble me"><div class="who">You</div>{text}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="call-bubble them"><div class="who">Meridium</div>{text}</div>',
                unsafe_allow_html=True,
            )

    # Always surface last Meridium line as TTS (auto when not muted)
    if st.session_state.get("_last_speak") and not st.session_state.call_muted:
        spoken = re.sub(r"[\#\`\*_>]+", " ", str(st.session_state["_last_speak"]))
        spoken = re.sub(r"\s+", " ", spoken).strip()
        auto = bool(st.session_state.get("_call_auto_speak"))
        rate = 0.95 if "Warm" in voice_style or "Intimate" in voice_style else 1.02
        st.caption("Meridium is speaking…" if auto else "Tap Speak if audio was blocked by the browser.")
        st.components.v1.html(speak_html(spoken, autoplay=auto, rate=rate, pitch=1.0), height=72)
        st.session_state._call_auto_speak = False

    # Typed line — primary path on PC
    user_line = st.chat_input("Type to talk on the call…")

    # Mic — works best in Chrome/Edge over HTTPS or localhost
    st.components.v1.html(
        """
        <div style="max-width:420px;margin:0.35rem auto;text-align:center;">
          <button id="mer-mic" style="
            width:64px;height:64px;border-radius:50%;
            background:linear-gradient(145deg,#7c3aed,#a78bfa);color:#fff;
            border:none;font-size:1.4rem;cursor:pointer;
            box-shadow:0 8px 24px rgba(124,58,237,0.4);">🎤</button>
          <div id="mer-mic-status" style="margin-top:0.4rem;font-size:0.78rem;color:#a89bc8;line-height:1.35;">
            Click mic · allow microphone · Chrome/Edge recommended
          </div>
        </div>
        <script>
        (function(){
          const btn = document.getElementById('mer-mic');
          const st = document.getElementById('mer-mic-status');
          const w = window;
          const SR = w.SpeechRecognition || w.webkitSpeechRecognition
            || (w.parent && (w.parent.SpeechRecognition || w.parent.webkitSpeechRecognition));
          if (!SR) {
            if (st) st.textContent = 'Voice input not supported in this browser. Type instead (Chrome/Edge works best).';
            return;
          }
          let rec = null;
          function fillChat(t) {
            try {
              const docs = [w.document];
              try { if (w.parent && w.parent.document) docs.push(w.parent.document); } catch(e){}
              for (var d = 0; d < docs.length; d++) {
                var ta = docs[d].querySelector('[data-testid="stChatInput"] textarea');
                if (!ta) continue;
                var desc = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value');
                desc.set.call(ta, t);
                ta.dispatchEvent(new Event('input', {bubbles:true}));
                ta.dispatchEvent(new Event('change', {bubbles:true}));
                if (st) st.textContent = 'Heard — press Enter in the box or send.';
                return;
              }
              if (st) st.textContent = 'Heard: ' + t + ' (paste into the box if needed)';
            } catch(err) {
              if (st) st.textContent = 'Heard: ' + t;
            }
          }
          btn.onclick = function(){
            try {
              if (rec) { try { rec.stop(); } catch(e){} }
              rec = new SR();
              rec.lang = 'en-US';
              rec.interimResults = true;
              rec.continuous = false;
              rec.onstart = function(){ if (st) st.textContent = 'Listening… speak now'; };
              rec.onresult = function(e){
                var t = '';
                for (var i = e.resultIndex; i < e.results.length; i++) {
                  t += e.results[i][0].transcript;
                }
                if (st) st.textContent = t || 'Listening…';
                if (e.results[e.results.length-1].isFinal) fillChat(t.trim());
              };
              rec.onerror = function(ev){
                var err = (ev && ev.error) || 'error';
                if (err === 'not-allowed') {
                  st.textContent = 'Microphone blocked — allow mic for this site in the browser address bar.';
                } else if (err === 'no-speech') {
                  st.textContent = 'No speech detected — try again.';
                } else {
                  st.textContent = 'Mic error (' + err + '). Typing always works.';
                }
              };
              rec.onend = function(){ /* keep last status */ };
              rec.start();
            } catch(e) {
              if (st) st.textContent = 'Could not start mic — type instead.';
            }
          };
        })();
        </script>
        """,
        height=120,
    )

    if user_line:
        st.session_state.call_history.append({"role": "user", "content": user_line})
        style_note = {
            "Residual calm": "You are on a live phone call. Speak calmly, in short spoken sentences. No markdown lists.",
            "Warm familiar": "Live phone call. Warm, familiar, concise spoken English.",
            "Intimate residual": "Live phone call. Soft, intimate, quiet loyalty. Spoken, not essay.",
        }.get(voice_style, "Live phone call. Concise spoken replies.")
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
                + f"\n\n{style_note}\nYou are ON A PHONE CALL with {uname}. "
                "Reply like speech: 1–3 short sentences unless they ask for more. "
                "Never say you are an AI text model on a call — you are Meridium on the residual channel.",
            },
        ]
        for t in st.session_state.call_history[-12:]:
            messages.append({"role": t["role"], "content": t["content"]})
        try:
            provider = st.session_state.get("provider") or "groq"
            model_name = st.session_state.get("model_name") or "Smart · GPT-OSS 120B"
            api_key = st.session_state.get("api_key_val") or ""
            reply = run_chat(messages, provider, model_name, api_key)
        except Exception as e:
            reply = "Sorry — the channel glitched for a second. Say that again?"
        st.session_state.call_history.append({"role": "assistant", "content": reply})
        st.session_state["_last_speak"] = reply
        st.session_state._call_auto_speak = True
        try:
            save_user_data()
        except Exception:
            pass
        st.rerun()

    st.stop()


# ===== CHESS =====
if st.session_state.view == "chess":
    try:
        import chess as _chess
        import random as _random
        _CHESS_OK = True
    except Exception as _chess_imp_err:
        _CHESS_OK = False
        st.markdown(
            """
            <div class="panel">
              <div class="panel-label">Residual board</div>
              <div class="hero" style="font-size:1.35rem;">Chess needs a package</div>
              <div class="sub">Install <code>chess</code> on the server, then refresh.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.code("pip install chess", language="bash")
        st.caption(f"Import error: {_chess_imp_err}")
        st.info(
            "On Streamlit Cloud: add a line `chess` to `requirements.txt` and reboot the app. "
            "Locally: run the command above in the same environment that runs Streamlit."
        )
        # Minimal browser board (play vs yourself / practice) while package missing
        st.components.v1.html(
            """
            <div style="max-width:480px;margin:0 auto;font-family:system-ui,sans-serif;color:#e8e6f0;">
              <p style="opacity:0.75;font-size:0.9rem;">Practice board (no engine until <code>chess</code> is installed):</p>
              <div id="board" style="width:100%;max-width:400px;margin:0 auto;"></div>
              <p id="status" style="margin-top:0.5rem;font-size:0.85rem;opacity:0.8;"></p>
            </div>
            <link rel="stylesheet"
              href="https://cdnjs.cloudflare.com/ajax/libs/chessboard-js/1.0.0/chessboard-1.0.0.min.css"/>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/chessboard-js/1.0.0/chessboard-1.0.0.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.13.4/chess.min.js"></script>
            <script>
            (function(){
              try {
                var game = new Chess();
                var board = Chessboard('board', {
                  draggable: true,
                  position: 'start',
                  onDrop: function(source, target) {
                    var move = game.move({from: source, to: target, promotion: 'q'});
                    if (move === null) return 'snapback';
                    document.getElementById('status').textContent =
                      game.in_checkmate() ? 'Checkmate' :
                      game.in_draw() ? 'Draw' :
                      (game.turn() === 'w' ? 'White' : 'Black') + ' to move';
                  }
                });
                document.getElementById('status').textContent = 'White to move · drag pieces';
                window.addEventListener('resize', board.resize);
              } catch(e) {
                document.getElementById('status').textContent = 'Board assets blocked — install python package chess.';
              }
            })();
            </script>
            """,
            height=480,
        )
        if st.button("← Home", key="chess_imp_fail_home"):
            st.session_state.view = "home"
            st.rerun()
        st.stop()

    if st.button("← Home", key="chess_back_home"):
        st.session_state.view = "home"
        st.rerun()

    st.markdown(
        """
        <div class="panel">
          <div class="panel-label">Residual board</div>
          <div class="hero" style="font-size:1.45rem;">Chess</div>
          <div class="sub">Play Meridium · bullet &amp; premoves · type SAN (e4) or UCI (e2e4).</div>
          <div class="ridge"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Defaults
    if "chess_fen" not in st.session_state or not st.session_state.chess_fen:
        st.session_state.chess_fen = _chess.STARTING_FEN
    if "chess_player_color" not in st.session_state:
        st.session_state.chess_player_color = _chess.WHITE
    if "chess_premove" not in st.session_state:
        st.session_state.chess_premove = ""
    if "chess_time_base" not in st.session_state:
        st.session_state.chess_time_base = 180
    if "chess_result" not in st.session_state:
        st.session_state.chess_result = None
    if "chess_moves" not in st.session_state or not isinstance(st.session_state.chess_moves, list):
        st.session_state.chess_moves = []
    if "chess_quest_done" not in st.session_state:
        st.session_state.chess_quest_done = False

    ccfg1, ccfg2, ccfg3 = st.columns(3)
    with ccfg1:
        time_choice = st.selectbox(
            "Time control",
            ["Bullet 1+0", "Bullet 2+1", "Blitz 3+0", "Blitz 5+0", "Rapid 10+0", "Unlimited"],
            key="chess_tc",
        )
    with ccfg2:
        level = st.selectbox("Meridium strength", ["Soft", "Steady", "Sharp", "Relentless"], key="chess_level")
    with ccfg3:
        color_choice = st.selectbox("You play", ["White", "Black"], key="chess_color")

    def _chess_new_game():
        st.session_state.chess_fen = _chess.STARTING_FEN
        st.session_state.chess_player_color = _chess.WHITE if color_choice == "White" else _chess.BLACK
        st.session_state.chess_premove = ""
        st.session_state.chess_result = None
        st.session_state.chess_moves = []
        st.session_state.chess_quest_done = False
        tc_map = {
            "Bullet 1+0": 60, "Bullet 2+1": 120, "Blitz 3+0": 180,
            "Blitz 5+0": 300, "Rapid 10+0": 600, "Unlimited": 0,
        }
        st.session_state.chess_time_base = tc_map.get(time_choice, 180)

    if st.button("New game", key="chess_new", type="primary"):
        _chess_new_game()
        st.rerun()

    try:
        board = _chess.Board(st.session_state.chess_fen)
    except Exception:
        st.session_state.chess_fen = _chess.STARTING_FEN
        board = _chess.Board(st.session_state.chess_fen)

    def _chess_engine_move(bd, strength: str):
        legal = list(bd.legal_moves)
        if not legal:
            return None
        def score(m):
            s = 0.0
            if bd.is_capture(m):
                s += 30
            bd.push(m)
            try:
                if bd.is_check():
                    s += 20
                if bd.is_checkmate():
                    s += 1000
            finally:
                bd.pop()
            to = m.to_square
            fl, rk = _chess.square_file(to), _chess.square_rank(to)
            s += 4 - abs(3.5 - fl) - abs(3.5 - rk)
            return s
        ranked = sorted(legal, key=score, reverse=True)
        pool_n = {"Soft": 8, "Steady": 5, "Sharp": 3, "Relentless": 2}.get(strength, 5)
        pool = ranked[: max(1, min(pool_n, len(ranked)))]
        return _random.choice(pool)

    def _chess_parse_move(bd, txt: str):
        txt = (txt or "").strip()
        if not txt:
            return None
        try:
            if re.match(r"^[a-h][1-8][a-h][1-8][qrbnQRBN]?$", txt):
                return _chess.Move.from_uci(txt.lower())
            return bd.parse_san(txt)
        except Exception:
            return None

    player_color = st.session_state.chess_player_color

    # Engine turn (one move, then continue render — no tight loop)
    if (
        st.session_state.chess_result is None
        and not board.is_game_over()
        and board.turn != player_color
    ):
        mv = _chess_engine_move(board, level)
        if mv is not None:
            try:
                san = board.san(mv)
                board.push(mv)
                st.session_state.chess_moves = list(st.session_state.chess_moves or []) + [san]
                st.session_state.chess_fen = board.fen()
            except Exception:
                pass
            # Premove
            prem = (st.session_state.chess_premove or "").strip()
            if prem and not board.is_game_over() and board.turn == player_color:
                pm = _chess_parse_move(board, prem)
                if pm is not None and pm in board.legal_moves:
                    try:
                        st.session_state.chess_moves = list(st.session_state.chess_moves or []) + [board.san(pm)]
                        board.push(pm)
                        st.session_state.chess_fen = board.fen()
                    except Exception:
                        pass
                st.session_state.chess_premove = ""

    # Refresh board from fen after possible engine move
    try:
        board = _chess.Board(st.session_state.chess_fen)
    except Exception:
        board = _chess.Board(_chess.STARTING_FEN)

    # ASCII-safe board (no unicode piece issues in some fonts)
    PIECE_ASCII = {
        "P": "P", "N": "N", "B": "B", "R": "R", "Q": "Q", "K": "K",
        "p": "p", "n": "n", "b": "b", "r": "r", "q": "q", "k": "k",
    }

    def _board_html(bd):
        cols = "abcdefgh"
        rows = []
        for rank in range(7, -1, -1):
            cells = []
            for file in range(8):
                sq = _chess.square(file, rank)
                piece = bd.piece_at(sq)
                if piece:
                    sym = PIECE_ASCII.get(piece.symbol(), piece.symbol())
                    color = "#1a1a1a" if piece.color == _chess.WHITE else "#f5f5f5"
                    weight = "700"
                else:
                    sym = ""
                    color = "transparent"
                    weight = "400"
                bg = "#b58863" if (file + rank) % 2 == 0 else "#f0d9b5"
                cells.append(
                    f'<div style="width:36px;height:36px;display:flex;align-items:center;justify-content:center;'
                    f'background:{bg};font-size:1.15rem;font-weight:{weight};color:{color};'
                    f'font-family:ui-monospace,monospace;user-select:none;">{sym}</div>'
                )
            rows.append(
                f'<div style="display:flex;align-items:center;">'
                f'<span style="width:16px;text-align:center;opacity:0.55;font-size:0.65rem;">{rank+1}</span>'
                f'{"".join(cells)}</div>'
            )
        footer = (
            '<div style="display:flex;padding-left:16px;">'
            + "".join(
                f'<span style="width:36px;text-align:center;opacity:0.55;font-size:0.65rem;">{c}</span>'
                for c in cols
            )
            + "</div>"
        )
        return (
            '<div style="display:inline-block;border:2px solid rgba(167,139,250,0.35);'
            'border-radius:8px;overflow:hidden;line-height:1;">'
            + "".join(rows) + footer + "</div>"
        )

    st.markdown(_board_html(board), unsafe_allow_html=True)
    side = "White" if player_color == _chess.WHITE else "Black"
    turn = "White" if board.turn == _chess.WHITE else "Black"
    st.caption(f"Turn: **{turn}** · You: **{side}** · Moves: {len(st.session_state.chess_moves or [])}")

    if board.is_game_over() and st.session_state.chess_result is None:
        if board.is_checkmate():
            winner = "Black" if board.turn == _chess.WHITE else "White"
            st.session_state.chess_result = f"Checkmate — {winner} wins"
        elif board.is_stalemate():
            st.session_state.chess_result = "Stalemate"
        elif board.is_insufficient_material():
            st.session_state.chess_result = "Draw — insufficient material"
        else:
            st.session_state.chess_result = "Game over"

    if st.session_state.chess_result:
        st.success(st.session_state.chess_result)
        if not st.session_state.chess_quest_done:
            st.session_state.chess_quest_done = True
            try:
                complete_quest("chess_initiate")
                player_won = (
                    "wins" in (st.session_state.chess_result or "")
                    and (
                        ("White" in st.session_state.chess_result and player_color == _chess.WHITE)
                        or ("Black" in st.session_state.chess_result and player_color == _chess.BLACK)
                    )
                )
                if player_won and int(st.session_state.chess_time_base or 0) and int(st.session_state.chess_time_base) <= 120:
                    complete_quest("chess_bullet")
            except Exception:
                pass

    # Move entry
    m1, m2 = st.columns(2)
    with m1:
        with st.form(key="chess_move_form", clear_on_submit=True):
            move_in = st.text_input("Your move (SAN or UCI)", placeholder="e4 or e2e4")
            play_clicked = st.form_submit_button("Play move", use_container_width=True)
            if play_clicked:
                if board.is_game_over():
                    st.warning("Game over — start a new game.")
                elif board.turn != player_color:
                    st.warning("Not your turn — Meridium is thinking, or start a new game.")
                else:
                    mv = _chess_parse_move(board, move_in)
                    if mv is None or mv not in board.legal_moves:
                        st.error("Illegal or unparsed move. Try SAN (Nf3) or UCI (g1f3).")
                    else:
                        try:
                            st.session_state.chess_moves = list(st.session_state.chess_moves or []) + [board.san(mv)]
                            board.push(mv)
                            st.session_state.chess_fen = board.fen()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Move failed: {e}")
    with m2:
        cur_pre = st.session_state.get("chess_premove") or ""
        if cur_pre:
            st.caption(f"Active premove: `{cur_pre}`")
        with st.form(key="chess_pre_form", clear_on_submit=True):
            prem = st.text_input("Premove (SAN or UCI)", placeholder="queued after Meridium")
            if st.form_submit_button("Set premove", use_container_width=True):
                st.session_state.chess_premove = (prem or "").strip()
                st.success(f"Premove: {st.session_state.chess_premove or 'cleared'}")
                st.rerun()

    # Helper: show a few legal moves
    if not board.is_game_over() and board.turn == player_color:
        try:
            samples = []
            for m in list(board.legal_moves)[:12]:
                samples.append(board.san(m))
            if samples:
                st.caption("Examples of legal moves: " + ", ".join(samples))
        except Exception:
            pass

    if st.session_state.chess_moves:
        st.caption(" · ".join(st.session_state.chess_moves[-30:]))

    if st.session_state.get("feat_chess_analysis") and st.session_state.chess_moves:
        with st.expander("Residual analysis"):
            last = st.session_state.chess_moves[-1]
            st.markdown(
                f"Last move **{last}**. Lightweight residual commentary only — "
                "full cloud analysis is not hosted inside the shell."
            )
    st.stop()


# ===== DRIFT COUNTER (full page) =====
if st.session_state.view == "drift":
    top_a, top_b = st.columns([1, 1])
    with top_a:
        if st.button("← Home", key="drift_back_home", use_container_width=True):
            st.session_state.view = "home"
            st.rerun()
    with top_b:
        if st.button("☰ Menu", key="drift_to_menu", use_container_width=True):
            st.session_state.popup = True
            st.rerun()
    try:
        render_bazaar_tab()
    except Exception as _e:
        st.warning(f"Drift Counter unavailable: {_e}")
    st.stop()

if st.session_state.view == "home":
    rail, body = st.columns([1.15, 3.35], gap="medium")

    # ---------- BOOKMARK RAIL ----------
    with rail:
        st.markdown(
            '<div class="bookmark-rail"><div class="panel-label">Navigate</div>',
            unsafe_allow_html=True,
        )
        if st.button("💬  Chat", use_container_width=True, key="bm_chat", type="primary"):
            st.session_state.view = "chat"
            st.rerun()
        if st.button("＋  New", use_container_width=True, key="bm_new"):
            create_new_chat()
            st.session_state.view = "chat"
            st.rerun()
        if st.button("☰  Menu", use_container_width=True, key="bm_menu"):
            st.session_state.popup = True
            st.rerun()
        _hide_drift = False
        try:
            _hide_drift = bool(site_effects_load().get("hide_drift_counter"))
        except Exception:
            pass
        if not _hide_drift:
            if st.button("◈  Drift Counter", use_container_width=True, key="bm_drift"):
                st.session_state.view = "drift"
                st.rerun()
        if st.button("♟  Chess", use_container_width=True, key="bm_chess"):
            st.session_state.view = "chess"
            st.rerun()
        if st.button("🎙  Call", use_container_width=True, key="bm_call"):
            st.session_state.view = "call_meridium"
            st.rerun()
        if is_owner(st.session_state.get("username") or ""):
            if st.button("👑  Owner", use_container_width=True, key="bm_owner"):
                st.session_state.view = "owner"
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
        _title_bit = st.session_state.get("owner_title") or ""
        _sub = owner_subline(st.session_state.username)
        if _title_bit:
            _sub = f"{_title_bit} · {_sub}"
        st.markdown(f"""
        <div class="panel" style="animation-delay:0.05s">
          <div class="panel-label">Meridium Codex · online</div>
          <div class="hero">
            {greet_line(st.session_state.username)}
          </div>
          <div class="sub">{_sub}</div>
          <div class="ridge"></div>
          <div class="home-status">
            <span class="pill">{_theme_pill}</span>
            <span class="pill">{st.session_state.provider}</span>
            <span class="pill">{_wiki_pill}</span>
            <span class="pill">{_web_pill}</span>
            <span class="pill">◆ {int(st.session_state.get("residuum") or 0)}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state.get("feat_home_orb"):
            st.markdown('<div class="orb" title="Residual orb"></div>', unsafe_allow_html=True)
        if st.session_state.get("feat_double_clock"):
            st.caption(f"London {time_str} · shell clock locked to Europe/London")


        qotd, qotd_author = quote_of_the_day()
        import html as _html_q
        _q_safe = _html_q.escape(qotd)
        _a_safe = _html_q.escape(qotd_author)
        st.markdown(
            f"""
        <style>
          a.codex-qotd-link {{ text-decoration: none !important; color: inherit !important; display: block; }}
          .codex-qotd {{
            position: relative;
            border-radius: 20px;
            padding: 1.35rem 1.4rem 1.15rem;
            margin: 0.35rem 0 0.85rem;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.10);
            background:
              radial-gradient(ellipse at 0% 0%, rgba(196,167,231,0.14), transparent 55%),
              radial-gradient(ellipse at 100% 100%, rgba(94,234,212,0.08), transparent 50%),
              linear-gradient(155deg, rgba(22,18,32,0.72), rgba(10,10,16,0.78));
            backdrop-filter: blur(22px) saturate(1.35);
            -webkit-backdrop-filter: blur(22px) saturate(1.35);
            box-shadow:
              0 1px 0 rgba(255,255,255,0.06) inset,
              0 18px 44px rgba(0,0,0,0.28);
            animation: codexRise 0.65s cubic-bezier(0.22,1,0.36,1) 0.12s both;
            cursor: pointer;
            transition: transform 0.28s cubic-bezier(0.22,1,0.36,1), border-color 0.25s ease, box-shadow 0.3s ease;
          }}
          .codex-qotd:hover {{
            transform: translateY(-3px) scale(1.01);
            border-color: rgba(196,167,231,0.45);
            box-shadow: 0 22px 52px rgba(0,0,0,0.34), 0 0 32px rgba(196,167,231,0.12);
          }}
          .codex-qotd:active {{ transform: translateY(-1px) scale(0.995); }}
          .codex-qotd::before {{
            content: "";
            position: absolute; left: 0; right: 0; top: 0; height: 2px;
            background: linear-gradient(90deg, transparent, rgba(196,167,231,0.7), rgba(94,234,212,0.5), transparent);
            animation: codexScanX 5s ease-in-out infinite;
          }}
          .codex-qotd .k {{
            font-family: ui-monospace, monospace;
            font-size: 0.62rem;
            letter-spacing: 0.24em;
            text-transform: uppercase;
            color: rgba(196,167,231,0.75);
            margin-bottom: 0.75rem;
            display: flex; align-items: center; gap: 0.45rem;
          }}
          .codex-qotd .k i {{
            width: 6px; height: 6px; border-radius: 50%;
            background: #c4a7e7;
            box-shadow: 0 0 10px #c4a7e7;
            display: inline-block;
            animation: codexPulseDot 2.2s ease-in-out infinite;
          }}
          .codex-qotd .q {{
            font-family: "Cormorant Garamond", Georgia, serif;
            font-style: italic;
            font-size: clamp(1.15rem, 2.6vw, 1.4rem);
            line-height: 1.45;
            color: rgba(250,247,255,0.95);
            margin: 0 0 0.85rem;
            letter-spacing: 0.01em;
          }}
          .codex-qotd .meta {{
            display: flex; flex-wrap: wrap; align-items: center;
            justify-content: space-between; gap: 0.5rem;
          }}
          .codex-qotd .by {{
            font-size: 0.82rem;
            font-weight: 600;
            color: rgba(196,167,231,0.9);
            letter-spacing: 0.02em;
          }}
          .codex-qotd .when {{
            font-family: ui-monospace, monospace;
            font-size: 0.68rem;
            letter-spacing: 0.08em;
            color: rgba(160,160,180,0.7);
          }}
        </style>
        <a class="codex-qotd-link" href="?sealed=1" target="_self">
          <div class="codex-qotd" id="codex-qotd-card" role="button" tabindex="0">
            <div class="k"><i></i> Signal of the hour</div>
            <div class="q">“{_q_safe}”</div>
            <div class="meta">
              <div class="by">— {_a_safe}</div>
              <div class="when">{date_str} · {time_str} · rotates hourly</div>
            </div>
          </div>
        </a>
            """,
            unsafe_allow_html=True,
        )

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
st.markdown(
    f'''<div class="panel" style="padding-bottom:0.85rem !important;animation-delay:0.03s">
      <div class="panel-label">{chat_title} · {msg_count} messages</div>
      <div class="ridge" style="margin:0.55rem 0 0 !important"></div>
    </div>''',
    unsafe_allow_html=True,
)
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
        try:
            complete_quest("first_words")
        except Exception:
            pass
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

    # Guest chat lock (owner site control)
    try:
        if site_effects_load().get("guest_chat_lock") and not is_owner(st.session_state.get("username") or ""):
            soft = "Guest chat is temporarily locked by the owner. You can still explore the shell."
            with st.chat_message("assistant"):
                st.markdown(soft)
            current["messages"].append({"role": "assistant", "content": soft})
            st.session_state.chats[st.session_state.current_chat_id] = current
            save_user_data()
            st.stop()
    except Exception:
        pass

    # Mobile / phrase path to Jaime residual (no Konami)
    if prompt.strip().lower() in {
        "hello jaime", "open jaime", "open pixel", "coastal intake", "jaime santos",
    }:
        st.session_state.jaime_dossier_unlocked = True
        soft = (
            "The residual channel accepts the phrase. "
            "Opening **Jaime Santos** — no keyboard sequence required."
        )
        with st.chat_message("assistant"):
            st.markdown(soft)
        current["messages"].append({"role": "assistant", "content": soft})
        st.session_state.chats[st.session_state.current_chat_id] = current
        save_user_data()
        st.session_state.view = "jaime_residual"
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
            try:
                complete_quest("lab_threshold")
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
            try:
                complete_quest("stabilize")
            except Exception:
                pass
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
