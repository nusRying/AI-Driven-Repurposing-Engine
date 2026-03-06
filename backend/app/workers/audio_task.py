import asyncio
from ..workers.celery_app import celery_app
from ..database import supabase
from ..services.audio_generator import AudioGeneratorService
from ..services.storage import StorageService
from ..config import settings

# Helper to run async in Celery
def run_async(coro):
    return asyncio.run(coro)

@celery_app.task(bind=True, max_retries=3)
def generate_audio(self, content_id: int):
    """
    Celery task to generate TTS audio from a script.
    Chains to video generation automatically.
    """
    audio_service = AudioGeneratorService()
    storage_service = StorageService()
    
    # Update status to Audio_Generating
    supabase.table("content_queue").update({"status": "Audio_Generating"}).eq("id", content_id).execute()
    
    try:
        import json
        import re
        from loguru import logger
        
        # 1. Fetch record
        res = supabase.table("content_queue").select("generated_script, user_id").eq("id", content_id).single().execute()
        content = res.data
        raw_script = content["generated_script"]
        
        try:
            # Clean markdown code blocks if the LLM ignored instructions
            clean_script = re.sub(r'(?i)```json\n?', '', raw_script)
            clean_script = re.sub(r'\n?```', '', clean_script).strip()
            scenes = json.loads(clean_script)
            full_narration = " ".join([scene.get("narration", "") for scene in scenes])
        except Exception as e:
            logger.warning(f"Could not parse script as JSON ({e}), falling back to raw text.")
            full_narration = raw_script
        
        # 2. Generate Audio (Sync)
        audio_bytes = audio_service.generate(full_narration)
        
        # 3. Upload to Storage
        import time
        file_name = f"{content_id}_{int(time.time())}.mp3"
        audio_url = storage_service.upload("audio", file_name, audio_bytes, "audio/mpeg")
        
        # 4. Update Database
        update_data = {
            "status": "Audio_Generated",
            "audio_url": audio_url
        }
        supabase.table("content_queue").update(update_data).eq("id", content_id).execute()
        
        # 5. Chain to Video Generation
        from ..workers.video_task import generate_video
        generate_video.delay(content_id)
        
        return f"Successfully generated audio for {content_id}"
        
    except Exception as exc:
        import traceback
        logger.error(f"Audio task error: {exc}")
        logger.error(traceback.format_exc())
        supabase.table("content_queue").update({
            "status": "Failed",
            "error_message": str(exc)
        }).eq("id", content_id).execute()
        raise self.retry(exc=exc, countdown=60)
