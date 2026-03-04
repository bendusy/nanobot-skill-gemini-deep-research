#!/usr/bin/env python3
"""
Experimental ACP (Agent Control Protocol) Test Snippet for Gemini CLI.

This script demonstrates how to communicate with the Gemini CLI running in
`--experimental-acp` mode via standard input/output (stdio) using JSON-RPC.
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
            msg = json.loads(line.strip())
            print(f"[ACP Response] {json.dumps(msg, indent=2)}")
        except json.JSONDecodeError:
            print(f"[Raw Output] {line.strip()}")

def main():
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

    # The CLI expects an 'initialize' method first, similar to MCP.
    # It requires a protocol version number in the params.
    request = {
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

    print(f"\nSending ACP Initialize Request:\n{json.dumps(request, indent=2)}\n")
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()

    try:
        print("Waiting for response (Press Ctrl+C to exit)...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        process.terminate()

if __name__ == "__main__":
    main()
