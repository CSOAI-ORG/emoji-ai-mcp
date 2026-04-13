"""
Emoji AI MCP Server
Emoji search and analysis tools powered by MEOK AI Labs.
"""

import re
import time
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("emoji-ai-mcp")

_call_counts: dict[str, list[float]] = defaultdict(list)
FREE_TIER_LIMIT = 50
WINDOW = 86400

def _check_rate_limit(tool_name: str) -> None:
    now = time.time()
    _call_counts[tool_name] = [t for t in _call_counts[tool_name] if now - t < WINDOW]
    if len(_call_counts[tool_name]) >= FREE_TIER_LIMIT:
        raise ValueError(f"Rate limit exceeded for {tool_name}. Free tier: {FREE_TIER_LIMIT}/day. Upgrade at https://meok.ai/pricing")
    _call_counts[tool_name].append(now)

EMOJI_DB = {
    "\U0001f600": {"name": "grinning face", "keywords": ["happy", "smile", "joy", "laugh"]},
    "\U0001f602": {"name": "face with tears of joy", "keywords": ["laugh", "cry", "funny", "lol"]},
    "\U0001f60d": {"name": "smiling face with heart-eyes", "keywords": ["love", "heart", "adore", "crush"]},
    "\U0001f914": {"name": "thinking face", "keywords": ["think", "wonder", "hmm", "ponder"]},
    "\U0001f44d": {"name": "thumbs up", "keywords": ["yes", "good", "ok", "approve", "like"]},
    "\U0001f44e": {"name": "thumbs down", "keywords": ["no", "bad", "dislike", "disapprove"]},
    "\u2764\ufe0f": {"name": "red heart", "keywords": ["love", "heart", "romance", "passion"]},
    "\U0001f525": {"name": "fire", "keywords": ["hot", "fire", "lit", "trending", "awesome"]},
    "\U0001f389": {"name": "party popper", "keywords": ["party", "celebrate", "congrats", "birthday"]},
    "\U0001f680": {"name": "rocket", "keywords": ["launch", "fast", "speed", "startup", "moon"]},
    "\U0001f4a1": {"name": "light bulb", "keywords": ["idea", "think", "bright", "insight"]},
    "\u2705": {"name": "check mark", "keywords": ["done", "complete", "yes", "correct", "check"]},
    "\u274c": {"name": "cross mark", "keywords": ["no", "wrong", "error", "delete", "cancel"]},
    "\u26a0\ufe0f": {"name": "warning", "keywords": ["warning", "alert", "caution", "danger"]},
    "\U0001f4dd": {"name": "memo", "keywords": ["note", "write", "document", "pen"]},
    "\U0001f41b": {"name": "bug", "keywords": ["bug", "insect", "debug", "error"]},
    "\U0001f3af": {"name": "bullseye", "keywords": ["target", "goal", "aim", "direct"]},
    "\U0001f4b0": {"name": "money bag", "keywords": ["money", "rich", "cash", "dollar", "profit"]},
    "\U0001f4c8": {"name": "chart increasing", "keywords": ["growth", "up", "increase", "chart", "stats"]},
    "\U0001f4c9": {"name": "chart decreasing", "keywords": ["down", "decrease", "loss", "decline"]},
    "\U0001f6e0\ufe0f": {"name": "hammer and wrench", "keywords": ["tools", "fix", "build", "repair", "settings"]},
    "\U0001f512": {"name": "locked", "keywords": ["lock", "security", "private", "safe"]},
    "\U0001f513": {"name": "unlocked", "keywords": ["unlock", "open", "public", "access"]},
    "\U0001f4e7": {"name": "e-mail", "keywords": ["email", "mail", "message", "inbox"]},
    "\U0001f30d": {"name": "globe", "keywords": ["world", "earth", "global", "international"]},
    "\u23f0": {"name": "alarm clock", "keywords": ["time", "alarm", "clock", "deadline", "urgent"]},
    "\U0001f4aa": {"name": "flexed biceps", "keywords": ["strong", "power", "muscle", "flex"]},
    "\U0001f4da": {"name": "books", "keywords": ["book", "read", "study", "library", "learn"]},
    "\U0001f916": {"name": "robot", "keywords": ["robot", "ai", "bot", "machine", "automation"]},
    "\U0001f332": {"name": "evergreen tree", "keywords": ["tree", "nature", "green", "forest", "environment"]},
}

SENTIMENT_MAP = {
    "happy": ["\U0001f600", "\U0001f389", "\U0001f44d"], "sad": ["\U0001f622", "\U0001f614", "\U0001f44e"],
    "love": ["\U0001f60d", "\u2764\ufe0f", "\U0001f48b"], "angry": ["\U0001f621", "\U0001f4a2", "\U0001f620"],
    "success": ["\u2705", "\U0001f680", "\U0001f3af", "\U0001f389"], "fail": ["\u274c", "\U0001f4c9", "\U0001f44e"],
    "idea": ["\U0001f4a1", "\U0001f914", "\U0001f3af"], "work": ["\U0001f6e0\ufe0f", "\U0001f4dd", "\U0001f4aa"],
    "money": ["\U0001f4b0", "\U0001f4c8", "\U0001f4b5"], "tech": ["\U0001f916", "\U0001f680", "\U0001f4bb"],
}


@mcp.tool()
def search_emoji(query: str, limit: int = 10) -> dict:
    """Search for emojis by keyword or description.

    Args:
        query: Search term (e.g., 'happy', 'fire', 'check')
        limit: Max results to return
    """
    _check_rate_limit("search_emoji")
    query_lower = query.lower()
    results = []
    for emoji, info in EMOJI_DB.items():
        score = 0
        if query_lower in info["name"]:
            score += 10
        if query_lower == info["name"]:
            score += 20
        for kw in info["keywords"]:
            if query_lower == kw:
                score += 15
            elif query_lower in kw:
                score += 5
        if score > 0:
            results.append({"emoji": emoji, "name": info["name"], "keywords": info["keywords"], "score": score})
    results.sort(key=lambda x: -x["score"])
    return {"query": query, "results": results[:limit], "total_matches": len(results)}


@mcp.tool()
def suggest_for_text(text: str, max_suggestions: int = 5) -> dict:
    """Suggest relevant emojis for a given text based on sentiment and keywords.

    Args:
        text: Text to analyze for emoji suggestions
        max_suggestions: Maximum number of suggestions
    """
    _check_rate_limit("suggest_for_text")
    text_lower = text.lower()
    suggestions = []
    seen = set()
    # Check sentiment keywords
    for sentiment, emojis in SENTIMENT_MAP.items():
        if sentiment in text_lower:
            for e in emojis:
                if e not in seen:
                    suggestions.append({"emoji": e, "reason": f"matches '{sentiment}' sentiment"})
                    seen.add(e)
    # Check emoji keywords
    for emoji, info in EMOJI_DB.items():
        if emoji in seen:
            continue
        for kw in info["keywords"]:
            if kw in text_lower:
                suggestions.append({"emoji": emoji, "name": info["name"], "reason": f"keyword '{kw}' found"})
                seen.add(emoji)
                break
    return {"text": text[:200], "suggestions": suggestions[:max_suggestions], "total_matches": len(suggestions)}


@mcp.tool()
def emoji_to_text(text: str) -> dict:
    """Convert emojis in text to their text descriptions.

    Args:
        text: Text containing emojis to convert
    """
    _check_rate_limit("emoji_to_text")
    result = text
    converted = []
    for emoji, info in EMOJI_DB.items():
        if emoji in result:
            result = result.replace(emoji, f"[{info['name']}]")
            converted.append({"emoji": emoji, "text": info["name"]})
    return {"original": text, "converted": result, "emojis_found": converted, "count": len(converted)}


@mcp.tool()
def count_emojis(text: str) -> dict:
    """Count and categorize emojis in text.

    Args:
        text: Text to analyze
    """
    _check_rate_limit("count_emojis")
    emoji_pattern = re.compile(
        "[\U0001f600-\U0001f64f\U0001f300-\U0001f5ff\U0001f680-\U0001f6ff"
        "\U0001f700-\U0001f77f\U0001f780-\U0001f7ff\U0001f800-\U0001f8ff"
        "\U0001f900-\U0001f9ff\U0001fa00-\U0001fa6f\U0001fa70-\U0001faff"
        "\u2702-\u27b0\u24c2-\U0001f251\u2600-\u26ff\u2700-\u27bf]+", re.UNICODE)
    found = emoji_pattern.findall(text)
    individual = list("".join(found))
    freq = defaultdict(int)
    for e in individual:
        freq[e] += 1
    details = []
    for e, count in sorted(freq.items(), key=lambda x: -x[1]):
        info = EMOJI_DB.get(e, {"name": "unknown"})
        details.append({"emoji": e, "name": info.get("name", "unknown"), "count": count})
    return {"total_emojis": len(individual), "unique_emojis": len(freq),
            "breakdown": details[:20], "text_length": len(text),
            "emoji_density": round(len(individual) / max(len(text), 1) * 100, 2)}


if __name__ == "__main__":
    mcp.run()
