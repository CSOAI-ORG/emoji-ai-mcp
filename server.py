"""
Emoji AI MCP Server
Emoji search, suggestion, and analysis tools powered by MEOK AI Labs.
"""


import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import re
import time
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("emoji-ai", instructions="MEOK AI Labs MCP Server")

_call_counts: dict[str, list[float]] = defaultdict(list)
FREE_TIER_LIMIT = 50
WINDOW = 86400

EMOJI_DB = {
    "smile": {"emoji": "\U0001f604", "name": "grinning face with smiling eyes", "category": "faces"},
    "laugh": {"emoji": "\U0001f602", "name": "face with tears of joy", "category": "faces"},
    "love": {"emoji": "\u2764\ufe0f", "name": "red heart", "category": "symbols"},
    "heart_eyes": {"emoji": "\U0001f60d", "name": "smiling face with heart-eyes", "category": "faces"},
    "think": {"emoji": "\U0001f914", "name": "thinking face", "category": "faces"},
    "sad": {"emoji": "\U0001f622", "name": "crying face", "category": "faces"},
    "angry": {"emoji": "\U0001f621", "name": "pouting face", "category": "faces"},
    "fire": {"emoji": "\U0001f525", "name": "fire", "category": "nature"},
    "rocket": {"emoji": "\U0001f680", "name": "rocket", "category": "travel"},
    "star": {"emoji": "\u2b50", "name": "star", "category": "nature"},
    "check": {"emoji": "\u2705", "name": "check mark", "category": "symbols"},
    "cross": {"emoji": "\u274c", "name": "cross mark", "category": "symbols"},
    "thumbsup": {"emoji": "\U0001f44d", "name": "thumbs up", "category": "hands"},
    "thumbsdown": {"emoji": "\U0001f44e", "name": "thumbs down", "category": "hands"},
    "clap": {"emoji": "\U0001f44f", "name": "clapping hands", "category": "hands"},
    "wave": {"emoji": "\U0001f44b", "name": "waving hand", "category": "hands"},
    "pray": {"emoji": "\U0001f64f", "name": "folded hands", "category": "hands"},
    "muscle": {"emoji": "\U0001f4aa", "name": "flexed biceps", "category": "hands"},
    "sun": {"emoji": "\u2600\ufe0f", "name": "sun", "category": "nature"},
    "moon": {"emoji": "\U0001f319", "name": "crescent moon", "category": "nature"},
    "rain": {"emoji": "\U0001f327\ufe0f", "name": "cloud with rain", "category": "nature"},
    "snow": {"emoji": "\u2744\ufe0f", "name": "snowflake", "category": "nature"},
    "tree": {"emoji": "\U0001f333", "name": "deciduous tree", "category": "nature"},
    "flower": {"emoji": "\U0001f33a", "name": "hibiscus", "category": "nature"},
    "dog": {"emoji": "\U0001f436", "name": "dog face", "category": "animals"},
    "cat": {"emoji": "\U0001f431", "name": "cat face", "category": "animals"},
    "pizza": {"emoji": "\U0001f355", "name": "pizza", "category": "food"},
    "coffee": {"emoji": "\u2615", "name": "hot beverage", "category": "food"},
    "beer": {"emoji": "\U0001f37a", "name": "beer mug", "category": "food"},
    "cake": {"emoji": "\U0001f382", "name": "birthday cake", "category": "food"},
    "money": {"emoji": "\U0001f4b0", "name": "money bag", "category": "objects"},
    "book": {"emoji": "\U0001f4d6", "name": "open book", "category": "objects"},
    "computer": {"emoji": "\U0001f4bb", "name": "laptop", "category": "objects"},
    "phone": {"emoji": "\U0001f4f1", "name": "mobile phone", "category": "objects"},
    "email": {"emoji": "\U0001f4e7", "name": "email", "category": "objects"},
    "lock": {"emoji": "\U0001f512", "name": "locked", "category": "objects"},
    "key": {"emoji": "\U0001f511", "name": "key", "category": "objects"},
    "warning": {"emoji": "\u26a0\ufe0f", "name": "warning", "category": "symbols"},
    "info": {"emoji": "\u2139\ufe0f", "name": "information", "category": "symbols"},
    "question": {"emoji": "\u2753", "name": "question mark", "category": "symbols"},
    "party": {"emoji": "\U0001f389", "name": "party popper", "category": "objects"},
    "gift": {"emoji": "\U0001f381", "name": "wrapped gift", "category": "objects"},
    "trophy": {"emoji": "\U0001f3c6", "name": "trophy", "category": "objects"},
    "100": {"emoji": "\U0001f4af", "name": "hundred points", "category": "symbols"},
    "bug": {"emoji": "\U0001f41b", "name": "bug", "category": "animals"},
    "sparkles": {"emoji": "\u2728", "name": "sparkles", "category": "nature"},
    "eyes": {"emoji": "\U0001f440", "name": "eyes", "category": "faces"},
    "brain": {"emoji": "\U0001f9e0", "name": "brain", "category": "objects"},
    "robot": {"emoji": "\U0001f916", "name": "robot", "category": "faces"},
    "skull": {"emoji": "\U0001f480", "name": "skull", "category": "faces"},
    "ghost": {"emoji": "\U0001f47b", "name": "ghost", "category": "faces"},
}

SENTIMENT_MAP = {
    "happy": ["smile", "laugh", "party", "sparkles", "star"],
    "sad": ["sad", "rain", "skull"],
    "angry": ["angry", "fire", "cross"],
    "love": ["love", "heart_eyes", "flower", "gift"],
    "success": ["check", "trophy", "100", "rocket", "muscle"],
    "failure": ["cross", "bug", "thumbsdown"],
    "thinking": ["think", "brain", "question", "eyes"],
    "celebration": ["party", "clap", "trophy", "gift", "cake", "sparkles"],
    "work": ["computer", "book", "coffee", "email", "money"],
    "nature": ["sun", "moon", "tree", "flower", "snow", "rain"],
}


def _check_rate_limit(tool_name: str) -> None:
    now = time.time()
    _call_counts[tool_name] = [t for t in _call_counts[tool_name] if now - t < WINDOW]
    if len(_call_counts[tool_name]) >= FREE_TIER_LIMIT:
        raise ValueError(f"Rate limit exceeded for {tool_name}. Free tier: {FREE_TIER_LIMIT}/day. Upgrade at https://meok.ai/pricing")
    _call_counts[tool_name].append(now)


@mcp.tool()
def search_emoji(query: str, limit: int = 10, api_key: str = "") -> dict:
    """Search for emojis by keyword or name.

    Args:
        query: Search keyword
        limit: Max results (default 10)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("search_emoji")
    q = query.lower()
    results = []
    for key, data in EMOJI_DB.items():
        if q in key or q in data["name"] or q in data["category"]:
            results.append({"key": key, **data})
    return {"results": results[:limit], "total": len(results), "query": query}


@mcp.tool()
def suggest_for_text(text: str, max_suggestions: int = 5, api_key: str = "") -> dict:
    """Suggest relevant emojis for a given text based on sentiment/content.

    Args:
        text: Text to analyze for emoji suggestions
        max_suggestions: Maximum emoji suggestions (default 5)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("suggest_for_text")
    text_lower = text.lower()
    scores = defaultdict(int)
    for sentiment, keys in SENTIMENT_MAP.items():
        if sentiment in text_lower:
            for k in keys:
                scores[k] += 3
    for key, data in EMOJI_DB.items():
        if key in text_lower or data["name"].split()[0] in text_lower:
            scores[key] += 5
    if not scores:
        positive = any(w in text_lower for w in ("good", "great", "awesome", "nice", "well", "thanks", "cool"))
        negative = any(w in text_lower for w in ("bad", "error", "fail", "wrong", "broken", "issue"))
        if positive:
            for k in ["thumbsup", "sparkles", "check"]:
                scores[k] = 2
        elif negative:
            for k in ["warning", "cross", "bug"]:
                scores[k] = 2
        else:
            scores["info"] = 1
    sorted_keys = sorted(scores.keys(), key=lambda k: -scores[k])
    suggestions = []
    for key in sorted_keys[:max_suggestions]:
        if key in EMOJI_DB:
            suggestions.append({"key": key, **EMOJI_DB[key], "relevance_score": scores[key]})
    return {"suggestions": suggestions, "text_analyzed": text[:200]}


@mcp.tool()
def emoji_to_text(text: str, api_key: str = "") -> dict:
    """Convert emojis in text to their text descriptions.

    Args:
        text: Text containing emojis to convert
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("emoji_to_text")
    reverse_map = {data["emoji"]: data["name"] for data in EMOJI_DB.values()}
    result = text
    found = []
    for emoji_char, name in reverse_map.items():
        if emoji_char in result:
            result = result.replace(emoji_char, f"[{name}]")
            found.append({"emoji": emoji_char, "description": name})
    return {"original": text, "converted": result, "emojis_found": found, "count": len(found)}


@mcp.tool()
def count_emojis(text: str, api_key: str = "") -> dict:
    """Count and categorize emojis in text.

    Args:
        text: Text to analyze for emojis
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    _check_rate_limit("count_emojis")
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
        "\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF"
        "\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF"
        "\U00002702-\U000027B0\U000024C2-\U0001F251\U0000200d\U0000fe0f]+")
    found = emoji_pattern.findall(text)
    categories = defaultdict(int)
    known = {data["emoji"]: data["category"] for data in EMOJI_DB.values()}
    for e in found:
        cat = known.get(e, "other")
        categories[cat] += 1
    text_len = len(text)
    emoji_density = len(found) / max(text_len, 1) * 100
    return {"total_emojis": len(found), "unique_emojis": len(set(found)),
            "categories": dict(categories), "emoji_density": f"{emoji_density:.1f}%",
            "text_length": text_len}


if __name__ == "__main__":
    mcp.run()
