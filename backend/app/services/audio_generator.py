import asyncio
try:
    from elevenlabs.client import ElevenLabs
    SDK_V1 = True
except ImportError:
    try:
        from elevenlabs import ElevenLabs
        SDK_V1 = True
    except ImportError:
        from elevenlabs import generate, set_api_key, Voice, VoiceSettings
        SDK_V1 = False

from ..config import settings
from typing import Optional
from loguru import logger

class AudioGeneratorService:
    def __init__(self):
        if SDK_V1:
            self.client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        else:
            set_api_key(settings.ELEVENLABS_API_KEY)

    async def generate(self, script: str, voice_id: Optional[str] = None) -> bytes:
        """
        Generate MP3 audio from script text using ElevenLabs.
        """
        voice_id = voice_id or settings.ELEVENLABS_VOICE_ID
        
        if SDK_V1:
            def _get_stream():
                return self.client.text_to_speech.convert(
                    voice_id=voice_id,
                    model_id="eleven_turbo_v2_5",
                    text=script,
                    voice_settings={
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                        "style": 0.5,
                        "use_speaker_boost": True
                    },
                    output_format="mp3_44100_128"
                )
            
            try:
                audio_stream = await asyncio.to_thread(_get_stream)
                
                # Collect all chunks into bytes
                def _collect_chunks(stream):
                    b = b""
                    for chunk in stream:
                        b += chunk
                    return b

                return await asyncio.to_thread(_collect_chunks, audio_stream)
            except Exception as e:
                logger.error(f"ElevenLabs (v1) generation failed: {e}")
                raise e
        else:
            # Legacy SDK support
            def _legacy_generate():
                return generate(
                    text=script,
                    voice=voice_id,
                    model="eleven_turbo_v2", # v0.2 doesn't have 2.5 usually
                    api_key=settings.ELEVENLABS_API_KEY
                )
            
            try:
                return await asyncio.to_thread(_legacy_generate)
            except Exception as e:
                logger.error(f"ElevenLabs (legacy) generation failed: {e}")
                raise e
