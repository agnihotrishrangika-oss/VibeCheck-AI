"""
Lightweight SQLite History Service.
Persists past analysis results, timeline events, and multi-platform policy assessments.
"""

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any

from app.core.config import settings

DB_PATH = settings.BASE_DIR / "storage" / "history.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                filename TEXT,
                duration_seconds REAL NOT NULL,
                language TEXT,
                total_segments INTEGER NOT NULL,
                risk_count INTEGER NOT NULL,
                highest_severity TEXT,
                summary TEXT,
                payload_json TEXT NOT NULL
            )
        """)
        conn.commit()


def save_analysis(
    video_id: str,
    duration_seconds: float,
    language: Optional[str],
    segments: List[Dict[str, Any]],
    filename: Optional[str] = None,
) -> Dict[str, Any]:
    init_db()
    risk_events = [s for s in segments if s.get("label") != "normal"]
    severities = []
    for s in risk_events:
        yt = s.get("youtube_policy", {})
        ig = s.get("instagram_policy", {})
        if yt and yt.get("severity"):
            severities.append(yt["severity"])
        if ig and ig.get("severity"):
            severities.append(ig["severity"])

    highest_sev = "Low"
    if "Critical" in severities:
        highest_sev = "Critical"
    elif "High" in severities:
        highest_sev = "High"
    elif "Medium-High" in severities:
        highest_sev = "Medium-High"
    elif "Medium" in severities:
        highest_sev = "Medium"

    summary = (
        f"{len(risk_events)} potential risk event(s) detected across {len(segments)} segment(s). "
        f"Spoken language: {language or 'unknown'}."
    )

    created_at = datetime.now(timezone.utc).isoformat()
    payload = {
        "video_id": video_id,
        "filename": filename,
        "created_at": created_at,
        "duration_seconds": duration_seconds,
        "language": language,
        "segments": segments,
        "risk_count": len(risk_events),
        "highest_severity": highest_sev,
        "summary": summary,
    }

    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO analyses (
                id, created_at, filename, duration_seconds, language,
                total_segments, risk_count, highest_severity, summary, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                video_id,
                created_at,
                filename or f"video_{video_id[:8]}.mp4",
                duration_seconds,
                language,
                len(segments),
                len(risk_events),
                highest_sev,
                summary,
                json.dumps(payload),
            ),
        )
        conn.commit()

    return payload


def get_all_analyses(limit: int = 50) -> List[Dict[str, Any]]:
    init_db()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, created_at, filename, duration_seconds, language,
                   total_segments, risk_count, highest_severity, summary
            FROM analyses
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def get_analysis_by_id(analysis_id: str) -> Optional[Dict[str, Any]]:
    init_db()
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT payload_json FROM analyses WHERE id = ?", (analysis_id,)
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row["payload_json"])
        return None
