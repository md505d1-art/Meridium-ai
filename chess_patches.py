"""Chess.com board + soft white pieces + soju paths + SFX + threefold."""
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
        + repr('1:"\u2659",2:"\u2658",3:"\u2657",4:"\u2656",5:"\u2655",6:"\u2654"')
        + ", "
        + repr('1:"\u265f",2:"\u265e",3:"\u265d",4:"\u265c",5:"\u265b",6:"\u265a"')
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


def apply_threefold_to_chess_html(html: str) -> str:
    """Inject threefold-repetition draw detection into chess widget."""
    if "posCounts" in html and "threefold repetition" in html:
        return html
    if "let gameOver = false;" in html and "posCounts" not in html:
        html = html.replace(
            "let gameOver = false;",
            "let gameOver = false; let posCounts = {}; let posList = [];",
            1,
        )
    helpers = (
        "\n  function posKey() {\n"
        "    var parts = [];\n"
        "    for (var i=0;i<64;i++) parts.push(sq[i]||0);\n"
        "    var cas = (castling.wK?'K':'')+(castling.wQ?'Q':'')+(castling.bK?'k':'')+(castling.bQ?'q':'');\n"
        "    return parts.join('.') + '|' + turn + '|' + cas + '|' + (ep==null?'-':ep);\n"
        "  }\n"
        "  function recordPosition() {\n"
        "    var k = posKey();\n"
        "    posCounts[k] = (posCounts[k] || 0) + 1;\n"
        "    posList.push(k);\n"
        "    return posCounts[k];\n"
        "  }\n"
        "  function unrecordLastPosition() {\n"
        "    if (!posList.length) return;\n"
        "    var k = posList.pop();\n"
        "    if (posCounts[k]) { posCounts[k]--; if (posCounts[k] <= 0) delete posCounts[k]; }\n"
        "  }\n"
    )
    if "function posKey()" not in html and "function endIfNeeded()" in html:
        html = html.replace("function endIfNeeded()", helpers + "\n  function endIfNeeded()", 1)
    needle = "if (endIfNeeded()) { render(); return; }"
    inject = (
        "try { var reps = recordPosition(); if (reps >= 3) { "
        "gameOver = true; active = null; "
        "statusEl.textContent = 'Draw \u2014 threefold repetition'; "
        "try{if(window.MerSFX)MerSFX.stalemate();}catch(e){} "
        "showAnalysis(true); render(); return; } } catch(e) {} "
        "if (endIfNeeded()) { render(); return; }"
    )
    if needle in html and "threefold repetition" not in html:
        html = html.replace(needle, inject, 1)
    if "unrecordLastPosition" in html:
        old_u = "undoMove(history.pop());\n    if (annotations.length) annotations.pop();"
        new_u = "undoMove(history.pop());\n    if (annotations.length) annotations.pop();\n    try{unrecordLastPosition();}catch(e){}"
        if old_u in html and html.count("unrecordLastPosition()") < 2:
            html = html.replace(old_u, new_u, 1)
    if "recordPosition();" not in html and "logMoves();\n  render();" in html:
        html = html.replace(
            "logMoves();\n  render();",
            "try{recordPosition();}catch(e){}\n  logMoves();\n  render();",
            1,
        )
    return html


def apply_sfx_to_chess_html(html: str) -> str:
    """Inject Meridium Web-Audio SFX into the chess widget HTML."""
    if "MerSFX" in html and "MerSFX.move" in html:
        try:
            html = apply_threefold_to_chess_html(html)
        except Exception:
            pass
        return html
    try:
        from pathlib import Path as _P
        engine = (_P(__file__).resolve().parent / "meridium_sfx.js").read_text(encoding="utf-8")
    except Exception:
        engine = ""
    if not engine:
        try:
            return apply_threefold_to_chess_html(html)
        except Exception:
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
            'statusEl.textContent = "Checkmate \u2014 " + winner + " wins";',
            'statusEl.textContent = "Checkmate \u2014 " + winner + " wins"; try{if(window.MerSFX)MerSFX.mate();}catch(e){}',
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
            'statusEl.textContent = "Flag \u2014 " + (active === "w" ? "Black" : "White") + " wins on time";',
            'statusEl.textContent = "Flag \u2014 " + (active === "w" ? "Black" : "White") + " wins on time"; try{if(window.MerSFX)MerSFX.flag();}catch(e){}',
            1,
        )
    try:
        html = apply_threefold_to_chess_html(html)
    except Exception:
        pass
    return html
