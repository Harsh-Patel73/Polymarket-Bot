from enum import IntEnum

from pydantic import Field
from pydantic_settings import BaseSettings


class SignatureType(IntEnum):
    EOA = 0
    MAGIC = 1
    BROWSER = 2


class BotConfig(BaseSettings):
    """All configuration loaded from .env. Validated at startup."""

    # Polymarket
    polymarket_host: str = "https://clob.polymarket.com"
    polygon_chain_id: int = 137
    private_key: str
    signature_type: int = SignatureType.EOA
    funder_address: str = ""

    clob_api_key: str = ""
    clob_api_secret: str = ""
    clob_api_passphrase: str = ""

    # Blockchain
    alchemy_rpc_url: str

    # AI
    anthropic_api_key: str
    claude_model: str = "claude-sonnet-4-20250514"

    # Telegram
    telegram_bot_token: str
    telegram_chat_id: int

    # Database
    db_path: str = "data/bot.db"

    # Trading parameters
    scan_interval_seconds: int = Field(default=300)
    min_edge: float = Field(default=0.05)
    max_slippage: float = Field(default=0.02)
    kelly_fraction: float = Field(default=0.25)
    max_position_usd: float = Field(default=50.0)
    max_total_exposure_usd: float = Field(default=500.0)
    min_market_liquidity_usd: float = Field(default=1000.0)
    min_hours_to_resolution: int = Field(default=24)

    # Prompt
    active_prompt_version: str = Field(default="v1")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }
