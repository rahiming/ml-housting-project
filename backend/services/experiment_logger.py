import json
from datetime import datetime, timezone
from pathlib import Path

LOGS_DIR = Path("logs")
LOG_FILE = LOGS_DIR / "ab_predictions.jsonl"


def log_prediction(event: dict) -> None:
    """Append one prediction event as a single JSONL line."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    event["timestamp"] = datetime.now(timezone.utc).isoformat()

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")
