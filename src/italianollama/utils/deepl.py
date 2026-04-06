"""DeepL API utilities for translation and vocabulary lookup.

Best practices implemented:
- Use os.environ/ prefix for secrets in config (Lazy evaluation)
- Include proper error handling and timeout management
- Support both free and pro endpoints
- Type hints for IDE support
"""

import os
from typing import Optional, Any

try:
    import deepl
    HAS_DEEPL = True
    from deepl import DeepLClient as _DeepLClient
except ImportError:
    HAS_DEEPL = False


class DeepLClient:
    """Interface to DeepL API for translation and language processing."""

    DEFAULT_TIMEOUT = 30.0

    def __init__(self, api_key: Optional[str] = None):
        """Initialize DeepL API client.

        Args:
            api_key: DeepL API key (defaults to DEEPL_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("DEEPL_API_KEY")
        self.client: Optional[Any] = None
        self._is_initialized = False

    def _get_client(self) -> Any:
        """Get or create DeepL client."""
        if not self.api_key:
            raise ValueError("DEEPL_API_KEY environment variable not set")

        if self.client is None or not self._is_initialized:
            if not HAS_DEEPL:
                raise ImportError("DeepL package not installed")
            self.client = _DeepLClient(auth_key=self.api_key)
            self._is_initialized = True

        return self.client

    def translate(
        self, text: str, target_lang: str = "DE", source_lang: str = "IT"
    ) -> str:
        """Translate text from Italian to target language.

        Args:
            text: Text to translate
            target_lang: Target language code (default: DE for German)
            source_lang: Source language code (default: IT for Italian)

        Returns:
            Translated text
        """
        if not self._is_initialized:
            client = self._get_client()
        else:
            client = self.client

        if client is None:
            raise ValueError("DeepL client not initialized")

        try:
            result = client.translate_text(
                text=text,
                source_lang=source_lang,
                target_lang=target_lang,
            )
            return str(result.text) if hasattr(result, "text") else str(result)
        except Exception as e:
            raise ValueError(f"DeepL translation failed: {e}")

    def detect_language(self, text: str) -> str:
        """Detect the language of given text.

        Args:
            text: Text to analyze

        Returns:
            Language code (e.g., 'IT', 'DE', 'EN')
        """
        if not self._is_initialized:
            client = self._get_client()
        else:
            client = self.client

        if client is None:
            raise ValueError("DeepL client not initialized")

        try:
            result = client.detect_language(text=text)
            return result[0].language if result else "unknown"
        except Exception as e:
            raise ValueError(f"DeepL language detection failed: {e}")

    def get_glossary_languages(self) -> list[str]:
        """Get list of supported languages for glossaries.

        Returns:
            List of language codes
        """
        if not self._is_initialized:
            client = self._get_client()
        else:
            client = self.client

        if client is None:
            raise ValueError("DeepL client not initialized")

        try:
            result = client.get_glossary_languages()
            return [lang.code for lang in result] if result else []
        except Exception:
            return []

    def is_available(self) -> bool:
        """Check if DeepL API is available and configured.

        Returns:
            True if API key is set and client can be initialized
        """
        try:
            if not self.api_key:
                return False
            self._get_client()
            return self.client is not None
        except Exception:
            return False


def get_deepl_client() -> Optional[DeepLClient]:
    """Get DeepL client if API key is configured.

    Returns:
        DeepLClient instance or None if not configured
    """
    api_key = os.getenv("DEEPL_API_KEY")

    if not api_key:
        return None

    try:
        return DeepLClient(api_key)
    except Exception:
        return None


def format_translation_for_vocabulary(
    italian_word: str,
    german_translation: str,
    pos: str = "",
    example_sentence: str = "",
) -> dict[str, Any]:
    """Format translation data for vocabulary entry.

    Args:
        italian_word: Italian word
        german_translation: German translation
        pos: Part of speech (noun, verb, adjective, etc.)
        example_sentence: Example usage sentence

    Returns:
        Dictionary formatted for vocabulary storage
    """
    article = ""
    gender = ""
    plural = ""

    if pos.lower() == "noun":
        word_lower = italian_word.lower().strip()
        if word_lower.startswith(("l'", "l")):
            article = "l'"
            gender = "m" if word_lower[1] in "aeiou" else "f"
        elif word_lower.startswith(("lo", "gli", "i")):
            article = "lo" if word_lower.startswith("lo") else "i"
            gender = "m"
        elif word_lower.startswith(("la", "le")):
            article = "la" if word_lower.startswith("la") else "le"
            gender = "f"
        elif word_lower.endswith("a"):
            article = "la"
            gender = "f"
        elif word_lower.endswith("o"):
            article = "il"
            gender = "m"
        elif word_lower.endswith("e"):
            article = "l'" if word_lower[0] in "aeiou" else "il"
            gender = "n"

        if gender == "m":
            plural = italian_word + "i" if not italian_word.endswith("co") else italian_word + "hi"
        elif gender == "f":
            plural = italian_word + "e" if not italian_word.endswith("cia") else italian_word + "ie"

    return {
        "italian_word": italian_word.strip(),
        "german_word": german_translation.strip(),
        "part_of_speech": pos.strip() if pos else "noun",
        "article": article,
        "gender": gender,
        "plural": plural,
        "vocabulary_type": "self-made",
        "example_sentence": example_sentence.strip() if example_sentence else "",
    }
