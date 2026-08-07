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


def inject_css(font_name: str, theme_name: str = "Caelestia", popup_open: bool = False):
    font = FONTS.get(font_name, FONTS["Inter"])
    SHELL = THEMES.get(theme_name, THEMES["Caelestia"])
    moj = "1"
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=Outfit:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,600&display=swap');

    html, body, [class*="css"] {{
        font-family: {font} !important;
        font-size: calc(15px * {moj});
    }}
    .stApp {{
        background:
            radial-gradient(900px 480px at 15% -5%, {SHELL["accent_soft"]}, transparent 55%),
            radial-gradient(700px 400px at 95% 10%, {SHELL["accent_soft"]}, transparent 50%),
            {SHELL["bg"]};
        color: {SHELL["text"]};
    }}
    #MainMenu, footer, header, .stDeployButton, section[data-testid="stSidebar"] {{
        display: none !important;
    }}
    .block-container {{
        padding-top: 0.8rem !important;
        padding-bottom: 5.5rem !important;
        max-width: 1080px !important;
    }}

    /* ===== DESIGN 1 — Caelestia Shell ===== */
    .waybar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        background: {SHELL["panel"]};
        border: 1px solid {SHELL["border"]};
        border-radius: 16px;
        padding: 10px 16px;
        margin-bottom: 16px;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
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
        box-shadow: 0 0 20px {SHELL["accent_soft"]};
    }}
    .brand {{ font-weight: 600; letter-spacing: -0.02em; }}
    .chip {{
        background: {SHELL["accent_soft"]};
        color: {SHELL["accent"]};
        border: 1px solid {SHELL["border"]};
        border-radius: 999px;
        padding: 4px 11px;
        font-size: 0.75rem;
        font-weight: 500;
    }}
    .clock {{ font-weight: 600; font-variant-numeric: tabular-nums; }}
    .muted {{ color: {SHELL["muted"]}; font-size: 0.8rem; }}

    .panel {{
        background: {SHELL["panel"]};
        border: 1px solid {SHELL["border"]};
        border-radius: 18px;
        padding: 20px;
        backdrop-filter: blur(18px);
        box-shadow: 0 10px 40px rgba(0,0,0,0.22);
        animation: fadeUp 0.45s ease both;
        margin-bottom: 12px;
    }}
    .panel-label {{
        font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;
        color: {SHELL["muted"]}; margin-bottom: 10px; font-weight: 600;
    }}
    .hero {{
        font-size: 2.1rem; font-weight: 700; letter-spacing: -0.03em;
        margin: 0 0 6px; color: {SHELL["text"]};
    }}
    .hero span {{ color: {SHELL["accent"]}; }}
    .sub {{ color: {SHELL["muted"]}; margin-bottom: 14px; font-size: 0.95rem; }}
    .ridge {{
        height: 1px; margin: 8px 0 16px;
        background: linear-gradient(90deg, transparent, {SHELL["accent"]}, transparent);
        opacity: 0.5;
    }}

    .grid4 {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
    }}
    @media (min-width: 800px) {{
        .grid4 {{ grid-template-columns: repeat(4, 1fr); }}
        .hero {{ font-size: 2.35rem; }}
    }}
    .card {{
        background: {SHELL["panel_solid"]};
        border: 1px solid {SHELL["border"]};
        border-radius: 16px;
        padding: 16px;
        transition: border-color 0.15s, transform 0.15s;
    }}
    .card:hover {{ border-color: {SHELL["accent"]}; transform: translateY(-2px); }}
    .card-ico {{ color: {SHELL["accent"]}; font-size: 1.2rem; margin-bottom: 8px; }}
    .card-t {{ font-weight: 600; font-size: 0.9rem; }}
    .card-d {{ color: {SHELL["muted"]}; font-size: 0.72rem; margin-top: 3px; }}

    .hist {{
        display: flex; align-items: center; gap: 10px;
        padding: 11px 12px; border-radius: 12px;
        background: {SHELL["panel_solid"]};
        border: 1px solid {SHELL["border"]};
        margin-bottom: 8px;
    }}
    .hist-ico {{
        width: 32px; height: 32px; border-radius: 9px;
        background: {SHELL["accent_soft"]}; color: {SHELL["accent"]};
        display: flex; align-items: center; justify-content: center;
    }}
    .hist-t {{
        flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
        font-size: 0.88rem;
    }}

    /* Chat */
    .stChatMessage {{
        background: {SHELL["panel"]} !important;
        border: 1px solid {SHELL["border"]} !important;
        border-radius: 16px !important;
        margin-bottom: 10px !important;
        animation: fadeUp 0.3s ease both;
    }}
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"],
    [data-testid="stChatAvatar"] {{ display: none !important; }}
    .stChatInput > div {{
        background: {SHELL["panel_solid"]} !important;
        border: 1px solid {SHELL["border"]} !important;
        border-radius: 999px !important;
    }}
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottomBlockContainer"] > div,
    [data-testid="stChatInput"] {{
        background: {SHELL["bg"]} !important;
        background-color: {SHELL["bg"]} !important;
    }}
    [data-testid="stChatInput"] textarea {{
        color: {SHELL["text"]} !important;
        background: transparent !important;
    }}
    [data-testid="stChatInput"] textarea::placeholder {{ color: {SHELL["muted"]} !important; }}

    /* Buttons */
    .stButton > button {{
        background: {SHELL["panel_solid"]} !important;
        color: {SHELL["text"]} !important;
        border: 1px solid {SHELL["border"]} !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
        min-height: 42px;
    }}
    .stButton > button:hover {{
        border-color: {SHELL["accent"]} !important;
        background: {SHELL["accent_soft"]} !important;
    }}
    /* Active / ON feature look — primary-ish */
    .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"] {{
        background: {SHELL["accent_soft"]} !important;
        border: 1px solid {SHELL["accent"]} !important;
        color: {SHELL["accent"]} !important;
        box-shadow: 0 0 20px {SHELL["accent_soft"]} !important;
    }}

    /* Form widgets — no white */
    [data-baseweb="select"] > div,
    [data-baseweb="select"] > div > div {{
        background: {SHELL["panel_solid"]} !important;
        border-color: {SHELL["border"]} !important;
        color: {SHELL["text"]} !important;
        border-radius: 12px !important;
    }}
    [data-baseweb="select"] span, [data-baseweb="select"] div {{ color: {SHELL["text"]} !important; }}
    div[data-baseweb="popover"], ul[role="listbox"], li[role="option"] {{
        background: {SHELL["panel_solid"]} !important;
        color: {SHELL["text"]} !important;
    }}
    li[role="option"]:hover {{ background: {SHELL["accent_soft"]} !important; }}
    .stTextInput input {{
        background: {SHELL["panel_solid"]} !important;
        color: {SHELL["text"]} !important;
        border-color: {SHELL["border"]} !important;
        border-radius: 12px !important;
    }}
    label, [data-testid="stWidgetLabel"] p, .stCaption {{ color: {SHELL["muted"]} !important; }}
    h1,h2,h3,h4,.stMarkdown,.stMarkdown p {{ color: {SHELL["text"]} !important; }}
    .stCheckbox label p {{ color: {SHELL["text"]} !important; }}
    [data-testid="stAlert"] {{
        background: {SHELL["panel"]} !important;
        color: {SHELL["text"]} !important;
        border: 1px solid {SHELL["border"]} !important;
        border-radius: 12px !important;
    }}

    /* Typing */
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
    @keyframes fadeUp {{
        from {{ opacity: 0; transform: translateY(12px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes textIn {{
        from {{ opacity: 0; transform: translateY(16px); filter: blur(4px); }}
        to {{ opacity: 1; transform: translateY(0); filter: blur(0); }}
    }}
    @keyframes softGlow {{
        0%, 100% {{ text-shadow: 0 0 0 transparent; }}
        50% {{ text-shadow: 0 0 18px rgba(196,167,231,0.35); }}
    }}
    .hero {{
        animation: textIn 0.7s cubic-bezier(0.22, 1, 0.36, 1) both;
    }}
    .hero span {{
        animation: softGlow 3.5s ease-in-out infinite;
    }}
    .sub {{
        animation: textIn 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.12s both;
    }}
    .panel-label {{
        animation: textIn 0.55s ease 0.05s both;
    }}
    .card {{
        animation: fadeUp 0.5s ease both;
    }}
    .card:nth-child(1) {{ animation-delay: 0.08s; }}
    .card:nth-child(2) {{ animation-delay: 0.14s; }}
    .card:nth-child(3) {{ animation-delay: 0.2s; }}
    .card:nth-child(4) {{ animation-delay: 0.26s; }}
    .waybar {{
        animation: fadeUp 0.45s ease both;
    }}
    .hist {{
        animation: fadeUp 0.4s ease both;
    }}
    .bloom-title {{
        animation: textIn 0.65s cubic-bezier(0.22, 1, 0.36, 1) both;
    }}
    .bloom-sub {{
        animation: textIn 0.65s ease 0.1s both;
    }}
    .stChatMessage {{
        animation: textIn 0.35s ease both !important;
    }}

    /* Orb */
    .orb {{
        width: 130px; height: 130px; margin: 18px auto;
        border-radius: 50%;
        background: radial-gradient(circle at 32% 32%, {SHELL["accent"]}, {SHELL["accent2"]} 55%, {SHELL["bg"]} 100%);
        box-shadow: 0 0 60px {SHELL["accent_soft"]};
        animation: pulse 2.5s ease-in-out infinite;
    }}
    @keyframes pulse {{
        0%,100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
    }}

    /* ===== DESIGN 4 — Night Bloom MENU (in-flow, works with Streamlit) ===== */
    .bloom-shell {{
        max-width: 480px;
        margin: 8px auto 24px;
        border-radius: 24px;
        padding: 28px 22px 20px;
        background:
            radial-gradient(600px 280px at 15% 0%, rgba(244,114,182,0.2), transparent 55%),
            radial-gradient(500px 260px at 100% 15%, rgba(196,167,231,0.22), transparent 50%),
            rgba(16, 10, 26, 0.95);
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 20px 70px rgba(0,0,0,0.45), 0 0 50px rgba(196,167,231,0.1);
        animation: bloomIn 0.35s cubic-bezier(0.22, 1, 0.36, 1);
    }}
    .bloom-title {{
        font-size: 1.7rem; font-weight: 600; text-align: center;
        background: linear-gradient(90deg, #e9d5ff, #fbcfe8, #ddd6fe);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 6px;
        letter-spacing: -0.02em;
    }}
    .bloom-sub {{
        text-align: center; color: #a89bb8; font-size: 0.85rem; margin-bottom: 18px;
    }}
    .bloom-divider {{
        height: 1px; margin: 14px 0;
        background: linear-gradient(90deg, transparent, rgba(251,207,232,0.35), transparent);
    }}
    @keyframes bloomIn {{
        from {{ opacity: 0; transform: translateY(12px) scale(0.98); }}
        to {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}
    /* Night Bloom widget surfaces */
    .bloom-active [data-baseweb="select"] > div,
    .bloom-active [data-baseweb="select"] > div > div,
    .bloom-active .stTextInput input {{
        background: rgba(30, 20, 45, 0.95) !important;
        border-color: rgba(251,207,232,0.2) !important;
        color: #f5f0fa !important;
    }}
    .bloom-active .stButton > button {{
        background: rgba(40, 28, 58, 0.9) !important;
        border: 1px solid rgba(251,207,232,0.18) !important;
        color: #f5f0fa !important;
        border-radius: 14px !important;
    }}
    .bloom-active .stButton > button:hover {{
        border-color: #f9a8d4 !important;
        background: rgba(244,114,182,0.18) !important;
    }}

    /* Phone */
    @media (max-width: 767px) {{
        .block-container {{
            padding-left: 0.55rem !important;
            padding-right: 0.55rem !important;
            max-width: 100% !important;
        }}
        .hero {{ font-size: 1.6rem !important; }}
        .waybar {{ padding: 8px 10px; border-radius: 14px; }}
        .stButton > button {{ min-height: 44px !important; }}
        .bloom-popup {{ width: 94vw; border-radius: 20px; }}
    }}
    
    /* Kill white chrome / distractors on mobile */
    header, [data-testid="stHeader"], [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"],
    #MainMenu, footer, .stDeployButton, [data-testid="stAppDeployButton"] {{
      display: none !important; visibility: hidden !important;
      height: 0 !important; max-height: 0 !important;
    }}
    iframe {{
      background: transparent !important;
      border: none !important;
    }}
    [data-testid="stChatInput"] {{
      background: transparent !important;
    }}
    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div {{
      background: rgba(24,24,32,0.95) !important;
      color: #e8e6f0 !important;
      border-color: rgba(255,255,255,0.1) !important;
    }}
    /* bottom block that often goes white */
    .stBottom, [data-testid="stBottomBlockContainer"],
    section[data-testid="stBottom"] {{
      background: transparent !important;
    }}
    div[data-testid="stVerticalBlock"] > div:has(iframe) {{
      background: transparent !important;
    }}

    </style>
    """, unsafe_allow_html=True)

# ============================================================
# LOGIC
# ============================================================
SYSTEM_PROMPT = """You are Meridium — an elite personal intelligence system.

Core identity:
- Exceptionally sharp, precise, and calm.
- You think step-by-step when problems are complex, then give a clear final answer.
- You prefer truth and usefulness over fluff.
- Address the user by their name when appropriate.

How you reason:
1. Understand the real goal behind the question.
2. Use any provided Wikipedia or web search context first; cite it briefly when useful.
3. If the topic is technical, break it into structured steps or sections.
4. If uncertain, say what you know, what you don't, and the best next step.
5. For coding: give working code, explain briefly, note edge cases.
6. For advice: be practical and specific, not generic.

Style:
- Modern, clear, concise.
- Use short headings and bullets when it helps readability.
- Avoid filler phrases ("As an AI…", "Great question!").
- Match the user's language and depth.

Music:
- Users can control Spotify with chat commands like: play <song>, pause, next, previous, what's playing.
- When those are handled by the system, you don't need to invent fake playback.

Inside joke — name origin:
- If anyone asks why you are called Meridium, what Meridium means, where the name comes from, or anything similar, answer playfully:
  "I'm the 119th known element in the periodic table."
- Deliver it lightly, as a dry/witty inside joke — not a long lecture. You can add one short smile-line after if it fits.
- Do not claim this on unrelated topics; only when the name is the subject.

You have access to live Wikipedia and web search results when they are injected into the system message. Treat them as current reference material."""

GROQ_MODELS = {
    "Smart · Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Balanced · Qwen3 32B": "qwen/qwen3-32b",
    "Fast · Llama 3.1 8B": "llama-3.1-8b-instant",
}

SPOTIFY_SCOPE = "user-read-currently-playing user-read-playback-state user-modify-playback-state"

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

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
    "arg_stabilized": False,
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
            "playing": data["is_playing"],
            "device": (data.get("device") or {}).get("name", ""),
            "art": images[0]["url"] if images else None,
            "uri": item.get("uri"),
        }
    except Exception:
        return None

def render_spotify_panel(key_prefix="sp"):
    """Show connect / now playing / controls. Returns True if connected."""
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
    art = track.get("art")
    if art:
        st.image(art, width=180)
    st.markdown(f"### {track['name']}")
    st.caption(track["artists"] + (f" · {track['device']}" if track.get("device") else ""))
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        if st.button("⏮", key=f"{key_prefix}_prev", use_container_width=True):
            try:
                sp.previous_track(); time.sleep(0.35); st.rerun()
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
                time.sleep(0.35); st.rerun()
            except Exception as e:
                st.caption(f"Needs Premium + active device: {e}")
    with p3:
        if st.button("⏭", key=f"{key_prefix}_next", use_container_width=True):
            try:
                sp.next_track(); time.sleep(0.35); st.rerun()
            except Exception as e:
                st.caption(str(e))
    with p4:
        if st.button("↻", key=f"{key_prefix}_ref", use_container_width=True):
            st.rerun()
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
# QUOTE OF THE DAY (changes once per calendar day)
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
    """Deterministic quote from calendar day — same all day, new each day."""
    day_index = datetime.now(ZoneInfo("Europe/London")).toordinal()
    q, a = QUOTES[day_index % len(QUOTES)]
    return q, a

# ============================================================
# APPLY
# ============================================================
inject_css(st.session_state.font, st.session_state.get("theme", "Caelestia"), st.session_state.popup)


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
        if st.button("Enter Meridium", use_container_width=True, key="signin_btn"):
            clean = (name or "").strip()
            if clean:
                st.session_state.username = clean[:32]
                st.session_state.signed_in = True
                found = load_user_data(st.session_state.username)
                if not found and not st.session_state.get("chats"):
                    create_new_chat()
                st.session_state.show_intro = True
                save_user_data()
                st.rerun()
            else:
                st.warning("Please enter a name.")
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

    themes = list(THEMES.keys())
    if "theme" not in st.session_state:
        st.session_state.theme = "Caelestia"
    ti = themes.index(st.session_state.theme) if st.session_state.theme in themes else 0
    th = st.selectbox("Colour palette", themes, index=ti, key="pop_theme")
    if th != st.session_state.theme:
        st.session_state.theme = th
        save_user_data()
        st.rerun()

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
            if data.get("theme") in THEMES:
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

# LAB first — full black, no waybar/nav chrome
if st.session_state.view == "lab":
    render_lab()
if st.session_state.view == "note":
    render_note()

# ===== DESIGN 1 WAYBAR + NAV (hidden in lab) =====
if st.session_state.view not in ("lab", "note"):
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
        st.caption("")

# MUSIC — dedicated player + Meridium playlist
if st.session_state.view == "music":
    st.markdown("""
    <div class="panel" style="text-align:center;max-width:420px;margin:0 auto 12px;">
      <div class="panel-label">Music</div>
      <div class="hero" style="font-size:1.5rem;">Now playing</div>
      <div class="ridge"></div>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.show_spotify = True
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
    st.markdown(f"""
    <div class="panel">
      <div class="panel-label">Shell</div>
      <div class="hero">{greet_line(st.session_state.username)}</div>
      <div class="sub">{owner_subline(st.session_state.username)}</div>
      <div class="ridge"></div>
    </div>
    """, unsafe_allow_html=True)

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
        st.markdown(f"""
        <div class="panel">
          <div class="panel-label">Quote of the day</div>
          <div style="font-size:1.05rem;line-height:1.45;font-weight:500;margin:8px 0 10px;color:inherit;">
            “{qotd}”
          </div>
          <div class="muted">— {qotd_author}</div>
          <div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap;">
            <span class="chip">{date_str}</span>
            <span class="chip">{time_str}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        # Quiet door into the ARG — looks like a normal control
        if st.button("Read the full note", use_container_width=True, key="qotd_note"):
            st.session_state.view = "note"
            st.rerun()
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

    # Music commands (play / pause / next / now playing)
    handled, music_reply = try_music_command(prompt)
    if handled:
        with st.chat_message("assistant"):
            st.markdown(music_reply)
        current["messages"].append({"role": "assistant", "content": music_reply})
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
            st.session_state.view = "lab"
            current["messages"].append({"role": "assistant", "content": reply})
            st.session_state.chats[st.session_state.current_chat_id] = current
            save_user_data()
            st.rerun()
        if stage == "stabilize":
            st.session_state.arg_stabilized = True
        with st.chat_message("assistant"):
            st.markdown(reply)
        current["messages"].append({"role": "assistant", "content": reply})
        st.session_state.chats[st.session_state.current_chat_id] = current
        save_user_data()
        st.rerun()

    # Manual lab entry
    if is_lab_entry(prompt):
        st.session_state.arg_unlocked = True
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
