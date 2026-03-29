"""Base node utilities for LangGraph nodes."""

import os


class LLMClient:
    """LiteLLM wrapper for unified LLM access.

    Supports: Ollama, OpenAI, Anthropic, Blablador via LiteLLM.
    """

    def __init__(self):
        self.base_url = os.getenv("LITELLM_BASE_URL", "http://litellm:4000")
        self.api_key = os.getenv("LITELLM_API_KEY", "dummy")
        self.model = os.getenv("LITELLM_MODEL", "tutor")

    async def chat(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Send chat request to LiteLLM."""
        import httpx

        # Build messages with system prompt
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": all_messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
            )

            if response.status_code != 200:
                raise Exception(f"LiteLLM error: {response.text}")

            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def chat_with_json(
        self,
        messages: list[dict],
        response_schema: dict,
        system_prompt: str | None = None,
    ) -> dict:
        """Send chat request expecting JSON response."""
        import httpx

        # Add JSON schema instruction
        schema_instruction = f"""
You must respond with valid JSON only. No other text.

Response schema:
{response_schema}
"""

        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt + schema_instruction})
        else:
            all_messages.append({"role": "system", "content": schema_instruction})
        all_messages.extend(messages)

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": all_messages,
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"},
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
            )

            if response.status_code != 200:
                raise Exception(f"LiteLLM error: {response.text}")

            result = response.json()
            import json

            return json.loads(result["choices"][0]["message"]["content"])


def create_llm_client() -> LLMClient:
    """Factory function for LLM client."""
    return LLMClient()
