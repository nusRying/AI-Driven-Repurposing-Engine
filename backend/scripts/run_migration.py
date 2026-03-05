import asyncio
import os
import asyncpg
from dotenv import load_dotenv
from loguru import logger

async def run_migration():
    load_dotenv(".env")
    
    # Explicit parameters for reliability
    db_host = "db.vfkakvmzlzrgwaxeetre.supabase.co"
    db_port = 5432
    db_user = "postgres"
    db_pass = "Ue@#ceme8677"
    db_name = "postgres"

    migration_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../supabase/migrations/001_initial_schema.sql"))
    
    if not os.path.exists(migration_path):
        logger.error(f"Migration file not found at: {migration_path}")
        return

    with open(migration_path, "r") as f:
        sql = f.read()

    logger.info(f"Connecting to database at {db_host}...")
    try:
        conn = await asyncpg.connect(
            user=db_user,
            password=db_pass,
            database=db_name,
            host=db_host,
            port=db_port
        )
        logger.info("Running initial schema migration...")
        await conn.execute(sql)
        logger.success("Migration completed successfully!")
        await conn.close()
    except Exception as e:
        logger.error(f"Migration failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_migration())
