import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from app.core.audit import AuditMixin

if TYPE_CHECKING:
    from app.models.user import User


# =============================================================================
# CV File Model - Multiple CV files with status tracking and reviewer
# =============================================================================


class CVFile(SQLModel, AuditMixin, table=True):
    """
    CV File model to store uploaded CV documents.
    Each user can have multiple CV files with different statuses.
    """

    __tablename__ = "cv_file"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_cv_id: uuid.UUID = Field(foreign_key="user_cv.id", index=True)

    # File information
    file_url: str = Field(max_length=500, description="URL to uploaded CV file")
    file_name: str = Field(max_length=255, description="Original file name")
    file_type: str = Field(max_length=50, description="File MIME type")
    file_size: int | None = Field(default=None, description="File size in bytes")

    # Status tracking
    status: str = Field(
        default="submitted",
        max_length=50,
        description="Status: submitted, requested, reviewed, rejected",
    )

    # Review information
    reviewed_by_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", description="User who reviewed this CV"
    )
    reviewed_at: datetime | None = Field(
        default=None, description="Timestamp when CV was reviewed"
    )
    review_notes: str | None = Field(
        default=None, max_length=1000, description="Review notes or feedback"
    )

    # Additional metadata
    is_primary: bool = Field(default=False, description="Mark as primary/default CV")
    version: int = Field(default=1, description="CV version number")

    # Relationships
    user_cv: "UserCV" = Relationship(back_populates="cv_files")
    reviewed_by: "User" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "CVFile.reviewed_by_id==User.id",
            "lazy": "joined",
        }
    )


# =============================================================================
# Education Model - Education history
# =============================================================================


class CVEducation(SQLModel, AuditMixin, table=True):
    """
    Education history for CV.
    Each CV can have multiple education entries.
    """

    __tablename__ = "cv_education"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_cv_id: uuid.UUID = Field(foreign_key="user_cv.id", index=True)

    institution: str = Field(
        max_length=255, description="Name of educational institution"
    )
    degree: str = Field(
        max_length=100, description="Degree obtained (e.g., Bachelor, Master, PhD)"
    )
    field_of_study: str = Field(max_length=255, description="Field of study or major")

    start_date: str = Field(max_length=7, description="Start date in YYYY-MM format")
    end_date: str | None = Field(
        default=None,
        max_length=7,
        description="End date in YYYY-MM format or 'Present'",
    )

    gpa: str | None = Field(default=None, max_length=10, description="GPA or grade")
    description: str | None = Field(
        default=None, max_length=1000, description="Additional description"
    )

    # Location
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)

    # Display order
    display_order: int = Field(default=0, description="Order for displaying in CV")

    # Relationships
    user_cv: "UserCV" = Relationship(back_populates="education")


# =============================================================================
# Work Experience Model - Work history
# =============================================================================


class CVWorkExperience(SQLModel, AuditMixin, table=True):
    """
    Work experience history for CV.
    Each CV can have multiple work experience entries.
    """

    __tablename__ = "cv_work_experience"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_cv_id: uuid.UUID = Field(foreign_key="user_cv.id", index=True)

    company: str = Field(max_length=255, description="Company name")
    position: str = Field(max_length=255, description="Job position/title")

    start_date: str = Field(max_length=7, description="Start date in YYYY-MM format")
    end_date: str | None = Field(
        default=None,
        max_length=7,
        description="End date in YYYY-MM format or 'Present'",
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Job responsibilities and achievements",
    )

    # Employment details
    employment_type: str | None = Field(
        default=None,
        max_length=50,
        description="Employment type: Full-time, Part-time, Contract, Internship, Freelance",
    )

    # Location
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    is_remote: bool = Field(default=False, description="Remote work position")

    # Display order
    display_order: int = Field(default=0, description="Order for displaying in CV")

    # Relationships
    user_cv: "UserCV" = Relationship(back_populates="work_experience")


# =============================================================================
# Skill Model - Skills and expertise
# =============================================================================


class CVSkill(SQLModel, AuditMixin, table=True):
    """
    Skills for CV.
    Each CV can have multiple skills.
    """

    __tablename__ = "cv_skill"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_cv_id: uuid.UUID = Field(foreign_key="user_cv.id", index=True)

    name: str = Field(max_length=100, description="Skill name")
    level: str | None = Field(
        default=None,
        max_length=50,
        description="Proficiency level: Beginner, Intermediate, Advanced, Expert",
    )
    category: str | None = Field(
        default=None,
        max_length=100,
        description="Skill category: Technical, Soft Skills, Language, etc.",
    )

    years_of_experience: int | None = Field(
        default=None, description="Years of experience with this skill"
    )

    # Display order
    display_order: int = Field(default=0, description="Order for displaying in CV")

    # Relationships
    user_cv: "UserCV" = Relationship(back_populates="skills")


# =============================================================================
# Certification Model - Certifications and licenses
# =============================================================================


class CVCertification(SQLModel, AuditMixin, table=True):
    """
    Certifications and licenses for CV.
    Each CV can have multiple certifications.
    """

    __tablename__ = "cv_certification"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_cv_id: uuid.UUID = Field(foreign_key="user_cv.id", index=True)

    name: str = Field(max_length=255, description="Certification name")
    issuer: str = Field(max_length=255, description="Issuing organization")

    issue_date: str = Field(max_length=7, description="Issue date in YYYY-MM format")
    expiration_date: str | None = Field(
        default=None, max_length=7, description="Expiration date in YYYY-MM format"
    )

    credential_id: str | None = Field(
        default=None, max_length=255, description="Credential ID or license number"
    )
    credential_url: str | None = Field(
        default=None, max_length=500, description="URL to verify credential"
    )

    description: str | None = Field(
        default=None, max_length=1000, description="Additional description"
    )

    # Display order
    display_order: int = Field(default=0, description="Order for displaying in CV")

    # Relationships
    user_cv: "UserCV" = Relationship(back_populates="certifications")


# =============================================================================
# Language Model - Language proficiency
# =============================================================================


class CVLanguage(SQLModel, AuditMixin, table=True):
    """
    Language proficiency for CV.
    Each CV can have multiple languages.
    """

    __tablename__ = "cv_language"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_cv_id: uuid.UUID = Field(foreign_key="user_cv.id", index=True)

    language: str = Field(max_length=100, description="Language name")
    proficiency: str = Field(
        max_length=50,
        description="Proficiency level: Native, Fluent, Professional, Intermediate, Beginner",
    )

    # Optional: certification details
    certification_name: str | None = Field(
        default=None,
        max_length=255,
        description="Language certification name (e.g., TOEFL, IELTS)",
    )
    certification_score: str | None = Field(
        default=None, max_length=50, description="Certification score"
    )

    # Display order
    display_order: int = Field(default=0, description="Order for displaying in CV")

    # Relationships
    user_cv: "UserCV" = Relationship(back_populates="languages")


# =============================================================================
# Project Model - Projects and portfolio
# =============================================================================


class CVProject(SQLModel, AuditMixin, table=True):
    """
    Projects and portfolio for CV.
    Each CV can have multiple projects.
    """

    __tablename__ = "cv_project"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_cv_id: uuid.UUID = Field(foreign_key="user_cv.id", index=True)

    name: str = Field(max_length=255, description="Project name")
    description: str = Field(max_length=2000, description="Project description")

    start_date: str | None = Field(
        default=None, max_length=7, description="Start date in YYYY-MM format"
    )
    end_date: str | None = Field(
        default=None,
        max_length=7,
        description="End date in YYYY-MM format or 'Present'",
    )

    project_url: str | None = Field(
        default=None, max_length=500, description="Project URL or demo link"
    )
    repository_url: str | None = Field(
        default=None, max_length=500, description="Code repository URL"
    )

    # Technologies used - stored as JSON array
    technologies: list[str] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Technologies/tools used in the project",
    )

    role: str | None = Field(
        default=None, max_length=100, description="Your role in the project"
    )
    company: str | None = Field(
        default=None, max_length=255, description="Company/organization (if applicable)"
    )

    # Display order
    display_order: int = Field(default=0, description="Order for displaying in CV")

    # Relationships
    user_cv: "UserCV" = Relationship(back_populates="projects")


# =============================================================================
# Main UserCV Model - CV Profile
# =============================================================================


class UserCV(SQLModel, AuditMixin, table=True):
    """
    User CV (Curriculum Vitae) model with detailed professional information.
    Each user can have one CV profile that links to multiple related records.
    """

    __tablename__ = "user_cv"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", unique=True, index=True)

    # Professional Summary
    professional_summary: str | None = Field(
        default=None, max_length=2000, description="Professional summary/objective"
    )

    # Social Links
    linkedin_url: str | None = Field(
        default=None, max_length=500, description="LinkedIn profile URL"
    )
    github_url: str | None = Field(
        default=None, max_length=500, description="GitHub profile URL"
    )
    portfolio_url: str | None = Field(
        default=None, max_length=500, description="Portfolio website URL"
    )

    # Relationships
    user: "User" = Relationship(back_populates="cv")
    cv_files: list["CVFile"] = Relationship(
        back_populates="user_cv", cascade_delete=True
    )
    education: list["CVEducation"] = Relationship(
        back_populates="user_cv", cascade_delete=True
    )
    work_experience: list["CVWorkExperience"] = Relationship(
        back_populates="user_cv", cascade_delete=True
    )
    skills: list["CVSkill"] = Relationship(
        back_populates="user_cv", cascade_delete=True
    )
    certifications: list["CVCertification"] = Relationship(
        back_populates="user_cv", cascade_delete=True
    )
    languages: list["CVLanguage"] = Relationship(
        back_populates="user_cv", cascade_delete=True
    )
    projects: list["CVProject"] = Relationship(
        back_populates="user_cv", cascade_delete=True
    )
