"""Trading API endpoints for placing and managing orders."""

import json
from flask import Blueprint, request, jsonify
from py_clob_client.clob_types import OrderType
from polymarket.clob import (
    create_clob_client,
    create_limit_order,
    create_market_order,
    post_order,
    cancel_order,
    cancel_all_orders,
    get_open_orders,
    get_trades,
    get_last_trade_price,
    get_midpoint,
)
from polymarket.attribution import get_builder_auth_headers, get_builder_key_id

trading_bp = Blueprint("trading", __name__, url_prefix="/api/trading")


@trading_bp.route("/order/limit", methods=["POST"])
def place_limit_order():
    """Place a limit order on a prediction market.

    Body:
        private_key: User's private key (from Privy embedded wallet)
        funder: Safe wallet address
        token_id: Token to trade
        price: Price per share (0.01-0.99)
        size: Number of shares
        side: BUY or SELL
        order_type: GTC|GTD|FOK (default GTC)
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body required"}), 400

        required = ["private_key", "funder", "token_id", "price", "size", "side"]
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Create authenticated client with builder attribution
        client = create_clob_client(
            private_key=data["private_key"],
            funder=data["funder"],
            signature_type=0,
        )

        # Create and sign the order
        signed_order = create_limit_order(
            client,
            token_id=data["token_id"],
            price=float(data["price"]),
            size=float(data["size"]),
            side=data["side"].upper(),
        )

        # Map order type
        order_type_map = {
            "GTC": OrderType.GTC,
            "GTD": OrderType.GTD,
            "FOK": OrderType.FOK,
        }
        otype = order_type_map.get(data.get("order_type", "GTC"), OrderType.GTC)

        # Post order with builder attribution headers
        result = post_order(client, signed_order, otype)

        return jsonify({
            "success": True,
            "order": result,
            "builder_key": get_builder_key_id(),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trading_bp.route("/order/market", methods=["POST"])
def place_market_order():
    """Place a market order on a prediction market.

    Body:
        private_key: User's private key
        funder: Safe wallet address
        token_id: Token to trade
        amount: Dollar amount to spend
        side: BUY or SELL
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body required"}), 400

        required = ["private_key", "funder", "token_id", "amount"]
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        client = create_clob_client(
            private_key=data["private_key"],
            funder=data["funder"],
            signature_type=0,
        )

        signed_order = create_market_order(
            client,
            token_id=data["token_id"],
            amount=float(data["amount"]),
        )

        result = post_order(client, signed_order, OrderType.FOK)

        return jsonify({
            "success": True,
            "order": result,
            "builder_key": get_builder_key_id(),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trading_bp.route("/order/<order_id>", methods=["DELETE"])
def cancel_single_order(order_id):
    """Cancel an open order.

    Body:
        private_key: User's private key
        funder: Safe wallet address
    """
    try:
        data = request.get_json()
        if not data or "private_key" not in data:
            return jsonify({"error": "private_key required"}), 400

        client = create_clob_client(
            private_key=data["private_key"],
            funder=data.get("funder"),
            signature_type=0,
        )

        result = cancel_order(client, order_id)
        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trading_bp.route("/orders/cancel-all", methods=["POST"])
def cancel_all():
    """Cancel all open orders.

    Body:
        private_key: User's private key
        funder: Safe wallet address
    """
    try:
        data = request.get_json()
        if not data or "private_key" not in data:
            return jsonify({"error": "private_key required"}), 400

        client = create_clob_client(
            private_key=data["private_key"],
            funder=data.get("funder"),
            signature_type=0,
        )

        result = cancel_all_orders(client)
        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trading_bp.route("/orders", methods=["POST"])
def list_open_orders():
    """Get open orders for the user.

    Body:
        private_key: User's private key
        funder: Safe wallet address
        market: (optional) Filter by market
    """
    try:
        data = request.get_json()
        if not data or "private_key" not in data:
            return jsonify({"error": "private_key required"}), 400

        client = create_clob_client(
            private_key=data["private_key"],
            funder=data.get("funder"),
            signature_type=0,
        )

        orders = get_open_orders(client, market=data.get("market"))
        return jsonify({"orders": orders})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trading_bp.route("/trades", methods=["POST"])
def list_trades():
    """Get trade history for the user.

    Body:
        private_key: User's private key
        funder: Safe wallet address
    """
    try:
        data = request.get_json()
        if not data or "private_key" not in data:
            return jsonify({"error": "private_key required"}), 400

        client = create_clob_client(
            private_key=data["private_key"],
            funder=data.get("funder"),
            signature_type=0,
        )

        trades = get_trades(client)
        return jsonify({"trades": trades})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trading_bp.route("/price/<token_id>", methods=["GET"])
def get_price(token_id):
    """Get current price and midpoint for a token."""
    try:
        client = create_clob_client()
        mid = get_midpoint(client, token_id)
        last = get_last_trade_price(client, token_id)
        return jsonify({"midpoint": mid, "last_trade": last})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
