import os
import io
from typing import Optional
from dotenv import load_dotenv
import whisper

from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

load_dotenv()

def transcribe_audio(audio_path: str, whisper_model: Optional[str] = None) -> str:
    model_name = whisper_model or os.getenv("WHISPER_MODEL", "base")
    
    # Ensure ffmpeg is available for Whisper
    ffmpeg_loc = os.getenv("FFMPEG_LOCATION") or os.getenv("FFMPEG_PATH")
    
    # Try common Windows locations if not explicitly set
    if not ffmpeg_loc:
        common_paths = [
            r"C:\ffmpeg-bin\bin",
            r"C:\ffmpeg\bin",
            r"C:\Program Files\ffmpeg\bin",
        ]
        for path in common_paths:
            if os.path.exists(os.path.join(path, "ffmpeg.exe")):
                ffmpeg_loc = path
                print(f"Found ffmpeg at: {ffmpeg_loc}")
                break
    
    if ffmpeg_loc:
        # If path points to exe, get the directory
        if ffmpeg_loc.lower().endswith(".exe"):
            ffmpeg_dir = os.path.dirname(ffmpeg_loc)
        else:
            ffmpeg_dir = ffmpeg_loc
        
        # Add to PATH temporarily for this process
        if ffmpeg_dir not in os.environ.get("PATH", ""):
            print(f"Adding ffmpeg to PATH: {ffmpeg_dir}")
            os.environ["PATH"] = f"{ffmpeg_dir};{os.environ.get('PATH', '')}"
    else:
        print("WARNING: ffmpeg not found. Whisper transcription may fail.")
        print("Please set FFMPEG_LOCATION environment variable or enter it in the sidebar.")
    
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path)
    return result.get("text", "").strip()

def tts_elevenlabs(text: str, voice: str = "Rachel") -> Optional[bytes]:
    api_key = os.getenv("ELEVEN_LABS_API_KEY")
    if not api_key:
        return None
    client = ElevenLabs(api_key=api_key)
    # Newer SDK
    audio = client.text_to_speech.convert(
        voice_id=None,  # default voice for provided name is handled via settings or voices list
        optimize_streaming_latency="0",
        output_format="mp3_44100_128" ,
        text=text,
        voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.8, style=0.0, use_speaker_boost=True),
        model_id="eleven_multilingual_v2"
    )
    # Stream bytes to buffer
    buf = io.BytesIO()
    for chunk in audio:
        if chunk:
            buf.write(chunk)
    return buf.getvalue()