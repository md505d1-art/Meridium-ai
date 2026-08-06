# ◈ Meridium

**Personal Intelligence System**

A modern, minimal, and futuristic personal AI designed for clarity, power, and elegance.

---

### ✨ Features

- **Powerful Free Models** – Defaults to strong models via Groq (Llama 3.3 70B and others)
- **Optional Grok Support** – Connect your xAI API key for Grok
- **Wikipedia Knowledge** – Instantly pulls relevant knowledge when needed
- **Spotify Integration** – See what’s currently playing + full playback controls
- **Clean Dark Interface** – Deep black, minimal, and refined design
- **Multi-device** – Works beautifully on phone, tablet, laptop, and desktop
- **Personalized Greeting** – “Hello, Master” every time you open it

---

### 🚀 Quick Start

1. Deploy this repository on [Streamlit Community Cloud](https://share.streamlit.io)
2. Add the following secrets in your Streamlit app settings:

```toml
GROQ_API_KEY = "your_groq_api_key"

# Optional – for Spotify
SPOTIFY_CLIENT_ID = "your_spotify_client_id"
SPOTIFY_CLIENT_SECRET = "your_spotify_client_secret"
SPOTIFY_REDIRECT_URI = "https://your-app-name.streamlit.app/"
