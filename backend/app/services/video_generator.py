import httpx
import os
import subprocess
from ..config import settings
from typing import Optional
from loguru import logger
from ..database import supabase
from ..services.storage import StorageService
from ..utils.caption_generator import CaptionGenerator
import mutagen.mp3  # Need to check audio duration for sync

class VideoGeneratorService:
    def __init__(self):
        self.heygen_key = settings.HEYGEN_API_KEY
        self.api_url = "https://api.heygen.com/v2/video/generate"
        self.storage = StorageService()

    def heygen_active(self) -> bool:
        """Checks if a real HeyGen key is provided."""
        return self.heygen_key and not self.heygen_key.startswith("your-") and len(self.heygen_key) > 20

    def generate(self, content_id: int, audio_url: str, avatar_id: Optional[str] = None) -> str:
        """
        Generates video using HeyGen (Paid) or FFmpeg (Free Local).
        Synchronous call for worker stability.
        """
        if self.heygen_active():
            return self._generate_heygen(audio_url, avatar_id)
        else:
            return self._generate_local(content_id, audio_url)

    def _generate_heygen(self, audio_url: str, avatar_id: Optional[str] = None) -> str:
        """Submit to HeyGen using sync client."""
        logger.info("Submitting video generation to HeyGen")
        avatar_id = avatar_id or settings.HEYGEN_AVATAR_ID
        headers = {
            "X-Api-Key": self.heygen_key,
            "Content-Type": "application/json"
        }
        payload = {
            "video_inputs": [{
                "character": {"type": "avatar", "avatar_id": avatar_id, "avatar_style": "normal"},
                "voice": {"type": "audio", "audio_url": audio_url}
            }],
            "dimension": {"width": 1080, "height": 1920}
        }

        with httpx.Client() as client:
            response = client.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["data"]["video_id"]

    def _generate_local(self, content_id: int, audio_url: str) -> str:
        """
        FREE ALTERNATIVE FLAG.
        """
        logger.info("Using Local Free Video Engine (FFmpeg)")
        return f"local_free_{content_id}"

    def complete_local_video(self, content_id: int, audio_url: str) -> str:
        """
        Does the actual FFmpeg work synchronously.
        Now with animated captions, JSON scenes, and dynamic stock B-Roll.
        """
        import json
        import re
        import asyncio
        from ..services.asset_fetcher import AssetFetcherService
        
        os.makedirs("/tmp/renders", exist_ok=True)
        out_path = f"/tmp/renders/{content_id}_final.mp4"
        ass_path = f"/tmp/renders/{content_id}_subs.ass"
        
        logger.info(f"Rendering Elite Cinematic video with FFmpeg: {out_path}")
        
        # 1. Fetch script and audio
        res = supabase.table("content_queue").select("generated_script").eq("id", content_id).single().execute()
        raw_script = res.data["generated_script"]
        
        # Parse JSON
        try:
            clean_script = re.sub(r'(?i)```json\n?', '', raw_script)
            clean_script = re.sub(r'\n?```', '', clean_script).strip()
            scenes = json.loads(clean_script)
            full_narration = " ".join([s.get("narration", "") for s in scenes])
        except Exception as e:
            logger.warning(f"Could not parse script as JSON ({e}), falling back to single scene.")
            full_narration = raw_script
            scenes = [{"narration": raw_script, "cartoon_keyword": "satisfying 3d animation"}]
        
        # Download audio locally
        audio_local_path = f"/tmp/renders/{content_id}_audio.mp3"
        with httpx.Client(follow_redirects=True) as client:
            resp = client.get(audio_url)
            resp.raise_for_status() # Ensure we actually downloaded it
            with open(audio_local_path, "wb") as f:
                f.write(resp.content)
            
            if os.path.getsize(audio_local_path) == 0:
                raise ValueError(f"Downloaded audio file is 0 bytes for URL: {audio_url}")
        
        audio_info = mutagen.mp3.MP3(audio_local_path)
        total_duration = audio_info.info.length
        total_words = len(full_narration.split())
        
        # 2. Generate Animated Captions
        cgen = CaptionGenerator()
        cgen.generate_ass(full_narration, total_duration, ass_path)
        safe_ass_path = ass_path.replace(":", "\\:").replace("\\", "/")

        # 3. Dynamic Asset Fetching & Scene Timings
        fetcher = AssetFetcherService()
        scene_assets = []
        sfx_events = [] # List of (timestamp, sfx_type)
        
        def run_async_fetch(kw, idx):
            loop = asyncio.get_event_loop() if asyncio.get_event_loop().is_running() else asyncio.new_event_loop()
            return loop.run_until_complete(fetcher.fetch_scene_asset(kw, idx, content_id))

        def run_async_fetch_bgm():
            loop = asyncio.get_event_loop() if asyncio.get_event_loop().is_running() else asyncio.new_event_loop()
            return loop.run_until_complete(fetcher.fetch_bgm())

        current_time = 0.0
        for idx, scene in enumerate(scenes):
            words_in_scene = len(scene.get("narration", "").split())
            ratio = words_in_scene / total_words if total_words > 0 else (1.0 / len(scenes))
            scene_duration = total_duration * ratio
            
            if scene_duration < 2.0:
                scene_duration = 2.0
            
            # Record SFX events
            sfx_type = scene.get("sfx", "none").lower()
            if sfx_type != "none":
                sfx_events.append((current_time, sfx_type))
                
            keyword = scene.get("cartoon_keyword", "satisfying loop")
            video_path = run_async_fetch(keyword, idx)
            
            if video_path and os.path.exists(video_path):
                scene_assets.append({
                    "path": video_path,
                    "duration": scene_duration
                })
            
            current_time += scene_duration

        bgm_path = run_async_fetch_bgm()

        # 4. Multi-Pass FFmpeg Rendering Strategy
        silent_video_path = f"/tmp/renders/{content_id}_silent.mp4"
        mixed_audio_path = f"/tmp/renders/{content_id}_mixed.wav"

        # PASS 1: VISUALS
        logger.info("Pass 1: Rendering Visuals (Split-Screen vstack)")
        bottom_gameplay_path = os.path.join(os.path.dirname(__file__), "..", "assets", "bottom_gameplay.mp4")
        if not os.path.exists(bottom_gameplay_path):
            bottom_gameplay_path = os.path.join(os.path.dirname(__file__), "..", "assets", "bg_video.mp4")

        cmd_pass1 = ["ffmpeg", "-y"]
        filter_parts_v = []
        concat_v_str = ""
        for i, asset in enumerate(scene_assets):
            cmd_pass1.extend(["-i", asset["path"]])
            filter_parts_v.append(
                f"[{i}:v]loop=-1:size=2,setpts=N/FRAME_RATE/TB,scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960,eq=brightness=-0.1:contrast=1.1,trim=duration={asset['duration']},fps=30[vtop{i}]"
            )
            concat_v_str += f"[vtop{i}]"
        
        if scene_assets:
            filter_parts_v.append(f"{concat_v_str}concat=n={len(scene_assets)}:v=1:a=0[top_concat]")
        
        bottom_idx = len(scene_assets)
        cmd_pass1.extend(["-stream_loop", "-1", "-i", bottom_gameplay_path])
        filter_parts_v.append(f"[{bottom_idx}:v]scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960,trim=duration={total_duration},setpts=PTS-STARTPTS[bottom_v]")
        
        if scene_assets:
            filter_parts_v.append(f"[top_concat][bottom_v]vstack=inputs=2[final_v]")
        else:
            filter_parts_v.append(f"color=c=0x1a1a2e:s=1080x960:r=30:d={total_duration}[top_concat]")
            filter_parts_v.append(f"[top_concat][bottom_v]vstack=inputs=2[final_v]")

        filter_complex_v = ";".join(filter_parts_v)
        cmd_pass1.extend(["-filter_complex", filter_complex_v, "-map", "[final_v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-t", str(total_duration), silent_video_path])
        subprocess.run(cmd_pass1, capture_output=True, text=True)

        # PASS 2: AUDIO (Mixing TTS, BGM, and SFX)
        logger.info("Pass 2: Rendering Audio (TTS + BGM + SFX)")
        cmd_pass2 = ["ffmpeg", "-y", "-i", audio_local_path]
        
        sfx_inputs = []
        sfx_map = {
            "pop": os.path.join(os.path.dirname(__file__), "..", "assets", "sfx_pop.m4a"),
            "whoosh": os.path.join(os.path.dirname(__file__), "..", "assets", "sfx_whoosh.m4a"),
            "ding": os.path.join(os.path.dirname(__file__), "..", "assets", "sfx_ding.m4a")
        }
        
        # Add BGM input if exists
        if bgm_path and os.path.exists(bgm_path):
            cmd_pass2.extend(["-stream_loop", "-1", "-i", bgm_path])
            has_bgm = True
        else:
            has_bgm = False
            
        # Add SFX inputs
        active_sfx_files = []
        for ts, sfx_type in sfx_events:
            path = sfx_map.get(sfx_type)
            if path and os.path.exists(path):
                cmd_pass2.extend(["-i", path])
                active_sfx_files.append((ts, len(active_sfx_files) + (2 if has_bgm else 1)))
        
        filter_parts_a = []
        mix_inputs = ["[0:a]"] # Start with narration
        
        if has_bgm:
            filter_parts_a.append(f"[1:a]volume=0.12[bgm_vol]")
            mix_inputs.append("[bgm_vol]")
            
        for i, (ts, input_idx) in enumerate(active_sfx_files):
            ms = int(ts * 1000)
            filter_parts_a.append(f"[{input_idx}:a]adelay={ms}|{ms}[sfx{i}]")
            mix_inputs.append(f"[sfx{i}]")
            
        mix_str = "".join(mix_inputs)
        filter_parts_a.append(f"{mix_str}amix=inputs={len(mix_inputs)}:duration=first:dropout_transition=2[final_a]")
        
        cmd_pass2.extend([
            "-filter_complex", ";".join(filter_parts_a),
            "-map", "[final_a]",
            "-c:a", "pcm_s16le", "-t", str(total_duration), mixed_audio_path
        ])
        
        subprocess.run(cmd_pass2, capture_output=True, text=True)

        # PASS 3: MUX & SUBTITLES & PROGRESS BAR
        logger.info("Pass 3: Final Mux (Subtitles + Progress Bar)")
        
        # Hormozi Progress Bar: A simple red bar at the bottom that fills up over time.
        # x=0, y=1914, w=iw*(t/duration), h=6, color=red, thickness=fill
        progress_bar_filter = f"drawbox=x=0:y=ih-6:w=iw*t/{total_duration}:h=6:color=red:t=fill"
        
        cmd_pass3 = [
            "ffmpeg", "-y",
            "-i", silent_video_path,
            "-i", mixed_audio_path,
            "-vf", f"subtitles={safe_ass_path},{progress_bar_filter}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(total_duration),
            out_path
        ]
        subprocess.run(cmd_pass3, capture_output=True, text=True)
        
        # Upload result
        with open(out_path, "rb") as f:
            final_url = self.storage.upload("video", f"{content_id}_repurposed.mp4", f.read(), "video/mp4")
            
        return final_url
