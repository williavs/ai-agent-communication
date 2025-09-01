#!/usr/bin/env python3
"""
AI Agent Communication - TTS Server
A lightweight FastAPI server that provides text-to-speech capabilities
for AI coding tools and agent communication systems.

Usage: python tts_server.py
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import uvicorn
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration - make paths relative to script location
SCRIPT_DIR = Path(__file__).parent.absolute()
DEFAULT_CONFIG_FILE = SCRIPT_DIR / 'config.json'
DEFAULT_VOICE_DIR = SCRIPT_DIR / 'voices'

# Global variables
voices = {}
config = {}

def load_config():
    """Load configuration from file or use defaults"""
    global config

    # Check for config file in script directory first, then environment
    config_file = os.environ.get('TTS_CONFIG', str(DEFAULT_CONFIG_FILE))

    default_config = {
        "host": "0.0.0.0",
        "port": 9003,
        "default_voice": "amy",
        "voice_dir": str(DEFAULT_VOICE_DIR),
        "voice_models": {
            "amy": "en_US-amy-medium.onnx",
            "danny": "en_US-danny-low.onnx",
            "kathleen": "en_US-kathleen-low.onnx",
            "libritts": "en_US-libritts-high.onnx",
            "lessac": "en_US-lessac-medium.onnx",
            "ryan": "en_US-ryan-medium.onnx"
        },
        "audio_backend": "auto",  # auto, paplay, aplay, sox, or ffplay
        "silence_padding": 0.2  # seconds of silence to add
    }

    if Path(config_file).exists():
        try:
            with open(config_file, 'r') as f:
                loaded_config = json.load(f)
                config = {**default_config, **loaded_config}
                logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            logger.warning(f"Failed to load config file: {e}, using defaults")
            config = default_config
    else:
        config = default_config
        logger.info("Using default configuration")

    return config

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models on startup"""
    global voices, config

    config = load_config()

    try:
        # Try to import piper
        try:
            from piper import PiperVoice
        except ImportError:
            logger.error("Piper not installed! Please run: pip install piper-tts")
            logger.error("Or use the install.sh script")
            sys.exit(1)

        voice_dir = Path(config["voice_dir"])
        voice_models = config["voice_models"]

        if not voice_dir.exists():
            logger.warning(f"Voice directory {voice_dir} does not exist, creating it...")
            voice_dir.mkdir(parents=True, exist_ok=True)

        # Load available voices
        for name, filename in voice_models.items():
            voice_file = voice_dir / filename
            if voice_file.exists():
                logger.info(f"Loading {name} voice model...")
                try:
                    voices[name] = PiperVoice.load(str(voice_file))
                    logger.info(f"✓ {name} loaded successfully!")
                except Exception as e:
                    logger.error(f"Failed to load {name}: {e}")
            else:
                logger.warning(f"Voice model not found: {voice_file}")
                logger.info(f"Download it with: ./install.sh download-voice {name}")

        if not voices:
            logger.error("No voice models loaded! Please install at least one voice model.")
            logger.info("Run: ./install.sh download-voice amy")
        else:
            logger.info(f"✓ Loaded {len(voices)} voice(s): {', '.join(voices.keys())}")

    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        sys.exit(1)

    yield

    logger.info("TTS Server shutting down...")

app = FastAPI(
    title="AI Agent Communication - TTS Server",
    description="TTS API for AI Agent Communication Systems",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Health check and status"""
    return {
        "service": "AI Agent Communication - TTS Server",
        "status": "running",
        "models_loaded": len(voices),
        "available_voices": list(voices.keys()),
        "default_voice": config.get("default_voice", "amy"),
        "endpoints": {
            "speak": "/speak?text=your+message&voice=amy",
            "play": "/play?text=your+message&voice=danny",
            "voices": "/voices"
        }
    }

@app.get("/voices")
async def list_voices():
    """List available voices with details"""
    return {
        "available": list(voices.keys()),
        "default": config.get("default_voice", "amy"),
        "descriptions": {
            "amy": "Natural female voice (medium quality)",
            "danny": "Clear male voice (low quality, fast)",
            "kathleen": "Professional female voice (low quality, fast)",
            "ryan": "Deep male voice (medium quality)",
            "lessac": "Alternative voice (medium quality)",
            "libritts": "High quality voice (slower)"
        }
    }

def get_audio_player():
    """Detect and return the best available audio player"""
    backend = config.get("audio_backend", "auto")

    if backend != "auto":
        return backend

    # Try to detect available audio players
    import subprocess

    players = ["paplay", "aplay", "sox", "ffplay", "afplay"]  # afplay for macOS

    for player in players:
        try:
            result = subprocess.run(["which", player], capture_output=True)
            if result.returncode == 0:
                logger.info(f"Using audio backend: {player}")
                return player
        except:
            continue

    logger.warning("No audio player found! Install pulseaudio-utils, alsa-utils, sox, or ffmpeg")
    return None

def play_audio_file(file_path):
    """Play audio file using the best available method"""
    player = get_audio_player()

    if not player:
        raise Exception("No audio player available")

    import subprocess

    # Build the command based on the player
    if player == "paplay":
        cmd = ["paplay", file_path]
    elif player == "aplay":
        cmd = ["aplay", "-q", file_path]
    elif player == "sox":
        cmd = ["play", "-q", file_path]
    elif player == "ffplay":
        cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", file_path]
    elif player == "afplay":  # macOS
        cmd = ["afplay", file_path]
    else:
        cmd = [player, file_path]

    result = subprocess.run(cmd, capture_output=True, timeout=30)

    if result.returncode != 0:
        error_msg = result.stderr.decode() if result.stderr else "Unknown error"
        raise Exception(f"Audio playback failed: {error_msg}")

    return True

@app.get("/speak")
async def speak_text(
    text: str = Query(..., description="Text to convert to speech"),
    voice: str = Query(default=None, description="Voice to use")
):
    """Generate speech and return audio file"""
    voice_name = voice or config.get("default_voice", "amy")

    if not voices:
        raise HTTPException(status_code=503, detail="No voice models loaded")

    if voice_name not in voices:
        available = list(voices.keys())
        raise HTTPException(status_code=400, detail=f"Voice '{voice_name}' not available. Choose from: {available}")

    selected_voice = voices[voice_name]

    try:
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name

        # Generate speech with optional silence padding
        import wave

        # Generate speech
        temp_speech_path = temp_path + ".speech"
        with wave.open(temp_speech_path, 'wb') as wav_file:
            selected_voice.synthesize_wav(text, wav_file)

        # Read the generated speech
        with wave.open(temp_speech_path, 'rb') as speech_wav:
            params = speech_wav.getparams()
            frames = speech_wav.readframes(params.nframes)

        # Add silence padding if configured
        silence_duration = config.get("silence_padding", 0.2)
        if silence_duration > 0:
            sample_rate = params.framerate
            silence_samples = int(sample_rate * silence_duration)
            silence_buffer = b'\x00' * (silence_samples * params.sampwidth * params.nchannels)
            frames = silence_buffer + frames

        # Write final audio
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setparams(params)
            wav_file.writeframes(frames)

        # Clean up
        try:
            os.unlink(temp_speech_path)
        except:
            pass

        return FileResponse(
            temp_path,
            media_type='audio/wav',
            filename='speech.wav'
        )

    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")

@app.get("/play")
async def play_text(
    text: str = Query(..., description="Text to speak and play locally"),
    voice: str = Query(default=None, description="Voice to use")
):
    """Generate speech and play it locally"""
    voice_name = voice or config.get("default_voice", "amy")

    if not voices:
        raise HTTPException(status_code=503, detail="No voice models loaded")

    if voice_name not in voices:
        available = list(voices.keys())
        raise HTTPException(status_code=400, detail=f"Voice '{voice_name}' not available. Choose from: {available}")

    selected_voice = voices[voice_name]

    try:
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name

        # Generate speech with optional silence padding
        import wave

        # Generate speech
        temp_speech_path = temp_path + ".speech"
        with wave.open(temp_speech_path, 'wb') as wav_file:
            selected_voice.synthesize_wav(text, wav_file)

        # Read the generated speech
        with wave.open(temp_speech_path, 'rb') as speech_wav:
            params = speech_wav.getparams()
            frames = speech_wav.readframes(params.nframes)

        # Add silence padding if configured
        silence_duration = config.get("silence_padding", 0.2)
        if silence_duration > 0:
            sample_rate = params.framerate
            silence_samples = int(sample_rate * silence_duration)
            silence_buffer = b'\x00' * (silence_samples * params.sampwidth * params.nchannels)
            frames = silence_buffer + frames

        # Write final audio
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setparams(params)
            wav_file.writeframes(frames)

        # Clean up temp speech file
        try:
            os.unlink(temp_speech_path)
        except:
            pass

        # Play the audio
        play_audio_file(temp_path)

        # Clean up
        try:
            os.unlink(temp_path)
        except:
            pass

        return {"status": "played", "text": text, "voice": voice_name}

    except Exception as e:
        logger.error(f"Playback failed: {e}")
        raise HTTPException(status_code=500, detail=f"Playback failed: {str(e)}")

def main():
    """Main entry point"""
    config = load_config()

    print("🚀 Starting AI Agent Communication - TTS Server...")
    print(f"📡 API will be available at: http://{config['host']}:{config['port']}")
    print("🎯 Usage examples:")
    print(f"   curl 'http://localhost:{config['port']}/speak?text=Hello%20world'")
    print(f"   curl 'http://localhost:{config['port']}/play?text=Hello%20world'")
    print(f"   say 'Hello world'  # Using the CLI tool")
    print()

    uvicorn.run(
        app,
        host=config["host"],
        port=config["port"],
        log_level="info"
    )

if __name__ == "__main__":
    main()