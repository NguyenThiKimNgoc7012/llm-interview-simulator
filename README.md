# 🧠 LLM Interview Simulator

A smart recruitment assistant that simulates real-time interview scenarios using voice-based interaction and Large Language Models (LLMs).

## 🚀 Overview
This project aims to assist recruiters and job applicants by automating the **initial interview process** through a conversational AI agent. It mimics real-world interview situations via voice and text, providing candidates with a realistic preparation experience and helping companies pre-screen applicants effectively.

## 🎯 Key Features
- 🎤 **Voice-based interview**: Automatically transcribes and analyzes user speech using Whisper.
- 💬 **LLM-driven conversation**: Simulates recruiter-style Q&A with a fine-tuned model (3–8B parameters).
- 📄 **Dynamic question generation**: Questions adapt based on candidate's answers in real-time.
- 📊 **Feedback & summary**: Provides a review after each session.
- 📎 **JD Matching**: Matches answers to uploaded job descriptions.
- 🌐 **Frontend integration**: Built with Flask + React for a seamless user experience.

## 🛠️ Tech Stack
- **Backend**: Python, Flask, LangChain, Groq API
- **Frontend**: ReactJS, TailwindCSS
- **Speech Recognition**: Whisper (OpenAI)
- **LLM**: Models from OpenRouter (3B–8B parameters)

## 👩‍💻 My Role
As the sole developer, I was responsible for:
- Designing conversation flows and evaluation metrics
- Integrating LLMs and STT (speech-to-text) pipeline
- Building both frontend and backend
- Fine-tuning prompts and handling API communication

## 📁 Project Structure
llm-interview-simulator/
├── backend/ # Flask API
├── frontend/ # React frontend
├── prompts/ # Custom system prompts
├── .env # API keys (excluded in .gitignore)
├── .gitignore
└── README.md

## 📦 Setup
```bash
# Clone the repo
git clone https://github.com/NguyenThiKimNgoc7012/llm-interview-simulator.git
cd llm-interview-simulator

# Backend setup
cd backend
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
npm start
## 🎥 Demo
