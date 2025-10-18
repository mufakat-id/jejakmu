import logging

from google.cloud import storage
from google.oauth2 import service_account

from app.core.config import settings

logger = logging.getLogger(__name__)


class GoogleCloudStorage:
    """Service for managing file uploads and retrieval from Google Cloud Storage."""

    def __init__(self):
        self.bucket_name = getattr(settings, "GCS_BUCKET_NAME", "default-bucket-name")

        # Initialize client with credentials if provided
        if settings.GOOGLE_APPLICATION_CREDENTIALS:
            credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_APPLICATION_CREDENTIALS
            )
            self.client = storage.Client(
                credentials=credentials, project=settings.GOOGLE_CLOUD_PROJECT
            )
        else:
            # Fall back to Application Default Credentials
            self.client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)

        self.bucket = self.client.bucket(self.bucket_name)

        # Note: We don't validate bucket existence here to avoid requiring
        # storage.buckets.get permission. The bucket will be validated
        # when the first operation is performed.

    def upload_file(self, file_path: str, destination_blob_name: str) -> str:
        """
        Upload a file to Google Cloud Storage.

        Args:
            file_path: Path to the local file to upload
            destination_blob_name: Name to give the file in GCS

        Returns:
            Signed URL of the uploaded file (valid for 7 days)
        """
        try:
            blob = self.bucket.blob(destination_blob_name)

            # Upload the file
            blob.upload_from_filename(file_path)

            # Make the blob publicly readable if needed
            # blob.make_public()

            # Return the public URL
            url = f"https://storage.googleapis.com/{self.bucket_name}/{destination_blob_name}"
            logger.info(f"File uploaded successfully to {url}")
            return url
        except Exception as e:
            logger.error(f"Error uploading file to GCS: {str(e)}")
            raise e

    def upload_file_from_memory(
        self,
        file_content: bytes,
        destination_blob_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Upload file content from memory to Google Cloud Storage.

        Args:
            file_content: File content as bytes
            destination_blob_name: Name to give the file in GCS
            content_type: MIME type of the content

        Returns:
            Public URL of the uploaded file
        """
        try:
            blob = self.bucket.blob(destination_blob_name)

            # Upload from memory
            blob.upload_from_string(file_content, content_type=content_type)

            # Generate a signed URL that's valid for 7 days
            # url = blob.generate_signed_url(
            #     version="v4",
            #     expiration=timedelta(days=7),
            #     method="GET",
            # )

            # Return the public URL
            url = f"https://storage.googleapis.com/{self.bucket_name}/{destination_blob_name}"

            logger.info(
                f"File uploaded from memory successfully to {destination_blob_name}"
            )
            return url
        except Exception as e:
            logger.error(f"Error uploading file from memory to GCS: {str(e)}")
            raise e

    def download_file(self, source_blob_name: str, destination_file_path: str) -> None:
        """
        Download a file from Google Cloud Storage.

        Args:
            source_blob_name: Name of the file in GCS
            destination_file_path: Local path to save the file
        """
        try:
            blob = self.bucket.blob(source_blob_name)
            blob.download_to_filename(destination_file_path)
            logger.info(
                f"File downloaded successfully from {source_blob_name} to {destination_file_path}"
            )
        except Exception as e:
            logger.error(f"Error downloading file from GCS: {str(e)}")
            raise e

    def get_file_url(
        self, blob_name: str, signed: bool = False, expiration_hours: int = 1
    ) -> str:
        """
        Generate a URL for a file in GCS.

        Args:
            blob_name: Name of the file in GCS
            signed: Whether to generate a signed URL for private files
            expiration_hours: Expiration time for signed URL (hours)

        Returns:
            URL to access the file
        """
        try:
            blob = self.bucket.blob(blob_name)

            if signed:
                # Generate a signed URL that expires
                from datetime import timedelta

                url = blob.generate_signed_url(
                    expiration=timedelta(hours=expiration_hours), method="GET"
                )
            else:
                # Generate public URL (requires the file to be publicly accessible)
                url = f"https://storage.googleapis.com/{self.bucket_name}/{blob_name}"

            return url
        except Exception as e:
            logger.error(f"Error generating file URL: {str(e)}")
            raise e

    def delete_file(self, blob_name: str) -> bool:
        """Delete a file from GCS."""
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            logger.info(f"File deleted: {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise

    def convert_public_url_to_signed_url(
        self, gcs_url: str, expiration_days: int = 1
    ) -> str:
        """
        Convert a public GCS URL to a signed URL.

        Args:
            gcs_url: Public GCS URL (e.g., https://storage.googleapis.com/bucket/path/file.jpg)
            expiration_days: Number of days until the signed URL expires (default: 7)

        Returns:
            Signed URL that can be accessed without authentication

        Example:
            >>> gcs = GoogleCloudStorage()
            >>> public_url = "https://storage.googleapis.com/asid-storage-dev/uploads/file.jpg"
            >>> signed_url = gcs.convert_public_url_to_signed_url(public_url)
        """
        try:
            # Extract blob name from URL
            # URL format: https://storage.googleapis.com/bucket-name/path/to/file.ext
            if "storage.googleapis.com" not in gcs_url:
                raise ValueError("Invalid GCS URL format")

            # Remove the base URL to get bucket and blob path
            url_parts = gcs_url.replace("https://storage.googleapis.com/", "").split(
                "/", 1
            )

            if len(url_parts) != 2:
                raise ValueError(
                    "Invalid GCS URL format. Expected: https://storage.googleapis.com/bucket/path"
                )

            bucket_name, blob_name = url_parts

            # Verify this is the correct bucket
            if bucket_name != self.bucket_name:
                logger.warning(
                    f"URL bucket '{bucket_name}' doesn't match configured bucket '{self.bucket_name}'"
                )

            # Get the blob
            blob = self.bucket.blob(blob_name)

            # Generate signed URL
            from datetime import timedelta

            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=expiration_days),
                method="GET",
            )

            logger.info(f"Generated signed URL for {blob_name}")
            return signed_url

        except Exception as e:
            logger.error(f"Error converting URL to signed URL: {str(e)}")
            raise e

    @staticmethod
    def extract_blob_name_from_url(gcs_url: str) -> str:
        """
        Extract blob name (file path) from a GCS URL.

        Args:
            gcs_url: GCS URL (public or signed)

        Returns:
            Blob name (path to file in bucket)

        Example:
            >>> url = "https://storage.googleapis.com/asid-storage-dev/uploads/file.jpg"
            >>> blob_name = GoogleCloudStorage.extract_blob_name_from_url(url)
            >>> print(blob_name)  # "uploads/file.jpg"
        """
        # Handle both public and signed URLs
        if "storage.googleapis.com" not in gcs_url:
            raise ValueError("Invalid GCS URL format")

        # Remove base URL and parameters
        base_url = gcs_url.split("?")[0]  # Remove query parameters if signed URL
        url_parts = base_url.replace("https://storage.googleapis.com/", "").split(
            "/", 1
        )

        if len(url_parts) != 2:
            raise ValueError("Invalid GCS URL format")

        _, blob_name = url_parts
        return blob_name


# Example usage in a transcription service:
def store_transcription_result_in_gcs(
    _self, transcription_id: str, result_data: dict
) -> str:
    """
    Store transcription result as JSON in Google Cloud Storage.

    Args:
        transcription_id: Unique ID for the transcription
        result_data: Transcription result data to store

    Returns:
        Public URL to the stored transcription
    """
    gcs_service = GoogleCloudStorage()

    # Convert result data to JSON string
    import json

    json_content = json.dumps(
        result_data, indent=2, default=str
    )  # default=str handles datetime objects

    # Create destination name
    destination_name = f"transcriptions/{transcription_id}.json"

    # Upload to GCS
    url = gcs_service.upload_file_from_memory(
        file_content=json_content.encode("utf-8"),
        destination_blob_name=destination_name,
        content_type="application/json",
    )

    return url
