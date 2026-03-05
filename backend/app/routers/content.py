from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.content_queue import ContentQueueResponse
from ..database import supabase
from ..workers.audio_task import generate_audio
from datetime import datetime

router = APIRouter(prefix="/api/content", tags=["content"])

# Placeholder for Auth Dependency (consistent with ingest)
async def get_current_user_id():
    return "00000000-0000-0000-0000-000000000000"

@router.get("/", response_model=List[ContentQueueResponse])
async def list_content(user_id: str = Depends(get_current_user_id)):
    res = supabase.table("content_queue").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return res.data

@router.get("/{content_id}", response_model=ContentQueueResponse)
async def get_content(content_id: int, user_id: str = Depends(get_current_user_id)):
    res = supabase.table("content_queue").select("*").eq("id", content_id).eq("user_id", user_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Content not found")
    return res.data

@router.post("/{content_id}/approve", response_model=ContentQueueResponse)
async def approve_script(content_id: int, user_id: str = Depends(get_current_user_id)):
    # 1. Verify existence and status
    res = supabase.table("content_queue").select("*").eq("id", content_id).eq("user_id", user_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # 2. Update status to Approved
    update_data = {
        "status": "Approved",
        "approved_at": datetime.now().isoformat()
    }
    updated = supabase.table("content_queue").update(update_data).eq("id", content_id).execute()
    
    # 3. Trigger Audio Generation Task
    generate_audio.delay(content_id)
    
    return updated.data[0]

@router.patch("/{content_id}", response_model=ContentQueueResponse)
async def update_script(content_id: int, script: str, user_id: str = Depends(get_current_user_id)):
    update_data = {
        "generated_script": script,
        "script_edited_by_user": True
    }
    res = supabase.table("content_queue").update(update_data).eq("id", content_id).eq("user_id", user_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Content not found")
    return res.data[0]

@router.delete("/{content_id}")
async def delete_content(content_id: int, user_id: str = Depends(get_current_user_id)):
    supabase.table("content_queue").delete().eq("id", content_id).eq("user_id", user_id).execute()
    return {"message": "Content deleted"}
