from collections import Counter
import math


def _tokenize(text: str) -> list[str]:
    cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
    return [tok for tok in cleaned.split() if tok]


def token_cosine_similarity(text_a: str, text_b: str) -> float:
    tokens_a = _tokenize(text_a)
    tokens_b = _tokenize(text_b)
    if not tokens_a or not tokens_b:
        return 0.0
    ca = Counter(tokens_a)
    cb = Counter(tokens_b)
    shared = set(ca) & set(cb)
    dot = sum(ca[t] * cb[t] for t in shared)
    na = math.sqrt(sum(v * v for v in ca.values()))
    nb = math.sqrt(sum(v * v for v in cb.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def concept_similarity(concept_a: dict, concept_b: dict) -> float:
    text_a = " ".join([concept_a.get("title", ""), concept_a.get("description", ""), " ".join(concept_a.get("mastery_signals", []))])
    text_b = " ".join([concept_b.get("title", ""), concept_b.get("description", ""), " ".join(concept_b.get("mastery_signals", []))])
    return token_cosine_similarity(text_a, text_b)
