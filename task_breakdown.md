# PlacementPro+ with SkillGap AI - Task List

## Phase 1: Project Setup + Base Structure (Week 1)
- [ ] **Frontend Setup (Team A)**
    - [ ] Initialize React + Vite project with Tailwind CSS
    - [ ] Install dependencies (Recharts/Chart.js, Axios, React Router)
    - [ ] Create folder structure (components, pages, services, context)
    - [ ] Build Profile Input Form
        - [ ] CGPA, Branch, Skills input
        - [ ] Internships & Projects details
- [ ] **Backend Setup (Team B)**
    - [ ] Initialize Python Flask environment
    - [ ] Install dependencies (Flask, Flask-CORS, pandas, scikit-learn, numpy, python-dotenv)
    - [ ] Create folder structure (app, models, routes, utils)
    - [ ] Create Base API Endpoints (Placeholders)
        - [ ] `/predict`
        - [ ] `/recommend`
        - [ ] `/skillgap`
        - [ ] `/roadmap`
- [ ] **Database Setup (Team C)**
    - [ ] Configure Supabase project (Instructional/Script)
    - [ ] Create Schema/Models for:
        - [ ] `students`
        - [ ] `companies`
        - [ ] `placement_records`
        - [ ] `skills_resources`

## Phase 2: Placement Prediction Model (Week 2)
- [ ] Data Collection & Preprocessing
    - [ ] Create/Import dataset
    - [ ] Preprocess features (CGPA, Skills vector, etc.)
- [ ] Model Training
    - [ ] Train RandomForest/XGBoost classifier
    - [ ] Save model (pickle/joblib)
- [ ] API Integration
    - [ ] Update `/predict` endpoint to load model and return probability
- [ ] Frontend Integration
    - [ ] Display placement probability (Gauge chart)

## Phase 3: Company Recommendation Engine (Week 3)
- [ ] Data Preparation
    - [ ] Create company dataset (Name, Skills, Package, Role)
- [ ] Recommendation Logic
    - [ ] Implement Cosine Similarity matching
    - [ ] Update `/recommend` endpoint
- [ ] Frontend Integration
    - [ ] Display ranked company cards

## Phase 4: SkillGap AI Integration (Week 4)
- [ ] Logic Implementation
    - [ ] Extract skills from student profile
    - [ ] Compare with target company requirements
    - [ ] Identify missing skills
- [ ] API Integration
    - [ ] Update `/skillgap` endpoint
- [ ] Frontend Integration
    - [ ] Show missing skills list

## Phase 5: AI Roadmap Generator (Week 5)
- [ ] LLM Integration
    - [ ] Setup Gemini/Groq API client
    - [ ] Design prompt for roadmap generation
- [ ] API Integration
    - [ ] Update `/roadmap` endpoint
- [ ] Frontend Integration
    - [ ] Display personalized learning roadmap timeline

## Phase 6: Final Dashboard + Comparison (Week 6)
- [ ] Dashboard Enhancements
    - [ ] Scenario saving
    - [ ] Skill radar chart
    - [ ] Probability trend chart

## Phase 7: Testing + Deployment (Week 7)
- [ ] Deployment
    - [ ] Deploy Frontend to Vercel
    - [ ] Deploy Backend to Render
    - [ ] Connect production Database

## Phase 8: Final Polish (Week 8)
- [ ] Documentation
    - [ ] Final Report
    - [ ] Architecture Diagram
    - [ ] Demo Slides
