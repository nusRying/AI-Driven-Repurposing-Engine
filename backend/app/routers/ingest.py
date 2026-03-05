from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
from ..models.content_queue import IngestRequest, ContentQueueResponse
from ..database import supabase
from ..workers.scrape_task import scrape_content
import uuid

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifies the Supabase JWT and returns the user ID.
    """
    token = credentials.credentials
    try:
        res = supabase.auth.get_user(token)
        if not res.user:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return {"id": res.user.id, "email": res.user.email}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Auth error: {str(e)}")

router = APIRouter(prefix="/api/ingest", tags=["ingestion"])

@router.post("/", response_model=List[ContentQueueResponse])
async def ingest_urls(
    request: IngestRequest,
    user_info: dict = Depends(get_current_user_id)
):
    user_id = user_info["id"]
    user_email = user_info["email"]
    
    # 0. Ensure user exists in public.users (Auto-sync if trigger is missing)
    try:
        supabase.table("users").upsert({
            "id": user_id,
            "email": user_email
        }, on_conflict="id").execute()
    except Exception as e:
        print(f"Warning: Failed to sync user to public table: {str(e)}")

    inserted_items = []
    
    for url in request.urls:
        url_str = str(url)
        # 1. Insert into Supabase
        data = {
            "user_id": user_id,
            "original_url": url_str,
            "status": "Pending"
        }
        
        result = supabase.table("content_queue").insert(data).execute()
        
        if result.data:
            item = result.data[0]
            inserted_items.append(item)
            # 2. Trigger asynchronous scraping task
            scrape_content.delay(item["id"])
            
    return inserted_items
