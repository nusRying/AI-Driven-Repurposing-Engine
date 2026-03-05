import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
from loguru import logger

def seed_kb(user_id: str):
    load_dotenv(".env")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("Missing SUPABASE environment variables.")
        return

    supabase: Client = create_client(supabase_url, supabase_key)
    
    logger.info(f"Seeding Knowledge Base for user: {user_id}")

    seed_entries = [
        {
            "user_id": user_id,
            "entry_type": "instruction",
            "title": "Short Punchy Delivery",
            "content": "Use simple words. Avoid jargon. Ensure sentences are rhythmic and easy for an AI avatar to speak without stumbling.",
            "priority": 10
        },
        {
            "user_id": user_id,
            "entry_type": "tone_example",
            "title": "Viral Hook Example",
            "content": "Stop scrolling! If you're still building websites manually in 2024, you're falling behind. Here's exactly how I automated my entire frontend workflow using three simple AI tools.",
            "priority": 9
        },
        {
            "user_id": user_id,
            "entry_type": "vocabulary",
            "title": "Keywords to Use",
            "content": "Efficiency, Automation, Hidden Gems, Game Changer, Massive ROI.",
            "priority": 5
        },
        {
            "user_id": user_id,
            "entry_type": "hook_template",
            "title": "The Transformation Hook",
            "content": "I went from [Pain Point] to [Desired Outcome] in just [Time Period] by using [Solution].",
            "priority": 10
        }
    ]

    try:
        # Check if already seeded (optional)
        existing = supabase.table("knowledge_base").select("id").eq("user_id", user_id).limit(1).execute()
        if existing.data:
            logger.warning("Knowledge Base already has entries for this user. Overwrite or skip?")
            # For simplicity, we'll just add them.
        
        res = supabase.table("knowledge_base").insert(seed_entries).execute()
        logger.success(f"Successfully seeded {len(seed_entries)} KB entries.")
    except Exception as e:
        logger.error(f"Seeding failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python scripts/seed_kb.py <USER_ID>")
        sys.exit(1)
    
    seed_kb(sys.argv[1])
