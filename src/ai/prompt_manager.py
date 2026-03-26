import json
import logging
from pathlib import Path

logger = logging.getLogger("polybot.prompts")


class PromptTemplate:
    def __init__(self, system: str, user_template: str, model_params: dict):
        self.system = system
        self.user_template = user_template
        self.model_params = model_params


class PromptManager:
    """Load and render versioned prompts from the /prompts folder."""

    def __init__(self, prompts_dir: str = "prompts", active_version: str | None = None):
        self.prompts_dir = Path(prompts_dir)
        self.active_version = active_version or self._load_active_version()
        self._cache: dict[str, PromptTemplate] = {}
        logger.info(f"Using prompt version: {self.active_version}")

    def _load_active_version(self) -> str:
        active_file = self.prompts_dir / "active.json"
        if active_file.exists():
            data = json.loads(active_file.read_text())
            return data.get("active_version", "v1")
        return "v1"

    def get_prompt(self, name: str = "market_analysis") -> PromptTemplate:
        cache_key = f"{self.active_version}/{name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        path = self.prompts_dir / self.active_version / f"{name}.json"
        if not path.exists():
            raise FileNotFoundError(f"Prompt not found: {path}")

        data = json.loads(path.read_text())
        template = PromptTemplate(
            system=data["system"],
            user_template=data["user_template"],
            model_params=data.get("model_params", {}),
        )
        self._cache[cache_key] = template
        return template

    def render(self, name: str = "market_analysis", **variables: str) -> tuple[str, str]:
        """Render a prompt with variables. Returns (system_message, user_message)."""
        template = self.get_prompt(name)
        user_msg = template.user_template
        for key, value in variables.items():
            user_msg = user_msg.replace(f"{{{{{key}}}}}", str(value))
        return template.system, user_msg

    def get_model_params(self, name: str = "market_analysis") -> dict:
        return self.get_prompt(name).model_params
