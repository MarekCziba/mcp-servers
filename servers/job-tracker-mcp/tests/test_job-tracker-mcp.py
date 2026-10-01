"""Offline tests for job-tracker-mcp — real SQLite file per test session, no network."""

from datetime import datetime, timedelta, timezone

import job_tracker_mcp.main as m
import pytest

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def _temp_db(tmp_path, monkeypatch):
    monkeypatch.setenv("JOB_TRACKER_DB", str(tmp_path / "jobs.db"))


async def test_add_job_creates_saved_job_with_history():
    job = await m.add_job(
        "Acme", "Backend Developer", url="https://acme.dev/jobs/1", source="linkedin"
    )
    assert job["id"] == 1
    assert job["stage"] == "saved"
    assert job["company"] == "Acme"
    full = await m.get_job(1)
    assert full["history"][0]["to_stage"] == "saved"


async def test_add_job_requires_company_and_role():
    assert "error" in await m.add_job("", "Role")
    assert "error" in await m.add_job("Company", "   ")


async def test_stage_happy_path_applied_to_offer():
    await m.add_job("Acme", "Backend Developer")
    job = await m.update_stage(1, "applied", note="Easy Apply on LinkedIn")
    assert job["stage"] == "applied"
    assert (await m.update_stage(1, "screening"))["stage"] == "screening"
    assert (await m.update_stage(1, "interview"))["stage"] == "interview"
    assert (await m.update_stage(1, "offer"))["stage"] == "offer"
    full = await m.get_job(1)
    assert [e["to_stage"] for e in full["history"]] == [
        "saved",
        "applied",
        "screening",
        "interview",
        "offer",
    ]


async def test_invalid_transition_is_rejected():
    await m.add_job("Acme", "Backend Developer")
    assert "error" in await m.update_stage(1, "offer")
    await m.update_stage(1, "applied")
    await m.update_stage(1, "rejected")
    err = await m.update_stage(1, "applied")
    assert "error" in err
    assert "terminal" in err["error"]


async def test_unknown_stage_and_unknown_job_return_errors():
    await m.add_job("Acme", "Backend Developer")
    assert "error" in await m.update_stage(1, "hired")
    assert "error" in await m.update_stage(999, "applied")
    assert "error" in await m.get_job(999)


async def test_add_note_appends_with_timestamp_and_history_entry():
    await m.add_job("Acme", "Backend Developer")
    job = await m.add_note(1, "Recruiter called, salary 120k")
    assert "Recruiter called" in job["notes"]
    assert "[" in job["notes"]
    full = await m.get_job(1)
    assert any("Recruiter called" in e["note"] for e in full["history"])


async def test_list_jobs_filters_by_stage_and_open_only():
    await m.add_job("A", "Role A")
    await m.add_job("B", "Role B")
    await m.add_job("C", "Role C")
    await m.update_stage(2, "applied")
    await m.update_stage(3, "applied")
    await m.update_stage(3, "rejected")
    assert len(await m.list_jobs()) == 3
    assert len(await m.list_jobs(stage="applied")) == 1
    open_jobs = await m.list_jobs(include_closed=False)
    assert {j["company"] for j in open_jobs} == {"A", "B"}
    assert await m.list_jobs(stage="nonsense") == []


async def test_stats_computes_rates_from_real_events():
    for i, stages in enumerate(
        [("applied",), ("applied", "interview"), ("applied", "rejected")], start=1
    ):
        await m.add_job(f"Co{i}", f"Role {i}", source="linkedin" if i < 3 else "other")
        for s in stages:
            await m.update_stage(i, s)
    stats = await m.stats()
    assert stats["total"] == 3
    assert stats["sent"] == 3
    assert stats["interviews"] == 1
    assert stats["offers"] == 0
    assert stats["interview_rate_pct"] == 33.3
    assert stats["by_stage"]["applied"] == 1
    assert stats["by_stage"]["rejected"] == 1
    assert stats["by_source"]["linkedin"] == 2
    assert stats["by_source"]["other"] == 1
    assert stats["oldest_open_days"] >= 0


async def test_stats_average_response_time_uses_event_gaps(monkeypatch):
    t0 = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    times = {"t": t0}

    def fake_now():
        times["t"] += timedelta(days=2)
        return times["t"].isoformat(timespec="seconds")

    monkeypatch.setattr(m, "_now", fake_now)
    await m.add_job("Acme", "Backend Developer")
    await m.update_stage(1, "applied")
    await m.update_stage(1, "screening")
    stats = await m.stats()
    assert stats["avg_response_days"] == 2.0


async def test_follow_ups_flags_cold_applications(monkeypatch):
    t0 = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    clock = {"t": t0}
    monkeypatch.setattr(m, "_now", lambda: clock["t"].isoformat(timespec="seconds"))
    await m.add_job("Cold", "Role Cold")
    await m.add_job("Fresh", "Role Fresh")
    await m.update_stage(1, "applied")
    clock["t"] = t0 + timedelta(days=10)
    await m.update_stage(2, "applied")
    cold = await m.follow_ups(days=7)
    assert [j["company"] for j in cold] == ["Cold"]
    assert cold[0]["days_waiting"] == 10.0
    assert await m.follow_ups(days=30) == []
    await m.update_stage(1, "rejected")
    assert await m.follow_ups(days=7) == []


async def test_export_csv_returns_text_and_writes_file(tmp_path):
    await m.add_job("Acme", "Backend Developer", source="linkedin")
    inline = await m.export_csv()
    assert inline["rows"] == 1
    assert inline["csv"].splitlines()[0].startswith("id,company,role")
    assert "Acme" in inline["csv"]
    target = tmp_path / "out" / "jobs.csv"
    written = await m.export_csv(str(target))
    assert written == {"path": str(target), "rows": 1}
    assert "Acme" in target.read_text(encoding="utf-8")
