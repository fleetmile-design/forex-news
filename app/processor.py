import re


def _clean_value(value: str | None) -> float | None:
    """Remove %, K, M suffixes and convert to float."""
    if not value:
        return None
    cleaned = re.sub(r"[%$,]", "", value.strip())
    multiplier = 1.0
    if cleaned.endswith("K"):
        multiplier = 1_000
        cleaned = cleaned[:-1]
    elif cleaned.endswith("M"):
        multiplier = 1_000_000
        cleaned = cleaned[:-1]
    elif cleaned.endswith("B"):
        multiplier = 1_000_000_000
        cleaned = cleaned[:-1]
    try:
        return float(cleaned) * multiplier
    except ValueError:
        return None


def calculate_sentiment(item: dict) -> tuple:
    """
    Compare actual vs forecast values:
    - actual > forecast  → ("Bullish", "text-green-400 font-bold")
    - actual < forecast  → ("Bearish", "text-red-400 font-bold")
    - equal or no data   → ("Neutral", "text-gray-300")
    """
    actual = _clean_value(item.get("actual") or "")
    forecast = _clean_value(item.get("forecast") or "")

    if actual is not None and forecast is not None:
        if actual > forecast:
            return ("Bullish", "text-green-400 font-bold")
        if actual < forecast:
            return ("Bearish", "text-red-400 font-bold")

    return ("Neutral", "text-gray-300")
