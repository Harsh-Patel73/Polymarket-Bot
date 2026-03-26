from src.db.database import Database


class Queries:
    """Named query functions for all database operations."""

    def __init__(self, db: Database):
        self._db = db

    # --- Positions ---

    async def insert_position(
        self,
        market_id: str,
        token_id: str,
        question: str,
        side: str,
        entry_price: float,
        size: float,
        shares: float,
        order_id: str | None,
        ai_probability: float,
        ai_confidence: str,
        ai_reasoning: str | None = None,
        prompt_version: str | None = None,
    ) -> int:
        cursor = await self._db.conn.execute(
            """INSERT INTO positions
               (market_id, token_id, question, side, entry_price, size, shares,
                order_id, ai_probability, ai_confidence, ai_reasoning, prompt_version)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                market_id, token_id, question, side, entry_price, size, shares,
                order_id, ai_probability, ai_confidence, ai_reasoning, prompt_version,
            ),
        )
        await self._db.conn.commit()
        return cursor.lastrowid  # type: ignore[return-value]

    async def get_open_positions(self) -> list[dict]:
        cursor = await self._db.conn.execute(
            "SELECT * FROM positions WHERE status = 'OPEN' ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    async def get_position(self, position_id: int) -> dict | None:
        cursor = await self._db.conn.execute(
            "SELECT * FROM positions WHERE id = ?", (position_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def update_position_price(self, position_id: int, current_price: float) -> None:
        await self._db.conn.execute(
            "UPDATE positions SET current_price = ?, updated_at = datetime('now') WHERE id = ?",
            (current_price, position_id),
        )
        await self._db.conn.commit()

    async def close_position(
        self, position_id: int, exit_price: float, pnl_usd: float, pnl_pct: float
    ) -> None:
        await self._db.conn.execute(
            """UPDATE positions
               SET status = 'CLOSED', exit_price = ?, pnl_usd = ?, pnl_pct = ?,
                   closed_at = datetime('now'), updated_at = datetime('now')
               WHERE id = ?""",
            (exit_price, pnl_usd, pnl_pct, position_id),
        )
        await self._db.conn.commit()

    async def get_total_open_exposure(self) -> float:
        cursor = await self._db.conn.execute(
            "SELECT COALESCE(SUM(size), 0) as total FROM positions WHERE status = 'OPEN'"
        )
        row = await cursor.fetchone()
        return float(row["total"])  # type: ignore[index]

    # --- Orders ---

    async def insert_order(
        self,
        order_id: str,
        position_id: int | None,
        market_id: str,
        token_id: str,
        side: str,
        price: float,
        size: float,
        order_type: str = "GTC",
    ) -> None:
        await self._db.conn.execute(
            """INSERT INTO orders
               (order_id, position_id, market_id, token_id, side, order_type, price, size)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (order_id, position_id, market_id, token_id, side, order_type, price, size),
        )
        await self._db.conn.commit()

    async def update_order_status(self, order_id: str, status: str, filled_size: float = 0.0) -> None:
        await self._db.conn.execute(
            """UPDATE orders SET status = ?, filled_size = ?, updated_at = datetime('now')
               WHERE order_id = ?""",
            (status, filled_size, order_id),
        )
        await self._db.conn.commit()

    # --- Scans ---

    async def insert_scan(
        self,
        markets_scanned: int,
        edges_found: int = 0,
        orders_placed: int = 0,
        errors: int = 0,
        duration_ms: int | None = None,
    ) -> None:
        await self._db.conn.execute(
            """INSERT INTO scans (markets_scanned, edges_found, orders_placed, errors, duration_ms)
               VALUES (?, ?, ?, ?, ?)""",
            (markets_scanned, edges_found, orders_placed, errors, duration_ms),
        )
        await self._db.conn.commit()

    # --- AI Analyses ---

    async def insert_analysis(
        self,
        market_id: str,
        question: str,
        market_price: float,
        prompt_version: str,
        ai_probability: float,
        ai_confidence: str,
        ai_reasoning: str | None,
        model: str,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        latency_ms: int | None = None,
    ) -> None:
        await self._db.conn.execute(
            """INSERT INTO ai_analyses
               (market_id, question, market_price, prompt_version,
                ai_probability, ai_confidence, ai_reasoning, model,
                input_tokens, output_tokens, latency_ms)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                market_id, question, market_price, prompt_version,
                ai_probability, ai_confidence, ai_reasoning, model,
                input_tokens, output_tokens, latency_ms,
            ),
        )
        await self._db.conn.commit()

    # --- Aggregates ---

    async def get_total_pnl(self) -> float:
        cursor = await self._db.conn.execute(
            "SELECT COALESCE(SUM(pnl_usd), 0) as total FROM positions WHERE status = 'CLOSED'"
        )
        row = await cursor.fetchone()
        return float(row["total"])  # type: ignore[index]

    async def get_position_count(self) -> dict:
        cursor = await self._db.conn.execute(
            """SELECT
                 COUNT(CASE WHEN status = 'OPEN' THEN 1 END) as open_count,
                 COUNT(CASE WHEN status = 'CLOSED' THEN 1 END) as closed_count
               FROM positions"""
        )
        row = await cursor.fetchone()
        return dict(row)  # type: ignore[arg-type]
