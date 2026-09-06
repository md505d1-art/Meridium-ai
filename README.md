# ◈ Meridium

**Personal Intelligence System**

A modern, minimal, and futuristic personal Intelligence designed for clarity, power, and elegance.

---

### ✨ Features

- **Powerful Free Models** – Defaults to strong models via Groq (Llama 3.3 70B and others)
- **Optional Grok Support** – Connect your xAI API key for Grok
- **Wikipedia Knowledge** – Instantly pulls relevant knowledge when needed
- **Spotify Integration** – See what’s currently playing + full playback controls
- **Chess (Soju)** – Play against Meridium with move grading and Soju commentary
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

# Optional – owner gate
OWNER_PASSWORD = "your_password"
OWNER_NAMES = "drae"
```

3. Install Python deps (local):

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

### ♟ Chess assets (required for the Chess page)

The Chess / Soju board needs files next to `app.py`:

```
chess_widget.html
soju/soju_idle.jpg
soju/soju_happy.jpg
soju/soju_shock.jpg
soju/soju_think.jpg
```

**Easiest path**

1. Download `meridium_chess_assets.zip` (widget + four Soju portraits).
2. From the repo root:

```bash
chmod +x install_chess_assets.sh
./install_chess_assets.sh /path/to/meridium_chess_assets.zip
```

Or manually:

```bash
unzip meridium_chess_assets.zip
```

3. Commit and push (or re-upload on Streamlit Cloud).

`app.py` also accepts `soju/*.b64` text files (base64 of each JPEG) if you prefer not to store binary images in git.
