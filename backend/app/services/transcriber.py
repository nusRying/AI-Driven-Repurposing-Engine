import asyncio
import io
import os
import tempfile
from typing import Optional, Tuple
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from openai import AsyncOpenAI
from ..config import settings
from loguru import logger

class TranscriberService:
    def __init__(self):
        self.dg_client = DeepgramClient(settings.DEEPGRAM_API_KEY)
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def transcribe(self, audio_data: bytes) -> Tuple[str, str]:
        """
        Transcribe audio using Deepgram nova-2 with OpenAI Whisper fallback.
        Returns (transcript_text, source_name).
        """
        if not audio_data:
            return "", "error"

        # 1. Try Deepgram Nova-2 (Fast & Cost effective)
        try:
            options = PrerecordedOptions(
                model="nova-2",
                smart_format=True,
                language="en",
            )
            
            payload: FileSource = {
                "buffer": audio_data,
            }

            # dg_client call is currently sync in SDK 3.x, wrapping in thread
            def _dg_call():
                return self.dg_client.listen.prerecorded.v("1").transcribe_file(payload, options)

            response = await asyncio.to_thread(_dg_call)
            transcript = response.results.channels[0].alternatives[0].transcript
            
            if transcript and len(transcript.strip()) > 5:
                return transcript, "deepgram"
            
            logger.warning("Deepgram returned empty or too short transcript. Falling back to Whisper...")

        except Exception as e:
            logger.error(f"Deepgram transcription failed: {e}. Falling back to Whisper...")

        # 2. Fallback to OpenAI Whisper (Robust for difficult audio)
        return await self._transcribe_whisper(audio_data)

    async def _transcribe_whisper(self, audio_data: bytes) -> Tuple[str, str]:
        try:
            # Whisper API requires a file-like object with a name
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
            
            try:
                with open(tmp_path, "rb") as audio_file:
                    response = await self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
                return str(response), "whisper"
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
        except Exception as e:
            logger.critical(f"Whisper fallback also failed: {e}")
            return f"Transcription error: {str(e)}", "error"
