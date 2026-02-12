"""Wallet management API endpoints - Safe deployment and token approvals."""

from flask import Blueprint, request, jsonify
from polymarket.relayer import (
    deploy_safe_wallet,
    get_safe_address,
    approve_all_tokens,
    get_transaction_status,
)

wallet_bp = Blueprint("wallet", __name__, url_prefix="/api/wallet")


@wallet_bp.route("/safe/address", methods=["POST"])
def predict_safe_address():
    """Get the predicted Safe address for a user's EOA.

    Body:
        owner_address: The user's EOA wallet address from Privy.
    """
    try:
        data = request.get_json()
        if not data or "owner_address" not in data:
            return jsonify({"error": "owner_address required"}), 400

        result = get_safe_address(data["owner_address"])
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@wallet_bp.route("/safe/deploy", methods=["POST"])
def deploy_wallet():
    """Deploy a Safe wallet for the user via the Polymarket relayer.

    This is gasless - Polymarket pays the gas fees.

    Body:
        owner_address: The user's EOA wallet address from Privy.
    """
    try:
        data = request.get_json()
        if not data or "owner_address" not in data:
            return jsonify({"error": "owner_address required"}), 400

        result = deploy_safe_wallet(data["owner_address"])
        return jsonify({"success": True, "deployment": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@wallet_bp.route("/safe/approve", methods=["POST"])
def approve_tokens():
    """Approve all required tokens for trading.

    Approves USDC.e and CTF tokens for all exchange contracts.
    Must be called once before the user can trade.

    Body:
        safe_address: The user's deployed Safe wallet address.
    """
    try:
        data = request.get_json()
        if not data or "safe_address" not in data:
            return jsonify({"error": "safe_address required"}), 400

        result = approve_all_tokens(data["safe_address"])
        return jsonify({"success": True, "approval": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@wallet_bp.route("/transaction/<tx_id>", methods=["GET"])
def transaction_status(tx_id):
    """Check the status of a relayer transaction.

    Returns status: NEW, EXECUTED, MINED, CONFIRMED, FAILED, or INVALID.
    """
    try:
        result = get_transaction_status(tx_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
