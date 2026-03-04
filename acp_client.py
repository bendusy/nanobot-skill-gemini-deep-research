#!/usr/bin/env python3
"""
ACP (Agent Control Protocol) Client for Gemini CLI.

This script provides a programmatic interface to the Gemini CLI running in
`--experimental-acp` mode via standard input/output (stdio) using JSON-RPC.
It allows for structured, streaming interactions with the Gemini Sub-Agent.

Usage:
    python3 acp_client.py "Your prompt here"
"""

import subprocess
import json
import sys
import time
import threading

session_id = None
turn_completed = False
final_response = []

def read_output(process):
    """Read and process output from the ACP process."""
    global session_id, turn_completed, final_response
    while True:
        line = process.stdout.readline()
        if not line:
            break
        try:
            msg = json.loads(line.strip())
            
            # Extract session ID
            if msg.get("id") == 2 and "result" in msg:
                session_id = msg["result"].get("sessionId")
                
            # Handle streaming updates
            if msg.get("method") == "session/update" and "params" in msg:
                update = msg["params"]
                if update.get("type") == "agent_message_chunk":
                    chunk = update.get("content", {}).get("text", "")
                    if chunk:
                        sys.stdout.write(chunk)
                        sys.stdout.flush()
                        final_response.append(chunk)
                elif update.get("type") == "tool_call":
                    tool_name = update.get("toolCall", {}).get("name", "unknown_tool")
                    print(f"\n[Agent is using tool: {tool_name}]", file=sys.stderr)
                
            # Check if the prompt turn is completed
            if msg.get("id") == 3 and "result" in msg and msg["result"].get("stopReason") == "end_turn":
                turn_completed = True
                
        except json.JSONDecodeError:
            pass

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 acp_client.py \"Your prompt here\"")
        sys.exit(1)
        
    prompt_text = sys.argv[1]
    global session_id, turn_completed
    
    process = subprocess.Popen(
        ["/opt/homebrew/bin/gemini", "--experimental-acp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    reader_thread = threading.Thread(target=read_output, args=(process,), daemon=True)
    reader_thread.start()

    # Step 1: Initialize
    init_request = {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": 1, "clientInfo": {"name": "nanobot-acp-client", "version": "1.0.0"}}
    }
    process.stdin.write(json.dumps(init_request) + "\n")
    process.stdin.flush()
    time.sleep(1)

    # Step 2: New Session
    new_session_request = {
        "jsonrpc": "2.0", "id": 2, "method": "session/new",
        "params": {"cwd": "/tmp", "mcpServers": []}
    }
    process.stdin.write(json.dumps(new_session_request) + "\n")
    process.stdin.flush()
    
    timeout = 5
    while session_id is None and timeout > 0:
        time.sleep(1)
        timeout -= 1
        
    if not session_id:
        print("[-] Failed to initialize ACP session.", file=sys.stderr)
        process.terminate()
        return

    # Step 3: Prompt
    prompt_request = {
        "jsonrpc": "2.0", "id": 3, "method": "session/prompt",
        "params": {
            "sessionId": session_id,
            "prompt": [{"type": "text", "text": prompt_text}]
        }
    }
    process.stdin.write(json.dumps(prompt_request) + "\n")
    process.stdin.flush()

    try:
        while not turn_completed:
            time.sleep(0.5)
        print("\n")
        process.terminate()
    except KeyboardInterrupt:
        process.terminate()

if __name__ == "__main__":
    main()
