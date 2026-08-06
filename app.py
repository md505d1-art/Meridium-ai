import streamlit as st
import os
import time
from openai import OpenAI
import wikipedia
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Meridium",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# DESIGN SYSTEM – Futuristic Minimal
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background: #050507;
    color: #e4e4e7;
}

#MainMenu, footer, header, .stDeployButton {
    visibility: hidden;
    display: none;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0a0a0c !important;
    border-right: 1px solid #18181b;
}
section[data-testid="stSidebar"] * {
    color: #a1a1aa !important;
}

/* Hero */
.hero {
    text-align: center;
    padding: 36px 16px 8px;
}
.hero-title {
    font-size: 2.7rem;
    font-weight: 500;
    letter-spacing: -1.2px;
    color: #fafafa;
    margin: 0;
}
.hero-sub {
    font-size: 0.95rem;
    color: #71717a;
    font-weight: 300;
    margin-top: 4px;
}
.greeting {
    font-size: 1.1rem;
    color: #a1a1aa;
    margin-top: 16px;
    font-weight: 400;
}

/* Chat */
.stChatMessage {
    background: #0c0c0e !important;
    border: 1px solid #18181b !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    margin-bottom: 10px !important;
}

/* Input */
.stChatInput > div {
    background: #0c0c0e !important;
    border: 1px solid #1f1f24 !important;
    border-radius: 14px !important;
}

/* Buttons */
.stButton > button {
    background: #18181b !important;
    color: #e4e4e7 !important;
    border: 1px solid #27272a !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    background: #27272a !important;
    border-color: #3f3f46 !important;
}

/* Links */
a {
    color: #a1a1aa !important;
    text-decoration: none !important;
}
a:hover {
    color: #fafafa !important;
}

/* Spotify card */
.sp-card {
    background: #0c0c0e;
    border: 1px solid #18181b;
    border-radius: 14px;
    padding: 14px 18px;
    max-width: 460px;
    margin: 0 auto 20px auto;
    display: flex;
    align-items: center;
    gap: 14px;
}
.sp-art {
    width: 58px;
    height: 58px;
    border-radius: 8px;
    object-fit: cover;
}
.sp-title {
    font-size: 0.92rem;
    font-weight: 500;
    color: #fafafa;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.sp-artist {
    font-size: 0.78rem;
    color: #71717a;
    margin-top: 2px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONFIG
# ============================================================
SYSTEM_PROMPT = """You are Meridium, a highly capable personal AI assistant.
You are intelligent, precise, calm and modern.
You solve problems clearly and effectively.
You can use Wikipedia knowledge when relevant.
Be helpful, structured and insightful. Avoid fluff.
Address the user respectfully."""

GROQ_MODELS = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Qwen3 32B": "qwen/qwen3-32b",
    "Llama 3.1 8B (Fast)": "llama-3.1-8b-instant",
}

SPOTIFY_SCOPE = "user-read-currently-playing user-read-playback-state user-modify-playback-state"

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

def make_client(provider: str, api_key: str = None):
    if provider == "groq":
        key = api_key or os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
        if not key:
            return None, "Please add a free Groq API key."
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

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### Meridium")
    st.caption("Control Panel")

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

    st.markdown("---")
    st.markdown("**Links**")
    st.markdown("[Get free Groq key](https://console.groq.com)")
    st.markdown("[Spotify Developer](https://developer.spotify.com/dashboard)")
    st.markdown("[Open Grok](https://grok.x.ai)")

    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

# ============================================================
# MAIN
# ============================================================
st.markdown("""
<div class="hero">
    <div class="hero-title">Meridium</div>
    <div class="hero-sub">Personal Intelligence System</div>
    <div class="greeting">Hello, Master</div>
</div>
""", unsafe_allow_html=True)

# ----- Spotify -----
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

elif sp:
    st.caption("Spotify connected — nothing playing right now.")
else:
    st.caption("Spotify not configured yet. Add Client ID & Secret in Streamlit Secrets.")

st.markdown("")

# ----- Chat -----
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Message Meridium..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if use_wiki and len(prompt.split()) > 2:
        wiki = get_wiki(prompt)
        if wiki:
            messages[0]["content"] += f"\n\nRelevant knowledge:\n{wiki}"

    for m in st.session_state.messages:
        messages.append({"role": m["role"], "content": m["content"]})

    with st.chat_message("assistant"):
        with st.spinner(""):
            reply = chat(messages, provider, model_name, api_key)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
