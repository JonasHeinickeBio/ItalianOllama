"""LLM client using hellmholtz for multi-provider support.

This module provides a unified interface for interacting with various LLM providers
including Ollama, OpenAI, Anthropic, and Helmholtz Blablador through hellmholtz.
"""

import logging
import os

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified LLM client using hellmholtz/aisuite.

    Supports multiple providers: ollama, openai, anthropic, helmholtz (blablador)
    """

    def __init__(
        self,
        provider: str = "ollama",
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        """Initialize the LLM client.

        Args:
            provider: LLM provider name (ollama, openai, anthropic, helmholtz)
            model: Model name (defaults to provider-specific default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.provider = provider
        self.model = model or self._get_default_model(provider)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None
        self._hellmholtz_client = None

        logger.info(f"Initializing LLM client with provider: {provider}, model: {self.model}")
        self._initialize_client()

    def _get_default_model(self, provider: str) -> str:
        """Get default model for a provider."""
        defaults = {
            "ollama": "llama3.2",
            "openai": "gpt-4o",
            "anthropic": "claude-3-5-sonnet-20241022",
            "helmholtz": "alias-fast",
            "blablador": "alias-fast",
        }
        return defaults.get(provider, "llama3.2")

    def _initialize_client(self):
        """Initialize the hellmholtz/aisuite client."""
        try:
            # Try to import from hellmholtz (which includes aisuite)
            from hellmholtz.llm import ChatLLM

            # Get provider configuration
            config = self._get_provider_config()

            # Initialize hellmholtz ChatLLM
            self._hellmholtz_client = ChatLLM(
                provider=self.provider,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **config,
            )

            logger.info(f"Successfully initialized hellmholtz client for {self.provider}")
            self._client = self._hellmholtz_client

        except ImportError:
            logger.warning("hellmholtz not installed, trying direct aisuite")
            self._initialize_aisuite_fallback()
        except Exception as e:
            logger.error(f"Failed to initialize hellmholtz client: {e}")
            self._initialize_aisuite_fallback()

    def _initialize_aisuite_fallback(self):
        """Fallback to direct aisuite if hellmholtz fails."""
        try:
            import aisuite as ai

            config = self._get_provider_config()
            self._client = ai.Client(config)
            logger.info(f"Initialized aisuite fallback for {self.provider}")

        except ImportError:
            logger.warning("aisuite not available, using direct API calls")
            self._client = None
        except Exception as e:
            logger.error(f"Failed to initialize aisuite: {e}")
            self._client = None

    def _get_provider_config(self) -> dict:
        """Get provider configuration from environment variables."""
        config = {}

        # Get API URL and key
        if self.provider in ("ollama", "helmholtz", "blablador"):
            base_url = os.getenv("BLABLADOR_API_URL") or os.getenv(
                "OLLAMA_BASE_URL", "http://localhost:11434"
            )
            api_key = os.getenv("BLABLADOR_API_KEY") or os.getenv("OLLAMA_API_KEY", "not-needed")

            config["base_url"] = base_url
            config["api_key"] = api_key

        elif self.provider == "openai":
            config["api_key"] = os.getenv("OPENAI_API_KEY", "")

        elif self.provider == "anthropic":
            config["api_key"] = os.getenv("ANTHROPIC_API_KEY", "")

        return config

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs,
    ) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model: Override default model
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional provider-specific arguments

        Returns:
            Generated text response
        """
        model = model or self.model
        temperature = temperature or self.temperature
        max_tokens = max_tokens or self.max_tokens

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            if self._hellmholtz_client:
                # Use hellmholtz ChatLLM
                response = self._hellmholtz_client.chat(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                )
                return response
            elif self._client:
                # Use aisuite directly
                response = self._client.chat.completions.create(
                    model=self._provider_to_model(model),
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                )
                return response.choices[0].message.content
            else:
                # Fallback: direct API call
                return await self._direct_generate(messages, model, temperature, max_tokens)

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise

    def _provider_to_model(self, model: str) -> str:
        """Convert model name to provider-specific format."""
        # For aisuite, model format is "provider:model"
        return f"{self.provider}:{model}"

    async def _direct_generate(
        self, messages: list[dict], model: str, temperature: float, max_tokens: int
    ) -> str:
        """Direct API call fallback."""
        import requests

        if self.provider in ("ollama", "helmholtz", "blablador"):
            base_url = os.getenv("BLABLADOR_API_URL") or os.getenv(
                "OLLAMA_BASE_URL", "http://localhost:11434"
            )
            api_key = os.getenv("BLABLADOR_API_KEY") or os.getenv("OLLAMA_API_KEY", "not-needed")

            url = f"{base_url}chat/completions"
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            response = requests.post(url, json=payload, headers=headers, timeout=120)
            response.raise_for_status()

            return response.json()["choices"][0]["message"]["content"]

        raise ValueError(f"Direct API not supported for provider: {self.provider}")

    async def chat(self, messages: list[dict], model: str | None = None, **kwargs) -> str:
        """Chat with conversation history.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Optional model override
            **kwargs: Additional arguments

        Returns:
            Assistant response
        """
        model = model or self.model

        try:
            if self._hellmholtz_client:
                return self._hellmholtz_client.chat(messages=messages, model=model, **kwargs)
            elif self._client:
                response = self._client.chat.completions.create(
                    model=self._provider_to_model(model), messages=messages, **kwargs
                )
                return response.choices[0].message.content
            else:
                # Extract user message for fallback
                user_msg = next((m for m in messages if m.get("role") == "user"), {"content": ""})
                return await self._direct_generate(
                    messages, model, self.temperature, self.max_tokens
                )

        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise

    def __repr__(self) -> str:
        return f"LLMClient(provider={self.provider}, model={self.model})"
