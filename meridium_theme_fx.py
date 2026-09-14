"""Theme CSS + canvas FX for Meridium atmospheres."""
from __future__ import annotations
import json

_ALIAS = {
    "aurora": "aurora_north",
    "sakura": "ember_sakura",
}


def _resolve(theme_id: str) -> str:
    tid = theme_id or "default"
    return _ALIAS.get(tid, tid)


def _css_for(theme_id: str) -> str:
    theme_id = _resolve(theme_id)
    base_force = (
        "html, body, .stApp, [data-testid=\"stAppViewContainer\"],"
        "[data-testid=\"stAppViewBlockContainer\"], section.main {"
        "  background-color: transparent !important; }"
        "[data-testid=\"stHeader\"] { background: transparent !important; }"
        "header[data-testid=\"stHeader\"] { background: transparent !important; }"
    )
    packs = {
        "default": base_force + (
            ".stApp, [data-testid=\"stAppViewContainer\"] {"
            "  background: linear-gradient(165deg, #0f0a18 0%, #1a1030 50%, #0c0814 100%) !important; }"
        ),
        "rainy_kyoto": base_force + (
            ".stApp, [data-testid=\"stAppViewContainer\"] {"
            "  background: linear-gradient(180deg, rgba(8,12,24,0.4), rgba(12,16,32,0.65)),"
            "  linear-gradient(180deg, #070b16 0%, #121a2e 45%, #1c2438 100%) !important; }"
            "[data-testid=\"stExpander\"], .stAlert {"
            "  background: rgba(200,210,230,0.10) !important;"
            "  border: 1px solid rgba(180,200,230,0.28) !important;"
            "  border-radius: 22px !important; backdrop-filter: blur(10px) !important; }"
            "h1, h2, h3 { color: #e8eef8 !important; text-shadow: 0 2px 16px rgba(140,170,220,0.45) !important; }"
            ".stButton > button { background: rgba(30,40,70,0.75) !important;"
            "  border: 1px solid rgba(160,180,220,0.35) !important; border-radius: 14px !important; color: #e8eef8 !important; }"
        ),
        "neon_tokyo": base_force + (
            ".stApp, [data-testid=\"stAppViewContainer\"] {"
            "  background: linear-gradient(135deg, #0a0414 0%, #180828 45%, #061018 100%) !important; }"
            "h1, h2, h3 { color: #ff4ec7 !important;"
            "  text-shadow: 0 0 10px #ff4ec7, 0 0 28px #00f0d0 !important; }"
            ".stButton > button { border: 1px solid #00f0d0 !important;"
            "  box-shadow: 0 0 16px rgba(0,240,208,0.35) !important;"
            "  background: rgba(10,5,20,0.85) !important; color: #f5f5f5 !important; border-radius: 4px !important; }"
            "[data-testid=\"stExpander\"] { border: 1px solid rgba(255,78,199,0.45) !important;"
            "  box-shadow: 0 0 24px rgba(255,78,199,0.18) !important; background: rgba(20,8,30,0.7) !important; }"
        ),
        "deep_ocean": base_force + (
            ".stApp, [data-testid=\"stAppViewContainer\"] {"
            "  background: radial-gradient(ellipse at 50% -10%, rgba(40,140,200,0.35), transparent 50%),"
            "  linear-gradient(180deg, #020c14 0%, #0a2840 50%, #021018 100%) !important; }"
            "h1, h2, h3 { color: #7dd3fc !important; text-shadow: 0 0 18px rgba(56,189,248,0.4) !important; }"
            ".stButton > button { background: rgba(8,40,60,0.8) !important;"
            "  border: 1px solid rgba(125,211,252,0.4) !important; color: #e0f2fe !important; border-radius: 999px !important; }"
        ),
        "aurora_north": base_force + (
            ".stApp, [data-testid=\"stAppViewContainer\"] {"
            "  background: linear-gradient(180deg, #04060f 0%, #0a1428 50%, #081418 100%) !important; }"
            "h1, h2, h3 { color: #a7f3d0 !important; text-shadow: 0 0 22px rgba(52,211,153,0.45) !important; }"
            ".stButton > button { background: rgba(10,30,30,0.75) !important;"
            "  border: 1px solid rgba(110,231,183,0.35) !important; color: #ecfdf5 !important; }"
        ),
        "ember_sakura": base_force + (
            ".stApp, [data-testid=\"stAppViewContainer\"] {"
            "  background: linear-gradient(180deg, #2a1520 0%, #4a2840 40%, #1a1018 100%) !important; }"
            "h1, h2, h3 { color: #fecdd3 !important; text-shadow: 0 2px 14px rgba(251,113,133,0.4) !important; }"
            ".stButton > button { background: rgba(60,30,40,0.8) !important;"
            "  border: 1px solid rgba(251,168,196,0.4) !important; color: #fff1f2 !important; border-radius: 16px !important; }"
        ),
        "static_void": base_force + (
            ".stApp, [data-testid=\"stAppViewContainer\"] { background: #050505 !important; }"
            "h1, h2, h3, p, label { color: #d4d4d4 !important; font-family: ui-monospace, monospace !important; }"
            ".stButton > button { background: #0a0a0a !important; color: #e5e5e5 !important;"
            "  border: 1px solid #525252 !important; border-radius: 0 !important; }"
        ),
        "golden_hour": base_force + (
            ".stApp, [data-testid=\"stAppViewContainer\"] {"
            "  background: radial-gradient(ellipse at 85% 5%, rgba(255,180,60,0.4), transparent 42%),"
            "  linear-gradient(180deg, #2a180c 0%, #5a3820 42%, #1a1008 100%) !important; }"
            "h1, h2, h3 { color: #fcd34d !important; text-shadow: 0 2px 16px rgba(251,191,36,0.45) !important; }"
            ".stButton > button { background: linear-gradient(180deg, #c2410c, #7c2d12) !important;"
            "  border: none !important; color: #fffbeb !important; border-radius: 10px !important; }"
        ),
        "cyber_rain": base_force + (
            ".stApp, [data-testid=\"stAppViewContainer\"] { background: #010805 !important; }"
            "h1, h2, h3 { color: #4ade80 !important; text-shadow: 0 0 12px #22c55e !important;"
            "  font-family: ui-monospace, monospace !important; }"
            ".stButton > button { background: #02140a !important; border: 1px solid #16a34a !important;"
            "  color: #bbf7d0 !important; border-radius: 2px !important; font-family: ui-monospace, monospace !important; }"
        ),
        "paper_lantern": base_force + (
            ".stApp, [data-testid=\"stAppViewContainer\"] {"
            "  background: linear-gradient(180deg, #1f1810 0%, #3a2e20 50%, #18120c 100%) !important; }"
            "h1, h2, h3 { color: #fde68a !important; text-shadow: 0 0 20px rgba(251,191,36,0.35) !important; }"
            ".stButton > button { background: rgba(60,45,25,0.85) !important;"
            "  border: 1px solid rgba(253,230,138,0.35) !important; color: #fffbeb !important; border-radius: 20px !important; }"
        ),
    }
    return packs.get(theme_id, packs["default"])


def _js_fx(theme_id: str) -> str:
    theme_id = _resolve(theme_id)
    head = (
        "(function(){try{"
        "var old=document.getElementById('mer-fx-root');if(old)old.remove();"
        "var root=document.createElement('div');root.id='mer-fx-root';"
        "root.style.cssText='position:fixed;inset:0;pointer-events:none;z-index:99990;overflow:hidden;';"
        "var c=document.createElement('canvas');c.id='mer-fx-canvas';"
        "c.style.cssText='position:absolute;inset:0;width:100%;height:100%;';"
        "root.appendChild(c);document.body.appendChild(root);"
        "var ctx=c.getContext('2d');var W,H,particles=[],t0=performance.now();"
        "function resize(){W=c.width=window.innerWidth;H=c.height=window.innerHeight;}"
        "window.addEventListener('resize',resize);resize();"
        "function grain(){ctx.fillStyle='rgba(255,255,255,0.015)';"
        "for(var i=0;i<90;i++)ctx.fillRect(Math.random()*W,Math.random()*H,1.2,1.2);}"
        "function vignette(){var vg=ctx.createRadialGradient(W/2,H/2,H*0.2,W/2,H/2,H*0.85);"
        "vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,'rgba(0,0,0,0.45)');"
        "ctx.fillStyle=vg;ctx.fillRect(0,0,W,H);}"
        "var THEME='" + theme_id + "';"
        "if(window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches){return;}"
    )
    bodies = {
        "rainy_kyoto": (
            "for(var i=0;i<160;i++)particles.push({x:Math.random()*W,y:Math.random()*H,"
            "len:10+Math.random()*22,spd:7+Math.random()*16,thick:0.8+Math.random()*1.4,near:Math.random()>0.55});"
            "var flash=0;function frame(){ctx.clearRect(0,0,W,H);"
            "var g=ctx.createLinearGradient(0,H*0.5,0,H);"
            "g.addColorStop(0,'rgba(180,200,230,0)');g.addColorStop(1,'rgba(180,200,230,0.14)');"
            "ctx.fillStyle=g;ctx.fillRect(0,0,W,H);"
            "for(var i=0;i<particles.length;i++){var p=particles[i];"
            "ctx.strokeStyle=p.near?'rgba(210,230,255,0.55)':'rgba(160,190,230,0.28)';"
            "ctx.lineWidth=p.thick;ctx.beginPath();ctx.moveTo(p.x,p.y);"
            "ctx.lineTo(p.x-1.8,p.y+p.len);ctx.stroke();"
            "p.y+=p.spd;p.x-=1.3;if(p.y>H+20){p.y=-20;p.x=Math.random()*W;}}"
            "if(Math.random()<0.005)flash=10;if(flash>0){ctx.fillStyle='rgba(220,230,255,'+(flash/22)+')';"
            "ctx.fillRect(0,0,W,H);flash--;}"
            "ctx.fillStyle='rgba(255,180,80,0.07)';ctx.beginPath();ctx.arc(W*0.18,H*0.32,70,0,6.28);ctx.fill();"
            "ctx.beginPath();ctx.arc(W*0.78,H*0.26,48,0,6.28);ctx.fill();"
            "grain();vignette();requestAnimationFrame(frame);}requestAnimationFrame(frame);"
        ),
        "neon_tokyo": (
            "function frame(){ctx.clearRect(0,0,W,H);ctx.fillStyle='rgba(0,0,0,0.12)';"
            "for(var y=0;y<H;y+=3)ctx.fillRect(0,y,W,1);var t=performance.now()/1000;"
            "function blob(x,y,r,col){var grd=ctx.createRadialGradient(x,y,0,x,y,r);"
            "grd.addColorStop(0,col);grd.addColorStop(1,'rgba(0,0,0,0)');ctx.fillStyle=grd;ctx.fillRect(x-r,y-r,r*2,r*2);}"
            "blob(W*0.18,H*0.28,200,'rgba(255,0,128,'+(0.14+0.06*Math.sin(t))+')');"
            "blob(W*0.82,H*0.68,220,'rgba(0,255,220,'+(0.12+0.05*Math.cos(t*1.3))+')');"
            "blob(W*0.5,H*0.15,120,'rgba(120,80,255,'+(0.08+0.04*Math.sin(t*0.7))+')');"
            "grain();vignette();requestAnimationFrame(frame);}requestAnimationFrame(frame);"
        ),
        "deep_ocean": (
            "for(var i=0;i<70;i++)particles.push({x:Math.random()*W,y:Math.random()*H,"
            "r:1+Math.random()*4,sp:0.35+Math.random()*1.3,a:0.12+Math.random()*0.4});"
            "function frame(){ctx.clearRect(0,0,W,H);var t=performance.now()/1000;"
            "ctx.fillStyle='rgba(80,180,255,'+(0.05+0.025*Math.sin(t))+')';"
            "ctx.beginPath();ctx.ellipse(W*0.5,0,W*0.75,H*0.28,0,0,6.28);ctx.fill();"
            "for(var i=0;i<particles.length;i++){var p=particles[i];ctx.beginPath();"
            "ctx.fillStyle='rgba(160,220,255,'+p.a+')';ctx.arc(p.x,p.y,p.r,0,6.28);ctx.fill();"
            "p.y-=p.sp;p.x+=Math.sin(t+p.x)*0.35;if(p.y<-10){p.y=H+10;p.x=Math.random()*W;}}"
            "grain();vignette();requestAnimationFrame(frame);}requestAnimationFrame(frame);"
        ),
        "aurora_north": (
            "function frame(){ctx.clearRect(0,0,W,H);var t=performance.now()/2800;"
            "for(var band=0;band<7;band++){ctx.beginPath();var y0=H*0.06+band*H*0.045;ctx.moveTo(0,y0);"
            "for(var x=0;x<=W;x+=10){var y=y0+Math.sin(x*0.007+t*(1+band*0.18)+band)*32+Math.sin(x*0.018-t*1.4)*14;ctx.lineTo(x,y);}"
            "ctx.lineTo(W,0);ctx.lineTo(0,0);ctx.closePath();"
            "var cols=['rgba(50,255,160,0.08)','rgba(140,80,255,0.09)','rgba(80,200,255,0.06)'];"
            "ctx.fillStyle=cols[band%3];ctx.fill();}"
            "for(var s=0;s<40;s++){ctx.fillStyle='rgba(220,240,255,'+(0.15+0.35*Math.random())+')';"
            "ctx.fillRect((s*97%W),(s*53% (H*0.45)),1.5,1.5);}"
            "grain();vignette();requestAnimationFrame(frame);}requestAnimationFrame(frame);"
        ),
        "ember_sakura": (
            "for(var i=0;i<65;i++)particles.push({x:Math.random()*W,y:Math.random()*H,"
            "r:2.5+Math.random()*5.5,sp:0.5+Math.random()*1.6,rot:Math.random()*6,"
            "rs:(Math.random()-0.5)*0.06,a:0.3+Math.random()*0.5});"
            "function frame(){ctx.clearRect(0,0,W,H);"
            "for(var i=0;i<particles.length;i++){var p=particles[i];ctx.save();ctx.translate(p.x,p.y);ctx.rotate(p.rot);"
            "ctx.fillStyle='rgba(255,170,190,'+p.a+')';ctx.beginPath();ctx.ellipse(0,0,p.r,p.r*0.55,0,0,6.28);ctx.fill();ctx.restore();"
            "p.y+=p.sp;p.x+=Math.sin(p.y*0.02)*0.9;p.rot+=p.rs;if(p.y>H+10){p.y=-10;p.x=Math.random()*W;}}"
            "ctx.fillStyle='rgba(255,120,80,0.04)';ctx.fillRect(0,H*0.7,W,H*0.3);"
            "grain();vignette();requestAnimationFrame(frame);}requestAnimationFrame(frame);"
        ),
        "static_void": (
            "var roll=0;function frame(){var img=ctx.createImageData(W,H);var d=img.data;"
            "for(var i=0;i<d.length;i+=4){var v=(Math.random()*48)|0;d[i]=d[i+1]=d[i+2]=v;d[i+3]=36;}"
            "ctx.putImageData(img,0,0);roll=(roll+1)%H;ctx.fillStyle='rgba(180,180,180,0.08)';"
            "ctx.fillRect(0,roll,W,2);vignette();requestAnimationFrame(frame);}requestAnimationFrame(frame);"
        ),
        "golden_hour": (
            "function frame(){ctx.clearRect(0,0,W,H);var t=performance.now()/4000;"
            "var g=ctx.createRadialGradient(W*0.85,H*0.05,10,W*0.7,H*0.2,W*0.65);"
            "g.addColorStop(0,'rgba(255,200,80,'+(0.22+0.06*Math.sin(t))+')');g.addColorStop(1,'rgba(255,160,40,0)');"
            "ctx.fillStyle=g;ctx.fillRect(0,0,W,H);ctx.fillStyle='rgba(255,220,150,0.28)';"
            "for(var i=0;i<40;i++){var x=(Math.sin(t*2+i)*0.5+0.5)*W;var y=(Math.cos(t*1.3+i*0.7)*0.5+0.5)*H*0.65;"
            "ctx.beginPath();ctx.arc(x,y,1.3,0,6.28);ctx.fill();}grain();vignette();"
            "requestAnimationFrame(frame);}requestAnimationFrame(frame);"
        ),
        "cyber_rain": (
            "var cols=Math.floor(W/16),drops=[];for(var i=0;i<cols;i++)drops.push(Math.random()*H);"
            "var chars='01アイウエオカキクケコ';function frame(){ctx.fillStyle='rgba(0,10,4,0.14)';ctx.fillRect(0,0,W,H);"
            "ctx.font='13px monospace';"
            "for(var i=0;i<drops.length;i++){var bright=Math.random()>0.92;"
            "ctx.fillStyle=bright?'#86efac':'#16a34a';var ch=chars[(Math.random()*chars.length)|0];"
            "ctx.fillText(ch,i*16,drops[i]*16);if(drops[i]*16>H&&Math.random()>0.975)drops[i]=0;drops[i]++;}"
            "grain();vignette();requestAnimationFrame(frame);}requestAnimationFrame(frame);"
        ),
        "paper_lantern": (
            "for(var i=0;i=22;i++)particles.push({x:Math.random()*W,y:Math.random()*H,"
            "r:8+Math.random()*20,sp:0.18+Math.random()*0.55,a:0.12+Math.random()*0.28,phase:Math.random()*6});"
            "function frame(){ctx.clearRect(0,0,W,H);var t=performance.now()/1000;"
            "for(var i=0;i<particles.length;i++){var p=particles[i];"
            "var flick=p.a*(0.85+0.15*Math.sin(t*3+p.phase));"
            "var grd=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.r);"
            "grd.addColorStop(0,'rgba(255,200,100,'+flick+')');grd.addColorStop(1,'rgba(255,160,40,0)');"
            "ctx.fillStyle=grd;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,6.28);ctx.fill();"
            "p.y-=p.sp;p.x+=Math.sin(t+p.phase)*0.45;if(p.y<-30){p.y=H+20;p.x=Math.random()*W;}}"
            "grain();vignette();requestAnimationFrame(frame);}requestAnimationFrame(frame);"
        ),
        "default": "",
    }
    # fix typo in paper_lantern init if present - use correct loop
    bodies["paper_lantern"] = (
        "for(var i=0;i<22;i++)particles.push({x:Math.random()*W,y:Math.random()*H,"
        "r:8+Math.random()*20,sp:0.18+Math.random()*0.55,a:0.12+Math.random()*0.28,phase:Math.random()*6});"
        "function frame(){ctx.clearRect(0,0,W,H);var t=performance.now()/1000;"
        "for(var i=0;i<particles.length;i++){var p=particles[i];"
        "var flick=p.a*(0.85+0.15*Math.sin(t*3+p.phase));"
        "var grd=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.r);"
        "grd.addColorStop(0,'rgba(255,200,100,'+flick+')');grd.addColorStop(1,'rgba(255,160,40,0)');"
        "ctx.fillStyle=grd;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,6.28);ctx.fill();"
        "p.y-=p.sp;p.x+=Math.sin(t+p.phase)*0.45;if(p.y<-30){p.y=H+20;p.x=Math.random()*W;}}"
        "grain();vignette();requestAnimationFrame(frame);}requestAnimationFrame(frame);"
    )
    tail = "}catch(e){console&&console.warn('mer-fx',e);}})();"
    return head + bodies.get(theme_id, "") + tail


def theme_engine_html(theme_id: str) -> str:
    theme_id = _resolve(theme_id)
    css = _css_for(theme_id)
    js = _js_fx(theme_id)
    css_json = json.dumps(css)
    bridge = (
        "<script>(function(){try{var css=" + css_json + ";"
        "var doc=window.parent&&window.parent.document?window.parent.document:document;"
        "var old=doc.getElementById('meridium-theme-live');if(old)old.remove();"
        "var s=doc.createElement('style');s.id='meridium-theme-live';s.textContent=css;"
        "doc.head.appendChild(s);}catch(e){}})();</script>"
    )
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'/>"
        "<style>html,body{margin:0;padding:0;background:transparent;overflow:hidden;}</style></head><body>"
        + bridge
        + "<script>" + js + "</script></body></html>"
    )
