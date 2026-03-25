# 🚀 PLACEMENT PRO+

### Hybrid Neuro-Symbolic AI System for Personalized Career Roadmap Generation

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![NetworkX](https://img.shields.io/badge/Graph_Theory-NetworkX-4CA1AF?style=for-the-badge&logo=appveyor&logoColor=white)
![NLP](https://img.shields.io/badge/NLP_Engine-Sentence_Transformers-FFB74D?style=for-the-badge&logo=huggingface&logoColor=black)

---

## 📖 Overview

**Placement Pro+** is a cutting-edge, 100% offline Artificial Intelligence platform built to bridge the gap between academic preparation and enterprise industry requirements. It provides students with real-time placement probability scoring, highly automated company mapping, and **dynamically generated 12-week growth roadmaps**. 

Crucially, Placement Pro+ **functions completely free of any external APIs**. It utilizes a proprietary **Neuro-Symbolic Layer**, merging the semantic understanding of Vector embeddings with the flawless mathematical logic of Directed Acyclic Graphs (DAGs).

![System Architecture](./docs/architecture.png)

### ✨ Key Features
- 🧠 **Neuro-Symbolic Brain**: Zero API calls. Relies entirely on local `.pkl` NLP models and hard-math Graph Pathfinding algorithms.
- 📊 **Placement Prediction**: A weighted algorithmic model calculating probability against internships and parsed skills.
- 🕸️ **Semantic Skill Mapping**: Utilizes `all-MiniLM-L6-v2` to understand messy user text and map it to an official ontology.
- 🎯 **Algorithmic Pathfinding**: Uses `NetworkX` shortest-path rendering to construct foolproof logical learning milestones.
- ⚡ **Cyberpunk UI Engine**: Extremely responsive "immersion terminal" UI built on React, Framer Motion, and Tailwind CSS.
- 📉 **Real-Time Data Visualization**: Recharts integration mapping candidate topologies (Radar Charts) and probability growth curves.

---

## 🏗️ Technical Architecture

The AI layer merges two discrete disciplines of Machine Learning:

```mermaid
flowchart TD
    A["Raw Profile Input (e.g. 'react stuff')"] --> B("NLP Vectorizer (sentence-transformers)")
    B -->|"Semantic Similarity Search"| C{"Local Knowledge Graph (NetworkX)"}
    C -->|"Maps to 'ReactJS' Node"| D("Graph Pathfinding Engine")
    D -->|"Calculates Shortest Path to Target Job"| E["Algorithmic 12-Week Roadmap JSON"]
```

---

## 🚀 Deployment & Installation

### Option 1: Render.com 1-Click Deploy
The repository contains a fully configured `render.yaml` Infrastructure-as-Code (IaC) file. Push this repository to GitHub and synchronize it with Render to automatically launch both the Frontend Vite Static Site and the Python WSGI Backend using Gunicorn.

### Option 2: Local Execution

**Backend Setup**
1. Navigate to `/backend`.
2. Activate your virtual environment: `python -m venv venv`.
3. Install the AI dependencies: `pip install -r requirements.txt`. (Note: The first execution will download an ~80MB NLP HuggingFace Model to your cache).
4. Run: `python -m flask run` or `gunicorn run:app`.

**Frontend Setup**
1. Navigate to `/frontend`.
2. Install node properties: `npm install`.
3. Start the dev server: `npm run dev`.

---

<p align="center">
  Built with mathematical precision by the <strong>sriiverse</strong> team.
</p>
