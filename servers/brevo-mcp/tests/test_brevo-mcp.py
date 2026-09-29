"""Tests for brevo-mcp without an API key — graceful error paths only, no email is sent."""

import asyncio
import inspect

import brevo_mcp.main as brevo
import pytest
from brevo_mcp.main import account_info, send_bulk_emails, send_email

NO_KEY_MESSAGE = "ERROR: BREVO_API_KEY not set"


def _disable_key_and_network(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BREVO_API_KEY", raising=False)
    monkeypatch.setattr(brevo, "BREVO_API_KEY", "")

    def _no_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("network connection attempted without BREVO_API_KEY")

    monkeypatch.setattr(brevo.httpx, "AsyncClient", _no_network)


def test_module_constants() -> None:
    assert brevo.MCP_SERVER_NAME == "brevo-mcp"
    assert brevo.BREVO_API == "https://api.brevo.com/v3"
    assert set(brevo.HEADERS) == {"api-key", "Content-Type", "Accept"}


async def test_tools_registered_on_server() -> None:
    tools = await brevo.mcp.list_tools()
    assert {tool.name for tool in tools} == {"send_email", "send_bulk_emails", "account_info"}
    assert all(tool.description for tool in tools)


def test_tool_signatures() -> None:
    send_sig = inspect.signature(send_email)
    assert list(send_sig.parameters) == [
        "to",
        "to_name",
        "subject",
        "html_content",
        "sender_email",
        "sender_name",
    ]
    assert send_sig.parameters["sender_email"].default == "marekcziba@gmail.com"
    assert send_sig.parameters["sender_name"].default == "Marek Cziba"
    assert send_sig.return_annotation is str

    bulk_sig = inspect.signature(send_bulk_emails)
    assert list(bulk_sig.parameters) == ["recipients", "sender_email", "sender_name"]
    assert bulk_sig.return_annotation is str

    assert list(inspect.signature(account_info).parameters) == []


async def test_send_email_without_key_returns_documented_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _disable_key_and_network(monkeypatch)
    result = await asyncio.wait_for(
        send_email(
            to="nobody@example.com",
            to_name="Nobody",
            subject="Must never be sent",
            html_content="<p>Must never be sent</p>",
        ),
        timeout=15,
    )
    assert result == NO_KEY_MESSAGE


async def test_send_bulk_emails_without_key_returns_documented_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _disable_key_and_network(monkeypatch)
    recipients = [
        {"email": "nobody@example.com", "name": "Nobody", "subject": "S", "html": "<p>x</p>"}
    ]
    result = await asyncio.wait_for(send_bulk_emails(recipients), timeout=15)
    assert result == NO_KEY_MESSAGE


async def test_account_info_without_key_returns_documented_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _disable_key_and_network(monkeypatch)
    assert await asyncio.wait_for(account_info(), timeout=15) == NO_KEY_MESSAGE
