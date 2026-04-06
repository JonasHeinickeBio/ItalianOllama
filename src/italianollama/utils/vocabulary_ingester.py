"""Vocabulary ingestion utilities for ItalianOllama."""

import json
import os
from typing import Optional

from italianollama.memory.learning import LearningManager
from italianollama.memory.neo4j_client import Neo4jClient


class VocabularyIngester:
    """Ingest vocabulary from JSON files into Neo4j graph."""

    def __init__(self, client: Neo4jClient):
        """Initialize ingester with Neo4j client.

        Args:
            client: Neo4jClient instance
        """
        self.client = client

    async def ingest_from_file(
        self, filepath: str, student_id: str = "admin"
    ) -> int:
        """Ingest vocabulary from JSON file.

        Args:
            filepath: Path to JSON file with vocabulary entries
            student_id: Student ID to associate vocabulary with

        Returns:
            Number of words ingested
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                vocabulary_list = json.load(f)
        except FileNotFoundError:
            print(f"✗ File not found: {filepath}")
            return 0
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON: {e}")
            return 0

        ingested = 0
        for entry in vocabulary_list:
            try:
                word = entry.get("italian_word", "").strip()
                if not word:
                    continue

                article = ""
                gender = ""
                plural = ""

                if entry.get("part_of_speech") == "noun":
                    gender = entry.get("gender", "")
                    if not gender:
                        gender = self._guess_gender(word.lower())

                    article = self._determine_article(word.lower(), gender)

                await self.client.learning.add_vocabulary(
                    student_id=student_id,
                    word=word,
                    definition=entry.get("german_word", ""),
                    topic=entry.get("topic", "general"),
                    confidence=0.8,
                    article=article,
                    gender=gender,
                    plural=plural,
                    cefr_level=entry.get("cefr_level", ""),
                    part_of_speech=entry.get("part_of_speech", ""),
                    italian_plural=entry.get("plural", ""),
                    german_word=entry.get("german_word", ""),
                )
                ingested += 1

            except Exception as e:
                print(f"  ⚠ Error ingesting {word}: {e}")
                continue

        return ingested

    def _determine_article(self, word: str, gender: str = "") -> str:
        """Determine Italian article based on word.

        Args:
            word: Italian word
            gender: Known gender (m, f) if available

        Returns:
            Article (il, la, l', lo, i, le, gli, l')
        """
        if not word:
            return ""

        vowels = "aeiou"

        special_cases = {
            "l'": ["uomo", "ufficio", "università", "ultimo", "unico"],
            "lo": ["stomaco", "psicologo", "zoo", "sfogo", "psiche", "scuola"],
            "i": ["stomaci", "psicologi", "zoo", "sfoghi"],
            "gli": ["lunedì", "lì", "ieri", "oggi", "inglese", "francese"],
        }

        for article, words in special_cases.items():
            if word in words:
                return article

        if word[0] in vowels:
            return "l'"
        elif gender == "m":
            if word[0] in "sz":
                return "lo"
            elif word[0] in "gh":
                return "il"
            elif word[0] in "bcdfjlmnpqrstvwxyz":
                return "lo"
            else:
                return "il"
        else:
            return "la"

    def _guess_gender(self, word: str) -> str:
        """Guess Italian noun gender based on ending.

        Args:
            word: Italian word

        Returns:
            Gender: 'm', 'f', or 'n' (neutral/unknown)
        """
        word_lower = word.lower()

        if word_lower.endswith(("one", "atore", "otto", "ismo", "ista", "ai")):
            return "m"
        elif word_lower.endswith(("onna", "atrice", "ità", "ione", "ante", "iste", "ade")):
            return "f"
        elif word_lower.endswith("e"):
            return "n"

        if word_lower.endswith("a"):
            return "f"
        elif word_lower.endswith("o"):
            return "m"
        elif word_lower.endswith("i"):
            return "m"

        return "n"


async def ingest_default_vocabulary(
    client: Neo4jClient, student_id: str = "admin"
) -> int:
    """Ingest default vocabulary from built-in dataset.

    Args:
        client: Neo4jClient instance
        student_id: Student ID to associate vocabulary with

    Returns:
        Number of words ingested
    """
    ingester = VocabularyIngester(client)

    default_file = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "data", "vocabulary_extracted.json"
    )

    if not os.path.exists(default_file):
        print(f"✗ Default vocabulary file not found: {default_file}")
        return 0

    print(f"📖 Ingesting default vocabulary from {default_file}")
    count = await ingester.ingest_from_file(default_file, student_id)
    print(f"✓ Ingested {count} vocabulary words")
    return count


async def main():
    """Main entry point for vocabulary ingestion."""
    import sys

    from italianollama.memory.neo4j_client import Neo4jClient

    print("📚 ItalianOllama Vocabulary Ingester")
    print("=" * 50)

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "")
    database = os.getenv("NEO4J_DATABASE", "neo4j")

    print(f"🔗 Connecting to Neo4j at {uri}")
    client = Neo4jClient(uri=uri, user=user, password=password, database=database)

    try:
        await client.connect()

        student_id = os.getenv("DEFAULT_STUDENT_ID", "admin")
        print(f"👤 Using student_id: {student_id}")

        count = await ingest_default_vocabulary(client, student_id)

        print(f"\n✅ Ingestion complete: {count} words")

    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    finally:
        await client.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
