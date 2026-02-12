"""Market discovery and filtering via Polymarket Gamma API."""

import json
import requests
from config import Config

GAMMA_URL = Config.GAMMA_API_URL

# Tags that correspond to crypto-related markets
CRYPTO_TAGS = {"crypto", "bitcoin", "ethereum", "defi", "nft", "blockchain", "solana"}


def get_crypto_events(
    limit=20,
    offset=0,
    active=True,
    closed=False,
    sort_by="volume",
    order="desc",
    search="",
    min_volume=0,
    min_liquidity=0,
):
    """Fetch crypto-related prediction market events from Gamma API."""
    # Gamma API: 'order' is a field name, 'ascending' controls direction
    order_field_map = {
        "volume": "volume",
        "liquidity": "liquidity",
        "newest": "createdAt",
        "ending_soon": "endDate",
    }
    ascending_map = {
        "volume": "false",
        "liquidity": "false",
        "newest": "false",
        "ending_soon": "true",
    }

    params = {
        "limit": limit,
        "offset": offset,
        "active": str(active).lower(),
        "closed": str(closed).lower(),
        "tag_slug": "crypto",
        "order": order_field_map.get(sort_by, "volume"),
        "ascending": ascending_map.get(sort_by, "false"),
    }

    if search:
        params["title"] = search

    resp = requests.get(f"{GAMMA_URL}/events", params=params, timeout=15)
    resp.raise_for_status()
    events = resp.json()

    # Client-side filtering for volume/liquidity thresholds
    filtered = []
    for event in events:
        markets = event.get("markets", [])
        total_volume = sum(float(m.get("volume", 0) or 0) for m in markets)
        total_liquidity = sum(float(m.get("liquidity", 0) or 0) for m in markets)

        if total_volume < min_volume:
            continue
        if total_liquidity < min_liquidity:
            continue

        filtered.append(_format_event(event, total_volume, total_liquidity))

    return filtered


def get_event_detail(event_id):
    """Get detailed information about a specific event and its markets."""
    resp = requests.get(f"{GAMMA_URL}/events/{event_id}", timeout=15)
    resp.raise_for_status()
    event = resp.json()

    markets = event.get("markets", [])
    total_volume = sum(float(m.get("volume", 0) or 0) for m in markets)
    total_liquidity = sum(float(m.get("liquidity", 0) or 0) for m in markets)

    result = _format_event(event, total_volume, total_liquidity)
    result["markets"] = [_format_market(m) for m in markets]
    return result


def get_market_detail(condition_id):
    """Get detailed information about a specific market."""
    resp = requests.get(
        f"{GAMMA_URL}/markets",
        params={"condition_id": condition_id},
        timeout=15,
    )
    resp.raise_for_status()
    markets = resp.json()
    if not markets:
        return None
    return _format_market(markets[0])


def search_crypto_markets(query, limit=20):
    """Search crypto markets by keyword.

    The Gamma API text search is unreliable, so we fetch a larger batch
    of crypto events and filter client-side by title/description match.
    """
    query_lower = query.lower()

    # Fetch a larger batch to filter from
    params = {
        "limit": 100,
        "active": "true",
        "closed": "false",
        "tag_slug": "crypto",
        "order": "volume",
        "ascending": "false",
    }
    resp = requests.get(f"{GAMMA_URL}/events", params=params, timeout=15)
    resp.raise_for_status()
    events = resp.json()

    results = []
    for event in events:
        title = (event.get("title") or "").lower()
        desc = (event.get("description") or "").lower()
        # Also check individual market questions
        market_match = any(
            query_lower in (m.get("question") or "").lower()
            for m in event.get("markets", [])
        )

        if query_lower in title or query_lower in desc or market_match:
            markets = event.get("markets", [])
            total_volume = sum(float(m.get("volume", 0) or 0) for m in markets)
            total_liquidity = sum(
                float(m.get("liquidity", 0) or 0) for m in markets
            )
            results.append(_format_event(event, total_volume, total_liquidity))

        if len(results) >= limit:
            break

    return results


def get_orderbook(token_id):
    """Fetch orderbook from CLOB API for a specific token."""
    resp = requests.get(
        f"{Config.CLOB_API_URL}/book",
        params={"token_id": token_id},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def _parse_json_field(value, default=None):
    """Parse a JSON-encoded string field from the Gamma API."""
    if default is None:
        default = []
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return default
    if isinstance(value, list):
        return value
    return default


def _format_event(event, total_volume, total_liquidity):
    """Format an event for the frontend."""
    markets = event.get("markets", [])
    summaries = []
    for m in markets[:5]:
        prices = _parse_json_field(m.get("outcomePrices"), ["0.5", "0.5"])
        summaries.append({
            "id": m.get("id"),
            "question": m.get("question", ""),
            "outcome_yes": prices[0] if prices else "0.5",
            "outcome_no": prices[1] if len(prices) > 1 else "0.5",
            "volume": float(m.get("volume", 0) or 0),
        })

    return {
        "id": event.get("id"),
        "title": event.get("title", ""),
        "description": event.get("description", ""),
        "slug": event.get("slug", ""),
        "image": event.get("image", ""),
        "icon": event.get("icon", ""),
        "active": event.get("active", False),
        "closed": event.get("closed", False),
        "tags": event.get("tags", []),
        "created_at": event.get("createdAt", ""),
        "end_date": event.get("endDate", ""),
        "total_volume": total_volume,
        "total_liquidity": total_liquidity,
        "market_count": len(markets),
        "markets_summary": summaries,
    }


def _format_market(market):
    """Format a market for the frontend."""
    outcome_prices = _parse_json_field(
        market.get("outcomePrices"), ["0.5", "0.5"]
    )
    tokens = _parse_json_field(market.get("clobTokenIds"), ["", ""])

    return {
        "id": market.get("id"),
        "condition_id": market.get("conditionId", ""),
        "question": market.get("question", ""),
        "description": market.get("description", ""),
        "outcome_yes_price": float(outcome_prices[0]) if outcome_prices else 0.5,
        "outcome_no_price": float(outcome_prices[1])
        if outcome_prices and len(outcome_prices) > 1
        else 0.5,
        "token_yes": tokens[0] if tokens else "",
        "token_no": tokens[1] if tokens and len(tokens) > 1 else "",
        "volume": float(market.get("volume", 0) or 0),
        "liquidity": float(market.get("liquidity", 0) or 0),
        "end_date": market.get("endDate", ""),
        "active": market.get("active", False),
        "closed": market.get("closed", False),
        "neg_risk": market.get("negRisk", False),
        "neg_risk_market_id": market.get("negRiskMarketId", ""),
        "image": market.get("image", ""),
        "icon": market.get("icon", ""),
    }
