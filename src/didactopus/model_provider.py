from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Callable
from urllib import request

from .config import ModelProviderConfig
from .roles import get_role


@dataclass
class ModelResponse:
    text: str
    provider: str
    model_name: str


class ModelProvider:
    def __init__(self, config: ModelProviderConfig) -> None:
        self.config = config

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
        if provider_name == "rolemesh":
            return self._generate_rolemesh(prompt, role, system_prompt, temperature, max_tokens, status_callback)
        if provider_name == "ollama":
            return self._generate_ollama(prompt, role, system_prompt, temperature, max_tokens, status_callback)
        if provider_name == "openai_compatible":
            return self._generate_openai_compatible(prompt, role, system_prompt, temperature, max_tokens, status_callback)
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

    def _generate_rolemesh(
        self,
        prompt: str,
        role: str | None,
        system_prompt: str | None,
        temperature: float | None,
        max_tokens: int | None,
        status_callback: Callable[[str], None] | None,
    ) -> ModelResponse:
        rolemesh = self.config.rolemesh
        model_name = rolemesh.role_to_model.get(role or "", rolemesh.default_model)
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
        body = self._rolemesh_chat_completion(payload)
        return self._response_from_chat_completion(body, provider="rolemesh", model_name=model_name)

    def _generate_ollama(
        self,
        prompt: str,
        role: str | None,
        system_prompt: str | None,
        temperature: float | None,
        max_tokens: int | None,
        status_callback: Callable[[str], None] | None,
    ) -> ModelResponse:
        ollama = self.config.ollama
        model_name = ollama.role_to_model.get(role or "", ollama.default_model)
        if status_callback is not None:
            status_callback(self.pending_notice(role, model_name))
        payload = self._build_messages_payload(prompt, system_prompt, model_name, temperature, max_tokens)
        body = self._chat_completion_request(
            base_url=ollama.base_url,
            api_key=ollama.api_key,
            timeout_seconds=ollama.timeout_seconds,
            payload=payload,
            auth_scheme="bearer",
        )
        return self._response_from_chat_completion(body, provider="ollama", model_name=model_name)

    def _generate_openai_compatible(
        self,
        prompt: str,
        role: str | None,
        system_prompt: str | None,
        temperature: float | None,
        max_tokens: int | None,
        status_callback: Callable[[str], None] | None,
    ) -> ModelResponse:
        compat = self.config.openai_compatible
        model_name = compat.role_to_model.get(role or "", compat.default_model)
        if status_callback is not None:
            status_callback(self.pending_notice(role, model_name))
        payload = self._build_messages_payload(prompt, system_prompt, model_name, temperature, max_tokens)
        body = self._chat_completion_request(
            base_url=compat.base_url,
            api_key=compat.api_key,
            timeout_seconds=compat.timeout_seconds,
            payload=payload,
            auth_scheme=compat.auth_scheme,
        )
        return self._response_from_chat_completion(body, provider="openai_compatible", model_name=model_name)

    def _build_messages_payload(
        self,
        prompt: str,
        system_prompt: str | None,
        model_name: str,
        temperature: float | None,
        max_tokens: int | None,
    ) -> dict:
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
        return payload

    def _response_from_chat_completion(self, body: dict, *, provider: str, model_name: str) -> ModelResponse:
        choices = body.get("choices", [])
        if not choices:
            raise RuntimeError(f"{provider} returned no choices.")
        message = choices[0].get("message", {})
        text = message.get("content", "")
        if not isinstance(text, str):
            text = str(text)
        return ModelResponse(text=text, provider=provider, model_name=model_name)

    def _rolemesh_chat_completion(self, payload: dict) -> dict:
        rolemesh = self.config.rolemesh
        return self._chat_completion_request(
            base_url=rolemesh.base_url,
            api_key=rolemesh.api_key,
            timeout_seconds=rolemesh.timeout_seconds,
            payload=payload,
            auth_scheme="x-api-key",
        )

    def _chat_completion_request(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout_seconds: float,
        payload: dict,
        auth_scheme: str,
    ) -> dict:
        url = base_url.rstrip("/") + "/chat/completions" if base_url.rstrip("/").endswith("/v1") else base_url.rstrip("/") + "/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
        }
        if api_key:
            if auth_scheme == "x-api-key":
                headers["X-Api-Key"] = api_key
            else:
                headers["Authorization"] = f"Bearer {api_key}"
        req = request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with request.urlopen(req, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
