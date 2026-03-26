import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs, OrderType

from src.config import BotConfig
from src.data.market_types import Market, OrderBook, OrderBookLevel

logger = logging.getLogger("polybot.clob")

_executor = ThreadPoolExecutor(max_workers=4)


class AsyncClobWrapper:
    """Async wrapper around the synchronous py-clob-client."""

    def __init__(self, config: BotConfig):
        self._config = config
        creds = None
        if config.clob_api_key:
            creds = ApiCreds(
                api_key=config.clob_api_key,
                api_secret=config.clob_api_secret,
                api_passphrase=config.clob_api_passphrase,
            )
        self._client = ClobClient(
            host=config.polymarket_host,
            key=config.private_key,
            chain_id=config.polygon_chain_id,
            creds=creds,
            signature_type=config.signature_type,
            funder=config.funder_address or None,
        )

    async def _run_sync(self, func, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(_executor, partial(func, *args, **kwargs))

    async def derive_api_credentials(self) -> ApiCreds:
        """Derive or create CLOB API credentials. Save these to .env."""
        creds = await self._run_sync(self._client.create_or_derive_api_creds)
        self._client.set_api_creds(creds)
        logger.info("API credentials derived successfully")
        return creds

    async def set_credentials(self, api_key: str, api_secret: str, api_passphrase: str) -> None:
        creds = ApiCreds(api_key=api_key, api_secret=api_secret, api_passphrase=api_passphrase)
        self._client.set_api_creds(creds)

    async def get_markets(self, next_cursor: str = "MA==") -> tuple[list[Market], str]:
        """Fetch simplified markets. Returns (markets, next_cursor)."""
        result = await self._run_sync(self._client.get_simplified_markets, next_cursor)
        markets = []
        for m in result.get("data", []):
            tokens = m.get("tokens", [])
            markets.append(
                Market(
                    condition_id=m.get("condition_id", ""),
                    question=m.get("question", ""),
                    description=m.get("description", ""),
                    tokens=tokens,
                    end_date_iso=m.get("end_date_iso", ""),
                    active=m.get("active", True),
                    closed=m.get("closed", False),
                )
            )
        return markets, result.get("next_cursor", "")

    async def get_all_active_markets(self, max_pages: int = 10) -> list[Market]:
        """Paginate through all active markets."""
        all_markets = []
        cursor = "MA=="
        for _ in range(max_pages):
            markets, cursor = await self.get_markets(cursor)
            all_markets.extend([m for m in markets if m.active and not m.closed])
            if not cursor or cursor == "LTE=":
                break
        logger.info(f"Fetched {len(all_markets)} active markets")
        return all_markets

    async def get_order_book(self, token_id: str) -> OrderBook:
        """Fetch orderbook for a token."""
        result = await self._run_sync(self._client.get_order_book, token_id)
        bids = [
            OrderBookLevel(price=float(b.get("price", 0)), size=float(b.get("size", 0)))
            for b in result.get("bids", [])
        ]
        asks = [
            OrderBookLevel(price=float(a.get("price", 0)), size=float(a.get("size", 0)))
            for a in result.get("asks", [])
        ]
        return OrderBook(bids=bids, asks=asks)

    async def get_midpoint(self, token_id: str) -> float:
        result = await self._run_sync(self._client.get_midpoint, token_id)
        return float(result.get("mid", 0))

    async def create_and_post_order(self, order_args: OrderArgs) -> dict:
        """Create a signed order and post it to the CLOB."""
        result = await self._run_sync(self._client.create_and_post_order, order_args)
        logger.info(f"Order posted: {result}")
        return result

    async def cancel_order(self, order_id: str) -> dict:
        result = await self._run_sync(self._client.cancel, order_id)
        logger.info(f"Order cancelled: {order_id}")
        return result

    async def get_open_orders(self) -> list[dict]:
        result = await self._run_sync(self._client.get_orders)
        return result if isinstance(result, list) else []
