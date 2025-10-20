import logging
import subprocess
from datetime import datetime
from pathlib import Path

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def backup_database() -> str | None:
    """
    Backup PostgreSQL database to SQL file

    Returns:
        Path to backup file if successful, None otherwise
    """
    # Create backups directory if it doesn't exist
    backup_dir = Path(__file__).parent.parent / "backups"
    backup_dir.mkdir(exist_ok=True)

    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_{settings.POSTGRES_DB}_{timestamp}.sql"
    backup_path = backup_dir / backup_filename

    # Build pg_dump command
    pg_dump_command = [
        "pg_dump",
        "-h", settings.POSTGRES_SERVER,
        "-p", str(settings.POSTGRES_PORT),
        "-U", settings.POSTGRES_USER,
        "-d", settings.POSTGRES_DB,
        "-F", "p",  # Plain text format
        "-f", str(backup_path),
        "--no-owner",  # Skip restoration of object ownership
        "--no-acl",  # Skip restoration of access privileges
    ]

    try:
        logger.info(f"Starting database backup to {backup_path}")

        # Set PGPASSWORD environment variable for authentication
        env = {"PGPASSWORD": settings.POSTGRES_PASSWORD}

        # Execute pg_dump
        result = subprocess.run(
            pg_dump_command,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )

        logger.info(f"Database backup completed successfully: {backup_path}")
        logger.info(f"Backup file size: {backup_path.stat().st_size / 1024 / 1024:.2f} MB")

        return str(backup_path)

    except subprocess.CalledProcessError as e:
        logger.error(f"Database backup failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during backup: {e}")
        return None


def backup_database_compressed() -> str | None:
    """
    Backup PostgreSQL database to compressed custom format file
    This format is smaller and can be restored with pg_restore

    Returns:
        Path to backup file if successful, None otherwise
    """
    # Create backups directory if it doesn't exist
    backup_dir = Path(__file__).parent.parent / "backups"
    backup_dir.mkdir(exist_ok=True)

    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_{settings.POSTGRES_DB}_{timestamp}.dump"
    backup_path = backup_dir / backup_filename

    # Build pg_dump command with custom format
    pg_dump_command = [
        "pg_dump",
        "-h", settings.POSTGRES_SERVER,
        "-p", str(settings.POSTGRES_PORT),
        "-U", settings.POSTGRES_USER,
        "-d", settings.POSTGRES_DB,
        "-F", "c",  # Custom compressed format
        "-f", str(backup_path),
        "--no-owner",
        "--no-acl",
    ]

    try:
        logger.info(f"Starting compressed database backup to {backup_path}")

        # Set PGPASSWORD environment variable for authentication
        env = {"PGPASSWORD": settings.POSTGRES_PASSWORD}

        # Execute pg_dump
        result = subprocess.run(
            pg_dump_command,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )

        logger.info(f"Compressed database backup completed successfully: {backup_path}")
        logger.info(f"Backup file size: {backup_path.stat().st_size / 1024 / 1024:.2f} MB")

        return str(backup_path)

    except subprocess.CalledProcessError as e:
        logger.error(f"Database backup failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during backup: {e}")
        return None


def list_backups() -> list[Path]:
    """
    List all backup files in the backups directory

    Returns:
        List of backup file paths, sorted by modification time (newest first)
    """
    backup_dir = Path(__file__).parent.parent / "backups"

    if not backup_dir.exists():
        return []

    # Get all .sql and .dump files
    backups = list(backup_dir.glob("backup_*.sql")) + list(backup_dir.glob("backup_*.dump"))

    # Sort by modification time, newest first
    backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    return backups


def cleanup_old_backups(keep_count: int = 10) -> None:
    """
    Keep only the most recent backups and delete older ones

    Args:
        keep_count: Number of most recent backups to keep (default: 10)
    """
    backups = list_backups()

    if len(backups) <= keep_count:
        logger.info(f"Found {len(backups)} backups, no cleanup needed (keeping {keep_count})")
        return

    # Delete old backups
    backups_to_delete = backups[keep_count:]

    for backup in backups_to_delete:
        try:
            backup.unlink()
            logger.info(f"Deleted old backup: {backup.name}")
        except Exception as e:
            logger.error(f"Failed to delete backup {backup.name}: {e}")

    logger.info(f"Cleanup completed. Kept {keep_count} most recent backups.")


def main() -> None:
    """Main function to run database backup"""
    logger.info("=" * 60)
    logger.info("Database Backup Script")
    logger.info("=" * 60)
    logger.info(f"Database: {settings.POSTGRES_DB}")
    logger.info(f"Host: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}")
    logger.info(f"User: {settings.POSTGRES_USER}")
    logger.info("=" * 60)

    # Perform backup (choose one format)
    # Option 1: Plain SQL format (easy to read, larger file size)
    backup_path = backup_database()

    # Option 2: Compressed custom format (smaller file size, need pg_restore)
    # Uncomment the line below to use compressed format instead
    # backup_path = backup_database_compressed()

    if backup_path:
        logger.info("✓ Backup successful!")

        # Clean up old backups (keep only last 10)
        cleanup_old_backups(keep_count=10)

        # List all available backups
        backups = list_backups()
        logger.info(f"\nAvailable backups ({len(backups)}):")
        for i, backup in enumerate(backups[:5], 1):  # Show only last 5
            size_mb = backup.stat().st_size / 1024 / 1024
            modified = datetime.fromtimestamp(backup.stat().st_mtime)
            logger.info(f"  {i}. {backup.name} ({size_mb:.2f} MB) - {modified.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        logger.error("✗ Backup failed!")
        exit(1)


if __name__ == "__main__":
    main()

