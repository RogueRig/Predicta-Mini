"""Market discovery and filtering via Polymarket Gamma API."""

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
    params = {
        "limit": limit,
        "offset": offset,
        "active": str(active).lower(),
        "closed": str(closed).lower(),
        "order": order,
        "ascending": "true" if order == "asc" else "false",
        "tag": "crypto",
    }

    if search:
        params["title"] = search

    resp = requests.get(f"{GAMMA_URL}/events", params=params, timeout=15)
    resp.raise_for_status()
    events = resp.json()

    # Additional client-side filtering
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

    if sort_by == "volume":
        filtered.sort(key=lambda e: e["total_volume"], reverse=(order == "desc"))
    elif sort_by == "liquidity":
        filtered.sort(key=lambda e: e["total_liquidity"], reverse=(order == "desc"))
    elif sort_by == "newest":
        filtered.sort(key=lambda e: e["created_at"], reverse=True)
    elif sort_by == "ending_soon":
        filtered.sort(key=lambda e: e["end_date"] or "9999", reverse=False)

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
    """Search crypto markets by keyword."""
    params = {
        "limit": limit,
        "active": "true",
        "closed": "false",
        "tag": "crypto",
        "title": query,
    }
    resp = requests.get(f"{GAMMA_URL}/events", params=params, timeout=15)
    resp.raise_for_status()
    events = resp.json()

    results = []
    for event in events:
        markets = event.get("markets", [])
        total_volume = sum(float(m.get("volume", 0) or 0) for m in markets)
        total_liquidity = sum(float(m.get("liquidity", 0) or 0) for m in markets)
        results.append(_format_event(event, total_volume, total_liquidity))

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


def _format_event(event, total_volume, total_liquidity):
    """Format an event for the frontend."""
    markets = event.get("markets", [])
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
        "markets_summary": [
            {
                "id": m.get("id"),
                "question": m.get("question", ""),
                "outcome_yes": m.get("outcomePrices", ["0.5", "0.5"])[0]
                if m.get("outcomePrices")
                else "0.5",
                "outcome_no": m.get("outcomePrices", ["0.5", "0.5"])[1]
                if m.get("outcomePrices") and len(m.get("outcomePrices", [])) > 1
                else "0.5",
                "volume": float(m.get("volume", 0) or 0),
            }
            for m in markets[:5]
        ],
    }


def _format_market(market):
    """Format a market for the frontend."""
    outcome_prices = market.get("outcomePrices", ["0.5", "0.5"])
    tokens = market.get("clobTokenIds", ["", ""])

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
