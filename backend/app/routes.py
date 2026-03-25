from flask import Blueprint, jsonify, request
from .models import db, User
from .services.ml_service import predictor
from .services.company_service import recommender
from .services.ai_engine import ai_service

api_bp = Blueprint('api', __name__)

@api_bp.route('/submit-profile', methods=['POST'])
def submit_profile():
    data = request.get_json(silent=True) or {}
    
    # Validation
    required_fields = ['full_name', 'target_designation', 'branch']
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({"status": "error", "message": f"Missing required fields: {', '.join(missing)}"}), 400
        
    try:
        new_user = User(
            full_name=data.get('full_name'),
            target_designation=data.get('target_designation'),
            cgpa=float(data.get('cgpa', 0)),
            grad_year=int(data.get('grad_year', 2024)),
            branch=data.get('branch'),
            skills=','.join(data.get('skills', [])),
            internships_count=int(data.get('internships_count', 0)),
            projects_count=int(data.get('projects_count', 0))
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "User profile initialized",
            "user_id": new_user.id
        }), 201
    except Exception as e:
        print(f"Error saving profile: {e}")
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 400

# ─── Phase 2: Placement Prediction ───────────────────────────────────────────
@api_bp.route('/predict-placement', methods=['POST'])
def predict_placement():
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"status": "error", "message": "Missing user_id parameter"}), 400
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
        
    prediction_result = predictor.predict_placement_probability(user)
    
    return jsonify({
        "status": "success",
        "result": prediction_result
    })

# ─── Phase 3: Company Recommendations ────────────────────────────────────────
@api_bp.route('/recommend-companies', methods=['POST'])
def recommend_companies():
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"status": "error", "message": "Missing user_id parameter"}), 400
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
        
    recommendations = recommender.recommend(user)
    
    return jsonify({
        "status": "success",
        "user_name": user.full_name,
        "target_designation": user.target_designation,
        "companies": recommendations
    })

# ─── Phase 4: Skill Gap AI Analysis ──────────────────────────────────────────
@api_bp.route('/skill-gap', methods=['POST'])
def analyze_skill_gap():
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"status": "error", "message": "Missing user_id parameter"}), 400
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
    
    analysis = ai_service.analyze_skill_gap(user)
    
    return jsonify({
        "status": "success",
        "analysis": analysis
    })

# ─── Phase 5: AI Roadmap Generator ───────────────────────────────────────────
@api_bp.route('/generate-roadmap', methods=['POST'])
def generate_roadmap():
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"status": "error", "message": "Missing user_id parameter"}), 400
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    # First, get skill gap to supply the roadmap generator
    skill_gap_data = ai_service.analyze_skill_gap(user)
    missing_skills = skill_gap_data.get("missing_skills", [])

    roadmap = ai_service.generate_roadmap(user, missing_skills)
    
    return jsonify({
        "status": "success",
        "roadmap": roadmap,
        "target": user.target_designation
    })

# ─── Phase 6: Full Dashboard Aggregate ───────────────────────────────────────
@api_bp.route('/dashboard', methods=['POST'])
def get_dashboard():
    """Returns all data needed for the dashboard in a single request."""
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"status": "error", "message": "Missing user_id parameter"}), 400
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
    
    # Gather all data
    # Scenario testing: Apply simulated skills if provided
    simulated_skills = data.get('simulated_skills')
    if simulated_skills is not None:
        user.skills = simulated_skills
        
    prediction = predictor.predict_placement_probability(user)
    companies = recommender.recommend(user)
    skill_gap = ai_service.analyze_skill_gap(user)
    
    return jsonify({
        "status": "success",
        "profile": user.to_dict(),
        "prediction": prediction,
        "companies": companies,
        "skill_gap": skill_gap
    })
