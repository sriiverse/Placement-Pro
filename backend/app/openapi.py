"""
openapi.py — Hand-crafted OpenAPI 3.0 specification for PlacementPro+ API.

This generates a spec dict that Flask serves at /api/docs/openapi.json.
The Swagger UI at /api/docs/ reads this JSON and renders interactive docs.

Why hand-crafted instead of flask-apispec auto-generation?
  - Our routes use Pydantic v2 (not Marshmallow), so flask-apispec cannot
    auto-introspect them.
  - A hand-crafted spec is more stable, portable, and easier to extend.
"""

OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "PlacementPro+ API",
        "version": "2.0.0",
        "description": (
            "Neuro-Symbolic AI Engine for Placement Prediction & Personalized Roadmaps. "
            "All `/api/` endpoints (except `/api/auth/*`) require a JWT Bearer token."
        ),
        "contact": {
            "name": "PlacementPro+ Team",
            "url": "https://github.com/sriiverse/Placement-Pro"
        },
        "license": {"name": "MIT"}
    },
    "servers": [
        {"url": "http://localhost:5000", "description": "Local development"},
        {"url": "https://vamsi25-placement-os.hf.space", "description": "Hugging Face Spaces (production)"},
    ],

    # ─── Reusable Components ───────────────────────────────────────────────────
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT access token — obtain from POST /api/auth/login"
            }
        },
        "schemas": {
            "Error": {
                "type": "object",
                "properties": {
                    "status":  {"type": "string", "example": "error"},
                    "message": {"type": "string", "example": "Validation failed."},
                    "errors":  {"type": "array", "items": {"type": "string"}}
                }
            },
            "ProfileRequest": {
                "type": "object",
                "required": ["full_name", "target_designation", "cgpa", "grad_year", "branch", "skills"],
                "properties": {
                    "full_name":          {"type": "string", "example": "Alice Smith"},
                    "target_designation": {"type": "string", "example": "Software Engineer"},
                    "cgpa":               {"type": "number", "minimum": 0, "maximum": 10, "example": 8.5},
                    "grad_year":          {"type": "integer", "minimum": 2020, "maximum": 2030, "example": 2025},
                    "branch":             {"type": "string", "example": "Computer Science"},
                    "skills":             {"type": "array", "items": {"type": "string"}, "example": ["Python", "React", "Docker"]},
                    "internships_count":  {"type": "integer", "minimum": 0, "default": 0, "example": 2},
                    "projects_count":     {"type": "integer", "minimum": 0, "default": 0, "example": 4}
                }
            },
            "UserIdRequest": {
                "type": "object",
                "required": ["user_id"],
                "properties": {
                    "user_id": {"type": "integer", "example": 1}
                }
            },
            "DashboardRequest": {
                "type": "object",
                "required": ["user_id"],
                "properties": {
                    "user_id":          {"type": "integer", "example": 1},
                    "simulated_skills": {"type": "string", "nullable": True, "example": "Python,React,Docker,Kubernetes"}
                }
            },
            "PredictionResult": {
                "type": "object",
                "properties": {
                    "probability":  {"type": "number", "example": 73.4},
                    "confidence":   {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
                    "key_factors":  {"type": "array", "items": {"type": "string"}}
                }
            },
            "Company": {
                "type": "object",
                "properties": {
                    "name":           {"type": "string", "example": "Google"},
                    "tier":           {"type": "string", "enum": ["TIER_1", "TIER_2", "TIER_3"]},
                    "match_score":    {"type": "number", "example": 87.5},
                    "matched_skills": {"type": "array", "items": {"type": "string"}},
                    "roles":          {"type": "array", "items": {"type": "string"}},
                    "package_lpa":    {"type": "string", "example": "25-50"},
                    "logo_color":     {"type": "string", "example": "#4285F4"}
                }
            },
            "AuthRequest": {
                "type": "object",
                "required": ["email", "password"],
                "properties": {
                    "email":    {"type": "string", "format": "email", "example": "user@example.com"},
                    "password": {"type": "string", "minLength": 6, "example": "secretpass123"}
                }
            },
            "AuthResponse": {
                "type": "object",
                "properties": {
                    "status":        {"type": "string", "example": "success"},
                    "access_token":  {"type": "string"},
                    "refresh_token": {"type": "string"},
                    "user": {
                        "type": "object",
                        "properties": {
                            "id":         {"type": "integer"},
                            "email":      {"type": "string"},
                            "created_at": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            }
        },
        "responses": {
            "UnauthorizedError": {
                "description": "JWT token missing or invalid",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
            },
            "NotFoundError": {
                "description": "Resource not found",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
            },
            "ValidationError": {
                "description": "Request body failed Pydantic validation",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
            },
            "RateLimitError": {
                "description": "Too many requests",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
            }
        }
    },

    # ─── Global security (applied to all routes) ───────────────────────────────
    "security": [{"BearerAuth": []}],

    # ─── Paths ────────────────────────────────────────────────────────────────
    "paths": {
        "/health": {
            "get": {
                "tags": ["Infrastructure"],
                "summary": "Liveness probe",
                "description": "Returns 200 immediately if the process is alive. Used by Docker HEALTHCHECK.",
                "security": [],
                "responses": {
                    "200": {
                        "description": "Service is alive",
                        "content": {"application/json": {"schema": {
                            "type": "object",
                            "properties": {
                                "status":  {"type": "string", "example": "healthy"},
                                "service": {"type": "string", "example": "placement-pro-core"}
                            }
                        }}}
                    }
                }
            }
        },
        "/ready": {
            "get": {
                "tags": ["Infrastructure"],
                "summary": "Readiness probe",
                "description": "Deep check — verifies DB connectivity and disk space. Returns 503 if degraded.",
                "security": [],
                "responses": {
                    "200": {"description": "Service is fully ready"},
                    "503": {"description": "Service is degraded (dependency unreachable)"}
                }
            }
        },
        "/api/auth/register": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Register a new account",
                "description": "Creates a new AuthUser and returns JWT access + refresh tokens. Rate limited to 3/minute.",
                "security": [],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AuthRequest"}}}
                },
                "responses": {
                    "201": {"description": "Account created", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AuthResponse"}}}},
                    "400": {"description": "Missing or invalid fields"},
                    "409": {"description": "Email already registered"},
                    "429": {"$ref": "#/components/responses/RateLimitError"}
                }
            }
        },
        "/api/auth/login": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Login",
                "description": "Authenticate with email + password. Returns JWT access + refresh tokens. Rate limited to 5/minute.",
                "security": [],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AuthRequest"}}}
                },
                "responses": {
                    "200": {"description": "Login successful", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AuthResponse"}}}},
                    "401": {"description": "Invalid email or password"},
                    "429": {"$ref": "#/components/responses/RateLimitError"}
                }
            }
        },
        "/api/auth/refresh": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Refresh access token",
                "description": "Exchange a valid refresh token for a new access token.",
                "responses": {
                    "200": {"description": "New access token issued"},
                    "401": {"$ref": "#/components/responses/UnauthorizedError"}
                }
            }
        },
        "/api/auth/me": {
            "get": {
                "tags": ["Authentication"],
                "summary": "Get current user",
                "description": "Returns the authenticated user's account info. Used to rehydrate the frontend session.",
                "responses": {
                    "200": {"description": "User info returned"},
                    "401": {"$ref": "#/components/responses/UnauthorizedError"}
                }
            }
        },
        "/api/submit-profile": {
            "post": {
                "tags": ["Profile"],
                "summary": "Submit placement profile",
                "description": "Creates a new placement profile with full Pydantic validation. Rate limited to 10/minute.",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ProfileRequest"}}}
                },
                "responses": {
                    "201": {"description": "Profile created", "content": {"application/json": {"schema": {
                        "type": "object",
                        "properties": {
                            "status":  {"type": "string", "example": "success"},
                            "user_id": {"type": "integer", "example": 1}
                        }
                    }}}},
                    "422": {"$ref": "#/components/responses/ValidationError"},
                    "429": {"$ref": "#/components/responses/RateLimitError"}
                }
            }
        },
        "/api/predict-placement": {
            "post": {
                "tags": ["AI Engine"],
                "summary": "Predict placement probability",
                "description": "Runs the ML scoring model against the user's profile and returns a probability + confidence.",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserIdRequest"}}}
                },
                "responses": {
                    "200": {"description": "Prediction result", "content": {"application/json": {"schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "result": {"$ref": "#/components/schemas/PredictionResult"}
                        }
                    }}}},
                    "404": {"$ref": "#/components/responses/NotFoundError"}
                }
            }
        },
        "/api/recommend-companies": {
            "post": {
                "tags": ["AI Engine"],
                "summary": "Get company recommendations",
                "description": "Returns up to 6 companies ranked by skill match score and CGPA eligibility.",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserIdRequest"}}}
                },
                "responses": {
                    "200": {"description": "Company list", "content": {"application/json": {"schema": {
                        "type": "object",
                        "properties": {
                            "status":    {"type": "string"},
                            "companies": {"type": "array", "items": {"$ref": "#/components/schemas/Company"}}
                        }
                    }}}},
                    "404": {"$ref": "#/components/responses/NotFoundError"}
                }
            }
        },
        "/api/skill-gap": {
            "post": {
                "tags": ["AI Engine"],
                "summary": "Analyze skill gap",
                "description": "Uses the Neuro-Symbolic engine to identify missing skills and generate a readiness score.",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserIdRequest"}}}
                },
                "responses": {
                    "200": {"description": "Skill gap analysis"},
                    "404": {"$ref": "#/components/responses/NotFoundError"}
                }
            }
        },
        "/api/generate-roadmap": {
            "post": {
                "tags": ["AI Engine"],
                "summary": "Generate 12-week AI roadmap",
                "description": "Combines skill gap analysis with knowledge graph traversal to produce a personalized 12-week study plan. Compute-heavy — rate limited to 5/minute.",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserIdRequest"}}}
                },
                "responses": {
                    "200": {"description": "12-week roadmap"},
                    "404": {"$ref": "#/components/responses/NotFoundError"},
                    "429": {"$ref": "#/components/responses/RateLimitError"}
                }
            }
        },
        "/api/dashboard": {
            "post": {
                "tags": ["AI Engine"],
                "summary": "Aggregate dashboard data",
                "description": "Single call returning prediction + companies + skill_gap. Supports skill simulation mode via `simulated_skills`. Rate limited to 30/minute.",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/DashboardRequest"}}}
                },
                "responses": {
                    "200": {"description": "Aggregated dashboard payload"},
                    "404": {"$ref": "#/components/responses/NotFoundError"},
                    "429": {"$ref": "#/components/responses/RateLimitError"}
                }
            }
        }
    },

    # ─── Tags (controls sidebar grouping in Swagger UI) ───────────────────────
    "tags": [
        {"name": "Infrastructure", "description": "Health and readiness probes"},
        {"name": "Authentication",  "description": "JWT register / login / refresh"},
        {"name": "Profile",         "description": "Student placement profile management"},
        {"name": "AI Engine",       "description": "Prediction, company matching, skill gap, and roadmap generation"},
    ]
}
