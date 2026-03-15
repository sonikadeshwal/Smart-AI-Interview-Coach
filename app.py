"""
╔══════════════════════════════════════════════════════════════╗
║   SMART AI INTERVIEW COACH  v4.0                            ║
║   Amber · Gold · Charcoal  —  Fresh Design                  ║
║   Resume · Voice · 5-Dim Score · PDF Report                 ║
╚══════════════════════════════════════════════════════════════╝
"""
import streamlit as st
import groq, json, io, base64, tempfile, os
from datetime import datetime

# ── optional deps ─────────────────────────────────────────────────────────────
try:
    import speech_recognition as sr
    SR_OK = True
except ImportError:
    SR_OK = False

PYAUDIO_OK = False
if SR_OK:
    try:
        import pyaudio as _pa; PYAUDIO_OK = True  # noqa
    except (ImportError, OSError):
        pass

try:
    from gtts import gTTS; TTS_OK = True
except ImportError:
    TTS_OK = False

try:
    import pypdf; PDF_READ_OK = True
except ImportError:
    PDF_READ_OK = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors as RC
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table,
        TableStyle, HRFlowable, KeepTogether
    )
    RL_OK = True
except ImportError:
    RL_OK = False

# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Smart AI Interview Coach",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM — Amber / Gold / Charcoal
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Fira+Code:wght@300;400;500&display=swap');

/* ── TOKENS ── */
:root {
  --gold:    #f5a623;
  --gold2:   #e8920f;
  --amber:   #fbbf24;
  --amber2:  #d97706;
  --cream:   #fef9ed;
  --warm:    #1c1612;
  --char:    #0f0d0a;
  --char2:   #181410;
  --char3:   #231f19;
  --surface: rgba(245,166,35,.055);
  --border:  rgba(245,166,35,.14);
  --border2: rgba(245,166,35,.28);
  --text:    #f5efe4;
  --muted:   rgba(245,239,228,.42);
  --green:   #4ade80;
  --red:     #f87171;
  --orange:  #fb923c;
  --sans:    'Plus Jakarta Sans', sans-serif;
  --serif:   'Playfair Display', serif;
  --mono:    'Fira Code', monospace;
}

/* ── RESET ── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
  background: var(--char) !important;
  color: var(--text) !important;
  font-family: var(--sans) !important;
}

[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(ellipse 90% 50% at 50% -5%,  rgba(245,166,35,.13) 0%, transparent 60%),
    radial-gradient(ellipse 50% 35% at 5%  80%,  rgba(251,191,36,.07) 0%, transparent 50%),
    radial-gradient(ellipse 40% 30% at 95% 20%,  rgba(245,166,35,.06) 0%, transparent 50%),
    var(--char) !important;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
footer { display: none !important; }

.block-container { max-width: 1120px !important; padding: 0 2rem 4rem !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--char2); }
::-webkit-scrollbar-thumb { background: var(--gold); border-radius: 3px; }

/* ══ HERO ══════════════════════════════════════════════════════════════════ */
.hero {
  text-align: center;
  padding: 4rem 0 2.5rem;
  position: relative;
}
.hero::after {
  content: '';
  position: absolute;
  bottom: 0; left: 50%;
  transform: translateX(-50%);
  width: 460px; height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold), var(--amber), transparent);
}
.hero-eyebrow {
  display: inline-flex; align-items: center; gap: .5rem;
  font-family: var(--mono); font-size: .65rem; letter-spacing: .22em;
  color: var(--gold); text-transform: uppercase;
  border: 1px solid rgba(245,166,35,.3); border-radius: 2rem;
  padding: .28rem 1rem; margin-bottom: 1.5rem;
  background: rgba(245,166,35,.07);
  animation: heroIn .5s ease both;
}
.hero-eyebrow::before {
  content: ''; width: 6px; height: 6px; border-radius: 50%;
  background: var(--gold); box-shadow: 0 0 8px var(--gold);
  animation: goldPulse 2s infinite;
}
@keyframes goldPulse { 0%,100%{opacity:1} 50%{opacity:.4} }

.hero h1 {
  font-family: var(--serif);
  font-size: clamp(2.8rem, 6vw, 4.8rem);
  font-weight: 900; line-height: .96;
  letter-spacing: -.02em;
  background: linear-gradient(160deg, #fef3c7 10%, var(--gold) 40%, var(--amber2) 70%, #f5efe4 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  animation: heroIn .6s .08s ease both;
}
.hero-sub {
  font-family: var(--mono); font-size: .8rem; color: var(--muted);
  margin-top: 1rem; animation: heroIn .6s .18s ease both;
}
.hero-features {
  display: flex; flex-wrap: wrap; justify-content: center; gap: .5rem;
  margin-top: 1.3rem; animation: heroIn .6s .26s ease both;
}
.hero-feat {
  font-family: var(--mono); font-size: .63rem; letter-spacing: .06em;
  padding: .22rem .7rem; border-radius: 3rem;
  border: 1px solid rgba(245,166,35,.2);
  color: rgba(245,239,228,.5);
  background: rgba(245,166,35,.04);
}

@keyframes heroIn {
  from { opacity:0; transform: translateY(-14px); }
  to   { opacity:1; transform: translateY(0); }
}

/* ══ STEP RAIL ═════════════════════════════════════════════════════════════ */
.rail {
  display: flex; justify-content: center; align-items: flex-start;
  gap: 0; margin: 2.2rem 0 2.8rem; position: relative;
}
.rail::before {
  content: ''; position: absolute;
  top: 14px; left: 14%; right: 14%; height: 1px;
  background: var(--border);
}
.rail-item {
  display: flex; flex-direction: column; align-items: center;
  gap: .4rem; flex: 1; max-width: 160px; position: relative; z-index: 1;
}
.rail-dot {
  width: 28px; height: 28px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--mono); font-size: .68rem; font-weight: 600;
  transition: all .3s;
}
.rail-dot.done   { background: var(--green); color: #0f1a12; box-shadow: 0 0 14px rgba(74,222,128,.5); }
.rail-dot.active { background: var(--gold);  color: var(--char); box-shadow: 0 0 20px rgba(245,166,35,.7); animation: dotPulse 2s infinite; }
.rail-dot.idle   { background: rgba(245,166,35,.08); border: 1px solid var(--border); color: var(--muted); }
@keyframes dotPulse { 0%,100%{box-shadow:0 0 20px rgba(245,166,35,.7)} 50%{box-shadow:0 0 36px rgba(245,166,35,1)} }
.rail-lbl {
  font-family: var(--mono); font-size: .58rem; letter-spacing: .12em;
  text-transform: uppercase; text-align: center;
}
.rail-lbl.done   { color: var(--green); }
.rail-lbl.active { color: var(--gold); }
.rail-lbl.idle   { color: var(--muted); }

/* ══ CARDS ══════════════════════════════════════════════════════════════════ */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 18px; padding: 1.8rem;
  position: relative; overflow: hidden;
  animation: cardUp .45s ease both;
  transition: border-color .25s, box-shadow .25s;
}
.card::before {
  content: ''; position: absolute; inset: 0; border-radius: 18px;
  background: linear-gradient(145deg, rgba(245,166,35,.07) 0%, transparent 55%);
  pointer-events: none;
}
.card:hover { border-color: var(--border2); box-shadow: 0 18px 55px rgba(245,166,35,.1); }
.card-green { border-color: rgba(74,222,128,.2) !important; }
.card-green::before { background: linear-gradient(145deg, rgba(74,222,128,.06) 0%, transparent 55%) !important; }
.card-orange { border-color: rgba(251,146,60,.2) !important; }

@keyframes cardUp {
  from { opacity:0; transform: translateY(22px); }
  to   { opacity:1; transform: translateY(0); }
}

/* ══ LABELS / TEXT ══════════════════════════════════════════════════════════ */
.lbl {
  font-family: var(--mono); font-size: .6rem; letter-spacing: .2em;
  text-transform: uppercase; color: var(--gold); margin-bottom: .55rem;
}
.lbl-green  { color: var(--green)  !important; }
.lbl-orange { color: var(--orange) !important; }
.lbl-red    { color: var(--red)    !important; }

/* ══ SCORE CARDS ════════════════════════════════════════════════════════════ */
.scores {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: .8rem;
  margin: 1.2rem 0;
}
.sc {
  background: rgba(245,166,35,.04); border: 1px solid var(--border);
  border-radius: 14px; padding: 1rem .8rem; text-align: center;
  animation: cardUp .4s ease both; transition: transform .2s, border-color .2s;
}
.sc:hover { transform: translateY(-3px); border-color: var(--border2); }
.sc-num {
  font-family: var(--serif); font-size: 2rem; font-weight: 900; line-height: 1;
}
.sc-dim {
  font-family: var(--mono); font-size: .56rem; letter-spacing: .14em;
  text-transform: uppercase; color: var(--muted); margin-top: .3rem;
}
.sc-lbl { font-size: .7rem; font-weight: 600; margin-top: .15rem; }

/* ══ CHIPS ══════════════════════════════════════════════════════════════════ */
.chips { display: flex; flex-wrap: wrap; gap: .4rem; margin-top: .6rem; }
.chip {
  font-family: var(--mono); font-size: .64rem; letter-spacing: .04em;
  padding: .2rem .6rem; border-radius: 3rem; border: 1px solid;
  animation: chipPop .25s ease both;
}
.chip-ok   { background: rgba(74,222,128,.1);  border-color: rgba(74,222,128,.4);  color: var(--green); }
.chip-miss { background: rgba(248,113,113,.1); border-color: rgba(248,113,113,.3); color: var(--red); }
@keyframes chipPop { from{opacity:0;transform:scale(.8)} to{opacity:1;transform:scale(1)} }

/* ══ FEEDBACK BLOCKS ════════════════════════════════════════════════════════ */
.fb {
  border-left: 3px solid var(--gold); border-radius: 0 12px 12px 0;
  padding: .9rem 1.2rem; font-size: .88rem; line-height: 1.72;
  color: rgba(245,239,228,.82); background: rgba(245,166,35,.06);
  margin-top: .7rem;
}
.fb-green  { border-left-color: var(--green)  !important; background: rgba(74,222,128,.06)  !important; }
.fb-orange { border-left-color: var(--orange) !important; background: rgba(251,146,60,.06)  !important; }
.fb-red    { border-left-color: var(--red)    !important; background: rgba(248,113,113,.06) !important; }

/* ══ QUESTION BUBBLE ════════════════════════════════════════════════════════ */
.qbubble {
  background: linear-gradient(135deg, rgba(245,166,35,.12), rgba(245,166,35,.04));
  border: 1px solid rgba(245,166,35,.25); border-radius: 0 16px 16px 16px;
  padding: 1.2rem 1.4rem; font-size: 1.04rem; line-height: 1.7;
  position: relative; animation: cardUp .35s ease both;
}
.qbubble::before {
  content: 'AI'; position: absolute; top: -1px; left: -1px;
  background: var(--gold); color: var(--char);
  font-family: var(--mono); font-size: .58rem; font-weight: 700;
  padding: .15rem .4rem; border-radius: 5px 0 5px 0;
}

/* ══ DIVIDER ════════════════════════════════════════════════════════════════ */
.div {
  height: 1px; margin: 1.6rem 0;
  background: linear-gradient(90deg, transparent, rgba(245,166,35,.4), rgba(251,191,36,.25), transparent);
}

/* ══ INPUTS ═════════════════════════════════════════════════════════════════ */
[data-testid="stTextArea"] textarea {
  background: rgba(245,166,35,.04) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important; color: var(--text) !important;
  font-family: var(--mono) !important; font-size: .87rem !important;
  transition: border-color .2s, box-shadow .2s !important;
}
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--gold) !important;
  box-shadow: 0 0 0 3px rgba(245,166,35,.15) !important;
}
[data-testid="stTextInput"] input {
  background: rgba(245,166,35,.04) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important; color: var(--text) !important;
  font-family: var(--sans) !important;
  transition: border-color .2s !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--gold) !important;
  box-shadow: 0 0 0 3px rgba(245,166,35,.15) !important;
}
[data-testid="stSelectbox"] > div > div,
[data-testid="stSlider"] {
  background: rgba(245,166,35,.04) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important; color: var(--text) !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
  background: var(--gold) !important;
  box-shadow: 0 0 12px rgba(245,166,35,.5) !important;
}

/* ══ BUTTONS ════════════════════════════════════════════════════════════════ */
.stButton > button {
  background: linear-gradient(135deg, var(--gold), var(--gold2)) !important;
  color: var(--char) !important; border: none !important;
  border-radius: 10px !important; font-family: var(--sans) !important;
  font-weight: 700 !important; font-size: .88rem !important;
  padding: .62rem 1.5rem !important;
  transition: all .2s !important; position: relative; overflow: hidden;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 28px rgba(245,166,35,.45) !important;
}
[data-testid="stDownloadButton"] > button {
  background: linear-gradient(135deg, var(--green), #16a34a) !important;
  color: #0d1a0f !important;
}
[data-testid="stDownloadButton"] > button:hover {
  box-shadow: 0 8px 28px rgba(74,222,128,.4) !important;
}

/* ══ PROGRESS ═══════════════════════════════════════════════════════════════ */
[data-testid="stProgress"] > div > div {
  background: linear-gradient(90deg, var(--gold), var(--amber), var(--gold)) !important;
  background-size: 200% 100% !important;
  border-radius: 4px !important;
  animation: shimmer 2s linear infinite !important;
}
@keyframes shimmer { 0%{background-position:200%} 100%{background-position:-200%} }

/* ══ TABS ════════════════════════════════════════════════════════════════════ */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: rgba(245,166,35,.05) !important;
  border-radius: 12px !important; border: 1px solid var(--border) !important;
  gap: .2rem !important; padding: .25rem !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  background: transparent !important; border-radius: 10px !important;
  color: var(--muted) !important; font-family: var(--sans) !important;
  font-weight: 500 !important; font-size: .84rem !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
  background: var(--gold) !important; color: var(--char) !important;
  font-weight: 700 !important;
}

/* ══ EXPANDER ════════════════════════════════════════════════════════════════ */
[data-testid="stExpander"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}
[data-testid="stExpander"] summary { color: var(--text) !important; font-family: var(--sans) !important; }

/* ══ FILE UPLOADER ═══════════════════════════════════════════════════════════ */
[data-testid="stFileUploader"] {
  background: rgba(245,166,35,.04) !important;
  border: 2px dashed rgba(245,166,35,.3) !important;
  border-radius: 14px !important;
  transition: border-color .2s !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--gold) !important; }

/* ══ ALERTS ══════════════════════════════════════════════════════════════════ */
[data-testid="stAlert"] {
  background: rgba(245,166,35,.07) !important;
  border: 1px solid rgba(245,166,35,.25) !important;
  border-radius: 10px !important;
  color: rgba(245,239,228,.8) !important;
}

/* ══ MISC ════════════════════════════════════════════════════════════════════ */
.dots { display: flex; gap: 4px; align-items: center; padding: .5rem 0; }
.dots span {
  width: 7px; height: 7px; border-radius: 50%; background: var(--gold);
  animation: dotBounce 1.2s ease infinite;
}
.dots span:nth-child(2) { animation-delay:.18s; background: var(--amber); }
.dots span:nth-child(3) { animation-delay:.36s; background: var(--amber2); }
@keyframes dotBounce { 0%,80%,100%{transform:translateY(0)} 40%{transform:translateY(-9px)} }

.resume-preview {
  background: rgba(245,166,35,.04); border: 1px solid var(--border);
  border-radius: 10px; padding: .9rem 1.1rem;
  font-family: var(--mono); font-size: .76rem; line-height: 1.8;
  color: var(--muted); max-height: 190px; overflow-y: auto;
}

.hist {
  border-left: 2px solid rgba(245,166,35,.3);
  padding: .6rem 1rem; margin-bottom: .7rem;
  transition: border-color .2s;
}
.hist:hover { border-left-color: var(--gold); }

audio { width:100%; border-radius:8px; height:36px; filter:invert(1) hue-rotate(180deg) brightness(.85); }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
DEFS = dict(
    step=0, groq_key="", role="", domain="Software Engineering",
    difficulty="Intermediate", num_q=5,
    resume_text="", use_resume=False, resume_info={},
    questions=[], current_q=0, answers=[], evaluations=[],
    voice_mode=False, tts_enabled=False,
    candidate_name="", report_summary=""
)
for k, v in DEFS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS — color
# ══════════════════════════════════════════════════════════════════════════════
def sc_color(s):
    if s >= 80: return "#4ade80"
    if s >= 60: return "#f5a623"
    if s >= 40: return "#fb923c"
    return "#f87171"

def sc_label(s):
    if s >= 80: return "Excellent"
    if s >= 60: return "Good"
    if s >= 40: return "Fair"
    return "Needs Work"

# ══════════════════════════════════════════════════════════════════════════════
# LLM
# ══════════════════════════════════════════════════════════════════════════════
def client():
    return groq.Groq(api_key=st.session_state.groq_key)

def llm(prompt, system="", json_mode=False, max_tokens=2000):
    msgs = []
    if system: msgs.append({"role":"system","content":system})
    msgs.append({"role":"user","content":prompt})
    kw = dict(model="llama-3.3-70b-versatile", messages=msgs,
              max_tokens=max_tokens, temperature=0.7)
    if json_mode: kw["response_format"] = {"type":"json_object"}
    r = client().chat.completions.create(**kw)
    return r.choices[0].message.content.strip()

def parse_resume(text):
    p = f"""Parse this resume. Return ONLY valid JSON:
{{
  "name":"", "skills":[], "experience_years":"",
  "education":"", "projects":[], "domains":[], "summary":""
}}

Resume:
{text[:4000]}"""
    return json.loads(llm(p, "You are a resume parser. Return ONLY JSON.", json_mode=True))

def gen_questions(role, domain, diff, n, resume=None):
    ctx = ""
    if resume:
        ctx = f"\nCandidate: skills={resume.get('skills',[][:8])}, exp={resume.get('experience_years','')}, projects={resume.get('projects',[][:4])}\nTailor questions to their background."
    p = f"""Generate {n} {diff.lower()}-level interview questions for a {role} in {domain}.{ctx}
Return ONLY valid JSON:
{{"questions":[{{"id":1,"question":"","category":"Technical|Behavioral|System Design|Conceptual|Project","difficulty":"{diff}","reference_answer":"2-4 sentences","key_concepts":["4-7 terms"],"follow_up":""}}]}}"""
    raw = llm(p, "You are a senior technical interviewer. Return ONLY JSON.", json_mode=True, max_tokens=2800)
    return json.loads(raw)["questions"]

def evaluate(q, ans):
    if not ans.strip() or ans == "[Skipped]":
        return dict(overall=0, clarity=0, technical=0, communication=0, depth=0, confidence=0,
                    covered=[], missing=q.get("key_concepts",[]),
                    strengths="—", improvements="Question skipped.",
                    feedback="No answer provided.", hint=q.get("reference_answer",""))
    p = f"""Evaluate this interview answer.

Question: {q['question']}
Reference: {q['reference_answer']}
Key Concepts: {', '.join(q['key_concepts'])}
Answer: {ans}

Return ONLY valid JSON:
{{"overall":<0-100>,"clarity":<0-100>,"technical":<0-100>,"communication":<0-100>,"depth":<0-100>,"confidence":<0-100>,
"covered":[],"missing":[],"strengths":"1-2 sentences","improvements":"1-2 sentences",
"feedback":"3-4 sentences","hint":"2-3 sentence model answer"}}"""
    raw = llm(p, "You are an expert interviewer. Return ONLY JSON.", json_mode=True, max_tokens=1000)
    return json.loads(raw)

def gen_summary(evs, role, resume=None):
    scores = [e.get("overall",0) for e in evs]
    avg = sum(scores)/max(len(scores),1)
    ctx = f"Role: {role}\nAvg score: {avg:.0f}/100\nPer-question scores: {scores}"
    if resume: ctx += f"\nExp: {resume.get('experience_years','')}"
    p = f"""{ctx}

Write a 4-5 sentence performance summary: overall assessment, strongest skill, key gap, actionable next step. Be honest and encouraging."""
    return llm(p, "You are a career coach.", max_tokens=350)

# ══════════════════════════════════════════════════════════════════════════════
# VOICE HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def tts(text):
    if not TTS_OK: return None
    try:
        t = gTTS(text=text, lang='en')
        b = io.BytesIO(); t.write_to_fp(b); b.seek(0)
        return b.read()
    except: return None

def live_transcribe():
    if not SR_OK: return "[SpeechRecognition not installed]"
    if not PYAUDIO_OK: return "[PyAudio missing — use file upload]"
    try:
        r = sr.Recognizer()
        with sr.Microphone() as s:
            r.adjust_for_ambient_noise(s, duration=0.5)
            audio = r.listen(s, timeout=15, phrase_time_limit=120)
        return r.recognize_google(audio)
    except sr.WaitTimeoutError:    return "[No speech detected — speak sooner]"
    except sr.UnknownValueError:   return "[Could not understand — speak clearly]"
    except sr.RequestError as e:   return f"[API error: {e}]"
    except Exception as e:         return f"[Error: {e}]"

def file_transcribe(data, mime):
    if not SR_OK: return "[SpeechRecognition not installed]"
    suffix = ".wav"
    for ext in [("mp3",".mp3"),("ogg",".ogg"),("m4a",".m4a"),
                ("mp4",".m4a"),("webm",".webm"),("flac",".flac")]:
        if ext[0] in mime: suffix = ext[1]; break
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(data); tmp = f.name
        wav = tmp
        if suffix != ".wav":
            wav = tmp.replace(suffix, "_c.wav")
            if os.system(f'ffmpeg -y -i "{tmp}" -ar 16000 -ac 1 "{wav}" -loglevel quiet 2>/dev/null') != 0:
                wav = tmp
        r = sr.Recognizer()
        with sr.AudioFile(wav) as s:
            audio = r.record(s)
        return r.recognize_google(audio)
    except sr.UnknownValueError: return "[Could not understand audio]"
    except sr.RequestError as e: return f"[API error: {e}]"
    except Exception as e:       return f"[Error: {e}]"
    finally:
        try: os.unlink(tmp)
        except: pass
        try:
            if wav != tmp and os.path.exists(wav): os.unlink(wav)
        except: pass

def extract_resume(f):
    if not PDF_READ_OK: return f.read().decode("utf-8", errors="ignore")
    try:
        r = pypdf.PdfReader(io.BytesIO(f.read()))
        return "\n".join(p.extract_text() or "" for p in r.pages)
    except: return ""

# ══════════════════════════════════════════════════════════════════════════════
# PDF REPORT
# ══════════════════════════════════════════════════════════════════════════════
def build_pdf(name, role, domain, diff, qs, ans, evs, summary):
    if not RL_OK: return None
    buf = io.BytesIO()
    W = A4[0] - 4*cm
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    def S(nm, **kw): return ParagraphStyle(nm, fontName="Helvetica", **kw)
    GOLD   = RC.HexColor("#b45309")
    DARK   = RC.HexColor("#1c1612")
    GRAY   = RC.HexColor("#6b7280")
    BODY_C = RC.HexColor("#374151")

    T  = S("T",  fontSize=22, fontName="Helvetica-Bold",   textColor=DARK, spaceAfter=4, alignment=TA_CENTER)
    SU = S("Su", fontSize=10,                              textColor=GOLD, spaceAfter=14, alignment=TA_CENTER)
    H2 = S("H2", fontSize=13, fontName="Helvetica-Bold",   textColor=DARK, spaceBefore=14, spaceAfter=6)
    H3 = S("H3", fontSize=9.5,fontName="Helvetica-Bold",   textColor=DARK, spaceBefore=8,  spaceAfter=4)
    B  = S("B",  fontSize=9,  leading=14,                  textColor=BODY_C, spaceAfter=5)
    M  = S("M",  fontSize=8,  fontName="Courier",          textColor=RC.HexColor("#4b5563"), leading=12)
    HN = S("HN", fontSize=8.5,fontName="Helvetica-Oblique",textColor=RC.HexColor("#92400e"), leading=13)
    SM = S("SM", fontSize=7.5,                             textColor=GRAY)

    story = []

    # Banner
    banner = Table([[Paragraph(
        "<b>🏆 Smart AI Interview Coach</b><br/>"
        "<font size='9' color='#fef3c7'>Performance Report</font>",
        S("BN", fontName="Helvetica-Bold", fontSize=14, textColor=RC.white,
          alignment=TA_CENTER, leading=20))
    ]], colWidths=[W])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), RC.HexColor("#92400e")),
        ("TOPPADDING",    (0,0),(-1,-1), 16),
        ("BOTTOMPADDING", (0,0),(-1,-1), 16),
        ("ROUNDEDCORNERS", [10]),
    ]))
    story += [banner, Spacer(1,14)]

    # Meta
    now = datetime.now().strftime("%B %d, %Y  %H:%M")
    mt = Table([
        ["Candidate", name or "—",    "Date",       now],
        ["Role",      role,            "Domain",     domain],
        ["Difficulty",diff,            "Questions",  str(len(qs))],
    ], colWidths=[2.5*cm, 6.5*cm, 2*cm, 5.5*cm])
    mt.setStyle(TableStyle([
        ("FONTNAME",(0,0),(-1,-1),"Helvetica"),
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
        ("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1), 8.5),
        ("TEXTCOLOR",(0,0),(0,-1), GOLD),
        ("TEXTCOLOR",(2,0),(2,-1), GOLD),
        ("TEXTCOLOR",(1,0),(1,-1), BODY_C),
        ("TEXTCOLOR",(3,0),(3,-1), BODY_C),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [RC.HexColor("#fefce8"), RC.white]),
        ("TOPPADDING",(0,0),(-1,-1),5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),6),
        ("BOX",(0,0),(-1,-1), 0.5, RC.HexColor("#fde68a")),
        ("INNERGRID",(0,0),(-1,-1), 0.3, RC.HexColor("#fde68a")),
    ]))
    story += [mt, Spacer(1,16)]

    # Scores
    def avg(k): return int(sum(e.get(k,0) for e in evs)/max(len(evs),1))
    def colr(s):
        if s>=80: return "#16a34a"
        if s>=60: return "#b45309"
        if s>=40: return "#c2410c"
        return "#dc2626"
    dims = [("OVERALL","overall"),("CLARITY","clarity"),("TECHNICAL","technical"),
            ("COMMUNICATION","communication"),("DEPTH","depth")]

    story.append(Paragraph("Score Summary", H2))
    sr_cells = []
    for lbl, key in dims:
        v = avg(key)
        sr_cells.append(Table([[
            Paragraph(f"<b><font size='20' color='{colr(v)}'>{v}</font></b>/100",
                      S("SN",fontName="Helvetica-Bold",fontSize=9,alignment=TA_CENTER)),
            Paragraph(lbl, S("SD",fontName="Helvetica",fontSize=6.5,
                              textColor=GRAY,alignment=TA_CENTER)),
            Paragraph(sc_label(v), S("SL",fontName="Helvetica-Bold",fontSize=7.5,
                                     textColor=RC.HexColor(colr(v)),alignment=TA_CENTER)),
        ]], colWidths=[(W/5)-4]))
    tbl_s = Table([sr_cells], colWidths=[(W/5)]*5)
    tbl_s.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), RC.HexColor("#fefce8")),
        ("BOX",(0,0),(-1,-1), 0.5, RC.HexColor("#fde68a")),
        ("INNERGRID",(0,0),(-1,-1), 0.3, RC.HexColor("#fde68a")),
        ("TOPPADDING",(0,0),(-1,-1),10),
        ("BOTTOMPADDING",(0,0),(-1,-1),10),
    ]))
    story += [tbl_s, Spacer(1,16)]

    # Summary
    story += [Paragraph("AI Performance Summary", H2),
              Paragraph(summary, B), Spacer(1,6),
              HRFlowable(width=W, thickness=0.5, color=RC.HexColor("#fde68a")),
              Spacer(1,12)]

    # Per-question
    story.append(Paragraph("Question-by-Question Breakdown", H2))
    for i, (q, ev, a) in enumerate(zip(qs, evs, ans)):
        sc = ev.get("overall",0)
        blk = []

        qh = Table([[
            Paragraph(f"Q{i+1}", S("QN",fontName="Helvetica-Bold",fontSize=11,
                                    textColor=RC.white, alignment=TA_CENTER)),
            Paragraph(q["question"], S("QT",fontName="Helvetica-Bold",fontSize=9.5,
                                       textColor=DARK)),
            Paragraph(f"<b>{sc}/100</b><br/><font size='7'>{sc_label(sc)}</font>",
                      S("QS",fontName="Helvetica-Bold",fontSize=11,
                         textColor=RC.HexColor(colr(sc)), alignment=TA_RIGHT)),
        ]], colWidths=[1.2*cm, W-3.6*cm, 2.4*cm])
        qh.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(0,0), RC.HexColor("#92400e")),
            ("BACKGROUND",(1,0),(2,0), RC.HexColor("#fefce8")),
            ("TOPPADDING",(0,0),(-1,-1),8),
            ("BOTTOMPADDING",(0,0),(-1,-1),8),
            ("LEFTPADDING",(0,0),(-1,-1),8),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("BOX",(0,0),(-1,-1),0.5,RC.HexColor("#fde68a")),
        ]))
        blk.append(qh)

        mini = []
        for lbl, key in [("Clarity","clarity"),("Technical","technical"),
                          ("Communication","communication"),("Depth","depth"),("Confidence","confidence")]:
            v = ev.get(key,0)
            mini.append(Paragraph(
                f"<b><font color='{colr(v)}'>{v}</font></b><br/>"
                f"<font size='6' color='#9ca3af'>{lbl}</font>",
                S("MC",fontName="Helvetica",fontSize=9,alignment=TA_CENTER,leading=12)))
        mt2 = Table([mini], colWidths=[W/5]*5)
        mt2.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),RC.HexColor("#fffbeb")),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("BOX",(0,0),(-1,-1),0.4,RC.HexColor("#fde68a")),
            ("INNERGRID",(0,0),(-1,-1),0.3,RC.HexColor("#fde68a")),
        ]))
        blk.append(mt2)

        ans_text = a if a and a != "[Skipped]" else "(Skipped)"
        blk += [Spacer(1,6), Paragraph("Your Answer:", H3), Paragraph(ans_text[:600], M)]

        covered = ev.get("covered",[])
        missing = ev.get("missing",[])
        if covered or missing:
            kw = "  ·  ".join(
                [f"<font color='#16a34a'>✓ {k}</font>" for k in covered] +
                [f"<font color='#dc2626'>✗ {k}</font>" for k in missing]
            )
            blk.append(Paragraph("Keywords: " + kw,
                                  S("KW",fontName="Helvetica",fontSize=8,
                                    leading=14,textColor=BODY_C)))

        blk += [Paragraph("Feedback:", H3), Paragraph(ev.get("feedback",""), B)]
        if ev.get("hint"):
            blk += [Paragraph("Model Answer:", H3), Paragraph(ev["hint"], HN)]

        blk += [Spacer(1,10),
                HRFlowable(width=W, thickness=0.4, color=RC.HexColor("#fde68a")),
                Spacer(1,8)]
        story.append(KeepTogether(blk))

    story += [Spacer(1,20), Paragraph(
        f"Generated by Smart AI Interview Coach · {now} · Powered by Groq LLaMA 3.3",
        S("FT",fontName="Helvetica",fontSize=7.5,textColor=GRAY,alignment=TA_CENTER)
    )]

    doc.build(story)
    buf.seek(0)
    return buf.read()

# ══════════════════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ══════════════════════════════════════════════════════════════════════════════
def render_rail():
    step = st.session_state.step
    items = ["Setup", "Interview", "Results"]
    html = '<div class="rail">'
    for i, lbl in enumerate(items):
        if i < step:    cls, ico = "done",   "✓"
        elif i == step: cls, ico = "active", str(i+1)
        else:           cls, ico = "idle",   str(i+1)
        html += (f'<div class="rail-item"><div class="rail-dot {cls}">{ico}</div>'
                 f'<span class="rail-lbl {cls}">{lbl}</span></div>')
    st.markdown(html + '</div>', unsafe_allow_html=True)

def score_grid(ev):
    dims = [("overall","Overall"),("clarity","Clarity"),("technical","Technical"),
            ("communication","Communication"),("depth","Depth")]
    html = '<div class="scores">'
    for k, lbl in dims:
        v = ev.get(k, 0); c = sc_color(v)
        html += (f'<div class="sc"><div class="sc-num" style="color:{c}">{v}</div>'
                 f'<div class="sc-dim">{lbl}</div>'
                 f'<div class="sc-lbl" style="color:{c}">{sc_label(v)}</div></div>')
    st.markdown(html + '</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 0 — SETUP
# ══════════════════════════════════════════════════════════════════════════════
def page_setup():
    render_rail()
    tab1, tab2 = st.tabs(["⚙  Configure", "📄  Resume Upload"])

    with tab1:
        cL, cR = st.columns([1.1, .9], gap="large")
        with cL:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<p class="lbl">🔑 Credentials & Role</p>', unsafe_allow_html=True)

            name = st.text_input("Your Name (optional)", placeholder="e.g. Aditya Kumar",
                                 value=st.session_state.candidate_name)
            st.session_state.candidate_name = name

            key = st.text_input("Groq API Key", type="password",
                                placeholder="gsk_...", value=st.session_state.groq_key,
                                help="Free at console.groq.com")
            st.session_state.groq_key = key

            role = st.text_input("Target Role", placeholder="e.g. Backend Engineer, Data Scientist",
                                 value=st.session_state.role)
            st.session_state.role = role

            ca, cb = st.columns(2)
            with ca:
                dom = st.selectbox("Domain", [
                    "Software Engineering","Data Science","Machine Learning / AI",
                    "DevOps & Cloud","Frontend Engineering","Cybersecurity",
                    "Product Management","System Design","Mobile Development",
                ])
                st.session_state.domain = dom
            with cb:
                diff = st.selectbox("Difficulty", ["Beginner","Intermediate","Advanced"],
                                    index=["Beginner","Intermediate","Advanced"]
                                    .index(st.session_state.difficulty))
                st.session_state.difficulty = diff

            nq = st.slider("Number of Questions", 3, 12, st.session_state.num_q)
            st.session_state.num_q = nq

            st.markdown('<div class="div"></div>', unsafe_allow_html=True)
            st.markdown('<p class="lbl">🎙 Voice Options</p>', unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                vm = st.toggle("Voice Input", value=st.session_state.voice_mode,
                               disabled=not SR_OK,
                               help="SpeechRecognition required. File-upload fallback if PyAudio missing.")
                st.session_state.voice_mode = vm
            with c2:
                tts_on = st.toggle("Read Questions Aloud", value=st.session_state.tts_enabled,
                                   disabled=not TTS_OK, help="pip install gTTS")
                st.session_state.tts_enabled = tts_on

            if not SR_OK:
                st.markdown('<p style="font-family:var(--mono);font-size:.66rem;color:var(--red)">✗ pip install SpeechRecognition</p>', unsafe_allow_html=True)
            elif not PYAUDIO_OK:
                st.markdown("""
<div style="font-family:var(--mono);font-size:.66rem;color:var(--gold);
     background:rgba(245,166,35,.07);border:1px solid rgba(245,166,35,.2);
     border-radius:8px;padding:.5rem .8rem;line-height:1.8;margin-top:.3rem">
  ⚠ PyAudio missing — <strong>file-upload mode active</strong><br>
  <span style="color:var(--muted)">Win: <code>pipwin install pyaudio</code> · Mac: <code>brew install portaudio && pip install pyaudio</code> · Linux: <code>sudo apt install python3-pyaudio</code></span>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown('<p style="font-family:var(--mono);font-size:.66rem;color:var(--green)">✓ Live mic ready</p>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀  Generate Interview Questions", use_container_width=True):
                if not key.strip():
                    st.error("Please enter your Groq API key.")
                elif not role.strip():
                    st.error("Please enter the target role.")
                else:
                    with st.spinner(""):
                        st.markdown('<div class="dots"><span></span><span></span><span></span></div>',
                                    unsafe_allow_html=True)
                        try:
                            ri = None
                            if st.session_state.use_resume and st.session_state.resume_text:
                                ri = parse_resume(st.session_state.resume_text)
                                st.session_state.resume_info = ri
                            qs = gen_questions(role, dom, diff, nq, ri)
                            st.session_state.questions = qs
                            st.session_state.current_q = 0
                            st.session_state.answers   = []
                            st.session_state.evaluations = []
                            st.session_state.step = 1
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

        with cR:
            st.markdown('<div class="card card-green">', unsafe_allow_html=True)
            st.markdown('<p class="lbl lbl-green">📊 Evaluation Dimensions</p>', unsafe_allow_html=True)
            for ico, nm, desc in [
                ("🎯","Overall Score",    "Composite weighted score"),
                ("💬","Clarity",          "Structure and coherence"),
                ("⚙","Technical",        "Correctness of concepts and facts"),
                ("🗣","Communication",    "Professional vocabulary & articulation"),
                ("🔬","Depth",            "Thoroughness beyond surface-level"),
                ("💪","Confidence",       "Assertiveness and decisiveness"),
            ]:
                st.markdown(f"""
<div style="display:flex;gap:.8rem;align-items:flex-start;margin-bottom:.9rem">
  <span style="font-size:1.05rem;min-width:1.4rem">{ico}</span>
  <div><div style="font-weight:600;font-size:.87rem">{nm}</div>
  <div style="font-family:var(--mono);font-size:.64rem;color:var(--muted);margin-top:.1rem">{desc}</div></div>
</div>""", unsafe_allow_html=True)
            st.markdown('<div class="div"></div>', unsafe_allow_html=True)
            st.markdown("""<div style="font-family:var(--mono);font-size:.67rem;color:var(--muted);line-height:2">
Model · <span style="color:var(--gold)">Groq LLaMA 3.3 70B</span><br>
Resume · <span style="color:var(--green)">Personalized questions</span><br>
Output · <span style="color:var(--orange)">PDF report + TXT export</span>
</div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card card-green">', unsafe_allow_html=True)
        st.markdown('<p class="lbl lbl-green">📄 Resume Upload</p>', unsafe_allow_html=True)
        st.markdown("""<p style="font-size:.87rem;color:var(--muted);margin-bottom:.9rem">
Upload your resume to get <strong style="color:var(--gold)">personalized questions</strong> based on your skills, experience, and projects.</p>""",
                    unsafe_allow_html=True)

        uf = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf","txt"])
        if uf:
            text = extract_resume(uf) if uf.type == "application/pdf" else uf.read().decode("utf-8", errors="ignore")
            if text.strip():
                st.session_state.resume_text = text
                st.session_state.use_resume  = True
                st.markdown(f"""
<p class="lbl lbl-green" style="margin-top:.8rem">✅ Resume loaded · {len(text.split())} words</p>
<div class="resume-preview">{text[:1200]}{'…' if len(text)>1200 else ''}</div>""",
                            unsafe_allow_html=True)
            else:
                st.error("Could not extract text from this file.")

        if st.session_state.resume_text:
            use = st.checkbox("Use resume for personalized questions",
                              value=st.session_state.use_resume)
            st.session_state.use_resume = use
        else:
            st.markdown('<div class="fb fb-orange" style="margin-top:.6rem">No resume uploaded yet — questions will use role &amp; domain only.</div>',
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

    st.progress(idx / total)
    st.markdown(f"""
<div style="font-family:var(--mono);font-size:.68rem;color:var(--muted);
     text-align:right;margin-top:-.4rem;margin-bottom:1rem">
  Question <span style="color:var(--gold);font-weight:600">{idx+1}</span> of {total}
</div>""", unsafe_allow_html=True)

    if st.session_state.evaluations:
        with st.expander(f"📊 Answered ({len(st.session_state.evaluations)}/{total})"):
            for i, ev in enumerate(st.session_state.evaluations):
                s = ev.get("overall",0)
                st.markdown(f"""
<div class="hist">
  <div style="font-size:.82rem;color:var(--muted);margin-bottom:.2rem">Q{i+1}: {qs[i]['question'][:72]}…</div>
  <span style="font-family:var(--mono);font-size:.72rem;color:{sc_color(s)};font-weight:600">
    {s}/100 · {sc_label(s)}</span>
</div>""", unsafe_allow_html=True)

    if idx >= total:
        st.session_state.step = 2; st.rerun(); return

    q = qs[idx]
    cat_colors = {"technical":"#f5a623","behavioral":"#fb923c","system design":"#4ade80",
                  "project":"#fbbf24","conceptual":"#a78bfa"}
    cat = q.get("category","General").lower()
    cc  = cat_colors.get(cat,"#f5a623")

    bc, _ = st.columns([.2,.8])
    with bc:
        st.markdown(f"""<div style="font-family:var(--mono);font-size:.62rem;color:{cc};
border:1px solid {cc}55;padding:.18rem .5rem;border-radius:3rem;
background:{cc}11;text-align:center;white-space:nowrap">{q.get('category','General')}</div>""",
                    unsafe_allow_html=True)

    st.markdown(f'<div class="qbubble">{q["question"]}</div>', unsafe_allow_html=True)

    if st.session_state.tts_enabled and TTS_OK:
        ab = tts(q["question"])
        if ab: st.audio(ab, format="audio/mp3")

    if q.get("follow_up"):
        with st.expander("💡 Follow-up question"):
            st.markdown(f'<div class="fb">{q["follow_up"]}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Answer input ──────────────────────────────────────────────
    answer = ""
    if st.session_state.voice_mode and SR_OK:
        if PYAUDIO_OK:
            mc, tc = st.columns([.1,.9])
            with mc:
                if st.button("🎤", key=f"mic_{idx}", help="Record (15s)"):
                    with st.spinner("🎙 Listening…"):
                        r = live_transcribe()
                        if r and not r.startswith("["):
                            st.session_state[f"vans_{idx}"] = r
                            st.success("✓ Transcribed!")
                        else:
                            st.warning(r)
            with tc:
                dv = st.session_state.get(f"vans_{idx}","")
                answer = st.text_area("Answer", value=dv, height=160,
                                      placeholder="Speak 🎤 or type…",
                                      key=f"ans_{idx}", label_visibility="collapsed")
        else:
            st.markdown("""
<div style="background:rgba(245,166,35,.07);border:1px solid rgba(245,166,35,.25);
     border-radius:12px;padding:.9rem 1.1rem;margin-bottom:.7rem">
  <div style="font-family:var(--mono);font-size:.65rem;color:var(--gold);margin-bottom:.35rem">
    ⚠ PyAudio not installed — FILE UPLOAD MODE</div>
  <div style="font-size:.8rem;color:var(--muted)">
    Record your answer on your phone, then upload below.</div>
</div>""", unsafe_allow_html=True)
            uc, fc = st.columns([.5,.5], gap="large")
            with uc:
                af = st.file_uploader("Upload audio", type=["wav","mp3","ogg","m4a","webm","flac"],
                                      key=f"af_{idx}", label_visibility="collapsed")
                if af:
                    st.audio(af)
                    if st.button("🔄 Transcribe", key=f"tr_{idx}", use_container_width=True):
                        with st.spinner("Transcribing…"):
                            r = file_transcribe(af.getvalue(), af.type)
                            if r and not r.startswith("["):
                                st.session_state[f"vans_{idx}"] = r
                                st.success("✓ Transcribed!")
                            else:
                                st.warning(r)
            with fc:
                st.markdown("""
<div style="font-family:var(--mono);font-size:.65rem;color:var(--muted);line-height:1.9;padding-top:.3rem">
  <strong style="color:var(--gold)">Fix PyAudio:</strong><br>
  Win → <code>pipwin install pyaudio</code><br>
  Mac → <code>brew install portaudio</code><br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>pip install pyaudio</code><br>
  Linux → <code>sudo apt install python3-pyaudio</code>
</div>""", unsafe_allow_html=True)
            dv = st.session_state.get(f"vans_{idx}","")
            answer = st.text_area("Answer", value=dv, height=140,
                                  placeholder="Transcription appears here, or type…",
                                  key=f"ans_{idx}", label_visibility="collapsed")
    else:
        answer = st.text_area("Answer", height=180,
                              placeholder="Type your answer here — be thorough and specific.",
                              key=f"ans_{idx}", label_visibility="collapsed")

    # ── Actions ───────────────────────────────────────────────────
    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        if st.button("✓  Submit Answer", use_container_width=True):
            if not answer.strip():
                st.warning("Please enter an answer first.")
            else:
                with st.spinner("Evaluating with AI…"):
                    try:
                        ev = evaluate(q, answer)
                        st.session_state.answers.append(answer)
                        st.session_state.evaluations.append(ev)
                        st.session_state.current_q += 1
                        if st.session_state.current_q >= total:
                            st.session_state.step = 2
                        st.rerun()
                    except Exception as e:
                        st.error(f"Evaluation error: {e}")
    with c2:
        if st.button("⏭  Skip", use_container_width=True):
            st.session_state.answers.append("[Skipped]")
            st.session_state.evaluations.append(evaluate(q,"[Skipped]"))
            st.session_state.current_q += 1
            if st.session_state.current_q >= total:
                st.session_state.step = 2
            st.rerun()
    with c3:
        st.markdown(f"""
<div style="font-family:var(--mono);font-size:.68rem;color:var(--muted);
     padding:.5rem 0;text-align:right">
  {q.get('difficulty','—')} · <span style="color:var(--gold)">{q.get('category','—')}</span>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — RESULTS
# ══════════════════════════════════════════════════════════════════════════════
def page_results():
    render_rail()
    evs  = st.session_state.evaluations
    qs   = st.session_state.questions
    ans  = st.session_state.answers
    role = st.session_state.role
    name = st.session_state.candidate_name
    ri   = st.session_state.resume_info

    if not evs:
        st.warning("No evaluations found."); return

    def avg(k): return int(sum(e.get(k,0) for e in evs)/max(len(evs),1))

    # ── Banner ─────────────────────────────────────────────────────
    st.markdown(f"""
<div style="text-align:center;padding:1.5rem 0 .5rem">
  <div style="font-family:var(--mono);font-size:.65rem;letter-spacing:.2em;
       color:var(--green);margin-bottom:.4rem">✓ INTERVIEW COMPLETE</div>
  <div style="font-family:var(--serif);font-size:clamp(2rem,4.5vw,3.4rem);
       font-weight:900;letter-spacing:-.02em;
       background:linear-gradient(160deg,#fef3c7,var(--gold),var(--amber2));
       -webkit-background-clip:text;-webkit-text-fill-color:transparent">
    {(name + ' — ') if name else ''}{role}
  </div>
  <div style="font-family:var(--mono);font-size:.72rem;color:var(--muted);margin-top:.4rem">
    {st.session_state.domain} · {st.session_state.difficulty} · {len(qs)} questions
  </div>
</div>""", unsafe_allow_html=True)

    # ── 5-dim summary ──────────────────────────────────────────────
    dims = [("overall","Overall"),("clarity","Clarity"),("technical","Technical"),
            ("communication","Communication"),("depth","Depth")]
    html = '<div class="scores">'
    for k, lbl in dims:
        v = avg(k); c = sc_color(v)
        html += (f'<div class="sc"><div class="sc-num" style="color:{c}">{v}</div>'
                 f'<div class="sc-dim">{lbl}</div>'
                 f'<div class="sc-lbl" style="color:{c}">{sc_label(v)}</div></div>')
    st.markdown(html + '</div>', unsafe_allow_html=True)

    # ── AI Summary ─────────────────────────────────────────────────
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    st.markdown('<p class="lbl">🤖 AI Performance Summary</p>', unsafe_allow_html=True)
    with st.spinner("Generating summary…"):
        try:
            summary = gen_summary(evs, role, ri or None)
        except Exception as e:
            summary = f"Summary unavailable ({e})."
    st.session_state.report_summary = summary
    st.markdown(f'<div class="fb">{summary}</div>', unsafe_allow_html=True)

    # ── Per-question ────────────────────────────────────────────────
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    st.markdown('<p class="lbl">📋 Question Breakdown</p>', unsafe_allow_html=True)

    for i, (q, ev, a) in enumerate(zip(qs, evs, ans)):
        sc = ev.get("overall",0)
        with st.expander(f"Q{i+1} · {q['question'][:60]}… · {sc}/100"):
            score_grid(ev)

            c1, c2 = st.columns([.62,.38])
            with c1:
                st.markdown(f'<div class="qbubble" style="font-size:.9rem">{q["question"]}</div>',
                            unsafe_allow_html=True)
                st.markdown(f"""
<div style="margin-top:.9rem">
  <p class="lbl" style="font-size:.58rem">YOUR ANSWER</p>
  <div style="background:rgba(245,166,35,.03);border:1px solid var(--border);
       border-radius:10px;padding:.8rem 1rem;font-family:var(--mono);font-size:.78rem;
       line-height:1.65;color:var(--muted)">{a if a!='[Skipped]' else '<em>Skipped</em>'}</div>
</div>""", unsafe_allow_html=True)

                covered = ev.get("covered",[])
                missing = ev.get("missing",[])
                kw = '<div style="margin-top:.8rem"><p class="lbl" style="font-size:.58rem">KEYWORDS</p><div class="chips">'
                for kw_ in covered: kw += f'<span class="chip chip-ok">✓ {kw_}</span>'
                for kw_ in missing: kw += f'<span class="chip chip-miss">✗ {kw_}</span>'
                st.markdown(kw + '</div></div>', unsafe_allow_html=True)

                st.markdown(f"""
<div style="margin-top:.8rem">
  <p class="lbl" style="font-size:.58rem">DETAILED FEEDBACK</p>
  <div class="fb">{ev.get('feedback','')}</div>
</div>""", unsafe_allow_html=True)

                if ev.get("hint"):
                    st.markdown(f"""
<div style="margin-top:.7rem">
  <p class="lbl lbl-green" style="font-size:.58rem">MODEL ANSWER HINT</p>
  <div class="fb fb-green">{ev['hint']}</div>
</div>""", unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
<div style="margin-bottom:.7rem">
  <p class="lbl lbl-green" style="font-size:.58rem">STRENGTH</p>
  <div class="fb fb-green" style="font-size:.8rem">{ev.get('strengths','—')}</div>
</div>
<div>
  <p class="lbl lbl-orange" style="font-size:.58rem">IMPROVE</p>
  <div class="fb fb-orange" style="font-size:.8rem">{ev.get('improvements','—')}</div>
</div>""", unsafe_allow_html=True)

                if q.get("reference_answer"):
                    st.markdown(f"""
<div style="margin-top:.7rem">
  <p class="lbl" style="font-size:.58rem">REFERENCE ANSWER</p>
  <div style="font-family:var(--mono);font-size:.73rem;color:var(--muted);
       background:rgba(245,166,35,.03);border:1px solid var(--border);
       border-radius:8px;padding:.65rem .9rem;line-height:1.65">{q['reference_answer']}</div>
</div>""", unsafe_allow_html=True)

    # ── Actions ─────────────────────────────────────────────────────
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button("🔄  New Interview", use_container_width=True):
            for k in ["questions","answers","evaluations","current_q","resume_info","report_summary"]:
                st.session_state[k] = DEFS.get(k, [])
            st.session_state.step = 0
            st.rerun()
    with c2:
        if st.button("⚙  Change Setup", use_container_width=True):
            st.session_state.step = 0
            st.session_state.questions   = []
            st.session_state.answers     = []
            st.session_state.evaluations = []
            st.rerun()
    with c3:
        txt = f"SMART AI INTERVIEW COACH — REPORT\n{'='*54}\n"
        txt += f"Candidate : {name or '—'}\nRole : {role}\n"
        txt += f"Domain : {st.session_state.domain}\nDifficulty : {st.session_state.difficulty}\n"
        txt += f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        txt += "SCORES\n" + "-"*30 + "\n"
        for k,l in [("overall","Overall"),("clarity","Clarity"),("technical","Technical"),
                    ("communication","Communication"),("depth","Depth")]:
            txt += f"{l:20}: {avg(k)}/100\n"
        txt += f"\nSUMMARY\n{'-'*30}\n{summary}\n\n"
        for i,(q,ev,a) in enumerate(zip(qs,evs,ans)):
            txt += f"\nQ{i+1}: {q['question']}\nAnswer: {a}\nScore: {ev.get('overall',0)}/100\nFeedback: {ev.get('feedback','')}\n"
        st.download_button("📥  Export TXT", txt,
                           file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                           mime="text/plain", use_container_width=True)
    with c4:
        if RL_OK:
            try:
                pdf = build_pdf(name, role, st.session_state.domain,
                                st.session_state.difficulty, qs, ans, evs, summary)
                if pdf:
                    st.download_button("📄  Download PDF",
                                       pdf,
                                       file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                       mime="application/pdf",
                                       use_container_width=True)
            except Exception as e:
                st.error(f"PDF error: {e}")
        else:
            st.markdown('<p style="font-family:var(--mono);font-size:.65rem;color:var(--gold);padding:.5rem 0">⚠ pip install reportlab for PDF</p>',
                        unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">Smart AI Interview Coach</div>
  <h1>Master Your<br>Next Interview</h1>
  <p class="hero-sub">Groq LLaMA 3.3 · 5-Dimension Scoring · Voice I/O · PDF Report</p>
  <div class="hero-features">
    <span class="hero-feat">📄 Resume Analysis</span>
    <span class="hero-feat">🤖 AI Questions</span>
    <span class="hero-feat">🎙 Voice Interview</span>
    <span class="hero-feat">📊 5-Dim Scoring</span>
    <span class="hero-feat">📄 PDF Report</span>
    <span class="hero-feat">💬 Personalized Feedback</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
s = st.session_state.step
if   s == 0: page_setup()
elif s == 1: page_interview()
elif s == 2: page_results()
