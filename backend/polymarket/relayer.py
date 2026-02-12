"""Relayer client for gasless transactions via Polymarket's Polygon relayer.

Uses the official py-builder-relayer-client SDK with proper RelayClient,
SafeTransaction models, and BuilderConfig authentication.
"""

from py_builder_relayer_client.client import RelayClient
from py_builder_relayer_client.models import SafeTransaction, OperationType
from py_builder_signing_sdk.config import BuilderConfig
from py_builder_signing_sdk.sdk_types import BuilderApiKeyCreds
from config import Config

# Max uint256 for token approvals
MAX_UINT256 = "0x" + "f" * 64


def _get_builder_config():
    """Create BuilderConfig from environment credentials."""
    creds = BuilderApiKeyCreds(
        key=Config.POLY_BUILDER_API_KEY,
        secret=Config.POLY_BUILDER_SECRET,
        passphrase=Config.POLY_BUILDER_PASSPHRASE,
    )
    return BuilderConfig(local_builder_creds=creds)


def create_relay_client(private_key=None):
    """Create an authenticated RelayClient.

    Args:
        private_key: Polygon wallet private key for signing transactions.
                     Falls back to server-side key from config.
    """
    pk = private_key or Config.PRIVATE_KEY
    return RelayClient(
        relayer_url=Config.RELAYER_URL,
        chain_id=Config.CHAIN_ID,
        private_key=pk,
        builder_config=_get_builder_config(),
    )


def get_safe_address(private_key=None):
    """Get the predicted Safe address for the signer's wallet.

    Returns:
        str: The predicted Safe wallet address.
    """
    client = create_relay_client(private_key)
    return client.get_expected_safe()


def is_safe_deployed(private_key=None):
    """Check if the Safe wallet is already deployed."""
    client = create_relay_client(private_key)
    safe_address = client.get_expected_safe()
    return client.get_deployed(safe_address)


def deploy_safe_wallet(private_key=None):
    """Deploy a Safe wallet via the Polymarket relayer (gasless).

    Returns:
        dict with transaction_id, transaction_hash, and safe_address.
    """
    client = create_relay_client(private_key)
    safe_address = client.get_expected_safe()

    # Check if already deployed
    if client.get_deployed(safe_address):
        return {
            "safe_address": safe_address,
            "already_deployed": True,
        }

    resp = client.deploy()
    return {
        "safe_address": safe_address,
        "transaction_id": resp.transactionID,
        "transaction_hash": resp.transactionHash,
        "already_deployed": False,
    }


def execute_transactions(transactions, private_key=None):
    """Execute gasless transactions through the relayer.

    Args:
        transactions: List of SafeTransaction objects.
        private_key: Wallet private key (falls back to config).

    Returns:
        dict with transaction_id and transaction_hash.
    """
    client = create_relay_client(private_key)
    resp = client.execute(transactions)
    return {
        "transaction_id": resp.transactionID,
        "transaction_hash": resp.transactionHash,
    }


def get_transaction_status(tx_id, private_key=None):
    """Check the status of a relayer transaction.

    States: NEW -> EXECUTED -> MINED -> CONFIRMED (or FAILED/INVALID).
    """
    client = create_relay_client(private_key)
    return client.get_transaction(tx_id)


def approve_all_tokens(private_key=None):
    """Approve USDC.e and CTF tokens for all exchange contracts.

    Executes all approvals in a single gasless batch transaction.
    Must be called once before the user can trade.
    """
    transactions = [
        # Approve USDC.e for CTF Exchange
        SafeTransaction(
            to=Config.USDCE_ADDRESS,
            operation=OperationType.Call,
            data=_encode_approve(Config.CTF_EXCHANGE_ADDRESS, MAX_UINT256),
            value="0",
        ),
        # Approve USDC.e for Neg Risk CTF Exchange
        SafeTransaction(
            to=Config.USDCE_ADDRESS,
            operation=OperationType.Call,
            data=_encode_approve(Config.NEG_RISK_CTF_EXCHANGE_ADDRESS, MAX_UINT256),
            value="0",
        ),
        # Approve CTF for CTF Exchange
        SafeTransaction(
            to=Config.CTF_ADDRESS,
            operation=OperationType.Call,
            data=_encode_set_approval_for_all(Config.CTF_EXCHANGE_ADDRESS, True),
            value="0",
        ),
        # Approve CTF for Neg Risk CTF Exchange
        SafeTransaction(
            to=Config.CTF_ADDRESS,
            operation=OperationType.Call,
            data=_encode_set_approval_for_all(
                Config.NEG_RISK_CTF_EXCHANGE_ADDRESS, True
            ),
            value="0",
        ),
        # Approve CTF for Neg Risk Adapter
        SafeTransaction(
            to=Config.CTF_ADDRESS,
            operation=OperationType.Call,
            data=_encode_set_approval_for_all(Config.NEG_RISK_ADAPTER_ADDRESS, True),
            value="0",
        ),
    ]

    return execute_transactions(transactions, private_key)


def _encode_approve(spender, amount):
    """Encode ERC20 approve(address,uint256)."""
    return "0x095ea7b3" + spender[2:].zfill(64) + amount[2:].zfill(64)


def _encode_set_approval_for_all(operator, approved):
    """Encode ERC1155 setApprovalForAll(address,bool)."""
    approved_hex = "1" if approved else "0"
    return "0xa22cb465" + operator[2:].zfill(64) + approved_hex.zfill(64)
