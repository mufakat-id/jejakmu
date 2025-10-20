import logging
import uuid
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.v1.deps import CurrentUser, SessionDep
from app.core.storage import GoogleCloudStorage
from app.schemas.common import Message
from app.schemas.user_cv import (
    CVCertificationCreate,
    CVCertificationPublic,
    CVCertificationUpdate,
    CVEducationCreate,
    CVEducationPublic,
    CVEducationUpdate,
    CVFileCreate,
    CVFilePublic,
    CVFilesPublic,
    CVFileUpdate,
    CVLanguageCreate,
    CVLanguagePublic,
    CVLanguageUpdate,
    CVProjectCreate,
    CVProjectPublic,
    CVProjectUpdate,
    CVSkillCreate,
    CVSkillPublic,
    CVSkillUpdate,
    CVWorkExperienceCreate,
    CVWorkExperiencePublic,
    CVWorkExperienceUpdate,
    UserCVCreate,
    UserCVFull,
    UserCVPublic,
    UserCVsPublic,
    UserCVUpdate,
)
from app.services.user_cv_service import UserCVService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cv", tags=["cv"])


# =============================================================================
# CV Profile Endpoints
# =============================================================================


@router.get("/", response_model=UserCVsPublic)
def read_cvs(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve all CVs (superuser only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    service = UserCVService(session)
    cvs, count = service.get_cvs(skip=skip, limit=limit)
    return UserCVsPublic(data=cvs, count=count)


@router.get("/me", response_model=UserCVFull)
def read_my_cv(session: SessionDep, current_user: CurrentUser) -> Any:
    """Get current user's full CV with all related data."""
    service = UserCVService(session)
    cv = service.get_cv_by_user_id(current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    return cv


@router.get("/{id}", response_model=UserCVPublic)
def read_cv(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """Get CV by ID."""
    service = UserCVService(session)
    cv = service.get_cv(id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return cv


@router.post("/", response_model=UserCVPublic)
def create_cv(
    *, session: SessionDep, current_user: CurrentUser, cv_in: UserCVCreate
) -> Any:
    """Create new CV profile."""
    if cv_in.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    service = UserCVService(session)
    try:
        cv = service.create_cv(cv_in)
        return cv
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{id}", response_model=UserCVPublic)
def update_cv(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    cv_in: UserCVUpdate,
) -> Any:
    """Update CV profile."""
    service = UserCVService(session)
    cv = service.get_cv(id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated_cv = service.update_cv(id, cv_in)
    if not updated_cv:
        raise HTTPException(status_code=404, detail="CV not found")

    return updated_cv


@router.delete("/{id}", response_model=Message)
def delete_cv(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
) -> Any:
    """Delete CV profile."""
    service = UserCVService(session)
    cv = service.get_cv(id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    success = service.delete_cv(id)
    if not success:
        raise HTTPException(status_code=404, detail="CV not found")

    return Message(message="CV deleted successfully")


# =============================================================================
# Education Endpoints
# =============================================================================


@router.post("/education", response_model=CVEducationPublic, tags=["cv-education"])
def create_education(
    *, session: SessionDep, current_user: CurrentUser, education_in: CVEducationCreate
) -> Any:
    """Add education entry to CV."""
    service = UserCVService(session)
    cv = service.get_cv(education_in.user_cv_id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    education = service.create_education(education_in)
    return education


@router.get("/education", response_model=list[CVEducationPublic], tags=["cv-education"])
def read_my_education(session: SessionDep, current_user: CurrentUser) -> Any:
    """Get all education entries for current user's CV."""
    service = UserCVService(session)
    cv = service.get_cv_by_user_id(current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    return service.get_education_by_cv(cv.id)


@router.patch(
    "/education/{id}", response_model=CVEducationPublic, tags=["cv-education"]
)
def update_education(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    education_in: CVEducationUpdate,
) -> Any:
    """Update education entry."""
    service = UserCVService(session)
    education = service.get_education(id)
    if not education:
        raise HTTPException(status_code=404, detail="Education not found")

    cv = service.get_cv(education.user_cv_id)
    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated = service.update_education(id, education_in)
    return updated


@router.delete("/education/{id}", response_model=Message, tags=["cv-education"])
def delete_education(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
) -> Any:
    """Delete education entry."""
    service = UserCVService(session)
    education = service.get_education(id)
    if not education:
        raise HTTPException(status_code=404, detail="Education not found")

    cv = service.get_cv(education.user_cv_id)
    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    service.delete_education(id)
    return Message(message="Education deleted successfully")


# =============================================================================
# Work Experience Endpoints
# =============================================================================


@router.post(
    "/work-experience",
    response_model=CVWorkExperiencePublic,
    tags=["cv-work-experience"],
)
def create_work_experience(
    *, session: SessionDep, current_user: CurrentUser, work_in: CVWorkExperienceCreate
) -> Any:
    """Add work experience entry to CV."""
    service = UserCVService(session)
    cv = service.get_cv(work_in.user_cv_id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    work = service.create_work_experience(work_in)
    return work


@router.get(
    "/work-experience",
    response_model=list[CVWorkExperiencePublic],
    tags=["cv-work-experience"],
)
def read_my_work_experience(session: SessionDep, current_user: CurrentUser) -> Any:
    """Get all work experience entries for current user's CV."""
    service = UserCVService(session)
    cv = service.get_cv_by_user_id(current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    return service.get_work_experience_by_cv(cv.id)


@router.patch(
    "/work-experience/{id}",
    response_model=CVWorkExperiencePublic,
    tags=["cv-work-experience"],
)
def update_work_experience(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    work_in: CVWorkExperienceUpdate,
) -> Any:
    """Update work experience entry."""
    service = UserCVService(session)
    work = service.get_work_experience(id)
    if not work:
        raise HTTPException(status_code=404, detail="Work experience not found")

    cv = service.get_cv(work.user_cv_id)
    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated = service.update_work_experience(id, work_in)
    return updated


@router.delete(
    "/work-experience/{id}", response_model=Message, tags=["cv-work-experience"]
)
def delete_work_experience(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
) -> Any:
    """Delete work experience entry."""
    service = UserCVService(session)
    work = service.get_work_experience(id)
    if not work:
        raise HTTPException(status_code=404, detail="Work experience not found")

    cv = service.get_cv(work.user_cv_id)
    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    service.delete_work_experience(id)
    return Message(message="Work experience deleted successfully")


# =============================================================================
# Skills Endpoints
# =============================================================================


@router.post("/skills", response_model=CVSkillPublic, tags=["cv-skills"])
def create_skill(
    *, session: SessionDep, current_user: CurrentUser, skill_in: CVSkillCreate
) -> Any:
    """Add skill to CV."""
    service = UserCVService(session)
    cv = service.get_cv(skill_in.user_cv_id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    skill = service.create_skill(skill_in)
    return skill


@router.get("/skills", response_model=list[CVSkillPublic], tags=["cv-skills"])
def read_my_skills(session: SessionDep, current_user: CurrentUser) -> Any:
    """Get all skills for current user's CV."""
    service = UserCVService(session)
    cv = service.get_cv_by_user_id(current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    return service.get_skills_by_cv(cv.id)


@router.patch("/skills/{id}", response_model=CVSkillPublic, tags=["cv-skills"])
def update_skill(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    skill_in: CVSkillUpdate,
) -> Any:
    """Update skill entry."""
    service = UserCVService(session)
    skill = service.get_skill(id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    cv = service.get_cv(skill.user_cv_id)
    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated = service.update_skill(id, skill_in)
    return updated


@router.delete("/skills/{id}", response_model=Message, tags=["cv-skills"])
def delete_skill(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
) -> Any:
    """Delete skill entry."""
    service = UserCVService(session)
    skill = service.get_skill(id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    cv = service.get_cv(skill.user_cv_id)
    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    service.delete_skill(id)
    return Message(message="Skill deleted successfully")


# =============================================================================
# Certifications Endpoints
# =============================================================================


@router.post(
    "/certifications", response_model=CVCertificationPublic, tags=["cv-certifications"]
)
def create_certification(
    *, session: SessionDep, current_user: CurrentUser, cert_in: CVCertificationCreate
) -> Any:
    """Add certification to CV."""
    service = UserCVService(session)
    cv = service.get_cv(cert_in.user_cv_id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    cert = service.create_certification(cert_in)
    return cert


@router.get(
    "/certifications",
    response_model=list[CVCertificationPublic],
    tags=["cv-certifications"],
)
def read_my_certifications(session: SessionDep, current_user: CurrentUser) -> Any:
    """Get all certifications for current user's CV."""
    service = UserCVService(session)
    cv = service.get_cv_by_user_id(current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    return service.get_certifications_by_cv(cv.id)


@router.patch(
    "/certifications/{id}",
    response_model=CVCertificationPublic,
    tags=["cv-certifications"],
)
def update_certification(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    cert_in: CVCertificationUpdate,
) -> Any:
    """Update certification entry."""
    service = UserCVService(session)
    cert = service.get_certification(id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")

    cv = service.get_cv(cert.user_cv_id)
    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated = service.update_certification(id, cert_in)
    return updated


@router.delete(
    "/certifications/{id}", response_model=Message, tags=["cv-certifications"]
)
def delete_certification(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
) -> Any:
    """Delete certification entry."""
    service = UserCVService(session)
    cert = service.get_certification(id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")

    cv = service.get_cv(cert.user_cv_id)
    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    service.delete_certification(id)
    return Message(message="Certification deleted successfully")


# =============================================================================
# Languages Endpoints
# =============================================================================


@router.post("/languages", response_model=CVLanguagePublic, tags=["cv-languages"])
def create_language(
    *, session: SessionDep, current_user: CurrentUser, lang_in: CVLanguageCreate
) -> Any:
    """Add language to CV."""
    service = UserCVService(session)
    cv = service.get_cv(lang_in.user_cv_id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    lang = service.create_language(lang_in)
    return lang


@router.get("/languages", response_model=list[CVLanguagePublic], tags=["cv-languages"])
def read_my_languages(session: SessionDep, current_user: CurrentUser) -> Any:
    """Get all languages for current user's CV."""
    service = UserCVService(session)
    cv = service.get_cv_by_user_id(current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    return service.get_languages_by_cv(cv.id)


@router.patch("/languages/{id}", response_model=CVLanguagePublic, tags=["cv-languages"])
def update_language(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    lang_in: CVLanguageUpdate,
) -> Any:
    """Update language entry."""
    service = UserCVService(session)
    lang = service.get_language(id)
    if not lang:
        raise HTTPException(status_code=404, detail="Language not found")

    cv = service.get_cv(lang.user_cv_id)
    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated = service.update_language(id, lang_in)
    return updated


@router.delete("/languages/{id}", response_model=Message, tags=["cv-languages"])
def delete_language(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
) -> Any:
    """Delete language entry."""
    service = UserCVService(session)
    lang = service.get_language(id)
    if not lang:
        raise HTTPException(status_code=404, detail="Language not found")

    cv = service.get_cv(lang.user_cv_id)
    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    service.delete_language(id)
    return Message(message="Language deleted successfully")


# =============================================================================
# Projects Endpoints
# =============================================================================


@router.post("/projects", response_model=CVProjectPublic, tags=["cv-projects"])
def create_project(
    *, session: SessionDep, current_user: CurrentUser, project_in: CVProjectCreate
) -> Any:
    """Add project to CV."""
    service = UserCVService(session)
    cv = service.get_cv(project_in.user_cv_id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    project = service.create_project(project_in)
    return project


@router.get("/projects", response_model=list[CVProjectPublic], tags=["cv-projects"])
def read_my_projects(session: SessionDep, current_user: CurrentUser) -> Any:
    """Get all projects for current user's CV."""
    service = UserCVService(session)
    cv = service.get_cv_by_user_id(current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    return service.get_projects_by_cv(cv.id)


@router.patch("/projects/{id}", response_model=CVProjectPublic, tags=["cv-projects"])
def update_project(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    project_in: CVProjectUpdate,
) -> Any:
    """Update project entry."""
    service = UserCVService(session)
    project = service.get_project(id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    cv = service.get_cv(project.user_cv_id)
    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated = service.update_project(id, project_in)
    return updated


@router.delete("/projects/{id}", response_model=Message, tags=["cv-projects"])
def delete_project(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
) -> Any:
    """Delete project entry."""
    service = UserCVService(session)
    project = service.get_project(id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    cv = service.get_cv(project.user_cv_id)
    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    service.delete_project(id)
    return Message(message="Project deleted successfully")


# =============================================================================
# CV Files Endpoints
# =============================================================================


@router.get("/files/requested", response_model=CVFilesPublic, tags=["cv-files"])
def read_requested_cv_files(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all CV files with status 'requested' (admin/reviewer only).
    Returns list of CV files with their associated CV information.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    service = UserCVService(session)
    cv_files, count = service.get_cv_files_by_status(
        "requested", skip=skip, limit=limit
    )

    # Enrich CV files with CV info
    enriched_files = []
    for cv_file in cv_files:
        cv = service.get_cv(cv_file.user_cv_id)
        file_dict = cv_file.model_dump()
        file_dict["user_cv"] = cv
        enriched_files.append(file_dict)

    return CVFilesPublic(data=enriched_files, count=count)


@router.post("/files/upload", response_model=CVFilePublic, tags=["cv-files"])
async def upload_cv_file(
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(..., description="CV file (PDF, DOC, DOCX)"),
) -> Any:
    """Upload CV file for current user."""
    # Validate file type
    allowed_content_types = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]

    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF, DOC, and DOCX files are allowed.",
        )

    try:
        # Get or create CV
        service = UserCVService(session)
        cv = service.get_cv_by_user_id(current_user.id)
        if not cv:
            # Auto-create CV if doesn't exist
            from app.schemas.user_cv import UserCVCreate

            cv_in = UserCVCreate(user_id=current_user.id)
            cv = service.create_cv(cv_in)

        # Upload file to GCS
        gcs_service = GoogleCloudStorage()
        file_content = await file.read()

        file_extension = file.filename.split(".")[-1] if "." in file.filename else "pdf"
        unique_filename = f"cv/{current_user.id}/{uuid.uuid4()}.{file_extension}"

        url = gcs_service.upload_file_from_memory(
            file_content=file_content,
            destination_blob_name=unique_filename,
            content_type=file.content_type or "application/pdf",
        )

        signed_url = gcs_service.convert_public_url_to_signed_url(url)

        # Create CV file record
        cv_file_in = CVFileCreate(
            user_cv_id=cv.id,
            file_url=signed_url,
            file_name=file.filename,
            file_type=file.content_type,
            file_size=len(file_content),
        )

        cv_file = service.create_cv_file(cv_file_in)
        logger.info(f"Uploaded CV file for user {current_user.id}: {signed_url}")

        return cv_file

    except ValueError as e:
        logger.error(f"GCS configuration error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Storage configuration error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error uploading CV file: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to upload CV file: {str(e)}"
        )


@router.get("/files", response_model=list[CVFilePublic], tags=["cv-files"])
def read_my_cv_files(session: SessionDep, current_user: CurrentUser) -> Any:
    """Get all CV files for current user."""
    service = UserCVService(session)
    cv = service.get_cv_by_user_id(current_user.id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    return service.get_cv_files_by_cv(cv.id)


@router.patch("/files/{id}", response_model=CVFilePublic, tags=["cv-files"])
def update_cv_file(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    file_in: CVFileUpdate,
) -> Any:
    """Update CV file (status, review notes, etc)."""
    service = UserCVService(session)
    cv_file = service.get_cv_file(id)
    if not cv_file:
        raise HTTPException(status_code=404, detail="CV file not found")

    cv = service.get_cv(cv_file.user_cv_id)
    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated = service.update_cv_file(id, file_in)
    return updated


@router.delete("/files/{id}", response_model=Message, tags=["cv-files"])
def delete_cv_file(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
) -> Any:
    """Delete CV file."""
    service = UserCVService(session)
    cv_file = service.get_cv_file(id)
    if not cv_file:
        raise HTTPException(status_code=404, detail="CV file not found")

    cv = service.get_cv(cv_file.user_cv_id)
    if cv.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    service.delete_cv_file(id)
    return Message(message="CV file deleted successfully")
