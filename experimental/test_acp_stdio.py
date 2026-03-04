#!/usr/bin/env python3
"""
Experimental ACP (Agent Control Protocol) Test Snippet for Gemini CLI.

This script demonstrates how to communicate with the Gemini CLI running in
`--experimental-acp` mode via standard input/output (stdio) using JSON-RPC.
Note: The exact ACP payload format may change as the CLI evolves.
"""

import subprocess
import json
import sys
import time
import threading

def read_output(process):
    """Read and print output from the ACP process."""
    while True:
        line = process.stdout.readline()
        if not line:
            break
        try:
            # Try to parse as JSON (ACP messages are typically JSON-RPC)
            msg = json.loads(line.strip())
            print(f"[ACP Response] {json.dumps(msg, indent=2)}")
        except json.JSONDecodeError:
            # Fallback to raw text if it's not JSON
            print(f"[Raw Output] {line.strip()}")

def main():
    print("Starting Gemini CLI in ACP mode...")
    
    # Start the CLI with the experimental ACP flag
    process = subprocess.Popen(
        ["/opt/homebrew/bin/gemini", "--experimental-acp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1 # Line buffered
    )

    # Start a thread to read responses asynchronously
    reader_thread = threading.Thread(target=read_output, args=(process,), daemon=True)
    reader_thread.start()

    # Wait a moment for initialization
    time.sleep(2)

    # Construct a sample ACP JSON-RPC request
    # (This is a generic structure; adjust based on official Gemini ACP docs)
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "agent.execute",
        "params": {
            "task": "Search the web for the latest news about AI agents.",
            "mode": "plan"
        }
    }

    print(f"\nSending ACP Request:\n{json.dumps(request, indent=2)}\n")
    
    # Send the request via stdin
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()

    # Keep the script running to receive the asynchronous response
    try:
        print("Waiting for response (Press Ctrl+C to exit)...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        process.terminate()

if __name__ == "__main__":
    main()
