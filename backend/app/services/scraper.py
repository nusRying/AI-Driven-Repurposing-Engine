import re
import asyncio
import os
import tempfile
import yt_dlp
from typing import Optional, Dict, Any, List
from apify_client import ApifyClient
from youtube_transcript_api import YouTubeTranscriptApi
from ..config import settings
from pydantic import BaseModel
from loguru import logger

class ScrapedData(BaseModel):
    platform: str
    url: str
    metadata: Dict[str, Any]
    transcript: Optional[str] = None
    transcript_source: Optional[str] = None
    audio_data: Optional[bytes] = None

class ScraperService:
    def __init__(self):
        # Apify client is no longer needed
        pass

    def detect_platform(self, url: str) -> str:
        url = str(url).lower()
        if "youtube.com" in url or "youtu.be" in url:
            return "youtube"
        elif "tiktok.com" in url:
            return "tiktok"
        elif "instagram.com" in url:
            return "instagram"
        return "generic"

    def _extract_youtube_id(self, url: str) -> Optional[str]:
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'youtu\.be\/([0-9A-Za-z_-]{11})',
            r'embed\/([0-9A-Za-z_-]{11})',
            r'shorts\/([0-9A-Za-z_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    async def _get_youtube_transcript(self, video_id: str) -> Optional[str]:
        try:
            transcript_list = await asyncio.to_thread(YouTubeTranscriptApi.get_transcript, video_id)
            return " ".join([t['text'] for t in transcript_list])
        except Exception as e:
            logger.warning(f"Could not fetch YouTube transcript for {video_id}: {e}")
            return None

    async def scrape(self, url: str) -> ScrapedData:
        platform = self.detect_platform(url)
        metadata = {}
        transcript = None
        transcript_source = None

        # 1. Fetch metadata and subtitles via yt-dlp (Local & Free)
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en.*'],
        }

        try:
            def _get_info():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            info = await asyncio.to_thread(_get_info)
            metadata = {
                "title": info.get("title"),
                "description": info.get("description"),
                "thumbnail_url": info.get("thumbnail"),
                "tags": info.get("tags"),
                "view_count": info.get("view_count"),
            }

            # 2. Extract Transcript from yt-dlp info if available
            # Note: yt-dlp provides subtitle URLs, but for simplicity 
            # we first try youtube-transcript-api for YouTube
            if platform == "youtube":
                video_id = info.get("id")
                if video_id:
                    transcript = await self._get_youtube_transcript(video_id)
                    if transcript:
                        transcript_source = "captions"

        except Exception as e:
            logger.error(f"yt-dlp scraping failed for {url}: {e}")

        # 3. Audio extraction if no transcript exists
        audio_data = None
        if not transcript:
            try:
                logger.info(f"No captions found for {url}. Attempting local audio extraction...")
                audio_data = await self.extract_audio(url)
            except Exception as e:
                logger.error(f"Audio extraction failed: {e}")

        return ScrapedData(
            platform=platform,
            url=url,
            metadata=metadata,
            transcript=transcript,
            transcript_source=transcript_source,
            audio_data=audio_data if not transcript else None
        )

    async def extract_audio(self, url: str) -> bytes:
        """
        Extract audio from URL using yt-dlp.
        Returns audio bytes.
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'outtmpl': tempfile.gettempdir() + '/%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }

        def _download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
                
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                # Cleanup
                if os.path.exists(file_path):
                    os.remove(file_path)
                return data

        return await asyncio.to_thread(_download)
