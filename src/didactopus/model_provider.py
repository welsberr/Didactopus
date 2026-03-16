from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Callable
from urllib import request

from .config import ModelProviderConfig


@dataclass
class ModelResponse:
    text: str
    provider: str
    model_name: str


class ModelProvider:
    def __init__(self, config: ModelProviderConfig) -> None:
        self.config = config

    def pending_notice(self, role: str | None, model_name: str | None = None) -> str:
        label = role or "assistant"
        notices = {
            "mentor": "Didactopus is reviewing the next learning step before answering.",
            "learner": "Didactopus is drafting the learner-side reflection now.",
            "practice": "Didactopus is designing a practice task for you now.",
            "project_advisor": "Didactopus is sketching a project direction now.",
            "evaluator": "Didactopus is evaluating the work before replying.",
        }
        notice = notices.get(label, "Didactopus is preparing the next response.")
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
        choices = body.get("choices", [])
        if not choices:
            raise RuntimeError("RoleMesh returned no choices.")
        message = choices[0].get("message", {})
        text = message.get("content", "")
        if not isinstance(text, str):
            text = str(text)
        return ModelResponse(text=text, provider="rolemesh", model_name=model_name)

    def _rolemesh_chat_completion(self, payload: dict) -> dict:
        rolemesh = self.config.rolemesh
        url = rolemesh.base_url.rstrip("/") + "/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
        }
        if rolemesh.api_key:
            headers["X-Api-Key"] = rolemesh.api_key
        req = request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with request.urlopen(req, timeout=rolemesh.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
