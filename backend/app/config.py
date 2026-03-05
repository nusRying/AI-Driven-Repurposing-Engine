from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    OLLAMA_HOST: str = "http://host.docker.internal:11434"

    # Apify
    APIFY_API_TOKEN: str

    # AI Service Keys
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    DEEPGRAM_API_KEY: str
    ELEVENLABS_API_KEY: str
    ELEVENLABS_VOICE_ID: str

    # HeyGen
    HEYGEN_API_KEY: str
    HEYGEN_AVATAR_ID: str
    HEYGEN_WEBHOOK_SECRET: Optional[str] = None

    # App URLs
    APP_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file="backend/.env", extra="ignore")

settings = Settings()
