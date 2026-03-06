from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import ingest, content, webhooks
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("AI Driven Repurposing Engine backend starting...")
    yield
    # Shutdown logic
    print("AI Driven Repurposing Engine backend shutting down...")

app = FastAPI(
    title="AI Driven Repurposing Engine",
    description="A full-stack content repurposing pipeline.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(ingest.router)
app.include_router(content.router)
app.include_router(webhooks.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend"}

@app.get("/")
async def root():
    return {"message": "AI Driven Repurposing Engine API is running"}
