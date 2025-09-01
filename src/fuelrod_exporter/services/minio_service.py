import os
import mimetypes
import json
from io import BytesIO
from typing import Optional

from minio import Minio, S3Error

from fuelrod_exporter.config import Config
from fuelrod_exporter.core.logging import SharedLogger


class MinioFileUploader:
    """Minimal service for uploading files to MinIO (bucket is public-read)."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self.logger = SharedLogger().get_logger()
        self.client: Optional[Minio] = None
        self._initialized = True

    def connect(self) -> Minio:
        """Connect to MinIO, ensure bucket exists, and set public-read policy."""
        if self.client:
            return self.client

        self.logger.info(f"Connecting to MinIO at {Config.MINIO_ENDPOINT} ...")
        self.client = Minio(
            Config.MINIO_ENDPOINT,
            access_key=Config.MINIO_ACCESS_KEY,
            secret_key=Config.MINIO_SECRET_KEY,
            secure=Config.MINIO_SECURE,
        )

        try:
            if not self.client.bucket_exists(Config.MINIO_BUCKET):
                self.client.make_bucket(Config.MINIO_BUCKET)
                self.logger.info(f"Created bucket '{Config.MINIO_BUCKET}'")
                self._set_public_read_policy()
            else:
                self.logger.debug(f"Using existing bucket '{Config.MINIO_BUCKET}'")
        except S3Error as e:
            self.logger.error(f"Bucket setup failed: {e}")
            raise

        return self.client

    def _set_public_read_policy(self) -> None:
        """Apply a public-read bucket policy."""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetBucketLocation"],
                    "Resource": f"arn:aws:s3:::{Config.MINIO_BUCKET}"
                },
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetObject"],
                    "Resource": f"arn:aws:s3:::{Config.MINIO_BUCKET}/*"
                },
            ],
        }

        try:
            self.client.set_bucket_policy(Config.MINIO_BUCKET, json.dumps(policy))
            self.logger.info(f"Set bucket '{Config.MINIO_BUCKET}' to public-read")
        except S3Error as e:
            self.logger.error(f"Failed to set public-read policy: {e}")
            raise

    def upload_file(self, local_path: str, object_name: Optional[str] = None) -> str:
        """Upload a local file to MinIO and return its public URL."""
        client = self.connect()
        object_name = object_name or os.path.basename(local_path)

        content_type, _ = mimetypes.guess_type(local_path)
        content_type = content_type or "application/octet-stream"

        try:
            client.fput_object(
                Config.MINIO_BUCKET,
                object_name,
                local_path,
                content_type=content_type,
            )
            self.logger.info(f"Uploaded '{local_path}' → '{object_name}' ({content_type})")
            return self.get_public_url(object_name)
        except S3Error as e:
            self.logger.error(f"Upload failed for '{local_path}': {e}")
            raise

    def upload_data(self, data: bytes, object_name: str, content_type: Optional[str] = None) -> str:
        """Upload raw bytes as an object to MinIO and return its public URL."""
        client = self.connect()

        if not content_type:
            content_type, _ = mimetypes.guess_type(object_name)
            content_type = content_type or "application/octet-stream"

        try:
            client.put_object(
                Config.MINIO_BUCKET,
                object_name,
                BytesIO(data),
                len(data),
                content_type=content_type,
            )
            self.logger.info(f"Uploaded {len(data)} bytes → '{object_name}' ({content_type})")
            return self.get_public_url(object_name)
        except S3Error as e:
            self.logger.error(f"Upload failed for '{object_name}': {e}")
            raise

    def get_public_url(self, object_name: str) -> str:
        """Generate the full public URL for an object."""
        protocol = "https" if Config.MINIO_SECURE else "http"
        return f"{protocol}://{Config.MINIO_ENDPOINT}/{Config.MINIO_BUCKET}/{object_name}"
