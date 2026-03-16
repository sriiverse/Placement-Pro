# 🚀 PLACEMENT PRO

### AI-Powered Campus Placement Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-1.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)

---

## 📖 Overview

**Placement Pro** is a cutting-edge AI platform designed to bridge the gap between academic preparation and industry requirements. It provides students with real-time placement probability scores, role-specific company recommendations, and AI-driven growth roadmaps.

### ✨ Key Features
- 📊 **Placement Prediction**: Heuristic ML engine calculating probability based on CGPA, projects, and internships.
- 🏢 **Company Matching**: Automated recommendations mapped to Tier-1, Tier-2, and Tier-3 companies.
- 🎯 **Skill Gap Analysis**: Deep insights into missing technical competencies powered by **Google Gemini 1.5 Flash**.
- 🗺️ **Personalized Roadmaps**: Dynamic 12-week preparation plans tailored to individual goals.
- ⚡ **Cyberpunk HUD UI**: A high-performance, immersive "Terminal" style interface built with Framer Motion.

---

## 🏗️ Project Architecture

```bash
Placement-Pro/
├── backend/                # Flask REST API + ML Engine
│   ├── app/
│   │   ├── services/       # Core Logic (ML, LLM, Recommendation)
│   │   ├── models.py       # database Schema
│   │   └── routes.py       # API Endpoints
│   └── run.py              # Entry Point
└── frontend/               # React + TypeScript (Vite)
    ├── src/
    │   ├── pages/          # Dashboard & Profile Wizard
    │   ├── components/     # HUD UI Components
    │   └── index.css       # Custom Cyberpunk Design System
```

---

## 🚀 Quick Start

### Backend Setup
1. Navigate to `/backend`.
2. Create a virtual environment: `python -m venv venv`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Setup `.env` with your `GEMINI_API_KEY`.
5. Run: `python run.py`.

### Frontend Setup
1. Navigate to `/frontend`.
2. Install dependencies: `npm install`.
3. Run: `npm run dev`.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, Flask, SQLAlchemy, NumPy, Google Generative AI SDK.
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Framer Motion, Lucide Icons.
- **Database**: SQLite (Development) / PostgreSQL (Production).

---

## 📈 Roadmap & Progress

- [x] **Phase 1-6**: Core MVP, ML Engine, Gemini Integration, Dashboard Aggregator.
- [ ] **Phase 7**: Supabase PostgreSQL Migration.
- [ ] **Phase 8**: JWT Authentication.
- [ ] **Phase 9**: AI Resume Parser.
- [ ] **Phase 10**: Cloud Deployment (Render/Netlify).

---

<p align="center">
  Built with precision by the <strong>sriiverse</strong> team.
</p>
