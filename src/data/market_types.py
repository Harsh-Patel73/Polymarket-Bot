from dataclasses import dataclass, field


@dataclass
class Market:
    condition_id: str
    question: str
    description: str
    tokens: list[dict]
    end_date_iso: str
    active: bool = True
    closed: bool = False
    volume: float = 0.0
    liquidity: float = 0.0

    @property
    def token_ids(self) -> list[str]:
        return [t["token_id"] for t in self.tokens]


@dataclass
class OrderBookLevel:
    price: float
    size: float


@dataclass
class OrderBook:
    bids: list[OrderBookLevel] = field(default_factory=list)
    asks: list[OrderBookLevel] = field(default_factory=list)

    @property
    def midpoint(self) -> float:
        if not self.bids or not self.asks:
            return 0.0
        best_bid = self.bids[0].price
        best_ask = self.asks[0].price
        return (best_bid + best_ask) / 2

    @property
    def spread(self) -> float:
        if not self.bids or not self.asks:
            return 1.0
        return self.asks[0].price - self.bids[0].price

    @property
    def bid_depth_usd(self) -> float:
        return sum(level.price * level.size for level in self.bids)

    @property
    def ask_depth_usd(self) -> float:
        return sum(level.price * level.size for level in self.asks)
