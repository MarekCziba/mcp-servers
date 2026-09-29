import json
import os

import httpx
from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "brevo-mcp"
mcp = MCPServer(MCP_SERVER_NAME)

BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
BREVO_API = "https://api.brevo.com/v3"
HEADERS = {
    "api-key": BREVO_API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json",
}


@mcp.tool()
async def send_email(
    to: str,
    to_name: str,
    subject: str,
    html_content: str,
    sender_email: str = "marekcziba@gmail.com",
    sender_name: str = "Marek Cziba",
) -> str:
    """Send a single transactional email via Brevo."""
    if not BREVO_API_KEY:
        return "ERROR: BREVO_API_KEY not set"
    payload = {
        "sender": {"email": sender_email, "name": sender_name},
        "to": [{"email": to, "name": to_name}],
        "subject": subject,
        "htmlContent": html_content,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{BREVO_API}/smtp/email", json=payload, headers=HEADERS)
    if resp.status_code == 201:
        return f"OK: {resp.json().get('messageId', '')}"
    return f"FAIL {resp.status_code}: {resp.text}"


@mcp.tool()
async def send_bulk_emails(
    recipients: list, sender_email: str = "marekcziba@gmail.com", sender_name: str = "Marek Cziba"
) -> str:
    """Send the same inquiry email to multiple recipients. Each recipient: {'email': str, 'name': str, 'subject': str, 'html': str}"""
    if not BREVO_API_KEY:
        return "ERROR: BREVO_API_KEY not set"
    results = []
    async with httpx.AsyncClient() as client:
        for r in recipients:
            payload = {
                "sender": {"email": sender_email, "name": sender_name},
                "to": [{"email": r["email"], "name": r.get("name", "")}],
                "subject": r["subject"],
                "htmlContent": r["html"],
            }
            resp = await client.post(f"{BREVO_API}/smtp/email", json=payload, headers=HEADERS)
            if resp.status_code == 201:
                results.append(f"OK: {r['email']} -> {resp.json().get('messageId', '')}")
            else:
                results.append(f"FAIL: {r['email']} -> {resp.status_code}")
    return "\n".join(results)


@mcp.tool()
async def account_info() -> str:
    """Get Brevo account information."""
    if not BREVO_API_KEY:
        return "ERROR: BREVO_API_KEY not set"
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BREVO_API}/account", headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        return json.dumps(
            {
                "email": data.get("email"),
                "company": data.get("companyName"),
                "plan": data.get("plan"),
            },
            indent=2,
        )
    return f"FAIL {resp.status_code}: {resp.text}"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
