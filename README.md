<![CDATA[<div align="center">

# 🚀 PLACEMENT PRO

### AI-Powered Campus Placement Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Gemini](https://img.shields.io/badge/Google_Gemini-1.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)

> **Placement Pro** is an AI-powered platform that predicts a student's placement probability, recommends matched companies, identifies skill gaps using Google Gemini, and generates a personalized 12-week preparation roadmap — all in one cyberpunk-themed dashboard.

[Live Demo](#) · [Report a Bug](https://github.com/sriiverse/Placement-Pro/issues) · [Request Feature](https://github.com/sriiverse/Placement-Pro/issues)

</div>

---

## 📸 Screenshots

> Dashboard UI with cyberpunk HUD design — Placement % ring, Company Matches, Skill Gap Analysis & Roadmap tabs.

---

## 🗂️ Project Structure

```
Placement-Pro/
├── backend/                     # Flask REST API
│   ├── app/
│   │   ├── __init__.py          # App factory, CORS, DB setup
│   │   ├── models.py            # SQLAlchemy User model
│   │   ├── routes.py            # All API endpoints (6 routes)
│   │   └── services/
│   │       ├── ml_service.py    # Custom placement prediction engine (Phase 2)
│   │       ├── company_service.py # Rule-based company recommender (Phase 3)
│   │       └── llm_service.py   # Google Gemini AI integration (Phase 4 & 5)
│   ├── run.py                   # Entry point
│   ├── requirements.txt
│   └── .env.example             # Environment variable template
│
└── frontend/                    # React + TypeScript (Vite)
    ├── src/
    │   ├── App.tsx              # Routing (React Router)
    │   ├── pages/
    │   │   ├── ProfileForm.tsx  # 3-step profile input wizard
    │   │   └── Dashboard.tsx    # Main HUD dashboard (4 tabs)
    │   ├── components/
    │   │   └── layout/
    │   │       ├── AppLayout.tsx
    │   │       └── Navbar.tsx
    │   ├── index.css            # Cyberpunk design system
    │   └── lib/utils.ts
    ├── index.html
    ├── package.json
    └── vite.config.ts
```

---

## ✅ Development Progress

### Phase Roadmap

| Phase | Feature | Status | Notes |
|-------|---------|--------|-------|
| **Phase 1** | User Profile API + SQLite DB | ✅ Complete | `POST /api/submit-profile` — saves user to DB |
| **Phase 2** | Placement Prediction Engine | ✅ Complete | Custom ML heuristic model with sigmoid scoring |
| **Phase 3** | Company Recommendation Engine | ✅ Complete | Skill + CGPA matching across 10 companies |
| **Phase 4** | AI Skill Gap Analysis (Gemini) | ✅ Complete | `POST /api/skill-gap` — Gemini 1.5 Flash powered |
| **Phase 5** | AI Roadmap Generator (Gemini) | ✅ Complete | 12-week personalized prep plan |
| **Phase 6** | Dashboard Aggregate API | ✅ Complete | `POST /api/dashboard` — all data in one call |
| **Phase 7** | Supabase PostgreSQL Migration | 🔲 Planned | Replace SQLite with cloud DB |
| **Phase 8** | User Auth (JWT) | 🔲 Planned | Login/Register with JWT tokens |
| **Phase 9** | Resume Upload & Parse | 🔲 Planned | Auto-fill profile from resume |
| **Phase 10** | Deployment (Render + Netlify) | 🔲 Planned | Production hosting |

---

## 🧠 Architecture Overview

```
User Input (ProfileForm)
        │
        ▼
POST /api/submit-profile  ──► SQLite DB (User table)
        │
        ▼
POST /api/dashboard
   ├── ml_service.PlacementPredictor    → Placement % (0–100)
   ├── company_service.CompanyRecommender → Top 6 company matches
   └── llm_service.GeminiService         → Skill gap + Readiness score
        │
        ▼
POST /api/generate-roadmap
   └── GeminiService → 12-week personalized roadmap
        │
        ▼
Dashboard UI (4 Tabs)
   ├── OVERVIEW   → Animated probability ring + key factors
   ├── COMPANIES  → Tier-ranked company cards with match %
   ├── SKILL_GAP  → AI-identified gaps with resources
   └── ROADMAP    → Weekly milestone cards
```

---

## ⚙️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Flask 3.x** | REST API framework |
| **Flask-SQLAlchemy** | ORM for database models |
| **SQLite** (dev) / **PostgreSQL** (prod) | Data persistence |
| **Flask-CORS** | Cross-origin request handling |
| **NumPy** | Sigmoid scoring in ML model |
| **Google Generative AI SDK** | Gemini 1.5 Flash LLM calls |
| **python-dotenv** | Environment variable management |

### Frontend
| Technology | Purpose |
|---|---|
| **React 18 + TypeScript** | UI framework |
| **Vite** | Build tool & dev server |
| **React Router v6** | Client-side routing |
| **Framer Motion** | Animations & tab transitions |
| **Axios** | HTTP client for API calls |
| **Tailwind CSS** | Utility-first styling |
| **Lucide React** | Icon library |

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/submit-profile` | Save a new user profile to the database |
| `POST` | `/api/predict-placement` | Get placement probability for a user |
| `POST` | `/api/recommend-companies` | Get top 6 company matches |
| `POST` | `/api/skill-gap` | AI-powered skill gap analysis (Gemini) |
| `POST` | `/api/generate-roadmap` | Generate a 12-week roadmap (Gemini) |
| `POST` | `/api/dashboard` | Aggregate endpoint — all data in one call |
| `GET`  | `/health` | Health check endpoint |

**Request body (all POST routes except health):**
```json
{ "user_id": 1 }
```

**`/submit-profile` request body:**
```json
{
  "full_name": "Ravi Kumar",
  "target_designation": "Software Engineer",
  "cgpa": 8.5,
  "grad_year": 2025,
  "branch": "Computer Science",
  "skills": ["React", "Python", "SQL"],
  "internships_count": 2,
  "projects_count": 4
}
```

---

## 🚀 Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Google Gemini API key ([get one free here](https://aistudio.google.com/app/apikey))

### 1. Clone the repo
```bash
git clone https://github.com/sriiverse/Placement-Pro.git
cd Placement-Pro
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create your .env file
copy .env.example .env       # Windows
# cp .env.example .env       # Mac/Linux
# → Add your GEMINI_API_KEY in .env

# Run the backend server
python run.py
# Server runs at: http://127.0.0.1:5000
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run the dev server
npm run dev
# App runs at: http://localhost:5173
```

---

## 🔑 Environment Variables

Create a `backend/.env` file with:

```env
# Flask
FLASK_APP=run.py
FLASK_ENV=development
PORT=5000
SECRET_KEY=your_secret_key_here

# Gemini AI (required for skill gap + roadmap features)
GEMINI_API_KEY=your_gemini_api_key_here

# Database (leave blank for SQLite in dev)
# DATABASE_URL=postgresql://user:password@host/dbname
```

> ⚠️ **Never commit your `.env` file.** It is already in `.gitignore`.

---

## 🧩 Key Design Decisions

### Custom ML Model vs Gemini API
The platform uses **two complementary intelligence systems**:

- **`ml_service.py` (PlacementPredictor)** — A fast, offline, deterministic weighted-scoring model using sigmoid normalization. Handles **quantitative prediction** (the % score). No API needed, zero latency.

- **`llm_service.py` (GeminiService)** — Google Gemini 1.5 Flash for **qualitative intelligence**: contextual skill gap reasoning, role-specific feedback, and detailed weekly roadmaps. Falls back to curated mock data if the API key is unavailable.

### Graceful Degradation
All Gemini-powered features have a **mock fallback** — the app is fully usable even without a Gemini API key. The mock responses are carefully crafted to be realistic and useful.

---

## 🤝 Contributing (Team Members)

1. **Branch naming:** `feature/<your-feature>` or `fix/<bug-name>`
2. **Never push directly to `main`** — raise a PR
3. **Never commit `.env`** files — use `.env.example` for reference
4. **Backend changes:** Add corresponding routes in `routes.py` and services in `app/services/`
5. **Frontend changes:** Keep pages in `src/pages/` and reusable components in `src/components/`

---

## 📄 License

This project is for academic and portfolio purposes. All rights reserved © 2026 sriiverse.

---

<div align="center">
Built with 🤖 AI + ☕ caffeine by the <strong>sriiverse</strong> team
</div>
]]>
