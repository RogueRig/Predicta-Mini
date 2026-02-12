import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-me-in-production")
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"

    # Polymarket APIs
    CLOB_API_URL = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
    GAMMA_API_URL = os.getenv("GAMMA_API_URL", "https://gamma-api.polymarket.com")
    RELAYER_URL = os.getenv("RELAYER_URL", "https://relayer-v2.polymarket.com")

    # Chain
    CHAIN_ID = int(os.getenv("CHAIN_ID", "137"))

    # Builder credentials
    POLY_BUILDER_API_KEY = os.getenv("POLY_BUILDER_API_KEY", "")
    POLY_BUILDER_SECRET = os.getenv("POLY_BUILDER_SECRET", "")
    POLY_BUILDER_PASSPHRASE = os.getenv("POLY_BUILDER_PASSPHRASE", "")
    POLY_BUILDER_KEY_ID = os.getenv(
        "POLY_BUILDER_KEY_ID", "019b99f0-0f93-7753-8dc3-d913cf44dcd4"
    )

    # Private key for server-side signing
    PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")

    # Privy
    PRIVY_APP_ID = os.getenv("PRIVY_APP_ID", "")
    PRIVY_APP_SECRET = os.getenv("PRIVY_APP_SECRET", "")

    # Polymarket contract addresses (Polygon)
    USDCE_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
    CTF_ADDRESS = "0x4d97dcd97ec945f40cf65f87097ace5ea0476045"
    CTF_EXCHANGE_ADDRESS = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
    NEG_RISK_CTF_EXCHANGE_ADDRESS = "0xC5d563A36AE78145C45a50134d48A1215220f80a"
    NEG_RISK_ADAPTER_ADDRESS = "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296"
