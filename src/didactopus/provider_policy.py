from __future__ import annotations

from .model_provider import ModelProvider


def is_healthy_gateway_model(model: dict) -> bool:
    geniehive = model.get("geniehive", {})
    if isinstance(geniehive, dict):
        route_type = str(geniehive.get("route_type", "")).strip().lower()
        if route_type == "role":
            return int(geniehive.get("healthy_target_count", 0) or 0) > 0
        if geniehive.get("health") not in (None, "", "healthy"):
            return False
    for key in ("healthy", "available", "enabled", "loaded"):
        value = model.get(key)
        if value is False:
            return False
    state = str(model.get("state", model.get("status", ""))).strip().lower()
    if state and state not in {"available", "healthy", "ready", "loaded", "online", "running"}:
        return False
    return bool(str(model.get("id", "")).strip())


def healthy_gateway_models(provider: ModelProvider) -> set[str]:
    config = provider.config
    if config.provider.lower() not in {"rolemesh", "geniehive", "gateway"}:
        return set()
    return {
        str(model.get("id", "")).strip()
        for model in provider.list_models()
        if isinstance(model, dict) and is_healthy_gateway_model(model)
    }


def gateway_fallback_score(model: dict) -> tuple[int, int, int, float, str]:
    geniehive = model.get("geniehive", {})
    route_type = ""
    operation = ""
    loaded_count = 0
    latency = None
    if isinstance(geniehive, dict):
        route_type = str(geniehive.get("route_type", "")).strip().lower()
        operation = str(geniehive.get("operation", "")).strip().lower()
        loaded_count = int(
            geniehive.get("loaded_target_count", geniehive.get("loaded_asset_count", 0)) or 0
        )
        latency = geniehive.get("best_p50_latency_ms")
        if latency is None:
            observed = geniehive.get("observed", {})
            if isinstance(observed, dict):
                latency = observed.get("p50_latency_ms")
    operation_score = 1 if operation in {"", "chat"} else 0
    route_score = 2 if route_type == "role" else 1 if route_type in {"asset", "service"} else 0
    latency_score = float(latency) if latency is not None else float("inf")
    return (operation_score, route_score, loaded_count, -latency_score, str(model.get("id", "")))


def is_gateway_model_routable(provider: ModelProvider, model_id: str, *, kind: str = "chat") -> bool:
    resolution = provider.resolve_route(model_id, kind=kind)
    return isinstance(resolution, dict) and resolution.get("service") is not None


def select_gateway_fallback_model(provider: ModelProvider, *, kind: str = "chat") -> str:
    gateway = provider.config.gateway
    if is_gateway_model_routable(provider, gateway.default_model, kind=kind):
        return gateway.default_model
    candidates = []
    for model in provider.list_models():
        if not isinstance(model, dict):
            continue
        model_id = str(model.get("id", "")).strip()
        if not model_id or not is_healthy_gateway_model(model):
            continue
        if not is_gateway_model_routable(provider, model_id, kind=kind):
            continue
        candidates.append(model)
    if not candidates:
        raise RuntimeError(f"No healthy gateway models available for {kind} generation.")
    return max(candidates, key=gateway_fallback_score)["id"]


def resolve_role_model_overrides(provider: ModelProvider, *, kind: str = "chat") -> dict[str, str]:
    config = provider.config
    if config.provider.lower() not in {"rolemesh", "geniehive", "gateway"}:
        return {}
    gateway = config.gateway
    fallback_model = select_gateway_fallback_model(provider, kind=kind)
    overrides: dict[str, str] = {}
    for role, model in gateway.role_to_model.items():
        if not is_gateway_model_routable(provider, model, kind=kind):
            overrides[role] = fallback_model
    return overrides


def effective_provider_for_kind(provider: ModelProvider, *, kind: str = "chat") -> ModelProvider:
    return provider.with_role_model_overrides(resolve_role_model_overrides(provider, kind=kind))


def provider_diagnostics_for_kind(provider: ModelProvider, *, kind: str = "chat") -> dict:
    config = provider.config
    provider_name = config.provider.lower()
    if provider_name not in {"rolemesh", "geniehive", "gateway"}:
        return {
            "provider": provider_name,
            "kind": kind,
            "healthy_models": [],
            "fallback_model": None,
            "role_model_overrides": {},
            "routes": {},
        }

    gateway = config.gateway
    overrides = resolve_role_model_overrides(provider, kind=kind)
    effective_provider = provider.with_role_model_overrides(overrides)
    role_models = {
        role: effective_provider.role_model_overrides.get(role, model)
        for role, model in gateway.role_to_model.items()
    }
    routes = {
        role: {
            "requested_model": role_models[role],
            "resolution": provider.resolve_route(role_models[role], kind=kind),
        }
        for role in sorted(role_models)
    }
    return {
        "provider": provider_name,
        "kind": kind,
        "healthy_models": sorted(healthy_gateway_models(provider)),
        "fallback_model": select_gateway_fallback_model(provider, kind=kind),
        "role_model_overrides": overrides,
        "routes": routes,
    }
