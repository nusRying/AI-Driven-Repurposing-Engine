import asyncio
from ..workers.celery_app import celery_app
from ..database import supabase
from ..services.video_generator import VideoGeneratorService

# Helper to run async in Celery
def run_async(coro):
    return asyncio.run(coro)

@celery_app.task(bind=True, max_retries=3)
def generate_video(self, content_id: int):
    """
    Celery task to submit a video generation request to HeyGen.
    Relies on webhooks for the final completion.
    """
    video_service = VideoGeneratorService()
    
    # Update status to Video_Generating
    supabase.table("content_queue").update({"status": "Video_Generating"}).eq("id", content_id).execute()
    
    try:
        # 1. Fetch record
        res = supabase.table("content_queue").select("audio_url").eq("id", content_id).single().execute()
        content = res.data
        
        # 2. Submit / Generate (Sync)
        video_result = video_service.generate(content_id, content["audio_url"])
        
        # 3. Handle Result
        if video_result.startswith("local_free_"):
            # Execute local FFmpeg finish (Sync)
            final_url = video_service.complete_local_video(content_id, content["audio_url"])
            supabase.table("content_queue").update({
                "status": "Video_Completed",
                "final_video_url": final_url
            }).eq("id", content_id).execute()
            return f"Successfully generated local free video for {content_id}"
        else:
            # HeyGen Case
            supabase.table("content_queue").update({"heygen_video_id": video_result}).eq("id", content_id).execute()
            return f"Successfully submitted video for {content_id} (HeyGen ID: {video_result})"
        
    except Exception as exc:
        supabase.table("content_queue").update({
            "status": "Failed",
            "error_message": str(exc)
        }).eq("id", content_id).execute()
        raise self.retry(exc=exc, countdown=60)
