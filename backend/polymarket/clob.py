"""CLOB client wrapper for Polymarket trading operations.

Uses BuilderConfig for automatic order attribution to the builder account.
All orders placed through this client are attributed to builder key
019b99f0-0f93-7753-8dc3-d913cf44dcd4 on the Polymarket Builder Leaderboard.
"""

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import (
    MarketOrderArgs,
    OrderArgs,
    OrderType,
    BookParams,
)
from py_builder_signing_sdk.config import BuilderConfig
from py_builder_signing_sdk.sdk_types import BuilderApiKeyCreds
from config import Config


def _get_builder_config():
    """Create BuilderConfig for order attribution."""
    if not Config.POLY_BUILDER_API_KEY:
        return None
    creds = BuilderApiKeyCreds(
        key=Config.POLY_BUILDER_API_KEY,
        secret=Config.POLY_BUILDER_SECRET,
        passphrase=Config.POLY_BUILDER_PASSPHRASE,
    )
    return BuilderConfig(local_builder_creds=creds)


def create_clob_client(private_key=None, funder=None, signature_type=0):
    """Create a CLOB client for trading with builder attribution.

    Args:
        private_key: User's private key for signing orders.
                     Falls back to server-side key from config.
        funder: The funder address (Safe wallet address).
        signature_type: 0=EOA, 1=Magic/email, 2=browser proxy.
    """
    pk = private_key or Config.PRIVATE_KEY

    if not pk:
        # Read-only client for market data
        return ClobClient(Config.CLOB_API_URL)

    client = ClobClient(
        Config.CLOB_API_URL,
        key=pk,
        chain_id=Config.CHAIN_ID,
        signature_type=signature_type,
        funder=funder,
        builder_config=_get_builder_config(),
    )
    client.set_api_creds(client.create_or_derive_api_creds())
    return client


def get_market_price(client, token_id, side="buy"):
    """Get the current price for a token."""
    return client.get_price(token_id, side)


def get_midpoint(client, token_id):
    """Get the midpoint price for a token."""
    return client.get_midpoint(token_id)


def get_orderbook(client, token_id):
    """Get the orderbook for a token."""
    return client.get_order_book(token_id)


def get_orderbooks(client, token_ids):
    """Get orderbooks for multiple tokens."""
    params = [BookParams(token_id=tid) for tid in token_ids]
    return client.get_order_books(params)


def create_limit_order(client, token_id, price, size, side="BUY"):
    """Create and sign a limit order.

    Args:
        client: Authenticated ClobClient.
        token_id: The token to trade.
        price: Price per share (0-1).
        size: Number of shares.
        side: BUY or SELL.
    """
    order_args = OrderArgs(
        price=price,
        size=size,
        side=side,
        token_id=token_id,
    )
    return client.create_order(order_args)


def create_market_order(client, token_id, amount, side="BUY"):
    """Create and sign a market order.

    Args:
        client: Authenticated ClobClient.
        token_id: The token to trade.
        amount: Dollar amount to spend.
        side: BUY or SELL.
    """
    order_args = MarketOrderArgs(
        token_id=token_id,
        amount=amount,
    )
    return client.create_market_order(order_args)


def post_order(client, signed_order, order_type=OrderType.GTC):
    """Submit a signed order to the CLOB.

    Builder attribution headers are automatically attached by the
    ClobClient when builder_config is set.
    """
    return client.post_order(signed_order, order_type)


def cancel_order(client, order_id):
    """Cancel an open order."""
    return client.cancel(order_id)


def cancel_all_orders(client):
    """Cancel all open orders."""
    return client.cancel_all()


def get_open_orders(client, market=None):
    """Get all open orders, optionally filtered by market."""
    if market:
        return client.get_orders(market=market)
    return client.get_orders()


def get_trades(client):
    """Get trade history."""
    return client.get_trades()


def get_last_trade_price(client, token_id):
    """Get the last trade price for a token."""
    return client.get_last_trade_price(token_id)
