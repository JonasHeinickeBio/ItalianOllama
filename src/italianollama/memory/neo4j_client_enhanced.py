"""Enhanced Neo4j client with semantic graph operations.

Handles all Neo4j operations with improved data model:
- Student learning journeys (sessions, attempts, performance)
- Semantic skills and competency tracking
- Module/curriculum management
- Advanced analytics and personalization queries
"""

from neo4j import AsyncGraphDatabase


class Neo4jClient:
    """Async Neo4j client for Italian Tutor (Enhanced).

    Handles:
    - Student CRUD with session/attempt tracking
    - Semantic skill development
    - Module and learning path management
    - Vocabulary with spaced repetition
    - Grammar concept tracking
    - Comprehensive learning analytics
    - Personalized recommendations
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "",
        database: str = "neo4j",
    ):
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self._driver = None

    async def connect(self):
        """Connect to Neo4j."""
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
        return self

    async def close(self):
        """Close the connection."""
        if self._driver:
            await self._driver.close()
            self._driver = None

    async def verify_connectivity(self) -> bool:
        """Verify connection is working."""
        if not self._driver:
            await self.connect()

        async with self._driver.session(database=self.database) as session:
            result = await session.run("RETURN 1 AS n")
            await result.consume()
        return True

    # ============================================================================
    # STUDENT MANAGEMENT
    # ============================================================================

    async def create_student(
        self, student_id: str, name: str, native_language: str = "English"
    ) -> str:
        """Create a new student node.

        Args:
            student_id: Unique identifier for student
            name: Display name
            native_language: L1 language (for contrastive analysis)

        Returns:
            Element ID of created student
        """
        query = """
        CREATE (s:Student {
            student_id: $student_id,
            name: $name,
            native_language: $native_language,
            created_at: datetime(),
            last_active: datetime(),
            total_xp: 0,
            current_streak: 0
        })
        RETURN elementId(s) AS id
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                student_id=student_id,
                name=name,
                native_language=native_language,
            )
            record = await result.single()
            return record["id"] if record else None

    async def get_student(self, student_id: str) -> dict | None:
        """Get comprehensive student profile.

        Includes:
        - Current level
        - Skill breakdown (XP per skill)
        - Module progress
        - Streak statistics
        - Total time invested
        """
        query = """
        MATCH (s:Student {student_id: $student_id})
        OPTIONAL MATCH (s)-[:ACHIEVED]->(level:CEFRLevel)
        OPTIONAL MATCH (s)-[:WORKING_ON]->(mod:Module)
        OPTIONAL MATCH (s)-[:ENROLLED_IN]->(session:Session)
        WITH s, level, mod, count(DISTINCT session) AS total_sessions, sum(session.duration_minutes) AS total_minutes
        OPTIONAL MATCH (s)-[:EXPERIENCED]->(skill:Skill)
        WITH s, level, mod, total_sessions, total_minutes, collect({skill: skill.skill_id, xp: 0}) AS skills_raw
        RETURN {
            student_id: s.student_id,
            name: s.name,
            native_language: s.native_language,
            created_at: s.created_at,
            last_active: s.last_active,
            current_level: CASE WHEN level IS NOT NULL THEN level.code ELSE 'A1' END,
            current_module: CASE WHEN mod IS NOT NULL THEN mod.module_id ELSE null END,
            total_xp: s.total_xp,
            current_streak: s.current_streak,
            total_sessions: total_sessions,
            total_minutes: total_minutes
        } AS profile
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id)
            record = await result.single()
            return dict(record["profile"]) if record else None

    async def get_student_stats(self, student_id: str) -> dict:
        """Get aggregated KPI statistics for dashboard.

        Returns:
            {
                total_exercises: int,
                avg_score: float,
                total_vocab: int,
                vocab_mature: int (confidence > 0.8),
                total_errors: int,
                streak_days: int,
                xp_this_week: int,
                skills: {skill_id: xp}
            }
        """
        query = """
        MATCH (s:Student {student_id: $student_id})
        OPTIONAL MATCH (s)-[:ENROLLED_IN]->(session:Session)-[:CONTAINS]->(a:Attempt)
        OPTIONAL MATCH (a)-[:RESULT]->(p:Performance)
        OPTIONAL MATCH (s)-[:KNOWS]->(vc:VocabConfidence)
        OPTIONAL MATCH (s)-[:MADE_ERROR]->(e:GrammarError)
        OPTIONAL MATCH (a)-[:GAINS]->(exp:Experience)-[:TOWARDS_SKILL]->(skill:Skill)
        WHERE a.completed_at > datetime() - duration('P7D')
        WITH s,
             count(DISTINCT a) AS total_exercises,
             avg(a.score) AS avg_score,
             count(DISTINCT vc) AS total_vocab,
             count(CASE WHEN vc.confidence_score > 0.8 THEN 1 END) AS vocab_mature,
             count(DISTINCT e) AS total_errors,
             s.current_streak AS streak,
             sum(exp.amount) AS xp_this_week,
             collect(DISTINCT {skill: skill.skill_id, xp: sum(exp.amount)}) AS skill_xps
        RETURN {
            total_exercises: COALESCE(total_exercises, 0),
            avg_score: COALESCE(avg_score, 0),
            total_vocab: COALESCE(total_vocab, 0),
            vocab_mature: COALESCE(vocab_mature, 0),
            total_errors: COALESCE(total_errors, 0),
            streak_days: streak,
            xp_this_week: COALESCE(xp_this_week, 0)
        } AS stats
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id)
            record = await result.single()
            return (
                dict(record["stats"])
                if record
                else {
                    "total_exercises": 0,
                    "avg_score": 0,
                    "total_vocab": 0,
                    "vocab_mature": 0,
                    "total_errors": 0,
                    "streak_days": 0,
                    "xp_this_week": 0,
                }
            )

    # ============================================================================
    # LEARNING SESSIONS & ATTEMPTS
    # ============================================================================

    async def create_session(
        self,
        student_id: str,
        session_id: str,
        module_context: str | None = None,
    ) -> str:
        """Create a new study session.

        Args:
            student_id: Student ID
            session_id: Unique session identifier (uuid preferred)
            module_context: Optional module_id if session is focused on a module

        Returns:
            Element ID of session
        """
        query = """
        MATCH (s:Student {student_id: $student_id})
        CREATE (sess:Session {
            session_id: $session_id,
            student_id: $student_id,
            started_at: datetime(),
            duration_minutes: 0,
            total_xp_earned: 0,
            exercise_count: 0,
            module_context: $module_context
        })
        CREATE (s)-[:ENROLLED_IN]->(sess)
        RETURN elementId(sess) AS id
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                student_id=student_id,
                session_id=session_id,
                module_context=module_context,
            )
            record = await result.single()
            return record["id"] if record else None

    async def record_exercise_attempt(
        self,
        session_id: str,
        attempt_id: str,
        exercise_type: str,
        template_id: str,
        is_correct: bool,
        score: float,
        xp_earned: int,
        duration_seconds: int = 10,
        response_time_ms: int = 0,
        confidence: float = 0.5,
        hints_used: int = 0,
        retries: int = 0,
        feedback: str = "",
    ) -> str:
        """Record an exercise attempt within a session.

        Args:
            session_id: Session ID
            attempt_id: Unique attempt identifier
            exercise_type: enum [flashcard, multiple_choice, translation, listening, speaking, etc.]
            template_id: ExerciseTemplate ID
            is_correct: Whether attempt was successful
            score: Score 0.0-1.0
            xp_earned: XP points awarded
            duration_seconds: Time spent on attempt
            response_time_ms: Time to first response
            confidence: Student's self-reported confidence 0.0-1.0
            hints_used: Number of hints requested
            retries: Number of retries before success
            feedback: Feedback message for student

        Returns:
            Element ID of attempt
        """
        query = """
        MATCH (sess:Session {session_id: $session_id})
        CREATE (a:Attempt {
            attempt_id: $attempt_id,
            session_id: $session_id,
            exercise_type: $exercise_type,
            started_at: datetime(),
            completed_at: datetime(),
            duration_seconds: $duration_seconds,
            response_time_ms: $response_time_ms,
            is_correct: $is_correct,
            confidence: $confidence,
            score: $score,
            xp_earned: $xp_earned,
            hints_used: $hints_used,
            retries: $retries,
            feedback: $feedback
        })
        CREATE (sess)-[:CONTAINS]->(a)
        OPTIONAL MATCH (t:ExerciseTemplate {template_id: $template_id})
        CREATE (a)-[:USES_TEMPLATE]->(t)
        RETURN elementId(a) AS id
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(
                query,
                session_id=session_id,
                attempt_id=attempt_id,
                exercise_type=exercise_type,
                template_id=template_id,
                is_correct=is_correct,
                score=score,
                xp_earned=xp_earned,
                duration_seconds=duration_seconds,
                response_time_ms=response_time_ms,
                confidence=confidence,
                hints_used=hints_used,
                retries=retries,
                feedback=feedback,
            )
            record = await result.single()
            return record["id"] if record else None

    async def end_session(self, session_id: str) -> None:
        """Close out a session and compute stats.

        Updates:
        - Session end_time
        - Total duration
        - Aggregated XP and exercise count
        - Student last_active time
        """
        query = """
        MATCH (s:Session {session_id: $session_id})
        SET s.ended_at = datetime(),
            s.duration_minutes = ROUND((datetime() - s.started_at).seconds / 60.0)
        MATCH (s)-[:CONTAINS]->(a:Attempt)
        WITH s, count(a) AS attempt_count, sum(a.xp_earned) AS total_xp
        SET s.exercise_count = attempt_count,
            s.total_xp_earned = total_xp
        MATCH (s)-[:FOR_STUDENT]->(student:Student)
        SET student.last_active = datetime(),
            student.total_xp = student.total_xp + total_xp
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(query, session_id=session_id)

    # ============================================================================
    # VOCABULARY & SPACED REPETITION
    # ============================================================================

    async def add_vocabulary(
        self,
        student_id: str,
        word: str,
        translation: str,
        topic: str = "general",
        level: str = "A1",
        example_sentence_italian: str = "",
        example_sentence_english: str = "",
        part_of_speech: str = "noun",
    ) -> None:
        """Add vocabulary word to student's collection.

        Creates or updates:
        - Vocabulary node (if not exists)
        - VocabConfidence node (student-specific tracking)
        """
        query = """
        MERGE (v:Vocabulary {word: $word, language: 'italian'})
        SET v.translation = $translation,
            v.topic = $topic,
            v.difficulty_level = $level,
            v.part_of_speech = $part_of_speech,
            v.example_sentence_italian = $example_sentence_italian,
            v.example_sentence_english = $example_sentence_english,
            v.created_at = datetime()
        MATCH (s:Student {student_id: $student_id})
        MERGE (vc:VocabConfidence {student_id: $student_id, word: $word})
        SET vc.confidence_score = 0.0,
            vc.last_seen = datetime(),
            vc.next_review = datetime(),
            vc.review_count = 0,
            vc.correct_count = 0,
            vc.incorrect_count = 0,
            vc.ease_factor = 2.5,
            vc.interval_days = 1,
            vc.tags = 'new'
        CREATE (s)-[:KNOWS]->(vc)
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                word=word,
                translation=translation,
                topic=topic,
                level=level,
                example_sentence_italian=example_sentence_italian,
                example_sentence_english=example_sentence_english,
                part_of_speech=part_of_speech,
            )

    async def get_student_vocabulary(
        self,
        student_id: str,
        limit: int = 20,
        only_due_for_review: bool = False,
    ) -> list[dict]:
        """Get student's vocabulary collection with confidence scores.

        Args:
            student_id: Student ID
            limit: Maximum results
            only_due_for_review: If True, only return words needing spaced repetition review

        Returns:
            List of vocabulary records with confidence/EF/interval
        """
        where_clause = ""
        if only_due_for_review:
            where_clause = "WHERE vc.next_review <= datetime()"

        query = f"""
        MATCH (s:Student {{student_id: $student_id}})-[:KNOWS]->(vc:VocabConfidence)
        MATCH (v:Vocabulary {{word: vc.word, language: 'italian'}})
        {where_clause}
        RETURN {{
            word: v.word,
            translation: v.translation,
            part_of_speech: v.part_of_speech,
            topic: v.topic,
            difficulty_level: v.difficulty_level,
            confidence_score: vc.confidence_score,
            ease_factor: vc.ease_factor,
            interval_days: vc.interval_days,
            next_review: vc.next_review,
            correct_count: vc.correct_count,
            tags: vc.tags
        }} AS vocab_record
        ORDER BY vc.confidence_score ASC
        LIMIT $limit
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id, limit=limit)
            records = await result.data()
            return [dict(r["vocab_record"]) for r in records]

    async def update_vocabulary_confidence(
        self,
        student_id: str,
        word: str,
        is_correct: bool,
        ease_factor: float | None = None,
        interval_days: int | None = None,
    ) -> None:
        """Update spaced repetition metrics for vocabulary (SM-2 algorithm).

        Args:
            student_id: Student ID
            word: Word to update
            is_correct: Whether recall was successful
            ease_factor: SM-2 ease factor (if calculation done in Python)
            interval_days: Next interval in days (if calculation done in Python)
        """
        query = """
        MATCH (s:Student {student_id: $student_id})-[:KNOWS]->(vc:VocabConfidence {word: $word})
        SET vc.last_seen = datetime(),
            vc.review_count = vc.review_count + 1,
            vc.correct_count = CASE WHEN $is_correct THEN vc.correct_count + 1 ELSE vc.correct_count END,
            vc.incorrect_count = CASE WHEN NOT $is_correct THEN vc.incorrect_count + 1 ELSE vc.incorrect_count END,
            vc.confidence_score = (vc.correct_count + 1.0) / (vc.review_count + 1.0),
            vc.ease_factor = COALESCE($ease_factor, vc.ease_factor),
            vc.interval_days = COALESCE($interval_days, vc.interval_days),
            vc.next_review = datetime() + duration({days: $interval_days})
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                word=word,
                is_correct=is_correct,
                ease_factor=ease_factor,
                interval_days=interval_days or 1,
            )

    # ============================================================================
    # SKILLS & LEARNING OUTCOMES
    # ============================================================================

    async def add_skill_experience(
        self,
        student_id: str,
        skill_id: str,
        xp_amount: int,
        attempt_id: str | None = None,
    ) -> None:
        """Award XP to a specific skill and create Experience node.

        Args:
            student_id: Student ID
            skill_id: Skill identifier (e.g., 'vocabulary', 'grammar', 'listening')
            xp_amount: XP points to award
            attempt_id: Optional backref to exercise attempt
        """
        query = """
        MATCH (s:Student {student_id: $student_id})
        MATCH (skill:Skill {skill_id: $skill_id})
        CREATE (exp:Experience {
            experience_id: randomUUID(),
            student_id: $student_id,
            amount: $xp_amount,
            earned_at: datetime()
        })
        CREATE (s)-[:GAINS]->(exp)-[:TOWARDS_SKILL]->(skill)
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                skill_id=skill_id,
                xp_amount=xp_amount,
            )

    async def get_skill_breakdown(self, student_id: str) -> dict:
        """Get XP earned per skill (breakdown).

        Returns:
            {skill_id: total_xp} for each skill student has interacted with
        """
        query = """
        MATCH (s:Student {student_id: $student_id})-[:GAINS]->(exp:Experience)-[:TOWARDS_SKILL]->(skill:Skill)
        WITH skill.skill_id AS skill_id, sum(exp.amount) AS total_xp
        RETURN collect({skill_id: skill_id, xp: total_xp}) AS breakdown
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id)
            record = await result.single()
            if record:
                return {item["skill_id"]: item["xp"] for item in record["breakdown"]}
            return {}

    # ============================================================================
    # MODULES & LEARNING PATHS
    # ============================================================================

    async def get_recommended_next_module(self, student_id: str) -> dict | None:
        """Recommend the next module for student based on level and progress.

        Returns:
            Module details or None if all modules completed
        """
        query = """
        MATCH (s:Student {student_id: $student_id})-[:ACHIEVED]->(level:CEFRLevel)
        MATCH (level)-[:REQUIRES]->(m:Module)
        WHERE NOT (s)-[:COMPLETED]->(m) AND NOT (s)-[:WORKING_ON]->(m)
        RETURN {
            module_id: m.module_id,
            title: m.title,
            description: m.description,
            level: m.level,
            estimated_hours: m.estimated_hours,
            vocabulary_count: m.vocabulary_count,
            exercise_count: m.exercise_count
        } AS module
        LIMIT 1
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id)
            record = await result.single()
            return dict(record["module"]) if record else None

    async def mark_module_completed(self, student_id: str, module_id: str, score: float) -> None:
        """Mark module as completed by student.

        Args:
            student_id: Student ID
            module_id: Module ID
            score: Performance score (0.0-1.0)
        """
        query = """
        MATCH (s:Student {student_id: $student_id})
        MATCH (m:Module {module_id: $module_id})
        CREATE (s)-[:COMPLETED {completed_at: datetime(), score: $score}]->(m)
        REMOVE (s)-[:WORKING_ON]->(m)
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(query, student_id=student_id, module_id=module_id, score=score)

    # ============================================================================
    # CONCEPTS & GRAMMAR TRACKING
    # ============================================================================

    async def record_concept_mastery(
        self,
        student_id: str,
        concept_id: str,
        mastery_level: float,  # 0.0-1.0
    ) -> None:
        """Track student's understanding of a grammar/linguistic concept.

        Args:
            student_id: Student ID
            concept_id: Concept identifier
            mastery_level: Estimated mastery 0.0-1.0
        """
        query = """
        MATCH (s:Student {student_id: $student_id})
        MATCH (c:Concept {concept_id: $concept_id})
        MERGE (s)-[r:UNDERSTANDS]->(c)
        SET r.mastery_level = $mastery_level,
            r.last_assessed = datetime()
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                concept_id=concept_id,
                mastery_level=mastery_level,
            )

    async def record_grammar_error(
        self,
        student_id: str,
        original: str,
        corrected: str,
        rule: str,
        concept_id: str | None = None,
        level: str = "A2",
    ) -> None:
        """Record a grammar error for pattern tracking.

        Args:
            student_id: Student ID
            original: Incorrect form
            corrected: Correct form
            rule: Rule description
            concept_id: Related Concept node ID
            level: CEFR level where error occurred
        """
        query = """
        MATCH (s:Student {student_id: $student_id})
        MERGE (e:GrammarError {
            pattern: $rule,
            original_example: $original,
            corrected_example: $corrected,
            level: $level
        })
        SET e.seen_count = coalesce(e.seen_count, 0) + 1,
            e.last_seen = datetime()
        MERGE (s)-[:MADE_ERROR]->(e)
        OPTIONAL MATCH (c:Concept {concept_id: $concept_id})
        MERGE (e)-[:RELATED_TO]->(c)
        """

        async with self._driver.session(database=self.database) as session:
            await session.run(
                query,
                student_id=student_id,
                original=original,
                corrected=corrected,
                rule=rule,
                concept_id=concept_id,
                level=level,
            )

    async def get_common_errors(self, student_id: str, limit: int = 10) -> list[dict]:
        """Get most frequent grammar errors for targeted review.

        Returns:
            List of error patterns ranked by frequency
        """
        query = """
        MATCH (s:Student {student_id: $student_id})-[:MADE_ERROR]->(e:GrammarError)
        OPTIONAL MATCH (e)-[:RELATED_TO]->(c:Concept)
        RETURN {
            rule: e.pattern,
            original: e.original_example,
            corrected: e.corrected_example,
            seen_count: e.seen_count,
            concept: c.concept_id,
            level: e.level
        } AS error
        ORDER BY e.seen_count DESC
        LIMIT $limit
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id, limit=limit)
            records = await result.data()
            return [dict(r["error"]) for r in records]

    # ============================================================================
    # ANALYTICS & DASHBOARDS
    # ============================================================================

    async def get_learning_velocity(self, student_id: str, days: int = 7) -> dict:
        """Get learning velocity metrics (XP per hour, exercises per session).

        Args:
            student_id: Student ID
            days: Lookback period in days

        Returns:
            Velocity metrics per skill
        """
        query = """
        MATCH (s:Student {student_id: $student_id})-[:ENROLLED_IN]->(sess:Session)-[:CONTAINS]->(a:Attempt)
        WHERE sess.started_at > datetime() - duration({days: $days})
        WITH sess, a, sess.duration_minutes AS session_minutes, a.xp_earned AS attempt_xp
        WITH collect({session_minutes: session_minutes, xp: attempt_xp}) AS attempts
        WITH sum(attempts[i].xp for i in range(0, size(attempts))) AS total_xp,
             sum(attempts[i].session_minutes for i in range(0, size(attempts))) AS total_minutes
        RETURN {
            total_xp: total_xp,
            total_hours: total_minutes / 60.0,
            xp_per_hour: CASE WHEN total_minutes > 0 THEN (total_xp * 60.0) / total_minutes ELSE 0 END,
            exercises_per_session: size(attempts)
        } AS velocity
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id, days=days)
            record = await result.single()
            return dict(record["velocity"]) if record else {}

    async def get_knowledge_graph(self, student_id: str, max_depth: int = 2) -> dict:
        """Export student's knowledge graph for visualization.

        Returns:
            {nodes: [...], links: [...]} for st-linkanalysis or similar viz
        """
        query = """
        MATCH (s:Student {student_id: $student_id})
        MATCH path = (s)-[r*1..3]->(target)
        WITH DISTINCT nodes(path) AS nodes_list, relationships(path) AS rels_list
        WITH nodes_list + collect(distinct target) AS all_nodes, rels_list
        UNWIND all_nodes AS node
        RETURN collect(DISTINCT {
            id: elementId(node),
            label: labels(node)[0],
            properties: properties(node)
        }) AS nodes,
        collect(DISTINCT {
            id: elementId(r),
            source: elementId(startNode(r)),
            target: elementId(endNode(r)),
            type: type(r)
        }) AS links
        FROM rels_list r
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id)
            record = await result.single()
            if record:
                return {
                    "nodes": record.get("nodes", []),
                    "links": record.get("links", []),
                }
            return {"nodes": [], "links": []}

    async def get_struggling_concepts(self, student_id: str, threshold: float = 0.6) -> list[dict]:
        """Identify grammar concepts where student is struggling (low mastery).

        Args:
            student_id: Student ID
            threshold: Mastery threshold below which to flag as struggling

        Returns:
            List of struggling concepts with learning resources
        """
        query = """
        MATCH (s:Student {student_id: $student_id})-[r:UNDERSTANDS]->(c:Concept)
        WHERE r.mastery_level < $threshold
        OPTIONAL MATCH (c)<-[:REQUIRES]-(t:ExerciseTemplate)
        OPTIONAL MATCH (t)-[:ASSESSES]->(skill:Skill)
        RETURN {
            concept_id: c.concept_id,
            title: c.title,
            mastery: r.mastery_level,
            difficulty_level: c.difficulty_level,
            common_mistakes: c.common_mistakes,
            practice_templates: collect(DISTINCT t.template_id)
        } AS concept
        ORDER BY r.mastery_level ASC
        LIMIT 10
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id, threshold=threshold)
            records = await result.data()
            return [dict(r["concept"]) for r in records]

    # ============================================================================
    # BACKWARDS COMPATIBILITY (Old API)
    # ============================================================================

    async def get_exercise_history(
        self,
        student_id: str,
        limit: int = 20,
    ) -> list[dict]:
        """Get student's exercise attempt history (legacy method)."""
        query = """
        MATCH (s:Student {student_id: $student_id})-[:MADE_ATTEMPT]->(e:Exercise)
        RETURN {
            type: e.type,
            score: e.score,
            level: e.level,
            completed_at: e.completed_at
        } AS exercise
        ORDER BY e.completed_at DESC
        LIMIT $limit
        """

        async with self._driver.session(database=self.database) as session:
            result = await session.run(query, student_id=student_id, limit=limit)
            records = await result.data()
            return [dict(r["exercise"]) for r in records]

    async def get_full_knowledge_graph(self, student_id: str) -> dict:
        """Get full knowledge graph for visualization (legacy method)."""
        return await self.get_knowledge_graph(student_id, max_depth=3)
