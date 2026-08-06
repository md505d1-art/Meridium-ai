import streamlit as st
import os
import re
import json
import time
import uuid
import hashlib
from pathlib import Path
from datetime import datetime
from openai import OpenAI
import wikipedia
from duckduckgo_search import DDGS
import spotipy
from spotipy.oauth2 import SpotifyOAuth

st.set_page_config(
    page_title="Meridium",
    page_icon="◈",
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
    payload = {
        "username": name,
        "font": st.session_state.get("font", "Inter"),
        "theme": st.session_state.get("theme", "Caelestia"),
        "provider": st.session_state.get("provider", "groq"),
        "model_name": st.session_state.get("model_name", "Smart · Llama 3.3 70B"),
        "show_widgets": st.session_state.get("show_widgets", True),
        "show_spotify": st.session_state.get("show_spotify", False),
        "use_wiki_toggle": st.session_state.get("use_wiki_toggle", True),
        "use_web_toggle": st.session_state.get("use_web_toggle", True),
        "chats": st.session_state.get("chats", {}),
        "current_chat_id": st.session_state.get("current_chat_id"),
        "saved_at": datetime.now().isoformat(),
    }
    try:
        _user_file(name).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

def load_user_data(username: str) -> bool:
    try:
        fp = _user_file(username)
        if not fp.exists():
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

def run_chat(messages, provider, model_name, api_key):
    client, err = make_client(provider, api_key)
    if err:
        return f"⚠️ {err}"
    if provider == "groq":
        model = GROQ_MODELS.get(model_name, "llama-3.3-70b-versatile")
        if model_name in GROQ_MODELS.values():
            model = model_name
    elif provider == "grok":
        model = "grok-4.5" if "4.5" in str(model_name) else "grok-3"
    else:
        model = model_name
    try:
        res = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.55,
            max_tokens=4096,
            top_p=0.9,
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def get_spotify():
    cid = st.secrets.get("SPOTIFY_CLIENT_ID", "") or os.getenv("SPOTIFY_CLIENT_ID", "")
    secret = st.secrets.get("SPOTIFY_CLIENT_SECRET", "") or os.getenv("SPOTIFY_CLIENT_SECRET", "")
    redirect = st.secrets.get("SPOTIFY_REDIRECT_URI", "http://localhost:8501")
    if not cid or not secret:
        return None
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=cid, client_secret=secret, redirect_uri=redirect,
        scope=SPOTIFY_SCOPE, cache_path=None, open_browser=False,
    ))

def current_track(sp):
    try:
        data = sp.current_playback()
        if not data or not data.get("item"):
            return None
        item = data["item"]
        return {
            "name": item["name"],
            "artists": ", ".join(a["name"] for a in item["artists"]),
            "playing": data["is_playing"],
        }
    except Exception:
        return None

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
# APPLY
# ============================================================
inject_css(st.session_state.font, st.session_state.get("theme", "Caelestia"), st.session_state.popup)
now = datetime.now()
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
    st.markdown(f"""
    <div style="position:fixed;inset:0;z-index:99999;display:flex;align-items:center;justify-content:center;
    background:#0c0c10;animation:introFade 2.3s ease forwards;">
      <div style="text-align:center;">
        <div style="font-size:0.72rem;letter-spacing:0.22em;text-transform:uppercase;color:#c4a7e7;margin-bottom:12px;">Meridium</div>
        <div style="font-size:1.9rem;font-weight:600;color:#e8e6f0;">Hello, <span style="color:#c4a7e7;">{user}</span></div>
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
      <div class="bloom-title">Hello, {st.session_state.username}</div>
      <div class="bloom-sub">Night Bloom · fonts · models · navigation</div>
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
        if st.button("✕  Close menu", use_container_width=True, key="pop_close"):
            st.session_state.popup = False
            st.rerun()
        if st.button("↩  Switch user", use_container_width=True, key="pop_signout"):
            st.session_state.signed_in = False
            st.session_state.username = ""
            st.session_state.show_intro = False
            st.session_state.popup = False
            st.rerun()

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

# ===== DESIGN 1 WAYBAR =====
st.markdown(f"""
<div class="waybar">
  <div class="waybar-left">
    <div class="logo-btn">◈</div>
    <span class="brand">Meridium</span>
    <span class="chip">{st.session_state.get("theme", "Caelestia")}</span>
    <span class="chip">{st.session_state.font}</span>
  </div>
  <div class="waybar-right">
    <span class="clock">{time_str}</span>
    <span class="muted">{date_str}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Nav
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
    if st.button("◎ Listen", use_container_width=True, key="n_listen"):
        st.session_state.view = "listen"
        st.rerun()
with n4:
    if st.button("☰ Menu", use_container_width=True, key="n_menu"):
        st.session_state.popup = True
        st.rerun()

# LISTEN
if st.session_state.view == "listen":
    st.markdown("""
    <div class="panel" style="text-align:center;">
      <div class="panel-label">Focus</div>
      <div style="color:#c4a7e7;margin-bottom:4px;">I'm listening…</div>
      <div class="orb"></div>
      <div class="muted">Caelestia calm · open chat when ready</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("💬 Open chat", use_container_width=True):
        st.session_state.view = "chat"
        st.rerun()
    st.stop()

# HOME — Design 1
if st.session_state.view == "home":
    st.markdown(f"""
    <div class="panel">
      <div class="panel-label">Shell</div>
      <div class="hero">Hello, <span>{st.session_state.username}</span></div>
      <div class="sub">Meridium · personal intelligence · Caelestia shell</div>
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

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="panel"><div class="panel-label">Status</div>', unsafe_allow_html=True)
        if st.session_state.show_widgets:
            st.markdown(f'<div style="display:flex;gap:8px;flex-wrap:wrap;"><span class="chip">{time_str}</span><span class="chip">{date_str}</span></div>', unsafe_allow_html=True)
        st.caption(f"Font · {st.session_state.font}")
        st.caption(f"Model · {st.session_state.model_name}")
        st.caption(f"Wiki {'on' if use_wiki else 'off'} · Web {'on' if use_web else 'off'}")
        if st.session_state.show_spotify:
            sp = get_spotify()
            track = current_track(sp) if sp else None
            if track:
                st.info(f"♫ {track['name']} — {track['artists']}")
            else:
                st.caption("♫ Spotify ready")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel"><div class="panel-label">Chat history</div>', unsafe_allow_html=True)
        for cid, data in sorted(st.session_state.chats.items(), key=lambda x: x[1].get("created", ""), reverse=True)[:8]:
            cols = st.columns([4, 1, 1])
            with cols[0]:
                st.markdown(f'<div class="hist"><div class="hist-ico">💬</div><div class="hist-t">{data.get("title","Untitled")}</div></div>', unsafe_allow_html=True)
            with cols[1]:
                if st.button("→", key=f"h_{cid}", help="Open"):
                    st.session_state.current_chat_id = cid
                    st.session_state.view = "chat"
                    save_user_data()
                    st.rerun()
            with cols[2]:
                if st.button("🗑", key=f"hd_{cid}", help="Delete"):
                    delete_chat(cid)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# CHAT
if st.session_state.current_chat_id not in st.session_state.chats:
    create_new_chat()
current = st.session_state.chats[st.session_state.current_chat_id]

st.markdown('<div class="panel"><div class="panel-label">Conversation</div><div class="ridge"></div>', unsafe_allow_html=True)

if st.session_state.show_spotify:
    sp = get_spotify()
    track = current_track(sp) if sp else None
    if track:
        st.caption(f"♫ {track['name']} — {track['artists']}")
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            if st.button("⏮", key="sp_prev", use_container_width=True):
                try:
                    sp.previous_track(); time.sleep(0.25); st.rerun()
                except Exception:
                    pass
        with p2:
            icon = "⏸" if track["playing"] else "▶"
            if st.button(icon, key="sp_play", use_container_width=True):
                try:
                    if track["playing"]:
                        sp.pause_playback()
                    else:
                        sp.start_playback()
                    time.sleep(0.25); st.rerun()
                except Exception:
                    pass
        with p3:
            if st.button("⏭", key="sp_next", use_container_width=True):
                try:
                    sp.next_track(); time.sleep(0.25); st.rerun()
                except Exception:
                    pass
        with p4:
            if st.button("↻", key="sp_ref", use_container_width=True):
                st.rerun()

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
    if len([m for m in current["messages"] if m["role"] == "user"]) == 1:
        update_chat_title(st.session_state.current_chat_id, prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    user_name = st.session_state.get("username") or "user"
    messages = [{"role": "system", "content": SYSTEM_PROMPT + f"\n\nThe user's name is {user_name}. Greet and address them as {user_name} when appropriate."}]
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
        time.sleep(1.0)
        reply = run_chat(messages, provider, model_name, api_key)
        typing.markdown(reply)

    ok, reply_mod = moderate_text(reply)
    if not ok:
        reply = reply_mod
    current["messages"].append({"role": "assistant", "content": reply})
    save_user_data()
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
