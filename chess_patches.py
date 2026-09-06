"""Chess.com-style board; clear white vs black pieces."""
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
            '            raise FileNotFoundError(f"Missing Soju asset: {name}")'
        ),
    )
    marker = (
        '        html = html.replace("__SOJU_THINK__", _b64img("soju_think.jpg"))\n'
        "        return html"
    )
    inject = '        html = html.replace("__SOJU_THINK__", _b64img("soju_think.jpg"))\n        html = html.replace(".sq.light { background: #f0d9b5; }", ".sq.light { background: #eeeed2; }")\n        html = html.replace(".sq.dark { background: #b58863; }", ".sq.dark { background: #769656; }")\n        html = html.replace(\n            \'1:"♙",2:"♘",3:"♗",4:"♖",5:"♕",6:"♔"\',\n            \'1:"♟",2:"♞",3:"♝",4:"♜",5:"♛",6:"♚"\',\n        )\n        html = html.replace("const light = (r + c) % 2 === 1;", "const light = (r + c) % 2 === 0;")\n        html = html.replace(\n            \'el.textContent = GLYPH[sq[mi]] || "";\',\n            "var _p=sq[mi];el.innerHTML=_p?(\'<span class=\\"pc \'+ (isWhite(_p)?\'w\':\'b\') +\'\\">\'+(GLYPH[_p]||\'\')+\'</span>\'):\'\';",\n        )\n        html = html.replace(\n            ".sq.last { box-shadow: inset 0 0 0 3px rgba(250,204,21,0.7); }",\n            ".sq.last { box-shadow: inset 0 0 0 3px rgba(250,204,21,0.7); }.pc{font-size:clamp(26px,6.2vw,40px);line-height:1;display:flex;align-items:center;justify-content:center;width:100%;height:100%;font-weight:700}.pc.w{color:#f8f8f8;-webkit-text-stroke:1.2px #111;text-shadow:-1.5px 0 #111,1.5px 0 #111,0 -1.5px #111,0 1.5px #111,0 2px 4px rgba(0,0,0,.45)}.pc.b{color:#111;text-shadow:0 1px 0 rgba(255,255,255,.4),0 2px 3px rgba(0,0,0,.3)}",\n        )\n        return html'
    if marker in code:
        code = code.replace(marker, inject, 1)
    return code
