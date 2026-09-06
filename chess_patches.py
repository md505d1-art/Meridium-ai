"""Chess + soju path patches."""
def apply_chess(code: str) -> str:
    old = (
        "        soju_dirs = [\n"
        '            widget.parent / "soju",\n'
        '            here / "soju",\n'
        '            cwd / "soju",\n'
        '            here / "assets" / "soju",\n'
        "        ]\n"
        "        soju_dir = next((d for d in soju_dirs if d.is_dir()), None)\n"
        "        if soju_dir is None:\n"
        "            raise FileNotFoundError(\n"
        '                "soju/ folder not found. Create soju/ next to app.py and add the four portraits."\n'
        "            )\n"
        "        def _b64img(name):\n"
        "            p = soju_dir / name\n"
        "            if not p.exists():\n"
        '                raise FileNotFoundError(f"Missing Soju asset: soju/{name}")\n'
        '            return "data:image/jpeg;base64," + _b64.b64encode(p.read_bytes()).decode()\n'
        '        html = html.replace("__PLAYER_WHITE__", player_white)\n'
        '        html = html.replace("__BASE__", str(int(base)))\n'
        '        html = html.replace("__INC__", str(int(inc)))\n'
        '        html = html.replace("__DEPTH__", str(int(depth)))\n'
        '        html = html.replace("__NONCE__", str(nonce))\n'
        '        html = html.replace("__SOJU_IDLE__", _b64img("soju_idle.jpg"))\n'
        '        html = html.replace("__SOJU_HAPPY__", _b64img("soju_happy.jpg"))\n'
        '        html = html.replace("__SOJU_SHOCK__", _b64img("soju_shock.jpg"))\n'
        '        html = html.replace("__SOJU_THINK__", _b64img("soju_think.jpg"))\n'
        "        return html"
    )
    new = (
        "        soju_dirs = [\n"
        '            widget.parent / "soju",\n'
        '            here / "soju",\n'
        '            cwd / "soju",\n'
        '            here / "assets" / "soju",\n'
        "        ]\n"
        "        soju_dir = next((d for d in soju_dirs if d.is_dir()), None)\n"
        "        def _b64img(name):\n"
        "            candidates = []\n"
        "            if soju_dir is not None:\n"
        "                candidates.append(soju_dir / name)\n"
        "            for root in (widget.parent, here, cwd):\n"
        "                candidates.append(root / name)\n"
        "            for p in candidates:\n"
        "                if p.exists() and p.is_file():\n"
        '                    return "data:image/jpeg;base64," + _b64.b64encode(p.read_bytes()).decode()\n'
        "            raise FileNotFoundError(\n"
        '                f"Missing Soju asset: {name} (looked in soju/ and next to app.py)"\n'
        "            )\n"
        '        html = html.replace("__PLAYER_WHITE__", player_white)\n'
        '        html = html.replace("__BASE__", str(int(base)))\n'
        '        html = html.replace("__INC__", str(int(inc)))\n'
        '        html = html.replace("__DEPTH__", str(int(depth)))\n'
        '        html = html.replace("__NONCE__", str(nonce))\n'
        "        for placeholder, fname in (\n"
        '            ("__SOJU_IDLE__", "soju_idle.jpg"),\n'
        '            ("__SOJU_HAPPY__", "soju_happy.jpg"),\n'
        '            ("__SOJU_SHOCK__", "soju_shock.jpg"),\n'
        '            ("__SOJU_THINK__", "soju_think.jpg"),\n'
        "        ):\n"
        "            if placeholder in html:\n"
        "                html = html.replace(placeholder, _b64img(fname))\n"
        '        html = html.replace("const light = (r + c) % 2 === 1;", "const light = (r + c) % 2 === 0;")\n'
        "        html = html.replace(\n"
        """            'el.textContent = GLYPH[sq[mi]] || "";',\n"""
        """            'el.textContent = GLYPH[sq[mi]] || ""; if (isWhite(sq[mi])) el.classList.add(\"piece-w\"); if (isBlack(sq[mi])) el.classList.add(\"piece-b\");',\n"""
        "        )\n"
        "        html = html.replace(\n"
        '            ".sq.last { box-shadow: inset 0 0 0 3px rgba(250,204,21,0.7); }",\n'
        '            ".sq.last { box-shadow: inset 0 0 0 3px rgba(250,204,21,0.7); }'
        ' .sq.piece-w{color:#fff8e7!important;-webkit-text-stroke:1.15px #1a1208;text-shadow:0 2px 3px rgba(0,0,0,.55);font-weight:700}'
        ' .sq.piece-b{color:#0a0a0a!important;-webkit-text-stroke:.55px #f3efe6;text-shadow:0 1px 1px rgba(255,255,255,.4),0 2px 3px rgba(0,0,0,.4);font-weight:700}'
        ' .sq.piece-w,.sq.piece-b{font-size:clamp(28px,6.5vw,42px);line-height:1}",\n'
        "        )\n"
        "        return html"
    )
    return code.replace(old, new, 1) if old in code else code
