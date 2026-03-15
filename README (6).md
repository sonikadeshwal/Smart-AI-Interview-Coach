# 🧠 Smart AI Interview Coach v3.0

> Resume-aware AI interviewer with 5-dimension scoring, voice I/O, **video recording + AI body language analysis**, and PDF reports.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch
streamlit run app.py
```

Open → `http://localhost:8501`

---

## 🔑 Get a Free Groq API Key

1. Visit **[console.groq.com](https://console.groq.com)**
2. Sign Up → API Keys → **Create API Key**
3. Copy (starts with `gsk_...`) and paste in the app

---

## ✨ All Features

### 1️⃣ Resume Upload & Analysis
- Upload PDF or TXT resume
- AI extracts skills, experience, projects, education
- Generates **personalized questions** based on your exact background

### 2️⃣ 5-Dimension Scoring
| Dimension     | What It Measures |
|---------------|-----------------|
| Overall       | Composite weighted score |
| Clarity       | Structure and coherence |
| Technical     | Correctness of concepts |
| Communication | Vocabulary & articulation |
| Depth         | Thoroughness beyond basics |

### 3️⃣ Voice Interview
- **Speech-to-Text**: Click 🎤 to record — needs `pyaudio`
- **Text-to-Speech**: Questions read aloud via gTTS

### 4️⃣ 📹 Video Recording (NEW in v3.0)
- Toggle **Video Recording** in setup — no extra install required
- Uses Streamlit's built-in `st.camera_input` (webcam in browser)
- **Capture a snapshot** per question while speaking your answer
- **AI Body Language Analysis** via Groq vision model scores:
  - Posture · Eye Contact · Confidence · Overall Presence
  - Instant feedback tip per snapshot
- **Video Gallery** in results — all snapshots with scores in a grid
- Per-snapshot download as `.jpg`
- Average On-Camera Presence score shown in results

### 5️⃣ PDF Interview Report
- Cover banner + meta info
- 5-score summary table
- Per-question: scores, keywords, feedback, model hints
- AI performance summary

### 6️⃣ Difficulty Levels
| Level         | Target Audience |
|---------------|-----------------|
| Beginner      | Students, freshers |
| Intermediate  | 1-3 years experience |
| Advanced      | Senior engineers |

---

## 📁 File Structure

```
smart_interview_coach/
├── app.py              ← Main Streamlit application (v3.0)
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## 🛠 Tech Stack

| Component            | Technology |
|----------------------|-----------|
| LLM Inference        | Groq API — LLaMA 3.3 70B |
| Vision / Body Lang.  | Groq — LLaMA 4 Scout (vision) |
| UI Framework         | Streamlit |
| Video / Webcam       | `st.camera_input` (built-in) |
| PDF Report           | ReportLab |
| Resume Parsing       | pypdf |
| Text-to-Speech       | gTTS |
| Speech-to-Text       | SpeechRecognition |
| Styling              | CSS — Outfit + JetBrains Mono |

---

## 📌 Resume Bullet Points

```
Smart AI Interview Coach                                           Mar. 2026
• Built a resume-aware AI interview platform using Groq LLaMA 3.3 70B that
  generates personalized questions and evaluates answers across 5 NLP dimensions
• Integrated webcam video recording via Streamlit's camera_input API with
  per-question AI body language analysis (posture, eye contact, confidence)
  using Groq's LLaMA 4 Scout vision model
• Implemented Speech-to-Text (SpeechRecognition) and Text-to-Speech (gTTS)
  for a full voice interview mode with real-time microphone transcription
• Generated professional PDF reports (ReportLab) with score summaries,
  keyword coverage, body language scores, and AI performance feedback
• Tech Stack: Python, Groq API, Streamlit, ReportLab, pypdf, gTTS, SpeechRecognition
```

---

## 📹 Video Recording Notes

- **No extra install** — `st.camera_input` is bundled with Streamlit
- Browser will ask for **camera permission** on first use — click Allow
- Snapshots are captured as JPEG images (not continuous video)
- Body language analysis requires Groq vision model access
- All snapshots stored in session and downloadable from the results gallery


> Resume-aware AI interviewer with 5-dimension scoring, voice I/O, and PDF reports.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch
streamlit run app.py
```

Open → `http://localhost:8501`

---

## 🔑 Get a Free Groq API Key

1. Visit **[console.groq.com](https://console.groq.com)**
2. Sign Up → API Keys → **Create API Key**
3. Copy (starts with `gsk_...`) and paste in the app

---

## ✨ All Features

### 1️⃣ Resume Upload & Analysis
- Upload PDF or TXT resume
- AI extracts skills, experience, projects, education
- Generates **personalized questions** based on your exact background
- Falls back to role+domain questions if no resume

### 2️⃣ 5-Dimension Scoring
Every answer is scored across 5 dimensions:

| Dimension     | What It Measures |
|---------------|-----------------|
| Overall       | Composite weighted score |
| Clarity       | Structure and coherence |
| Technical     | Correctness of concepts |
| Communication | Vocabulary & articulation |
| Depth         | Thoroughness beyond basics |

### 3️⃣ Voice Interview
- **Speech-to-Text**: Click 🎤 to record (15 sec limit) — needs `pyaudio`
- **Text-to-Speech**: Questions read aloud via gTTS
- Both can be toggled independently in setup

### 4️⃣ PDF Interview Report
- One-click beautifully formatted PDF
- Cover banner with score summary
- Per-question breakdown with all 5 scores
- Covered/missing keywords
- AI feedback, model hints, reference answers
- AI performance summary

### 5️⃣ Difficulty Levels
| Level         | Target Audience |
|---------------|-----------------|
| Beginner      | Students, freshers, bootcamp grads |
| Intermediate  | 1-3 years experience |
| Advanced      | Senior engineers, architects |

---

## 📁 File Structure

```
smart_interview_coach/
├── app.py              ← Main Streamlit application
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## 🛠 Tech Stack

| Component         | Technology |
|-------------------|-----------|
| LLM Inference     | Groq API — LLaMA 3.3 70B |
| UI Framework      | Streamlit |
| PDF Report        | ReportLab |
| Resume Parsing    | pypdf |
| Text-to-Speech    | gTTS |
| Speech-to-Text    | SpeechRecognition |
| Styling           | CSS — Outfit + JetBrains Mono |

---

## 📌 Resume Bullet Points

```
Smart AI Interview Coach                                          Mar. 2026
• Built a resume-aware AI interview platform using Groq LLaMA 3.3 70B that
  generates personalized questions from uploaded resumes and evaluates answers
  across 5 NLP dimensions: clarity, technical accuracy, communication, depth, confidence
• Integrated Speech-to-Text (SpeechRecognition) and Text-to-Speech (gTTS) for
  a full voice interview mode with real-time microphone transcription
• Implemented automated PDF report generation (ReportLab) with per-question
  breakdowns, keyword coverage analysis, AI feedback, and performance summary
• Tech Stack: Python, Groq API, Streamlit, ReportLab, pypdf, gTTS, SpeechRecognition
```

---

## ⚙ Voice Setup (Optional)

### Text-to-Speech
```bash
pip install gTTS
```
Requires internet (Google TTS API).

### Speech-to-Text
```bash
pip install SpeechRecognition

# Linux
sudo apt-get install python3-pyaudio

# macOS
brew install portaudio && pip install pyaudio

# Windows
pip install pyaudio
```

---

## 🎨 UI Highlights

- Dark glassmorphism with gradient accents
- Animated step rail with pulse effects
- 5-card score grid with color-coded rings
- Keyword chip tags (green = covered, red = missing)
- Tabbed setup (Config | Resume)
- Per-question expandable breakdown
- Export: TXT + PDF (formatted report)
