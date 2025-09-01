# Slaygent Communication System

A complete, portable communication system for AI coding assistants and agents. Enables seamless messaging between tmux panes, text-to-speech output, and agent discovery across your development environment.



- **Cross-Agent Messaging**: AI CLI TOOLS Send messages between AI CLI Tools in different tmux panes
- **Text-to-Speech**: Voice output with multiple neural voices
- **Agent Discovery**: Automatically detect and list active AI agents
- **Easy Installation**: One-command setup with comprehensive install script
- **Flexible Configuration**: Environment variables and config files

## 📦 Quick Start

### 1. Clone or Download
```bash
git clone <your-repo-url>
cd ai-agent-communication
```

### 2. Install Dependencies
```bash
./install.sh
```
This will install all required system and Python dependencies automatically.

### 3. Start the Services
```bash
# Terminal 1: Start TTS Server
python3 tts_server.py

# Terminal 2: Start Agent Discovery
python3 agent_discovery.py
```

### 4. Test the System
```bash
# Test voice output
./bin/say "AI Agent Communication System is ready!"

# Discover available agents
./bin/search-agents

# Send a message (if agents are running)
./bin/msg claude "Hello from terminal"
```

## 🏗️ Architecture

```
ai-agent-communication/
├── tmux_message.py      # Core messaging between tmux panes
├── tts_server.py       # FastAPI TTS server with neural voices
├── agent_discovery.py   # HTTP server for agent detection
├── bin/
│   ├── say              # Voice output utility
│   ├── search-agents    # Agent discovery tool
│   └── msg              # Easy messaging interface
├── voices/              # Voice model storage
├── config.json          # Configuration file
├── requirements.txt     # Python dependencies
├── install.sh          # Installation script
└── README.md           # This file
```

## 🎯 Core Components

### TMUX Message System (`tmux_message.py`)
Send messages between AI agents in tmux panes with automatic metadata.

```bash
# Send to specific agent
python3 tmux_message.py claude /home/user/project "Build completed"

# Send to all panes
python3 tmux_message.py --all "System maintenance in 5 minutes"

# Send to specific pane
python3 tmux_message.py --pane %1 "Direct message"

# Execute command in pane
python3 tmux_message.py --command "say 'Alert'" --pane %2
```

### Text-to-Speech Server (`tts_server.py`)
FastAPI server providing neural TTS with multiple voice models.

```bash
# Start server
python3 tts_server.py

# API Endpoints
GET  /speak?text=Hello%20world&voice=amy    # Download audio file
GET  /play?text=Hello%20world&voice=danny  # Play immediately
GET  /voices                               # List available voices
GET  /                                    # Health check
```

### Agent Discovery Server (`agent_discovery.py`)
HTTP server that detects active AI agents in tmux sessions.

```bash
# Start server
python3 agent_discovery.py

# API Endpoints
GET  /agents   # List all detected agents
GET  /health   # Health check
```

### CLI Tools

#### Voice Output (`bin/say`)
```bash
# Basic usage
./bin/say "System is online"

# With specific voice
./bin/say "Alert detected" kathleen

# Available voices: amy, danny, kathleen, ryan, lessac, libritts
```

#### Agent Discovery (`bin/search-agents`)
```bash
./bin/search-agents
# Output:
# 🤖 claude:
#    • %1 in /home/user/project
# 🤖 opencode:
#    • %3 in /home/user/docs
```

#### Easy Messaging (`bin/msg`)
```bash
# Send message to agent
./bin/msg claude "Hello from terminal"
./bin/msg opencode "Status check"
```

## ⚙️ Configuration

### Environment Variables
```bash
# TTS Server
TTS_HOST=localhost          # Server hostname
TTS_PORT=9003              # Server port
TTS_URL=http://localhost:9003  # Full URL (overrides HOST/PORT)

# Agent Discovery
DISCOVERY_HOST=localhost   # Server hostname
DISCOVERY_PORT=9005        # Server port
DISCOVERY_URL=http://localhost:9005  # Full URL (overrides HOST/PORT)
```

### Configuration File (`config.json`)
```json
{
  "host": "0.0.0.0",
  "port": 9003,
  "default_voice": "amy",
  "voice_dir": "./voices",
  "voice_models": {
    "amy": "en_US-amy-medium.onnx",
    "danny": "en_US-danny-low.onnx",
    "kathleen": "en_US-kathleen-low.onnx",
    "ryan": "en_US-ryan-medium.onnx",
    "lessac": "en_US-lessac-medium.onnx"
  },
  "audio_backend": "auto",
  "silence_padding": 0.2
}
```

## 🔧 Manual Installation

If the install script doesn't work for your system:

### System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get install curl jq tmux python3 python3-pip pulseaudio-utils alsa-utils sox ffmpeg

# Fedora/CentOS
sudo dnf install curl jq tmux python3 python3-pip pulseaudio-utils alsa-utils sox ffmpeg

# Arch Linux
sudo pacman -S curl jq tmux python python-pip pulseaudio alsa-utils sox ffmpeg

# macOS
brew install curl jq tmux python3
```

### Python Dependencies
```bash
pip3 install -r requirements.txt
```

### Voice Models
```bash
mkdir -p voices
# Download voice models from https://huggingface.co/rhasspy/piper-voices
```

## 🎤 Voice Models

The system supports multiple neural TTS voices:

- **amy**: Natural female voice (medium quality) - Default
- **danny**: Clear male voice (low quality, fast)
- **kathleen**: Professional female voice (low quality, fast)
- **ryan**: Deep male voice (medium quality)
- **lessac**: Alternative voice (medium quality)
- **libritts**: High quality voice (slower)

Download additional voices from [Hugging Face](https://huggingface.co/rhasspy/piper-voices).

## 🔍 Troubleshooting

### TTS Server Issues
```bash
# Check if server is running
curl http://localhost:9003/

# Test voice output
./bin/say "Test message"
```

### Agent Discovery Issues
```bash
# Check if server is running
curl http://localhost:9005/health

# Test agent detection
./bin/search-agents
```

### TMUX Issues
```bash
# Check tmux version
tmux -V

# List active sessions
tmux list-sessions

# List panes in current session
tmux list-panes
```

### Common Problems
1. **"No audio player found"**: Install pulseaudio-utils or alsa-utils
2. **"Voice model not found"**: Run `./install.sh` to download default voice
3. **"Agent not found"**: Make sure AI agents are running in tmux panes
4. **"Permission denied"**: Run `chmod +x bin/* *.py`

## 🤝 Integration Examples

### With Claude Code
```bash
# In Claude Code tmux pane
tmux send-keys -t %1 "I received: $(cat /tmp/message.txt)" C-m
```

### With Development Workflow
```bash
# Build completion notification
./bin/say "Build completed successfully" && ./bin/msg claude "Ready for testing"

# Error alerts
./bin/say "Build failed" kathleen && ./bin/msg opencode "Check build logs"
```

### System Monitoring
```bash
# CPU alert
./bin/say "High CPU usage detected" ryan

# Disk space warning
./bin/say "Disk space low" kathleen
```

## 📋 API Reference

### TMUX Message API
```python
from tmux_message import send_message_to_pane, get_tmux_panes

# Get all panes
panes = get_tmux_panes()

# Send message
success = send_message_to_pane("%1", "Hello from Python")
```

### TTS Server API
```python
import requests

# Generate speech
response = requests.get("http://localhost:9003/speak?text=Hello&voice=amy")
with open("speech.wav", "wb") as f:
    f.write(response.content)

# Play immediately
requests.get("http://localhost:9003/play?text=Hello&voice=danny")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [Piper TTS](https://github.com/rhasspy/piper) for neural voice synthesis
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [tmux](https://github.com/tmux/tmux) for terminal multiplexing

---

**Made with ❤️ for AI agent communication**
