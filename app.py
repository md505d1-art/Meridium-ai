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
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# THEMES — matching the mockup aesthetic
# ============================================================
THEMES = {
    "Soft Dark": {
        "bg": "linear-gradient(160deg, #0e0c18 0%, #12101c 50%, #0c0a14 100%)",
        "bg_solid": "#0e0c18",
        "surface": "#1a1728",
        "bubble": "#1e1a2e",
        "bubble_user": "#2a2440",
        "border": "#2e2848",
        "text": "#f0eef8",
        "muted": "#9a94b0",
        "accent": "#a78bfa",
        "accent_soft": "rgba(167, 139, 250, 0.18)",
        "sidebar": "#12101a",
        "input": "#1a1728",
        "btn": "#1e1a2e",
        "btn_text": "#f0eef8",
        "radius": "20px",
        "font": "'Inter', system-ui, sans-serif",
        "mode": "dark",
    },
    "Cloud": {
        "bg": "#f4f5f9",
        "bg_solid": "#f4f5f9",
        "surface": "#ffffff",
        "bubble": "#ffffff",
        "bubble_user": "#e8eaf2",
        "border": "#e2e4ec",
        "text": "#1a1a22",
        "muted": "#6b6b7b",
        "accent": "#7c6cf0",
        "accent_soft": "rgba(124, 108, 240, 0.12)",
        "sidebar": "#eef0f6",
        "input": "#ffffff",
        "btn": "#1a1a22",
        "btn_text": "#ffffff",
        "radius": "20px",
        "font": "'Inter', system-ui, sans-serif",
        "mode": "light",
    },
    "Peach": {
        "bg": "linear-gradient(160deg, #1a1210 0%, #1e1614 100%)",
        "bg_solid": "#1a1210",
        "surface": "#241a17",
        "bubble": "#2c201c",
        "bubble_user": "#3a2a24",
        "border": "#3d2e28",
        "text": "#f5ebe6",
        "muted": "#a89088",
        "accent": "#ff9f7a",
        "accent_soft": "rgba(255, 159, 122, 0.15)",
        "sidebar": "#160f0d",
        "input": "#241a17",
        "btn": "#2c201c",
        "btn_text": "#f5ebe6",
        "radius": "20px",
        "font": "'Inter', system-ui, sans-serif",
        "mode": "dark",
    },
    "Mint": {
        "bg": "linear-gradient(160deg, #0d1412 0%, #101a17 100%)",
        "bg_solid": "#0d1412",
        "surface": "#15201c",
        "bubble": "#1a2823",
        "bubble_user": "#223530",
        "border": "#2a3d36",
        "text": "#e6f2ee",
        "muted": "#7a9a90",
        "accent": "#5eead4",
        "accent_soft": "rgba(94, 234, 212, 0.12)",
        "sidebar": "#0b110f",
        "input": "#15201c",
        "btn": "#1a2823",
        "btn_text": "#e6f2ee",
        "radius": "20px",
        "font": "'Inter', system-ui, sans-serif",
        "mode": "dark",
    },
    "Lavender": {
        "bg": "linear-gradient(160deg, #12101a 0%, #16141f 100%)",
        "bg_solid": "#12101a",
        "surface": "#1a1726",
        "bubble": "#221e30",
        "bubble_user": "#2c2740",
        "border": "#322c48",
        "text": "#efeaf8",
        "muted": "#9a90b0",
        "accent": "#c4b5fd",
        "accent_soft": "rgba(196, 181, 253, 0.14)",
        "sidebar": "#0e0c14",
        "input": "#1a1726",
        "btn": "#221e30",
        "btn_text": "#efeaf8",
        "radius": "20px",
        "font": "'Inter', system-ui, sans-serif",
        "mode": "dark",
    },
    "Ocean": {
        "bg": "linear-gradient(160deg, #0a1218 0%, #0d1620 100%)",
        "bg_solid": "#0a1218",
        "surface": "#0f1a22",
        "bubble": "#152430",
        "bubble_user": "#1c3040",
        "border": "#243848",
        "text": "#e6f0f6",
        "muted": "#7a9ab0",
        "accent": "#38bdf8",
        "accent_soft": "rgba(56, 189, 248, 0.12)",
        "sidebar": "#081018",
        "input": "#0f1a22",
        "btn": "#152430",
        "btn_text": "#e6f0f6",
        "radius": "20px",
        "font": "'Inter', system-ui, sans-serif",
        "mode": "dark",
    },
    "Rose": {
        "bg": "#faf6f7",
        "bg_solid": "#faf6f7",
        "surface": "#ffffff",
        "bubble": "#ffffff",
        "bubble_user": "#f3e8eb",
        "border": "#ebdde2",
        "text": "#2a1a1e",
        "muted": "#8a6a72",
        "accent": "#e879a9",
        "accent_soft": "rgba(232, 121, 169, 0.12)",
        "sidebar": "#f5eef1",
        "input": "#ffffff",
        "btn": "#2a1a1e",
        "btn_text": "#ffffff",
        "radius": "20px",
        "font": "'Inter', system-ui, sans-serif",
        "mode": "light",
    },
    "Newspaper": {
        "bg": "#f7f4ef",
        "bg_solid": "#f7f4ef",
        "surface": "#ffffff",
        "bubble": "#ffffff",
        "bubble_user": "#efeae2",
        "border": "#d6d0c4",
        "text": "#1a1a1a",
        "muted": "#5c5c5c",
        "accent": "#333333",
        "accent_soft": "rgba(0,0,0,0.06)",
        "sidebar": "#efeae2",
        "input": "#ffffff",
        "btn": "#1a1a1a",
        "btn_text": "#ffffff",
        "radius": "10px",
        "font": "'Times New Roman', Times, serif",
        "mode": "light",
    },
}

def inject_theme(name: str):
    t = THEMES[name]
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: {t["font"]} !important;
    }}

    .stApp {{
        background: {t["bg"]};
        color: {t["text"]};
    }}

    #MainMenu, footer, header, .stDeployButton {{
        visibility: hidden !important;
        display: none !important;
    }}

    /* Sidebar — soft panel */
    section[data-testid="stSidebar"] {{
        display: none !important;
    }}
    section[data-testid="stSidebar"][aria-expanded="true"] {{
        display: none !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {t["muted"]} !important;
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stMarkdown strong {{
        color: {t["text"]} !important;
    }}

    /* Bubbly chat cards */
    .stChatMessage {{
        background: {t["bubble"]} !important;
        border: 1px solid {t["border"]} !important;
        border-radius: {t["radius"]} !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }}

    /* Rounded input */
    .stChatInput > div {{
        background: {t["input"]} !important;
        border: 1px solid {t["border"]} !important;
        border-radius: 28px !important;
        box-shadow: 0 4px 24px rgba(0,0,0,0.1);
    }}

    /* Soft pill buttons */
    .stButton > button {{
        background: {t["btn"]} !important;
        color: {t["btn_text"]} !important;
        border: 1px solid {t["border"]} !important;
        border-radius: 999px !important;
        font-weight: 500 !important;
        padding: 0.4rem 1.1rem !important;
        transition: all 0.18s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.15);
        border-color: {t["accent"]} !important;
    }}

    a {{ color: {t["accent"]} !important; text-decoration: none !important; }}

    /* Hero */
    .hero {{
        text-align: center;
        padding: 28px 16px 8px;
    }}
    .hero-title {{
        font-size: 2.6rem;
        font-weight: 600;
        letter-spacing: -1px;
        color: {t["text"]};
        margin: 0;
    }}
    .hero-sub {{
        font-size: 0.95rem;
        color: {t["muted"]};
        margin-top: 6px;
        font-weight: 400;
    }}
    .greeting {{
        display: inline-block;
        margin-top: 16px;
        padding: 8px 20px;
        background: {t["accent_soft"]};
        color: {t["accent"]};
        border-radius: 999px;
        font-size: 0.95rem;
        font-weight: 500;
        border: 1px solid {t["accent"]}33;
    }}

    /* Time / date widgets — large & centered like mockup */

    /* Intro animation */
    .intro-overlay {{
        position: fixed;
        inset: 0;
        z-index: 99999;
        display: flex;
        align-items: center;
        justify-content: center;
        background: {t["bg_solid"]};
        animation: introFade 2.8s ease forwards;
    }}
    .intro-text {{
        font-size: 2rem;
        font-weight: 500;
        color: {t["text"]};
        letter-spacing: 0.02em;
        animation: introIn 1.4s ease forwards;
        opacity: 0;
    }}
    .intro-text span {{
        color: {t["accent"]};
    }}
    @keyframes introIn {{
        0% {{ opacity: 0; transform: translateY(12px); }}
        30% {{ opacity: 1; transform: translateY(0); }}
        75% {{ opacity: 1; }}
        100% {{ opacity: 0; transform: translateY(-8px); }}
    }}
    @keyframes introFade {{
        0%, 70% {{ opacity: 1; pointer-events: all; }}
        100% {{ opacity: 0; pointer-events: none; }}
    }}

    /* Control bar */
    .control-bar {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        max-width: 520px;
        margin: 12px auto 8px auto;
        padding: 10px;
        background: {t["surface"]};
        border: 1px solid {t["border"]};
        border-radius: 18px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }}

    .widget-bar {{
        display: flex;
        gap: 14px;
        justify-content: center;
        flex-wrap: wrap;
        margin: 18px auto 22px auto;
    }}
    .widget-pill {{
        background: {t["surface"]};
        border: 1px solid {t["border"]};
        border-radius: 16px;
        padding: 14px 28px;
        text-align: center;
        box-shadow: 0 4px 18px rgba(0,0,0,0.1);
        min-width: 120px;
    }}
    .widget-pill .value {{
        font-size: 1.6rem;
        font-weight: 600;
        color: {t["text"]};
        letter-spacing: -0.5px;
    }}
    .widget-pill .label {{
        font-size: 0.72rem;
        color: {t["muted"]};
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 2px;
    }}

    /* Spotify card */
    .sp-card {{
        background: {t["surface"]};
        border: 1px solid {t["border"]};
        border-radius: {t["radius"]};
        padding: 14px 16px;
        max-width: 420px;
        margin: 0 auto 16px auto;
        display: flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.1);
    }}
    .sp-art {{
        width: 52px; height: 52px;
        border-radius: 14px;
        object-fit: cover;
    }}
    .sp-title {{
        font-size: 0.9rem;
        font-weight: 560;
        color: {t["text"]};
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .sp-artist {{
        font-size: 0.76rem;
        color: {t["muted"]};
        margin-top: 2px;
    }}

    /* Hide default chat avatars */
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"],
    [data-testid="stChatAvatar"],
    .stChatMessage [data-testid="stImage"] {{
        display: none !important;
    }}
    [data-testid="stChatMessage"] {{
        padding-left: 0.5rem !important;
    }}

    /* Hide default Streamlit sidebar toggle */
    [data-testid="collapsedControl"] {{
        display: none !important;
    }}

    /* Logo menu button */
    .logo-btn {{
        position: fixed;
        top: 14px;
        left: 14px;
        z-index: 100000;
        width: 48px;
        height: 48px;
        border-radius: 14px;
        background: {t["surface"]};
        border: 1px solid {t["border"]};
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        animation: logoIn 0.6s ease;
    }}
    .logo-btn:hover {{
        transform: scale(1.06);
        border-color: {t["accent"]};
        box-shadow: 0 6px 24px rgba(167, 139, 250, 0.25);
    }}
    .logo-btn svg {{
        width: 28px;
        height: 28px;
    }}
    @keyframes logoIn {{
        from {{ opacity: 0; transform: scale(0.8); }}
        to {{ opacity: 1; transform: scale(1); }}
    }}

    /* Slide-out menu panel */
    .side-menu {{
        position: fixed;
        top: 0;
        left: 0;
        width: min(300px, 85vw);
        height: 100vh;
        z-index: 99998;
        background: {t["sidebar"]};
        border-right: 1px solid {t["border"]};
        box-shadow: 8px 0 40px rgba(0,0,0,0.35);
        padding: 72px 20px 24px 20px;
        animation: menuSlide 0.35s cubic-bezier(0.22, 1, 0.36, 1);
        overflow-y: auto;
    }}
    .side-menu-backdrop {{
        position: fixed;
        inset: 0;
        z-index: 99997;
        background: rgba(0,0,0,0.45);
        animation: fadeIn 0.3s ease;
    }}
    @keyframes menuSlide {{
        from {{ transform: translateX(-100%); opacity: 0.6; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    .menu-item {{
        display: block;
        padding: 12px 14px;
        margin-bottom: 6px;
        border-radius: 12px;
        color: {t["text"]} !important;
        background: transparent;
        border: 1px solid transparent;
        font-size: 0.95rem;
        transition: background 0.2s ease;
    }}
    .menu-item:hover {{
        background: {t["surface"]};
        border-color: {t["border"]};
    }}

    /* Text animations */
    .hero-title {{
        animation: textRise 0.8s ease both;
    }}
    .hero-sub {{
        animation: textRise 0.8s ease 0.15s both;
    }}
    .greeting, .widget-bar {{
        animation: textRise 0.8s ease 0.28s both;
    }}
    @keyframes textRise {{
        from {{ opacity: 0; transform: translateY(14px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Light theme text force */
    {" .stApp, .stMarkdown, .stMarkdown p, .stCaption, [data-testid='stChatMessageContent'], label, p {{ color: " + t["text"] + " !important; }} " if t["mode"] == "light" else ""}
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
Address the user respectfully."""

GROQ_MODELS = {
    "Smart (Llama 3.3 70B)": "llama-3.3-70b-versatile",
    "Balanced (Qwen3 32B)": "qwen/qwen3-32b",
    "Fast (Llama 3.1 8B)": "llama-3.1-8b-instant",
}
SPOTIFY_SCOPE = "user-read-currently-playing user-read-playback-state user-modify-playback-state"

# ============================================================
# SESSION
# ============================================================
defaults = {
    "theme": "Soft Dark",
    "chats": {},
    "current_chat_id": None,
    "show_spotify": False,
    "show_widgets": True,
    "view": "home",  # home | chat
    "show_intro": True,
    "menu_open": False,
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
            return None, "Please add a free Groq API key in Streamlit Secrets."
        return OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1"), None
    if provider == "grok":
        key = api_key or os.getenv("XAI_API_KEY") or st.secrets.get("XAI_API_KEY", "")
        if not key:
            return None, "Please add an xAI API key."
        return OpenAI(api_key=key, base_url="https://api.x.ai/v1"), None
    if provider == "openrouter":
        key = api_key or os.getenv("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY", "")
        if not key:
            return None, "Please add an OpenRouter API key."
        return OpenAI(api_key=key, base_url="https://openrouter.ai/api/v1"), None
    return None, "Unknown provider"

def chat(messages, provider, model_name, api_key):
    client, err = make_client(provider, api_key)
    if err:
        return f"⚠️ {err}"
    if provider == "groq":
        model = GROQ_MODELS.get(model_name, "llama-3.3-70b-versatile")
    elif provider == "grok":
        model = "grok-4.5"
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
        scope=SPOTIFY_SCOPE, cache_path=None, open_browser=False
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
inject_theme(st.session_state.theme)
now = datetime.now()
time_str = now.strftime("%H:%M")
date_str = now.strftime("%a, %b %d")

# ============================================================
# SIDEBAR
# ============================================================


# ---- Logo menu button (top-left) ----
LOGO_SVG = """<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#e8e0ff"/>
      <stop offset="100%" style="stop-color:#a78bfa"/>
    </linearGradient>
  </defs>
  <path d="M20 30 Q20 75 50 80 Q80 75 80 30 L68 30 Q68 60 50 66 Q32 60 32 30 Z" fill="url(#g)"/>
  <path d="M35 38 L50 58 L65 38" fill="none" stroke="url(#g)" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

lc1, lc2, lc3 = st.columns([1, 6, 1])
with lc1:
    if st.button("◈", key="logo_menu_btn", help="Open menu"):
        st.session_state.menu_open = not st.session_state.menu_open
        st.rerun()

if st.session_state.menu_open:
    st.markdown('<div class="side-menu-backdrop"></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown("### Menu")
        m1, m2 = st.columns(2)
        with m1:
            if st.button("⌂ Home", use_container_width=True, key="m_home"):
                st.session_state.view = "home"
                st.session_state.menu_open = False
                st.rerun()
            if st.button("💬 Chat", use_container_width=True, key="m_chat"):
                st.session_state.view = "chat"
                st.session_state.menu_open = False
                st.rerun()
            if st.button("＋ New chat", use_container_width=True, key="m_new"):
                create_new_chat()
                st.session_state.view = "chat"
                st.session_state.menu_open = False
                st.rerun()
        with m2:
            if st.button("🕒 Toggle time", use_container_width=True, key="m_time"):
                st.session_state.show_widgets = not st.session_state.show_widgets
                st.rerun()
            if st.button("🎵 Toggle music", use_container_width=True, key="m_music"):
                st.session_state.show_spotify = not st.session_state.show_spotify
                st.rerun()
            if st.button("✕ Close", use_container_width=True, key="m_close"):
                st.session_state.menu_open = False
                st.rerun()

        st.markdown("**Theme**")
        theme = st.selectbox("Theme", list(THEMES.keys()),
                             index=list(THEMES.keys()).index(st.session_state.theme),
                             key="menu_theme")
        if theme != st.session_state.theme:
            st.session_state.theme = theme
            st.rerun()

        st.markdown("**Model**")
        provider = st.selectbox("Provider", ["groq", "grok", "openrouter"],
            index=["groq","grok","openrouter"].index(st.session_state.get("provider","groq")) if st.session_state.get("provider","groq") in ["groq","grok","openrouter"] else 0,
            key="menu_prov")
        st.session_state.provider = provider
        if provider == "groq":
            model_name = st.selectbox("Model", list(GROQ_MODELS.keys()), index=0, key="menu_model")
        elif provider == "grok":
            model_name = st.selectbox("Model", ["Grok 4.5", "Grok 4.3"], index=0, key="menu_model")
        else:
            model_name = st.selectbox("Model", [
                "meta-llama/llama-3.3-70b-instruct:free",
                "qwen/qwen3-32b:free",
            ], index=0, key="menu_model")
        api_key = st.text_input("API Key (optional)", type="password", key="menu_key")
        st.session_state.api_key_val = api_key
        st.session_state.model_name = model_name
        st.session_state.provider = provider
        if "use_wiki_toggle" not in st.session_state:
            st.session_state.use_wiki_toggle = True
        if "use_web_toggle" not in st.session_state:
            st.session_state.use_web_toggle = True
        st.session_state.use_wiki_toggle = st.checkbox("Wikipedia", value=st.session_state.use_wiki_toggle, key="menu_wiki")
        st.session_state.use_web_toggle = st.checkbox("Web search", value=st.session_state.use_web_toggle, key="menu_web")
        use_wiki = st.session_state.use_wiki_toggle
        use_web = st.session_state.use_web_toggle

        st.markdown("---")
        st.markdown("**Chats**")
        sorted_chats = sorted(
            st.session_state.chats.items(),
            key=lambda x: x[1].get("created", ""),
            reverse=True,
        )
        for cid, data in sorted_chats[:12]:
            label = data.get("title", "Untitled")
            if st.button(label, key=f"menu_c_{cid}", use_container_width=True):
                st.session_state.current_chat_id = cid
                st.session_state.view = "chat"
                st.session_state.menu_open = False
                st.rerun()


# Legacy sidebar (hidden via CSS)
with st.sidebar:
    st.markdown("### Meridium")
    st.caption("Personal Intelligence")

    theme = st.selectbox(
        "Theme", list(THEMES.keys()),
        index=list(THEMES.keys()).index(st.session_state.theme)
    )
    if theme != st.session_state.theme:
        st.session_state.theme = theme
        st.rerun()

    st.markdown("---")
    st.markdown("**Widgets**")
    st.session_state.show_widgets = st.checkbox("Show time", value=st.session_state.show_widgets)
    st.session_state.show_spotify = st.checkbox("Show Spotify", value=st.session_state.show_spotify)

    st.markdown("---")
    if st.button("＋  New chat", use_container_width=True):
        create_new_chat()
        st.session_state.view = "chat"
        st.rerun()
    if st.button("⌂  Home", use_container_width=True):
        st.session_state.view = "home"
        st.rerun()

    st.markdown("**Chats**")
    sorted_chats = sorted(
        st.session_state.chats.items(),
        key=lambda x: x[1].get("created", ""),
        reverse=True,
    )
    for cid, data in sorted_chats:
        active = cid == st.session_state.current_chat_id
        label = ("● " if active else "○ ") + data.get("title", "Untitled")
        if st.button(label, key=f"c_{cid}", use_container_width=True):
            st.session_state.current_chat_id = cid
            st.session_state.view = "chat"
            st.rerun()

    st.markdown("---")
    st.markdown("**Model**")
    provider = st.selectbox("Provider", ["groq", "grok", "openrouter"], index=0)
    if provider == "groq":
        model_name = st.selectbox("Model", list(GROQ_MODELS.keys()), index=0)
    elif provider == "grok":
        model_name = st.selectbox("Model", ["Grok 4.5", "Grok 4.3"], index=0)
    else:
        model_name = st.selectbox("Model", [
            "meta-llama/llama-3.3-70b-instruct:free",
            "qwen/qwen3-32b:free",
        ], index=0)

    api_key = st.text_input("API Key (optional)", type="password")
    if "use_wiki_toggle" not in st.session_state:
        st.session_state.use_wiki_toggle = True
    if "use_web_toggle" not in st.session_state:
        st.session_state.use_web_toggle = True
    st.session_state.use_wiki_toggle = st.checkbox("Wikipedia", value=st.session_state.use_wiki_toggle)
    st.session_state.use_web_toggle = st.checkbox("Web search", value=st.session_state.use_web_toggle)
    use_wiki = st.session_state.use_wiki_toggle
    use_web = st.session_state.use_web_toggle

    st.markdown("---")
    st.markdown("[Groq](https://console.groq.com) · [Spotify](https://developer.spotify.com/dashboard)")

# ============================================================
# MAIN
# ============================================================

# ============================================================
# MAIN — Home or Chat
# ============================================================

# Quick actions always available in sidebar context

# Ensure model settings always exist
if "provider" not in st.session_state:
    st.session_state.provider = "groq"
if "model_name" not in st.session_state:
    st.session_state.model_name = list(GROQ_MODELS.keys())[0]
if "api_key_val" not in st.session_state:
    st.session_state.api_key_val = ""
if "use_wiki_toggle" not in st.session_state:
    st.session_state.use_wiki_toggle = True
if "use_web_toggle" not in st.session_state:
    st.session_state.use_web_toggle = True

provider = st.session_state.get("provider", "groq")
model_name = st.session_state.get("model_name", list(GROQ_MODELS.keys())[0])
api_key = st.session_state.get("api_key_val", "")
use_wiki = st.session_state.use_wiki_toggle
use_web = st.session_state.use_web_toggle

if st.session_state.show_intro:
    st.markdown("""
    <div class="intro-overlay">
        <div class="intro-text">Hello, <span>Master</span></div>
    </div>
    """, unsafe_allow_html=True)
    import time as _t
    _t.sleep(2.6)
    st.session_state.show_intro = False
    st.rerun()

if st.session_state.view == "home":
    # -------- HOME MENU --------
    st.markdown("""
    <div class="hero" style="padding-top: 36px;">
        <div class="hero-title">Meridium</div>
        <div class="hero-sub">Personal Intelligence System</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.show_widgets:
        _now = datetime.now()
        time_str = _now.strftime("%H:%M")
        date_str = _now.strftime("%a, %b %d")
        st.markdown(f"""
        <div class="widget-bar">
            <div class="widget-pill">
                <div class="value">{time_str}</div>
                <div class="label">Time</div>
            </div>
            <div class="widget-pill">
                <div class="value">{date_str}</div>
                <div class="label">Date</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("##### Control bar")
    r1 = st.columns(4)
    with r1[0]:
        if st.button("💬 Chat", use_container_width=True, key="cb_chat"):
            st.session_state.view = "chat"
            st.rerun()
    with r1[1]:
        if st.button("＋ New", use_container_width=True, key="cb_new"):
            create_new_chat()
            st.session_state.view = "chat"
            st.rerun()
    with r1[2]:
        if st.button("🕒 Time", use_container_width=True, key="cb_time"):
            st.session_state.show_widgets = not st.session_state.show_widgets
            st.rerun()
    with r1[3]:
        if st.button("🎵 Music", use_container_width=True, key="cb_music"):
            st.session_state.show_spotify = not st.session_state.show_spotify
            st.rerun()

    r2 = st.columns(4)
    with r2[0]:
        if st.button("🌐 Web", use_container_width=True, key="cb_web"):
            st.session_state["use_web_toggle"] = not st.session_state.get("use_web_toggle", True)
            st.rerun()
    with r2[1]:
        if st.button("📖 Wiki", use_container_width=True, key="cb_wiki"):
            st.session_state["use_wiki_toggle"] = not st.session_state.get("use_wiki_toggle", True)
            st.rerun()
    with r2[2]:
        keys = list(THEMES.keys())
        if st.button("🎨 Theme", use_container_width=True, key="cb_theme"):
            i = keys.index(st.session_state.theme)
            st.session_state.theme = keys[(i + 1) % len(keys)]
            st.rerun()
    with r2[3]:
        if st.button("☰ Menu", use_container_width=True, key="cb_menu"):
            st.toast("Tap the top-left button to open the full menu")

    web_on = st.session_state.get("use_web_toggle", True)
    wiki_on = st.session_state.get("use_wiki_toggle", True)
    st.caption(
        f"Time: {'on' if st.session_state.show_widgets else 'off'} · "
        f"Music: {'on' if st.session_state.show_spotify else 'off'} · "
        f"Web: {'on' if web_on else 'off'} · "
        f"Wiki: {'on' if wiki_on else 'off'} · "
        f"Theme: {st.session_state.theme}"
    )

    if st.session_state.show_spotify:
        sp = get_spotify()
        track = current_track(sp) if sp else None
        if track:
            art = f'<img class="sp-art" src="{track["art"]}">' if track["art"] else ""
            st.markdown(f"""
            <div class="sp-card">
                {art}
                <div>
                    <div class="sp-title">{track["name"]}</div>
                    <div class="sp-artist">{track["artists"]}{" · " + track["device"] if track["device"] else ""}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif sp:
            st.caption("Spotify connected — nothing playing.")
        else:
            st.caption("Add Spotify keys in Secrets to enable music.")

else:
    # -------- CHAT VIEW (no Meridium title) --------
    current = st.session_state.chats[st.session_state.current_chat_id]

    # Top bar: back to home
    b1, b2, b3 = st.columns([1, 3, 1])
    with b1:
        if st.button("← Home", use_container_width=True):
            st.session_state.view = "home"
            st.rerun()
    with b3:
        if st.button("＋ New", use_container_width=True):
            create_new_chat()
            st.rerun()

    if st.session_state.show_spotify:
        sp = get_spotify()
        track = current_track(sp) if sp else None
        if track:
            art = f'<img class="sp-art" src="{track["art"]}">' if track["art"] else ""
            st.markdown(f"""
            <div class="sp-card">
                {art}
                <div>
                    <div class="sp-title">{track["name"]}</div>
                    <div class="sp-artist">{track["artists"]}{" · " + track["device"] if track["device"] else ""}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("⏮", use_container_width=True, key="prev"):
                    try:
                        sp.previous_track(); __import__("time").sleep(0.3); st.rerun()
                    except: pass
            with c2:
                icon = "⏸" if track["playing"] else "▶️"
                if st.button(icon, use_container_width=True, key="play"):
                    try:
                        if track["playing"]:
                            sp.pause_playback()
                        else:
                            sp.start_playback()
                        __import__("time").sleep(0.3); st.rerun()
                    except: pass
            with c3:
                if st.button("⏭", use_container_width=True, key="next"):
                    try:
                        sp.next_track(); __import__("time").sleep(0.3); st.rerun()
                    except: pass
            with c4:
                if st.button("↻", use_container_width=True, key="ref"):
                    st.rerun()
        elif sp:
            st.caption("Spotify connected — nothing playing.")
        else:
            st.caption("Add Spotify keys in Secrets to enable music.")

    for msg in current["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Message Meridium…"):
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
            with st.spinner(""):
                reply = chat(messages, provider, model_name, api_key)
                st.markdown(reply)

        current["messages"].append({"role": "assistant", "content": reply})
        st.rerun()
