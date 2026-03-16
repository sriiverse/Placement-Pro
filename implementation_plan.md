# Implementation Plan - Phase 1: Project Setup + Base Structure

This plan outlines the steps for Phase 1 of the PlacementPro+ with SkillGap AI project. The goal is to establish a solid foundation for the application, including the frontend dashboard, backend API server, and database schema.

## User Review Required
> [!IMPORTANT]
> - Ensure you have Node.js and Python installed.
> - You will need to set up a Supabase project manually and provide the connection details/keys.
> - We will use `Vite` for React and `Flask` for the backend.

## Proposed Changes

### Frontend (Team Member A)
Will be set up in `frontend/` directory.

#### [NEW] [frontend/](file:///d:/FRP/frontend)
- Initialize React + Vite project.
- Configure Tailwind CSS.
- Install dependencies: `axios` (for API communication), `react-router-dom`, `recharts`, `lucide-react`, `framer-motion`.
- Create basic layout and `Dashboard` component.
- Create `ProfileForm` component.

### Backend (Team Member B)
Will be set up in `backend/` directory.

#### [NEW] [backend/](file:///d:/FRP/backend)
- Initialize Python virtual environment.
- Create `requirements.txt`: `flask`, `flask-cors`, `pandas`, `scikit-learn`, `numpy`, `python-dotenv`, `psycopg2-binary`, `google-generativeai` (Gemini SDK), `joblib`.
- Create `app/` structure with `routes.py`, `models.py`, `services/`.
- **Model Serving:** Implement loading of ML models using `joblib`.
- **LLM Integration:** Setup `Gemini/Groq` client for roadmap generation.
- Implement placeholder endpoints: `/predict`, `/recommend`, `/skillgap`, `/roadmap`.

### Database & Deployment (Team Member C)
Will be set up conceptually and via scripts.

#### [NEW] [database/](file:///d:/FRP/database)
- Create `schema.sql` for Supabase/PostgreSQL.
    - Tables: `students`, `companies`, `placement_records`, `skills_resources`.

#### Deployment Plan
- **Frontend:** Vercel
- **Backend:** Render
- **Database:** Supabase

## Verification Plan

### Automated Tests
- Review the `frontend` build using `npm run build`.
- Start the `backend` server using `flask run` and verify endpoints with `curl` or Postman.

### Manual Verification
- Open the frontend in the browser and check if the dashboard loads.
- Verify that the frontend can communicate with the backend (e.g., a simple health check or "Hello World" message).
