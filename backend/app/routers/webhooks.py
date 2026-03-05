from fastapi import APIRouter, Request, HTTPException
from ..database import supabase
import httpx

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

@router.post("/heygen")
async def heygen_webhook(request: Request):
    """
    Receiver for HeyGen v2 webhooks.
    Docs: https://docs.heygen.com/reference/webhook-events
    """
    payload = await request.json()
    event_type = payload.get("event_type")
    data = payload.get("event_data", {})
    
    video_id = data.get("video_id")
    if not video_id:
        raise HTTPException(status_code=400, detail="Missing video_id")

    # 1. Look up content by heygen_video_id
    res = supabase.table("content_queue").select("id").eq("heygen_video_id", video_id).single().execute()
    if not res.data:
        # Might be a request from another environment or older session
        return {"status": "ignored", "reason": "video_id not found in queue"}

    content_id = res.data["id"]

    if event_type == "video.success":
        video_url = data.get("url")
        # 2. Update status and save URL
        supabase.table("content_queue").update({
            "status": "Video_Completed",
            "final_video_url": video_url
        }).eq("id", content_id).execute()
        return {"status": "success"}

    elif event_type == "video.failed":
        error_msg = data.get("error", "Unknown HeyGen error")
        supabase.table("content_queue").update({
            "status": "Failed",
            "error_message": error_msg
        }).eq("id", content_id).execute()
        return {"status": "handled_failure"}

    return {"status": "received", "event_type": event_type}
