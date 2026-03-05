import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
import redis
from loguru import logger

# Add the backend app to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

def verify_infra():
    # 1. Load Environment
    load_dotenv(".env")
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    if not supabase_url or not supabase_key:
        logger.error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment.")
        return

    logger.info(f"Connecting to Supabase PostgREST AI: {supabase_url}")
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # 2. Verify Database Connection
        logger.info("Checking if content_queue exists...")
        try:
            db_res = supabase.table("content_queue").select("id").limit(1).execute()
            logger.success("Table 'content_queue' exists.")
        except Exception as e:
            logger.warning(f"Table check failed (might not exist yet): {e}")

        # 3. Verify Storage Buckets
        logger.info("Initializing storage check...")
        required_buckets = ["thumbnails", "audio", "video"]
        existing_buckets = [b.name for b in supabase.storage.list_buckets()]
        
        for bucket in required_buckets:
            if bucket in existing_buckets:
                logger.success(f"Bucket '{bucket}' already exists.")
            else:
                logger.warning(f"Bucket '{bucket}' missing. Attempting to create...")
                try:
                    supabase.storage.create_bucket(bucket, options={"public": True})
                    logger.success(f"Bucket '{bucket}' created successfully.")
                except Exception as e:
                    logger.error(f"Failed to create bucket '{bucket}': {e}")
        
        # 4. Verify Redis
        logger.info(f"Verifying Redis connection: {redis_url}")
        try:
            r = redis.from_url(redis_url)
            if r.ping():
                logger.success("Redis connection successful.")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")

    except Exception as e:
        logger.critical(f"Infra verification failed: {e}")

if __name__ == "__main__":
    verify_infra()
