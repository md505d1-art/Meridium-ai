"""Jarvis-style call patches."""
def apply_call(code: str) -> str:
    reps = [
        ('f"Hey, {uname}. Channel\'s open — I\'m here."',
         'f"At your service, {uname}. All systems online."'),
        ('f"Connected. Residual link stable. What\'s on your mind, {uname}?"',
         'f"Link established. How may I assist you, {uname}?"'),
        ('f"You reached me. No committees on this line. Talk whenever you\'re ready."',
         'f"Channel secure. I am listening, {uname}."'),
        ('"Reply like speech: 1–3 short sentences unless they ask for more. "',
         '"Reply like a polished AI butler (Jarvis-style): calm, precise, slightly witty, loyal. Speech only: 1–3 short sentences unless they ask for more. No markdown. "'),
        ('"Never say you are an AI text model on a call — you are Meridium on the residual channel."',
         '"Never say you are an AI text model — you are Meridium, their personal intelligence, on a live voice channel."'),
        ("Residual voice channel · not a chatbot window",
         "Personal intelligence · voice channel"),
        ('voice_opts = ["Residual calm", "Warm familiar"] + (["Intimate residual"] if warm else [])',
         'voice_opts = ["Jarvis calm", "Warm familiar"] + (["Intimate residual"] if warm else [])'),
        ('"Residual calm": "You are on a live phone call. Speak calmly, in short spoken sentences. No markdown lists."',
         '"Jarvis calm": "Live call. Jarvis-style: composed, efficient, dry wit, short spoken sentences. No markdown."'),
        ('voice_style = st.session_state.get("call_voice_style") or "Residual calm"',
         'voice_style = st.session_state.get("call_voice_style") or "Jarvis calm"'),
        ("return voices.find(v => /en-GB/i.test(v.lang) && /female|google|natural|samantha|moira|zira/i.test(v.name))\n          || voices.find(v => /en-GB/i.test(v.lang))\n          || voices.find(v => /en-US/i.test(v.lang) && /female|google|natural|samantha|zira/i.test(v.name))\n          || voices.find(v => /en-US/i.test(v.lang))\n          || voices.find(v => /^en/i.test(v.lang))\n          || null;",
         "return voices.find(v => /en-GB/i.test(v.lang) && /male|daniel|google uk english male|arthur|rishi/i.test(v.name))\n          || voices.find(v => /en-GB/i.test(v.lang))\n          || voices.find(v => /en-US/i.test(v.lang) && /male|david|alex|google us english/i.test(v.name))\n          || voices.find(v => /en-US/i.test(v.lang))\n          || voices.find(v => /^en/i.test(v.lang))\n          || null;"),
        ('rate = 0.95 if "Warm" in voice_style or "Intimate" in voice_style else 1.02',
         'rate = 0.92 if ("Warm" in voice_style or "Intimate" in voice_style) else 0.96'),
        ("st.components.v1.html(speak_html(spoken, autoplay=auto, rate=rate, pitch=1.0), height=72)",
         "st.components.v1.html(speak_html(spoken, autoplay=auto, rate=rate, pitch=0.9 if 'Jarvis' in str(voice_style) else 1.0), height=72)"),
    ]
    for a, b in reps:
        code = code.replace(a, b)
    return code
