# Auto-stitched Meridium entrypoint — full source lives in app_parts/
from pathlib import Path
_parts_dir = Path(__file__).resolve().parent / "app_parts"
_code = "".join(
    p.read_text(encoding="utf-8")
    for p in sorted(_parts_dir.glob("part_*.txt"))
)
exec(compile(_code, str(Path(__file__).resolve().parent / "app.py"), "exec"), globals())
