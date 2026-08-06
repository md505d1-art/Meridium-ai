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

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Meridium",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# THEMES
# ============================================================
THEMES = {
    "Modern": {
        "font": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
        "bg": "#050507",
        "sidebar_bg": "#0a0a0c",
        "card_bg": "#0c0c0e",
        "border": "#18181b",
        "text": "#e4e4e7",
        "muted": "#71717a",
        "title": "#fafafa",
        "accent": "#a1a1aa",
        "input_bg": "#0c0c0e",
        "button_bg": "#18181b",
        "button_border": "#27272a",
        "chat_bg": "#0c0c0e",
        "hero_weight": "500",
        "layout": "standard"
    },
    "Editorial": {
        "font": "'Newsreader', 'Libre Baskerville', Georgia, serif",
        "bg": "#0b0b0d",
        "sidebar_bg": "#111113",
        "card_bg": "#121214",
        "border": "#1c1c1f",
        "text": "#e8e6e3",
        "muted": "#8a8780",
        "title": "#f5f3ef",
        "accent": "#c4bdb3",
        "input_bg": "#121214",
        "button_bg": "#1a1a1d",
        "button_border": "#2a2a2e",
        "chat_bg": "#121214",
        "hero_weight": "500",
        "layout": "standard"
    },
    "Newspaper": {
        "font": "'Times New Roman', Times, serif",
        "bg": "#f7f4ef",
        "sidebar_bg": "#efeae2",
        "card_bg": "#ffffff",
        "border": "#d6d0c4",
        "text": "#1a1a1a",
        "muted": "#5c5c5c",
        "title": "#111111",
        "accent": "#333333",
        "input_bg": "#ffffff",
        "button_bg": "#1a1a1a",
        "button_border": "#1a1a1a",
        "chat_bg": "#ffffff",
        "hero_weight": "700",
        "layout": "newspaper"
    }
}

def inject_theme(theme_name: str):
    t = THEMES[theme_name]
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap');

    html, body, [class*="css"] {{
        font-family: {t["font"]};
    }}

    .stApp {{
        background: {t["bg"]};
        color: {t["text"]};
    }}

    #MainMenu, footer, header, .stDeployButton {{
        visibility: hidden;
        display: none;
    }}

    section[data-testid="stSidebar"] {{
        background: {t["sidebar_bg"]} !important;
        border-right: 1px solid {t["border"]};
    }}
    section[data-testid="stSidebar"] * {{
        color: {t["muted"]} !important;
    }}
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: {t["title"]} !important;
    }}

    .hero {{
        text-align: center;
        padding: 28px 16px 6px;
    }}
    .hero-title {{
        font-size: 2.5rem;
        font-weight: {t["hero_weight"]};
        letter-spacing: -0.8px;
        color: {t["title"]};
        margin: 0;
    }}
    .hero-sub {{
        font-size: 0.95rem;
        color: {t["muted"]};
        font-weight: 400;
        margin-top: 4px;
    }}
    .greeting {{
        font-size: 1.05rem;
        color: {t["accent"]};
        margin-top: 14px;
        font-weight: 400;
    }}

    .stChatMessage {{
        background: {t["chat_bg"]} !important;
        border: 1px solid {t["border"]} !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        margin-bottom: 10px !important;
    }}

    .stChatInput > div {{
        background: {t["input_bg"]} !important;
        border: 1px solid {t["border"]} !important;
        border-radius: 14px !important;
    }}

    .stButton > button {{
        background: {t["button_bg"]} !important;
        color: {"#f5f5f5" if theme_name != "Newspaper" else "#ffffff"} !important;
        border: 1px solid {t["button_border"]} !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease;
    }}
    .stButton > button:hover {{
        opacity: 0.9;
    }}

    a {{
        color: {t["accent"]} !important;
        text-decoration: none !important;
    }}
    a:hover {{
        color: {t["title"]} !important;
    }}

    .sp-card {{
        background: {t["card_bg"]};
        border: 1px solid {t["border"]};
        border-radius: 14px;
        padding: 14px 18px;
        max-width: 460px;
        margin: 0 auto 18px auto;
        display: flex;
        align-items: center;
        gap: 14px;
    }}
    .sp-art {{
        width: 56px;
        height: 56px;
        border-radius: 8px;
        object-fit: cover;
    }}
    .sp-title {{
        font-size: 0.92rem;
        font-weight: 500;
        color: {t["title"]};
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .sp-artist {{
        font-size: 0.78rem;
        color: {t["muted"]};
        margin-top: 2px;
    }}

    {" .stApp {{ max-width: 1100px; margin: 0 auto; }} .hero-title {{ font-size: 2.8rem; letter-spacing: -0.5px; }} " if theme_name == "Newspaper" else ""}
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
    "Llama 3.3 70B (Smart)": "llama-3.3-70b-versatile",
    "Qwen3 32B": "qwen/qwen3-32b",
    "Llama 3.1 8B (Fast)": "llama-3.1-8b-instant",
}

SPOTIFY_SCOPE = "user-read-currently-playing user-read-playback-state user-modify-playback-state"

# ============================================================
# SESSION STATE INIT
# ============================================================
if "theme" not in st.session_state:
    st.session_state.theme = "Modern"

if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    first_id = str(uuid.uuid4())[:8]
    st.session_state.chats[first_id] = {
        "title": "New conversation",
        "messages": [],
        "created": datetime.now().isoformat()
    }
    st.session_state.current_chat_id = first_id

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
    """Free web search via DuckDuckGo (no API key needed)."""
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
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
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
        client_id=cid,
        client_secret=secret,
        redirect_uri=redirect,
        scope=SPOTIFY_SCOPE,
        cache_path=None,
        open_browser=False
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
            "device": data.get("device", {}).get("name", "")
        }
    except Exception:
        return None

def create_new_chat():
    new_id = str(uuid.uuid4())[:8]
    st.session_state.chats[new_id] = {
        "title": "New conversation",
        "messages": [],
        "created": datetime.now().isoformat()
    }
    st.session_state.current_chat_id = new_id

def switch_chat(chat_id):
    st.session_state.current_chat_id = chat_id

def update_chat_title(chat_id, first_message):
    title = first_message.strip()
    if len(title) > 42:
        title = title[:42] + "…"
    st.session_state.chats[chat_id]["title"] = title

# ============================================================
# APPLY THEME
# ============================================================
inject_theme(st.session_state.theme)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### Meridium")
    st.caption("Personal Intelligence System")

    theme = st.selectbox(
        "Theme",
        options=list(THEMES.keys()),
        index=list(THEMES.keys()).index(st.session_state.theme)
    )
    if theme != st.session_state.theme:
        st.session_state.theme = theme
        st.rerun()

    st.markdown("---")

    if st.button("＋ New chat", use_container_width=True):
        create_new_chat()
        st.rerun()

    st.markdown("**Conversations**")

    sorted_chats = sorted(
        st.session_state.chats.items(),
        key=lambda x: x[1].get("created", ""),
        reverse=True
    )

    for cid, chat_data in sorted_chats:
        is_active = cid == st.session_state.current_chat_id
        label = chat_data.get("title", "Untitled")
        if st.button(
            ("› " if is_active else "  ") + label,
            key=f"chat_{cid}",
            use_container_width=True
        ):
            switch_chat(cid)
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
            "qwen/qwen3-32b:free"
        ], index=0)

    api_key = st.text_input("API Key (optional)", type="password")
    use_wiki = st.checkbox("Wikipedia", value=True)
    use_web = st.checkbox("Web search (Google-like)", value=True)

    st.markdown("---")
    st.markdown("[Groq Key](https://console.groq.com)")
    st.markdown("[Spotify Dev](https://developer.spotify.com/dashboard)")
    st.markdown("[Grok](https://grok.x.ai)")

# ============================================================
# MAIN AREA
# ============================================================
current = st.session_state.chats[st.session_state.current_chat_id]

st.markdown("""
<div class="hero">
    <div class="hero-title">Meridium</div>
    <div class="hero-sub">Personal Intelligence System</div>
    <div class="greeting">Hello, Master</div>
</div>
""", unsafe_allow_html=True)

# ----- Spotify (optional) -----
sp = get_spotify()
track = current_track(sp) if sp else None

if track:
    art_tag = f'<img class="sp-art" src="{track["art"]}">' if track["art"] else ""
    st.markdown(f"""
    <div class="sp-card">
        {art_tag}
        <div>
            <div class="sp-title">{track["name"]}</div>
            <div class="sp-artist">{track["artists"]}{' • ' + track["device"] if track["device"] else ''}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("⏮", use_container_width=True, key="prev"):
            try:
                sp.previous_track()
                time.sleep(0.35)
                st.rerun()
            except: pass
    with c2:
        icon = "⏸" if track["playing"] else "▶️"
        if st.button(icon, use_container_width=True, key="play"):
            try:
                if track["playing"]:
                    sp.pause_playback()
                else:
                    sp.start_playback()
                time.sleep(0.35)
                st.rerun()
            except: pass
    with c3:
        if st.button("⏭", use_container_width=True, key="next"):
            try:
                sp.next_track()
                time.sleep(0.35)
                st.rerun()
            except: pass
    with c4:
        if st.button("↻", use_container_width=True, key="refresh"):
            st.rerun()

# ----- Messages -----
for msg in current["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----- Input -----
if prompt := st.chat_input("Message Meridium..."):
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
