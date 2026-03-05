import asyncio
from ..workers.celery_app import celery_app
from ..database import supabase
from ..services.script_generator import ScriptGeneratorService

# Helper to run async in Celery
def run_async(coro):
    return asyncio.run(coro)

@celery_app.task(bind=True, max_retries=3)
def generate_script(self, content_id: int):
    """
    Celery task to generate an AI script from a transcript.
    Stops the pipeline for human approval.
    """
    generator = ScriptGeneratorService()
    
    # Update status to Script_Generating
    supabase.table("content_queue").update({"status": "Script_Generating"}).eq("id", content_id).execute()
    
    try:
        # 1. Fetch record
        res = supabase.table("content_queue").select("user_id").eq("id", content_id).single().execute()
        user_id = res.data["user_id"]
        
        # 2. Generate Script (Async)
        script = run_async(generator.generate(content_id, user_id))
        
        # 3. Update Database
        update_data = {
            "status": "Script_Generated",
            "generated_script": script
        }
        
        supabase.table("content_queue").update(update_data).eq("id", content_id).execute()
        
        return f"Successfully generated script for {content_id}"
        
    except Exception as exc:
        supabase.table("content_queue").update({
            "status": "Failed",
            "error_message": str(exc)
        }).eq("id", content_id).execute()
        raise self.retry(exc=exc, countdown=60)
