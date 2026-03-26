import json
import logging
import time
from datetime import date

from anthropic import AsyncAnthropic

from src.ai.analysis_types import MarketAnalysis
from src.ai.prompt_manager import PromptManager
from src.config import BotConfig

logger = logging.getLogger("polybot.ai")


class ClaudeClient:
    """AsyncAnthropic client for market probability estimation."""

    def __init__(self, config: BotConfig, prompt_manager: PromptManager):
        self._client = AsyncAnthropic(api_key=config.anthropic_api_key)
        self._model = config.claude_model
        self._prompts = prompt_manager

    async def analyze_market(
        self,
        question: str,
        description: str,
        current_price: float,
        end_date: str,
    ) -> MarketAnalysis:
        """Analyze a market and return structured probability estimate."""
        system_msg, user_msg = self._prompts.render(
            "market_analysis",
            question=question,
            description=description,
            current_price=f"{current_price:.4f}",
            end_date=end_date,
            today=date.today().isoformat(),
        )
        params = self._prompts.get_model_params("market_analysis")

        start = time.monotonic()
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=params.get("max_tokens", 300),
            temperature=params.get("temperature", 0.3),
            system=system_msg,
            messages=[{"role": "user", "content": user_msg}],
        )
        latency = int((time.monotonic() - start) * 1000)

        raw_text = response.content[0].text
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse Claude response: {raw_text[:200]}")
            raise

        analysis = MarketAnalysis(
            probability=float(parsed["probability"]),
            confidence=parsed["confidence"],
            reasoning=parsed["reasoning"],
            raw_response=raw_text,
            model=self._model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            latency_ms=latency,
        )

        logger.info(
            f"Analysis: p={analysis.probability:.2f} conf={analysis.confidence} "
            f"({latency}ms, {response.usage.input_tokens}+{response.usage.output_tokens} tokens)"
        )
        return analysis
