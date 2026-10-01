# job-tracker-mcp

A local job application tracker exposed over the Model Context Protocol (MCP).
Track every application from *saved* to *offer* with a full stage history,
see your real interview rate, and get told which applications are going cold —
from any MCP client (Claude Desktop, Claude Code, Cursor, Windsurf...).

No API keys. No account. No subscription. Your data stays in a SQLite file on
your machine.

## Why this exists

Job searching in 2026 is a funnel problem, and most people manage it in a
spreadsheet that breaks exactly when they need it most:

- Median time from search start to first offer hit **108 days** in Q1 2026
  (Huntr Q1 2026 Job Search Trends Report, 139,927 applications).
- The cold-application-to-interview ratio is **~2–3%**; around **40 applications
  per interview** is the market average for generic portal applying.
- Spreadsheets work below ~15–20 tracked applications and stop scaling after
  that — every row is manual work, nothing tells you an application went quiet.

This server is the minimal version of that tracker that an AI agent can
actually operate: structured stages, enforced state machine, real event log,
and statistics computed from the events rather than from what you remember.

## Tools (8)

| Tool | What it does |
| --- | --- |
| `add_job` | Save a new job in stage `saved` (company, role, URL, source, location, salary, notes) |
| `update_stage` | Move a job through the pipeline; invalid jumps are rejected with the allowed transitions |
| `list_jobs` | List jobs, optionally by stage or open-only |
| `get_job` | One job plus its complete stage history |
| `add_note` | Append a timestamped note (recruiter call, email, salary info) |
| `stats` | Totals per stage, interview rate %, average response time, per-source breakdown, oldest open application |
| `follow_ups` | Applications with no movement for N days (default 7) — the ones going cold |
| `export_csv` | Export the whole tracker as CSV (to a file or inline) |

### Stages and state machine

```
saved → applied → screening → interview → offer
          ↓          ↓           ↓         ↓
       rejected / withdrawn (terminal)
```

`update_stage` refuses impossible jumps (e.g. `saved → offer`), so the history
stays trustworthy.

## Quick start

```bash
uvx --from "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/job-tracker-mcp" job-tracker-mcp
```

Or run from a clone:

```bash
cd servers/job-tracker-mcp
pip install -e .
job-tracker-mcp
```

### Claude Desktop / Claude Code config

```json
{
  "mcpServers": {
    "job-tracker": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/job-tracker-mcp",
        "job-tracker-mcp"
      ]
    }
  }
}
```

## Data location

SQLite database at `~/.job-tracker/jobs.db` (override with the
`JOB_TRACKER_DB` environment variable). Two tables: `jobs` and `events`
(every stage change and note is an immutable event row).

## Example session

> "I just applied to Acme for a backend role from LinkedIn"
> → `add_job(company="Acme", role="Backend Developer", source="linkedin")`
> → `update_stage(job_id=1, stage="applied")`
>
> "How is my search going?"
> → `stats()` → `{sent: 23, interviews: 2, interview_rate_pct: 8.7, ...}`
>
> "Which applications went quiet?"
> → `follow_ups(days=7)` → 4 jobs with `days_waiting`

## Development

```bash
uv run pytest servers/job-tracker-mcp -v   # 11 offline tests, real SQLite
uv run ruff check servers/job-tracker-mcp
```

MIT license.
