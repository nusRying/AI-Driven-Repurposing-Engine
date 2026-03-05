from ..database import supabase
from ..config import settings
from typing import Optional

class StorageService:
    @staticmethod
    def upload(bucket: str, file_path: str, file_data: bytes, content_type: str = "application/octet-stream") -> str:
        """
        Upload file data to a Supabase Storage bucket.
        Returns the public URL of the uploaded file.
        """
        try:
            # Overwrite if exists
            supabase.storage.from_(bucket).upload(
                path=file_path,
                file=file_data,
                file_options={"content-type": content_type, "x-upsert": "true"}
            )
            
            # Get public URL
            res = supabase.storage.from_(bucket).get_public_url(file_path)
            return res
            
        except Exception as e:
            print(f"Storage upload failed: {e}")
            raise e
