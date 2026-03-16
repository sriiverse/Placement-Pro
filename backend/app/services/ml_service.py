import numpy as np

class PlacementPredictor:
    def __init__(self):
        # Initializing dummy coefficients for a heuristic weighted model
        # For Phase 2 MVP, we'll use a rule-based weighted sum passed through a sigmoid
        # to guarantee realistic 0-100 prediction probabilities.
        self.weights = {
            'cgpa': 0.5,
            'internships': 1.2,
            'projects': 0.8,
            'tech_stack': 0.3 # weight per relevant skill
        }
        
        self.high_value_skills = [
            'react', 'node', 'python', 'java', 'aws', 'docker', 'kubernetes',
            'machine learning', 'sql', 'mongodb', 'system design', 'c++'
        ]

    def _calculate_base_score(self, user):
        score = 0
        
        # CGPA impact (normalized roughly around 7.0 - 10.0)
        cgpa_normalized = (user.cgpa - 6.0) / 4.0 if user.cgpa > 6.0 else 0
        score += cgpa_normalized * self.weights['cgpa'] * 5 
        
        # Internship impact
        score += min(user.internships_count, 3) * self.weights['internships']
        
        # Projects impact
        score += min(user.projects_count, 5) * self.weights['projects']
        
        # Skills impact
        if user.skills:
            user_skill_list = [s.strip().lower() for s in user.skills.split(',')]
            relevant_skills = sum(1 for skill in user_skill_list if any(h_s in skill for h_s in self.high_value_skills))
            score += relevant_skills * self.weights['tech_stack']

        return score

    def predict_placement_probability(self, user):
        """
        Returns a probability score between 0 and 100 based on the user's profile.
        Uses a sigmoid function to curve the scores realistically.
        """
        if not user:
            return 0.0

        raw_score = self._calculate_base_score(user)
        
        # Base offset to center the sigmoid (assume an average profile gets ~50-60%)
        # Shift the raw score so that a "good" profile lands on the upper asymptote
        shifted_score = raw_score - 4.5 
        
        # Sigmoid function for 0 to 1 mapping
        probability = 1 / (1 + np.exp(-shifted_score))
        
        # Scale to percentage
        final_percentage = round(probability * 100, 2)
        
        # Formatting confidence string
        confidence = "HIGH" if final_percentage > 75 else "MEDIUM" if final_percentage > 45 else "LOW"
        
        # Identify quick win factors
        factors = []
        if user.cgpa < 7.5:
            factors.append("CGPA below optimal threshold")
        if user.internships_count == 0:
            factors.append("No internship experience")
        elif user.internships_count >= 2:
            factors.append("Strong practical experience")
        if user.projects_count > 3:
            factors.append("Excellent project portfolio")

        return {
            "probability": final_percentage,
            "confidence": confidence,
            "key_factors": factors
        }

predictor = PlacementPredictor()
