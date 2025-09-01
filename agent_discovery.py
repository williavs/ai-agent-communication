#!/usr/bin/env python3
"""
AI Agent Communication - Agent Discovery Server
Ultra-simple HTTP server for live detection of AI agent instances in tmux sessions.

Usage: python agent_discovery.py [port]

Default port: 9005
"""

import subprocess
import json
import time
import sys
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default port
DEFAULT_PORT = 9005

def detect_agents(tmux_output):
    """Parse tmux output into agent data structure"""
    agents = {}

    for line in tmux_output.strip().split('\n'):
        if line.strip():  # Skip empty lines
            parts = line.split(':', 2)
            if len(parts) == 3:
                pane, cmd, path = parts
                if cmd not in agents:
                    agents[cmd] = []
                agents[cmd].append({
                    'pane': pane,
                    'path': path.strip(),
                    'command': cmd
                })

    return agents

def get_live_agents():
    """Get current agent instances from tmux"""
    try:
        result = subprocess.run([
            'tmux', 'list-panes', '-a', '-F',
            '#{pane_id}:#{pane_current_command}:#{pane_current_path}'
        ], capture_output=True, text=True, timeout=2)

        if result.returncode == 0:
            return detect_agents(result.stdout)
        else:
            logger.warning(f"tmux command failed: {result.stderr}")
            return {}

    except subprocess.TimeoutExpired:
        logger.error("tmux command timed out")
        return {}
    except FileNotFoundError:
        logger.error("tmux not found - is it installed?")
        return {}
    except Exception as e:
        logger.error(f"Error getting live agents: {e}")
        return {}

class AgentHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

    def do_GET(self):
        if self.path == '/agents':
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                data = {
                    'agents': get_live_agents(),
                    'timestamp': time.time(),
                    'server': 'AI Agent Communication - Discovery Server'
                }
                self.wfile.write(json.dumps(data, indent=2).encode())
            except Exception as e:
                logger.error(f"Error handling /agents request: {e}")
                self.send_response(500)
                self.end_headers()

        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            health_data = {
                'status': 'healthy',
                'timestamp': time.time(),
                'service': 'Agent Discovery Server'
            }
            self.wfile.write(json.dumps(health_data).encode())

        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_data = {
                'error': 'Not found',
                'available_endpoints': ['/agents', '/health']
            }
            self.wfile.write(json.dumps(error_data).encode())

def main():
    """Main entry point"""
    port = DEFAULT_PORT

    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            logger.error(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)

    server_address = ('127.0.0.1', port)

    try:
        httpd = HTTPServer(server_address, AgentHandler)
        logger.info(f"🚀 Agent Discovery Server starting on http://127.0.0.1:{port}")
        logger.info("📡 Available endpoints:")
        logger.info(f"   GET /agents  - List all detected agents")
        logger.info(f"   GET /health  - Health check")
        logger.info("🛑 Press Ctrl+C to stop")

        httpd.serve_forever()

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()