<div align="center">

# Emoji Ai MCP

**Emoji AI MCP Server**

[![PyPI](https://img.shields.io/pypi/v/meok-emoji-ai-mcp)](https://pypi.org/project/meok-emoji-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Emoji AI MCP Server
Emoji search, suggestion, and analysis tools powered by MEOK AI Labs.

## Tools

| Tool | Description |
|------|-------------|
| `search_emoji` | Search for emojis by keyword or name. |
| `suggest_for_text` | Suggest relevant emojis for a given text based on sentiment/content. |
| `emoji_to_text` | Convert emojis in text to their text descriptions. |
| `count_emojis` | Count and categorize emojis in text. |

## Installation

```bash
pip install meok-emoji-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "emoji-ai": {
      "command": "python",
      "args": ["-m", "meok_emoji_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
