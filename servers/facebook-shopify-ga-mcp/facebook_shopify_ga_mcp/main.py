"""facebook-shopify-ga-mcp — Facebook Ads, Shopify and Google Analytics 4 metrics in one MCP server."""

from __future__ import annotations

import asyncio
import os
import httpx
from datetime import datetime, timezone, timedelta

from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "facebook-shopify-ga-mcp"
server = MCPServer(MCP_SERVER_NAME)

# --- shared HTTP client (tests replace _CLIENT with MockTransport) ---
_CLIENT: httpx.AsyncClient | None = None


def get_client() -> httpx.AsyncClient:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = httpx.AsyncClient(timeout=30)
    return _CLIENT


def _fb_url(endpoint: str) -> str:
    return f"https://graph.facebook.com/v20.0{endpoint}"


def _shopify_url(path: str) -> str:
    shop = os.getenv("SHOPIFY_SHOP", "")
    return f"https://{shop}/admin/api/2023-10/{path.lstrip('/')}"


# --- Facebook ---
async def facebook_ad_insights(
    ad_account_id: str,
    date_preset: str = "last_30_days",
    metrics: str = "spend,impressions,clicks,reach",
    dimensions: str = "campaign_name,adset_name,ad_name",
) -> list[dict]:
    """Fetch Facebook Ads insights from the Marketing API."""
    fb_token = os.getenv("FB_ACCESS_TOKEN", "")
    if not fb_token:
        return [{"error": "Set FB_ACCESS_TOKEN to read real Facebook data; with MockTransport it works offline."}]
    url = _fb_url(f"/{ad_account_id}/insights")
    params = {
        "access_token": fb_token,
        "date_preset": date_preset,
        "fields": metrics,
        "levels": dimensions,
    }
    try:
        r = await get_client().get(url, params=params)
        r.raise_for_status()
    except Exception as exc:
        return [{"error": str(exc)}]
    return r.json().get("data", [])


# --- Shopify ---
async def shopify_orders(
    days: int = 7,
    status: str = "any",
    fields: str = "id,total_price,financial_status,customer_id,tags,created_at,line_items",
) -> list[dict]:
    """Fetch Shopify orders from the last N days."""
    shop = os.getenv("SHOPIFY_SHOP", "")
    token = os.getenv("SHOPIFY_ACCESS_TOKEN", "")
    if not shop or not token:
        return [{"error": "Set SHOPIFY_SHOP + SHOPIFY_ACCESS_TOKEN to read real Shopify data; works offline with MockTransport."}]
    since = (datetime.now(timezone.utc) - timedelta(days=max(days, 0))).isoformat()
    url = _shopify_url("orders.json")
    params = {"status": status, "since": since, "fields": fields}
    try:
        r = await get_client().get(
            url, headers={"X-Shopify-Access-Token": token}, params=params
        )
        r.raise_for_status()
    except Exception as exc:
        return [{"error": str(exc)}]
    return r.json().get("orders", [])


async def shopify_products(since_days: int = 30) -> list[dict]:
    """Fetch Shopify products (last updated N days ago)."""
    shop = os.getenv("SHOPIFY_SHOP", "")
    token = os.getenv("SHOPIFY_ACCESS_TOKEN", "")
    if not shop or not token:
        return [{"error": "Set SHOPIFY_SHOP + SHOPIFY_ACCESS_TOKEN"}]
    since = (datetime.now(timezone.utc) - timedelta(days=max(since_days, 0))).isoformat()
    url = _shopify_url("products.json")
    params = {"since_updated_at": since, "fields": "id,title,handle,variants,price"}
    try:
        r = await get_client().get(
            url, headers={"X-Shopify-Access-Token": token}, params=params
        )
        r.raise_for_status()
    except Exception:
        return []
    return r.json().get("products", [])


# --- Google Analytics 4 (optional) ---
try:
    from google.analytics.data_v1 import BetaAnalyticsDataClient
    from google.analytics.data_v1 import DateRange
    from google.analytics.data_v1 import Dimension
    from google.analytics.data_v1 import Metric
    from google.analytics.data_v1 import RunReportRequest
    _HAS_GA4 = True
except Exception:
    _HAS_GA4 = False


def _ga4_client():
    key_path = os.getenv("GA4_KEY_PATH", "")
    if not key_path:
        return None
    try:
        return BetaAnalyticsDataClient.from_service_account_json(key_path)
    except Exception:
        return None


async def ga4_report(
    property_id: str = "",
    dimensions: str = "sessionDefaultChannelGroup",
    metrics: str = "totalRevenue,eventCount",
    start_date: str = "30daysAgo",
    end_date: str = "today",
) -> dict:
    """Run a GA4 Data API report. Requires optional `google-analytics-data` + service‑account JSON."""
    if not _HAS_GA4:
        return {
            "error": (
                "GA4 client not installed: uv pip install google-analytics-data google-auth; "
                "then set GA4_KEY_PATH and GA4_PROPERTY_ID"
            )
        }
    pid = property_id or os.getenv("GA4_PROPERTY_ID", "")
    if not pid:
        return {"error": "Set GA4_PROPERTY_ID (numeric ID after properties/), e.g. 335748417"}
    client = _ga4_client()
    if not client:
        return {"error": f"Could not build GA4 client from GA4_KEY_PATH={os.getenv('GA4_KEY_PATH', '')}"}
    dims = [Dimension(name=d.strip()) for d in dimensions.split(",") if d.strip()]
    mets = [Metric(name=m.strip()) for m in metrics.split(",") if m.strip()]
    req = RunReportRequest(
        property=f"properties/{pid}",
        dimensions=dims,
        metrics=mets,
        date_ranges=[DateRange(start=start_date, end=end_date)],
    )
    try:
        loop = asyncio.get_running_loop()
        resp = await loop.run_in_executor(None, client.run_report, req)
    except Exception as exc:
        return {"error": f"GA4 request failed: {exc}"}
    rows = []
    for row in resp.rows:
        d_vals = [d.value for d in row.dimension_values]
        m_vals = [float(m.value) for m in row.metric_values]
        rows.append(
            dict(
                zip(
                    [d.name for d in row.dimension_values] + [m.name for m in row.metric_values],
                    d_vals + m_vals,
                )
            )
        )
    return {"row_count": len(rows), "rows": rows}


# --- pure helpers ---
def calculate_roas(ad_spend: float, revenue: float) -> dict:
    """Calculate ROAS and profit margin percentage."""
    if not ad_spend:
        return {"roas": 0.0, "message": "ad_spend is zero; ROAS undefined"}
    roas = revenue / ad_spend
    return {"roas": round(roas, 2), "profit_margin_pct": round((roas - 1) * 100, 1)}


def sum_orders(orders: list[dict]) -> dict:
    """Aggregate order list: count, revenue, by financial status."""
    total_revenue = 0.0
    by_status: dict[str, int] = {}
    for o in orders:
        try:
            rev = float(o.get("total_price") or 0)
        except (TypeError, ValueError):
            rev = 0.0
        total_revenue += rev
        status = o.get("financial_status", "unknown")
        by_status[status] = by_status.get(status, 0) + 1
    return {"orders": len(orders), "revenue": round(total_revenue, 2), "by_status": by_status}


# --- correlation ---
async def top_performing_campaigns(days: int = 7) -> list[dict]:
    """Join Facebook Ads + Shopify: per-campaign spend, attributed Shopify revenue, ROAS."""
    fb = await facebook_ad_insights("act_placeholder", f"last_{days}_days")
    shop = await shopify_orders(days)
    _ = await ga4_report()  # optional, ignored if unavailable
    fb_rows = [r for r in fb if isinstance(r, dict) and "error" not in r]
    orders = [o for o in shop if isinstance(o, dict) and "error" not in o]
    result: list[dict] = []
    for f in fb_rows:
        campaign = f.get("campaign_name", "unknown")
        camp_id = f.get("campaign_id")
        try:
            spend = float(f.get("spend", 0))
        except (TypeError, ValueError):
            spend = 0.0
        attributed = 0.0
        for o in orders:
            if camp_id and str(camp_id) in str(o.get("tags") or ""):
                attributed += float(o.get("total_price") or 0)
        calc = calculate_roas(spend, attributed)
        result.append(
            {
                "campaign": campaign,
                "campaign_id": camp_id,
                "ad_spend": round(spend, 2),
                "revenue": round(attributed, 2),
                "impressions": float(f.get("impressions", 0) or 0),
                "clicks": float(f.get("clicks", 0) or 0),
                **calc,
            }
        )
    return sorted(result, key=lambda r: r["revenue"], reverse=True)


# --- MCP entry ---
def main() -> None:
    server.run()


if __name__ == "__main__":
    main()