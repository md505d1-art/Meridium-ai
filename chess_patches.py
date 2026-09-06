"""Chess.com board + soft white pieces + soju paths."""
def apply_chess(code: str) -> str:
    old = (
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
    )
    new = (
        "        soju_dir = next((d for d in soju_dirs if d.is_dir()), None)\n"
        "        def _b64img(name):\n"
        "            cands = ([soju_dir / name] if soju_dir else []) + [here / name, widget.parent / name]\n"
        "            for p in cands:\n"
        "                if p.exists() and p.is_file():\n"
        '                    return "data:image/jpeg;base64," + _b64.b64encode(p.read_bytes()).decode()\n'
        '            raise FileNotFoundError(f"Missing Soju asset: {name}")'
    )
    if old in code:
        code = code.replace(old, new, 1)

    marker = (
        'html = html.replace("__SOJU_THINK__", _b64img("soju_think.jpg"))\n'
        "        return html"
    )
    js = (
        "var _p=sq[mi];el.innerHTML=_p?"
        "('<span class=\"pc '+ (isWhite(_p)?'w':'b') +'\">'+(GLYPH[_p]||'')+'</span>'):'';"
    )
    css_old = ".sq.last { box-shadow: inset 0 0 0 3px rgba(250,204,21,0.7); }"
    css_new = (
        css_old
        + ".pc{font-size:clamp(26px,6.2vw,40px);line-height:1;display:flex;align-items:center;"
        + "justify-content:center;width:100%;height:100%;font-weight:600}"
        + ".pc.w{color:#fffef7;-webkit-text-stroke:0.45px rgba(30,20,10,.55);"
        + "text-shadow:0 1px 2px rgba(0,0,0,.28)}"
        + ".pc.b{color:#121212;text-shadow:0 1px 1px rgba(255,255,255,.35),0 1px 2px rgba(0,0,0,.25)}"
    )
    inject = (
        'html = html.replace("__SOJU_THINK__", _b64img("soju_think.jpg"))\n'
        '        html = html.replace(".sq.light { background: #f0d9b5; }", ".sq.light { background: #eeeed2; }")\n'
        '        html = html.replace(".sq.dark { background: #b58863; }", ".sq.dark { background: #769656; }")\n'
        "        html = html.replace("
        + repr('1:"♙",2:"♘",3:"♗",4:"♖",5:"♕",6:"♔"')
        + ", "
        + repr('1:"♟",2:"♞",3:"♝",4:"♜",5:"♛",6:"♚"')
        + ")\n"
        '        html = html.replace("const light = (r + c) % 2 === 1;", "const light = (r + c) % 2 === 0;")\n'
        "        html = html.replace("
        + repr('el.textContent = GLYPH[sq[mi]] || "";')
        + ", "
        + repr(js)
        + ")\n"
        "        html = html.replace("
        + repr(css_old)
        + ", "
        + repr(css_new)
        + ")\n"
        "        return html"
    )
    if marker in code:
        code = code.replace(marker, inject, 1)
    return code


def apply_sfx_to_chess_html(html: str) -> str:
    """Inject Meridium Web-Audio SFX into the chess widget HTML."""
    if "MerSFX" in html and "MerSFX.move" in html:
        return html
    try:
        from pathlib import Path as _P
        engine = (_P(__file__).resolve().parent / "meridium_sfx.js").read_text(encoding="utf-8")
    except Exception:
        engine = ""
    if not engine:
        return html
    if "<script>" in html and "MerSFX" not in html:
        html = html.replace("<script>", "<script>\n" + engine + "\n", 1)
    if "MerSFX.capture" not in html:
        needle = "function afterMove(from, to, snap, side, matBefore, isPlayer) {"
        inject = (
            "function afterMove(from, to, snap, side, matBefore, isPlayer) {\n"
            "    try { var captured = !!(snap && snap.toP); var epCap = snap && snap.epCapP;\n"
            "      if (captured || epCap) { if (window.MerSFX) MerSFX.capture(); }\n"
            "      else if (window.MerSFX) MerSFX.move(); } catch(e) {}"
        )
        if needle in html:
            html = html.replace(needle, inject, 1)
    if "MerSFX.check" not in html:
        html = html.replace(
            'statusEl.innerHTML = (inCheck(turn) ? "Check. " : "") +',
            'try{if(inCheck(turn)&&window.MerSFX)MerSFX.check();}catch(e){} statusEl.innerHTML = (inCheck(turn) ? "Check. " : "") +',
            1,
        )
    if "MerSFX.mate" not in html:
        html = html.replace(
            'statusEl.textContent = "Checkmate — " + winner + " wins";',
            'statusEl.textContent = "Checkmate — " + winner + " wins"; try{if(window.MerSFX)MerSFX.mate();}catch(e){}',
            1,
        )
    if "MerSFX.stalemate" not in html:
        html = html.replace(
            'statusEl.textContent = "Stalemate";',
            'statusEl.textContent = "Stalemate"; try{if(window.MerSFX)MerSFX.stalemate();}catch(e){}',
            1,
        )
    if "MerSFX.select" not in html:
        html = html.replace(
            "selected = mi;\n        legal = legalMovesForSide(mi, turn);",
            "selected = mi;\n        legal = legalMovesForSide(mi, turn); try{if(window.MerSFX)MerSFX.select();}catch(e){}",
            1,
        )
    if "MerSFX.flag" not in html:
        html = html.replace(
            'statusEl.textContent = "Flag — " + (active === "w" ? "Black" : "White") + " wins on time";',
            'statusEl.textContent = "Flag — " + (active === "w" ? "Black" : "White") + " wins on time"; try{if(window.MerSFX)MerSFX.flag();}catch(e){}',
            1,
        )
    return html
