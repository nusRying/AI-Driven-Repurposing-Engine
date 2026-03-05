import asyncio
from typing import Dict, Any
from ..workers.celery_app import celery_app
from ..database import supabase
from ..services.scraper import ScraperService
from ..services.transcriber import TranscriberService
from loguru import logger

# Helper to run async in Celery
def run_async(coro):
    return asyncio.run(coro)

@celery_app.task(bind=True, max_retries=3)
def scrape_content(self, content_id: int):
    """
    Celery task to scrape content metadata and transcripts.
    Chains to script generation upon success.
    """
    scraper = ScraperService()
    transcriber = TranscriberService()
    
    # 1. Fetch record
    res = supabase.table("content_queue").select("*").eq("id", content_id).single().execute()
    if not res.data:
        logger.error(f"Content {content_id} not found")
        return f"Content {content_id} not found"
    
    url = res.data["original_url"]
    
    # Update status to Scraping
    supabase.table("content_queue").update({"status": "Scraping"}).eq("id", content_id).execute()
    
    try:
        # 2. Run Scraper (Async)
        scraped_data = run_async(scraper.scrape(url))
        
        transcript = scraped_data.transcript
        transcript_source = scraped_data.transcript_source
        
        # 3. Handle missing captions via Deepgram
        if not transcript and scraped_data.audio_data:
            logger.info(f"Triggering Deepgram for {content_id}...")
            supabase.table("content_queue").update({"status": "Transcribing"}).eq("id", content_id).execute()
            
            transcript, source = run_async(transcriber.transcribe(scraped_data.audio_data))
            transcript_source = source

        # 4. Update Database
        update_data = {
            "status": "Scraped",
            "platform": scraped_data.platform,
            "source_title": scraped_data.metadata.get("title") or scraped_data.metadata.get("text"),
            "source_description": scraped_data.metadata.get("description") or scraped_data.metadata.get("caption"),
            "thumbnail_url": scraped_data.metadata.get("thumbnail_url") or scraped_data.metadata.get("displayUrl"),
            "original_transcript": transcript,
            "transcript_source": transcript_source,
        }
        
        supabase.table("content_queue").update(update_data).eq("id", content_id).execute()
        
        # 5. Chain to Script Generation
        from ..workers.script_task import generate_script
        generate_script.delay(content_id)
        
        return f"Successfully processed {content_id}"
        
    except Exception as exc:
        logger.error(f"Scrape task failed for {content_id}: {exc}")
        supabase.table("content_queue").update({
            "status": "Failed",
            "error_message": str(exc)
        }).eq("id", content_id).execute()
        raise self.retry(exc=exc, countdown=60)
