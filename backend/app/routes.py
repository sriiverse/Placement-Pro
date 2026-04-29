from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from .models import db, User
from .schemas import ProfileSchema, UserIdSchema, DashboardSchema, format_validation_errors
from .services.ml_service import predictor
from .services.company_service import recommender
from .services.ai_engine import ai_service
from .logger import get_logger, apply_correlation_filter
from .extensions import limiter
from .cache import (
    prediction_cache, companies_cache, skill_gap_cache, roadmap_cache,
    invalidate_all_for_user
)

api_bp = Blueprint('api', __name__)

logger = get_logger("placementpro.routes")
apply_correlation_filter(logger)


# ─── Helper: lookup user or return 404 ───────────────────────────────────────
def _get_user_or_404(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        logger.warning("User not found", extra={"user_id": user_id})
        return None, jsonify({"status": "error", "message": f"User {user_id} not found."}), 404
    return user, None, None


# ─── Phase 1: Profile Submission ─────────────────────────────────────────────
@api_bp.route('/submit-profile', methods=['POST'])
@limiter.limit("10 per minute")
def submit_profile():
    data = request.get_json(silent=True) or {}

    try:
        validated = ProfileSchema(**data)
    except ValidationError as exc:
        errors = format_validation_errors(exc)
        logger.warning("Profile validation failed", extra={"errors": errors})
        return jsonify({"status": "error", "message": "Validation failed.", "errors": errors}), 422

    try:
        new_user = User(
            full_name=validated.full_name,
            target_designation=validated.target_designation,
            cgpa=validated.cgpa,
            grad_year=validated.grad_year,
            branch=validated.branch,
            skills=','.join(validated.skills),
            internships_count=validated.internships_count,
            projects_count=validated.projects_count,
        )
        db.session.add(new_user)
        db.session.commit()

        logger.info(
            "New user profile created",
            extra={
                "user_id": new_user.id,
                "target_designation": validated.target_designation,
                "skills_count": len(validated.skills),
            }
        )
        return jsonify({
            "status": "success",
            "message": "User profile initialized.",
            "user_id": new_user.id
        }), 201

    except Exception as exc:
        db.session.rollback()
        logger.error("Database error saving profile", exc_info=exc)
        return jsonify({"status": "error", "message": "Database error. Please try again."}), 500


# ─── Phase 2: Placement Prediction ───────────────────────────────────────────
@api_bp.route('/predict-placement', methods=['POST'])
def predict_placement():
    data = request.get_json(silent=True) or {}

    try:
        validated = UserIdSchema(**data)
    except ValidationError as exc:
        errors = format_validation_errors(exc)
        logger.warning("predict-placement validation failed", extra={"errors": errors})
        return jsonify({"status": "error", "message": "Validation failed.", "errors": errors}), 422

    user, err_resp, err_code = _get_user_or_404(validated.user_id)
    if err_resp:
        return err_resp, err_code

    # ── Cache check ───────────────────────────────────────────────────────────
    cached = prediction_cache.get(user)
    if cached:
        logger.info("Prediction served from cache", extra={"user_id": user.id})
        return jsonify({"status": "success", "result": cached, "cached": True})

    result = predictor.predict_placement_probability(user)
    prediction_cache.set(user, result)

    logger.info(
        "Placement prediction generated",
        extra={"user_id": user.id, "probability": result.get("probability")}
    )
    return jsonify({"status": "success", "result": result, "cached": False})


# ─── Phase 3: Company Recommendations ────────────────────────────────────────
@api_bp.route('/recommend-companies', methods=['POST'])
def recommend_companies():
    data = request.get_json(silent=True) or {}

    try:
        validated = UserIdSchema(**data)
    except ValidationError as exc:
        errors = format_validation_errors(exc)
        logger.warning("recommend-companies validation failed", extra={"errors": errors})
        return jsonify({"status": "error", "message": "Validation failed.", "errors": errors}), 422

    user, err_resp, err_code = _get_user_or_404(validated.user_id)
    if err_resp:
        return err_resp, err_code

    cached = companies_cache.get(user)
    if cached:
        logger.info("Companies served from cache", extra={"user_id": user.id})
        return jsonify({"status": "success", "user_name": user.full_name,
                        "target_designation": user.target_designation,
                        "companies": cached, "cached": True})

    companies = recommender.recommend(user)
    companies_cache.set(user, companies)

    logger.info(
        "Company recommendations generated",
        extra={"user_id": user.id, "matches_count": len(companies)}
    )
    return jsonify({
        "status": "success",
        "user_name": user.full_name,
        "target_designation": user.target_designation,
        "companies": companies,
        "cached": False
    })


# ─── Phase 4: Skill Gap AI Analysis ──────────────────────────────────────────
@api_bp.route('/skill-gap', methods=['POST'])
def analyze_skill_gap():
    data = request.get_json(silent=True) or {}

    try:
        validated = UserIdSchema(**data)
    except ValidationError as exc:
        errors = format_validation_errors(exc)
        logger.warning("skill-gap validation failed", extra={"errors": errors})
        return jsonify({"status": "error", "message": "Validation failed.", "errors": errors}), 422

    user, err_resp, err_code = _get_user_or_404(validated.user_id)
    if err_resp:
        return err_resp, err_code

    cached = skill_gap_cache.get(user)
    if cached:
        logger.info("Skill gap served from cache", extra={"user_id": user.id})
        return jsonify({"status": "success", "analysis": cached, "cached": True})

    analysis = ai_service.analyze_skill_gap(user)
    skill_gap_cache.set(user, analysis)

    logger.info(
        "Skill gap analysis completed",
        extra={
            "user_id": user.id,
            "readiness_score": analysis.get("readiness_score"),
            "missing_count": len(analysis.get("missing_skills", [])),
        }
    )
    return jsonify({"status": "success", "analysis": analysis, "cached": False})


# ─── Phase 5: AI Roadmap Generator ───────────────────────────────────────────
@api_bp.route('/generate-roadmap', methods=['POST'])
@limiter.limit("5 per minute")
def generate_roadmap():
    data = request.get_json(silent=True) or {}

    try:
        validated = UserIdSchema(**data)
    except ValidationError as exc:
        errors = format_validation_errors(exc)
        logger.warning("generate-roadmap validation failed", extra={"errors": errors})
        return jsonify({"status": "error", "message": "Validation failed.", "errors": errors}), 422

    user, err_resp, err_code = _get_user_or_404(validated.user_id)
    if err_resp:
        return err_resp, err_code

    cached = roadmap_cache.get(user)
    if cached:
        logger.info("Roadmap served from cache", extra={"user_id": user.id})
        return jsonify({"status": "success", "roadmap": cached,
                        "target": user.target_designation, "cached": True})

    logger.info("Generating AI roadmap", extra={"user_id": user.id, "target": user.target_designation})

    skill_gap_data = ai_service.analyze_skill_gap(user)
    missing_skills = skill_gap_data.get("missing_skills", [])
    roadmap = ai_service.generate_roadmap(user, missing_skills)
    roadmap_cache.set(user, roadmap)

    logger.info("Roadmap generated", extra={"user_id": user.id, "weeks": len(roadmap)})
    return jsonify({"status": "success", "roadmap": roadmap,
                    "target": user.target_designation, "cached": False})


# ─── Phase 6: Full Dashboard Aggregate ───────────────────────────────────────
@api_bp.route('/dashboard', methods=['POST'])
@limiter.limit("30 per minute")
def get_dashboard():
    """Returns all data needed for the dashboard in a single request."""
    data = request.get_json(silent=True) or {}

    try:
        validated = DashboardSchema(**data)
    except ValidationError as exc:
        errors = format_validation_errors(exc)
        logger.warning("dashboard validation failed", extra={"errors": errors})
        return jsonify({"status": "error", "message": "Validation failed.", "errors": errors}), 422

    user, err_resp, err_code = _get_user_or_404(validated.user_id)
    if err_resp:
        return err_resp, err_code

    is_simulation = validated.simulated_skills is not None

    if is_simulation:
        # Simulation mode: overlay skills temporarily, never cache simulated results
        user.skills = validated.simulated_skills
        logger.info("Dashboard simulation mode active", extra={"user_id": user.id})
        prediction = predictor.predict_placement_probability(user)
        companies  = recommender.recommend(user)
        skill_gap  = ai_service.analyze_skill_gap(user)
    else:
        # Normal mode: use caches where available
        prediction = prediction_cache.get(user)
        if not prediction:
            prediction = predictor.predict_placement_probability(user)
            prediction_cache.set(user, prediction)

        companies = companies_cache.get(user)
        if not companies:
            companies = recommender.recommend(user)
            companies_cache.set(user, companies)

        skill_gap = skill_gap_cache.get(user)
        if not skill_gap:
            skill_gap = ai_service.analyze_skill_gap(user)
            skill_gap_cache.set(user, skill_gap)

    logger.info(
        "Dashboard aggregated",
        extra={
            "user_id": user.id,
            "simulation": is_simulation,
            "probability": prediction.get("probability"),
            "company_matches": len(companies),
        }
    )
    return jsonify({
        "status": "success",
        "profile":    user.to_dict(),
        "prediction": prediction,
        "companies":  companies,
        "skill_gap":  skill_gap,
        "simulation": is_simulation,
    })
