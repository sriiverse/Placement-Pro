"""
Phase 7: Neuro-Symbolic Service
Powers the SkillGap Analysis and Roadmap Generation using 
Semantic Vector Embeddings and a Directed Acyclic Knowledge Graph.
"""

from .vector_service import VectorService
from .graph_service import KnowledgeGraphService

class NeuroSymbolicService:
    def __init__(self):
        self.graph_service = KnowledgeGraphService()
        try:
            self.vector_service = VectorService()
        except Exception as e:
            print("Warning: VectorService unavailable.", e)
            self.vector_service = None

    def analyze_skill_gap(self, user):
        user_skills_raw = [s.strip() for s in (user.skills or "").split(',')]
        target_role = (user.target_designation or "Backend Engineer").title()
        
        all_graph_nodes = self.graph_service.get_all_nodes()
        
        if self.vector_service:
            mapped_skills = self.vector_service.map_user_skills_to_graph(user_skills_raw, all_graph_nodes)
        else:
            mapped_skills = [s for s in user_skills_raw if s in all_graph_nodes]
            
        missing_path = self.graph_service.get_shortest_path(mapped_skills, target_role)
        
        if not missing_path:
            missing_path = ["System Design", "Cloud Architecture"]
            
        gaps_detailed = []
        for i, m_skill in enumerate(missing_path[:3]):
            priority = "HIGH" if i == 0 else "MEDIUM"
            gaps_detailed.append({
                "skill": m_skill,
                "priority": priority,
                "reason": f"Required prerequisite for {target_role}",
                "resources": [f"{m_skill} Official Docs", "Recommended Video Course"]
            })
            
        base_score = 40
        cgpa_bonus = max(0, ((user.cgpa or 6.0) - 6.0) * 5)
        path_penalty = len(missing_path) * 5
        readiness_score = int(min(max(base_score + cgpa_bonus + (len(mapped_skills)*5) - path_penalty, 10), 98))
        
        summary = f"Your profile mapped to {len(mapped_skills)} core industry skills. To reach {target_role}, the knowledge graph indicates you must navigate {len(missing_path)} prerequisite nodes, starting with {missing_path[0] if missing_path else 'Advanced Concepts'}."
        
        return {
            "missing_skills": missing_path,
            "skill_gaps": gaps_detailed,
            "strengths": mapped_skills if mapped_skills else user_skills_raw[:3],
            "readiness_score": readiness_score,
            "summary": summary
        }

    def generate_roadmap(self, user, skill_gaps):
        target = user.target_designation or "Backend Engineer"
        missing_nodes = skill_gaps if skill_gaps else ["System Design"]
        
        roadmap = []
        weeks_per_node = max(1, 12 // len(missing_nodes)) if missing_nodes else 4
        
        current_week = 1
        for node in missing_nodes:
            roadmap.append({
                "week": current_week,
                "theme": f"Foundation: {node}",
                "topics": [f"Intro to {node}", "Core Primitives", "Environment Setup"],
                "resources": ["Official Documentation", "Crash Course Video"],
                "milestone": f"Basic understanding of {node}"
            })
            current_week += 1
            if current_week <= 12 and weeks_per_node >= 2:
                roadmap.append({
                    "week": current_week,
                    "theme": f"Deep Dive: {node}",
                    "topics": ["Advanced Patterns", "Integration", "Best Practices"],
                    "resources": ["Advanced Textbook", "Code Walkthroughs"],
                    "milestone": f"Build a prototype using {node}"
                })
                current_week += 1
                
        while current_week <= 12:
            roadmap.append({
                "week": current_week,
                "theme": f"Project Phase & Placement Prep",
                "topics": ["Resume Review", "Mock Interviews", "System Design Practice"],
                "resources": ["Pramp", "Interviewing.io"],
                "milestone": f"Interview Ready for {target}"
            })
            current_week += 1
            
        return roadmap[:12]

# Maintain the exported variable name to not break routes.py
ai_service = NeuroSymbolicService()
