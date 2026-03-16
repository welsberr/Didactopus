from .model_provider import ModelProvider
from .role_prompts import mentor_system_prompt


def generate_socratic_prompt(provider: ModelProvider, concept: str, weak_dimensions: list[str] | None = None) -> str:
    weak_text = ""
    if weak_dimensions:
        weak_text = f" Focus especially on weak dimensions: {', '.join(weak_dimensions)}."
    return provider.generate(
        f"Ask one probing question about '{concept}'.{weak_text}",
        role="mentor",
        system_prompt=mentor_system_prompt(),
    ).text
