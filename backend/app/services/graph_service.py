import networkx as nx

class KnowledgeGraphService:
    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_skill_graph()

    def _build_skill_graph(self):
        # Base Foundation
        self.graph.add_edge("Programming Logic", "Data Structures")
        self.graph.add_edge("Data Structures", "Algorithms")
        self.graph.add_edge("Algorithms", "Git")
        
        # Frontend Path
        self.graph.add_edge("Git", "HTML/CSS")
        self.graph.add_edge("HTML/CSS", "JavaScript")
        self.graph.add_edge("JavaScript", "React")
        self.graph.add_edge("JavaScript", "Vue")
        self.graph.add_edge("React", "Next.js")
        self.graph.add_edge("Next.js", "Frontend Engineer")
        self.graph.add_edge("Vue", "Frontend Engineer")

        # Backend Path
        self.graph.add_edge("Git", "Python")
        self.graph.add_edge("Git", "Java")
        self.graph.add_edge("Git", "Node.js")
        self.graph.add_edge("Python", "SQL")
        self.graph.add_edge("Python", "FastAPI")
        self.graph.add_edge("Python", "Django")
        self.graph.add_edge("Java", "Spring Boot")
        self.graph.add_edge("Node.js", "Express")
        self.graph.add_edge("SQL", "Databases")
        self.graph.add_edge("FastAPI", "Backend Engineer")
        self.graph.add_edge("Django", "Backend Engineer")
        self.graph.add_edge("Spring Boot", "Backend Engineer")
        self.graph.add_edge("Express", "Backend Engineer")
        self.graph.add_edge("Databases", "Backend Engineer")
        self.graph.add_edge("Backend Engineer", "System Design")
        
        # DevOps / Cloud Path
        self.graph.add_edge("Git", "Linux/Bash")
        self.graph.add_edge("Linux/Bash", "Docker")
        self.graph.add_edge("Docker", "Kubernetes")
        self.graph.add_edge("Docker", "AWS")
        self.graph.add_edge("Docker", "Azure")
        self.graph.add_edge("Kubernetes", "DevOps Engineer")
        self.graph.add_edge("AWS", "DevOps Engineer")
        self.graph.add_edge("Azure", "DevOps Engineer")

        # Data Science Path
        self.graph.add_edge("Python", "Pandas")
        self.graph.add_edge("SQL", "Pandas")
        self.graph.add_edge("Pandas", "Machine Learning")
        self.graph.add_edge("Machine Learning", "Deep Learning")
        self.graph.add_edge("Deep Learning", "Data Scientist")

    def get_all_nodes(self):
        return list(self.graph.nodes())

    def get_shortest_path(self, current_skills_mapped, target_role):
        """
        Calculates the missing skills by finding the path from foundational skills to the target role.
        """
        target = target_role
        
        # Basic mapping to standardize target role
        role_map = {
            "frontend": "Frontend Engineer",
            "backend": "Backend Engineer",
            "data": "Data Scientist",
            "devops": "DevOps Engineer",
            "sde": "System Design"
        }
        
        target = role_map.get(target.lower(), "Backend Engineer")  # Default if unknown
            
        if target not in self.graph.nodes():
            target = "Backend Engineer"

        try:
            # Always map from the root so we get the full chronological path
            full_path = nx.shortest_path(self.graph, source="Programming Logic", target=target)
            
            # Remove skills the user already knows from the path
            missing_skills = [skill for skill in full_path if skill not in current_skills_mapped]
            
            # Omit the target role itself
            if target in missing_skills:
                missing_skills.remove(target)
                
            return missing_skills
        except nx.NetworkXNoPath:
            return []
