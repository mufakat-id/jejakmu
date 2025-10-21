import logging

from sqlalchemy import Engine
from sqlmodel import Session, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.db import engine
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init(db_engine: Engine) -> None:
    try:
        with Session(db_engine) as session:
            # Try to create session to check if DB is awake
            session.exec(select(1))
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service")
    logger.info(f"Database server: {settings.POSTGRES_SERVER}")
    logger.info(f"Database port: {settings.POSTGRES_PORT}")
    logger.info(f"Database name: {settings.POSTGRES_DB}")
    logger.info(f"Database user: {settings.POSTGRES_USER}")
    logger.info(
        f"Connection URI (without password): postgresql+psycopg://{settings.POSTGRES_USER}:***@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    init(engine)
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
