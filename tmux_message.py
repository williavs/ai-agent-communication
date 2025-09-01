#!/usr/bin/env python3
"""
Portable tmux messaging system for AI agents

Usage:
  tmux-message <agent_name> <directory> <message>
  tmux-message --all <message>                    # Send to all panes
  tmux-message --pane <pane_id> <message>         # Send to specific pane
  tmux-message --command <command> --pane <id>    # Execute command in pane
  tmux-message --status                           # Show tmux status

Examples:
  tmux-message claude /home/user "Hello from opencode"
  tmux-message --all "System alert: Disk space low"
  tmux-message --pane %1 "Build complete"
  tmux-message --command "say 'Alert'" --pane %2
"""

import subprocess
import sys
import os


def get_tmux_panes():
    """Get list of all tmux panes with their details"""
    try:
        result = subprocess.run([
            'tmux', 'list-panes', '-a', '-F',
            '#{pane_id}:#{pane_current_command}:#{pane_current_path}'
        ], capture_output=True, text=True)

        if result.returncode != 0:
            return []

        panes = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue

            parts = line.split(':', 2)
            if len(parts) == 3:
                panes.append({
                    'pane_id': parts[0],
                    'command': parts[1],
                    'path': parts[2]
                })

        return panes

    except Exception as e:
        print(f"Error getting tmux panes: {e}", file=sys.stderr)
        return []


def find_agent(app_name, target_dir):
    """Find agent pane by application name and directory"""
    panes = get_tmux_panes()

    for pane in panes:
        if pane['command'] == app_name and pane['path'] == target_dir:
            return pane

    return None


def find_pane_by_id(pane_id):
    """Find pane by pane ID"""
    panes = get_tmux_panes()

    for pane in panes:
        if pane['pane_id'] == pane_id:
            return pane

    return None


def get_current_pane_info():
    """Get info about the current pane (sender)"""
    try:
        result = subprocess.run([
            'tmux', 'display-message', '-p',
            '#{pane_id}:#{pane_current_command}:#{pane_current_path}'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            parts = result.stdout.strip().split(':', 2)
            if len(parts) == 3:
                return {
                    'pane_id': parts[0],
                    'command': parts[1],
                    'path': parts[2]
                }
    except Exception as e:
        print(f"Error getting current pane info: {e}", file=sys.stderr)

    return None


def format_message_with_metadata(message, sender_info):
    """Format message with sender metadata"""
    if not sender_info:
        return message

    formatted = f"[FROM: {sender_info['command']} in {sender_info['path']} (pane {sender_info['pane_id']})]\n{message}"
    return formatted


def send_message_to_pane(pane_id, message):
    """Send message to specific tmux pane and press enter"""
    try:
        import time

        # Send the message
        result1 = subprocess.run([
            'tmux', 'send-keys', '-t', pane_id, message
        ])

        # Small delay to ensure message is processed
        time.sleep(0.1)

        # Press enter separately to make sure it happens
        result2 = subprocess.run([
            'tmux', 'send-keys', '-t', pane_id, 'C-m'
        ])

        # Additional delay and second enter press for reliability
        time.sleep(0.1)
        result3 = subprocess.run([
            'tmux', 'send-keys', '-t', pane_id, 'C-m'
        ])

        return result1.returncode == 0 and (result2.returncode == 0 or result3.returncode == 0)

    except Exception as e:
        print(f"Error sending message to pane {pane_id}: {e}", file=sys.stderr)
        return False


def send_to_all_panes(message):
    """Send message to all tmux panes"""
    panes = get_tmux_panes()
    if not panes:
        print("No tmux panes found", file=sys.stderr)
        return False

    success_count = 0
    for pane in panes:
        if send_message_to_pane(pane['pane_id'], message):
            success_count += 1

    print(f"Message sent to {success_count}/{len(panes)} panes")
    return success_count > 0


def execute_command_in_pane(pane_id, command):
    """Execute a command in a specific pane"""
    try:
        # Send the command followed by enter
        result = subprocess.run([
            'tmux', 'send-keys', '-t', pane_id, command, 'C-m'
        ])
        return result.returncode == 0
    except Exception as e:
        print(f"Error executing command in pane {pane_id}: {e}", file=sys.stderr)
        return False


def show_status():
    """Show tmux status information"""
    try:
        print("=== TMUX STATUS ===")

        # Show sessions
        result = subprocess.run(['tmux', 'list-sessions'], capture_output=True, text=True)
        if result.returncode == 0:
            print("\nSessions:")
            print(result.stdout.strip())
        else:
            print("No tmux sessions found")

        # Show panes
        panes = get_tmux_panes()
        if panes:
            print(f"\nPanes ({len(panes)} total):")
            for pane in panes:
                print(f"  {pane['pane_id']}: {pane['command']} @ {pane['path']}")
        else:
            print("No panes found")

    except Exception as e:
        print(f"Error getting tmux status: {e}", file=sys.stderr)


def main(argv=None):
    """Command-line interface"""
    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        print(__doc__)
        sys.exit(1)

    # Handle different command modes
    if argv[1] == '--all' and len(argv) >= 3:
        message = ' '.join(argv[2:])
        sender_info = get_current_pane_info()
        formatted_message = format_message_with_metadata(message, sender_info)
        success = send_to_all_panes(formatted_message)
        sys.exit(0 if success else 1)

    elif argv[1] == '--pane' and len(argv) >= 4:
        pane_id = argv[2]
        message = ' '.join(argv[3:])
        sender_info = get_current_pane_info()
        formatted_message = format_message_with_metadata(message, sender_info)
        success = send_message_to_pane(pane_id, formatted_message)
        if success:
            print(f"Message sent to pane {pane_id}")
        else:
            print(f"Failed to send message to pane {pane_id}", file=sys.stderr)
            sys.exit(1)

    elif argv[1] == '--command' and '--pane' in argv and len(argv) >= 5:
        try:
            pane_idx = argv.index('--pane')
            if pane_idx + 1 < len(argv):
                pane_id = argv[pane_idx + 1]
                command = ' '.join(argv[2:pane_idx])
                success = execute_command_in_pane(pane_id, command)
                if success:
                    print(f"Command executed in pane {pane_id}")
                else:
                    print(f"Failed to execute command in pane {pane_id}", file=sys.stderr)
                    sys.exit(1)
            else:
                print("Error: --pane requires a pane ID", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            print(f"Error parsing command arguments: {e}", file=sys.stderr)
            sys.exit(1)

    elif argv[1] == '--status':
        show_status()
        sys.exit(0)

    elif len(argv) >= 4:
        # Original format: tmux-message <agent> <directory> <message>
        app_name = argv[1]
        target_dir = argv[2]
        message = ' '.join(argv[3:])

        # Find the target agent
        agent = find_agent(app_name, target_dir)
        if not agent:
            print(f"Error: No {app_name} agent found in {target_dir}", file=sys.stderr)
            sys.exit(1)

        # Get sender info for metadata
        sender_info = get_current_pane_info()

        # Format message with sender metadata
        formatted_message = format_message_with_metadata(message, sender_info)

        # Send the message
        success = send_message_to_pane(agent['pane_id'], formatted_message)
        if success:
            print(f"Message sent to {app_name} in {target_dir}")
            if sender_info:
                print(f"From: {sender_info['command']} in {sender_info['path']} (pane {sender_info['pane_id']})")
        else:
            print(f"Failed to send message to {agent['pane_id']}", file=sys.stderr)
            sys.exit(1)

    else:
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()