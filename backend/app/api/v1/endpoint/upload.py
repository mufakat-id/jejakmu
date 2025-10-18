import logging
import uuid

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import RedirectResponse

from app.core.storage import GoogleCloudStorage
from app.schemas import BaseResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])
file_router = APIRouter(prefix="/file", tags=["file"])


@router.post("/", response_model=BaseResponse[list[str]], status_code=201)
async def upload_files(
    files: list[UploadFile] = File(..., description="Multiple files to upload"),
) -> BaseResponse[list[str]]:
    """
    Upload multiple files to Google Cloud Storage.

    **Parameters:**
    - files: List of files to upload

    **Returns:**
    - List of URLs for the uploaded files

    **Example Response:**
    ```json
    {
        "code": 201,
        "message": "Files uploaded successfully",
        "data": [
            "https://storage.googleapis.com/bucket-name/file1.pdf",
            "https://storage.googleapis.com/bucket-name/file2.jpg"
        ]
    }
    ```
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    try:
        gcs_service = GoogleCloudStorage()
        uploaded_urls = []

        for file in files:
            # Generate unique filename
            file_extension = (
                file.filename.split(".")[-1] if "." in file.filename else ""
            )
            unique_filename = (
                f"{uuid.uuid4()}.{file_extension}"
                if file_extension
                else str(uuid.uuid4())
            )

            # Read file content
            file_content = await file.read()

            # Determine content type
            content_type = file.content_type or "application/octet-stream"

            # Upload to GCS
            destination_blob_name = f"uploads/{unique_filename}"
            url = gcs_service.upload_file_from_memory(
                file_content=file_content,
                destination_blob_name=destination_blob_name,
                content_type=content_type,
            )

            uploaded_urls.append(gcs_service.convert_public_url_to_signed_url(url))
            logger.info(f"Uploaded file: {file.filename} -> {url}")
            logger.info(
                f"Signed URL: {file.filename} -> {gcs_service.convert_public_url_to_signed_url(url)}"
            )

        return BaseResponse(
            code=201,
            message=f"{len(uploaded_urls)} file(s) uploaded successfully",
            data=uploaded_urls,
        )

    except ValueError as e:
        # Handle GCS bucket validation errors
        logger.error(f"GCS configuration error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Storage configuration error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error uploading files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload files: {str(e)}")


@file_router.get("/signed-url/", status_code=307)
async def get_signed_url(
    url: str = Query(..., description="Public GCS URL to convert to signed URL"),
    expiration_days: int = Query(
        1, ge=1, le=365, description="Number of days until the signed URL expires"
    ),
) -> RedirectResponse:
    """
    Convert a public GCS URL to a signed URL and redirect to it.

    **Parameters:**
    - url: Public GCS URL (e.g., https://storage.googleapis.com/bucket/path/file.jpg)
    - expiration_days: Number of days until the signed URL expires (default: 7, max: 365)

    **Returns:**
    - Redirects to the signed URL that can be accessed without authentication
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")

    try:
        gcs_service = GoogleCloudStorage()
        signed_url = gcs_service.convert_public_url_to_signed_url(
            gcs_url=url, expiration_days=expiration_days
        )

        logger.info(f"Generated signed URL for: {url}")

        return RedirectResponse(url=signed_url, status_code=307)

    except ValueError as e:
        logger.error(f"Invalid URL format: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid URL: {str(e)}")
    except Exception as e:
        logger.error(f"Error generating signed URL: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate signed URL: {str(e)}"
        )
