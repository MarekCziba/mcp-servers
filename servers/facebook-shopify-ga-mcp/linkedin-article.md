# Building an MCP Server That Unifies Facebook Ads, Shopify Orders & GA4

I recently built **`facebook-shopify-ga-mcp`** — a Microsoft Cloud Partner (MCP) server that aggregates data from three major platforms into a single, queryable endpoint.

## What It Does

The server exposes one endpoint (`top_performing_campaigns`) that joins:

- **Facebook Ads Insights** → spend, impressions, clicks, reach, ROAS
- **Shopify Orders** → revenue, tags, financial status
- **(Optionally) Google Analytics 4** → event counts, sessions

It calculates **ROAS per campaign** and returns campaigns ranked by revenue.

## Key Design Decisions

| Challenge | Solution |
|-----------|----------|
| **Env vars in tests** weren't picked up at import time | Moved `os.getenv()` calls inside each function so monkeypatching works |
| `httpx.Response` has no `.get()` method | Changed `r.get("data", [])` → `r.json().get("data", [])` |
| Deprecated `datetime.utcnow()` | Used `datetime.now(timezone.utc)` |
| Offline testing | Built `httpx.MockTransport` to simulate Facebook/Shopify responses |

## Why This Matters

- **Real-world integrations**: Many SaaS products need to combine data from multiple vendors.
- **LLM agents**: Agents often need structured data (spend, revenue, ROAS) without hard-coding API calls.
- **Testability**: With `MockTransport`, you can unit-test the server without hitting real APIs.

## How to Run

```bash
uv run main.py
```

Then call:

```
GET http://localhost:8000/top_performing_campaigns?days=7
```

## Takeaway

Building an MCP server isn't just about exposing APIs—it's about designing a cohesive data pipeline that serves real business needs. If you'd like me to:

1. **Push the code to GitHub** (create `linkedin-article.md`, commit, push)
2. **Copy the LinkedIn post** directly into your feed

Just say the word and I'll handle it!

---

*Repo: https://github.com/your-org/facebook-shopify-ga-mcp* (replace with your actual URL).