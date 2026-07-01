from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Callable
from urllib import parse, request

from .config import ModelProviderConfig
from .roles import get_role


@dataclass
class ModelResponse:
    text: str
    provider: str
    model_name: str


class ModelProvider:
    def __init__(self, config: ModelProviderConfig, role_model_overrides: dict[str, str] | None = None) -> None:
        self.config = config
        self.role_model_overrides = dict(role_model_overrides or {})

    def with_role_model_overrides(self, role_model_overrides: dict[str, str] | None) -> ModelProvider:
        merged = dict(self.role_model_overrides)
        if role_model_overrides:
            merged.update(role_model_overrides)
        return ModelProvider(self.config, role_model_overrides=merged)

    def pending_notice(self, role: str | None, model_name: str | None = None) -> str:
        spec = get_role(role or "")
        notice = spec.pending_notice if spec is not None else "Didactopus is preparing the next response."
        if model_name:
            return f"{notice} Model: {model_name}."
        return notice

    def generate(
        self,
        prompt: str,
        role: str | None = None,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        status_callback: Callable[[str], None] | None = None,
    ) -> ModelResponse:
        provider_name = self.config.provider.lower()
        if provider_name in {"rolemesh", "geniehive", "gateway"}:
            return self._generate_gateway(prompt, role, system_prompt, temperature, max_tokens, status_callback)
        return self._generate_stub(prompt, role)

    def _generate_stub(self, prompt: str, role: str | None) -> ModelResponse:
        local = self.config.local
        preview = prompt.strip().replace("\n", " ")[:120]
        role_text = f"[{role}] " if role else ""
        return ModelResponse(
            text=f"[stubbed-response] {role_text}{preview}",
            provider=local.backend,
            model_name=local.model_name,
        )

    def _generate_gateway(
        self,
        prompt: str,
        role: str | None,
        system_prompt: str | None,
        temperature: float | None,
        max_tokens: int | None,
        status_callback: Callable[[str], None] | None,
    ) -> ModelResponse:
        gateway = self.config.gateway
        provider_name = self.config.provider.lower()
        model_name = self.role_model_overrides.get(role or "", gateway.role_to_model.get(role or "", gateway.default_model))
        if status_callback is not None:
            status_callback(self.pending_notice(role, model_name))
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": model_name,
            "messages": messages,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        body = self._rolemesh_chat_completion(payload) if provider_name == "rolemesh" else self._gateway_chat_completion(payload)
        choices = body.get("choices", [])
        if not choices:
            raise RuntimeError(f"{provider_name} returned no choices.")
        message = choices[0].get("message", {})
        text = message.get("content", "")
        if not isinstance(text, str):
            text = str(text)
        return ModelResponse(text=text, provider=provider_name, model_name=model_name)

    def list_models(self) -> list[dict]:
        provider_name = self.config.provider.lower()
        if provider_name not in {"rolemesh", "geniehive", "gateway"}:
            return []
        return self._rolemesh_list_models() if provider_name == "rolemesh" else self._gateway_list_models()

    def resolve_route(self, model: str, *, kind: str | None = None) -> dict | None:
        provider_name = self.config.provider.lower()
        if provider_name not in {"rolemesh", "geniehive", "gateway"}:
            return None
        return self._rolemesh_resolve_route(model, kind=kind) if provider_name == "rolemesh" else self._gateway_resolve_route(model, kind=kind)

    def _gateway_chat_completion(self, payload: dict) -> dict:
        gateway = self.config.gateway
        url = gateway.base_url.rstrip("/") + "/v1/chat/completions"
        headers = self._gateway_headers(content_type="application/json")
        req = request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with request.urlopen(req, timeout=gateway.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    def _gateway_list_models(self) -> list[dict]:
        gateway = self.config.gateway
        url = gateway.base_url.rstrip("/") + "/v1/models"
        req = request.Request(url, headers=self._gateway_headers(), method="GET")
        with request.urlopen(req, timeout=gateway.timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
        data = body.get("data", [])
        return [item for item in data if isinstance(item, dict)]

    def _gateway_resolve_route(self, model: str, *, kind: str | None = None) -> dict | None:
        gateway = self.config.gateway
        params = {"model": model}
        if kind is not None:
            params["kind"] = kind
        url = gateway.base_url.rstrip("/") + "/v1/cluster/routes/resolve?" + parse.urlencode(params)
        req = request.Request(url, headers=self._gateway_headers(), method="GET")
        try:
            with request.urlopen(req, timeout=gateway.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except Exception:
            return None
        resolution = body.get("resolution")
        return resolution if isinstance(resolution, dict) else None

    def _gateway_headers(self, *, content_type: str | None = None) -> dict[str, str]:
        headers: dict[str, str] = {}
        if content_type:
            headers["Content-Type"] = content_type
        gateway = self.config.gateway
        if gateway.api_key:
            headers["X-Api-Key"] = gateway.api_key
        return headers

    def _rolemesh_list_models(self) -> list[dict]:
        return self._gateway_list_models()

    def _rolemesh_resolve_route(self, model: str, *, kind: str | None = None) -> dict | None:
        return self._gateway_resolve_route(model, kind=kind)

    # Compatibility alias while RoleMesh-named demos and tests still exist.
    def _rolemesh_chat_completion(self, payload: dict) -> dict:
        return self._gateway_chat_completion(payload)
