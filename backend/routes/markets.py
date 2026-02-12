"""Market discovery and filtering API endpoints."""

from flask import Blueprint, request, jsonify
from polymarket.markets import (
    get_crypto_events,
    get_event_detail,
    get_market_detail,
    search_crypto_markets,
    get_orderbook,
)

markets_bp = Blueprint("markets", __name__, url_prefix="/api/markets")


@markets_bp.route("/", methods=["GET"])
def list_markets():
    """List crypto prediction markets with filtering.

    Query params:
        limit: Number of results (default 20, max 100)
        offset: Pagination offset
        sort_by: volume|liquidity|newest|ending_soon
        order: asc|desc
        search: Search query
        min_volume: Minimum total volume
        min_liquidity: Minimum total liquidity
        active: true|false (default true)
        closed: true|false (default false)
    """
    try:
        limit = min(int(request.args.get("limit", 20)), 100)
        offset = int(request.args.get("offset", 0))
        sort_by = request.args.get("sort_by", "volume")
        order = request.args.get("order", "desc")
        search = request.args.get("search", "")
        min_volume = float(request.args.get("min_volume", 0))
        min_liquidity = float(request.args.get("min_liquidity", 0))
        active = request.args.get("active", "true").lower() == "true"
        closed = request.args.get("closed", "false").lower() == "true"

        events = get_crypto_events(
            limit=limit,
            offset=offset,
            active=active,
            closed=closed,
            sort_by=sort_by,
            order=order,
            search=search,
            min_volume=min_volume,
            min_liquidity=min_liquidity,
        )

        return jsonify({"events": events, "count": len(events)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@markets_bp.route("/search", methods=["GET"])
def search_markets():
    """Search crypto markets by keyword.

    Query params:
        q: Search query (required)
        limit: Number of results (default 20)
    """
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "Search query 'q' is required"}), 400

    limit = min(int(request.args.get("limit", 20)), 100)

    try:
        results = search_crypto_markets(query, limit=limit)
        return jsonify({"events": results, "count": len(results)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@markets_bp.route("/event/<event_id>", methods=["GET"])
def event_detail(event_id):
    """Get detailed info about a specific event and its markets."""
    try:
        event = get_event_detail(event_id)
        return jsonify(event)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@markets_bp.route("/detail/<condition_id>", methods=["GET"])
def market_detail(condition_id):
    """Get detailed info about a specific market."""
    try:
        market = get_market_detail(condition_id)
        if not market:
            return jsonify({"error": "Market not found"}), 404
        return jsonify(market)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@markets_bp.route("/orderbook/<token_id>", methods=["GET"])
def orderbook(token_id):
    """Get the orderbook for a specific token."""
    try:
        book = get_orderbook(token_id)
        return jsonify(book)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
