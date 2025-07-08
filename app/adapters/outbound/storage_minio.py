from minio import Minio
from app.core.settings import settings

class MinIOStorage:
    def __init__(self, endpoint, access_key, secret_key):
        self.client = Minio(
            endpoint.replace("http://", "").replace("https://", ""),
            access_key=access_key,
            secret_key=secret_key,
            secure=endpoint.startswith("https://"),
        )
        self.bucket = "documents"
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload(self, file_bytes: bytes, filename: str) -> str:
        self.client.put_object(
            self.bucket,
            filename,
            data=bytes(file_bytes),
            length=len(file_bytes),
        )
        return f"{self.bucket}/{filename}"

    def download(self, filename: str) -> bytes:
        resp = self.client.get_object(self.bucket, filename)
        return resp.read()
