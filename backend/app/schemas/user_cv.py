import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field


# Base schemas for CV components

class CVFileBase(SQLModel):
    file_url: str = Field(max_length=500)
    file_name: str = Field(max_length=255)
    file_type: str = Field(max_length=50)
    file_size: int | None = None
    status: str = Field(default="submitted", max_length=50)
    review_notes: str | None = Field(default=None, max_length=1000)
    is_primary: bool = False
    version: int = 1


class CVFileCreate(CVFileBase):
    user_cv_id: uuid.UUID


class CVFileUpdate(SQLModel):
    status: str | None = None
    review_notes: str | None = None
    is_primary: bool | None = None
    reviewed_by_id: uuid.UUID | None = None


class CVFilePublic(CVFileBase):
    id: uuid.UUID
    user_cv_id: uuid.UUID
    reviewed_by_id: uuid.UUID | None = None
    reviewed_at: datetime | None = None


# Education schemas
class CVEducationBase(SQLModel):
    institution: str = Field(max_length=255)
    degree: str = Field(max_length=100)
    field_of_study: str = Field(max_length=255)
    start_date: str = Field(max_length=7)
    end_date: str | None = Field(default=None, max_length=7)
    gpa: str | None = None
    description: str | None = None
    city: str | None = None
    country: str | None = None
    display_order: int = 0


class CVEducationCreate(CVEducationBase):
    user_cv_id: uuid.UUID


class CVEducationUpdate(SQLModel):
    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    gpa: str | None = None
    description: str | None = None
    city: str | None = None
    country: str | None = None
    display_order: int | None = None


class CVEducationPublic(CVEducationBase):
    id: uuid.UUID
    user_cv_id: uuid.UUID


# Work Experience schemas
class CVWorkExperienceBase(SQLModel):
    company: str = Field(max_length=255)
    position: str = Field(max_length=255)
    start_date: str = Field(max_length=7)
    end_date: str | None = None
    description: str | None = None
    employment_type: str | None = None
    city: str | None = None
    country: str | None = None
    is_remote: bool = False
    display_order: int = 0


class CVWorkExperienceCreate(CVWorkExperienceBase):
    user_cv_id: uuid.UUID


class CVWorkExperienceUpdate(SQLModel):
    company: str | None = None
    position: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    employment_type: str | None = None
    city: str | None = None
    country: str | None = None
    is_remote: bool | None = None
    display_order: int | None = None


class CVWorkExperiencePublic(CVWorkExperienceBase):
    id: uuid.UUID
    user_cv_id: uuid.UUID


# Skill schemas
class CVSkillBase(SQLModel):
    name: str = Field(max_length=100)
    level: str | None = None
    category: str | None = None
    years_of_experience: int | None = None
    display_order: int = 0


class CVSkillCreate(CVSkillBase):
    user_cv_id: uuid.UUID


class CVSkillUpdate(SQLModel):
    name: str | None = None
    level: str | None = None
    category: str | None = None
    years_of_experience: int | None = None
    display_order: int | None = None


class CVSkillPublic(CVSkillBase):
    id: uuid.UUID
    user_cv_id: uuid.UUID


# Certification schemas
class CVCertificationBase(SQLModel):
    name: str = Field(max_length=255)
    issuer: str = Field(max_length=255)
    issue_date: str = Field(max_length=7)
    expiration_date: str | None = None
    credential_id: str | None = None
    credential_url: str | None = None
    description: str | None = None
    display_order: int = 0


class CVCertificationCreate(CVCertificationBase):
    user_cv_id: uuid.UUID


class CVCertificationUpdate(SQLModel):
    name: str | None = None
    issuer: str | None = None
    issue_date: str | None = None
    expiration_date: str | None = None
    credential_id: str | None = None
    credential_url: str | None = None
    description: str | None = None
    display_order: int | None = None


class CVCertificationPublic(CVCertificationBase):
    id: uuid.UUID
    user_cv_id: uuid.UUID


# Language schemas
class CVLanguageBase(SQLModel):
    language: str = Field(max_length=100)
    proficiency: str = Field(max_length=50)
    certification_name: str | None = None
    certification_score: str | None = None
    display_order: int = 0


class CVLanguageCreate(CVLanguageBase):
    user_cv_id: uuid.UUID


class CVLanguageUpdate(SQLModel):
    language: str | None = None
    proficiency: str | None = None
    certification_name: str | None = None
    certification_score: str | None = None
    display_order: int | None = None


class CVLanguagePublic(CVLanguageBase):
    id: uuid.UUID
    user_cv_id: uuid.UUID


# Project schemas
class CVProjectBase(SQLModel):
    name: str = Field(max_length=255)
    description: str = Field(max_length=2000)
    start_date: str | None = None
    end_date: str | None = None
    project_url: str | None = None
    repository_url: str | None = None
    technologies: list[str] | None = None
    role: str | None = None
    company: str | None = None
    display_order: int = 0


class CVProjectCreate(CVProjectBase):
    user_cv_id: uuid.UUID


class CVProjectUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    project_url: str | None = None
    repository_url: str | None = None
    technologies: list[str] | None = None
    role: str | None = None
    company: str | None = None
    display_order: int | None = None


class CVProjectPublic(CVProjectBase):
    id: uuid.UUID
    user_cv_id: uuid.UUID


# UserCV Base schema - shared properties
class UserCVBase(SQLModel):
    professional_summary: str | None = Field(default=None, max_length=2000)
    linkedin_url: str | None = Field(default=None, max_length=500)
    github_url: str | None = Field(default=None, max_length=500)
    portfolio_url: str | None = Field(default=None, max_length=500)


# Create request
class UserCVCreate(UserCVBase):
    user_id: uuid.UUID


# Update request
class UserCVUpdate(UserCVBase):
    pass


# Public response with all relations
class UserCVPublic(UserCVBase):
    id: uuid.UUID
    user_id: uuid.UUID


# Full CV response with all related data
class UserCVFull(UserCVPublic):
    cv_files: list[CVFilePublic] = []
    education: list[CVEducationPublic] = []
    work_experience: list[CVWorkExperiencePublic] = []
    skills: list[CVSkillPublic] = []
    certifications: list[CVCertificationPublic] = []
    languages: list[CVLanguagePublic] = []
    projects: list[CVProjectPublic] = []


# List response
class UserCVsPublic(SQLModel):
    data: list[UserCVPublic]
    count: int
