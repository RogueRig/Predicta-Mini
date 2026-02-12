"""CLOB client wrapper for Polymarket trading operations."""

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import (
    MarketOrderArgs,
    OrderArgs,
    OrderType,
    BookParams,
)
from config import Config


def create_clob_client(private_key=None, funder=None, signature_type=0):
    """Create an authenticated CLOB client for trading.

    Args:
        private_key: User's private key for signing orders.
        funder: The funder address (proxy/safe wallet address).
        signature_type: 0=EOA, 1=Magic/email, 2=browser proxy.
    """
    if not private_key:
        # Read-only client for market data
        return ClobClient(Config.CLOB_API_URL)

    client = ClobClient(
        Config.CLOB_API_URL,
        key=private_key,
        chain_id=Config.CHAIN_ID,
        signature_type=signature_type,
        funder=funder,
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
    signed_order = client.create_order(order_args)
    return signed_order


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
    signed_order = client.create_market_order(order_args)
    return signed_order


def post_order(client, signed_order, order_type=OrderType.GTC):
    """Submit a signed order to the CLOB."""
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
