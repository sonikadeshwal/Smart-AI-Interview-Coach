# 🏆 Smart AI Interview Coach

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-f5a623?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-f5a623?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

### 🚀 [**Live Demo → smart-ai-interview-coach.streamlit.app**](https://smart-ai-interview-coach-rimxxmirddubqywlguf5nx.streamlit.app/)

*An AI-powered mock interview platform that evaluates your answers in real time using NLP, semantic scoring, and voice interaction.*

</div>

---

## 📸 Preview

| Setup | Interview | Results |
|-------|-----------|---------|
| Configure role, domain & difficulty | Answer AI-generated questions | 5-dimension scores + PDF report |

---

## ✨ Features

### 📄 Resume Analysis
- Upload **PDF or TXT** resume
- AI extracts skills, experience, education, and projects
- Automatically generates **personalized questions** tailored to your exact background
- Falls back to role + domain if no resume is provided

### 🤖 AI Interviewer
- Powered by **Groq LLaMA 3.3 70B** — ultra-fast inference
- Generates role-specific questions across 5 categories:
  `Technical` · `Behavioral` · `System Design` · `Conceptual` · `Project`
- Includes follow-up questions and reference answers

### 🎙 Voice Interview
- **Speech-to-Text** — click mic button, speak, auto-transcribe (requires PyAudio)
- **File Upload Fallback** — record on any device → upload WAV/MP3/OGG → transcribe
- **Text-to-Speech** — questions read aloud via Google TTS (gTTS)

### 📊 5-Dimension Scoring
Every answer is evaluated across **5 independent dimensions**:

| Dimension | What It Measures |
|-----------|-----------------|
| 🎯 Overall | Composite weighted score (0–100) |
| 💬 Clarity | Structure, coherence, and conciseness |
| ⚙ Technical | Correctness of technical concepts and facts |
| 🗣 Communication | Professional vocabulary and articulation |
| 🔬 Depth | Thoroughness and insight beyond surface-level |

### 📄 PDF Interview Report
One-click **professional PDF report** including:
- Score summary table (all 5 dimensions)
- Per-question breakdown with feedback
- Covered & missing keywords
- Model answer hints
- AI-generated performance summary
- Strengths and areas to improve

### 🎚 Difficulty Levels

| Level | Target Audience |
|-------|-----------------|
| Beginner | Students, freshers, bootcamp graduates |
| Intermediate | 1–3 years of experience |
| Advanced | Senior engineers and architects |

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| **LLM** | [Groq](https://console.groq.com) — LLaMA 3.3 70B |
| **UI Framework** | [Streamlit](https://streamlit.io) |
| **PDF Generation** | ReportLab |
| **Resume Parsing** | pypdf |
| **Text-to-Speech** | gTTS (Google TTS) |
| **Speech-to-Text** | SpeechRecognition + Google Speech API |
| **Fonts** | Playfair Display · Plus Jakarta Sans · Fira Code |

---

## 🚀 Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/smart-ai-interview-coach.git
cd smart-ai-interview-coach
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get a free Groq API key
1. Go to **[console.groq.com](https://console.groq.com)**
2. Sign Up → API Keys → **Create API Key**
3. Copy the key (starts with `gsk_...`)

### 4. Run the app
```bash
streamlit run app.py
```

Open → `http://localhost:8501`

---

## 🎤 Voice Setup (Optional)

### Text-to-Speech
```bash
pip install gTTS
```

### Speech-to-Text with Live Mic
```bash
pip install SpeechRecognition

# Windows
pip install pipwin && pipwin install pyaudio

# macOS
brew install portaudio && pip install pyaudio

# Linux
sudo apt-get install python3-pyaudio portaudio19-dev
```

> ⚠ **No PyAudio?** No problem — the app automatically switches to **file upload mode**. Record on your phone and upload any `.wav`, `.mp3`, `.ogg`, `.m4a`, or `.webm` file.

---

## 📁 Project Structure

```
smart-ai-interview-coach/
├── app.py               ← Main Streamlit application
├── requirements.txt     ← Python dependencies
└── README.md            ← This file
```

---

## 📌 Resume / LinkedIn Bullet Points

```
Smart AI Interview Coach                                        Mar. 2026
GitHub | Live Demo: smart-ai-interview-coach.streamlit.app

• Developed an AI-powered mock interview platform using Groq LLaMA 3.3 70B
  that generates personalized questions from uploaded resumes and evaluates
  answers across 5 NLP dimensions: clarity, technical accuracy,
  communication, depth, and confidence

• Implemented Speech-to-Text (SpeechRecognition) with live mic support and
  audio file fallback, plus Text-to-Speech (gTTS) for a full voice interview
  experience with automatic transcription

• Built automated PDF report generation (ReportLab) with per-question
  breakdowns, keyword coverage analysis, model answer hints, and an
  AI-generated performance summary

• Tech Stack: Python · Groq API · Streamlit · ReportLab · pypdf · gTTS ·
  SpeechRecognition
```

---

## 🔗 Links

| | |
|--|--|
| 🌐 **Live Demo** | [smart-ai-interview-coach.streamlit.app](https://smart-ai-interview-coach-rimxxmirddubqywlguf5nx.streamlit.app/) |
| 🤖 **Groq API** | [console.groq.com](https://console.groq.com) |
| 📦 **Streamlit** | [streamlit.io](https://streamlit.io) |

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📄 License

This project is licensed under the **MIT License**.

---

<div align="center">

Made with ❤️ using Groq LLaMA 3.3 · Streamlit · Python

⭐ **Star this repo if it helped your placement prep!**

</div>
