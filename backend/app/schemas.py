"""
Pydantic v2 schemas for request validation.

Every incoming API request body is validated against these schemas before
any business logic runs. This gives us:
  - Automatic type coercion  (e.g. "8.5" str → 8.5 float)
  - Clear, structured error messages instead of raw Python exceptions
  - A single source of truth for what the API accepts
"""

import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# ─── Profile Submission ───────────────────────────────────────────────────────

class ProfileSchema(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    target_designation: str = Field(..., min_length=2, max_length=100)
    cgpa: float = Field(..., ge=0.0, le=10.0)
    grad_year: int = Field(..., ge=2020, le=2030)
    branch: str = Field(..., min_length=2, max_length=100)
    skills: List[str] = Field(..., min_length=1)
    internships_count: int = Field(default=0, ge=0, le=50)
    projects_count: int = Field(default=0, ge=0, le=100)

    @field_validator('full_name', 'target_designation', 'branch')
    @classmethod
    def only_alphabets_and_spaces(cls, v: str, info) -> str:
        """Reject strings that contain digits or special characters."""
        if not re.match(r'^[a-zA-Z\s\-/]+$', v.strip()):
            raise ValueError(
                f"'{info.field_name}' must contain only letters, spaces, or hyphens."
            )
        return v.strip()

    @field_validator('skills')
    @classmethod
    def skills_not_empty(cls, v: List[str]) -> List[str]:
        """Strip whitespace and remove blank entries."""
        cleaned = [s.strip() for s in v if s.strip()]
        if not cleaned:
            raise ValueError("At least one skill must be provided.")
        return cleaned

    @field_validator('full_name', 'target_designation', 'branch', mode='before')
    @classmethod
    def strip_strings(cls, v) -> str:
        if isinstance(v, str):
            return v.strip()
        return v


# ─── User-ID Based Requests ───────────────────────────────────────────────────

class UserIdSchema(BaseModel):
    """Used by endpoints that just need a valid user_id."""
    user_id: int = Field(..., gt=0)


class DashboardSchema(BaseModel):
    """Dashboard request — user_id required, simulated_skills optional."""
    user_id: int = Field(..., gt=0)
    simulated_skills: Optional[str] = None

    @field_validator('simulated_skills')
    @classmethod
    def validate_simulated_skills(cls, v: Optional[str]) -> Optional[str]:
        """Allow None or a non-empty comma-separated string."""
        if v is not None and not v.strip():
            return None
        return v


# ─── Helper: format Pydantic errors for API responses ────────────────────────

def format_validation_errors(exc) -> list:
    """
    Convert a Pydantic ValidationError into a flat list of human-readable
    error strings suitable for returning in an API response.
    """
    errors = []
    for err in exc.errors():
        field = ' → '.join(str(loc) for loc in err['loc'])
        msg = err['msg']
        errors.append(f"{field}: {msg}")
    return errors
