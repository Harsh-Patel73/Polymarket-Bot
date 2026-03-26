import asyncio
import json
import logging
from collections.abc import Callable, Coroutine
from typing import Any

import websockets

from src.constants import POLYMARKET_WS_URL

logger = logging.getLogger("polybot.ws")


class PolymarketWebSocket:
    """Real-time price feed via Polymarket WebSocket."""

    def __init__(self, on_price_update: Callable[[dict], Coroutine[Any, Any, None]]):
        self._on_price_update = on_price_update
        self._subscriptions: set[str] = set()
        self._ws: Any = None
        self._running = False

    async def connect(self) -> None:
        self._ws = await websockets.connect(POLYMARKET_WS_URL)
        self._running = True
        logger.info("WebSocket connected")

    async def subscribe(self, token_ids: list[str]) -> None:
        if not self._ws:
            return
        for token_id in token_ids:
            if token_id not in self._subscriptions:
                msg = json.dumps({
                    "type": "subscribe",
                    "channel": "market",
                    "assets_id": token_id,
                })
                await self._ws.send(msg)
                self._subscriptions.add(token_id)
                logger.debug(f"Subscribed to {token_id}")

    async def unsubscribe(self, token_ids: list[str]) -> None:
        if not self._ws:
            return
        for token_id in token_ids:
            if token_id in self._subscriptions:
                msg = json.dumps({
                    "type": "unsubscribe",
                    "channel": "market",
                    "assets_id": token_id,
                })
                await self._ws.send(msg)
                self._subscriptions.discard(token_id)

    async def listen(self) -> None:
        """Main listen loop. Run as an asyncio task."""
        while self._running:
            try:
                if not self._ws:
                    await self.connect()
                async for raw_msg in self._ws:
                    if not self._running:
                        break
                    try:
                        msg = json.loads(raw_msg)
                        await self._on_price_update(msg)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON from WS: {raw_msg[:100]}")
            except websockets.ConnectionClosed:
                logger.warning("WebSocket disconnected, reconnecting in 5s...")
                await asyncio.sleep(5)
                self._ws = None
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await asyncio.sleep(5)
                self._ws = None

    async def close(self) -> None:
        self._running = False
        if self._ws:
            await self._ws.close()
            self._ws = None
