"""Illustrated coach portraits (SVG generated at import)."""
from __future__ import annotations
import base64

def _p(style, bg, accent, secondary, hair, skin):
    if style == "gotham":
        x = f'<ellipse cx="128" cy="70" rx="70" ry="45" fill="{hair}"/><rect x="58" y="70" width="140" height="35" fill="{hair}"/><ellipse cx="95" cy="100" rx="18" ry="15" fill="none" stroke="{accent}" stroke-width="3"/><ellipse cx="161" cy="100" rx="18" ry="15" fill="none" stroke="{accent}" stroke-width="3"/><line x1="113" y1="100" x2="143" y2="100" stroke="{accent}" stroke-width="2"/>'
    elif style == "hikaru":
        x = f'<ellipse cx="128" cy="65" rx="75" ry="50" fill="{hair}"/><path d="M55 90 Q40 50 70 55" fill="{hair}"/><path d="M201 90 Q216 50 186 55" fill="{hair}"/>'
    elif style == "magnus":
        x = f'<ellipse cx="128" cy="72" rx="68" ry="42" fill="{hair}"/><rect x="60" y="72" width="136" height="30" fill="{hair}"/>'
    elif style in ("anna", "botez"):
        x = f'<ellipse cx="128" cy="68" rx="78" ry="48" fill="{hair}"/><ellipse cx="55" cy="160" rx="28" ry="70" fill="{hair}"/><ellipse cx="201" cy="160" rx="28" ry="70" fill="{hair}"/>'
    elif style == "eric":
        x = f'<ellipse cx="128" cy="70" rx="70" ry="45" fill="{hair}"/><rect x="58" y="70" width="140" height="32" fill="{hair}"/><ellipse cx="95" cy="100" rx="17" ry="14" fill="none" stroke="#2a2a32" stroke-width="2.5"/><ellipse cx="161" cy="100" rx="17" ry="14" fill="none" stroke="#2a2a32" stroke-width="2.5"/><line x1="112" y1="100" x2="144" y2="100" stroke="#2a2a32" stroke-width="2"/>'
    else:
        x = f'<ellipse cx="128" cy="70" rx="70" ry="45" fill="{hair}"/><rect x="58" y="70" width="140" height="32" fill="{hair}"/>'
    s = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">'
        f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{bg}"/><stop offset="100%" stop-color="{secondary}"/></linearGradient></defs>'
        f'<rect width="256" height="256" rx="40" fill="url(#bg)"/><circle cx="128" cy="128" r="100" fill="{accent}" opacity="0.12"/>'
        f'<ellipse cx="128" cy="250" rx="80" ry="55" fill="{accent}"/><ellipse cx="128" cy="255" rx="65" ry="45" fill="{secondary}"/>'
        f'<rect x="112" y="155" width="32" height="40" fill="{skin}"/><ellipse cx="128" cy="115" rx="58" ry="65" fill="{skin}"/>{x}'
        f'<ellipse cx="128" cy="115" rx="52" ry="58" fill="{skin}"/>'
        f'<ellipse cx="108" cy="108" rx="11" ry="13" fill="#fff"/><ellipse cx="148" cy="108" rx="11" ry="13" fill="#fff"/>'
        f'<ellipse cx="110" cy="110" rx="6" ry="7" fill="#1a1520"/><ellipse cx="150" cy="110" rx="6" ry="7" fill="#1a1520"/>'
        f'<circle cx="112" cy="108" r="2" fill="#fff"/><circle cx="152" cy="108" r="2" fill="#fff"/>'
        f'<path d="M95 95 Q108 88 120 95" fill="none" stroke="{hair}" stroke-width="3" stroke-linecap="round"/>'
        f'<path d="M136 95 Q148 88 161 95" fill="none" stroke="{hair}" stroke-width="3" stroke-linecap="round"/>'
        f'<path d="M128 112 L124 130 L132 130" fill="none" stroke="#c4a090" stroke-width="2" stroke-linecap="round"/>'
        f'<path d="M112 140 Q128 155 144 140" fill="none" stroke="#c07070" stroke-width="2.5" stroke-linecap="round"/>'
        f'<circle cx="128" cy="220" r="14" fill="#0c0a12"/><path d="M122 228 L128 212 L134 228 Z" fill="{accent}"/><circle cx="128" cy="214" r="3" fill="{accent}"/></svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(s.encode()).decode()

PORTRAITS = {
    "gotham": _p("gotham", "#1e1b4b", "#a78bfa", "#312e81", "#2a2030", "#f0d2be"),
    "hikaru": _p("hikaru", "#0f172a", "#38bdf8", "#1e3a5f", "#1a1514", "#ebc8af"),
    "magnus": _p("magnus", "#111827", "#fbbf24", "#1f2937", "#d2b478", "#f5dcc8"),
    "anna": _p("anna", "#4c1d95", "#f9a8d4", "#6b21a8", "#281914", "#fadccd"),
    "botez": _p("botez", "#831843", "#fb7185", "#9f1239", "#1e1412", "#f5d7c8"),
    "fabi": _p("fabi", "#1e3a5f", "#93c5fd", "#0c4a6e", "#231c19", "#f0d2be"),
    "danya": _p("danya", "#164e63", "#67e8f9", "#0e7490", "#2d231e", "#ebcdb4"),
    "eric": _p("eric", "#3f1d0b", "#fdba74", "#7c2d12", "#322319", "#f5dcc8"),
}
