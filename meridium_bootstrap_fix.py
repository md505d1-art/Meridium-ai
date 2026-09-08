"""Import this first to make data dirs cloud-safe."""
from __future__ import annotations

def apply():
    try:
        from meridium_paths import meridium_data_dir
    except Exception:
        return
    for mod_name, attr in (
        ("meridium_themes", "_data_dir"),
        ("meridium_study", "_data"),
        ("meridium_nadir", "_data"),
    ):
        try:
            mod = __import__(mod_name)
            setattr(mod, attr, meridium_data_dir)
        except Exception:
            pass
