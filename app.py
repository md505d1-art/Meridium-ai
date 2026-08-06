import streamlit as st
import os
from openai import OpenAI
import wikipedia
from datetime import datetime

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Meridium",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS (Dark / Caelestia-inspired) ======================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(160deg, #0a0b0f 0%, #11131a 50%, #0d0f14 100%);
        color: #e8eaf0;
    }
    section[data-testid="stSidebar"] {
        background: rgba(16, 18, 26, 0.95) !important;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    h1, h2, h3 {
        color: #e8eaf0 !important;
        font-weight: 600;
        letter-spacing: -0.3px;
    }
    .stChatMessage {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #5b7cfa, #7c9cff) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 560;
    }
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: 650;
        background: linear-gradient(135deg, #e8eaf0, #7c9cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .sidebar-sub {
        color: #9aa3b8;
        font-size: 0.85rem;
        margin-bottom: 20px;
    }
    a {
        color: #7c9cff !important;
        text-decoration: none;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ====================== CONFIG ======================
SYSTEM_PROMPT = """You are Meridium, a highly capable personal AI assistant.
You are intelligent, helpful, precise, and have a calm, modern personality.
You have access to Wikipedia knowledge and can solve modern problems effectively.
Be clear, structured, and insightful. Avoid unnecessary fluff.
When using Wikipedia information, cite the source naturally.
You were created to be a strong personal AI companion."""

GROQ_MODELS = {
    "Llama 3.3 70B (Strong & Fast)": "llama-3.3-70b-versatile",
    "Qwen3 32B": "qwen/qwen3-32b",
    "Llama 3.1 8B (Fastest)": "llama-3.1-8b-instant",
}

def get_wikipedia_summary(query: str, sentences: int = 3) -> str:
    try:
        wikipedia.set_lang("en")
        search_results = wikipedia.search(query, results=3)
        if not search_results:
            return ""
        page_title = search_results[0]
        summary = wikipedia.summary(page_title, sentences=sentences, auto_suggest=False)
        url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
        return f"**Wikipedia: {page_title}**\n\n{summary}\n\nSource: {url}"
    except Exception:
        return ""

def create_client(provider: str, api_key: str = None):
    if provider == "groq":
        key = api_key or os.getenv("GROQ_API_KEY", "") or st.secrets.get("GROQ_API_KEY", "")
        if not key:
            return None, "Please add a free Groq API key in the sidebar or in Streamlit secrets."
        return OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1"), None
    elif provider == "grok":
        key = api_key or os.getenv("XAI_API_KEY", "") or st.secrets.get("XAI_API_KEY", "")
        if not key:
            return None, "Please add an xAI (Grok) API key."
        return OpenAI(api_key=key, base_url="https://api.x.ai/v1"), None
    elif provider == "openrouter":
        key = api_key or os.getenv("OPENROUTER_API_KEY", "") or st.secrets.get("OPENROUTER_API_KEY", "")
        if not key:
            return None, "Please add an OpenRouter API key."
        return OpenAI(api_key=key, base_url="https://openrouter.ai/api/v1"), None
    return None, "Unknown provider"

def generate_response(messages, provider, model_name, api_key):
    client, error = create_client(provider, api_key)
    if error:
        return f"⚠️ {error}"
    if provider == "groq":
        model_id = GROQ_MODELS.get(model_name, "llama-3.3-70b-versatile")
    elif provider == "grok":
        model_id = "grok-4.5"
    else:
        model_id = model_name
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown('<div class="sidebar-title">Meridium</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Your personal AI</div>', unsafe_allow_html=True)
    st.markdown("### Settings")
    provider = st.selectbox("Provider", options=["groq", "grok", "openrouter"], index=0)
    if provider == "groq":
        model_name = st.selectbox("Model", list(GROQ_MODELS.keys()), index=0)
    elif provider == "grok":
        model_name = st.selectbox("Model", ["Grok 4.5", "Grok 4.3"], index=0)
    else:
        model_name = st.selectbox("Model", ["meta-llama/llama-3.3-70b-instruct:free", "qwen/qwen3-32b:free"], index=0)
    api_key = st.text_input("API Key (optional)", type="password", placeholder="Paste free Groq key here")
    use_wikipedia = st.checkbox("Use Wikipedia knowledge", value=True)
    st.markdown("---")
    st.markdown("**Quick Links**")
    st.markdown("- [Get free Groq key](https://console.groq.com)")
    st.markdown("- [Open Grok](https://grok.x.ai)")
    st.markdown("- [xAI Console](https://console.x.ai)")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ====================== MAIN AREA ======================
st.markdown("## Meridium")
st.caption("Modern • Capable • Free")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask Meridium anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if use_wikipedia and len(prompt.split()) > 2:
        wiki_info = get_wikipedia_summary(prompt)
        if wiki_info:
            messages[0]["content"] += f"\n\n[Relevant Wikipedia knowledge]:\n{wiki_info}"

    for msg in st.session_state.messages:
        messages.append({"role": msg["role"], "content": msg["content"]})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = generate_response(messages, provider, model_name, api_key)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
