"""
Initial sites data - creates default site on first run
"""
import logging

from sqlmodel import Session, select

from app.core.db import engine
from app.models.site import Site

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_sites() -> None:
    """Initialize default site if no sites exist."""
    with Session(engine) as session:
        # Check if any sites exist
        statement = select(Site)
        sites = session.exec(statement).all()

        if not sites:
            logger.info("Creating default site...")

            # Create default site for localhost
            default_site = Site(
                domain="localhost:8000",
                name="Development Site",
                frontend_domain="localhost:5173",
                is_active=True,
                is_default=True,
                settings={
                    "description": "Default development site",
                    "environment": "local",
                },
            )

            session.add(default_site)
            session.commit()
            session.refresh(default_site)

            logger.info(f"Created default site: {default_site.name}")
            logger.info(f"  Backend:  {default_site.domain}")
            logger.info(f"  Frontend: {default_site.frontend_domain}")
        else:
            logger.info(
                f"Sites already exist ({len(sites)} sites found), skipping initialization."
            )


def main() -> None:
    logger.info("Initializing sites")
    init_sites()
    logger.info("Sites initialized successfully")


if __name__ == "__main__":
    main()
