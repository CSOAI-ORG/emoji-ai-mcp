# Emoji Ai

> By [MEOK AI Labs](https://meok.ai) — MEOK AI Labs MCP Server

Emoji AI MCP Server

## Installation

```bash
pip install emoji-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install emoji-ai-mcp
```

## Tools

### `search_emoji`
Search for emojis by keyword or name.

**Parameters:**
- `query` (str)
- `limit` (int)

### `suggest_for_text`
Suggest relevant emojis for a given text based on sentiment/content.

**Parameters:**
- `text` (str)
- `max_suggestions` (int)

### `emoji_to_text`
Convert emojis in text to their text descriptions.

**Parameters:**
- `text` (str)

### `count_emojis`
Count and categorize emojis in text.

**Parameters:**
- `text` (str)


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/emoji-ai-mcp](https://github.com/CSOAI-ORG/emoji-ai-mcp)
- **PyPI**: [pypi.org/project/emoji-ai-mcp](https://pypi.org/project/emoji-ai-mcp/)

## License

MIT — MEOK AI Labs
