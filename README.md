# 🚀 PLACEMENT PRO+

### Hybrid Neuro-Symbolic AI System for Personalized Career Roadmap Generation

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
</p>

<p align="center">
  <img src="https://github.com/sriiverse/Placement-Pro/actions/workflows/ci.yml/badge.svg" alt="CI Status" />
  <img src="https://img.shields.io/badge/coverage-85%25-brightgreen?style=flat-square&logo=pytest" alt="Test Coverage" />
  <img src="https://img.shields.io/badge/security-OWASP_headers-blueviolet?style=flat-square&logo=owasp" alt="Security" />
  <img src="https://img.shields.io/badge/API_Docs-Swagger_UI-85EA2D?style=flat-square&logo=swagger" alt="API Docs" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License" />
</p>

---

## 📖 Overview

**Placement Pro+** is a production-grade AI platform that bridges the gap between academic preparation and enterprise industry requirements. It provides students with real-time placement probability scoring, AI-driven company matching, and **dynamically generated 12-week personalised growth roadmaps**.

The system operates **100% offline** — no paid APIs, no external LLM calls. It uses a proprietary **Neuro-Symbolic Layer**, merging the semantic understanding of Vector Embeddings with the mathematical precision of Directed Acyclic Graph (DAG) pathfinding.

---

## ✨ Feature Highlights

| Feature | Technology | Detail |
|---|---|---|
| 🧠 **Neuro-Symbolic AI** | `sentence-transformers` + `NetworkX` | Semantic skill mapping via cosine similarity + DAG shortest-path |
| 📊 **Placement Prediction** | Sigmoid-weighted heuristic model | Internships, CGPA, projects → 0–100% probability score |
| 🎯 **Company Matching** | Rule-based recommendation engine | CGPA gate + skill overlap scoring across 10+ companies |
| 📝 **12-Week Roadmap** | Knowledge graph pathfinding | Topologically ordered, gap-aware learning milestones |
| 🔐 **JWT Auth System** | `flask-jwt-extended` + `bcrypt` | Registration, login, token refresh, route protection |
| ⚡ **Intelligent Caching** | `cachetools.TTLCache` + `@lru_cache` | 4 TTL namespaces + memoized ML embeddings (leverages 24GB RAM) |
| 🛡️ **OWASP Security** | `flask-talisman` | HSTS, CSP, Referrer Policy, Feature Policy headers |
| 📈 **Observability** | Prometheus + Sentry + JSON Logging | `/metrics`, `/health`, `/ready`, structured request correlation IDs |
| 🐳 **Containerised** | Docker Compose | Multi-service, non-root images, health checks |
| 🔁 **CI/CD** | GitHub Actions | Lint → Test → Security scan → Docker build on every push |

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    A["Raw Profile Input (e.g. 'react stuff')"] --> B("NLP Vectorizer (sentence-transformers)")
    B -->|"Cosine Similarity ≥ 0.60"| C{"Knowledge Graph (NetworkX DAG)"}
    C -->|"Maps to 'ReactJS' Node"| D("Shortest-Path Engine (BFS/Dijkstra)")
    D -->|"Calculates gap to Target Role"| E["12-Week Roadmap JSON"]
    E --> F["React Cyberpunk Dashboard (Framer Motion)"]
```

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)
```bash
git clone https://github.com/sriiverse/Placement-Pro.git
cd Placement-Pro
cp backend/.env.example backend/.env
docker compose up --build
```
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:5000
- **Swagger UI:** http://localhost:5000/api/docs
- **Prometheus Metrics:** http://localhost:5000/metrics

### Option 2: Local Development

**Backend**
```bash
cd backend
python -m venv .venv && .venv/Scripts/activate   # Windows
pip install -r requirements.txt
cp .env.example .env
flask run
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing

```bash
# Run full test suite with coverage report
cd backend
pytest tests/ --cov=app --cov-report=term-missing

# Run only unit tests (fast — no DB)
pytest tests/ -k "TestML or TestSchema or TestCompany"
```

**Test Coverage Map**

| Module | Tests |
|---|---|
| `app/models.py` | ✅ Instantiation, `to_dict()`, FK links |
| `app/schemas.py` | ✅ Valid inputs, digit rejection, CGPA bounds, empty skills |
| `services/ml_service.py` | ✅ Probability range, ranking, null handling, confidence levels |
| `services/company_service.py` | ✅ Sort order, CGPA filter, null user, result keys |
| `app/auth.py` | ✅ Register, duplicate, short password, login, wrong password, JWT `/me` |
| `app/__init__.py` | ✅ `/health`, `/ready`, `/api/docs/openapi.json` |

---

## 🛡️ Security

The API enforces the following OWASP-recommended security controls:

- **HSTS** — `Strict-Transport-Security` header enforced
- **CSP** — `Content-Security-Policy` restricts scripts to `'self'` + Swagger CDN
- **Referrer Policy** — `strict-origin-when-cross-origin`
- **Feature Policy** — Geolocation, microphone, and camera disabled
- **Rate Limiting** — Per-endpoint via `flask-limiter` (brute-force protection on auth)
- **Pydantic v2 Validation** — Every input field validated before business logic runs
- **bcrypt** — Passwords hashed with work factor 12; same error for user-not-found vs wrong password (no enumeration)

---

## 📡 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | ❌ | Liveness probe |
| `GET` | `/ready` | ❌ | Deep readiness check (DB + cache + disk) |
| `GET` | `/metrics` | ❌ | Prometheus metrics |
| `GET` | `/api/docs` | ❌ | Swagger UI |
| `POST` | `/api/auth/register` | ❌ | Create account |
| `POST` | `/api/auth/login` | ❌ | Login → JWT tokens |
| `POST` | `/api/auth/refresh` | 🔐 | Rotate access token |
| `GET` | `/api/auth/me` | 🔐 | Current user info |
| `POST` | `/api/submit-profile` | 🔐 | Create placement profile |
| `POST` | `/api/dashboard` | 🔐 | Full AI dashboard aggregate |
| `POST` | `/api/predict-placement` | 🔐 | Placement probability score |
| `POST` | `/api/recommend-companies` | 🔐 | Company recommendations |
| `POST` | `/api/skill-gap` | 🔐 | Skill gap analysis |
| `POST` | `/api/generate-roadmap` | 🔐 | 12-week learning roadmap |

---

## 🗂️ Project Structure

```
Placement-Pro/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # App factory (Talisman, Prometheus, Sentry, JWT)
│   │   ├── auth.py              # JWT auth blueprint
│   │   ├── routes.py            # Protected AI API routes
│   │   ├── models.py            # SQLAlchemy models (AuthUser, User)
│   │   ├── schemas.py           # Pydantic v2 validation schemas
│   │   ├── cache.py             # TTL cache namespaces + fingerprinting
│   │   ├── logger.py            # JSON structured logging + correlation IDs
│   │   ├── extensions.py        # Flask-Limiter
│   │   ├── openapi.py           # OpenAPI 3.0 spec
│   │   └── services/
│   │       ├── ml_service.py    # Placement prediction (sigmoid model)
│   │       ├── company_service.py # Company recommendation engine
│   │       ├── ai_engine.py     # Neuro-symbolic orchestrator
│   │       ├── vector_service.py  # Semantic embedding (lru_cache)
│   │       └── graph_service.py   # Knowledge graph + pathfinding
│   ├── tests/
│   │   └── test_basic.py        # 30+ unit & integration tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── context/
│   │   │   ├── AuthContext.tsx   # JWT auth state + global API interceptors
│   │   │   └── ToastContext.tsx  # Custom toast notification system
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx     # AI dashboard with cache-hit badges
│   │   │   ├── ProfileForm.tsx   # Multi-step cyberpunk form
│   │   │   └── Login.tsx         # Auth gateway
│   │   └── components/ui/
│   │       └── Skeleton.tsx      # Shimmer skeleton loaders
│   ├── Dockerfile
│   └── nginx.conf
├── .github/workflows/ci.yml      # CI/CD pipeline
├── docker-compose.yml
└── render.yaml                   # IaC for 1-click Render deploy
```

---

<p align="center">
  Built with mathematical precision by the <strong>sriiverse</strong> team · PlacementPro+ v2.0
</p>
