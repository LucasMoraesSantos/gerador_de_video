from pathlib import Path
import subprocess

from app.config import settings


def render_short_video(background_video: str, narration_audio: str, subtitle_srt: str, output_file: str) -> str:
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        settings.ffmpeg_bin,
        '-y',
        '-i',
        background_video,
        '-i',
        narration_audio,
        '-vf',
        f"subtitles={subtitle_srt}:force_style='Fontsize=16,PrimaryColour=&H00FFFFFF&'",
        '-map',
        '0:v:0',
        '-map',
        '1:a:0',
        '-shortest',
        output_file,
    ]
    subprocess.run(cmd, check=True)
    return output_file
