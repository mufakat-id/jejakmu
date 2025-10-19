import uuid
from sqlmodel import Session

from app.repositories.user_cv_repository import (
    UserCVRepository,
    CVFileRepository,
    CVEducationRepository,
    CVWorkExperienceRepository,
    CVSkillRepository,
    CVCertificationRepository,
    CVLanguageRepository,
    CVProjectRepository,
)
from app.schemas.user_cv import (
    UserCVCreate,
    UserCVUpdate,
    CVFileCreate,
    CVFileUpdate,
    CVEducationCreate,
    CVEducationUpdate,
    CVWorkExperienceCreate,
    CVWorkExperienceUpdate,
    CVSkillCreate,
    CVSkillUpdate,
    CVCertificationCreate,
    CVCertificationUpdate,
    CVLanguageCreate,
    CVLanguageUpdate,
    CVProjectCreate,
    CVProjectUpdate,
)


class UserCVService:
    """Service for CV business logic - uses repositories for data access"""

    def __init__(self, session: Session):
        self.cv_repo = UserCVRepository(session)
        self.file_repo = CVFileRepository(session)
        self.education_repo = CVEducationRepository(session)
        self.work_repo = CVWorkExperienceRepository(session)
        self.skill_repo = CVSkillRepository(session)
        self.cert_repo = CVCertificationRepository(session)
        self.lang_repo = CVLanguageRepository(session)
        self.project_repo = CVProjectRepository(session)

    # =============================================================================
    # UserCV Business Logic
    # =============================================================================

    def get_cv(self, cv_id: uuid.UUID):
        """Get CV by ID"""
        return self.cv_repo.get(cv_id)

    def get_cv_by_user_id(self, user_id: uuid.UUID):
        """Get CV by user ID"""
        return self.cv_repo.get_by_user_id(user_id)

    def get_cvs(self, skip: int = 0, limit: int = 100):
        """Get all CVs with pagination"""
        cvs = self.cv_repo.get_all(skip=skip, limit=limit)
        count = self.cv_repo.count()
        return cvs, count

    def create_cv(self, cv_in: UserCVCreate):
        """Create new CV - validates user doesn't already have one"""
        existing_cv = self.cv_repo.get_by_user_id(cv_in.user_id)
        if existing_cv:
            raise ValueError(f"CV already exists for user {cv_in.user_id}")

        cv_data = cv_in.model_dump()
        return self.cv_repo.create(cv_data)

    def update_cv(self, cv_id: uuid.UUID, cv_in: UserCVUpdate):
        """Update CV"""
        cv = self.cv_repo.get(cv_id)
        if not cv:
            return None

        update_data = cv_in.model_dump(exclude_unset=True)
        return self.cv_repo.update(cv, update_data)

    def delete_cv(self, cv_id: uuid.UUID) -> bool:
        """Delete CV"""
        return self.cv_repo.delete(cv_id)

    # =============================================================================
    # CV File Business Logic
    # =============================================================================

    def get_cv_file(self, file_id: uuid.UUID):
        """Get CV file by ID"""
        return self.file_repo.get(file_id)

    def get_cv_files_by_cv(self, cv_id: uuid.UUID):
        """Get all CV files for a CV"""
        return self.file_repo.get_by_cv_id(cv_id)

    def create_cv_file(self, file_in: CVFileCreate):
        """Create CV file record"""
        file_data = file_in.model_dump()
        return self.file_repo.create(file_data)

    def update_cv_file(self, file_id: uuid.UUID, file_in: CVFileUpdate):
        """Update CV file"""
        cv_file = self.file_repo.get(file_id)
        if not cv_file:
            return None

        update_data = file_in.model_dump(exclude_unset=True)
        return self.file_repo.update(cv_file, update_data)

    def delete_cv_file(self, file_id: uuid.UUID) -> bool:
        """Delete CV file"""
        return self.file_repo.delete(file_id)

    # =============================================================================
    # Education Business Logic
    # =============================================================================

    def get_education(self, education_id: uuid.UUID):
        """Get education by ID"""
        return self.education_repo.get(education_id)

    def get_education_by_cv(self, cv_id: uuid.UUID):
        """Get all education entries for a CV"""
        return self.education_repo.get_by_cv_id(cv_id)

    def create_education(self, education_in: CVEducationCreate):
        """Create education entry"""
        education_data = education_in.model_dump()
        return self.education_repo.create(education_data)

    def update_education(self, education_id: uuid.UUID, education_in: CVEducationUpdate):
        """Update education entry"""
        education = self.education_repo.get(education_id)
        if not education:
            return None

        update_data = education_in.model_dump(exclude_unset=True)
        return self.education_repo.update(education, update_data)

    def delete_education(self, education_id: uuid.UUID) -> bool:
        """Delete education entry"""
        return self.education_repo.delete(education_id)

    # =============================================================================
    # Work Experience Business Logic
    # =============================================================================

    def get_work_experience(self, work_id: uuid.UUID):
        """Get work experience by ID"""
        return self.work_repo.get(work_id)

    def get_work_experience_by_cv(self, cv_id: uuid.UUID):
        """Get all work experience entries for a CV"""
        return self.work_repo.get_by_cv_id(cv_id)

    def create_work_experience(self, work_in: CVWorkExperienceCreate):
        """Create work experience entry"""
        work_data = work_in.model_dump()
        return self.work_repo.create(work_data)

    def update_work_experience(self, work_id: uuid.UUID, work_in: CVWorkExperienceUpdate):
        """Update work experience entry"""
        work = self.work_repo.get(work_id)
        if not work:
            return None

        update_data = work_in.model_dump(exclude_unset=True)
        return self.work_repo.update(work, update_data)

    def delete_work_experience(self, work_id: uuid.UUID) -> bool:
        """Delete work experience entry"""
        return self.work_repo.delete(work_id)

    # =============================================================================
    # Skill Business Logic
    # =============================================================================

    def get_skill(self, skill_id: uuid.UUID):
        """Get skill by ID"""
        return self.skill_repo.get(skill_id)

    def get_skills_by_cv(self, cv_id: uuid.UUID):
        """Get all skills for a CV"""
        return self.skill_repo.get_by_cv_id(cv_id)

    def create_skill(self, skill_in: CVSkillCreate):
        """Create skill entry"""
        skill_data = skill_in.model_dump()
        return self.skill_repo.create(skill_data)

    def update_skill(self, skill_id: uuid.UUID, skill_in: CVSkillUpdate):
        """Update skill entry"""
        skill = self.skill_repo.get(skill_id)
        if not skill:
            return None

        update_data = skill_in.model_dump(exclude_unset=True)
        return self.skill_repo.update(skill, update_data)

    def delete_skill(self, skill_id: uuid.UUID) -> bool:
        """Delete skill entry"""
        return self.skill_repo.delete(skill_id)

    # =============================================================================
    # Certification Business Logic
    # =============================================================================

    def get_certification(self, cert_id: uuid.UUID):
        """Get certification by ID"""
        return self.cert_repo.get(cert_id)

    def get_certifications_by_cv(self, cv_id: uuid.UUID):
        """Get all certifications for a CV"""
        return self.cert_repo.get_by_cv_id(cv_id)

    def create_certification(self, cert_in: CVCertificationCreate):
        """Create certification entry"""
        cert_data = cert_in.model_dump()
        return self.cert_repo.create(cert_data)

    def update_certification(self, cert_id: uuid.UUID, cert_in: CVCertificationUpdate):
        """Update certification entry"""
        cert = self.cert_repo.get(cert_id)
        if not cert:
            return None

        update_data = cert_in.model_dump(exclude_unset=True)
        return self.cert_repo.update(cert, update_data)

    def delete_certification(self, cert_id: uuid.UUID) -> bool:
        """Delete certification entry"""
        return self.cert_repo.delete(cert_id)

    # =============================================================================
    # Language Business Logic
    # =============================================================================

    def get_language(self, lang_id: uuid.UUID):
        """Get language by ID"""
        return self.lang_repo.get(lang_id)

    def get_languages_by_cv(self, cv_id: uuid.UUID):
        """Get all languages for a CV"""
        return self.lang_repo.get_by_cv_id(cv_id)

    def create_language(self, lang_in: CVLanguageCreate):
        """Create language entry"""
        lang_data = lang_in.model_dump()
        return self.lang_repo.create(lang_data)

    def update_language(self, lang_id: uuid.UUID, lang_in: CVLanguageUpdate):
        """Update language entry"""
        lang = self.lang_repo.get(lang_id)
        if not lang:
            return None

        update_data = lang_in.model_dump(exclude_unset=True)
        return self.lang_repo.update(lang, update_data)

    def delete_language(self, lang_id: uuid.UUID) -> bool:
        """Delete language entry"""
        return self.lang_repo.delete(lang_id)

    # =============================================================================
    # Project Business Logic
    # =============================================================================

    def get_project(self, project_id: uuid.UUID):
        """Get project by ID"""
        return self.project_repo.get(project_id)

    def get_projects_by_cv(self, cv_id: uuid.UUID):
        """Get all projects for a CV"""
        return self.project_repo.get_by_cv_id(cv_id)

    def create_project(self, project_in: CVProjectCreate):
        """Create project entry"""
        project_data = project_in.model_dump()
        return self.project_repo.create(project_data)

    def update_project(self, project_id: uuid.UUID, project_in: CVProjectUpdate):
        """Update project entry"""
        project = self.project_repo.get(project_id)
        if not project:
            return None

        update_data = project_in.model_dump(exclude_unset=True)
        return self.project_repo.update(project, update_data)

    def delete_project(self, project_id: uuid.UUID) -> bool:
        """Delete project entry"""
        return self.project_repo.delete(project_id)
