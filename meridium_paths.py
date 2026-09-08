"""Cloud-safe data directory for Meridium."""
from __future__ import annotations

from pathlib import Path
import os
import tempfile


def meridium_data_dir() -> Path:
    """Prefer /tmp on Streamlit Cloud so writes do not restart the app."""
    if os.environ.get("STREAMLIT_SHARING_MODE") or os.environ.get("STREAMLIT_SERVER_HEADLESS"):
        d = Path(tempfile.gettempdir()) / "meridium_data"
    else:
        d = Path(__file__).resolve().parent / "data"
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        d = Path(tempfile.gettempdir()) / "meridium_data"
        try:
            d.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
    return d
