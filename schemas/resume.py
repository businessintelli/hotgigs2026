from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from schemas.common import BaseResponse


class ResumeCreate(BaseModel):
    """Resume creation schema."""

    candidate_id: int
    file_name: str = Field(min_length=1, max_length=255)
    file_type: str = Field(max_length=50)
    file_size: int = Field(ge=0)
    is_primary: Optional[bool] = Field(default=False)


class ResumeUpdate(BaseModel):
    """Resume update schema."""

    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None


class ResumeResponse(BaseResponse):
    """Resume response schema."""

    candidate_id: int
    file_path: str
    file_name: str
    file_type: str
    file_size: int
    is_primary: bool
    uploaded_at: datetime

    class Config:
        from_attributes = True


class ParsedResumeCreate(BaseModel):
    """Parsed resume creation schema."""

    resume_id: int
    raw_text: Optional[str] = None
    skills_extracted: Optional[List[str]] = Field(default_factory=list)
    experience_extracted: Optional[List[dict]] = Field(default_factory=list)
    education_extracted: Optional[List[dict]] = Field(default_factory=list)
    certifications_extracted: Optional[List[str]] = Field(default_factory=list)
    parsing_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    parser_version: Optional[str] = Field(default=None, max_length=50)


class ParsedResumeResponse(BaseResponse):
    """Parsed resume response schema."""

    resume_id: int
    raw_text: Optional[str] = None
    parsed_data: Optional[dict] = None
    skills_extracted: Optional[List[str]] = None
    experience_extracted: Optional[List[dict]] = None
    education_extracted: Optional[List[dict]] = None
    certifications_extracted: Optional[List[str]] = None
    parsing_confidence: Optional[float] = None
    parser_version: Optional[str] = None
    parsed_at: datetime

    class Config:
        from_attributes = True
