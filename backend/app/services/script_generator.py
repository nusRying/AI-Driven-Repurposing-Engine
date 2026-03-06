import httpx
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from ..config import settings
from ..database import supabase
from loguru import logger
import asyncio

class ScriptGeneratorService:
    def __init__(self):
        # Configuration for both Local (Ollama) and Cloud (Gemini)
        self.ollama_host = settings.OLLAMA_HOST
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.has_gemini = True
        else:
            self.has_gemini = False

    async def _retrieve_knowledge(self, user_id: str) -> Dict[str, List[str]]:
        """
        Structured retrieval from knowledge_base table.
        """
        try:
            res = supabase.table("knowledge_base") \
                .select("*") \
                .eq("user_id", user_id) \
                .eq("is_active", True) \
                .order("priority", desc=True) \
                .execute()

            grouped = {
                "system_prompts": [],
                "tone_examples": [],
                "vocabulary": [],
                "instructions": [],
                "hook_templates": [],
            }
            for entry in res.data:
                key = entry["entry_type"] + "s"
                if key in grouped:
                    grouped[key].append(entry["content"])
            return grouped
        except Exception as e:
            logger.error(f"Failed to retrieve KB for user {user_id}: {e}")
            return {}

    async def generate(self, content_id: int, user_id: str, model_pref: Optional[str] = None, temperature: float = 0.7) -> str:
        # 1. Fetch content metadata
        res = supabase.table("content_queue").select("*").eq("id", content_id).single().execute()
        content = res.data
        
        # 2. Fetch Knowledge Base for RAG
        kb = await self._retrieve_knowledge(user_id)

        # 3. Build Dynamic Prompts
        kb_context = []
        if kb.get('instructions'):
            kb_context.append(f"### CORE INSTRUCTIONS:\n{chr(10).join(kb['instructions'])}")
        
        if kb.get('tone_examples'):
            kb_context.append(f"### WRITING STYLE EXAMPLES (Imitate this cadence):\n{chr(10).join(f'Example: {ex}' for ex in kb['tone_examples'])}")
            
        if kb.get('vocabulary'):
            kb_context.append(f"### TERMS TO USE/AVOID:\n{chr(10).join(kb['vocabulary'])}")

        if kb.get('hook_templates'):
            kb_context.append(f"### PREFERRED HOOK TYPES:\n{chr(10).join(kb['hook_templates'])}")

        system_prompt = f"""You are an elite Content Marketer and viral video strategist. 
Your goal is to transform long-form transcripts into high-retention 2-minute video lessons (300-350 words).

{chr(10).join(kb_context) if kb_context else "Use a professional, engaging, and authoritative tone."}

### PSYCHOLOGICAL REQUIREMENTS:
1. THE 3-PART HOOK (0-3s): Start with a pattern interrupt. 
   - Visual hook idea must be shocking.
   - Audio hook must make a bold claim.
2. POP-CULTURE INTEGRATION: You are creating videos under Educational Fair Use. DO NOT restrict yourself to copyright-free material. For your 'cartoon_keyword', specify highly recognizable, famous pop-culture moments to maximize viewer retention (e.g., 'family guy funny moment', 'spongebob thinking meme', 'gta 5 mega ramp jump', 'marvel epic scene', 'tiktok viral meme').
3. OPEN LOOPS: Insert a transition around the 1-minute mark to retain viewers (e.g., "But here is the crazy part...").
4. PACING: Short, punchy sentences designed for TikTok/Reels/Shorts retention metrics.

### OUTPUT FORMAT: ABSOLUTE STRICT JSON ARRAY
Respond ONLY with a raw JSON array. DO NOT wrap it in Markdown like ```json. Do not add any conversational text.
You are the Video Director. Break the 300-word script down into exactly 3 to 5 logical "Scenes" based on visual context.

Array Schema:
[
  {{
    "scene_number": 1,
    "narration": "The exact spoken text for this block...",
    "cartoon_keyword": "A search term for a famous pop-culture video background (e.g. 'spongebob meme', 'gta 5 stunts', 'family guy funny', 'movie epic scene')",
    "sfx": "whoosh" // Options: "pop", "whoosh", "ding", or "none"
  }},
  ...
]"""

        user_prompt = f"""VIDEO TITLE: {content.get('source_title', 'No Title')}
TRANSCRIPT:
---
{content.get('original_transcript', '')}
---
Write the elite 2-minute viral script and output the STRICT JSON array scene breakdown."""

        # 4. LLM Execution (Priority: Gemini if key exists, else fallback to Ollama)
        try:
            # Check for production/cloud key first
            if self.has_gemini:
                logger.info("Generating script using Google Gemini 1.5 Pro (Cloud)...")
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-pro",
                    system_instruction=system_prompt
                )
                response = await asyncio.to_thread(model.generate_content, user_prompt, generation_config={"temperature": temperature})
                return response.text
            
            # Fallback to local Ollama
            logger.info(f"Generating script using local Ollama API ({model_pref or 'llama3'})...")
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/chat",
                    json={
                        "model": model_pref or "llama3",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "stream": False,
                        "options": {
                            "temperature": temperature
                        }
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data['message']['content']

        except Exception as e:
            logger.critical(f"Script generation failed (Hybrid): {e}")
            raise e
