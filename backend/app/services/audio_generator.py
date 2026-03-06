import asyncio
import edge_tts
from ..config import settings
from typing import Optional
from loguru import logger
import os

def run_async(coro):
    """Helper to run async code in a synchronous block."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

try:
    from elevenlabs.client import ElevenLabs
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

class AudioGeneratorService:
    def __init__(self):
        self.eleven_key = settings.ELEVENLABS_API_KEY
        if self.eleven_active() and SDK_AVAILABLE:
            self.client = ElevenLabs(api_key=self.eleven_key)
        
    def eleven_active(self) -> bool:
        """Checks if a real ElevenLabs key is provided."""
        return self.eleven_key and not self.eleven_key.startswith("xi-") and self.eleven_key != "your-elevenlabs-key"

    def generate(self, script: str, voice_id: Optional[str] = None) -> bytes:
        """
        Generate MP3 audio from script text.
        Synchronous method for Celery worker stability.
        """
        if self.eleven_active() and SDK_AVAILABLE:
            return self._generate_elevenlabs(script, voice_id)
        else:
            return self._generate_edge_tts(script)

    def _generate_edge_tts(self, text: str) -> bytes:
        """
        Generates highly natural Neural audio using Edge-TTS.
        Much more human-like than gTTS.
        """
        logger.info("Generating high-quality natural audio using Edge-TTS")
        # Sonia is a very clear and engaging British female voice
        voice = "en-GB-SoniaNeural"
        communicate = edge_tts.Communicate(text, voice)
        
        try:
            # Capture bytes from the generator
            audio_bytes = b""
            async def _capture():
                nonlocal audio_bytes
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_bytes += chunk["data"]
            
            run_async(_capture())
            
            if len(audio_bytes) == 0:
                raise ValueError(f"edge-tts returned zero audio bytes for text length {len(text)}.")
                
            return audio_bytes
        except Exception as e:
            logger.error(f"Edge-TTS failed ({e}). Falling back to gTTS.")
            from gtts import gTTS
            import io
            tts = gTTS(text=text, lang="en")
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            return fp.getvalue()

    def _generate_elevenlabs(self, script: str, voice_id: Optional[str] = None) -> bytes:
        """
        Generate MP3 audio using ElevenLabs (Paid/Free Tier).
        Synchronous call.
        """
        logger.info("Generating audio using ElevenLabs")
        voice_id = voice_id or settings.ELEVENLABS_VOICE_ID
        
        try:
            # ElevenLabs v1 client .convert is a generator that yields bytes
            audio_generator = self.client.text_to_speech.convert(
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
            b = b""
            for chunk in audio_generator:
                b += chunk
            return b
        except Exception as e:
            logger.error(f"ElevenLabs generation failed: {e}")
            raise e
