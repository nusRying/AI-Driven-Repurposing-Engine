import httpx
from ..config import settings
from typing import Optional

class VideoGeneratorService:
    def __init__(self):
        self.api_url = "https://api.heygen.com/v2/video/generate"
        self.headers = {
            "X-Api-Key": settings.HEYGEN_API_KEY,
            "Content-Type": "application/json"
        }

    async def generate(self, audio_url: str, avatar_id: Optional[str] = None) -> str:
        """
        Submit a video generation request to HeyGen using an audio URL.
        Returns the heygen_video_id.
        """
        avatar_id = avatar_id or settings.HEYGEN_AVATAR_ID
        
        payload = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "audio",
                    "audio_url": audio_url
                }
            }],
            "dimension": {"width": 1080, "height": 1920}
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("data") and data["data"].get("video_id"):
                return data["data"]["video_id"]
            else:
                raise Exception(f"HeyGen API Error: {data}")
