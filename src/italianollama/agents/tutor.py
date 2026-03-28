"""Language tutor agent using LLM and memory graph."""

from dataclasses import dataclass
import logging
import uuid

from italianollama.llm.client import LLMClient
from italianollama.memory.graph import MemoryGraph

logger = logging.getLogger(__name__)


@dataclass
class ChatResponse:
    """Response from the tutor."""

    response: str
    session_id: str
    vocabulary: list[dict] | None = None
    grammar_notes: list[str] | None = None


class LanguageTutor:
    """AI-powered language tutor using LLM and knowledge graph.

    Provides conversational language learning with memory of vocabulary,
    grammar rules, and learning history.
    """

    # System prompts for different levels
    SYSTEM_PROMPTS = {
        "beginner": """You are a patient Italian language tutor for beginners.
- Use simple vocabulary and short sentences
- Always provide translations in English
- Explain grammar in simple terms
- Encourage the learner
- Correct errors gently
- Use lots of examples
- Ask follow-up questions to check understanding
""",
        "intermediate": """You are an Italian language tutor for intermediate learners.
- Use natural Italian phrases and idioms
- Provide explanations in both Italian and English
- Focus on nuance and context
- Introduce more complex grammar gradually
- Encourage fluent conversation
- Correct subtle errors in usage
""",
        "advanced": """You are an advanced Italian language tutor.
- Discuss complex topics in Italian
- Focus on nuance, idiom usage, and cultural context
- Teach literary and formal register
- Provide sophisticated vocabulary alternatives
- Discuss regional variations
""",
    }

    # Topic-specific vocabulary
    TOPIC_VOCABULARY = {
        "daily_conversation": [
            "buongiorno",
            "grazie",
            "prego",
            "scusa",
            "arrivederci",
            "come stai",
            "bene grazie",
            "non capisco",
        ],
        "food_and_dining": [
            "il menu",
            "il conto",
            "primo",
            "secondo",
            "dolce",
            "vino",
            "caffè",
            "acqua",
            "buon appetito",
        ],
        "travel": [
            "l'aeroporto",
            "la stazione",
            "l'hotel",
            "la prenotazione",
            "biglietto",
            "passaporto",
            "valigia",
        ],
        "healthcare": [
            "l'ospedale",
            "il medico",
            "la pharmacy",
            "il dolore",
            "la ricetta",
            "l'appuntamento",
        ],
        "science": [
            "la ricerca",
            "l'esperimento",
            "il laboratorio",
            "l'ipotesi",
            "la conclusione",
            "i dati",
        ],
    }

    def __init__(
        self,
        llm_client: LLMClient,
        memory: MemoryGraph,
        default_language: str = "italian",
        default_level: str = "intermediate",
    ):
        """Initialize the language tutor.

        Args:
            llm_client: LLM client for generating responses
            memory: Knowledge graph for storing learning data
            default_language: Default target language
            default_level: Default proficiency level
        """
        self.llm_client = llm_client
        self.memory = memory
        self.default_language = default_language
        self.default_level = default_level

        logger.info(f"LanguageTutor initialized for {default_language}")

    async def chat(
        self,
        message: str,
        language: str | None = None,
        level: str | None = None,
        session_id: str | None = None,
    ) -> ChatResponse:
        """Chat with the language tutor.

        Args:
            message: User's message
            language: Target language (defaults to Italian)
            level: Proficiency level (beginner/intermediate/advanced)
            session_id: Optional session ID for conversation continuity

        Returns:
            ChatResponse with tutor's reply and metadata
        """
        language = language or self.default_language
        level = level or self.default_level
        session_id = session_id or str(uuid.uuid4())

        # Create session if it doesn't exist
        await self.memory.create_session(session_id=session_id, language=language, level=level)

        # Get conversation history
        session = await self.memory.get_session(session_id)
        messages = self._build_messages(message, language, level, session)

        # Get relevant vocabulary from memory
        relevant_vocab = await self._get_relevant_vocabulary(message, language)

        # Generate response
        system_prompt = self._build_system_prompt(language, level, relevant_vocab)

        try:
            response = await self.llm_client.generate(
                prompt=message, system_prompt=system_prompt, messages=messages
            )
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            response = "Mi dispiace, ho avuto un problema. Per favore, riprova. (Sorry, I had a problem. Please try again.)"

        # Extract vocabulary from response for storage
        vocab_learned = await self._extract_and_store_vocabulary(response, language)

        # Store conversation in memory
        await self.memory.add_message(
            session_id=session_id, role="user", content=message, vocabulary_learned=vocab_learned
        )
        await self.memory.add_message(
            session_id=session_id,
            role="assistant",
            content=response,
            vocabulary_learned=vocab_learned,
        )

        return ChatResponse(
            response=response,
            session_id=session_id,
            vocabulary=relevant_vocab[:5] if relevant_vocab else None,
            grammar_notes=None,
        )

    def _build_system_prompt(self, language: str, level: str, relevant_vocab: list[dict]) -> str:
        """Build the system prompt with context."""
        base_prompt = self.SYSTEM_PROMPTS.get(level, self.SYSTEM_PROMPTS["intermediate"])

        # Add relevant vocabulary context
        if relevant_vocab:
            vocab_list = ", ".join([v["word"] for v in relevant_vocab])
            base_prompt += f"\n\nRelevant vocabulary from previous lessons: {vocab_list}"

        # Add language-specific instructions
        if language == "italian":
            base_prompt += "\n\nCurrent focus: Italian language learning."

        return base_prompt

    def _build_messages(
        self, current_message: str, language: str, level: str, session: dict | None
    ) -> list[dict]:
        """Build message history for context."""
        messages = []

        # Add system prompt
        system_prompt = self._build_system_prompt(language, level, [])
        messages.append({"role": "system", "content": system_prompt})

        # Add conversation history (last 10 messages)
        if session and "messages" in session:
            for msg in session["messages"][-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})

        return messages

    async def _get_relevant_vocabulary(self, message: str, language: str) -> list[dict]:
        """Get vocabulary relevant to the user's message."""
        # Simple keyword matching
        message_lower = message.lower()

        # Check for topic keywords
        topics = []
        topic_keywords = {
            "food": ["food", "eat", "restaurant", "cibo", "mangiare", "ristorante"],
            "travel": ["travel", "hotel", "airport", "viaggio", "hotel", "aereoporto"],
            "health": ["health", "doctor", "hospital", "salute", "medico", "ospedale"],
            "science": ["science", "research", "experiment", "scienza", "ricerca"],
            "daily": ["hello", "thank", "please", "grazie", "prego", "buongiorno"],
        }

        for topic, keywords in topic_keywords.items():
            if any(kw in message_lower for kw in keywords):
                topics.append(topic)

        # Get vocabulary for identified topics
        all_vocab = []
        for topic in topics:
            topic_name = f"{topic}_conversation" if topic != "daily" else "daily_conversation"
            vocab = await self.memory.get_vocabulary(language=language, topic=topic_name, limit=10)
            all_vocab.extend(vocab)

        # If no topics found, get recent vocabulary
        if not all_vocab:
            all_vocab = await self.memory.get_vocabulary(language=language, limit=10)

        return all_vocab

    async def _extract_and_store_vocabulary(self, text: str, language: str) -> list[str]:
        """Extract and store new vocabulary from tutor response.

        This is a simplified version - in production, use NLP for extraction.
        """
        # Simple Italian word list for demo
        common_italian_words = [
            "grazie",
            "prego",
            "scusa",
            "buongiorno",
            "buonasera",
            "arrivederci",
            "perfetto",
            "molto",
            "bene",
            "bene",
            "capisco",
            "non capisco",
            "come",
            "stai",
            "oggi",
            "ieri",
            "domani",
            "ora",
            "adesso",
            "mai",
            "sempre",
        ]

        words_found = []
        text_lower = text.lower()

        for word in common_italian_words:
            if word in text_lower and len(word) > 3:
                words_found.append(word)

        return words_found[:3]  # Limit to 3 words per response

    async def teach_vocabulary_topic(self, topic: str, language: str = "italian") -> str:
        """Teach vocabulary for a specific topic.

        Args:
            topic: Topic name (e.g., "food", "travel")
            language: Target language

        Returns:
            Lesson content as string
        """
        topic_key = f"{topic}_conversation"
        vocab_words = self.TOPIC_VOCABULARY.get(topic_key, [])

        if not vocab_words:
            return f"Topic '{topic}' not found."

        # Create vocabulary items in memory
        for word in vocab_words:
            await self.memory.add_vocabulary(
                word=word,
                translation="",  # Would need translation API
                examples=[],
                topic=topic_key,
                language=language,
            )

        # Generate lesson using LLM
        prompt = f"Teach me {len(vocab_words)} Italian vocabulary words for the topic '{topic}'. Provide the words and their English translations."

        try:
            response = await self.llm_client.generate(
                prompt=prompt, system_prompt=self.SYSTEM_PROMPTS["beginner"]
            )
            return response
        except Exception as e:
            logger.error(f"Lesson generation failed: {e}")
            return "Sorry, I couldn't generate the lesson. Please try again."

    async def quiz_vocabulary(
        self, topic: str | None = None, count: int = 5, language: str = "italian"
    ) -> dict:
        """Generate a vocabulary quiz.

        Args:
            topic: Optional topic filter
            count: Number of questions
            language: Target language

        Returns:
            Quiz questions and answers
        """
        # Get vocabulary from memory
        vocab = await self.memory.get_vocabulary(language=language, topic=topic, limit=count * 2)

        if len(vocab) < count:
            # Fallback to default vocabulary
            all_topics = list(self.TOPIC_VOCABULARY.keys())
            vocab = []
            for t in all_topics:
                for word in self.TOPIC_VOCABULARY[t]:
                    vocab.append({"word": word, "topic": t, "translation": ""})
                    if len(vocab) >= count * 2:
                        break
                if len(vocab) >= count * 2:
                    break

        # Generate quiz questions
        prompt = f"Create a {count}-question Italian vocabulary quiz. For each question, show an Italian word and ask for the English translation."

        # Add vocabulary context
        if vocab:
            vocab_context = "\n".join(
                [f"- {v['word']}: {v.get('translation', '?')}" for v in vocab[: count * 2]]
            )
            prompt += f"\n\nUse these words:\n{vocab_context}"

        try:
            questions = await self.llm_client.generate(
                prompt=prompt,
                system_prompt="You are a vocabulary quiz generator. Create clear, simple questions.",
            )

            return {"questions": questions, "vocabulary": vocab[:count], "topic": topic or "mixed"}
        except Exception as e:
            logger.error(f"Quiz generation failed: {e}")
            return {"error": "Failed to generate quiz"}

    def __repr__(self) -> str:
        return f"LanguageTutor(language={self.default_language}, level={self.default_level})"
