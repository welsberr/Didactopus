from .model_provider import ModelProvider


def suggest_capstone(provider: ModelProvider, domain: str) -> str:
    prompt = (
        f"Suggest one realistic capstone project for a learner pursuing mastery in {domain}. "
        f"The project must require synthesis, verification, and original work."
    )
    return provider.generate(prompt).text
