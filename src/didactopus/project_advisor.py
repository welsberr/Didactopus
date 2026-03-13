from .model_provider import ModelProvider


def suggest_capstone(provider: ModelProvider, domain: str) -> str:
    return provider.generate(
        f"Suggest one realistic capstone project for mastery in {domain}."
    ).text
