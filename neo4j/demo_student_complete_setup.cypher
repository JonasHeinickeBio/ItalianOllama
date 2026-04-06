// PHASE 1: CREATE CONSTRAINTS & INDEXES

CREATE CONSTRAINT student_id IF NOT EXISTS FOR (s:Student) REQUIRE s.student_id IS UNIQUE;
CREATE CONSTRAINT vocab_word IF NOT EXISTS FOR (v:Vocabulary) REQUIRE v.word IS UNIQUE;

CREATE INDEX IF NOT EXISTS FOR (s:Student) ON (s.student_id);
CREATE INDEX IF NOT EXISTS FOR (v:Vocabulary) ON (v.topic);
CREATE INDEX IF NOT EXISTS FOR (e:Exercise) ON (e.type);
CREATE INDEX IF NOT EXISTS FOR (l:CEFRLevel) ON (l.name);
CREATE INDEX IF NOT EXISTS FOR (g:GrammarError) ON (g.rule);

// PHASE 2: CREATE CEFR LEVELS

MERGE (a1:CEFRLevel {name: 'A1'})
ON CREATE SET a1.description = 'Can understand and use very basic phrases for immediate needs'
ON MATCH SET a1.description = 'Can understand and use very basic phrases for immediate needs';

MERGE (a2:CEFRLevel {name: 'A2'})
ON CREATE SET a2.description = 'Can handle simple, everyday situations with basic language'
ON MATCH SET a2.description = 'Can handle simple, everyday situations with basic language';

MERGE (b1:CEFRLevel {name: 'B1'})
ON CREATE SET b1.description = 'Can produce simple and coherent spoken and written text'
ON MATCH SET b1.description = 'Can produce simple and coherent spoken and written text';

MERGE (a1)-[:UNLOCKS]->(a2);
MERGE (a2)-[:UNLOCKS]->(b1);

// PHASE 3: CREATE STUDENT

MERGE (student:Student {student_id: 'maria_doe_001'})
ON CREATE SET
  student.name = 'Maria Doe',
  student.email = 'maria.doe@example.com',
  student.created_at = datetime({year: 2025, month: 1, day: 15}),
  student.last_active = datetime(),
  student.native_language = 'English',
  student.learning_goal = 'travel',
  student.total_xp = 250,
  student.current_streak = 7,
  student.preferred_exercise_type = 'flashcard',
  student.notes = 'Quick learner, especially strong with vocabulary. Prefers speaking practice!'
ON MATCH SET
  student.name = 'Maria Doe',
  student.email = 'maria.doe@example.com',
  student.native_language = 'English',
  student.learning_goal = 'travel',
  student.last_active = datetime(),
  student.notes = 'Quick learner, especially strong with vocabulary. Prefers speaking practice!';

// PHASE 4: CREATE PLACEMENT LEVEL RELATIONSHIP

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (l:CEFRLevel {name: 'A2'})
MERGE (student)-[:HAS_PLACEMENT_LEVEL {confidence: 0.85, determined_at: datetime()}]->(l);

// PHASE 7: CREATE VOCABULARY

MERGE (v1:Vocabulary {word: 'ciao'})
ON CREATE SET v1.definition = 'hello / goodbye (informal)', v1.topic = 'greetings';

MERGE (v2:Vocabulary {word: 'grazie'})
ON CREATE SET v2.definition = 'thank you', v2.topic = 'politeness';

MERGE (v3:Vocabulary {word: 'per favore'})
ON CREATE SET v3.definition = 'please', v3.topic = 'politeness';

MERGE (v4:Vocabulary {word: 'mangiare'})
ON CREATE SET v4.definition = 'to eat', v4.topic = 'food';

MERGE (v5:Vocabulary {word: 'pizza'})
ON CREATE SET v5.definition = 'pizza', v5.topic = 'food';

// PHASE 8: KNOWS RELATIONSHIPS (idempotent)

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (v1:Vocabulary {word: 'ciao'})
WITH student, v1
MERGE (student)-[k1:KNOWS]->(v1)
ON CREATE SET k1.confidence = 0.95, k1.learned_at = datetime();

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (v2:Vocabulary {word: 'grazie'})
WITH student, v2
MERGE (student)-[k2:KNOWS]->(v2)
ON CREATE SET k2.confidence = 0.98, k2.learned_at = datetime();

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (v3:Vocabulary {word: 'per favore'})
WITH student, v3
MERGE (student)-[k3:KNOWS]->(v3)
ON CREATE SET k3.confidence = 0.85, k3.learned_at = datetime();

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (v4:Vocabulary {word: 'mangiare'})
WITH student, v4
MERGE (student)-[k4:KNOWS]->(v4)
ON CREATE SET k4.confidence = 0.90, k4.learned_at = datetime();

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (v5:Vocabulary {word: 'pizza'})
WITH student, v5
MERGE (student)-[k5:KNOWS]->(v5)
ON CREATE SET k5.confidence = 0.88, k5.learned_at = datetime();

// PHASE 6: CREATE EXERCISES

MERGE (ex1:Exercise {type: 'vocabulary', level: 'A2'})
ON CREATE SET ex1.score = 85, ex1.xp_earned = 10, ex1.completed_at = datetime();

MERGE (ex2:Exercise {type: 'grammar', level: 'A2'})
ON CREATE SET ex2.score = 75, ex2.xp_earned = 8, ex2.completed_at = datetime();

MERGE (ex3:Exercise {type: 'vocabulary', level: 'A1'})
ON CREATE SET ex3.score = 92, ex3.xp_earned = 12, ex3.completed_at = datetime();

// PHASE 7: COMPLETED RELATIONSHIPS

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (ex1:Exercise {type: 'vocabulary', level: 'A2'})
MERGE (student)-[:COMPLETED]->(ex1);

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (ex2:Exercise {type: 'grammar', level: 'A2'})
MERGE (student)-[:COMPLETED]->(ex2);

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (ex3:Exercise {type: 'vocabulary', level: 'A1'})
MERGE (student)-[:COMPLETED]->(ex3);

// PHASE 8: CREATE GRAMMAR ERRORS

MERGE (err1:GrammarError {rule: 'gender agreement'})
ON CREATE SET err1.context = 'La macchina rosso', err1.correction = 'La macchina rossa';

MERGE (err2:GrammarError {rule: 'verb conjugation'})
ON CREATE SET err2.context = 'Io sono avere fame', err2.correction = 'Io ho fame';

// PHASE 9: MADE_ERROR RELATIONSHIPS

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (err1:GrammarError {rule: 'gender agreement'})
MERGE (student)-[:MADE_ERROR {error_count: 2, last_error_at: datetime()}]->(err1);

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (err2:GrammarError {rule: 'verb conjugation'})
MERGE (student)-[:MADE_ERROR {error_count: 1, last_error_at: datetime()}]->(err2);

// PHASE 10: TEST SESSION

MERGE (sess:TestSession {session_id: 'session_maria_001_2025_01_20'})
ON CREATE SET
  sess.student_id = 'maria_doe_001',
  sess.started_at = datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 0}),
  sess.status = 'completed';

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (sess:TestSession {session_id: 'session_maria_001_2025_01_20'})
MERGE (student)-[:HAS_TEST_SESSION]->(sess);

// PHASE 11: TEST RESULT

MERGE (result:TestResult {student_id: 'maria_doe_001', session_id: 'session_maria_001_2025_01_20'})
ON CREATE SET
  result.total_correct = 22,
  result.total_questions = 30,
  result.score_percentage = 73.3,
  result.scores_by_section = '{"reading": 80, "listening": 70, "grammar": 75}',
  result.determined_level = 'A2',
  result.completed_at = datetime();

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (result:TestResult {student_id: 'maria_doe_001'})
MERGE (student)-[:HAS_TEST_RESULT]->(result);

// PHASE 12: NIVEAU TEST

MERGE (nt:NiveauTest {test_type: 'placement', level: 'A2'})
ON CREATE SET
  nt.readiness = 0.75,
  nt.skill_scores = '{"reading": 80, "listening": 70, "grammar": 75, "writing": 65}',
  nt.completed_at = datetime()
ON MATCH SET
  nt.readiness = 0.75,
  nt.skill_scores = '{"reading": 80, "listening": 70, "grammar": 75, "writing": 65}',
  nt.completed_at = datetime();

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (nt:NiveauTest {test_type: 'placement', level: 'A2'})
MERGE (student)-[:READY_FOR]->(nt);

// PHASE 13: CHAT MESSAGES

MERGE (msg1:ChatMessage {timestamp: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 30})})
ON CREATE SET
  msg1.user_content = 'Ciao, come stai?',
  msg1.assistant_content = 'Ciao! Sto bene, grazie. E tu?',
  msg1.content_length = 55,
  msg1.session_id = 'chat_001'
ON MATCH SET
  msg1.user_content = 'Ciao, come stai?',
  msg1.assistant_content = 'Ciao! Sto bene, grazie. E tu?',
  msg1.content_length = 55,
  msg1.session_id = 'chat_001';

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (msg1:ChatMessage {timestamp: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 30})})
MERGE (student)-[:HAS_CHAT_MESSAGE {timestamp: datetime()}]->(msg1);

MERGE (msg2:ChatMessage {timestamp: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 35})})
ON CREATE SET
  msg2.user_content = "Sto bene anch'io. Voglio imparare l'italiano.",
  msg2.assistant_content = 'Fantastico! Quali argomenti ti interessano?',
  msg2.content_length = 73,
  msg2.session_id = 'chat_001'
ON MATCH SET
  msg2.user_content = "Sto bene anch'io. Voglio imparare l'italiano.",
  msg2.assistant_content = 'Fantastico! Quali argomenti ti interessano?',
  msg2.content_length = 73,
  msg2.session_id = 'chat_001';

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (msg2:ChatMessage {timestamp: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 35})})
MERGE (student)-[:HAS_CHAT_MESSAGE {timestamp: datetime()}]->(msg2);

// PHASE 14: SESSIONS

MERGE (sess1:Session {session_type: 'flashcard_review', started_at: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 30})})
ON CREATE SET
  sess1.completed_at = datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 55}),
  sess1.details = '{"topic": "greetings", "duration": 300}',
  sess1.words_reviewed = 10,
  sess1.correct_answers = 8,
  sess1.accuracy = 0.8,
  sess1.duration_seconds = 1500
ON MATCH SET
  sess1.completed_at = datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 55}),
  sess1.details = '{"topic": "greetings", "duration": 300}',
  sess1.words_reviewed = 10,
  sess1.correct_answers = 8,
  sess1.accuracy = 0.8,
  sess1.duration_seconds = 1500;

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (sess1:Session {session_type: 'flashcard_review', started_at: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 30})})
MERGE (student)-[:COMPLETED_SESSION]->(sess1);

MERGE (sess2:Session {session_type: 'vocabulary_practice', started_at: datetime({year: 2025, month: 1, day: 22, hour: 10, minute: 0})})
ON CREATE SET
  sess2.completed_at = datetime({year: 2025, month: 1, day: 22, hour: 10, minute: 20}),
  sess2.details = '{"topic": "food", "duration": 300}',
  sess2.words_reviewed = 8,
  sess2.correct_answers = 7,
  sess2.accuracy = 0.875,
  sess2.duration_seconds = 1200
ON MATCH SET
  sess2.completed_at = datetime({year: 2025, month: 1, day: 22, hour: 10, minute: 20}),
  sess2.details = '{"topic": "food", "duration": 300}',
  sess2.words_reviewed = 8,
  sess2.correct_answers = 7,
  sess2.accuracy = 0.875,
  sess2.duration_seconds = 1200;

MATCH (student:Student {student_id: 'maria_doe_001'})
MATCH (sess2:Session {session_type: 'vocabulary_practice', started_at: datetime({year: 2025, month: 1, day: 22, hour: 10, minute: 0})})
MERGE (student)-[:COMPLETED_SESSION]->(sess2);

// PHASE 15: VERIFICATION

MATCH (s:Student {student_id: 'maria_doe_001'})
RETURN s.name AS student_name, s.student_id AS student_id, s.total_xp AS total_xp, s.current_streak AS current_streak, s.native_language AS native_language;

MATCH (s:Student {student_id: 'maria_doe_001'})-[:KNOWS]->(v:Vocabulary)
RETURN count(DISTINCT v) AS total_vocab;

MATCH (s:Student {student_id: 'maria_doe_001'})-[:COMPLETED]->(e:Exercise)
RETURN count(DISTINCT e) AS total_exercises;

MATCH (s:Student {student_id: 'maria_doe_001'})-[:MADE_ERROR]->(g:GrammarError)
RETURN count(DISTINCT g) AS total_errors;

MATCH (s:Student {student_id: 'maria_doe_001'})-[:HAS_CHAT_MESSAGE]->(c:ChatMessage)
RETURN count(DISTINCT c) AS total_chat_messages;

MATCH (s:Student {student_id: 'maria_doe_001'})-[:COMPLETED_SESSION]->(sess:Session)
RETURN count(DISTINCT sess) AS total_sessions;

MATCH (s:Student {student_id: 'maria_doe_001'})-[:HAS_TEST_SESSION]->(t:TestSession)
RETURN count(DISTINCT t) AS total_test_sessions;

MATCH (s:Student {student_id: 'maria_doe_001'})-[:HAS_TEST_RESULT]->(r:TestResult)
RETURN r.determined_level AS determined_level, r.score_percentage AS score_percentage;

MATCH (s:Student {student_id: 'maria_doe_001'})
WITH s
OPTIONAL MATCH (s)-[r]->(target)
RETURN s.name AS student_name, count(r) AS total_relationships, collect(DISTINCT type(r)) AS relationship_types;

RETURN "COMPLETE" AS status,
       "Created: 3 CEFR Levels (A1, A2, B1)" AS entities_created,
       "Demo Student: maria_doe_001 (Maria Doe)" AS demo_student,
       "Vocabulary: 5 words with confidence levels" AS vocabulary,
       "Exercises: 3 completed with scores and XP" AS exercises,
       "Grammar Errors: 2 error types tracked" AS errors,
       "Chat Messages: 2 conversation exchanges" AS chat,
       "Sessions: 2 learning sessions with metrics" AS sessions,
       "Test Results: 1 placement test (A2 level, 73.3% score)" AS tests;
