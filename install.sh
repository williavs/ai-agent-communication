#!/bin/bash
# AI Agent Communication System - Installation Script
# This script sets up the complete AI agent communication system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VOICES_DIR="$SCRIPT_DIR/voices"

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)

# System dependency installation
install_system_deps() {
    log_info "Installing system dependencies..."

    if [[ "$OS" == "linux" ]]; then
        # Detect package manager
        if command_exists apt-get; then
            log_info "Using apt-get..."
            sudo apt-get update
            sudo apt-get install -y curl jq tmux python3 python3-pip python3-venv

            # Audio dependencies
            sudo apt-get install -y pulseaudio-utils alsa-utils sox ffmpeg

        elif command_exists dnf; then
            log_info "Using dnf..."
            sudo dnf install -y curl jq tmux python3 python3-pip

            # Audio dependencies
            sudo dnf install -y pulseaudio-utils alsa-utils sox ffmpeg

        elif command_exists pacman; then
            log_info "Using pacman..."
            sudo pacman -S --noconfirm curl jq tmux python python-pip

            # Audio dependencies
            sudo pacman -S --noconfirm pulseaudio alsa-utils sox ffmpeg

        else
            log_warning "Unknown package manager. Please install manually: curl, jq, tmux, python3, pip"
        fi

    elif [[ "$OS" == "macos" ]]; then
        if command_exists brew; then
            log_info "Using Homebrew..."
            brew install curl jq tmux python3

            # Audio dependencies (macOS has built-in audio support)
            log_info "macOS detected - using built-in audio support"
        else
            log_warning "Homebrew not found. Please install Homebrew and run: brew install curl jq tmux python3"
        fi
    else
        log_warning "Unsupported OS: $OS. Please install dependencies manually."
    fi
}

# Python environment setup
setup_python_env() {
    log_info "Setting up Python environment..."

    # Check Python version
    if ! command_exists python3; then
        log_error "Python 3 not found. Please install Python 3 first."
        exit 1
    fi

    python3 --version

    # Install Python dependencies
    log_info "Installing Python dependencies..."
    pip3 install --user -r "$SCRIPT_DIR/requirements.txt"

    log_success "Python dependencies installed"
}

# Voice model setup
setup_voice_models() {
    log_info "Setting up voice models..."

    mkdir -p "$VOICES_DIR"

    # Download default voice model (amy)
    VOICE_MODEL="en_US-amy-medium.onnx"
    VOICE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx"

    if [ ! -f "$VOICES_DIR/$VOICE_MODEL" ]; then
        log_info "Downloading default voice model (amy)..."
        if curl -L -o "$VOICES_DIR/$VOICE_MODEL" "$VOICE_URL"; then
            log_success "Voice model downloaded: $VOICE_MODEL"
        else
            log_warning "Failed to download voice model. You can download it manually later."
        fi
    else
        log_info "Voice model already exists: $VOICE_MODEL"
    fi
}

# Make scripts executable
setup_scripts() {
    log_info "Setting up scripts..."

    # Make Python scripts executable
    chmod +x "$SCRIPT_DIR"/*.py
    chmod +x "$SCRIPT_DIR/bin"/*

    log_success "Scripts are now executable"
}

# Create desktop shortcuts (optional)
create_shortcuts() {
    if [[ "$OS" == "linux" ]]; then
        log_info "Creating desktop shortcuts..."

        DESKTOP_DIR="$HOME/.local/share/applications"

        mkdir -p "$DESKTOP_DIR"

        # TTS Server shortcut
        cat > "$DESKTOP_DIR/ai-agent-tts.desktop" << EOF
[Desktop Entry]
Name=AI Agent TTS Server
Comment=Start the AI Agent Text-to-Speech Server
Exec=$SCRIPT_DIR/tts_server.py
Icon=multimedia
Terminal=true
Type=Application
Categories=Utility;
EOF

        # Agent Discovery shortcut
        cat > "$DESKTOP_DIR/ai-agent-discovery.desktop" << EOF
[Desktop Entry]
Name=AI Agent Discovery
Comment=Start the AI Agent Discovery Server
Exec=$SCRIPT_DIR/agent_discovery.py
Icon=network
Terminal=true
Type=Application
Categories=Utility;
EOF

        log_success "Desktop shortcuts created"
    fi
}

# Post-installation instructions
show_instructions() {
    echo ""
    log_success "Installation completed successfully!"
    echo ""
    echo "🚀 Getting Started:"
    echo ""
    echo "1. Start the TTS Server:"
    echo "   $SCRIPT_DIR/tts_server.py"
    echo ""
    echo "2. Start the Agent Discovery Server:"
    echo "   $SCRIPT_DIR/agent_discovery.py"
    echo ""
    echo "3. Test voice output:"
    echo "   $SCRIPT_DIR/bin/say 'Hello, AI Agent Communication System is ready!'"
    echo ""
    echo "4. Discover available agents:"
    echo "   $SCRIPT_DIR/bin/search-agents"
    echo ""
    echo "5. Send messages between agents:"
    echo "   $SCRIPT_DIR/bin/msg claude 'Hello from terminal'"
    echo ""
    echo "📚 Available Scripts:"
    echo "   • tmux_message.py    - Send messages between tmux panes"
    echo "   • tts_server.py     - Text-to-speech server"
    echo "   • agent_discovery.py - Agent discovery server"
    echo "   • bin/say            - Voice output utility"
    echo "   • bin/search-agents  - Find active agents"
    echo "   • bin/msg            - Easy messaging tool"
    echo ""
    echo "🔧 Configuration:"
    echo "   • Edit config.json to customize settings"
    echo "   • Set environment variables for custom servers:"
    echo "     TTS_HOST, TTS_PORT, DISCOVERY_HOST, DISCOVERY_PORT"
    echo ""
    echo "📖 For more information, see README.md"
}

# Main installation process
main() {
    echo ""
    log_info "AI Agent Communication System - Installation"
    echo "=============================================="
    echo ""

    # Check if we're in the right directory
    if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
        log_error "requirements.txt not found. Please run this script from the ai-agent-communication directory."
        exit 1
    fi

    log_info "Detected OS: $OS"
    log_info "Installation directory: $SCRIPT_DIR"

    # Installation steps
    install_system_deps
    setup_python_env
    setup_voice_models
    setup_scripts
    create_shortcuts

    show_instructions
}

# Run main function
main "$@"