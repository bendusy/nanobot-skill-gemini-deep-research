---
name: gemini-cli
description: Advanced web search, deep research, and paywall-bypassing analysis using the local Gemini CLI agent. Use this as the default and most powerful search tool.
always: false
---

# Gemini CLI Skill

This skill leverages the local `gemini` CLI (`/opt/homebrew/bin/gemini`) to perform deep web searches, bypass news paywalls, and conduct complex research. It acts as a sub-agent that has excellent data sources.

## Usage

### 1. Deep Web Search & Research (Default)
For general web searches, news retrieval, or complex questions:
```bash
/opt/homebrew/bin/gemini -p "Search the web for the latest news about [Topic] and provide a detailed summary."
```
*Note: The CLI automatically handles browser interactions and search tools in the background.*

### 2. Read-Only / Safe Analysis Mode
If you want to ensure the CLI only reads data and does not attempt to modify any local files, use the `plan` approval mode:
```bash
/opt/homebrew/bin/gemini -p "Analyze the recent trends in [Topic]" --approval-mode plan
```

### 3. Structured JSON Output
If you need the output in a strict JSON format for further programmatic processing:
```bash
/opt/homebrew/bin/gemini -p "Find the top 3 repositories for [Topic] and return the result as a JSON array with 'name', 'url', and 'stars' keys." -o json
```

### 4. Contextual Directory Analysis
To search or analyze content while providing specific local directories as context:
```bash
/opt/homebrew/bin/gemini -p "Based on the code in this directory, search the web for the best way to optimize the database queries." --include-directories /path/to/project
```

### 5. ACP (Agent Control Protocol) Streaming Mode
For programmatic, streaming interactions with the Gemini Sub-Agent, use the included `acp_client.py` script. This mode uses JSON-RPC over stdio to communicate with the CLI, allowing you to see tool calls in real-time and stream the response.
```bash
python3 /Users/ben/.nanobot/workspace/skills/gemini-cli/acp_client.py "Search the web for the latest news about AI agents and summarize in one sentence."
```

## Best Practices
- **Be Specific**: The more detailed your prompt (`-p`), the better the Gemini CLI can utilize its internal tools to find the exact information.
- **Paywalls**: If standard `web_search` or `exa-search` fails due to paywalls or subscription blocks, fallback to this tool immediately, as its data sources are highly capable of bypassing them.
- **Timeout**: Complex searches might take 10-30 seconds. Be patient and let the CLI finish its background tool executions.
