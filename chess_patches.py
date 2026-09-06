"""Chess.com board + softer white pieces + soju root paths."""
def apply_chess(code: str) -> str:
    code = code.replace(
        (
            "        soju_dir = next((d for d in soju_dirs if d.is_dir()), None)\n"
            "        if soju_dir is None:\n"
            "            raise FileNotFoundError(\n"
            '                "soju/ folder not found. Create soju/ next to app.py and add the four portraits."\n'
            "            )\n"
            "        def _b64img(name):\n"
            "            p = soju_dir / name\n"
            "            if not p.exists():\n"
            '                raise FileNotFoundError(f"Missing Soju asset: soju/{name}")\n'
            '            return "data:image/jpeg;base64," + _b64.b64encode(p.read_bytes()).decode()'
        ),
        (
            "        soju_dir = next((d for d in soju_dirs if d.is_dir()), None)\n"
            "        def _b64img(name):\n"
            "            cands = ([soju_dir / name] if soju_dir else []) + [here / name, widget.parent / name]\n"
            "            for p in cands:\n"
            "                if p.exists() and p.is_file():\n"
            '                    return "data:image/jpeg;base64," + _b64.b64encode(p.read_bytes()).decode()\n'
            '            raise FileNotFoundError(f"Missing Soju asset: {name})