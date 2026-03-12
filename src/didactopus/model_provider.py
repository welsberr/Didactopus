from dataclasses import dataclass
from .config import ModelProviderConfig


@dataclass
class ModelResponse:
    text: str
    provider: str
    model_name: str


class ModelProvider:
    def __init__(self, config: ModelProviderConfig) -> None:
        self.config = config

    def describe(self) -> str:
        local = self.config.local
        return f"mode={self.config.mode}, local={local.backend}:{local.model_name}"

    def generate(self, prompt: str) -> ModelResponse:
        local = self.config.local
        preview = prompt.strip().replace("\n", " ")[:120]
        return ModelResponse(
            text=f"[stubbed-response] {preview}",
            provider=local.backend,
            model_name=local.model_name,
        )
