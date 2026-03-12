from .model_provider import ModelProvider


def generate_practice_task(provider: ModelProvider, concept: str) -> str:
    prompt = (
        f"Generate one practice task for the concept '{concept}'. Require reasoning, "
        f"not mere recall, and avoid giving the answer."
    )
    return provider.generate(prompt).text
