"""Wallet management API endpoints - Safe deployment and token approvals.

The Polymarket relayer derives the Safe address from the signer's private key.
All operations use the server-side private key from config, which acts on
behalf of users. In production, each user would have their own key via Privy.
"""

from flask import Blueprint, request, jsonify
from polymarket.relayer import (
    deploy_safe_wallet,
    get_safe_address,
    is_safe_deployed,
    approve_all_tokens,
    get_transaction_status,
)

wallet_bp = Blueprint("wallet", __name__, url_prefix="/api/wallet")


@wallet_bp.route("/safe/address", methods=["POST"])
def predict_safe_address():
    """Get the predicted Safe address for the configured signer.

    The Safe address is deterministically derived from the private key.
    Optionally accepts a private_key in the body; defaults to server key.
    """
    try:
        data = request.get_json() or {}
        private_key = data.get("private_key")

        safe_address = get_safe_address(private_key)
        deployed = is_safe_deployed(private_key)

        return jsonify({
            "address": safe_address,
            "deployed": deployed,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@wallet_bp.route("/safe/deploy", methods=["POST"])
def deploy_wallet():
    """Deploy a Safe wallet via the Polymarket relayer (gasless).

    Polymarket pays all gas fees. The Safe address is derived from
    the signer's private key.
    """
    try:
        data = request.get_json() or {}
        private_key = data.get("private_key")

        result = deploy_safe_wallet(private_key)
        return jsonify({"success": True, "deployment": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@wallet_bp.route("/safe/approve", methods=["POST"])
def approve_tokens():
    """Approve all required tokens for trading (gasless).

    Approves USDC.e and CTF tokens for all exchange contracts
    in a single batch transaction. Must be called once before trading.
    """
    try:
        data = request.get_json() or {}
        private_key = data.get("private_key")

        result = approve_all_tokens(private_key)
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
