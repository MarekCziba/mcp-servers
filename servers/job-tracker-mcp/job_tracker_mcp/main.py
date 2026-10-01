import csv
import io
import os
import sqlite3
from datetime import datetime, timezone

from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "job-tracker-mcp"
mcp = MCPServer(MCP_SERVER_NAME)

STAGES = ("saved", "applied", "screening", "interview", "offer", "rejected", "withdrawn")
TRANSITIONS = {
    "saved": {"applied", "withdrawn"},
    "applied": {"screening", "interview", "offer", "rejected", "withdrawn"},
    "screening": {"interview", "offer", "rejected", "withdrawn"},
    "interview": {"offer", "rejected", "withdrawn"},
    "offer": {"rejected", "withdrawn"},
    "rejected": set(),
    "withdrawn": set(),
}
APPLIED_STAGES = ("applied", "screening", "interview", "offer", "rejected", "withdrawn")

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    url TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT '',
    location TEXT NOT NULL DEFAULT '',
    salary TEXT NOT NULL DEFAULT '',
    stage TEXT NOT NULL DEFAULT 'saved',
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    from_stage TEXT NOT NULL,
    to_stage TEXT NOT NULL,
    at TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT ''
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _db_path() -> str:
    path = os.environ.get("JOB_TRACKER_DB")
    if not path:
        path = os.path.join(os.path.expanduser("~"), ".job-tracker", "jobs.db")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    return path


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


def _job(row: sqlite3.Row) -> dict:
    return dict(row)


def _fetch_job(conn: sqlite3.Connection, job_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()


@mcp.tool()
async def add_job(
    company: str,
    role: str,
    url: str = "",
    source: str = "",
    location: str = "",
    salary: str = "",
    notes: str = "",
) -> dict:
    """Save a new job in stage 'saved'. company and role are required."""
    if not company.strip() or not role.strip():
        return {"error": "company and role are required."}
    now = _now()
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO jobs (company, role, url, source, location, salary, notes,"
            " created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (company.strip(), role.strip(), url, source, location, salary, notes, now, now),
        )
        job_id = cur.lastrowid
        conn.execute(
            "INSERT INTO events (job_id, from_stage, to_stage, at) VALUES (?, 'saved', 'saved', ?)",
            (job_id, now),
        )
        return _job(_fetch_job(conn, job_id))


@mcp.tool()
async def update_stage(job_id: int, stage: str, note: str = "") -> dict:
    """Move a job to a new stage. Valid: saved, applied, screening, interview, offer, rejected, withdrawn."""
    if stage not in STAGES:
        return {"error": f"Unknown stage '{stage}'. Valid stages: {', '.join(STAGES)}."}
    with _connect() as conn:
        row = _fetch_job(conn, job_id)
        if row is None:
            return {"error": f"No job with id {job_id}."}
        current = row["stage"]
        if stage not in TRANSITIONS[current]:
            allowed = ", ".join(sorted(TRANSITIONS[current])) or "none (terminal stage)"
            return {
                "error": f"Cannot move '{current}' -> '{stage}'. Allowed from '{current}': {allowed}."
            }
        now = _now()
        conn.execute("UPDATE jobs SET stage = ?, updated_at = ? WHERE id = ?", (stage, now, job_id))
        conn.execute(
            "INSERT INTO events (job_id, from_stage, to_stage, at, note) VALUES (?, ?, ?, ?, ?)",
            (job_id, current, stage, now, note),
        )
        return _job(_fetch_job(conn, job_id))


@mcp.tool()
async def list_jobs(stage: str = "", include_closed: bool = True) -> list[dict]:
    """List all tracked jobs, optionally filtered by one stage."""
    query = "SELECT * FROM jobs"
    params: tuple = ()
    if stage:
        if stage not in STAGES:
            return []
        query += " WHERE stage = ?"
        params = (stage,)
    elif not include_closed:
        query += " WHERE stage NOT IN ('rejected', 'withdrawn')"
    query += " ORDER BY updated_at DESC"
    with _connect() as conn:
        return [_job(r) for r in conn.execute(query, params).fetchall()]


@mcp.tool()
async def get_job(job_id: int) -> dict:
    """Get one job with its full stage history (all stage changes and notes)."""
    with _connect() as conn:
        row = _fetch_job(conn, job_id)
        if row is None:
            return {"error": f"No job with id {job_id}."}
        events = [
            dict(e)
            for e in conn.execute(
                "SELECT from_stage, to_stage, at, note FROM events WHERE job_id = ? ORDER BY at, id",
                (job_id,),
            ).fetchall()
        ]
        job = _job(row)
        job["history"] = events
        return job


@mcp.tool()
async def add_note(job_id: int, note: str) -> dict:
    """Append a timestamped note (recruiter call, email, salary info) to a job."""
    if not note.strip():
        return {"error": "note must not be empty."}
    with _connect() as conn:
        row = _fetch_job(conn, job_id)
        if row is None:
            return {"error": f"No job with id {job_id}."}
        now = _now()
        merged = (row["notes"] + f"\n[{now}] {note.strip()}").strip()
        conn.execute(
            "UPDATE jobs SET notes = ?, updated_at = ? WHERE id = ?", (merged, now, job_id)
        )
        conn.execute(
            "INSERT INTO events (job_id, from_stage, to_stage, at, note) VALUES (?, ?, ?, ?, ?)",
            (job_id, row["stage"], row["stage"], now, note.strip()),
        )
        return _job(_fetch_job(conn, job_id))


@mcp.tool()
async def stats() -> dict:
    """Pipeline statistics: counts per stage, interview rate, average response time, per-source breakdown."""
    now_dt = datetime.fromisoformat(_now())
    with _connect() as conn:
        by_stage = {s: 0 for s in STAGES}
        for r in conn.execute("SELECT stage, COUNT(*) AS n FROM jobs GROUP BY stage"):
            by_stage[r["stage"]] = r["n"]
        sent = sum(by_stage[s] for s in APPLIED_STAGES)
        interviews = conn.execute(
            "SELECT COUNT(DISTINCT job_id) AS n FROM events WHERE to_stage = 'interview'"
        ).fetchone()["n"]
        offers = conn.execute(
            "SELECT COUNT(DISTINCT job_id) AS n FROM events WHERE to_stage = 'offer'"
        ).fetchone()["n"]
        by_source = {
            (r["source"] or "unknown"): r["n"]
            for r in conn.execute(
                "SELECT source, COUNT(*) AS n FROM jobs WHERE stage != 'saved'"
                " GROUP BY source ORDER BY n DESC"
            )
        }
        gaps = []
        for r in conn.execute(
            "SELECT MIN(e1.at) AS applied_at,"
            " MIN(CASE WHEN e2.to_stage IN ('screening', 'interview', 'offer')"
            " THEN e2.at END) AS responded_at"
            " FROM jobs j"
            " JOIN events e1 ON e1.job_id = j.id AND e1.to_stage = 'applied'"
            " LEFT JOIN events e2 ON e2.job_id = j.id AND e2.at > e1.at"
            " GROUP BY j.id"
        ):
            if r["applied_at"] and r["responded_at"]:
                delta = datetime.fromisoformat(r["responded_at"]) - datetime.fromisoformat(
                    r["applied_at"]
                )
                gaps.append(delta.total_seconds() / 86400)
        oldest = None
        row = conn.execute(
            "SELECT updated_at FROM jobs WHERE stage IN ('applied', 'screening', 'interview', 'offer')"
            " ORDER BY updated_at ASC LIMIT 1"
        ).fetchone()
        if row:
            oldest = round(
                (now_dt - datetime.fromisoformat(row["updated_at"])).total_seconds() / 86400, 1
            )
    return {
        "total": sum(by_stage.values()),
        "by_stage": by_stage,
        "sent": sent,
        "interviews": interviews,
        "offers": offers,
        "interview_rate_pct": round(interviews / sent * 100, 1) if sent else 0.0,
        "avg_response_days": round(sum(gaps) / len(gaps), 1) if gaps else None,
        "by_source": by_source,
        "oldest_open_days": oldest,
    }


@mcp.tool()
async def follow_ups(days: int = 7) -> list[dict]:
    """Jobs applied or in progress with no stage change for N days (default 7) — the ones going cold."""
    now_dt = datetime.fromisoformat(_now())
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs WHERE stage IN ('applied', 'screening', 'interview', 'offer')"
            " ORDER BY updated_at ASC"
        ).fetchall()
    result = []
    for row in rows:
        waiting = round(
            (now_dt - datetime.fromisoformat(row["updated_at"])).total_seconds() / 86400, 1
        )
        if waiting >= days:
            job = _job(row)
            job["days_waiting"] = waiting
            result.append(job)
    return result


@mcp.tool()
async def export_csv(path: str = "") -> dict:
    """Export all jobs as CSV. Give a file path to write it, or omit it to get the CSV text back."""
    with _connect() as conn:
        rows = [_job(r) for r in conn.execute("SELECT * FROM jobs ORDER BY id").fetchall()]
    fields = [
        "id",
        "company",
        "role",
        "url",
        "source",
        "location",
        "salary",
        "stage",
        "notes",
        "created_at",
        "updated_at",
    ]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    if path:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            fh.write(buf.getvalue())
        return {"path": path, "rows": len(rows)}
    return {"rows": len(rows), "csv": buf.getvalue()}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
