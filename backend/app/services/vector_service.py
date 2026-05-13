import numpy as np
from functools import lru_cache

class VectorService:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Lazy-loads the Semantic Embedding model on first use.
        This prevents blocking the Gunicorn startup sequence.
        all-MiniLM-L6-v2 is ~80MB and perfect for CPU similarity tasks.
        """
        self._model_name = model_name
        self._model = None  # Loaded on first use, not at startup

    @property
    def model(self):
        """Lazy-load the model on first access."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
        return self._model
    
    def encode_skills(self, skills_list):
        if not skills_list:
            return []
        return self.model.encode(skills_list)
        
    @lru_cache(maxsize=4096)
    def _encode_single(self, skill_string: str):
        """Memoized embedding generation for single skills to leverage high RAM."""
        return self.model.encode([skill_string])[0]
        
    def _cosine_similarity(self, vec1, vec2):
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    def map_user_skills_to_graph(self, user_skills, graph_nodes, threshold=0.60):
        """
        Takes messy user string array (e.g. ['some react stuff', 'db'])
        and maps them to strict Graph Nodes (e.g. ['React', 'Databases'])
        using Semantic Cosine Similarity.
        """
        if not user_skills or not graph_nodes:
            return []
            
        # Encode graph nodes globally
        node_embeddings = self.encode_skills(graph_nodes)
        
        mapped_skills = set()
        
        for user_skill in user_skills:
            clean_skill = user_skill.strip()
            if not clean_skill:
                continue
                
            user_embedding = self._encode_single(clean_skill)
            
            best_match = None
            best_score = -1
            
            for idx, node_name in enumerate(graph_nodes):
                score = self._cosine_similarity(user_embedding, node_embeddings[idx])
                if score > best_score:
                    best_score = score
                    best_match = node_name
                    
            if best_score >= threshold and best_match:
                mapped_skills.add(best_match)
                
        return list(mapped_skills)
