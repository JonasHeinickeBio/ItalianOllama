"""Vocabulary and exercise tracking."""

import logging

from italianollama.memory.base import Neo4jBaseClient

logger = logging.getLogger(__name__)


class LearningManager(Neo4jBaseClient):
    """Handles vocabulary, exercises, and error tracking."""

    async def add_vocabulary(
        self,
        student_id: str,
        word: str,
        definition: str = "",
        topic: str = "",
        confidence: float = 0.5,
        article: str = "",
        gender: str = "",
        plural: str = "",
        cefr_level: str = "",
        part_of_speech: str = "",
        italian_plural: str = "",
        german_word: str = "",
        vocabulary_type: str = "premade",
    ):
        """Add vocabulary word for student.

        Args:
            student_id: Student ID
            word: Italian word
            definition: Definition or translation
            topic: Vocabulary topic/category
            confidence: Confidence level (0.0-1.0)
            article: Article (il, la, l', lo, i, le, gli, l')
            gender: Gender (m, f, n)
            plural: Plural form
            cefr_level: CEFR level (A1.1, A1.2, etc.)
            part_of_speech: Noun, verb, adjective, etc.
            italian_plural: Italian plural form
            german_word: German translation
            vocabulary_type: Type (premade or self-made)
        """
        logger.info(f"📚 Adding vocabulary - student_id={student_id}, word={word}")
        query = """
        MERGE (s:Student {student_id: $student_id})
        MERGE (v:Vocabulary {word: $word})
        SET v.definition = $definition,
            v.topic = $topic,
            v.article = $article,
            v.gender = $gender,
            v.plural = $plural,
            v.cefr_level = $cefr_level,
            v.part_of_speech = $part_of_speech,
            v.italian_plural = $italian_plural,
            v.german_word = $german_word,
            v.vocabulary_type = $vocabulary_type,
            v.updated_at = datetime()
        MERGE (s)-[rel:KNOWS]->(v)
        SET rel.confidence = $confidence,
            rel.learned_at = datetime(),
            s.last_active = datetime()
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                word=word,
                definition=definition,
                topic=topic,
                confidence=confidence,
                article=article,
                gender=gender,
                plural=plural,
                cefr_level=cefr_level,
                part_of_speech=part_of_speech,
                italian_plural=italian_plural,
                german_word=german_word,
                vocabulary_type=vocabulary_type,
            )
        logger.info("✓ Vocabulary added")

    async def add_exercise(
        self,
        student_id: str,
        exercise_type: str,
        level: str,
        score: float,
        xp_earned: int = 10,
    ):
        """Record completed exercise.

        Args:
            student_id: Student ID
            exercise_type: Type of exercise (grammar, vocabulary, etc.)
            level: CEFR level of exercise
            score: Score as percentage (0-100)
            xp_earned: Experience points awarded
        """
        logger.info(
            f"✏️ Recording exercise - student_id={student_id}, type={exercise_type}, score={score}"
        )
        query = """
        MERGE (s:Student {student_id: $student_id})
        CREATE (e:Exercise {
            type: $exercise_type,
            level: $level,
            score: $score,
            xp_earned: $xp_earned,
            completed_at: datetime()
        })
        MERGE (s)-[:COMPLETED]->(e)
        SET s.total_xp = COALESCE(s.total_xp, 0) + $xp_earned,
            s.last_active = datetime()
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                exercise_type=exercise_type,
                level=level,
                score=score,
                xp_earned=xp_earned,
            )
        logger.info("✓ Exercise recorded")

    async def add_grammar_error(
        self,
        student_id: str,
        rule: str,
        context: str = "",
        correction: str = "",
    ):
        """Track grammar error.

        Args:
            student_id: Student ID
            rule: Grammar rule that was violated
            context: Example sentence with error
            correction: Corrected version
        """
        logger.info(f"🔴 Recording grammar error - student_id={student_id}, rule={rule}")
        query = """
        MERGE (s:Student {student_id: $student_id})
        MERGE (err:GrammarError {rule: $rule})
        SET err.context = $context,
            err.correction = $correction,
            err.updated_at = datetime()
        MERGE (s)-[rel:MADE_ERROR]->(err)
        SET rel.error_count = COALESCE(rel.error_count, 0) + 1,
            rel.last_error_at = datetime(),
            s.last_active = datetime()
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                rule=rule,
                context=context,
                correction=correction,
            )
        logger.info("✓ Grammar error recorded")

    async def get_vocabulary(
        self,
        student_id: str,
        limit: int = 50,
        vocabulary_type: str | None = None,
    ) -> list[dict]:
        """Get student's vocabulary list.

        Args:
            student_id: Student ID
            limit: Maximum number of words
            vocabulary_type: Filter by type (premade, self-made, or None for all)

        Returns:
            List of vocabulary entries with confidence scores and details
        """
        logger.debug(f"📚 Fetching vocabulary - student_id={student_id}")
        
        if vocabulary_type:
            query = """
            MATCH (s:Student {student_id: $student_id})-[rel:KNOWS]->(v:Vocabulary {vocabulary_type: $vocabulary_type})
            RETURN {
                word: v.word,
                definition: v.definition,
                topic: v.topic,
                confidence: rel.confidence,
                learned_at: rel.learned_at,
                article: v.article,
                gender: v.gender,
                plural: v.plural,
                cefr_level: v.cefr_level,
                part_of_speech: v.part_of_speech,
                italian_plural: v.italian_plural,
                german_word: v.german_word,
                vocabulary_type: v.vocabulary_type,
                updated_at: v.updated_at
            } AS vocab
            ORDER BY rel.confidence DESC
            LIMIT $limit
            """
        else:
            query = """
            MATCH (s:Student {student_id: $student_id})-[rel:KNOWS]->(v:Vocabulary)
            RETURN {
                word: v.word,
                definition: v.definition,
                topic: v.topic,
                confidence: rel.confidence,
                learned_at: rel.learned_at,
                article: v.article,
                gender: v.gender,
                plural: v.plural,
                cefr_level: v.cefr_level,
                part_of_speech: v.part_of_speech,
                italian_plural: v.italian_plural,
                german_word: v.german_word,
                vocabulary_type: v.vocabulary_type,
                updated_at: v.updated_at
            } AS vocab
            ORDER BY rel.confidence DESC
            LIMIT $limit
            """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                student_id=student_id,
                limit=limit,
                vocabulary_type=vocabulary_type if vocabulary_type else None,
            )
            records = await result.data()
            return [dict(r["vocab"]) for r in records]

    async def get_student_vocabulary(
        self,
        student_id: str,
        limit: int = 50,
    ) -> list[dict]:
        """Alias for get_vocabulary for API compatibility.

        Args:
            student_id: Student ID
            limit: Maximum number of words

        Returns:
            List of vocabulary entries with confidence scores
        """
        return await self.get_vocabulary(student_id, limit)

    async def get_common_errors(
        self,
        student_id: str,
        limit: int = 10,
    ) -> list[dict]:
        """Get most common grammar errors.

        Args:
            student_id: Student ID
            limit: Maximum number of errors

        Returns:
            List of grammar errors sorted by frequency
        """
        logger.debug(f"🔴 Fetching grammar errors - student_id={student_id}")
        query = """
        MATCH (s:Student {student_id: $student_id})-[rel:MADE_ERROR]->(e:GrammarError)
        RETURN {
            rule: e.rule,
            context: e.context,
            correction: e.correction,
            error_count: rel.error_count,
            last_error_at: rel.last_error_at
        } AS error
        ORDER BY rel.error_count DESC
        LIMIT $limit
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                student_id=student_id,
                limit=limit,
            )
            records = await result.data()
            return [dict(r["error"]) for r in records]

    async def get_exercise_history(
        self,
        student_id: str,
        limit: int = 20,
    ) -> list[dict]:
        """Get exercise attempt history.

        Args:
            student_id: Student ID
            limit: Maximum number of records

        Returns:
            List of exercises with scores
        """
        logger.debug(f"✏️ Fetching exercise history - student_id={student_id}")
        query = """
        MATCH (s:Student {student_id: $student_id})-[:COMPLETED]->(e:Exercise)
        RETURN {
            type: e.type,
            score: e.score,
            level: e.level,
            xp_earned: e.xp_earned,
            completed_at: e.completed_at
        } AS exercise
        ORDER BY e.completed_at DESC
        LIMIT $limit
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                student_id=student_id,
                limit=limit,
            )
            records = await result.data()
            return [dict(r["exercise"]) for r in records]

    async def create_session(
        self,
        student_id: str,
        session_type: str,
        details: dict | None = None,
    ) -> str:
        """Create a new learning session.

        Args:
            student_id: Student ID
            session_type: Type of session (flashcard_review, vocabulary_practice, etc.)
            details: Additional session data as dict

        Returns:
            Session ID or None on error
        """
        logger.info(f"📝 Creating session - student_id={student_id}, type={session_type}")
        
        query = """
        MERGE (s:Student {student_id: $student_id})
        CREATE (sess:Session {
            session_type: $session_type,
            started_at: datetime(),
            details: $details,
            completed_at: datetime()
        })
        MERGE (s)-[:COMPLETED_SESSION]->(sess)
        RETURN elementId(sess) AS session_id
        """
        
        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                student_id=student_id,
                session_type=session_type,
                details=str(details) if details else "{}",
            )
            record = await result.single()
            session_id = record["session_id"] if record else None
            logger.info(f"✓ Session created: {session_id}")
            return session_id

    async def update_session(
        self,
        session_id: str,
        words_reviewed: int = 0,
        correct_answers: int = 0,
        accuracy: float = 0.0,
        duration_seconds: int = 0,
    ) -> bool:
        """Update session with completion metrics.

        Args:
            session_id: Session node ID
            words_reviewed: Number of words reviewed
            correct_answers: Number of correct answers
            accuracy: Accuracy percentage
            duration_seconds: Session duration

        Returns:
            True if update successful
        """
        logger.debug(f"📊 Updating session - session_id={session_id}")
        
        query = """
        MATCH (sess:Session)
        WHERE elementId(sess) = $session_id
        SET sess.words_reviewed = $words_reviewed,
            sess.correct_answers = $correct_answers,
            sess.accuracy = $accuracy,
            sess.duration_seconds = $duration_seconds,
            sess.completed_at = datetime()
        RETURN sess.session_type
        """
        
        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                session_id=session_id,
                words_reviewed=words_reviewed,
                correct_answers=correct_answers,
                accuracy=accuracy,
                duration_seconds=duration_seconds,
            )
            record = await result.single()
            logger.info("✓ Session updated")
            return record is not None

    async def get_session_history(
        self,
        student_id: str,
        limit: int = 10,
    ) -> list[dict]:
        """Get session history for a student.

        Args:
            student_id: Student ID
            limit: Maximum number of sessions

        Returns:
            List of session records
        """
        logger.debug(f"📅 Fetching session history - student_id={student_id}")
        
        query = """
        MATCH (s:Student {student_id: $student_id})-[:COMPLETED_SESSION]->(sess:Session)
        RETURN {
            session_type: sess.session_type,
            started_at: sess.started_at,
            completed_at: sess.completed_at,
            words_reviewed: COALESCE(sess.words_reviewed, 0),
            correct_answers: COALESCE(sess.correct_answers, 0),
            accuracy: COALESCE(sess.accuracy, 0.0),
            duration_seconds: COALESCE(sess.duration_seconds, 0)
        } AS session
        ORDER BY sess.started_at DESC
        LIMIT $limit
        """
        
        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                student_id=student_id,
                limit=limit,
            )
            records = await result.data()
            return [dict(r["session"]) for r in records]

    async def ingest_vocabulary_from_file(self, filepath: str, student_id: str = "admin"):
        """Ingest vocabulary from JSON file into Neo4j graph.

        Args:
            filepath: Path to JSON file with vocabulary entries
            student_id: Student ID to associate vocabulary with (default: admin)
        """
        import json
        
        logger.info(f"📖 Ingesting vocabulary from {filepath}")
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                vocabulary_list = json.load(f)
        except FileNotFoundError:
            logger.error(f"✗ File not found: {filepath}")
            return 0
        except json.JSONDecodeError as e:
            logger.error(f"✗ Invalid JSON: {e}")
            return 0
        
        ingested = 0
        skipped = 0
        for entry in vocabulary_list:
            try:
                word = entry.get("italian_word", "").strip()
                if not word:
                    skipped += 1
                    continue
                
                article = entry.get("article", "")
                gender = entry.get("gender", "")
                plural = ""
                italian_plural = entry.get("italian_plural", entry.get("plural", ""))
                vocabulary_type = entry.get("vocabulary_type", "premade")
                part_of_speech = entry.get("part_of_speech", "")
                
                if not article or not gender:
                    if part_of_speech == "noun":
                        if not gender:
                            gender = self._guess_gender(word)
                        article = self._determine_article(word, gender, part_of_speech)
                    elif part_of_speech in ("article", "article (contracted)"):
                        article = word
                        gender = "m" if word in ("il", "lo", "l'", "la") else "f"
                    else:
                        article = ""
                        gender = ""
                
                await self.add_vocabulary(
                    student_id=student_id,
                    word=word,
                    definition=entry.get("german_word", ""),
                    topic=entry.get("topic", "general"),
                    confidence=0.8,
                    article=article,
                    gender=gender,
                    plural=plural,
                    cefr_level=entry.get("cefr_level", ""),
                    part_of_speech=part_of_speech,
                    italian_plural=italian_plural,
                    german_word=entry.get("german_word", ""),
                    vocabulary_type=vocabulary_type,
                )
                ingested += 1
                
                if ingested % 100 == 0:
                    logger.info(f"  ✓ Ingested {ingested}/{len(vocabulary_list)} words")
                    
            except Exception as e:
                logger.warning(f"  ⚠ Error ingesting {entry.get('italian_word', 'unknown')}: {e}")
                continue
        
        logger.info(f"✓ Ingested {ingested} vocabulary words from {filepath} (skipped {skipped})")
        return ingested

    def _determine_article(self, word: str, gender: str = "", part_of_speech: str = "") -> str:
        """Determine Italian article based on word.

        Args:
            word: Italian word
            gender: Known gender (m, f) if available
            part_of_speech: POS tag for additional context

        Returns:
            Article (il, la, l', lo, i, le, gli, l')
        """
        if not word or part_of_speech != "noun":
            return ""
        
        word_lower = word.lower().strip()
        
        if not gender:
            gender = self._guess_gender(word_lower)
        
        vowels = "aeiou"
        special_cases = {
            "l'": ["uomo", "ufficio", "università", "ultimo", "unico"],
            "lo": ["stomaco", "psicologo", "zoo", "sfogo"],
            "i": ["stomaci", "psicologi", "zoo", "sfoghi"],
            "gli": ["lunedì", "lì", "ieri", "oggi"],
        }
        
        for article, words in special_cases.items():
            if word_lower in words:
                return article
        
        if word_lower[0] in vowels:
            return "l'"
        elif gender == "m":
            if word_lower[0] in "sz":
                return "lo"
            elif word_lower[0] in "gh":
                return "il"
            elif word_lower[0] in "bcdfjlmnpqrstvwxyz":
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
        
        if word_lower.endswith(("one", "atore", "otto", "ismo", "ista")):
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
