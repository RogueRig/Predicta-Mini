"""Relayer client for gasless transactions via Polymarket's Polygon relayer."""

import hashlib
import hmac
import time
import requests
from config import Config

RELAYER_URL = Config.RELAYER_URL


def _build_hmac_signature(secret, timestamp, method, path, body=""):
    """Build HMAC signature for relayer authentication."""
    message = f"{timestamp}{method}{path}{body}"
    signature = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return signature


def _get_auth_headers(method, path, body=""):
    """Generate authentication headers for relayer requests."""
    timestamp = str(int(time.time()))
    signature = _build_hmac_signature(
        Config.POLY_BUILDER_SECRET,
        timestamp,
        method,
        path,
        body,
    )
    return {
        "POLY_BUILDER_API_KEY": Config.POLY_BUILDER_API_KEY,
        "POLY_BUILDER_TIMESTAMP": timestamp,
        "POLY_BUILDER_PASSPHRASE": Config.POLY_BUILDER_PASSPHRASE,
        "POLY_BUILDER_SIGNATURE": signature,
        "Content-Type": "application/json",
    }


def deploy_safe_wallet(owner_address):
    """Deploy a Safe wallet for a user via the relayer.

    Args:
        owner_address: The EOA address that will own the Safe.

    Returns:
        dict with wallet address and deployment status.
    """
    path = "/safe/deploy"
    body = f'{{"owner": "{owner_address}"}}'
    headers = _get_auth_headers("POST", path, body)

    resp = requests.post(
        f"{RELAYER_URL}{path}",
        headers=headers,
        data=body,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_safe_address(owner_address):
    """Get the predicted Safe address for an owner (before or after deployment).

    Args:
        owner_address: The EOA address.

    Returns:
        dict with the predicted safe address.
    """
    path = f"/safe/address?owner={owner_address}"
    headers = _get_auth_headers("GET", path)

    resp = requests.get(
        f"{RELAYER_URL}{path}",
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def execute_transaction(safe_address, to, data="0x", value="0"):
    """Execute a gasless transaction through the relayer.

    Args:
        safe_address: The Safe wallet address.
        to: Target contract address.
        data: Encoded function call data.
        value: MATIC value to send (usually "0").

    Returns:
        dict with transaction hash and status.
    """
    path = "/safe/execute"
    body = (
        f'{{"safe": "{safe_address}", '
        f'"to": "{to}", '
        f'"data": "{data}", '
        f'"value": "{value}"}}'
    )
    headers = _get_auth_headers("POST", path, body)

    resp = requests.post(
        f"{RELAYER_URL}{path}",
        headers=headers,
        data=body,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def execute_batch(safe_address, transactions):
    """Execute multiple transactions atomically via the relayer.

    Args:
        safe_address: The Safe wallet address.
        transactions: List of {to, data, value} dicts.

    Returns:
        dict with transaction hash and status.
    """
    import json

    path = "/safe/execute-batch"
    body = json.dumps({"safe": safe_address, "transactions": transactions})
    headers = _get_auth_headers("POST", path, body)

    resp = requests.post(
        f"{RELAYER_URL}{path}",
        headers=headers,
        data=body,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_transaction_status(tx_id):
    """Check the status of a relayer transaction.

    States: NEW -> EXECUTED -> MINED -> CONFIRMED (or FAILED/INVALID).
    """
    path = f"/transaction/{tx_id}"
    headers = _get_auth_headers("GET", path)

    resp = requests.get(
        f"{RELAYER_URL}{path}",
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def approve_token(safe_address, token_address, spender_address, amount=None):
    """Approve a token for spending via gasless relayer transaction.

    Args:
        safe_address: The Safe wallet.
        token_address: ERC20 token contract.
        spender_address: Contract to approve.
        amount: Approval amount (None = max uint256).
    """
    if amount is None:
        amount = "0x" + "f" * 64  # max uint256

    # ERC20 approve(address,uint256) function selector
    data = (
        "0x095ea7b3"
        + spender_address[2:].zfill(64)
        + str(amount)[2:].zfill(64)
        if isinstance(amount, str) and amount.startswith("0x")
        else "0x095ea7b3"
        + spender_address[2:].zfill(64)
        + hex(int(amount))[2:].zfill(64)
    )

    return execute_transaction(safe_address, token_address, data)


def approve_all_tokens(safe_address):
    """Approve USDC.e and CTF tokens for all exchange contracts.

    This must be done before the user can trade.
    """
    max_uint = "0x" + "f" * 64

    transactions = []

    # Approve USDC.e for CTF Exchange
    transactions.append(
        {
            "to": Config.USDCE_ADDRESS,
            "data": _encode_approve(Config.CTF_EXCHANGE_ADDRESS, max_uint),
            "value": "0",
        }
    )
    # Approve USDC.e for Neg Risk CTF Exchange
    transactions.append(
        {
            "to": Config.USDCE_ADDRESS,
            "data": _encode_approve(Config.NEG_RISK_CTF_EXCHANGE_ADDRESS, max_uint),
            "value": "0",
        }
    )
    # Approve CTF for CTF Exchange
    transactions.append(
        {
            "to": Config.CTF_ADDRESS,
            "data": _encode_set_approval_for_all(Config.CTF_EXCHANGE_ADDRESS, True),
            "value": "0",
        }
    )
    # Approve CTF for Neg Risk CTF Exchange
    transactions.append(
        {
            "to": Config.CTF_ADDRESS,
            "data": _encode_set_approval_for_all(
                Config.NEG_RISK_CTF_EXCHANGE_ADDRESS, True
            ),
            "value": "0",
        }
    )
    # Approve CTF for Neg Risk Adapter
    transactions.append(
        {
            "to": Config.CTF_ADDRESS,
            "data": _encode_set_approval_for_all(Config.NEG_RISK_ADAPTER_ADDRESS, True),
            "value": "0",
        }
    )

    return execute_batch(safe_address, transactions)


def _encode_approve(spender, amount):
    """Encode ERC20 approve(address,uint256)."""
    return "0x095ea7b3" + spender[2:].zfill(64) + amount[2:].zfill(64)


def _encode_set_approval_for_all(operator, approved):
    """Encode ERC1155 setApprovalForAll(address,bool)."""
    approved_hex = "1" if approved else "0"
    return "0xa22cb465" + operator[2:].zfill(64) + approved_hex.zfill(64)
