from dataclasses import dataclass


@dataclass
class MarketAnalysis:
    probability: float
    confidence: str  # "high", "medium", "low"
    reasoning: str
    raw_response: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
