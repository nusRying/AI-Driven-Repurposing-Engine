import json
from app.database import supabase
from app.workers.audio_task import generate_audio
import time

script_data = [
    {
        "scene_number": 1,
        "narration": "Stop scrolling! What if I told you that everything you know about productivity is completely backwards? A recent study just uncovered the secret to getting more done by doing absolutely nothing.",
        "cartoon_keyword": "cartoon brain",
        "sfx": "whoosh"
    },
    {
        "scene_number": 2,
        "narration": "Let me explain. Our brains are not designed to be constantly stimulated. When you take a break to look at your phone, you are actually draining the exact mental energy you need to focus. It is called cognitive depletion.",
        "cartoon_keyword": "battery drain loop",
        "sfx": "pop"
    },
    {
        "scene_number": 3,
        "narration": "But here is the crazy part... if you stare at a blank wall for just two minutes, your brain enters a default mode network, completely restoring your dopamine levels.",
        "cartoon_keyword": "abstract mind puzzle",
        "sfx": "pop"
    }
]

print("Injecting script...")
supabase.table("content_queue").update({"generated_script": json.dumps(script_data)}).eq("id", 8).execute()

print("Triggering audio task for ID 8...")
generate_audio.delay(8)
print("Done.")
