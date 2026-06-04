import os
import tempfile
import subprocess
from faster_whisper import WhisperModel

# Load once and reuse
model = WhisperModel(
    "small",
    device="cpu",  # GitHub Actions runners usually don't have GPU
    compute_type="int8",
    download_root=os.path.expanduser("~/.cache/huggingface/hub"),
    token=os.getenv("HF_TOKEN")
)

def transcribe_video(video_path):
    """
    Extract audio from video, transcribe it,
    remove temp audio file, and return transcript.
    """

    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as tmp_audio:

        audio_path = tmp_audio.name

    try:
        # Extract audio
        subprocess.run(
            [
                "ffmpeg",
                "-i", video_path,
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                audio_path,
                "-y"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        # Transcribe
        segments, info = model.transcribe(
            audio_path,
            beam_size=5
        )

        transcript = " ".join(
            segment.text.strip()
            for segment in segments
        )

        return transcript

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
