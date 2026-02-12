"""Order attribution for tracking trades to the builder account.

Attribution is handled automatically by passing BuilderConfig to both
the ClobClient (for CLOB orders) and RelayClient (for gasless txns).
The BuilderConfig generates HMAC-signed headers on every request.

This module provides the builder key ID for display purposes.
"""

from config import Config

BUILDER_KEY_ID = Config.POLY_BUILDER_KEY_ID


def get_builder_key_id():
    """Return the builder key ID for order attribution."""
    return BUILDER_KEY_ID
