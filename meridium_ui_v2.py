"""Meridium UI v2 — full visual redesign layer."""
from __future__ import annotations

UI_CSS = r"""
<style id="meridium-ui-v2">
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
  --mer-bg: #07070c;
  --mer-panel: rgba(18, 18, 28, 0.92);
  --mer-border: rgba(140, 120, 255, 0.22);
  --mer-accent: #8b5cf6;
  --mer-accent2: #22d3ee;
  --mer-text: #ece8ff;
  --mer-muted: #9b95b5;
  --mer-radius: 16px;
  --mer-shadow: 0 12px 40px rgba(0,0,0,0.45);
}

html, body, .stApp {
  background: var(--mer-bg) !important;
  color: var(--mer-text) !important;
  font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
}

.stApp {
  background:
    radial-gradient(ellipse at 20% -10%, rgba(139,92,246,0.18), transparent 50%),
    radial-gradient(ellipse at 90% 10%, rgba(34,211,238,0.08), transparent 40%),
    linear-gradient(180deg, #0a0a12 0%, #07070c 40%, #050508 100%) !important;
}

section.main .block-container {
  padding-top: 1.2rem !important;
  padding-bottom: 3rem !important;
  max-width: 1100px !important;
}

h1, h2, h3, h4 {
  font-family: 'IBM Plex Sans', sans-serif !important;
  letter-spacing: -0.02em !important;
  color: var(--mer-text) !important;
}
h1 { font-weight: 700 !important; }
h2, h3 { font-weight: 600 !important; }

p, label, span, .stMarkdown {
  color: var(--mer-text) !important;
}

.stCaption, [data-testid="stCaptionContainer"] {
  color: var(--mer-muted) !important;
}

.stButton > button {
  background: linear-gradient(180deg, rgba(30,28,48,0.95), rgba(18,16,32,0.98)) !important;
  color: var(--mer-text) !important;
  border: 1px solid var(--mer-border) !important;
  border-radius: 12px !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.25) !important;
  font-weight: 500 !important;
  transition: border-color 0.15s, box-shadow 0.15s, transform 0.1s !important;
}
.stButton > button:hover {
  border-color: rgba(139,92,246,0.55) !important;
  box-shadow: 0 0 20px rgba(139,92,246,0.2) !important;
  transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {
  background: linear-gradient(135deg, #7c3aed, #5b21b6) !important;
  border: 1px solid rgba(167,139,250,0.5) !important;
}

[data-testid="stExpander"] {
  background: var(--mer-panel) !important;
  border: 1px solid var(--mer-border) !important;
  border-radius: var(--mer-radius) !important;
  box-shadow: var(--mer-shadow) !important;
}

[data-testid="stMetric"] {
  background: var(--mer-panel) !important;
  border: 1px solid var(--mer-border) !important;
  border-radius: 14px !important;
  padding: 0.6rem 0.8rem !important;
}

.stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div {
  background: rgba(12,12,20,0.9) !important;
  border: 1px solid var(--mer-border) !important;
  border-radius: 10px !important;
  color: var(--mer-text) !important;
}

[data-testid="stSidebar"] {
  background: #0a0a12 !important;
  border-right: 1px solid var(--mer-border) !important;
}

hr { border-color: rgba(139,92,246,0.15) !important; }

code, pre {
  font-family: 'IBM Plex Mono', ui-monospace, monospace !important;
}

div[data-testid="stAlert"] {
  border-radius: 12px !important;
}

header[data-testid="stHeader"] {
  background: rgba(7,7,12,0.7) !important;
  backdrop-filter: blur(12px) !important;
}

@media (max-width: 768px) {
  section.main .block-container { padding: 0.7rem 0.7rem 4rem !important; }
  .stButton > button { min-height: 2.7rem !important; }
}
</style>
"""


def inject_ui(st) -> None:
    try:
        st.markdown(UI_CSS, unsafe_allow_html=True)
    except Exception:
        pass
