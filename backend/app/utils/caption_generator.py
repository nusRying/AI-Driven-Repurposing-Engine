import re
import os

class CaptionGenerator:
    """
    Utility to generate .ass (Advanced Substation Alpha) subtitle files
    with word-level animations for high engagement.
    """
    
    def __init__(self, font_name="DejaVu Sans", font_size=24):
        self.font_name = font_name
        self.font_size = font_size

    def _estimate_word_durations(self, text: str, total_duration: float):
        """
        Estimates the duration of each word based on character count and total audio length.
        A robust fallback when Whisper/alignment models are unavailable.
        """
        words = text.split()
        if not words:
            return []
            
        char_counts = [len(w) for w in words]
        total_chars = sum(char_counts)
        
        # Calculate time per character
        time_per_char = total_duration / total_chars if total_chars > 0 else 0
        
        timed_words = []
        current_time = 0.0
        
        for word in words:
            duration = len(word) * time_per_char
            timed_words.append({
                "word": word,
                "start": current_time,
                "end": current_time + duration
            })
            current_time += duration
            
        return timed_words

    def format_time(self, seconds: float) -> str:
        """Formats seconds into ASS time format H:MM:SS.CC"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int(round((seconds - int(seconds)) * 100))
        if centisecs == 100:
            secs += 1
            centisecs = 0
        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"

    def generate_ass(self, text: str, total_duration: float, output_path: str):
        """
        Generates an .ass file with aggressive word-by-word "Hormozi" style Kinetic Typography.
        Includes explosive scale-ups and bold color highlighting.
        """
        timed_words = self._estimate_word_durations(text, total_duration)
        
        header = [
            "[Script Info]",
            "ScriptType: v4.00+",
            "PlayResX: 1080",
            "PlayResY: 1920",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            # Style: Alignment 10 means Middle Center. 
            # High-contrast colors: Primary &H0000FFFF (Yellow), Border &H00000000 (Black)
            f"Style: Default,{self.font_name},105,&H0000FFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,6,3,10,10,10,960,1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ]
        
        events = []
        # We process every single word as its own dramatic event for high retention
        for word_data in timed_words:
            start_str = self.format_time(word_data["start"])
            end_str = self.format_time(word_data["end"])
            word = word_data["word"].upper().strip(",.?!:;\"'")
            
            if not word:
                continue
                
            # EXPLOSIVE POP ANIMATION:
            # \fscx0\fscy0 : Start at zero size
            # \t(0,100,\fscx120\fscy120) : Pop up to 120% in 100ms
            # \t(100,200,\fscx100\fscy100) : Settle back to 100% size
            # \c&H0000FFFF& : Bright Yellow Primary
            # \3c&H00000000& : Thick black border
            pop_tags = "{\\an10\\fscx100\\fscy100\\t(0,80,\\fscx125\\fscy125)\\t(80,150,\\fscx100\\fscy100)}"
            
            line = f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{pop_tags}{word}"
            events.append(line)
            
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(header + events))
            
        return output_path
