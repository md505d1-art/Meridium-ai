import streamlit as st
import os
import time
import uuid
from datetime import datetime
from openai import OpenAI
import wikipedia
from duckduckgo_search import DDGS
import spotipy
from spotipy.oauth2 import SpotifyOAuth

st.set_page_config(
    page_title="Meridium",
    page_icon="◈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# COLOR PALETTES — same glass UI, different colors
# ============================================================
THEMES = {
    "Violet": {
        "bg": "linear-gradient(165deg, #0b0614 0%, #160e28 40%, #0d0818 100%)",
        "bg_solid": "#0d0818",
        "text": "#f2eefc",
        "muted": "#9ca3af",
        "accent": "#a78bfa",
        "accent2": "#7c3aed",
        "accent_soft": "rgba(167,139,250,0.15)",
        "accent_border": "rgba(167,139,250,0.35)",
        "glass": "rgba(255,255,255,0.05)",
        "glass_border": "rgba(255,255,255,0.08)",
        "chip_text": "#c4b5fd",
        "tagline": "#ddd6fe",
        "orb": "radial-gradient(circle at 35% 35%, #c4b5fd, #7c3aed 55%, #2e1065 100%)",
        "orb_glow": "rgba(124, 58, 237, 0.55)",
        "mode": "dark",
    },
    "Peach": {
        "bg": "linear-gradient(165deg, #1a1010 0%, #2a1814 40%, #140e0c 100%)",
        "bg_solid": "#140e0c",
        "text": "#faf0eb",
        "muted": "#a89088",
        "accent": "#ff9f7a",
        "accent2": "#e87a5a",
        "accent_soft": "rgba(255,159,122,0.15)",
        "accent_border": "rgba(255,159,122,0.35)",
        "glass": "rgba(255,255,255,0.05)",
        "glass_border": "rgba(255,200,180,0.1)",
        "chip_text": "#ffc4a8",
        "tagline": "#f5d5c8",
        "orb": "radial-gradient(circle at 35% 35%, #ffc4a8, #ff9f7a 55%, #5c2a1a 100%)",
        "orb_glow": "rgba(255, 159, 122, 0.5)",
        "mode": "dark",
    },
    "Lavender": {
        "bg": "linear-gradient(165deg, #120e1a 0%, #1c1628 40%, #0e0a14 100%)",
        "bg_solid": "#0e0a14",
        "text": "#f3eefc",
        "muted": "#9a90b0",
        "accent": "#c4b5fd",
        "accent2": "#a78bfa",
        "accent_soft": "rgba(196,181,253,0.15)",
        "accent_border": "rgba(196,181,253,0.35)",
        "glass": "rgba(255,255,255,0.05)",
        "glass_border": "rgba(200,180,255,0.1)",
        "chip_text": "#ddd6fe",
        "tagline": "#e9e5f8",
        "orb": "radial-gradient(circle at 35% 35%, #ddd6fe, #c4b5fd 55%, #3b0764 100%)",
        "orb_glow": "rgba(196, 181, 253, 0.55)",
        "mode": "dark",
    },
    "Mint": {
        "bg": "linear-gradient(165deg, #0a1210 0%, #0f1c18 40%, #081210 100%)",
        "bg_solid": "#081210",
        "text": "#e8f5f0",
        "muted": "#7a9a90",
        "accent": "#5eead4",
        "accent2": "#2dd4bf",
        "accent_soft": "rgba(94,234,212,0.12)",
        "accent_border": "rgba(94,234,212,0.35)",
        "glass": "rgba(255,255,255,0.05)",
        "glass_border": "rgba(150,255,220,0.1)",
        "chip_text": "#99f6e4",
        "tagline": "#ccfbf1",
        "orb": "radial-gradient(circle at 35% 35%, #99f6e4, #5eead4 55%, #134e4a 100%)",
        "orb_glow": "rgba(94, 234, 212, 0.5)",
        "mode": "dark",
    },
    "Ocean": {
        "bg": "linear-gradient(165deg, #061018 0%, #0c1a28 40%, #050e14 100%)",
        "bg_solid": "#050e14",
        "text": "#e8f4fc",
        "muted": "#7a9ab0",
        "accent": "#38bdf8",
        "accent2": "#0ea5e9",
        "accent_soft": "rgba(56,189,248,0.12)",
        "accent_border": "rgba(56,189,248,0.35)",
        "glass": "rgba(255,255,255,0.05)",
        "glass_border": "rgba(100,200,255,0.1)",
        "chip_text": "#7dd3fc",
        "tagline": "#bae6fd",
        "orb": "radial-gradient(circle at 35% 35%, #7dd3fc, #38bdf8 55%, #0c4a6e 100%)",
        "orb_glow": "rgba(56, 189, 248, 0.5)",
        "mode": "dark",
    },
    "Rose": {
        "bg": "linear-gradient(165deg, #160a10 0%, #241018 40%, #10080c 100%)",
        "bg_solid": "#10080c",
        "text": "#fdf2f8",
        "muted": "#a08090",
        "accent": "#f472b6",
        "accent2": "#ec4899",
        "accent_soft": "rgba(244,114,182,0.14)",
        "accent_border": "rgba(244,114,182,0.35)",
        "glass": "rgba(255,255,255,0.05)",
        "glass_border": "rgba(255,150,200,0.1)",
        "chip_text": "#f9a8d4",
        "tagline": "#fbcfe8",
        "orb": "radial-gradient(circle at 35% 35%, #f9a8d4, #f472b6 55%, #831843 100%)",
        "orb_glow": "rgba(244, 114, 182, 0.5)",
        "mode": "dark",
    },
    "Soft Dark": {
        "bg": "linear-gradient(165deg, #0c0c10 0%, #141418 40%, #0a0a0c 100%)",
        "bg_solid": "#0a0a0c",
        "text": "#f0f0f4",
        "muted": "#8b8b9a",
        "accent": "#a1a1aa",
        "accent2": "#71717a",
        "accent_soft": "rgba(161,161,170,0.12)",
        "accent_border": "rgba(161,161,170,0.3)",
        "glass": "rgba(255,255,255,0.04)",
        "glass_border": "rgba(255,255,255,0.08)",
        "chip_text": "#d4d4d8",
        "tagline": "#e4e4e7",
        "orb": "radial-gradient(circle at 35% 35%, #d4d4d8, #a1a1aa 55%, #27272a 100%)",
        "orb_glow": "rgba(161, 161, 170, 0.4)",
        "mode": "dark",
    },
    "Cloud": {
        "bg": "linear-gradient(165deg, #f4f5f9 0%, #e8eaf2 50%, #f0f1f6 100%)",
        "bg_solid": "#eef0f5",
        "text": "#1a1a22",
        "muted": "#6b6b7b",
        "accent": "#7c6cf0",
        "accent2": "#6c5ce7",
        "accent_soft": "rgba(124,108,240,0.12)",
        "accent_border": "rgba(124,108,240,0.3)",
        "glass": "rgba(255,255,255,0.7)",
        "glass_border": "rgba(0,0,0,0.06)",
        "chip_text": "#5b4cdb",
        "tagline": "#3f3f50",
        "orb": "radial-gradient(circle at 35% 35%, #c4b5fd, #7c6cf0 55%, #4c1d95 100%)",
        "orb_glow": "rgba(124, 108, 240, 0.35)",
        "mode": "light",
    },
    "Newspaper": {
        "bg": "linear-gradient(165deg, #f7f4ef 0%, #efeae2 50%, #f5f2eb 100%)",
        "bg_solid": "#f0ebe3",
        "text": "#1a1a1a",
        "muted": "#5c5c5c",
        "accent": "#333333",
        "accent2": "#111111",
        "accent_soft": "rgba(0,0,0,0.06)",
        "accent_border": "rgba(0,0,0,0.15)",
        "glass": "rgba(255,255,255,0.85)",
        "glass_border": "rgba(0,0,0,0.08)",
        "chip_text": "#333333",
        "tagline": "#2a2a2a",
        "orb": "radial-gradient(circle at 35% 35%, #d6d0c4, #8a8580 55%, #3a3a3a 100%)",
        "orb_glow": "rgba(0,0,0,0.2)",
        "mode": "light",
    },
}

def inject_css(theme_name: str = "Violet"):
    t = THEMES.get(theme_name, THEMES["Violet"])
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    }}

    .stApp {{
        background: {t["bg"]};
        color: {t["text"]};
    }}

    /* Override Streamlit default light surfaces everywhere */
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {{
        background: transparent !important;
        background-color: transparent !important;
    }}
    .stApp, .main, .block-container {{
        color: {t["text"]} !important;
    }}
    /* Force all baseweb controls dark */
    [data-baseweb="select"] > div,
    [data-baseweb="select"] > div > div {{
        background-color: {t["bg_solid"]} !important;
        border-color: {t["glass_border"]} !important;
    }}
    [data-baseweb="popover"] > div,
    [data-baseweb="popover"] ul,
    [role="listbox"] {{
        background-color: {t["bg_solid"]} !important;
        color: {t["text"]} !important;
    }}
    [role="option"] {{
        background-color: {t["bg_solid"]} !important;
        color: {t["text"]} !important;
    }}
    [role="option"]:hover, [role="option"][aria-selected="true"] {{
        background-color: {t["accent_soft"]} !important;
    }}
    /* Streamlit secondary / default button variants */
    button[kind="secondary"],
    button[kind="primary"],
    button[data-testid="baseButton-secondary"],
    button[data-testid="baseButton-primary"],
    button[data-testid="baseButton-secondaryFormSubmit"] {{
        background-color: {t["glass"]} !important;
        background: {t["glass"]} !important;
        color: {t["text"]} !important;
        border: 1px solid {t["glass_border"]} !important;
    }}


    #MainMenu, footer, header, .stDeployButton {{
        display: none !important;
    }}
    section[data-testid="stSidebar"] {{
        display: none !important;
    }}

    .glass {{
        background: {t["glass"]};
        border: 1px solid {t["glass_border"]};
        border-radius: 20px;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    }}

    .home-wrap {{
        max-width: 420px;
        margin: 0 auto;
        padding: 12px 8px 40px;
        animation: fadeUp 0.55s ease both;
    }}
    .top-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 28px;
    }}
    .avatar-pill {{
        width: 40px; height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, {t["accent"]}, {t["accent2"]});
        display: flex; align-items: center; justify-content: center;
        font-size: 1.1rem;
        box-shadow: 0 4px 16px {t["orb_glow"]};
        color: #fff;
    }}
    .premium-chip {{
        background: {t["accent_soft"]};
        border: 1px solid {t["accent_border"]};
        color: {t["chip_text"]};
        padding: 8px 14px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 500;
    }}
    .hello {{
        font-size: 1.75rem;
        font-weight: 700;
        line-height: 1.25;
        margin: 0 0 6px;
        letter-spacing: -0.03em;
        color: {t["text"]};
        animation: fadeUp 0.6s ease 0.08s both;
    }}
    .hello span {{ color: {t["chip_text"]}; }}
    .tagline {{
        font-size: 1.35rem;
        font-weight: 600;
        color: {t["tagline"]};
        margin: 0 0 22px;
        animation: fadeUp 0.6s ease 0.14s both;
    }}

    .feat-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin: 18px 0 22px;
    }}
    .feat-card {{
        background: {t["glass"]};
        border: 1px solid {t["glass_border"]};
        border-radius: 18px;
        padding: 18px 14px;
        min-height: 100px;
        transition: transform 0.2s ease, border-color 0.2s;
        animation: fadeUp 0.55s ease both;
    }}
    .feat-card:hover {{
        transform: translateY(-3px);
        border-color: {t["accent_border"]};
    }}
    .feat-icon {{
        font-size: 1.35rem;
        margin-bottom: 10px;
        display: block;
        color: {t["accent"]};
    }}
    .feat-title {{
        font-size: 0.92rem;
        font-weight: 600;
        color: {t["text"]};
    }}
    .feat-sub {{
        font-size: 0.75rem;
        color: {t["muted"]};
        margin-top: 4px;
    }}

    .hist-title {{
        font-size: 0.85rem;
        font-weight: 600;
        color: {t["muted"]};
        margin: 8px 0 12px;
        letter-spacing: 0.02em;
    }}
    .hist-item {{
        background: {t["glass"]};
        border: 1px solid {t["glass_border"]};
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 12px;
        animation: fadeUp 0.5s ease both;
    }}
    .hist-icon {{
        width: 36px; height: 36px;
        border-radius: 10px;
        background: {t["accent_soft"]};
        display: flex; align-items: center; justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
        color: {t["accent"]};
    }}
    .hist-text {{
        flex: 1;
        font-size: 0.88rem;
        color: {t["text"]};
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .chat-top {{
        text-align: center;
        padding: 8px 0 12px;
        font-weight: 600;
        font-size: 1.05rem;
        color: {t["text"]};
        animation: fadeUp 0.4s ease both;
    }}
    .stChatMessage {{
        background: {t["glass"]} !important;
        border: 1px solid {t["glass_border"]} !important;
        border-radius: 18px !important;
        padding: 12px 16px !important;
        margin-bottom: 10px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
        animation: bubbleIn 0.35s ease both;
        color: {t["text"]} !important;
    }}
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"],
    [data-testid="stChatAvatar"] {{
        display: none !important;
    }}

    /* Chat input — remove white bar */
    .stChatInput > div {{
        background: {t["glass"]} !important;
        border: 1px solid {t["accent_border"]} !important;
        border-radius: 999px !important;
        box-shadow: 0 4px 24px rgba(0,0,0,0.15);
    }}
    .stChatInput,
    [data-testid="stChatInput"] {{
        background: transparent !important;
        background-color: transparent !important;
    }}
    .stChatInput textarea,
    .stChatInput input,
    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInput"] input {{
        background: transparent !important;
        color: {t["text"]} !important;
        caret-color: {t["accent"]} !important;
    }}
    div[data-testid="stBottomBlockContainer"],
    [data-testid="stBottom"],
    .stBottom {{
        background: {t["bg_solid"]} !important;
        background-color: {t["bg_solid"]} !important;
        border: none !important;
        box-shadow: none !important;
    }}
    .stApp [data-testid="stBottomBlockContainer"] {{
        background: {t["bg_solid"]} !important;
        background-color: {t["bg_solid"]} !important;
    }}
    [data-testid="stChatInputSubmitButton"] {{
        background: {t["accent_soft"]} !important;
        color: {t["text"]} !important;
        border: 1px solid {t["accent_border"]} !important;
        border-radius: 999px !important;
    }}
    /* Placeholder colour */
    .stChatInput textarea::placeholder,
    [data-testid="stChatInput"] textarea::placeholder {{
        color: {t["muted"]} !important;
        opacity: 0.8;
    }}

    /* ===== Buttons ===== */
    .stButton > button {{
        background: {t["glass"]} !important;
        color: {t["text"]} !important;
        border: 1px solid {t["glass_border"]} !important;
        border-radius: 999px !important;
        font-weight: 500 !important;
        transition: all 0.18s ease !important;
    }}
    .stButton > button:hover {{
        background: {t["accent_soft"]} !important;
        border-color: {t["accent_border"]} !important;
        transform: translateY(-1px);
    }}
    .stButton > button:active {{
        transform: scale(0.97);
    }}

    /* ===== Selectboxes / dropdowns (kill white) ===== */
    div[data-baseweb="select"] > div {{
        background-color: {t["bg_solid"]} !important;
        background: {t["glass"]} !important;
        border-color: {t["glass_border"]} !important;
        color: {t["text"]} !important;
        border-radius: 14px !important;
    }}
    div[data-baseweb="select"] * {{
        color: {t["text"]} !important;
    }}
    /* Dropdown popover menu */
    div[data-baseweb="popover"] {{
        background-color: {t["bg_solid"]} !important;
    }}
    ul[data-baseweb="menu"] {{
        background-color: {t["bg_solid"]} !important;
        border: 1px solid {t["glass_border"]} !important;
        border-radius: 12px !important;
    }}
    ul[data-baseweb="menu"] li {{
        background-color: {t["bg_solid"]} !important;
        color: {t["text"]} !important;
    }}
    ul[data-baseweb="menu"] li:hover {{
        background-color: {t["accent_soft"]} !important;
    }}
    /* Text inputs */
    .stTextInput input, .stTextInput > div > div > input,
    [data-testid="stTextInput"] input {{
        background-color: {t["bg_solid"]} !important;
        background: {t["glass"]} !important;
        color: {t["text"]} !important;
        border: 1px solid {t["glass_border"]} !important;
        border-radius: 14px !important;
    }}
    .stTextInput > div > div {{
        background-color: transparent !important;
        border-color: {t["glass_border"]} !important;
    }}
    /* Labels & captions */
    label, .stSelectbox label, .stTextInput label,
    [data-testid="stWidgetLabel"] p {{
        color: {t["muted"]} !important;
    }}
    .stCaption, [data-testid="stCaptionContainer"] {{
        color: {t["muted"]} !important;
    }}
    /* Checkboxes */
    .stCheckbox label p {{
        color: {t["text"]} !important;
    }}
    /* Info / alert boxes */
    [data-testid="stAlert"] {{
        background: {t["glass"]} !important;
        color: {t["text"]} !important;
        border: 1px solid {t["glass_border"]} !important;
        border-radius: 14px !important;
    }}
    /* Markdown headings in menu */
    h1, h2, h3, h4 {{
        color: {t["text"]} !important;
    }}
    /* Number input / generic widgets */
    [data-baseweb="input"] {{
        background-color: {t["bg_solid"]} !important;
    }}
    [data-baseweb="input"] input {{
        color: {t["text"]} !important;
    }}


    .orb-wrap {{
        text-align: center;
        padding: 28px 12px;
        animation: fadeUp 0.5s ease both;
    }}
    .orb {{
        width: 140px; height: 140px;
        margin: 12px auto 18px;
        border-radius: 50%;
        background: {t["orb"]};
        box-shadow: 0 0 60px {t["orb_glow"]}, inset 0 0 30px rgba(255,255,255,0.15);
        animation: orbPulse 2.4s ease-in-out infinite;
    }}
    @keyframes orbPulse {{
        0%, 100% {{ transform: scale(1); box-shadow: 0 0 50px {t["orb_glow"]}; }}
        50% {{ transform: scale(1.06); box-shadow: 0 0 80px {t["orb_glow"]}; }}
    }}
    .listen-label {{
        color: {t["chip_text"]};
        font-size: 1.05rem;
        font-weight: 500;
        margin-bottom: 8px;
    }}
    .listen-quote {{
        color: {t["muted"]};
        font-size: 0.9rem;
        max-width: 280px;
        margin: 0 auto;
        line-height: 1.45;
    }}

    .time-chip {{
        display: inline-flex;
        gap: 16px;
        justify-content: center;
        width: 100%;
        margin: 8px 0 16px;
    }}
    .time-chip span {{
        background: {t["glass"]};
        border: 1px solid {t["glass_border"]};
        border-radius: 14px;
        padding: 10px 18px;
        font-size: 0.95rem;
        font-weight: 600;
        color: {t["text"]};
    }}

    @keyframes fadeUp {{
        from {{ opacity: 0; transform: translateY(14px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes bubbleIn {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Typing indicator — 3 bouncing dots */
    .typing-wrap {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 2px;
    }}
    .typing-wrap .dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: {t["accent"]};
        animation: typingBounce 1.2s ease-in-out infinite;
    }}
    .typing-wrap .dot:nth-child(2) {{ animation-delay: 0.15s; }}
    .typing-wrap .dot:nth-child(3) {{ animation-delay: 0.3s; }}
    @keyframes typingBounce {{
        0%, 60%, 100% {{ transform: translateY(0); opacity: 0.45; }}
        30% {{ transform: translateY(-7px); opacity: 1; }}
    }}

    @media (max-width: 480px) {{
        .hello {{ font-size: 1.5rem; }}
        .tagline {{ font-size: 1.15rem; }}
        .home-wrap {{ padding: 8px 4px 32px; }}
    }}

    {" .stMarkdown, .stMarkdown p, .stCaption, label, p {{ color: " + t["text"] + " !important; }} " if t["mode"] == "light" else ""}
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# CONFIG
# ============================================================
SYSTEM_PROMPT = """You are Meridium, a highly capable personal AI assistant.
You are intelligent, precise, calm and modern.
You solve problems clearly and effectively.
You can use Wikipedia knowledge and web search results when relevant.
Be helpful, structured and insightful. Avoid fluff.
Address the user respectfully as Master when appropriate."""

GROQ_MODELS = {
    "Smart · Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Balanced · Qwen3 32B": "qwen/qwen3-32b",
    "Fast · Llama 3.1 8B": "llama-3.1-8b-instant",
}
SPOTIFY_SCOPE = "user-read-currently-playing user-read-playback-state user-modify-playback-state"

# ============================================================
# STATE
# ============================================================
defaults = {
    "view": "home",          # home | chat | menu | listen
    "theme": "Violet",
    "chats": {},
    "current_chat_id": None,
    "show_widgets": True,
    "show_spotify": False,
    "show_intro": True,
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

# ============================================================
# HELPERS
# ============================================================
def get_wiki(query: str, sentences: int = 3) -> str:
    try:
        wikipedia.set_lang("en")
        results = wikipedia.search(query, results=3)
        if not results:
            return ""
        title = results[0]
        summary = wikipedia.summary(title, sentences=sentences, auto_suggest=False)
        return f"**{title}**\n\n{summary}"
    except Exception:
        return ""

def get_web_search(query: str, max_results: int = 5) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return ""
        lines = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            body = r.get("body", "")
            href = r.get("href", "")
            lines.append(f"{i}. **{title}**\n{body}\nSource: {href}")
        return "\n\n".join(lines)
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
        # if stored value is already an API id
        if model_name in GROQ_MODELS.values():
            model = model_name
    elif provider == "grok":
        model = "grok-4.5" if "4.5" in str(model_name) else "grok-3"
    else:
        model = model_name
    try:
        res = client.chat.completions.create(
            model=model, messages=messages, temperature=0.7, max_tokens=2048
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
    auth = SpotifyOAuth(
        client_id=cid, client_secret=secret, redirect_uri=redirect,
        scope=SPOTIFY_SCOPE, cache_path=None, open_browser=False,
    )
    return spotipy.Spotify(auth_manager=auth)

def current_track(sp):
    try:
        data = sp.current_playback()
        if not data or not data.get("item"):
            return None
        item = data["item"]
        return {
            "name": item["name"],
            "artists": ", ".join(a["name"] for a in item["artists"]),
            "art": item["album"]["images"][0]["url"] if item["album"]["images"] else None,
            "playing": data["is_playing"],
            "device": data.get("device", {}).get("name", ""),
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

def update_chat_title(chat_id, first_message):
    title = first_message.strip()
    if len(title) > 40:
        title = title[:40] + "…"
    st.session_state.chats[chat_id]["title"] = title

# ============================================================
# APPLY
# ============================================================
inject_css(st.session_state.get("theme", "Violet"))
now = datetime.now()
time_str = now.strftime("%H:%M")
date_str = now.strftime("%a · %b %d")

provider = st.session_state.provider
model_name = st.session_state.model_name
api_key = st.session_state.api_key_val
use_wiki = st.session_state.use_wiki_toggle
use_web = st.session_state.use_web_toggle

# ============================================================
# INTRO
# ============================================================
if st.session_state.show_intro:
    _t = THEMES.get(st.session_state.get("theme", "Violet"), THEMES["Violet"])
    st.markdown(f"""
    <div style="position:fixed;inset:0;z-index:99999;display:flex;align-items:center;
    justify-content:center;background:{_t["bg_solid"]};animation:introFade 2.5s ease forwards;">
        <div style="font-size:1.85rem;font-weight:600;color:{_t["text"]};animation:fadeUp 1.2s ease forwards;">
            Hello, <span style="color:{_t["chip_text"]};">Master</span>
        </div>
    </div>
    <style>
    @keyframes introFade {{
        0%, 65% {{ opacity: 1; pointer-events: all; }}
        100% {{ opacity: 0; pointer-events: none; }}
    }}
    </style>
    """, unsafe_allow_html=True)
    time.sleep(2.4)
    st.session_state.show_intro = False
    st.rerun()

# ============================================================
# TOP BAR (always)
# ============================================================
b1, b2, b3 = st.columns([1, 3, 1])
with b1:
    if st.button("◈", key="nav_logo", help="Menu"):
        st.session_state.view = "menu" if st.session_state.view != "menu" else "home"
        st.rerun()
with b3:
    if st.session_state.view != "home":
        if st.button("⌂", key="nav_home", help="Home"):
            st.session_state.view = "home"
            st.rerun()

# ============================================================
# MENU
# ============================================================
if st.session_state.view == "menu":
    st.markdown('<div class="home-wrap">', unsafe_allow_html=True)
    st.markdown("### Menu")
    st.caption("Navigate · Widgets · Settings")

    theme_opts = list(THEMES.keys())
    cur = st.session_state.get("theme", "Violet")
    picked = st.selectbox(
        "Colour palette",
        theme_opts,
        index=theme_opts.index(cur) if cur in theme_opts else 0,
        key="theme_pick",
    )
    if picked != st.session_state.theme:
        st.session_state.theme = picked
        st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⌂  Home", use_container_width=True, key="m_home"):
            st.session_state.view = "home"
            st.rerun()
        if st.button("💬  Chat", use_container_width=True, key="m_chat"):
            st.session_state.view = "chat"
            st.rerun()
        if st.button("＋  New chat", use_container_width=True, key="m_new"):
            create_new_chat()
            st.session_state.view = "chat"
            st.rerun()
        if st.button("◎  Listen", use_container_width=True, key="m_listen"):
            st.session_state.view = "listen"
            st.rerun()
    with c2:
        tl = "🕒  Time ON" if st.session_state.show_widgets else "🕒  Time OFF"
        if st.button(tl, use_container_width=True, key="m_time"):
            st.session_state.show_widgets = not st.session_state.show_widgets
            st.rerun()
        ml = "♫  Music ON" if st.session_state.show_spotify else "♫  Music OFF"
        if st.button(ml, use_container_width=True, key="m_music"):
            st.session_state.show_spotify = not st.session_state.show_spotify
            st.rerun()
        if st.button("✕  Close", use_container_width=True, key="m_close"):
            st.session_state.view = "home"
            st.rerun()

    st.markdown("---")
    st.markdown("**Model**")
    st.session_state.provider = st.selectbox(
        "Provider", ["groq", "grok", "openrouter"],
        index=["groq", "grok", "openrouter"].index(st.session_state.provider)
        if st.session_state.provider in ["groq", "grok", "openrouter"] else 0,
        key="menu_prov",
    )
    if st.session_state.provider == "groq":
        opts = list(GROQ_MODELS.keys())
    elif st.session_state.provider == "grok":
        opts = ["Grok 4.5", "Grok 4.3"]
    else:
        opts = ["meta-llama/llama-3.3-70b-instruct:free", "qwen/qwen3-32b:free"]
    _mi = opts.index(st.session_state.model_name) if st.session_state.model_name in opts else 0
    st.session_state.model_name = st.selectbox("Model", opts, index=_mi, key="menu_model")

    st.session_state.api_key_val = st.text_input(
        "API Key (optional)", type="password",
        value=st.session_state.api_key_val, key="menu_key",
    )
    st.session_state.use_wiki_toggle = st.checkbox("Wikipedia", value=st.session_state.use_wiki_toggle)
    st.session_state.use_web_toggle = st.checkbox("Web search", value=st.session_state.use_web_toggle)

    st.markdown("---")
    st.markdown("**Chats**")
    for cid, data in sorted(st.session_state.chats.items(), key=lambda x: x[1].get("created", ""), reverse=True)[:10]:
        if st.button(data.get("title", "Untitled"), key=f"mc_{cid}", use_container_width=True):
            st.session_state.current_chat_id = cid
            st.session_state.view = "chat"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ============================================================
# LISTEN VIEW (orb)
# ============================================================
if st.session_state.view == "listen":
    st.markdown("""
    <div class="orb-wrap">
        <div class="listen-label">I'm listening…</div>
        <div class="orb"></div>
        <div class="listen-quote">Tap below to open chat and speak with Meridium.</div>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("💬  Start chatting", use_container_width=True, key="listen_chat"):
            st.session_state.view = "chat"
            st.rerun()
        if st.button("⌂  Home", use_container_width=True, key="listen_home"):
            st.session_state.view = "home"
            st.rerun()
    st.stop()

# ============================================================
# HOME
# ============================================================
if st.session_state.view == "home":
    st.markdown('<div class="home-wrap">', unsafe_allow_html=True)

    st.markdown("""
    <div class="top-row">
        <div class="avatar-pill">◈</div>
        <div class="premium-chip">✦ Meridium</div>
    </div>
    <div class="hello">Hello, <span>Master</span></div>
    <div class="tagline">Make anything you imagine.</div>
    """, unsafe_allow_html=True)

    if st.session_state.show_widgets:
        st.markdown(f"""
        <div class="time-chip">
            <span>{time_str}</span>
            <span>{date_str}</span>
        </div>
        """, unsafe_allow_html=True)

    # Primary actions
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        if st.button("Start chat", use_container_width=True, key="h_chat"):
            st.session_state.view = "chat"
            st.rerun()
    with a2:
        if st.button("＋ New", use_container_width=True, key="h_new"):
            create_new_chat()
            st.session_state.view = "chat"
            st.rerun()
    with a3:
        if st.button("◎ Listen", use_container_width=True, key="h_listen"):
            st.session_state.view = "listen"
            st.rerun()
    with a4:
        if st.button("☰ Menu", use_container_width=True, key="h_menu"):
            st.session_state.view = "menu"
            st.rerun()

    # Feature cards
    st.markdown("""
    <div class="feat-grid">
        <div class="feat-card" style="animation-delay:0.1s">
            <span class="feat-icon">✧</span>
            <div class="feat-title">Smart chat</div>
            <div class="feat-sub">Powerful free models</div>
        </div>
        <div class="feat-card" style="animation-delay:0.18s">
            <span class="feat-icon">◈</span>
            <div class="feat-title">Web + Wiki</div>
            <div class="feat-sub">Live knowledge</div>
        </div>
        <div class="feat-card" style="animation-delay:0.26s">
            <span class="feat-icon">♫</span>
            <div class="feat-title">Music</div>
            <div class="feat-sub">Spotify controls</div>
        </div>
        <div class="feat-card" style="animation-delay:0.34s">
            <span class="feat-icon">◎</span>
            <div class="feat-title">Listen mode</div>
            <div class="feat-sub">Focus & calm</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Spotify strip
    if st.session_state.show_spotify:
        sp = get_spotify()
        track = current_track(sp) if sp else None
        if track:
            st.info(f"♫  **{track['name']}** — {track['artists']}")
        else:
            st.caption("♫  Music on — connect Spotify in Secrets to control playback")

    # Chat history
    st.markdown('<div class="hist-title">Chat history</div>', unsafe_allow_html=True)
    sorted_chats = sorted(
        st.session_state.chats.items(),
        key=lambda x: x[1].get("created", ""),
        reverse=True,
    )
    for i, (cid, data) in enumerate(sorted_chats[:6]):
        title = data.get("title", "Untitled")
        cols = st.columns([5, 1])
        with cols[0]:
            st.markdown(f"""
            <div class="hist-item" style="animation-delay:{0.1 + i * 0.05}s">
                <div class="hist-icon">💬</div>
                <div class="hist-text">{title}</div>
            </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            if st.button("→", key=f"hist_{cid}", help="Open"):
                st.session_state.current_chat_id = cid
                st.session_state.view = "chat"
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ============================================================
# CHAT
# ============================================================
if st.session_state.current_chat_id not in st.session_state.chats:
    create_new_chat()
current = st.session_state.chats[st.session_state.current_chat_id]

st.markdown('<div class="chat-top">Meridium</div>', unsafe_allow_html=True)

nav1, nav2, nav3 = st.columns(3)
with nav1:
    if st.button("← Home", use_container_width=True, key="c_home"):
        st.session_state.view = "home"
        st.rerun()
with nav2:
    if st.button("＋ New", use_container_width=True, key="c_new"):
        create_new_chat()
        st.rerun()
with nav3:
    if st.button("☰ Menu", use_container_width=True, key="c_menu"):
        st.session_state.view = "menu"
        st.rerun()

if st.session_state.show_spotify:
    sp = get_spotify()
    track = current_track(sp) if sp else None
    if track:
        st.caption(f"♫  {track['name']} — {track['artists']}")
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            if st.button("⏮", key="sp_prev", use_container_width=True):
                try:
                    sp.previous_track(); time.sleep(0.3); st.rerun()
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
                    time.sleep(0.3); st.rerun()
                except Exception:
                    pass
        with p3:
            if st.button("⏭", key="sp_next", use_container_width=True):
                try:
                    sp.next_track(); time.sleep(0.3); st.rerun()
                except Exception:
                    pass
        with p4:
            if st.button("↻", key="sp_ref", use_container_width=True):
                st.rerun()

for msg in current["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask Meridium anything…"):
    current["messages"].append({"role": "user", "content": prompt})
    if len(current["messages"]) == 1:
        update_chat_title(st.session_state.current_chat_id, prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if use_wiki and len(prompt.split()) > 2:
        wiki = get_wiki(prompt)
        if wiki:
            messages[0]["content"] += f"\n\nRelevant Wikipedia knowledge:\n{wiki}"
    if use_web and len(prompt.split()) > 2:
        web = get_web_search(prompt)
        if web:
            messages[0]["content"] += f"\n\nRelevant web search results:\n{web}"

    for m in current["messages"]:
        messages.append({"role": m["role"], "content": m["content"]})

    with st.chat_message("assistant"):
        typing = st.empty()
        typing.markdown(
            '<div class="typing-wrap"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>',
            unsafe_allow_html=True,
        )
        # short idle so the dots are visible before the reply lands
        time.sleep(1.2)
        reply = run_chat(messages, provider, model_name, api_key)
        typing.markdown(reply)

    current["messages"].append({"role": "assistant", "content": reply})
    st.rerun()
