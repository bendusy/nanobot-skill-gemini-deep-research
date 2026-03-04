#!/usr/bin/env python3
"""
Experimental ACP (Agent Control Protocol) Test Snippet for Gemini CLI.

This script demonstrates how to communicate with the Gemini CLI running in
`--experimental-acp` mode via standard input/output (stdio) using JSON-RPC.

It performs a complete flow:
1. Initialize the ACP connection
2. Create a new session
3. Send a prompt and stream the response (including tool calls and text chunks)
"""

import subprocess
import json
import sys
import time
import threading

session_id = None
turn_completed = False

def read_output(process):
    """Read and print output from the ACP process."""
    global session_id, turn_completed
    while True:
        line = process.stdout.readline()
        if not line:
            break
        try:
            msg = json.loads(line.strip())
            
            # Print the raw JSON response for debugging
            print(f"[ACP Response] {json.dumps(msg, indent=2)}")
            
            # Extract session ID if this is the response to session/new
            if msg.get("id") == 2 and "result" in msg:
                session_id = msg["result"].get("sessionId")
                print(f"\n[+] Extracted Session ID: {session_id}\n")
                
            # Check if the prompt turn is completed
            if msg.get("id") == 3 and "result" in msg and msg["result"].get("stopReason") == "end_turn":
                print("\n[+] Prompt turn completed successfully.")
                turn_completed = True
                
        except json.JSONDecodeError:
            print(f"[Raw Output] {line.strip()}")

def main():
    global session_id, turn_completed
    print("Starting Gemini CLI in ACP mode...")
    
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
    time.sleep(2)

    # Step 1: Initialize the ACP connection
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": 1,
            "clientInfo": {
                "name": "nanobot-test-client",
                "version": "1.0.0"
            }
        }
    }

    print(f"\n[1] Sending ACP Initialize Request:\n{json.dumps(init_request, indent=2)}\n")
    process.stdin.write(json.dumps(init_request) + "\n")
    process.stdin.flush()
    time.sleep(2)

    # Step 2: Create a new session
    new_session_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "session/new",
        "params": {
            "cwd": "/tmp",
            "mcpServers": []
        }
    }

    print(f"\n[2] Sending ACP New Session Request:\n{json.dumps(new_session_request, indent=2)}\n")
    process.stdin.write(json.dumps(new_session_request) + "\n")
    process.stdin.flush()
    
    # Wait for session ID to be extracted
    timeout = 5
    while session_id is None and timeout > 0:
        time.sleep(1)
        timeout -= 1
        
    if not session_id:
        print("[-] Failed to get session ID. Exiting.")
        process.terminate()
        return

    # Step 3: Send a prompt request
    prompt_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "session/prompt",
        "params": {
            "sessionId": session_id,
            "prompt": [
                {
                    "type": "text",
                    "text": "Search the web for the latest news about AI agents and summarize in one sentence."
                }
            ]
        }
    }

    print(f"\n[3] Sending ACP Prompt Request:\n{json.dumps(prompt_request, indent=2)}\n")
    process.stdin.write(json.dumps(prompt_request) + "\n")
    process.stdin.flush()

    try:
        print("Waiting for response (Press Ctrl+C to exit)...")
        # Wait until the turn is completed or user interrupts
        while not turn_completed:
            time.sleep(1)
        
        print("\nExiting gracefully...")
        process.terminate()
        
    except KeyboardInterrupt:
        print("\nExiting...")
        process.terminate()

if __name__ == "__main__":
    main()
