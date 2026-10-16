import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

CYRILLIC_PATTERN = re.compile(r"[\u0400-\u04FF]")
LATIN_NAME_PATTERN = re.compile(r"^[A-Za-z\s'ʻ’‘`\.\-]+$")
LATIN_SCHOOL_PATTERN = re.compile(r"^[A-Za-z0-9\s'ʻ’‘`\.\-,\/#№()&]+$")

class SubmissionCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255, description="Full Name (F.I.Sh / Ф.И.О)")
    phone: str = Field(..., min_length=7, max_length=50, description="Phone number")
    telegram_username: str = Field(..., min_length=2, max_length=100, description="Telegram User Name")
    region: str = Field(..., min_length=2, max_length=100, description="Selected region")
    school: str = Field(..., min_length=2, max_length=255, description="School/Lyceum where applicant studies")
    question_text: Optional[str] = Field(None, max_length=2000, description="Optional question or comment")

    @field_validator("full_name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 2:
            raise ValueError("Name is too short")
        if CYRILLIC_PATTERN.search(clean):
            raise ValueError("Full name must be entered only in English (Latin) alphabet. Cyrillic letters are not allowed.")
        if not LATIN_NAME_PATTERN.match(clean):
            raise ValueError("Full name contains invalid characters. Use English letters, spaces, and apostrophes only.")
        return clean

    @field_validator("school")
    @classmethod
    def validate_school(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 2:
            raise ValueError("School name is too short")
        if CYRILLIC_PATTERN.search(clean):
            raise ValueError("School name must be entered only in English (Latin) alphabet. Cyrillic letters are not allowed.")
        if not LATIN_SCHOOL_PATTERN.match(clean):
            raise ValueError("School name contains invalid characters. Use English letters, numbers, and standard punctuation only.")
        return clean

    @field_validator("telegram_username")
    @classmethod
    def format_telegram_username(cls, v: str) -> str:
        clean = v.strip()
        if not clean.startswith("@"):
            clean = f"@{clean}"
        if CYRILLIC_PATTERN.search(clean):
            raise ValueError("Telegram username must contain only English (Latin) letters and numbers.")
        handle = clean[1:]
        if not re.match(r"^[a-zA-Z0-9_]+$", handle):
            raise ValueError("Telegram username must contain only Latin characters, digits, or underscores.")
        return clean

    @field_validator("question_text")
    @classmethod
    def validate_question(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        clean = v.strip()
        if not clean:
            return None
        if CYRILLIC_PATTERN.search(clean):
            raise ValueError("Question/comment must be entered only in English (Latin) alphabet. Cyrillic letters are not allowed.")
        return clean

class SubmissionResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    telegram_username: str
    region: str
    school: str
    question_text: Optional[str] = None
    telegram_sent: bool
    status: Optional[str] = "Yangi"
    is_contacted: bool = False
    contacted_by: Optional[str] = None
    contacted_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class HealthResponse(BaseModel):
    status: str
    project: str
    telegram_configured: bool
    db_connected: bool

class AdminLoginRequest(BaseModel):
    username: str
    password: str

