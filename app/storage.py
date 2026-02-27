from datetime import datetime
from typing import List
import pandas as pd

news_db: List[dict] = []
log_entries: List[str] = []


def add_log(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entries.append(f"[{timestamp}] {message}")


def get_logs(limit: int = 50) -> List[str]:
    return log_entries[-limit:]


def get_stats() -> dict:
    sources = list({item.get("source", "unknown") for item in news_db})
    last_fetch = log_entries[-1] if log_entries else "Never"
    return {
        "total": len(news_db),
        "sources": len(sources),
        "last_fetch": last_fetch,
    }


def export_csv(filepath: str) -> None:
    df = pd.DataFrame(news_db)
    df.to_csv(filepath, index=False)
