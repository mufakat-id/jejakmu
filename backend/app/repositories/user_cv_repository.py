import uuid

from sqlmodel import Session, select

from app.models.user_cv import (
    CVCertification,
    CVEducation,
    CVFile,
    CVLanguage,
    CVProject,
    CVSkill,
    CVWorkExperience,
    UserCV,
)
from app.repositories.base import BaseRepository


class UserCVRepository(BaseRepository[UserCV]):
    """Repository for UserCV database operations"""

    def __init__(self, session: Session):
        super().__init__(UserCV, session)

    def get_by_user_id(self, user_id: uuid.UUID) -> UserCV | None:
        """Get CV by user ID with all relationships loaded"""
        statement = select(UserCV).where(UserCV.user_id == user_id)
        cv = self.session.exec(statement).first()
        if cv:
            # Eagerly load all relationships
            _ = cv.cv_files
            _ = cv.education
            _ = cv.work_experience
            _ = cv.skills
            _ = cv.certifications
            _ = cv.languages
            _ = cv.projects
        return cv

    def count(self) -> int:
        """Count total CVs"""
        statement = select(UserCV)
        return len(self.session.exec(statement).all())


class CVFileRepository(BaseRepository[CVFile]):
    """Repository for CVFile database operations"""

    def __init__(self, session: Session):
        super().__init__(CVFile, session)

    def get_by_cv_id(self, cv_id: uuid.UUID) -> list[CVFile]:
        """Get all CV files for a CV"""
        statement = (
            select(CVFile)
            .where(CVFile.user_cv_id == cv_id)
            .order_by(CVFile.version.desc())
        )
        return list(self.session.exec(statement).all())

    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> list[CVFile]:
        """Get all CV files by status with pagination"""
        statement = (
            select(CVFile)
            .where(CVFile.status == status)
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.exec(statement).all())

    def count_by_status(self, status: str) -> int:
        """Count CV files by status"""
        statement = select(CVFile).where(CVFile.status == status)
        return len(self.session.exec(statement).all())


class CVEducationRepository(BaseRepository[CVEducation]):
    """Repository for CVEducation database operations"""

    def __init__(self, session: Session):
        super().__init__(CVEducation, session)

    def get_by_cv_id(self, cv_id: uuid.UUID) -> list[CVEducation]:
        """Get all education entries for a CV"""
        statement = (
            select(CVEducation)
            .where(CVEducation.user_cv_id == cv_id)
            .order_by(CVEducation.display_order)
        )
        return list(self.session.exec(statement).all())


class CVWorkExperienceRepository(BaseRepository[CVWorkExperience]):
    """Repository for CVWorkExperience database operations"""

    def __init__(self, session: Session):
        super().__init__(CVWorkExperience, session)

    def get_by_cv_id(self, cv_id: uuid.UUID) -> list[CVWorkExperience]:
        """Get all work experience entries for a CV"""
        statement = (
            select(CVWorkExperience)
            .where(CVWorkExperience.user_cv_id == cv_id)
            .order_by(CVWorkExperience.display_order)
        )
        return list(self.session.exec(statement).all())


class CVSkillRepository(BaseRepository[CVSkill]):
    """Repository for CVSkill database operations"""

    def __init__(self, session: Session):
        super().__init__(CVSkill, session)

    def get_by_cv_id(self, cv_id: uuid.UUID) -> list[CVSkill]:
        """Get all skills for a CV"""
        statement = (
            select(CVSkill)
            .where(CVSkill.user_cv_id == cv_id)
            .order_by(CVSkill.display_order)
        )
        return list(self.session.exec(statement).all())


class CVCertificationRepository(BaseRepository[CVCertification]):
    """Repository for CVCertification database operations"""

    def __init__(self, session: Session):
        super().__init__(CVCertification, session)

    def get_by_cv_id(self, cv_id: uuid.UUID) -> list[CVCertification]:
        """Get all certifications for a CV"""
        statement = (
            select(CVCertification)
            .where(CVCertification.user_cv_id == cv_id)
            .order_by(CVCertification.display_order)
        )
        return list(self.session.exec(statement).all())


class CVLanguageRepository(BaseRepository[CVLanguage]):
    """Repository for CVLanguage database operations"""

    def __init__(self, session: Session):
        super().__init__(CVLanguage, session)

    def get_by_cv_id(self, cv_id: uuid.UUID) -> list[CVLanguage]:
        """Get all languages for a CV"""
        statement = (
            select(CVLanguage)
            .where(CVLanguage.user_cv_id == cv_id)
            .order_by(CVLanguage.display_order)
        )
        return list(self.session.exec(statement).all())


class CVProjectRepository(BaseRepository[CVProject]):
    """Repository for CVProject database operations"""

    def __init__(self, session: Session):
        super().__init__(CVProject, session)

    def get_by_cv_id(self, cv_id: uuid.UUID) -> list[CVProject]:
        """Get all projects for a CV"""
        statement = (
            select(CVProject)
            .where(CVProject.user_cv_id == cv_id)
            .order_by(CVProject.display_order)
        )
        return list(self.session.exec(statement).all())
