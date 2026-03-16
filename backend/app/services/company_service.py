"""
Phase 3: Company Recommendation Engine
Uses skill matching and CGPA heuristics to map users to top companies.
"""

COMPANY_DATABASE = [
    {
        "name": "Google",
        "roles": ["Software Engineer", "ML Engineer", "Data Scientist"],
        "required_skills": ["python", "algorithms", "system design", "data structures"],
        "min_cgpa": 8.0,
        "tier": "TIER_1",
        "package_lpa": "25-50",
        "logo_color": "#4285F4"
    },
    {
        "name": "Microsoft",
        "roles": ["SDE", "Cloud Engineer", "Product Manager"],
        "required_skills": ["c++", "java", "azure", "algorithms"],
        "min_cgpa": 7.5,
        "tier": "TIER_1",
        "package_lpa": "20-45",
        "logo_color": "#00A4EF"
    },
    {
        "name": "Amazon",
        "roles": ["SDE", "DevOps Engineer", "Solutions Architect"],
        "required_skills": ["aws", "java", "python", "docker", "system design"],
        "min_cgpa": 7.0,
        "tier": "TIER_1",
        "package_lpa": "18-40",
        "logo_color": "#FF9900"
    },
    {
        "name": "Meta",
        "roles": ["Frontend Engineer", "ML Engineer", "Backend Engineer"],
        "required_skills": ["react", "python", "machine learning", "system design"],
        "min_cgpa": 7.5,
        "tier": "TIER_1",
        "package_lpa": "22-48",
        "logo_color": "#0668E1"
    },
    {
        "name": "Flipkart",
        "roles": ["SDE", "Backend Engineer", "Data Analyst"],
        "required_skills": ["java", "mysql", "python", "sql"],
        "min_cgpa": 7.0,
        "tier": "TIER_2",
        "package_lpa": "15-28",
        "logo_color": "#2874F0"
    },
    {
        "name": "Swiggy",
        "roles": ["SDE", "React Developer", "ML Engineer"],
        "required_skills": ["react", "node", "python", "mongodb"],
        "min_cgpa": 6.5,
        "tier": "TIER_2",
        "package_lpa": "12-25",
        "logo_color": "#FC8019"
    },
    {
        "name": "Razorpay",
        "roles": ["Backend Engineer", "SDE", "Payment Systems Engineer"],
        "required_skills": ["python", "java", "node", "sql"],
        "min_cgpa": 7.0,
        "tier": "TIER_2",
        "package_lpa": "14-30",
        "logo_color": "#3395FF"
    },
    {
        "name": "Zomato",
        "roles": ["Backend SDE", "Data Engineer", "Frontend Dev"],
        "required_skills": ["python", "react", "sql", "node"],
        "min_cgpa": 6.5,
        "tier": "TIER_2",
        "package_lpa": "12-22",
        "logo_color": "#E23744"
    },
    {
        "name": "Infosys",
        "roles": ["Systems Engineer", "Java Developer", "Analyst"],
        "required_skills": ["java", "sql", "python"],
        "min_cgpa": 6.0,
        "tier": "TIER_3",
        "package_lpa": "4-8",
        "logo_color": "#007CC3"
    },
    {
        "name": "TCS",
        "roles": ["Developer", "Analyst", "Digital Engineer"],
        "required_skills": ["java", "python", "sql", "c++"],
        "min_cgpa": 6.0,
        "tier": "TIER_3",
        "package_lpa": "3.5-7",
        "logo_color": "#FF0000"
    },
]

class CompanyRecommender:
    def recommend(self, user):
        if not user:
            return []

        user_skills = [s.strip().lower() for s in user.skills.split(',')] if user.skills else []
        recommendations = []

        for company in COMPANY_DATABASE:
            # Check CGPA eligibility
            if user.cgpa < company["min_cgpa"]:
                continue

            # Calculate skill match score
            company_skills = company["required_skills"]
            matched_skills = [s for s in company_skills if any(s in user_s for user_s in user_skills)]
            if len(company_skills) == 0:
                skill_match_pct = 50
            else:
                skill_match_pct = round((len(matched_skills) / len(company_skills)) * 100, 1)

            # Only recommend if at least 25% skills match
            if skill_match_pct < 25:
                continue

            # CGPA bonus
            cgpa_bonus = min((user.cgpa - company["min_cgpa"]) * 5, 20)

            # Experience bonus
            exp_bonus = min((user.internships_count * 5) + (user.projects_count * 2), 20)

            final_score = min(skill_match_pct + cgpa_bonus + exp_bonus, 99.5)

            recommendations.append({
                "name": company["name"],
                "tier": company["tier"],
                "match_score": round(final_score, 1),
                "matched_skills": matched_skills,
                "roles": company["roles"][:2],
                "package_lpa": company["package_lpa"],
                "logo_color": company["logo_color"]
            })

        # Sort by match score descending
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        return recommendations[:6]  # Top 6


recommender = CompanyRecommender()
