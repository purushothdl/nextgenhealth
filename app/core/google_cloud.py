import mimetypes
from google.cloud import storage
from google.oauth2 import service_account
from app.core.config import settings
import os
import uuid

# Initialize GCS client
def initialize_gcs_client():
    credentials = service_account.Credentials.from_service_account_file(settings.GOOGLE_CLOUD_CREDENTIALS_PATH)
    client = storage.Client(credentials=credentials)
    return client

# Upload file to GCS
async def upload_ticket_to_gcs(bucket_name: str, file, ticket_id: str, file_type: str):
    client = initialize_gcs_client()
    bucket = client.bucket(bucket_name)

    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # Generate file path
    file_path = f"tickets/{ticket_id}/{file_type}/{unique_filename}"

    # Detect content type using the provided content type or by guessing from the filename
    content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

    # Upload file with correct MIME type
    blob = bucket.blob(file_path)
    blob.upload_from_file(file.file, content_type=content_type)

    # Make the file publicly accessible
    blob.make_public()

    # Return the public URL
    return blob.public_url

async def upload_report_file_to_gcs(bucket_name: str, file, ticket_id: str, file_type: str):
    """
    Upload a report file (image or document) to Google Cloud Storage.
    """
    client = initialize_gcs_client()
    bucket = client.bucket(bucket_name)

    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # Generate file path
    file_path = f"tickets/{ticket_id}/reports/{unique_filename}"

    # Detect content type using the provided content type or by guessing from the filename
    content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

    # Upload file with correct MIME type
    blob = bucket.blob(file_path)
    blob.upload_from_file(file.file, content_type=content_type)

    # Make the file publicly accessible
    blob.make_public()

    # Return the public URL
    return blob.public_url

def download_file_from_gcs(url: str) -> bytes:
    """
    Download a file from Google Cloud Storage.
    """
    client = storage.Client()
    bucket_name, blob_name = url.replace("https://storage.googleapis.com/", "").split("/", 1)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.download_as_bytes()