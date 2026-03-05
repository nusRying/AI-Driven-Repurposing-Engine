# AI Driven Repurposing Engine

A full-stack content repurposing pipeline designed to transform long-form video content into high-retention short-form social media assets.

## 🚀 Recent Progress

We have completed a comprehensive project assessment and infrastructure verification. Key accomplishments include:

- **Architecture Validation**: Confirmed the end-to-end flow from URL ingestion to final avatar video generation.
- **Pipeline Mapping**: Identified all core stages including smart scraping, RAG-based scripting, and multi-AI rendering.
- **Dependency Resolution**: Fixed a critical version conflict between `supabase` and `httpx` and silenced Docker build warnings.
- **Infrastructure Readiness**: Verified Supabase database schema and storage bucket configuration.

## 🛠 Technology Stack

### Backend (Python/FastAPI)

- **API**: FastAPI for high-performance service orchestration.
- **Task Queue**: Celery with Redis for asynchronous processing.
- **Database**: Supabase (PostgreSQL) for state management and Knowledge Base (KB).
- **Storage**: Supabase Storage for thumbnails, audio, and video assets.

### Frontend (Next.js)

- **Framework**: Next.js 15 with App Router.
- **UI Components**: Tailwind CSS, Framer Motion, and Lucide React.
- **Real-time**: Supabase subscriptions for pipeline status tracking.

### AI Engine (Best-in-Class Models)

- **Scraping**: `yt-dlp` and Apify (YouTube/TikTok/Instagram).
- **Transcription**: Deepgram for high-fidelity speech-to-text.
- **Scripting**: Claude 3.5 Sonnet and GPT-4o for brand-aligned script generation.
- **Audio**: ElevenLabs for realistic voice synthesis.
- **Video**: HeyGen for automated avatar delivery.

## 🔄 Content Pipeline Flow

1.  **Ingest**: Accept source URLs via API/Dashboard.
2.  **Scrape**: Extract metadata and captions (or fallback to audio extraction).
3.  **Transcribe**: Use Deepgram for audio-to-text if captions aren't available.
4.  **Script**: Generate a viral short-form script using Knowledge Base instructions (RAG).
5.  **Approve**: Manual review/edit of the script via the Command Center.
6.  **Audio**: Synthesize voiceover via ElevenLabs.
7.  **Video**: Render final 4K avatar video via HeyGen.

## ⚙️ Getting Started

### Prerequisites

- Docker Desktop
- Python 3.11+
- Node.js 20+

### Setup Infrastructure

```bash
# From project root
docker compose up -d redis
```

### Start Backend

```bash
# From backend/ directory
uvicorn app.main:app --reload
celery -A app.workers.celery_app worker --loglevel=info
```

### Start Frontend

```bash
# From frontend/ directory
npm run dev
```

## 📝 Configuration

Ensure `backend/.env` is populated with the necessary AI service keys (OpenAI, Anthropic, HeyGen, etc.).
