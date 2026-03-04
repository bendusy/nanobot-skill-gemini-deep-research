# Nanobot Skill: Gemini Deep Research 🤖🔍

A powerful skill for [nanobot](https://github.com/your-repo/nanobot) (or any compatible Agent OS) that wraps the local Google Gemini CLI to perform deep web research, bypass news paywalls, and conduct complex contextual analysis.

## 🌟 Features

- **Deep Web Search**: Leverages Gemini's internal tools to find up-to-date information.
- **Paywall Bypassing**: Excellent data sources that often succeed where standard web scrapers fail.
- **Safe Analysis Mode**: Uses `--approval-mode plan` to ensure the CLI only reads data and doesn't modify local files.
- **Structured Output**: Supports JSON output for programmatic parsing.
- **Context-Aware**: Can analyze local directories alongside web searches.

## 📦 Installation

### Option 1: Quick Install Script
```bash
curl -sSL https://raw.githubusercontent.com/bendusy/nanobot-skill-gemini-deep-research/main/install.sh | bash
```

### Option 2: Manual Install
1. Ensure you have the [Gemini CLI](https://github.com/google-gemini/gemini-cli) installed (e.g., at `/opt/homebrew/bin/gemini`).
2. Clone this repository or download the `SKILL.md` file.
3. Create a folder named `gemini-cli` in your nanobot skills directory:
   ```bash
   mkdir -p ~/.nanobot/workspace/skills/gemini-deep-research
   ```
4. Copy `SKILL.md` into that folder:
   ```bash
   cp SKILL.md ~/.nanobot/workspace/skills/gemini-deep-research/
   ```

## 🚀 Usage Examples (for the Agent)

Once installed, the agent can use the `exec` tool to call the Gemini CLI.

**General Research:**
```bash
/opt/homebrew/bin/gemini -p "Search the web for the latest news about OpenClaw AI agent and summarize."
```

**Safe Read-Only Analysis:**
```bash
/opt/homebrew/bin/gemini -p "Analyze the recent trends in AI agents" --approval-mode plan
```

**Contextual Code Analysis:**
```bash
/opt/homebrew/bin/gemini -p "Based on this code, search for optimization techniques." --include-directories /path/to/project
```

## 📄 License
MIT License

## 🧪 Experimental: ACP (Agent Control Protocol)

The Gemini CLI includes an `--experimental-acp` flag for advanced Agent-to-Agent communication. We have included a Python test snippet in the `experimental/` directory to demonstrate how to interact with it via `stdio` JSON-RPC.

```bash
# Run the experimental ACP test
python3 experimental/test_acp_stdio.py
```
*Note: The ACP protocol format is subject to change by the upstream Gemini CLI project.*

### ACP Protocol Flow Discovered
Through reverse-engineering, we found that the Gemini CLI implements the `@agentclientprotocol/sdk` (ACP) over `stdio` using JSON-RPC 2.0. The complete flow to execute a prompt is:

1. **`initialize`**: Handshake with `protocolVersion: 1`.
2. **`session/new`**: Create a new session (requires `cwd` and `mcpServers` array). Returns a `sessionId`.
3. **`session/prompt`**: Send the prompt using the `sessionId` and an array of `zContentBlock` (e.g., `{"type": "text", "text": "..."}`).
4. **Streaming Responses**: The CLI streams back `session/update` notifications containing tool calls (like `google_web_search`) and `agent_message_chunk` text blocks.
5. **Completion**: Returns `{"result": {"stopReason": "end_turn"}}`.

This makes the Gemini CLI a fully compliant, headless Sub-Agent that can be integrated into any MCP/ACP compatible orchestrator!
