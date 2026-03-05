import asyncio
import os
from dotenv import load_dotenv
from app.services.script_generator import ScriptGeneratorService
from loguru import logger

async def compare_models():
    load_dotenv(".env")
    
    # Mock user ID
    user_id = "00000000-0000-0000-0000-000000000000"
    
    # Sample Transcript (about 1.5 mins of content)
    sample_transcript = """
    In today's video, I want to talk about how AI is literally changing the way we build software. 
    Earlier this year, I was spending about 20 hours a week just doing repetitive coding tasks like 
    writing boilerplate or creating unit tests. But since I started using tools like Claude 3.5 
    and specialized agent frameworks, I've cut that time down to almost nothing. 
    The key isn't just asking the AI to write code, it's about building systems that allow the AI 
    to understand your entire codebase. When you have a RAG system hooked up to your actual source 
    files, the quality of suggestions goes through the roof. You don't have to explain context 
    every time. It just knows. This is a game changer for efficiency and ROI.
    """

    generator = ScriptGeneratorService()

    logger.info("Generating with Claude 3.5 Sonnet...")
    claude_script = await generator.generate(content_id=1, user_id=user_id, model_pref="claude-3.5-sonnet")
    
    logger.info("Generating with GPT-4o...")
    gpt_script = await generator.generate(content_id=1, user_id=user_id, model_pref="gpt-4o")

    print("\n" + "="*50)
    print("CLAUDE 3.5 SONNET RESULT:")
    print("-"*50)
    print(claude_script)
    print("="*50)
    
    print("\n" + "="*50)
    print("GPT-4o RESULT:")
    print("-"*50)
    print(gpt_script)
    print("="*50)

    # Save to file for review
    with open("scripts/comparison_results.txt", "w") as f:
        f.write("CLAUDE 3.5 SONNET:\n")
        f.write(claude_script)
        f.write("\n\n" + "="*20 + "\n\n")
        f.write("GPT-4o:\n")
        f.write(gpt_script)

if __name__ == "__main__":
    # Note: This script assumes a record with ID 1 exists in content_queue 
    # to fetch metadata, but we could mock the service better.
    # For now, let's just run it and see.
    asyncio.run(compare_models())
