"""
Phase 4 & 5: LLM Service using Google Gemini
Powers the SkillGap AI Analysis and Roadmap Generation.
"""
import os
import google.generativeai as genai

class GeminiService:
    def __init__(self):
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key and api_key != 'your_gemini_api_key_here':
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
        else:
            self.enabled = False

    def analyze_skill_gap(self, user, target_company=None):
        """Phase 4: SkillGap AI Analysis"""
        user_skills = user.skills if user.skills else ""
        target = target_company or user.target_designation

        if not self.enabled:
            # Return a curated mock response if Gemini key is not configured
            return self._mock_skill_gap(user_skills, target)

        prompt = f"""You are a technical hiring expert. Analyze the skill gap for this candidate:

Candidate Profile:
- Target Role: {target}
- Current Skills: {user_skills}
- CGPA: {user.cgpa}
- Internships: {user.internships_count}
- Projects: {user.projects_count}

Provide a structured JSON response with:
{{
  "missing_skills": ["skill1", "skill2", "skill3"],
  "skill_gaps": [
    {{"skill": "System Design", "priority": "HIGH", "reason": "...", "resources": ["resource1"]}}
  ],
  "strengths": ["strength1", "strength2"],
  "readiness_score": 75,
  "summary": "2-sentence analysis"
}}

Be concise and specific to the target role."""

        try:
            response = self.model.generate_content(prompt)
            import json, re
            text = response.text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"Gemini error: {e}")

        return self._mock_skill_gap(user_skills, target)

    def generate_roadmap(self, user, skill_gaps):
        """Phase 5: AI Roadmap Generator"""
        target = user.target_designation
        
        if not self.enabled:
            return self._mock_roadmap(target, skill_gaps)

        gap_list = ', '.join(skill_gaps) if skill_gaps else 'general software engineering skills'
        
        prompt = f"""Create a 12-week personalized placement preparation roadmap for:
- Target Role: {target}
- Skill Gaps to Address: {gap_list}
- Current Skills: {user.skills}

Return a JSON array of weekly milestones:
[
  {{
    "week": 1,
    "theme": "Foundation Building", 
    "topics": ["topic1", "topic2"],
    "resources": ["resource1"],
    "milestone": "Complete X"
  }}
]

Generate exactly 12 weeks. Be very specific and action-oriented."""

        try:
            response = self.model.generate_content(prompt)
            import json, re
            text = response.text
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"Gemini error: {e}")

        return self._mock_roadmap(target, skill_gaps)

    def _mock_skill_gap(self, user_skills, target):
        """Curated mock response for when Gemini is not configured"""
        skills_lower = user_skills.lower()
        missing = []
        if "system design" not in skills_lower:
            missing.append("System Design")
        if "sql" not in skills_lower and "postgresql" not in skills_lower:
            missing.append("SQL / Databases")
        if "docker" not in skills_lower:
            missing.append("Docker / Containerization")
        if not missing:
            missing = ["Advanced DSA", "Cloud Deployment"]

        return {
            "missing_skills": missing,
            "skill_gaps": [
                {"skill": missing[0], "priority": "HIGH", "reason": f"Critical for {target} interviews", "resources": ["LeetCode", "System Design Primer"]},
                {"skill": "DSA & Algorithms", "priority": "HIGH", "reason": "Required for technical rounds", "resources": ["CLRS Book", "LeetCode Top 150"]}
            ],
            "strengths": [s.strip() for s in user_skills.split(',')[:3] if s.strip()],
            "readiness_score": 65,
            "summary": f"The candidate shows promise for a {target} role but needs to strengthen system design and DSA skills. Focus on the identified gaps over the next 12 weeks."
        }

    def _mock_roadmap(self, target, skill_gaps):
        """12-week curated roadmap"""
        return [
            {"week": 1, "theme": "DSA Foundation", "topics": ["Arrays & Strings", "Big-O Analysis"], "resources": ["LeetCode Easy 50"], "milestone": "Solve 25 easy DSA problems"},
            {"week": 2, "theme": "Linked Lists & Stacks", "topics": ["Linked Lists", "Stacks & Queues"], "resources": ["NeetCode.io"], "milestone": "Master 3 linked list patterns"},
            {"week": 3, "theme": "Trees & Recursion", "topics": ["Binary Trees", "DFS/BFS", "Recursion"], "resources": ["Visualgo.net"], "milestone": "Solve 20 tree problems"},
            {"week": 4, "theme": "Dynamic Programming Intro", "topics": ["Memoization", "Tabulation", "Classic DP"], "resources": ["DP Patterns - Aditya Verma"], "milestone": "Complete DP playlist"},
            {"week": 5, "theme": "System Design Basics", "topics": ["Load Balancing", "Caching", "CDN", "Databases"], "resources": ["System Design Primer GitHub"], "milestone": "Design 3 basic systems"},
            {"week": 6, "theme": "Databases & SQL", "topics": ["SQL Joins", "Indexing", "Normalization", "NoSQL"], "resources": ["SQLZoo", "MongoDB University"], "milestone": "Complete 30 SQL challenges"},
            {"week": 7, "theme": "Web Technologies", "topics": ["REST APIs", "HTTP", "Authentication", "WebSockets"], "resources": ["MDN Web Docs"], "milestone": "Build a REST API project"},
            {"week": 8, "theme": "Cloud & DevOps", "topics": ["Docker", "CI/CD", "AWS Basics", "Kubernetes intro"], "resources": ["AWS Free Tier", "Docker Docs"], "milestone": "Deploy an app on cloud"},
            {"week": 9, "theme": "Advanced System Design", "topics": ["Microservices", "Message Queues", "Distributed Systems"], "resources": ["ByteByteGo Book"], "milestone": "Design Twitter / URL Shortener"},
            {"week": 10, "theme": "Mock Interviews", "topics": ["Behavioral Questions", "STAR Method", "HR Round Prep"], "resources": ["Pramp.com", "Interviewing.io"], "milestone": "Complete 5 mock interviews"},
            {"week": 11, "theme": "Company-Specific Prep", "topics": [f"Standard {target} Interview Patterns", "OOP Concepts", "Concurrency"], "resources": ["Company Interview Guides on GitHub"], "milestone": "Solve 20 company-tagged problems"},
            {"week": 12, "theme": "Final Sprint & Revision", "topics": ["High-frequency patterns", "Resume polish", "System design revision"], "resources": ["All previous resources"], "milestone": "Ready for placement season!"}
        ]


gemini_service = GeminiService()
