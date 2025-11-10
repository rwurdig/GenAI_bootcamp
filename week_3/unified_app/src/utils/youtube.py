import os
import subprocess
import sys
from typing import Optional, Dict, Any, List
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
import re

AUDIO_OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "downloads"))

def _extract_video_id(url: str) -> Optional[str]:
    match = re.search(r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{6,})", url)
    return match.group(1) if match else None

def get_youtube_transcript(url: str, languages: Optional[List[str]] = None) -> Optional[str]:
    languages = languages or ["en", "en-US"]
    vid = _extract_video_id(url)
    if not vid:
        return None
    try:
        parts = YouTubeTranscriptApi.get_transcript(vid, languages=languages)
        return " ".join([p.get("text", "") for p in parts if p.get("text")])
    except NoTranscriptFound:
        return None
    except Exception:
        return None

def download_audio_with_ytdlp(url: str) -> Optional[str]:
    os.makedirs(AUDIO_OUT, exist_ok=True)
    out_path = os.path.join(AUDIO_OUT, "yt_audio.%(ext)s")
    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "-x",
        "--audio-format",
        "mp3",
        "-o",
        out_path,
    ]

    # allow explicit ffmpeg location via env var for systems without ffmpeg on PATH
    ffmpeg_loc = os.getenv("FFMPEG_LOCATION") or os.getenv("FFMPEG_PATH")
    if ffmpeg_loc:
        # If the path points to ffmpeg.exe, extract the directory
        if ffmpeg_loc.lower().endswith("ffmpeg.exe"):
            ffmpeg_loc = os.path.dirname(ffmpeg_loc)
        cmd.extend(["--ffmpeg-location", ffmpeg_loc])
        print(f"Using ffmpeg location: {ffmpeg_loc}")
    else:
        print("No FFMPEG_LOCATION set, yt-dlp will search PATH")

    # append url last
    cmd.append(url)
    
    print(f"Running command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"yt-dlp succeeded. stdout:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        # Print stdout/stderr to aid debugging (visible in Streamlit logs)
        print("yt-dlp failed. stdout:\n", e.stdout)
        print("yt-dlp failed. stderr:\n", e.stderr)
        # Don't return yet - check if the file was downloaded anyway
    except FileNotFoundError as e:
        print(f"File not found error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
    
    # Check if the file exists (even if yt-dlp had postprocessing errors)
    try:
        for f in os.listdir(AUDIO_OUT):
            if f.startswith("yt_audio") and (f.endswith(".mp3") or f.endswith(".webm")):
                audio_path = os.path.join(AUDIO_OUT, f)
                print(f"Found audio file: {audio_path}")
                
                # If it's mp3, return it immediately
                if f.endswith(".mp3"):
                    return audio_path
                
                # If it's webm and we have ffmpeg, try to convert it
                if f.endswith(".webm") and ffmpeg_loc:
                    mp3_path = audio_path.replace(".webm", ".mp3")
                    if not os.path.exists(mp3_path):
                        print(f"Converting webm to mp3...")
                        # Build correct ffmpeg executable path
                        if os.path.isdir(ffmpeg_loc):
                            ffmpeg_exe = os.path.join(ffmpeg_loc, "ffmpeg.exe")
                        elif os.path.isfile(ffmpeg_loc):
                            ffmpeg_exe = ffmpeg_loc
                        else:
                            print(f"Invalid ffmpeg location: {ffmpeg_loc}")
                            return audio_path  # Return webm as fallback
                        
                        if not os.path.isfile(ffmpeg_exe):
                            print(f"ffmpeg.exe not found at: {ffmpeg_exe}")
                            return audio_path  # Return webm as fallback
                        
                        convert_cmd = [
                            ffmpeg_exe, "-i", audio_path,
                            "-vn", "-acodec", "libmp3lame", "-q:a", "2",
                            mp3_path, "-y"
                        ]
                        try:
                            print(f"Running conversion: {' '.join(convert_cmd)}")
                            subprocess.run(convert_cmd, check=True, capture_output=True, text=True)
                            print(f"Converted to: {mp3_path}")
                            return mp3_path
                        except Exception as conv_err:
                            print(f"Conversion failed: {conv_err}, returning webm")
                            return audio_path
                    else:
                        print(f"MP3 already exists: {mp3_path}")
                        return mp3_path
                
                # Return webm if no conversion attempted
                return audio_path
    except Exception as e:
        print(f"Error listing directory: {e}")
    
    return None