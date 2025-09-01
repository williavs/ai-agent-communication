# AI Agent Communication - Usage Examples

This directory contains practical examples of how to use the AI Agent Communication System in various scenarios.

## 🎯 Basic Usage Examples

### 1. Getting Started
```bash
# After installation, start the core services
python3 tts_server.py      # Terminal 1
python3 agent_discovery.py  # Terminal 2

# Test voice output
./bin/say "System initialized successfully"

# Check for available agents
./bin/search-agents
```

### 2. Voice Output Examples
```bash
# Basic voice messages
./bin/say "Build completed"
./bin/say "Tests passed" amy
./bin/say "Warning: High CPU usage" kathleen
./bin/say "Critical error detected" ryan

# Different voices for different message types
./bin/say "Good morning! System ready for development" amy
./bin/say "Build failed - check logs" kathleen
./bin/say "Security alert: Unauthorized access attempt" ryan
./bin/say "Debug: Variable X is undefined" danny
```

## 🔧 Development Workflow Integration

### 3. Build Notifications
```bash
# In your build script (build.sh)
#!/bin/bash

echo "Starting build..."
./bin/say "Build started"

if npm run build; then
    ./bin/say "Build completed successfully" amy
    ./bin/msg claude "Build finished - ready for testing"
else
    ./bin/say "Build failed - check logs" kathleen
    ./bin/msg opencode "Build error - needs attention"
fi
```

### 4. Test Automation
```bash
# In your test script (test.sh)
#!/bin/bash

echo "Running test suite..."
./bin/say "Starting test suite"

if npm test; then
    ./bin/say "All tests passed" amy
    ./bin/msg claude "Tests successful - ready for deployment"
else
    ./bin/say "Tests failed" kathleen
    ./bin/msg opencode "Test failures detected"
fi
```

### 5. Deployment Scripts
```bash
# Deploy script with voice feedback
#!/bin/bash

./bin/say "Starting deployment to production" kathleen

# Pre-deployment checks
if ./bin/health-check.sh; then
    ./bin/say "Health checks passed"

    # Actual deployment
    if docker-compose up -d; then
        ./bin/say "Deployment successful" amy
        ./bin/msg claude "Production deployment completed"
    else
        ./bin/say "Deployment failed" ryan
        ./bin/msg opencode "Deployment error - rollback initiated"
    fi
else
    ./bin/say "Health checks failed - aborting deployment" ryan
fi
```

## 💬 Inter-Agent Communication

### 6. Agent-to-Agent Messaging
```bash
# Send messages between AI agents
./bin/msg claude "Please review the new authentication module"
./bin/msg opencode "Database migration completed - verify data integrity"
./bin/msg homelab "System resources optimized"

# Using tmux_message directly for more control
python3 tmux_message.py claude /home/user/project "Code review needed"
python3 tmux_message.py opencode /home/user/docs "Documentation updated"
```

### 7. Broadcast Messages
```bash
# Send to all active agents
python3 tmux_message.py --all "System maintenance in 5 minutes"
python3 tmux_message.py --all "Emergency: Disk space critical"
python3 tmux_message.py --all "Meeting in 10 minutes"
```

### 8. Direct Pane Communication
```bash
# Send to specific tmux pane
python3 tmux_message.py --pane %1 "Focus on the authentication bug"
python3 tmux_message.py --pane %3 "Documentation review needed"

# Execute commands in specific panes
python3 tmux_message.py --command "git status" --pane %1
python3 tmux_message.py --command "./bin/say 'Command executed'" --pane %2
```

## 🔍 Monitoring and Alerts

### 9. System Monitoring
```bash
# CPU monitoring script
#!/bin/bash
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')

if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    ./bin/say "High CPU usage: ${CPU_USAGE}%" ryan
    ./bin/msg claude "CPU usage critical - investigate processes"
fi
```

### 10. Disk Space Monitoring
```bash
# Disk space alert
#!/bin/bash
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

if [ "$DISK_USAGE" -gt 90 ]; then
    ./bin/say "Disk space critical: ${DISK_USAGE} percent used" kathleen
    ./bin/msg opencode "Clean up disk space immediately"
elif [ "$DISK_USAGE" -gt 75 ]; then
    ./bin/say "Disk space warning: ${DISK_USAGE} percent used" danny
fi
```

### 11. Service Health Checks
```bash
# Health check script
#!/bin/bash

# Check TTS server
if curl -s http://localhost:9003/ > /dev/null; then
    echo "TTS server: OK"
else
    ./bin/say "TTS server is down" ryan
fi

# Check agent discovery
if curl -s http://localhost:9005/health > /dev/null; then
    echo "Agent discovery: OK"
else
    ./bin/say "Agent discovery server is down" ryan
fi

# Check for active agents
AGENT_COUNT=$(./bin/search-agents 2>/dev/null | grep -c "🤖")
if [ "$AGENT_COUNT" -gt 0 ]; then
    ./bin/say "Found ${AGENT_COUNT} active agents"
else
    ./bin/say "No active agents detected" danny
fi
```

## 🚀 Advanced Integration Examples

### 12. Git Hook Integration
```bash
# .git/hooks/post-commit
#!/bin/bash
./bin/say "Commit completed"
./bin/msg claude "New commit pushed - review changes"
```

### 13. CI/CD Pipeline Integration
```bash
# In your CI/CD pipeline
#!/bin/bash

echo "Starting CI pipeline..."
./bin/say "CI pipeline started"

# Run tests
if npm test; then
    ./bin/say "Tests passed - building"
    if npm run build; then
        ./bin/say "Build successful - deploying"
        # Deployment logic here
        ./bin/say "Deployment completed" amy
    else
        ./bin/say "Build failed" kathleen
        exit 1
    fi
else
    ./bin/say "Tests failed" ryan
    exit 1
fi
```

### 14. Development Environment Setup
```bash
# Setup script for new development environment
#!/bin/bash

echo "Setting up development environment..."

# Start services
python3 tts_server.py &
TTS_PID=$!

python3 agent_discovery.py &
DISCOVERY_PID=$!

# Wait for services to start
sleep 3

# Test system
./bin/say "Development environment ready" amy
./bin/search-agents

echo "Services started. Press Ctrl+C to stop."
trap "kill $TTS_PID $DISCOVERY_PID" INT
wait
```

### 15. Multi-Agent Collaboration
```bash
# Complex workflow with multiple agents
#!/bin/bash

# Start feature development
./bin/say "Starting feature development" amy
./bin/msg claude "Begin implementing user authentication"

# Wait for implementation
sleep 300  # 5 minutes

# Code review phase
./bin/say "Code review time" kathleen
./bin/msg opencode "Please review authentication implementation"

# Testing phase
sleep 600  # 10 minutes
./bin/say "Testing phase" danny
./bin/msg claude "Run comprehensive tests"

# Deployment
sleep 300  # 5 minutes
./bin/say "Ready for deployment" amy
./bin/msg homelab "Deploy authentication feature to staging"
```

## 🔧 API Usage Examples

### 16. Direct TTS API Usage
```python
# Python script using TTS API
import requests

def speak_message(message, voice="amy"):
    """Send message to TTS server"""
    try:
        response = requests.get(
            f"http://localhost:9003/play",
            params={"text": message, "voice": voice}
        )
        return response.status_code == 200
    except:
        return False

# Usage
speak_message("Build completed successfully", "amy")
speak_message("Error detected", "kathleen")
```

### 17. Agent Discovery API
```python
# Python script for agent discovery
import requests
import json

def get_active_agents():
    """Get list of active agents"""
    try:
        response = requests.get("http://localhost:9005/agents")
        if response.status_code == 200:
            data = response.json()
            return data.get("agents", {})
    except:
        pass
    return {}

def send_to_agent(agent_name, message):
    """Send message to specific agent"""
    agents = get_active_agents()
    if agent_name in agents and agents[agent_name]:
        # Use tmux_message.py or direct tmux commands
        import subprocess
        pane_id = agents[agent_name][0]["pane"]
        subprocess.run([
            "python3", "tmux_message.py",
            "--pane", pane_id, message
        ])

# Usage
agents = get_active_agents()
print(f"Active agents: {list(agents.keys())}")

send_to_agent("claude", "Hello from Python script")
```

### 18. Custom Notification System
```python
# Custom notification system
import time
import subprocess

class AgentNotifier:
    def __init__(self):
        self.tts_host = "localhost"
        self.tts_port = 9003

    def speak(self, message, voice="amy"):
        """Voice notification"""
        subprocess.run([
            "./bin/say", message, voice
        ], capture_output=True)

    def message_agent(self, agent, message):
        """Send message to agent"""
        subprocess.run([
            "./bin/msg", agent, message
        ], capture_output=True)

    def notify_build_status(self, status, project="main"):
        """Notify about build status"""
        if status == "success":
            self.speak(f"Build successful for {project}", "amy")
            self.message_agent("claude", f"✅ Build completed: {project}")
        elif status == "failure":
            self.speak(f"Build failed for {project}", "kathleen")
            self.message_agent("opencode", f"❌ Build failed: {project}")
        elif status == "started":
            self.speak(f"Build started for {project}", "danny")

# Usage
notifier = AgentNotifier()
notifier.notify_build_status("started", "authentication-service")
time.sleep(60)  # Simulate build time
notifier.notify_build_status("success", "authentication-service")
```

## 🎮 Interactive Examples

### 19. Development Dashboard
```bash
# Interactive development dashboard
#!/bin/bash

while true; do
    clear
    echo "=== AI Agent Development Dashboard ==="
    echo ""

    # Show active agents
    echo "🤖 Active Agents:"
    ./bin/search-agents
    echo ""

    # Show system status
    echo "🖥️  System Status:"
    echo "   CPU: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')%"
    echo "   Memory: $(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')%"
    echo "   Disk: $(df / | tail -1 | awk '{print $5}')"
    echo ""

    # Menu
    echo "Commands:"
    echo "  1. Send message to Claude"
    echo "  2. Send message to OpenCode"
    echo "  3. Voice test"
    echo "  4. System health check"
    echo "  q. Quit"
    echo ""

    read -n 1 -s choice
    case $choice in
        1) ./bin/msg claude "Message from dashboard" ;;
        2) ./bin/msg opencode "Message from dashboard" ;;
        3) ./bin/say "Voice test from dashboard" ;;
        4) ./bin/say "Running health check" && sleep 2 ;;
        q) break ;;
    esac

    sleep 5
done
```

### 20. Emergency Alert System
```bash
# Emergency alert system
#!/bin/bash

# Define emergency conditions
check_emergency() {
    # High CPU
    CPU=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    if (( $(echo "$CPU > 95" | bc -l) )); then
        ./bin/say "EMERGENCY: CPU usage at ${CPU} percent" ryan
        ./bin/msg claude "URGENT: CPU critical - immediate action required"
        return 0
    fi

    # Low disk space
    DISK=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$DISK" -gt 98 ]; then
        ./bin/say "EMERGENCY: Disk space at ${DISK} percent" ryan
        ./bin/msg opencode "URGENT: Disk full - clean up immediately"
        return 0
    fi

    # High memory usage
    MEM=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ "$MEM" -gt 95 ]; then
        ./bin/say "EMERGENCY: Memory usage at ${MEM} percent" ryan
        ./bin/msg homelab "URGENT: Memory critical - check processes"
        return 0
    fi

    return 1
}

# Monitor continuously
echo "Emergency monitoring active..."
while true; do
    if check_emergency; then
        sleep 30  # Wait before next check after alert
    else
        sleep 60  # Normal check interval
    fi
done
```

These examples demonstrate the versatility of the AI Agent Communication System for various development, monitoring, and automation scenarios. Feel free to adapt them to your specific workflow!