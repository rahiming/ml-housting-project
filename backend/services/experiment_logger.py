import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("uvicorn.error")

LOGS_DIR = Path("logs")
LOG_FILE = LOGS_DIR / "ab_predictions.jsonl"

_conn = None

_CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS predictions (
        id             SERIAL PRIMARY KEY,
        timestamp      TIMESTAMPTZ NOT NULL,
        request_id     TEXT,
        user_id        TEXT,
        variant        TEXT,
        model_version  TEXT,
        execution_mode TEXT,
        prediction     FLOAT,
        latency_ms     FLOAT,
        features       JSONB
    )
"""

_INSERT = """
    INSERT INTO predictions
      (timestamp, request_id, user_id, variant, model_version,
       execution_mode, prediction, latency_ms, features)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


def _get_conn():
    global _conn
    url = os.getenv("DATABASE_URL")
    if not url:
        return None
    import psycopg2

    try:
        if _conn is None or _conn.closed:
            _conn = psycopg2.connect(url)
            _conn.autocommit = True
            with _conn.cursor() as cur:
                cur.execute(_CREATE_TABLE)
    except Exception as exc:
        logger.warning("Connexion PostgreSQL echouee : %s", exc)
        _conn = None
    return _conn


def log_prediction(event: dict) -> None:
    event["timestamp"] = datetime.now(timezone.utc).isoformat()

    conn = _get_conn()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    _INSERT,
                    (
                        event["timestamp"],
                        event.get("request_id"),
                        event.get("user_id"),
                        event.get("variant"),
                        event.get("model_version"),
                        event.get("execution_mode"),
                        event.get("prediction"),
                        event.get("latency_ms"),
                        json.dumps(event.get("features", {})),
                    ),
                )
            return
        except Exception as exc:
            logger.warning("Ecriture PostgreSQL echouee, fallback JSONL : %s", exc)
            global _conn  # noqa: PLW0603
            _conn = None

    # Fallback : fichier local (dev sans DATABASE_URL)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
