"""
╔══════════════════════════════════════════════════════════════════╗
║         SMART AI INTERVIEW COACH  v3.0                          ║
║  Resume · Voice · 5-Dim Scoring · PDF Report · Video Recording  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import groq, json, re, io, base64, tempfile, os, time
from datetime import datetime
from pathlib import Path

# ── Optional imports (graceful fallback) ─────────────────────────────────────
try:
    import speech_recognition as sr
    SR_OK = True
except ImportError:
    SR_OK = False

# PyAudio is the common failure point — detect separately
PYAUDIO_OK = False
if SR_OK:
    try:
        import pyaudio as _pa  # noqa: F401
        PYAUDIO_OK = True
    except (ImportError, OSError):
        PYAUDIO_OK = False

# SPEECH_OK = SR installed (file-upload path works even without PyAudio)
SPEECH_OK = SR_OK

try:
    from gtts import gTTS
    TTS_OK = True
except ImportError:
    TTS_OK = False

try:
    import pypdf
    PDF_READ_OK = True
except ImportError:
    PDF_READ_OK = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors as rl_colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Smart AI Interview Coach",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
  --bg:        #04060d;
  --bg2:       #080c18;
  --surface:   rgba(255,255,255,.035);
  --border:    rgba(255,255,255,.07);
  --border-hi: rgba(99,102,241,.45);
  --indigo:    #6366f1;
  --violet:    #8b5cf6;
  --emerald:   #10b981;
  --amber:     #f59e0b;
  --rose:      #f43f5e;
  --sky:       #38bdf8;
  --text:      #eef0f8;
  --muted:     rgba(238,240,248,.4);
  --mono:      'JetBrains Mono', monospace;
  --sans:      'Outfit', sans-serif;
}

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 100% 60% at 50% -10%,  rgba(99,102,241,.14) 0%, transparent 65%),
        radial-gradient(ellipse 60%  40% at 90% 90%,   rgba(16,185,129,.07) 0%, transparent 55%),
        radial-gradient(ellipse 40%  30% at 10% 70%,   rgba(139,92,246,.06) 0%, transparent 50%),
        var(--bg) !important;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
footer { display: none !important; }

.block-container { max-width: 1140px !important; padding: 0 2rem 3rem !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--indigo); border-radius: 3px; }

/* ══ HERO ══════════════════════════════════════════════════════ */
.hero-wrap {
    text-align: center;
    padding: 3.5rem 0 2rem;
    position: relative;
}
.hero-wrap::before {
    content: '';
    position: absolute;
    bottom: 0; left: 50%;
    transform: translateX(-50%);
    width: 500px; height: 1px;
    background: linear-gradient(90deg, transparent, var(--indigo), var(--emerald), transparent);
    opacity: .6;
}
.hero-tag {
    display: inline-flex; align-items: center; gap: .5rem;
    font-family: var(--mono);
    font-size: .68rem; letter-spacing: .2em; color: var(--emerald);
    border: 1px solid rgba(16,185,129,.3); border-radius: 2rem;
    padding: .28rem 1rem; margin-bottom: 1.4rem;
    background: rgba(16,185,129,.06);
    animation: fadeSlide .5s ease both;
}
.hero-tag::before { content: '◉'; animation: blink 2s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

.hero h1 {
    font-size: clamp(2.6rem, 5.5vw, 4.2rem);
    font-weight: 900; letter-spacing: -.04em; line-height: 1;
    background: linear-gradient(135deg, #eef0f8 0%, var(--indigo) 45%, var(--violet) 70%, var(--emerald) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: fadeSlide .6s .1s ease both;
}
.hero-sub {
    font-family: var(--mono); font-size: .82rem;
    color: var(--muted); margin-top: .9rem;
    animation: fadeSlide .6s .2s ease both;
}
.hero-pills {
    display: flex; flex-wrap: wrap; justify-content: center; gap: .5rem;
    margin-top: 1.1rem;
    animation: fadeSlide .6s .3s ease both;
}
.hero-pill {
    font-family: var(--mono); font-size: .64rem; letter-spacing: .08em;
    padding: .2rem .7rem; border-radius: 3rem;
    border: 1px solid rgba(255,255,255,.1); color: var(--muted);
}

@keyframes fadeSlide {
    from { opacity: 0; transform: translateY(-16px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ══ STEP RAIL ══════════════════════════════════════════════════ */
.rail {
    display: flex; align-items: flex-start; justify-content: center;
    gap: 0; margin: 2rem 0 2.5rem; position: relative;
}
.rail::before {
    content: ''; position: absolute;
    top: 14px; left: 12%; right: 12%; height: 1px;
    background: var(--border);
}
.rail-item {
    display: flex; flex-direction: column; align-items: center;
    gap: .4rem; flex: 1; max-width: 140px; position: relative; z-index: 1;
}
.rail-dot {
    width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: var(--mono); font-size: .68rem; font-weight: 600;
    transition: all .3s;
}
.rail-dot.done  { background: var(--emerald); color: #fff; box-shadow: 0 0 16px rgba(16,185,129,.5); }
.rail-dot.active{ background: var(--indigo);  color: #fff; box-shadow: 0 0 20px rgba(99,102,241,.7); animation: railPulse 2s infinite; }
.rail-dot.idle  { background: rgba(255,255,255,.06); border: 1px solid var(--border); color: var(--muted); }
@keyframes railPulse { 0%,100%{ box-shadow:0 0 20px rgba(99,102,241,.7); } 50%{ box-shadow:0 0 35px rgba(99,102,241,1); } }
.rail-label {
    font-family: var(--mono); font-size: .58rem; letter-spacing: .12em;
    text-transform: uppercase; text-align: center; max-width: 90px;
}
.rail-label.done   { color: var(--emerald); }
.rail-label.active { color: var(--indigo); }
.rail-label.idle   { color: var(--muted); }

/* ══ CARDS ══════════════════════════════════════════════════════ */
.card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 18px; padding: 1.7rem; position: relative; overflow: hidden;
    animation: cardIn .4s ease both;
    transition: border-color .25s, box-shadow .25s;
}
.card::before {
    content: ''; position: absolute; inset: 0; border-radius: 18px;
    background: linear-gradient(145deg, rgba(99,102,241,.06) 0%, transparent 55%);
    pointer-events: none;
}
.card:hover { border-color: rgba(99,102,241,.3); box-shadow: 0 16px 50px rgba(99,102,241,.08); }
.card-accent-emerald { border-color: rgba(16,185,129,.25) !important; }
.card-accent-emerald::before { background: linear-gradient(145deg, rgba(16,185,129,.06) 0%, transparent 55%) !important; }
.card-accent-violet { border-color: rgba(139,92,246,.25) !important; }

@keyframes cardIn {
    from { opacity:0; transform: translateY(20px); }
    to   { opacity:1; transform: translateY(0); }
}

/* ══ SECTION LABEL ══════════════════════════════════════════════ */
.slabel {
    font-family: var(--mono); font-size: .62rem; letter-spacing: .22em;
    text-transform: uppercase; color: var(--indigo); margin-bottom: .6rem;
}
.slabel-green { color: var(--emerald) !important; }
.slabel-amber { color: var(--amber) !important; }

/* ══ SCORE BADGES ════════════════════════════════════════════════ */
.score-grid {
    display: grid; grid-template-columns: repeat(5, 1fr); gap: .75rem;
    margin: 1.2rem 0;
}
.score-card {
    background: rgba(255,255,255,.025); border: 1px solid var(--border);
    border-radius: 14px; padding: 1rem .8rem; text-align: center;
    animation: cardIn .4s ease both; transition: transform .2s, border-color .2s;
}
.score-card:hover { transform: translateY(-3px); border-color: var(--border-hi); }
.score-num {
    font-size: 1.9rem; font-weight: 900; letter-spacing: -.04em; line-height: 1;
}
.score-dim {
    font-family: var(--mono); font-size: .58rem; letter-spacing: .12em;
    text-transform: uppercase; color: var(--muted); margin-top: .3rem;
}

/* ══ KEYWORD CHIPS ══════════════════════════════════════════════ */
.chips { display: flex; flex-wrap: wrap; gap: .4rem; margin-top: .6rem; }
.chip {
    font-family: var(--mono); font-size: .66rem; letter-spacing: .04em;
    padding: .2rem .6rem; border-radius: 3rem; border: 1px solid;
    animation: chipIn .25s ease both;
}
.chip-ok   { background: rgba(16,185,129,.1);  border-color: rgba(16,185,129,.4);  color: var(--emerald); }
.chip-miss { background: rgba(244,63,94,.1);   border-color: rgba(244,63,94,.3);   color: #fb7185; }
.chip-neu  { background: rgba(99,102,241,.1);  border-color: rgba(99,102,241,.3);  color: #a5b4fc; }
@keyframes chipIn { from{opacity:0;transform:scale(.82)} to{opacity:1;transform:scale(1)} }

/* ══ FEEDBACK BLOCK ═════════════════════════════════════════════ */
.fb {
    background: rgba(99,102,241,.07); border-left: 3px solid var(--indigo);
    border-radius: 0 12px 12px 0; padding: 1rem 1.3rem;
    font-size: .9rem; line-height: 1.75; color: rgba(238,240,248,.82);
    margin-top: .8rem;
}
.fb-green { border-left-color: var(--emerald) !important; background: rgba(16,185,129,.07) !important; }
.fb-amber { border-left-color: var(--amber)   !important; background: rgba(245,158,11,.07) !important; }
.fb-rose  { border-left-color: var(--rose)    !important; background: rgba(244,63,94,.07)  !important; }

/* ══ Q BUBBLE ══════════════════════════════════════════════════ */
.q-bubble {
    background: linear-gradient(135deg, rgba(99,102,241,.13), rgba(99,102,241,.04));
    border: 1px solid rgba(99,102,241,.28); border-radius: 0 16px 16px 16px;
    padding: 1.2rem 1.4rem; font-size: 1.04rem; line-height: 1.7; position: relative;
    animation: cardIn .35s ease both;
}
.q-bubble::before {
    content: 'AI'; position: absolute; top: -1px; left: -1px;
    background: var(--indigo); color: #fff;
    font-family: var(--mono); font-size: .6rem; font-weight: 700;
    padding: .15rem .4rem; border-radius: 5px 0 5px 0;
}

/* ══ INPUTS ════════════════════════════════════════════════════ */
[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,.03) !important;
    border: 1px solid rgba(255,255,255,.1) !important;
    border-radius: 12px !important; color: var(--text) !important;
    font-family: var(--mono) !important; font-size: .88rem !important;
    transition: border-color .2s, box-shadow .2s !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--indigo) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,.14) !important;
}
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text) !important;
    font-family: var(--sans) !important;
    transition: border-color .2s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--indigo) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,.14) !important;
}
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text) !important;
}

/* ══ BUTTONS ════════════════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, var(--indigo), #4f46e5) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-family: var(--sans) !important;
    font-weight: 600 !important; font-size: .88rem !important;
    letter-spacing: .02em !important; padding: .6rem 1.5rem !important;
    transition: all .2s !important; position: relative; overflow: hidden;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(99,102,241,.45) !important;
}
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, var(--emerald), #059669) !important;
}
[data-testid="stDownloadButton"] > button:hover {
    box-shadow: 0 8px 28px rgba(16,185,129,.4) !important;
}

/* ══ FILE UPLOADER ══════════════════════════════════════════════ */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,.025) !important;
    border: 2px dashed rgba(99,102,241,.3) !important;
    border-radius: 14px !important; padding: .5rem !important;
    transition: border-color .2s !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--indigo) !important; }
[data-testid="stFileUploader"] label { color: var(--text) !important; }

/* ══ PROGRESS ══════════════════════════════════════════════════ */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, var(--indigo), var(--violet), var(--emerald)) !important;
    border-radius: 4px !important;
    animation: shimmer 2.5s linear infinite !important;
    background-size: 200% 100% !important;
}
@keyframes shimmer { 0%{background-position:200%} 100%{background-position:-200%} }

/* ══ TABS ══════════════════════════════════════════════════════ */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(255,255,255,.02) !important;
    border-radius: 12px !important; border: 1px solid var(--border) !important;
    gap: .2rem !important; padding: .25rem !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important; border-radius: 10px !important;
    color: var(--muted) !important; font-family: var(--sans) !important;
    font-weight: 500 !important; font-size: .85rem !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: var(--indigo) !important; color: #fff !important;
}
[data-testid="stTabs"] [data-baseweb="tab-panel"] { padding: 1rem 0 0 !important; }

/* ══ EXPANDER ══════════════════════════════════════════════════ */
[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important; border-radius: 12px !important;
}
[data-testid="stExpander"] summary { color: var(--text) !important; }

/* ══ ALERTS ════════════════════════════════════════════════════ */
[data-testid="stAlert"] {
    background: rgba(99,102,241,.08) !important;
    border: 1px solid rgba(99,102,241,.25) !important;
    border-radius: 10px !important; color: rgba(238,240,248,.8) !important;
}

/* ══ DIVIDER ════════════════════════════════════════════════════ */
.divider {
    height: 1px; margin: 1.5rem 0;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,.35), rgba(16,185,129,.25), transparent);
}

/* ══ VOICE RECORDER ════════════════════════════════════════════ */
.mic-btn {
    display: inline-flex; align-items: center; justify-content: center;
    width: 58px; height: 58px; border-radius: 50%;
    background: linear-gradient(135deg, var(--rose), #be185d);
    border: none; cursor: pointer; font-size: 1.5rem;
    box-shadow: 0 6px 24px rgba(244,63,94,.4);
    transition: all .2s;
}
.mic-btn:hover { transform: scale(1.08); box-shadow: 0 10px 32px rgba(244,63,94,.55); }
.mic-recording { animation: micPulse 1s infinite; }
@keyframes micPulse {
    0%,100%{ box-shadow:0 0 0 0 rgba(244,63,94,.6); }
    50%{ box-shadow:0 0 0 16px rgba(244,63,94,0); }
}
.voice-badge {
    display: inline-flex; align-items: center; gap: .4rem;
    font-family: var(--mono); font-size: .68rem; color: var(--rose);
    border: 1px solid rgba(244,63,94,.3); border-radius: 3rem;
    padding: .2rem .7rem; background: rgba(244,63,94,.07);
    animation: blink 1.5s infinite;
}

/* ══ TYPING DOTS ════════════════════════════════════════════════ */
.dots { display: flex; gap: 4px; align-items: center; padding: .4rem 0; }
.dots span {
    width: 7px; height: 7px; border-radius: 50%; background: var(--indigo);
    animation: dotBounce 1.2s ease infinite;
}
.dots span:nth-child(2) { animation-delay: .18s; background: var(--violet); }
.dots span:nth-child(3) { animation-delay: .36s; background: var(--emerald); }
@keyframes dotBounce { 0%,80%,100%{transform:translateY(0)} 40%{transform:translateY(-9px)} }

/* ══ RESUME HIGHLIGHT ══════════════════════════════════════════ */
.resume-box {
    background: rgba(16,185,129,.05); border: 1px solid rgba(16,185,129,.2);
    border-radius: 12px; padding: 1rem 1.2rem;
    font-family: var(--mono); font-size: .78rem; line-height: 1.8;
    color: rgba(238,240,248,.7); max-height: 200px; overflow-y: auto;
}

/* ══ AUDIO PLAYER ══════════════════════════════════════════════ */
audio {
    width: 100%; border-radius: 8px; height: 38px;
    filter: invert(1) hue-rotate(180deg) brightness(.85);
}

/* ══ HISTORY ENTRY ══════════════════════════════════════════════ */
.hist {
    border-left: 2px solid rgba(99,102,241,.3);
    padding: .6rem 1rem; margin-bottom: .7rem;
    transition: border-color .2s; cursor: default;
}
.hist:hover { border-left-color: var(--indigo); }

/* ══ VIDEO SECTION ══════════════════════════════════════════════ */
.video-wrap {
    background: rgba(0,0,0,.35);
    border: 1px solid rgba(244,63,94,.2);
    border-radius: 16px;
    padding: 1.2rem;
    position: relative;
    overflow: hidden;
}
.video-wrap::before {
    content: '';
    position: absolute; inset: 0; border-radius: 16px;
    background: linear-gradient(145deg, rgba(244,63,94,.05) 0%, transparent 60%);
    pointer-events: none;
}
.rec-badge {
    display: inline-flex; align-items: center; gap: .4rem;
    font-family: var(--mono); font-size: .65rem; letter-spacing: .1em;
    color: var(--rose); border: 1px solid rgba(244,63,94,.35);
    border-radius: 3rem; padding: .2rem .7rem;
    background: rgba(244,63,94,.08);
    animation: recBlink 1.2s infinite;
    margin-bottom: .7rem;
}
@keyframes recBlink { 0%,100%{opacity:1} 50%{opacity:.5} }
.rec-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--rose);
    box-shadow: 0 0 6px var(--rose);
    animation: recBlink 1.2s infinite;
}

.vid-thumb-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: .9rem; margin-top: .8rem;
}
.vid-thumb {
    background: rgba(255,255,255,.03);
    border: 1px solid var(--border);
    border-radius: 12px; overflow: hidden;
    transition: border-color .2s, transform .2s;
    animation: cardIn .35s ease both;
}
.vid-thumb:hover { border-color: var(--rose); transform: translateY(-2px); }
.vid-thumb-label {
    font-family: var(--mono); font-size: .65rem;
    color: var(--muted); padding: .5rem .7rem;
    border-top: 1px solid var(--border);
}

.cam-tip {
    font-family: var(--mono); font-size: .68rem;
    color: var(--muted); line-height: 1.7;
    background: rgba(244,63,94,.05);
    border: 1px solid rgba(244,63,94,.15);
    border-radius: 10px; padding: .7rem 1rem;
    margin-top: .6rem;
}

/* Camera input override */
[data-testid="stCameraInput"] {
    background: rgba(0,0,0,.4) !important;
    border: 2px dashed rgba(244,63,94,.3) !important;
    border-radius: 14px !important;
}
[data-testid="stCameraInput"]:hover {
    border-color: var(--rose) !important;
}
[data-testid="stCameraInput"] button {
    background: linear-gradient(135deg, var(--rose), #be185d) !important;
    border: none !important; border-radius: 8px !important;
    color: #fff !important; font-family: var(--sans) !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
DEFAULTS = {
    "step": 0,
    "groq_key": "",
    "role": "",
    "domain": "Software Engineering",
    "difficulty": "Intermediate",
    "num_q": 5,
    "resume_text": "",
    "use_resume": False,
    "questions": [],
    "current_q": 0,
    "answers": [],
    "evaluations": [],
    "voice_mode": False,
    "tts_enabled": False,
    "candidate_name": "",
    "video_mode": False,
    "video_snapshots": [],    # list of (q_index, image_bytes, timestamp)
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# LLM HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def get_client():
    return groq.Groq(api_key=st.session_state.groq_key)

def llm_call(prompt: str, system: str = "", json_mode: bool = False,
             max_tokens: int = 2000) -> str:
    client = get_client()
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    kwargs = dict(model="llama-3.3-70b-versatile", messages=msgs,
                  max_tokens=max_tokens, temperature=0.7)
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    r = client.chat.completions.create(**kwargs)
    return r.choices[0].message.content.strip()

def extract_resume_info(resume_text: str) -> dict:
    sys = "You are a resume parser. Always respond with valid JSON only."
    prompt = f"""Parse this resume and extract key info.

Resume:
{resume_text[:4000]}

Return JSON:
{{
  "name": "candidate name or empty string",
  "skills": ["list of technical skills"],
  "experience_years": "e.g. 3 years or fresher",
  "education": "highest degree and field",
  "projects": ["project names/titles"],
  "domains": ["relevant technical domains"],
  "summary": "2-sentence professional summary"
}}"""
    raw = llm_call(prompt, sys, json_mode=True)
    return json.loads(raw)

def generate_questions(role, domain, difficulty, num_q, resume_info=None):
    sys = "You are a senior technical interviewer. Always respond with valid JSON only."
    resume_ctx = ""
    if resume_info:
        resume_ctx = f"""
Candidate background:
- Skills: {', '.join(resume_info.get('skills', [])[:10])}
- Experience: {resume_info.get('experience_years', 'unknown')}
- Education: {resume_info.get('education', 'unknown')}
- Projects: {', '.join(resume_info.get('projects', [])[:5])}
Tailor questions to this specific candidate's background."""

    prompt = f"""Generate {num_q} {difficulty.lower()}-level interview questions for a {role} in {domain}.
{resume_ctx}

Return JSON:
{{
  "questions": [
    {{
      "id": 1,
      "question": "...",
      "category": "Technical|Behavioral|System Design|Project|Conceptual",
      "difficulty": "{difficulty}",
      "reference_answer": "2-4 sentence ideal answer",
      "key_concepts": ["4-7 key terms"],
      "follow_up": "one follow-up question"
    }}
  ]
}}"""
    raw = llm_call(prompt, sys, json_mode=True, max_tokens=2500)
    return json.loads(raw)["questions"]

def evaluate_answer(question: dict, user_answer: str) -> dict:
    if not user_answer.strip() or user_answer == "[Skipped]":
        return {
            "overall_score": 0, "clarity_score": 0, "technical_score": 0,
            "communication_score": 0, "depth_score": 0, "confidence_score": 0,
            "covered_keywords": [], "missing_keywords": question.get("key_concepts", []),
            "strengths": "—", "improvements": "Question was skipped.",
            "detailed_feedback": "No answer was provided.",
            "model_answer_hint": question.get("reference_answer", ""),
        }
    sys = "You are an expert technical interviewer. Respond ONLY with valid JSON."
    prompt = f"""Evaluate this interview answer across 5 dimensions.

Question: {question['question']}
Category: {question.get('category','General')}
Reference Answer: {question['reference_answer']}
Key Concepts: {', '.join(question['key_concepts'])}
Candidate Answer: {user_answer}

Return JSON:
{{
  "overall_score":       <0-100>,
  "clarity_score":       <0-100>,
  "technical_score":     <0-100>,
  "communication_score": <0-100>,
  "depth_score":         <0-100>,
  "confidence_score":    <0-100>,
  "covered_keywords":    ["concepts mentioned"],
  "missing_keywords":    ["concepts NOT mentioned"],
  "strengths":           "1-2 sentence strength",
  "improvements":        "1-2 sentence improvement",
  "detailed_feedback":   "3-4 sentence detailed evaluation",
  "model_answer_hint":   "2-3 sentence ideal answer hint"
}}"""
    raw = llm_call(prompt, sys, json_mode=True, max_tokens=1200)
    return json.loads(raw)

def analyze_body_language(image_b64: str, question: str) -> dict:
    """Send webcam snapshot to Groq vision for body language / presence analysis."""
    client = get_client()
    msgs = [{
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
            },
            {
                "type": "text",
                "text": (
                    f'You are an expert interview coach analyzing a candidate\'s on-camera presence.\n'
                    f'Question they are answering: "{question}"\n\n'
                    'Analyze the image and return ONLY valid JSON:\n'
                    '{\n'
                    '  "posture_score": <0-100>,\n'
                    '  "eye_contact_score": <0-100>,\n'
                    '  "confidence_score": <0-100>,\n'
                    '  "overall_presence": <0-100>,\n'
                    '  "posture_feedback": "1 sentence",\n'
                    '  "eye_contact_feedback": "1 sentence",\n'
                    '  "confidence_feedback": "1 sentence",\n'
                    '  "quick_tip": "1 actionable tip to improve on-camera presence"\n'
                    '}'
                )
            }
        ],
    }]
    try:
        r = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=msgs, max_tokens=400,
            response_format={"type": "json_object"}
        )
        return json.loads(r.choices[0].message.content.strip())
    except Exception:
        return {
            "posture_score": 0, "eye_contact_score": 0,
            "confidence_score": 0, "overall_presence": 0,
            "posture_feedback": "Vision analysis unavailable (model may not support images).",
            "eye_contact_feedback": "Try meta-llama/llama-4-scout-17b-16e-instruct on Groq.",
            "confidence_feedback": "—",
            "quick_tip": "Ensure good lighting and look directly into the camera."
        }

def generate_overall_summary(evs: list, role: str, resume_info: dict = None) -> str:
    scores = [e.get("overall_score", 0) for e in evs]
    avg = sum(scores) / len(scores) if scores else 0
    sys = "You are a career coach writing professional interview performance summaries."
    ctx = f"Candidate role: {role}\nAverage score: {avg:.0f}/100\nScores per question: {scores}"
    if resume_info:
        ctx += f"\nExperience: {resume_info.get('experience_years', '')}"
    prompt = f"""{ctx}

Write a 4-5 sentence professional performance summary covering:
1. Overall performance assessment
2. Strongest demonstrated competency
3. Key area needing improvement
4. Specific actionable next step
Be specific, honest, and encouraging."""
    return llm_call(prompt, sys, max_tokens=400)

# ══════════════════════════════════════════════════════════════════════════════
# VOICE HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def text_to_speech_bytes(text: str) -> bytes | None:
    if not TTS_OK:
        return None
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception:
        return None

def record_and_transcribe() -> str:
    """Live mic → text. Requires PyAudio. Returns transcript or error string."""
    if not SR_OK:
        return "[SpeechRecognition not installed]"
    if not PYAUDIO_OK:
        return "[PyAudio missing — use the audio file upload instead]"
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as src:
            recognizer.adjust_for_ambient_noise(src, duration=0.5)
            audio = recognizer.listen(src, timeout=15, phrase_time_limit=120)
        return recognizer.recognize_google(audio)
    except sr.WaitTimeoutError:
        return "[No speech detected — try speaking sooner after clicking]"
    except sr.UnknownValueError:
        return "[Could not understand audio — please speak clearly and try again]"
    except sr.RequestError as e:
        return f"[Google Speech API error: {e}]"
    except Exception as e:
        return f"[Recognition error: {e}]"


def transcribe_audio_file(audio_bytes: bytes, mime: str) -> str:
    """Transcribe an uploaded audio file (wav/mp3/ogg/m4a) → text.
    Works WITHOUT PyAudio — only needs SpeechRecognition."""
    if not SR_OK:
        return "[SpeechRecognition not installed — pip install SpeechRecognition]"
    import wave, struct

    recognizer = sr.Recognizer()
    suffix = ".wav"
    if "mp3" in mime:    suffix = ".mp3"
    elif "ogg" in mime:  suffix = ".ogg"
    elif "m4a" in mime or "mp4" in mime: suffix = ".m4a"
    elif "webm" in mime: suffix = ".webm"
    elif "flac" in mime: suffix = ".flac"

    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        # Try ffmpeg conversion to wav for non-wav formats
        wav_path = tmp_path
        if suffix != ".wav":
            wav_path = tmp_path.replace(suffix, "_converted.wav")
            ret = os.system(f'ffmpeg -y -i "{tmp_path}" -ar 16000 -ac 1 "{wav_path}" -loglevel quiet 2>/dev/null')
            if ret != 0 or not os.path.exists(wav_path):
                # ffmpeg not available — try reading directly anyway
                wav_path = tmp_path

        with sr.AudioFile(wav_path) as src:
            audio = recognizer.record(src)

        result = recognizer.recognize_google(audio)
        return result
    except sr.UnknownValueError:
        return "[Could not understand audio — ensure the recording is clear]"
    except sr.RequestError as e:
        return f"[Google Speech API error: {e}]"
    except Exception as e:
        return f"[Transcription error: {e}]"
    finally:
        try:
            os.unlink(tmp_path)
            if wav_path != tmp_path and os.path.exists(wav_path):
                os.unlink(wav_path)
        except Exception:
            pass

def extract_pdf_text(uploaded_file) -> str:
    if not PDF_READ_OK:
        return uploaded_file.read().decode("utf-8", errors="ignore")
    try:
        reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    except Exception:
        return ""

# ══════════════════════════════════════════════════════════════════════════════
# PDF REPORT GENERATION
# ══════════════════════════════════════════════════════════════════════════════
def score_color_hex(score: int) -> str:
    if score >= 80: return "#10b981"
    if score >= 60: return "#f59e0b"
    if score >= 40: return "#f97316"
    return "#f43f5e"

def score_label(score: int) -> str:
    if score >= 80: return "Excellent"
    if score >= 60: return "Good"
    if score >= 40: return "Fair"
    return "Needs Work"

def generate_pdf_report(
    candidate_name, role, domain, difficulty,
    questions, answers, evaluations, summary
) -> bytes:
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="Smart AI Interview Coach — Report",
    )

    W = A4[0] - 4*cm
    styles = getSampleStyleSheet()

    # Custom styles
    def S(name, **kw):
        return ParagraphStyle(name, fontName="Helvetica", **kw)

    TITLE    = S("Title2",   fontSize=22, fontName="Helvetica-Bold",   textColor=colors.HexColor("#1e1b4b"), spaceAfter=4)
    SUB      = S("Sub",      fontSize=11, fontName="Helvetica",         textColor=colors.HexColor("#4338ca"), spaceAfter=12)
    H2       = S("H2",       fontSize=13, fontName="Helvetica-Bold",   textColor=colors.HexColor("#1e1b4b"), spaceBefore=14, spaceAfter=6)
    H3       = S("H3",       fontSize=10, fontName="Helvetica-Bold",   textColor=colors.HexColor("#374151"), spaceBefore=8,  spaceAfter=4)
    BODY     = S("Body2",    fontSize=9,  leading=14,                   textColor=colors.HexColor("#374151"), spaceAfter=6)
    MONO     = S("Mono",     fontSize=8,  fontName="Courier",           textColor=colors.HexColor("#4b5563"), leading=12)
    SMALL    = S("Small",    fontSize=7.5,                              textColor=colors.HexColor("#9ca3af"))
    HINT     = S("Hint",     fontSize=8.5, fontName="Helvetica-Oblique",textColor=colors.HexColor("#6366f1"), leading=13)
    from reportlab.lib import colors

    story = []

    # ── Cover banner ──────────────────────────────────────────────
    banner_data = [[
        Paragraph("🧠 SMART AI INTERVIEW COACH", ParagraphStyle(
            "BannerT", fontName="Helvetica-Bold", fontSize=14,
            textColor=colors.white, alignment=TA_CENTER)),
        Paragraph("Performance Report", ParagraphStyle(
            "BannerS", fontName="Helvetica", fontSize=9,
            textColor=colors.HexColor("#c7d2fe"), alignment=TA_CENTER)),
    ]]
    banner = Table([[Paragraph(
        f"<b>🧠 Smart AI Interview Coach</b><br/>"
        f"<font size='9' color='#c7d2fe'>Performance Report</font>",
        ParagraphStyle("Ban", fontName="Helvetica-Bold", fontSize=14,
                       textColor=colors.white, alignment=TA_CENTER, leading=20)
    )]], colWidths=[W])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#4338ca")),
        ("ROUNDEDCORNERS", [10]),
        ("TOPPADDING",    (0,0),(-1,-1), 16),
        ("BOTTOMPADDING", (0,0),(-1,-1), 16),
    ]))
    story.append(banner)
    story.append(Spacer(1, 14))

    # ── Meta info ─────────────────────────────────────────────────
    now = datetime.now().strftime("%B %d, %Y  %H:%M")
    meta = [
        ["Candidate",  candidate_name or "—",    "Date",       now],
        ["Role",       role,                      "Domain",     domain],
        ["Difficulty", difficulty,                "Questions",  str(len(questions))],
    ]
    meta_table = Table(meta, colWidths=[2.5*cm, 6.5*cm, 2*cm, 5.5*cm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME",      (0,0),(-1,-1), "Helvetica"),
        ("FONTNAME",      (0,0),(0,-1),  "Helvetica-Bold"),
        ("FONTNAME",      (2,0),(2,-1),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 8.5),
        ("TEXTCOLOR",     (0,0),(0,-1),  colors.HexColor("#4338ca")),
        ("TEXTCOLOR",     (2,0),(2,-1),  colors.HexColor("#4338ca")),
        ("TEXTCOLOR",     (1,0),(1,-1),  colors.HexColor("#1f2937")),
        ("TEXTCOLOR",     (3,0),(3,-1),  colors.HexColor("#1f2937")),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [colors.HexColor("#f8f7ff"), colors.white]),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("BOX",           (0,0),(-1,-1), 0.5, colors.HexColor("#e5e7eb")),
        ("INNERGRID",     (0,0),(-1,-1), 0.3, colors.HexColor("#e5e7eb")),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 16))

    # ── Score summary ─────────────────────────────────────────────
    evs = evaluations
    def avg(key): return sum(e.get(key,0) for e in evs) / max(len(evs),1)

    dims = [
        ("OVERALL",       int(avg("overall_score"))),
        ("CLARITY",       int(avg("clarity_score"))),
        ("TECHNICAL",     int(avg("technical_score"))),
        ("COMMUNICATION", int(avg("communication_score"))),
        ("DEPTH",         int(avg("depth_score"))),
    ]

    story.append(Paragraph("Score Summary", H2))

    score_rows = [[
        Table([[
            Paragraph(f"<b><font size='20'>{val}</font></b>/100",
                      ParagraphStyle("SN", fontName="Helvetica-Bold", fontSize=20,
                                     textColor=colors.HexColor(score_color_hex(val)),
                                     alignment=TA_CENTER)),
            Paragraph(dim, ParagraphStyle("SD", fontName="Helvetica", fontSize=7,
                                          textColor=colors.HexColor("#9ca3af"),
                                          alignment=TA_CENTER)),
            Paragraph(score_label(val), ParagraphStyle("SL", fontName="Helvetica-Bold", fontSize=8,
                                                        textColor=colors.HexColor(score_color_hex(val)),
                                                        alignment=TA_CENTER)),
        ]], colWidths=[(W/5)-4])
        for dim, val in dims
    ]]

    score_tbl = Table(score_rows, colWidths=[(W/5)]*5)
    score_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#f9f9ff")),
        ("BOX",           (0,0),(-1,-1), 0.5, colors.HexColor("#e5e7eb")),
        ("INNERGRID",     (0,0),(-1,-1), 0.3, colors.HexColor("#e5e7eb")),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("ROUNDEDCORNERS",[8]),
    ]))
    story.append(score_tbl)
    story.append(Spacer(1, 16))

    # ── AI Summary ───────────────────────────────────────────────
    story.append(Paragraph("AI Performance Summary", H2))
    story.append(Paragraph(summary, BODY))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width=W, thickness=0.5, color=colors.HexColor("#e5e7eb")))
    story.append(Spacer(1, 12))

    # ── Per-question breakdown ────────────────────────────────────
    story.append(Paragraph("Question-by-Question Breakdown", H2))

    for i, (q, ev, a) in enumerate(zip(questions, evs, answers)):
        sc = ev.get("overall_score", 0)
        col = colors.HexColor(score_color_hex(sc))

        block = []
        # Q header
        q_header = Table([[
            Paragraph(f"Q{i+1}", ParagraphStyle(
                "QN", fontName="Helvetica-Bold", fontSize=11,
                textColor=colors.white, alignment=TA_CENTER)),
            Paragraph(q['question'], ParagraphStyle(
                "QT", fontName="Helvetica-Bold", fontSize=9.5,
                textColor=colors.HexColor("#1e1b4b"))),
            Paragraph(f"<b>{sc}/100</b><br/><font size='7'>{score_label(sc)}</font>",
                      ParagraphStyle("QS", fontName="Helvetica-Bold", fontSize=11,
                                     textColor=col, alignment=TA_RIGHT)),
        ]], colWidths=[1.2*cm, W-3.6*cm, 2.4*cm])
        q_header.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(0,0),   colors.HexColor("#4338ca")),
            ("BACKGROUND",    (1,0),(2,0),   colors.HexColor("#eef2ff")),
            ("TOPPADDING",    (0,0),(-1,-1), 8),
            ("BOTTOMPADDING", (0,0),(-1,-1), 8),
            ("LEFTPADDING",   (0,0),(-1,-1), 8),
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
            ("BOX",           (0,0),(-1,-1), 0.5, colors.HexColor("#c7d2fe")),
        ]))
        block.append(q_header)

        # Scores mini row
        score_keys = [("Clarity",ev.get("clarity_score",0)),
                      ("Technical",ev.get("technical_score",0)),
                      ("Communication",ev.get("communication_score",0)),
                      ("Depth",ev.get("depth_score",0)),
                      ("Confidence",ev.get("confidence_score",0))]
        mini_cells = []
        for lbl, val in score_keys:
            mini_cells.append(Paragraph(
                f"<b><font color='{score_color_hex(val)}'>{val}</font></b><br/>"
                f"<font size='6.5' color='#9ca3af'>{lbl}</font>",
                ParagraphStyle("MC", fontName="Helvetica", fontSize=9,
                               alignment=TA_CENTER, leading=12)))
        mini_tbl = Table([mini_cells], colWidths=[W/5]*5)
        mini_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#f8f7ff")),
            ("TOPPADDING",    (0,0),(-1,-1), 5),
            ("BOTTOMPADDING", (0,0),(-1,-1), 5),
            ("BOX",           (0,0),(-1,-1), 0.4, colors.HexColor("#e5e7eb")),
            ("INNERGRID",     (0,0),(-1,-1), 0.3, colors.HexColor("#e5e7eb")),
        ]))
        block.append(mini_tbl)

        # Answer
        ans_text = a if a and a != "[Skipped]" else "(Skipped)"
        block.append(Spacer(1, 6))
        block.append(Paragraph("Your Answer:", H3))
        block.append(Paragraph(ans_text[:600], MONO))

        # Keywords
        covered = ev.get("covered_keywords", [])
        missing = ev.get("missing_keywords", [])
        if covered or missing:
            kw_parts = []
            for kw in covered: kw_parts.append(f"<font color='#10b981'>✓ {kw}</font>")
            for kw in missing: kw_parts.append(f"<font color='#f43f5e'>✗ {kw}</font>")
            block.append(Paragraph("Keywords: " + "  ·  ".join(kw_parts),
                                   ParagraphStyle("KW", fontName="Helvetica", fontSize=8,
                                                  leading=14, textColor=colors.HexColor("#374151"))))

        # Feedback
        block.append(Paragraph("Feedback:", H3))
        block.append(Paragraph(ev.get("detailed_feedback",""), BODY))

        if ev.get("model_answer_hint"):
            block.append(Paragraph("Model Answer Hint:", H3))
            block.append(Paragraph(ev.get("model_answer_hint",""), HINT))

        block.append(Spacer(1, 10))
        block.append(HRFlowable(width=W, thickness=0.4, color=colors.HexColor("#e5e7eb")))
        block.append(Spacer(1, 8))

        story.append(KeepTogether(block))

    # ── Footer ────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        f"Generated by Smart AI Interview Coach · {now} · Powered by Groq LLaMA 3.3-70B",
        ParagraphStyle("Foot", fontName="Helvetica", fontSize=7.5,
                       textColor=colors.HexColor("#9ca3af"), alignment=TA_CENTER)
    ))

    doc.build(story)
    buf.seek(0)
    return buf.read()

# ══════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def render_rail():
    step = st.session_state.step
    items = ["Setup", "Interview", "Results"]
    html = '<div class="rail">'
    for i, lbl in enumerate(items):
        if i < step:   cls, icon = "done",   "✓"
        elif i == step: cls, icon = "active", str(i+1)
        else:           cls, icon = "idle",   str(i+1)
        html += (f'<div class="rail-item">'
                 f'<div class="rail-dot {cls}">{icon}</div>'
                 f'<span class="rail-label {cls}">{lbl}</span></div>')
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def score_badge(val: int, dim: str = "Score"):
    c = score_color_hex(val)
    return (f'<div class="score-card">'
            f'<div class="score-num" style="color:{c}">{val}</div>'
            f'<div class="score-dim">{dim}</div>'
            f'</div>')

def render_score_grid(ev: dict):
    dims = [
        ("overall_score",       "Overall"),
        ("clarity_score",       "Clarity"),
        ("technical_score",     "Technical"),
        ("communication_score", "Communication"),
        ("depth_score",         "Depth"),
    ]
    html = '<div class="score-grid">'
    for key, lbl in dims:
        html += score_badge(ev.get(key, 0), lbl)
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 0 — SETUP
# ══════════════════════════════════════════════════════════════════════════════
def page_setup():
    render_rail()

    tab1, tab2 = st.tabs(["⚙ Configure", "📄 Resume Upload"])

    with tab1:
        col_l, col_r = st.columns([1.05, .95], gap="large")

        with col_l:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<p class="slabel">🔑 Credentials & Role</p>', unsafe_allow_html=True)

            name = st.text_input("Your Name (optional)", placeholder="e.g. Aditya Singh",
                                 value=st.session_state.candidate_name)
            st.session_state.candidate_name = name

            api_key = st.text_input("Groq API Key", type="password",
                                    placeholder="gsk_...",
                                    value=st.session_state.groq_key,
                                    help="Free at console.groq.com")
            st.session_state.groq_key = api_key

            role = st.text_input("Target Role", placeholder="e.g. Backend Engineer, ML Engineer",
                                 value=st.session_state.role)
            st.session_state.role = role

            col_a, col_b = st.columns(2)
            with col_a:
                domain = st.selectbox("Domain", [
                    "Software Engineering", "Data Science", "Machine Learning / AI",
                    "DevOps & Cloud", "Frontend Engineering", "Cybersecurity",
                    "Product Management", "System Design", "Mobile Development",
                ], index=0)
                st.session_state.domain = domain
            with col_b:
                difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"],
                                          index=["Beginner","Intermediate","Advanced"]
                                          .index(st.session_state.difficulty))
                st.session_state.difficulty = difficulty

            num_q = st.slider("Number of Questions", 3, 12, st.session_state.num_q)
            st.session_state.num_q = num_q

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown('<p class="slabel">🎙 Voice & Video Options</p>', unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                vm = st.toggle("Voice Input (Mic)", value=st.session_state.voice_mode,
                               disabled=not SR_OK,
                               help="Requires: pip install SpeechRecognition  (PyAudio optional — file upload fallback available)")
                st.session_state.voice_mode = vm
            with c2:
                tts = st.toggle("Read Questions Aloud", value=st.session_state.tts_enabled,
                                disabled=not TTS_OK,
                                help="Requires: pip install gTTS")
                st.session_state.tts_enabled = tts
            with c3:
                vid = st.toggle("📹 Video Recording", value=st.session_state.video_mode,
                                help="Records webcam snapshots per question + AI body language analysis")
                st.session_state.video_mode = vid

            # Status indicators
            if not SR_OK:
                st.markdown('<p style="font-family:var(--mono);font-size:.68rem;color:#f43f5e">✗ pip install SpeechRecognition  (voice input unavailable)</p>', unsafe_allow_html=True)
            elif not PYAUDIO_OK:
                st.markdown("""
<div style="font-family:var(--mono);font-size:.68rem;color:#f59e0b;
     background:rgba(245,158,11,.07);border:1px solid rgba(245,158,11,.2);
     border-radius:8px;padding:.5rem .8rem;line-height:1.7">
  ⚠ PyAudio not found — <strong>file upload fallback active</strong><br>
  <span style="color:rgba(238,240,248,.4)">Record audio on any device → upload → auto-transcribe</span><br>
  Fix: <code>pipwin install pyaudio</code> (Win) · <code>brew install portaudio &amp;&amp; pip install pyaudio</code> (Mac) · <code>sudo apt install python3-pyaudio</code> (Linux)
</div>""", unsafe_allow_html=True)
            else:
                st.markdown('<p style="font-family:var(--mono);font-size:.68rem;color:#10b981">✓ Live mic ready (PyAudio detected)</p>', unsafe_allow_html=True)
            if not TTS_OK:
                st.markdown('<p style="font-family:var(--mono);font-size:.68rem;color:#f59e0b">⚠ pip install gTTS for text-to-speech</p>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀  Start Interview", use_container_width=True):
                if not api_key.strip():
                    st.error("Enter your Groq API key to continue.")
                elif not role.strip():
                    st.error("Enter the target role.")
                else:
                    with st.spinner(""):
                        st.markdown('<div class="dots"><span></span><span></span><span></span></div>',
                                    unsafe_allow_html=True)
                        try:
                            resume_info = None
                            if st.session_state.use_resume and st.session_state.resume_text:
                                resume_info = extract_resume_info(st.session_state.resume_text)
                                st.session_state["resume_info"] = resume_info
                            qs = generate_questions(role, domain, difficulty, num_q, resume_info)
                            st.session_state.questions   = qs
                            st.session_state.current_q   = 0
                            st.session_state.answers     = []
                            st.session_state.evaluations = []
                            st.session_state.step        = 1
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error generating questions: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            st.markdown('<div class="card card-accent-emerald">', unsafe_allow_html=True)
            st.markdown('<p class="slabel slabel-green">📊 Evaluation Dimensions</p>', unsafe_allow_html=True)
            dims = [
                ("🎯", "Overall Score",    "Composite weighted score across all dimensions"),
                ("💬", "Clarity",          "How clear and structured the answer is"),
                ("⚙", "Technical",        "Correctness of technical concepts and facts"),
                ("🗣", "Communication",    "Professional vocabulary and articulation"),
                ("🔬", "Depth",            "Thoroughness and insight beyond basics"),
                ("💪", "Confidence",       "Assertiveness and decisiveness of response"),
            ]
            for icon, name, desc in dims:
                st.markdown(f"""
<div style="display:flex;gap:.8rem;align-items:flex-start;margin-bottom:.9rem">
  <span style="font-size:1.1rem;min-width:1.5rem">{icon}</span>
  <div>
    <div style="font-weight:600;font-size:.88rem">{name}</div>
    <div style="font-family:var(--mono);font-size:.66rem;color:var(--muted);margin-top:.1rem">{desc}</div>
  </div>
</div>""", unsafe_allow_html=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown("""<div style="font-family:var(--mono);font-size:.68rem;color:var(--muted);line-height:1.9">
Model · <span style="color:var(--indigo)">Groq LLaMA 3.3 70B</span><br>
Resume analysis · <span style="color:var(--emerald)">Personalized questions</span><br>
Output · <span style="color:var(--amber)">PDF report + export</span>
</div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card card-accent-emerald">', unsafe_allow_html=True)
        st.markdown('<p class="slabel slabel-green">📄 Resume Upload & Analysis</p>', unsafe_allow_html=True)
        st.markdown("""<p style="font-size:.88rem;color:var(--muted);margin-bottom:1rem">
Upload your resume to get <strong style="color:var(--emerald)">personalized questions</strong> tailored to your background, skills, and projects.</p>""",
                    unsafe_allow_html=True)

        uploaded = st.file_uploader("Upload Resume (PDF or TXT)",
                                    type=["pdf", "txt"],
                                    help="Your resume is used only to generate relevant questions")
        if uploaded:
            if uploaded.type == "application/pdf":
                text = extract_pdf_text(uploaded)
            else:
                text = uploaded.read().decode("utf-8", errors="ignore")

            if text.strip():
                st.session_state.resume_text = text
                st.session_state.use_resume  = True
                st.markdown(f"""
<p class="slabel slabel-green" style="margin-top:1rem">✅ Resume loaded ({len(text.split())} words)</p>
<div class="resume-box">{text[:1200]}{'…' if len(text)>1200 else ''}</div>""",
                            unsafe_allow_html=True)
            else:
                st.error("Could not extract text from this file.")

        if st.session_state.resume_text:
            use = st.checkbox("Use resume for personalized questions",
                              value=st.session_state.use_resume)
            st.session_state.use_resume = use
            if not use:
                st.info("Resume uploaded but will not be used. Toggle on to personalize questions.")
        else:
            st.markdown("""<div class="fb fb-amber" style="margin-top:.6rem">
No resume uploaded yet. You can still start the interview — questions will be based on role & domain.</div>""",
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — INTERVIEW
# ══════════════════════════════════════════════════════════════════════════════
def page_interview():
    render_rail()

    qs    = st.session_state.questions
    idx   = st.session_state.current_q
    total = len(qs)

    # Progress
    st.progress(idx / total)
    st.markdown(f"""
<div style="font-family:var(--mono);font-size:.7rem;color:var(--muted);
     text-align:right;margin-top:-.45rem;margin-bottom:1.1rem">
  <span style="color:var(--indigo);font-weight:600">{idx+1}</span> / {total} questions
</div>""", unsafe_allow_html=True)

    # Answered history
    if st.session_state.evaluations:
        with st.expander(f"📊 Completed answers ({len(st.session_state.evaluations)}/{total})"):
            for i, ev in enumerate(st.session_state.evaluations):
                sc = ev.get("overall_score", 0)
                c  = score_color_hex(sc)
                st.markdown(f"""
<div class="hist">
  <div style="font-size:.83rem;color:var(--muted);margin-bottom:.25rem">
    Q{i+1}: {qs[i]['question'][:72]}…</div>
  <span style="font-family:var(--mono);font-size:.73rem;color:{c};font-weight:600">
    {sc}/100 · {score_label(sc)}</span>
</div>""", unsafe_allow_html=True)

    if idx >= total:
        st.session_state.step = 2
        st.rerun()
        return

    q = qs[idx]

    # Category badge
    cat_map = {"technical":"#6366f1","behavioral":"#ec4899","system design":"#14b8a6",
               "project":"#10b981","conceptual":"#f59e0b"}
    cat = q.get("category","General").lower()
    cat_c = cat_map.get(cat, "#6366f1")

    col_badge, _ = st.columns([.18, .82])
    with col_badge:
        st.markdown(f"""<div style="font-family:var(--mono);font-size:.63rem;
color:{cat_c};border:1px solid {cat_c}55;padding:.2rem .55rem;border-radius:3rem;
background:{cat_c}11;text-align:center;white-space:nowrap">{q.get('category','General')}</div>""",
                    unsafe_allow_html=True)

    # Question bubble
    st.markdown(f'<div class="q-bubble">{q["question"]}</div>', unsafe_allow_html=True)

    # TTS
    if st.session_state.tts_enabled and TTS_OK:
        audio_bytes = text_to_speech_bytes(q["question"])
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")

    # Follow-up hint
    if q.get("follow_up"):
        with st.expander("💡 Possible follow-up"):
            st.markdown(f'<div class="fb">{q["follow_up"]}</div>', unsafe_allow_html=True)

    # ── VIDEO RECORDING PANEL ─────────────────────────────────────
    if st.session_state.video_mode:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="video-wrap">', unsafe_allow_html=True)
        st.markdown(
            '<div class="rec-badge"><div class="rec-dot"></div>LIVE CAMERA · RECORDING</div>',
            unsafe_allow_html=True
        )

        col_cam, col_caminfo = st.columns([.6, .4], gap="large")
        with col_cam:
            snapshot = st.camera_input(
                "📸 Capture a snapshot for AI body language analysis",
                key=f"cam_{idx}",
                label_visibility="collapsed",
            )

            if snapshot is not None:
                img_bytes = snapshot.getvalue()
                img_b64   = base64.b64encode(img_bytes).decode()
                ts        = datetime.now().strftime("%H:%M:%S")

                # Store snapshot
                snaps = st.session_state.video_snapshots
                # Replace existing snap for this question if already captured
                snaps = [s for s in snaps if s[0] != idx]
                snaps.append((idx, img_bytes, img_b64, ts))
                st.session_state.video_snapshots = snaps

                st.markdown(f"""
<div style="font-family:var(--mono);font-size:.65rem;color:var(--emerald);margin-top:.4rem">
  ✓ Snapshot captured at {ts} — will be analysed with your answer
</div>""", unsafe_allow_html=True)

        with col_caminfo:
            snap_this = next(
                (s for s in st.session_state.video_snapshots if s[0] == idx), None
            )
            if snap_this:
                st.markdown('<p class="slabel" style="color:var(--rose)">📷 Captured Snapshot</p>',
                            unsafe_allow_html=True)
                st.image(snap_this[1], use_container_width=True)
                st.markdown(f"""
<div style="font-family:var(--mono);font-size:.63rem;color:var(--muted)">
  Q{idx+1} · {snap_this[3]}
</div>""", unsafe_allow_html=True)
            else:
                st.markdown("""
<div class="cam-tip">
  📹 <strong>How to use:</strong><br>
  1. Allow camera access when prompted<br>
  2. Position yourself well — look at the camera<br>
  3. Hit the capture button to take a snapshot<br>
  4. AI will analyse your posture, eye contact &amp; confidence<br><br>
  💡 Take the snapshot <em>while</em> speaking your answer
</div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Answer input ──────────────────────────────────────────────
    answer = ""

    if st.session_state.voice_mode and SR_OK:

        if PYAUDIO_OK:
            # ── LIVE MIC PATH (PyAudio present) ──────────────────
            col_mic, col_txt = st.columns([.12, .88])
            with col_mic:
                if st.button("🎤", key="mic_btn", help="Click to record (up to 15 sec)"):
                    with st.spinner("🎙 Listening… speak now"):
                        result = record_and_transcribe()
                        if result and not result.startswith("["):
                            st.session_state[f"voice_ans_{idx}"] = result
                            st.success("✓ Transcribed!")
                        else:
                            st.warning(result or "Could not transcribe. Try again.")
            with col_txt:
                default_voice = st.session_state.get(f"voice_ans_{idx}", "")
                answer = st.text_area("Your Answer", value=default_voice, height=160,
                                      placeholder="Speak (🎤) or type here…",
                                      key=f"ans_{idx}", label_visibility="collapsed")

        else:
            # ── FILE UPLOAD FALLBACK (PyAudio missing) ────────────
            st.markdown("""
<div style="background:rgba(245,158,11,.07);border:1px solid rgba(245,158,11,.25);
     border-radius:12px;padding:.9rem 1.1rem;margin-bottom:.8rem">
  <div style="font-family:var(--mono);font-size:.68rem;color:#f59e0b;
       letter-spacing:.1em;margin-bottom:.4rem">⚠ PYAUDIO NOT INSTALLED — FILE UPLOAD MODE</div>
  <div style="font-size:.82rem;color:rgba(238,240,248,.7);line-height:1.6">
    Record your answer on your phone or mic app, then upload the audio file below.<br>
    <span style="font-family:var(--mono);font-size:.7rem;color:rgba(238,240,248,.4)">
    Supported: WAV · MP3 · OGG · M4A · WebM · FLAC</span>
  </div>
</div>""", unsafe_allow_html=True)

            col_up, col_or = st.columns([.55, .45], gap="large")
            with col_up:
                st.markdown('<p class="slabel" style="font-size:.62rem">🎵 Upload Audio Answer</p>',
                            unsafe_allow_html=True)
                audio_file = st.file_uploader(
                    "Upload audio",
                    type=["wav","mp3","ogg","m4a","mp4","webm","flac"],
                    key=f"audio_upload_{idx}",
                    label_visibility="collapsed"
                )
                if audio_file is not None:
                    st.audio(audio_file)
                    if st.button("🔄  Transcribe Audio", key=f"transcribe_{idx}",
                                 use_container_width=True):
                        with st.spinner("Transcribing with Google Speech…"):
                            result = transcribe_audio_file(
                                audio_file.getvalue(), audio_file.type
                            )
                            if result and not result.startswith("["):
                                st.session_state[f"voice_ans_{idx}"] = result
                                st.success("✓ Transcribed successfully!")
                            else:
                                st.warning(result)

            with col_or:
                st.markdown("""
<div style="font-family:var(--mono);font-size:.68rem;color:var(--muted);
     line-height:1.9;padding-top:.4rem">
  <strong style="color:var(--amber)">Quick Fix:</strong><br>
  Windows → <code>pipwin install pyaudio</code><br>
  macOS → <code>brew install portaudio</code><br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>pip install pyaudio</code><br>
  Linux → <code>sudo apt install python3-pyaudio</code>
</div>""", unsafe_allow_html=True)

            default_voice = st.session_state.get(f"voice_ans_{idx}", "")
            answer = st.text_area(
                "Your Answer (transcribed or typed)",
                value=default_voice, height=150,
                placeholder="Transcription will appear here, or type your answer…",
                key=f"ans_{idx}", label_visibility="collapsed"
            )

    elif st.session_state.voice_mode and not SR_OK:
        # SpeechRecognition not installed at all
        st.markdown("""
<div style="background:rgba(244,63,94,.07);border:1px solid rgba(244,63,94,.2);
     border-radius:12px;padding:.9rem 1.1rem;margin-bottom:.8rem">
  <div style="font-family:var(--mono);font-size:.68rem;color:var(--rose);margin-bottom:.3rem">
    ✗ SpeechRecognition not installed</div>
  <code style="font-size:.75rem">pip install SpeechRecognition</code>
  <span style="font-size:.8rem;color:var(--muted)"> — then restart the app</span>
</div>""", unsafe_allow_html=True)
        answer = st.text_area("Your Answer", height=180,
                              placeholder="Type your answer here. Be thorough and specific.",
                              key=f"ans_{idx}", label_visibility="collapsed")
    else:
        answer = st.text_area("Your Answer", height=180,
                              placeholder="Type your answer here. Be thorough and specific.",
                              key=f"ans_{idx}", label_visibility="collapsed")

    # ── Action row ────────────────────────────────────────────────
    ca, cb, cc = st.columns([1, 1, 2])
    with ca:
        if st.button("✓  Submit Answer", use_container_width=True):
            if not answer.strip():
                st.warning("Please enter an answer.")
            else:
                with st.spinner("Evaluating…"):
                    try:
                        ev = evaluate_answer(q, answer)

                        # ── Video / body language analysis ──
                        if st.session_state.video_mode:
                            snap = next(
                                (s for s in st.session_state.video_snapshots if s[0] == idx),
                                None
                            )
                            if snap:
                                bl = analyze_body_language(snap[2], q["question"])
                                ev["body_language"] = bl

                        st.session_state.answers.append(answer)
                        st.session_state.evaluations.append(ev)
                        st.session_state.current_q += 1
                        if st.session_state.current_q >= total:
                            st.session_state.step = 2
                        st.rerun()
                    except Exception as e:
                        st.error(f"Evaluation error: {e}")
    with cb:
        if st.button("⏭  Skip", use_container_width=True):
            st.session_state.answers.append("[Skipped]")
            st.session_state.evaluations.append(evaluate_answer(q, "[Skipped]"))
            st.session_state.current_q += 1
            if st.session_state.current_q >= total:
                st.session_state.step = 2
            st.rerun()
    with cc:
        st.markdown(f"""
<div style="font-family:var(--mono);font-size:.7rem;color:var(--muted);
     padding:.55rem 0;text-align:right">
  Difficulty · <span style="color:var(--indigo)">{q.get('difficulty','—')}</span>
  &nbsp;·&nbsp; Category · <span style="color:var(--violet)">{q.get('category','—')}</span>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — RESULTS
# ══════════════════════════════════════════════════════════════════════════════
def page_results():
    render_rail()

    evs   = st.session_state.evaluations
    qs    = st.session_state.questions
    ans   = st.session_state.answers
    role  = st.session_state.role
    name  = st.session_state.candidate_name
    ri    = st.session_state.get("resume_info", None)

    if not evs:
        st.warning("No evaluations found.")
        return

    def avg(key): return int(sum(e.get(key, 0) for e in evs) / max(len(evs), 1))

    # ── Top banner ────────────────────────────────────────────────
    st.markdown(f"""
<div style="text-align:center;padding:1.5rem 0 .5rem">
  <div style="font-family:var(--mono);font-size:.68rem;letter-spacing:.2em;
       color:var(--emerald);margin-bottom:.4rem">✓ INTERVIEW COMPLETE</div>
  <div style="font-size:clamp(2rem,4vw,3rem);font-weight:900;letter-spacing:-.04em;
       background:linear-gradient(135deg,#eef0f8,var(--indigo),var(--violet));
       -webkit-background-clip:text;-webkit-text-fill-color:transparent">
    {name + ' — ' if name else ''}{role}
  </div>
  <div style="font-family:var(--mono);font-size:.75rem;color:var(--muted);margin-top:.4rem">
    {st.session_state.domain} · {st.session_state.difficulty} · {len(qs)} questions
  </div>
</div>""", unsafe_allow_html=True)

    # ── 5-dim score grid ──────────────────────────────────────────
    dims = [
        ("overall_score",       "Overall"),
        ("clarity_score",       "Clarity"),
        ("technical_score",     "Technical"),
        ("communication_score", "Communication"),
        ("depth_score",         "Depth"),
    ]
    html = '<div class="score-grid">'
    for key, lbl in dims:
        v = avg(key)
        c = score_color_hex(v)
        html += (f'<div class="score-card">'
                 f'<div class="score-num" style="color:{c}">{v}</div>'
                 f'<div style="font-size:.62rem;font-family:var(--mono);color:var(--muted);'
                 f'letter-spacing:.1em;text-transform:uppercase;margin:.25rem 0 .15rem">{lbl}</div>'
                 f'<div style="font-size:.68rem;font-weight:600;color:{c}">{score_label(v)}</div>'
                 f'</div>')
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

    # ── AI summary ────────────────────────────────────────────────
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="slabel">🤖 AI Performance Summary</p>', unsafe_allow_html=True)
    with st.spinner("Generating performance summary…"):
        try:
            summary = generate_overall_summary(evs, role, ri)
        except Exception as e:
            summary = f"Summary unavailable ({e})."
    st.session_state["report_summary"] = summary
    st.markdown(f'<div class="fb">{summary}</div>', unsafe_allow_html=True)

    # ── Per-question breakdown ────────────────────────────────────
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="slabel">📋 Question Breakdown</p>', unsafe_allow_html=True)

    for i, (q, ev, a) in enumerate(zip(qs, evs, ans)):
        sc = ev.get("overall_score", 0)
        c  = score_color_hex(sc)
        with st.expander(f"Q{i+1} · {q['question'][:60]}… · {sc}/100"):
            # 5-dim mini row
            render_score_grid(ev)

            c1, c2 = st.columns([.62, .38])
            with c1:
                st.markdown(f'<div class="q-bubble" style="font-size:.9rem">{q["question"]}</div>',
                            unsafe_allow_html=True)
                st.markdown(f"""
<div style="margin-top:.9rem">
  <p class="slabel" style="font-size:.6rem">YOUR ANSWER</p>
  <div style="background:rgba(255,255,255,.02);border:1px solid var(--border);
       border-radius:10px;padding:.8rem 1rem;font-family:var(--mono);font-size:.8rem;
       line-height:1.65;color:rgba(238,240,248,.7)">{a if a != "[Skipped]" else "<em>Skipped</em>"}</div>
</div>""", unsafe_allow_html=True)

                # Keywords
                covered = ev.get("covered_keywords", [])
                missing = ev.get("missing_keywords", [])
                kw_html = '<div style="margin-top:.9rem"><p class="slabel" style="font-size:.6rem">KEYWORDS</p><div class="chips">'
                for kw in covered: kw_html += f'<span class="chip chip-ok">✓ {kw}</span>'
                for kw in missing: kw_html += f'<span class="chip chip-miss">✗ {kw}</span>'
                kw_html += '</div></div>'
                st.markdown(kw_html, unsafe_allow_html=True)

                # Detailed feedback
                st.markdown(f"""
<div style="margin-top:.9rem">
  <p class="slabel" style="font-size:.6rem">DETAILED FEEDBACK</p>
  <div class="fb">{ev.get('detailed_feedback','')}</div>
</div>""", unsafe_allow_html=True)

                if ev.get("model_answer_hint"):
                    st.markdown(f"""
<div style="margin-top:.7rem">
  <p class="slabel slabel-green" style="font-size:.6rem">MODEL ANSWER HINT</p>
  <div class="fb fb-green">{ev['model_answer_hint']}</div>
</div>""", unsafe_allow_html=True)

            with c2:
                # Strength / Improve
                st.markdown(f"""
<div style="margin-bottom:.7rem">
  <p class="slabel slabel-green" style="font-size:.6rem">STRENGTH</p>
  <div class="fb fb-green" style="font-size:.82rem">{ev.get('strengths','—')}</div>
</div>
<div>
  <p class="slabel slabel-amber" style="font-size:.6rem">IMPROVE</p>
  <div class="fb fb-amber" style="font-size:.82rem">{ev.get('improvements','—')}</div>
</div>""", unsafe_allow_html=True)

                # Reference answer
                if q.get("reference_answer"):
                    st.markdown(f"""
<div style="margin-top:.7rem">
  <p class="slabel" style="font-size:.6rem">REFERENCE ANSWER</p>
  <div style="font-family:var(--mono);font-size:.75rem;color:var(--muted);
       background:rgba(255,255,255,.02);border:1px solid var(--border);
       border-radius:8px;padding:.7rem .9rem;line-height:1.65">{q['reference_answer']}</div>
</div>""", unsafe_allow_html=True)

                # ── Body Language Panel ──
                bl = ev.get("body_language")
                snap_data = next(
                    (s for s in st.session_state.video_snapshots if s[0] == i), None
                )
                if bl or snap_data:
                    st.markdown("""
<div style="margin-top:.9rem">
  <p class="slabel" style="font-size:.6rem;color:var(--rose)">📹 BODY LANGUAGE ANALYSIS</p>
</div>""", unsafe_allow_html=True)
                    if snap_data:
                        st.image(snap_data[1], use_container_width=True)
                    if bl:
                        bl_dims = [
                            ("Posture",     bl.get("posture_score", 0)),
                            ("Eye Contact", bl.get("eye_contact_score", 0)),
                            ("Confidence",  bl.get("confidence_score", 0)),
                            ("Presence",    bl.get("overall_presence", 0)),
                        ]
                        bl_html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:.4rem;margin:.5rem 0">'
                        for lbl, val in bl_dims:
                            c_bl = score_color_hex(val)
                            bl_html += (f'<div style="background:rgba(255,255,255,.02);'
                                        f'border:1px solid {c_bl}33;border-radius:8px;'
                                        f'padding:.5rem .6rem;text-align:center">'
                                        f'<div style="font-size:1.1rem;font-weight:800;color:{c_bl}">{val}</div>'
                                        f'<div style="font-family:var(--mono);font-size:.56rem;'
                                        f'color:var(--muted);text-transform:uppercase;'
                                        f'letter-spacing:.08em">{lbl}</div></div>')
                        bl_html += '</div>'
                        st.markdown(bl_html, unsafe_allow_html=True)
                        tip = bl.get("quick_tip", "")
                        if tip:
                            st.markdown(f"""
<div class="fb" style="border-left-color:var(--rose);background:rgba(244,63,94,.07);
     font-size:.78rem;margin-top:.4rem">
  💡 {tip}
</div>""", unsafe_allow_html=True)

    # ── Video Gallery ──────────────────────────────────────────────
    snaps = st.session_state.video_snapshots
    if snaps:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<p class="slabel" style="color:var(--rose)">📹 Video Snapshot Gallery</p>',
                    unsafe_allow_html=True)

        # Avg body language scores
        bl_scores = [ev.get("body_language", {}).get("overall_presence", 0)
                     for ev in evs if ev.get("body_language")]
        if bl_scores:
            avg_bl = int(sum(bl_scores) / len(bl_scores))
            st.markdown(f"""
<div style="display:inline-flex;align-items:center;gap:.8rem;
     background:rgba(244,63,94,.07);border:1px solid rgba(244,63,94,.2);
     border-radius:10px;padding:.6rem 1.1rem;margin-bottom:1rem">
  <div style="font-size:1.5rem;font-weight:900;color:{score_color_hex(avg_bl)}">{avg_bl}</div>
  <div>
    <div style="font-weight:600;font-size:.85rem">Avg On-Camera Presence</div>
    <div style="font-family:var(--mono);font-size:.62rem;color:var(--muted)">{score_label(avg_bl)}</div>
  </div>
</div>""", unsafe_allow_html=True)

        cols_v = st.columns(min(len(snaps), 4))
        for j, snap in enumerate(snaps):
            q_idx, img_bytes, img_b64, ts = snap
            with cols_v[j % len(cols_v)]:
                st.markdown(f'<div class="vid-thumb">', unsafe_allow_html=True)
                st.image(img_bytes, use_container_width=True)
                sc_bl = evs[q_idx].get("body_language", {}).get("overall_presence", 0) if q_idx < len(evs) else 0
                c_bl  = score_color_hex(sc_bl)
                st.markdown(f"""
<div class="vid-thumb-label">
  Q{q_idx+1} · {ts}
  {f'<span style="float:right;color:{c_bl};font-weight:700">{sc_bl}</span>' if sc_bl else ''}
</div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                # Individual download
                st.download_button(
                    f"⬇ Q{q_idx+1}",
                    img_bytes,
                    file_name=f"snapshot_q{q_idx+1}_{ts.replace(':','')}.jpg",
                    mime="image/jpeg",
                    use_container_width=True,
                    key=f"dl_snap_{j}"
                )

    # ── Actions ───────────────────────────────────────────────────
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    ca, cb, cc, cd = st.columns(4)

    with ca:
        if st.button("🔄  New Interview", use_container_width=True):
            for k in ["questions","answers","evaluations","step","current_q","resume_info","video_snapshots"]:
                st.session_state[k] = DEFAULTS.get(k, [])
            st.rerun()

    with cb:
        if st.button("⚙  Change Setup", use_container_width=True):
            st.session_state.step = 0
            st.session_state.questions = []
            st.session_state.answers   = []
            st.session_state.evaluations = []
            st.rerun()

    with cc:
        # Text export
        txt = f"SMART AI INTERVIEW COACH — REPORT\n{'='*55}\n"
        txt += f"Candidate : {name or '—'}\nRole      : {role}\n"
        txt += f"Domain    : {st.session_state.domain}\nDifficulty: {st.session_state.difficulty}\n"
        txt += f"Date      : {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        txt += f"SCORES\n{'-'*30}\n"
        for k, l in [("overall_score","Overall"),("clarity_score","Clarity"),
                     ("technical_score","Technical"),("communication_score","Communication"),
                     ("depth_score","Depth")]:
            txt += f"{l:20}: {avg(k)}/100\n"
        txt += f"\nSUMMARY\n{'-'*30}\n{summary}\n\n"
        for i,(q,ev,a) in enumerate(zip(qs,evs,ans)):
            txt += f"\nQ{i+1}: {q['question']}\nAnswer: {a}\nScore: {ev.get('overall_score',0)}/100\nFeedback: {ev.get('detailed_feedback','')}\n"
        st.download_button("📥  Export TXT", txt,
                           file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                           mime="text/plain", use_container_width=True)

    with cd:
        if REPORTLAB_OK:
            try:
                pdf_bytes = generate_pdf_report(
                    candidate_name=name, role=role,
                    domain=st.session_state.domain,
                    difficulty=st.session_state.difficulty,
                    questions=qs, answers=ans, evaluations=evs,
                    summary=st.session_state.get("report_summary","")
                )
                st.download_button(
                    "📄  Download PDF Report",
                    pdf_bytes,
                    file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"PDF generation failed: {e}")
        else:
            st.markdown('<p style="font-family:var(--mono);font-size:.7rem;color:var(--amber);padding:.55rem 0">⚠ pip install reportlab for PDF</p>',
                        unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HERO HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-wrap">
  <div class="hero-tag">SMART AI INTERVIEW COACH</div>
  <h1>Your Personal AI<br>Interview Trainer</h1>
  <p class="hero-sub">Groq LLaMA 3.3 · 5-Dimension Scoring · Voice I/O · Video Recording · PDF Report</p>
  <div class="hero-pills">
    <span class="hero-pill">📄 Resume Analysis</span>
    <span class="hero-pill">🤖 AI Interviewer</span>
    <span class="hero-pill">🎙 Voice Interview</span>
    <span class="hero-pill">📹 Video Recording</span>
    <span class="hero-pill">🧍 Body Language AI</span>
    <span class="hero-pill">📊 Performance Report</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
step = st.session_state.step
if   step == 0: page_setup()
elif step == 1: page_interview()
elif step == 2: page_results()
