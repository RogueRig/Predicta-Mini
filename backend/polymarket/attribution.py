"""Order attribution for tracking trades to the builder account.

Adds HMAC-signed authentication headers to CLOB API requests
so all orders are attributed to the builder account on the
Polymarket Builder Leaderboard.
"""

import hashlib
import hmac
import time
from config import Config

BUILDER_KEY_ID = Config.POLY_BUILDER_KEY_ID


def build_hmac_signature(secret, timestamp, method, path, body=""):
    """Build HMAC signature for builder authentication.

    Args:
        secret: Builder API secret.
        timestamp: Unix timestamp string.
        method: HTTP method (GET, POST, DELETE).
        path: Request path.
        body: Request body string.

    Returns:
        HMAC-SHA256 hex signature.
    """
    message = f"{timestamp}{method}{path}{body}"
    return hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def get_builder_auth_headers(method, path, body=""):
    """Generate builder authentication headers for order attribution.

    These headers must be included with every order submission
    to attribute the trade to the builder account.

    Returns:
        dict of authentication headers.
    """
    timestamp = str(int(time.time()))
    signature = build_hmac_signature(
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
    }


def get_builder_key_id():
    """Return the builder key ID for order attribution."""
    return BUILDER_KEY_ID
