/* Meridium SFX — Web Audio procedural sounds (no external files) */
(function (global) {
  var AC = null;
  var muted = false;
  try {
    muted = localStorage.getItem("mer_sfx_mute") === "1";
  } catch (e) {}

  function ctx() {
    if (!AC) {
      var C = global.AudioContext || global.webkitAudioContext;
      if (!C) return null;
      AC = new C();
    }
    if (AC.state === "suspended") {
      try { AC.resume(); } catch (e) {}
    }
    return AC;
  }

  function env(g, t0, a, d, s, r, peak) {
    peak = peak == null ? 0.18 : peak;
    g.gain.setValueAtTime(0.0001, t0);
    g.gain.exponentialRampToValueAtTime(peak, t0 + a);
    g.gain.exponentialRampToValueAtTime(Math.max(0.0001, peak * s), t0 + a + d);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + a + d + r);
  }

  function tone(freq, dur, type, peak, slide) {
    if (muted) return;
    var c = ctx();
    if (!c) return;
    var t0 = c.currentTime;
    var o = c.createOscillator();
    var g = c.createGain();
    o.type = type || "sine";
    o.frequency.setValueAtTime(freq, t0);
    if (slide) o.frequency.exponentialRampToValueAtTime(Math.max(20, slide), t0 + dur);
    env(g, t0, 0.01, dur * 0.35, 0.35, dur * 0.55, peak);
    o.connect(g);
    g.connect(c.destination);
    o.start(t0);
    o.stop(t0 + dur + 0.05);
  }

  function noise(dur, peak) {
    if (muted) return;
    var c = ctx();
    if (!c) return;
    var n = Math.floor(c.sampleRate * dur);
    var buf = c.createBuffer(1, n, c.sampleRate);
    var d = buf.getChannelData(0);
    for (var i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / n);
    var src = c.createBufferSource();
    src.buffer = buf;
    var g = c.createGain();
    var f = c.createBiquadFilter();
    f.type = "bandpass";
    f.frequency.value = 1200;
    f.Q.value = 0.7;
    g.gain.value = peak == null ? 0.08 : peak;
    src.connect(f);
    f.connect(g);
    g.connect(c.destination);
    src.start();
  }

  var SFX = {
    setMuted: function (m) {
      muted = !!m;
      try {
        localStorage.setItem("mer_sfx_mute", muted ? "1" : "0");
      } catch (e) {}
    },
    isMuted: function () {
      return muted;
    },
    unlock: function () {
      ctx();
    },
    tick: function () { tone(880, 0.04, "square", 0.04); },
    select: function () { tone(660, 0.05, "triangle", 0.05); },
    move: function () {
      tone(420, 0.07, "triangle", 0.07);
      setTimeout(function () { tone(520, 0.05, "sine", 0.04); }, 30);
    },
    capture: function () {
      tone(180, 0.12, "sawtooth", 0.1, 90);
      noise(0.06, 0.06);
    },
    check: function () {
      tone(740, 0.08, "square", 0.08);
      setTimeout(function () { tone(980, 0.12, "square", 0.07); }, 70);
    },
    mate: function () {
      tone(523, 0.12, "sine", 0.1);
      setTimeout(function () { tone(659, 0.12, "sine", 0.1); }, 100);
      setTimeout(function () { tone(784, 0.22, "sine", 0.12); }, 200);
    },
    stalemate: function () { tone(400, 0.15, "triangle", 0.06, 220); },
    illegal: function () { tone(140, 0.1, "sawtooth", 0.06, 80); },
    puzzleOk: function () {
      tone(660, 0.08, "sine", 0.08);
      setTimeout(function () { tone(880, 0.08, "sine", 0.08); }, 80);
      setTimeout(function () { tone(1175, 0.16, "sine", 0.09); }, 160);
    },
    puzzleBad: function () { tone(220, 0.14, "triangle", 0.07, 110); },
    hint: function () {
      tone(990, 0.06, "sine", 0.05);
      setTimeout(function () { tone(790, 0.08, "sine", 0.04); }, 60);
    },
    unlock: function () {
      tone(523, 0.08, "sine", 0.08);
      setTimeout(function () { tone(659, 0.08, "sine", 0.08); }, 90);
      setTimeout(function () { tone(784, 0.08, "sine", 0.08); }, 180);
      setTimeout(function () { tone(1046, 0.2, "sine", 0.1); }, 270);
    },
    title: function () {
      tone(392, 0.1, "sine", 0.09);
      setTimeout(function () { tone(523, 0.1, "sine", 0.09); }, 110);
      setTimeout(function () { tone(659, 0.1, "sine", 0.09); }, 220);
      setTimeout(function () { tone(784, 0.28, "sine", 0.12); }, 330);
      noise(0.08, 0.04);
    },
    whoosh: function () {
      noise(0.18, 0.07);
      tone(300, 0.2, "sine", 0.05, 80);
    },
    residual: function () {
      noise(0.05, 0.04);
      tone(1500, 0.04, "square", 0.03);
    },
    click: function () { tone(1000, 0.03, "square", 0.03); },
    notify: function () {
      tone(880, 0.07, "sine", 0.07);
      setTimeout(function () { tone(1320, 0.1, "sine", 0.06); }, 80);
    },
    flag: function () {
      tone(300, 0.1, "sawtooth", 0.08);
      setTimeout(function () { tone(200, 0.18, "sawtooth", 0.07, 100); }, 90);
    },
    coach: function () {
      tone(560, 0.06, "triangle", 0.05);
      setTimeout(function () { tone(700, 0.08, "triangle", 0.04); }, 50);
    },
  };

  global.MerSFX = SFX;
  function unlockOnce() {
    SFX.unlock();
    try {
      global.removeEventListener("pointerdown", unlockOnce, true);
      global.removeEventListener("keydown", unlockOnce, true);
    } catch (e) {}
  }
  try {
    global.addEventListener("pointerdown", unlockOnce, true);
    global.addEventListener("keydown", unlockOnce, true);
  } catch (e) {}
})(typeof window !== "undefined" ? window : this);
