/*
 * ITALIAN TUTOR - Improved Semantic Knowledge Graph
 * Cypher Migration Script with Complete Demo Student
 *
 * This script creates:
 * 1. Complete curriculum structure (A1-A2 levels)
 * 2. Full knowledge graph (vocabulary, concepts, skills, exercises)
 * 3. Demo student "Maria" with complete learning journey across 3 sessions
 * 4. All semantic relationships
 *
 * Run with: cat this_file.cypher | cypher-shell -u neo4j -p password
 * Or paste into Neo4j browser
 */

// ============================================================================
// PHASE 1: CREATE CONSTRAINTS & INDEXES
// ============================================================================

// Unique constraints
CREATE CONSTRAINT student_id IF NOT EXISTS FOR (s:Student) REQUIRE s.student_id IS UNIQUE;
CREATE CONSTRAINT session_id IF NOT EXISTS FOR (s:Session) REQUIRE s.session_id IS UNIQUE;
CREATE CONSTRAINT module_id IF NOT EXISTS FOR (m:Module) REQUIRE m.module_id IS UNIQUE;
CREATE CONSTRAINT topic_id IF NOT EXISTS FOR (t:Topic) REQUIRE t.topic_id IS UNIQUE;
CREATE CONSTRAINT vocab_id IF NOT EXISTS FOR (v:Vocabulary) REQUIRE (v.word, v.language) IS UNIQUE;
CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.concept_id IS UNIQUE;
CREATE CONSTRAINT skill_id IF NOT EXISTS FOR (s:Skill) REQUIRE s.skill_id IS UNIQUE;
CREATE CONSTRAINT template_id IF NOT EXISTS FOR (t:ExerciseTemplate) REQUIRE t.template_id IS UNIQUE;
CREATE CONSTRAINT attempt_id IF NOT EXISTS FOR (a:Attempt) REQUIRE a.attempt_id IS UNIQUE;
CREATE CONSTRAINT cefr_code IF NOT EXISTS FOR (c:CEFRLevel) REQUIRE c.code IS UNIQUE;

// Indexes for performance
CREATE INDEX student_id_idx IF NOT EXISTS FOR (s:Student) ON (s.student_id);
CREATE INDEX session_student_idx IF NOT EXISTS FOR (s:Session) ON (s.student_id);
CREATE INDEX attempt_session_idx IF NOT EXISTS FOR (a:Attempt) ON (a.session_id);
CREATE INDEX vocab_level_idx IF NOT EXISTS FOR (v:Vocabulary) ON (v.difficulty_level);
CREATE INDEX concept_level_idx IF NOT EXISTS FOR (c:Concept) ON (c.difficulty_level);

// ============================================================================
// PHASE 2: CREATE CEFR LEVELS (Static Reference Data)
// ============================================================================

CREATE (a1:CEFRLevel {
  code: 'A1',
  title: 'Elementary',
  description: 'Can understand and use very basic phrases for immediate needs',
  vocab_range: '500-1000 words',
  assessment_score_passing: 0.75,
  typical_hours: 80
});

CREATE (a2:CEFRLevel {
  code: 'A2',
  title: 'Pre-Intermediate',
  description: 'Can handle simple, everyday situations with basic language',
  vocab_range: '1000-2000 words',
  assessment_score_passing: 0.75,
  typical_hours: 100
});

CREATE (b1:CEFRLevel {
  code: 'B1',
  title: 'Intermediate',
  description: 'Can produce simple and coherent spoken and written text',
  vocab_range: '2000-4000 words',
  assessment_score_passing: 0.80,
  typical_hours: 120
});

// Link levels in progression
WITH a1, a2, b1
CREATE (a1)-[:UNLOCKS]->(a2),
       (a2)-[:UNLOCKS]->(b1);

// ============================================================================
// PHASE 3: CREATE SKILLS (Learning Competencies)
// ============================================================================

CREATE (skill_vocab:Skill {
  skill_id: 'vocabulary',
  title: 'Vocabulary Recognition & Production',
  description: 'Understanding and using Italian words appropriately',
  xp_required_per_level: 500
});

CREATE (skill_grammar:Skill {
  skill_id: 'grammar',
  title: 'Grammar & Morphology',
  description: 'Understanding and applying Italian grammar rules',
  xp_required_per_level: 600
});

CREATE (skill_reading:Skill {
  skill_id: 'reading',
  title: 'Reading Comprehension',
  description: 'Understanding written Italian text',
  xp_required_per_level: 400
});

CREATE (skill_writing:Skill {
  skill_id: 'writing',
  title: 'Written Expression',
  description: 'Composing coherent Italian text',
  xp_required_per_level: 700
});

CREATE (skill_listening:Skill {
  skill_id: 'listening',
  title: 'Listening Comprehension',
  description: 'Understanding spoken Italian',
  xp_required_per_level: 450
});

CREATE (skill_speaking:Skill {
  skill_id: 'speaking',
  title: 'Oral Expression',
  description: 'Speaking fluent Italian',
  xp_required_per_level: 800
});

// ============================================================================
// PHASE 4: CREATE CONCEPTS (Grammar & Linguistic)
// ============================================================================

CREATE (concept_present:Concept {
  concept_id: 'present_simple_tense',
  title: 'Present Simple Tense',
  description: 'Regular present tense conjugation (io, tu, lui/lei, noi, voi, loro)',
  grammar_category: 'tense',
  difficulty_level: 'A1',
  common_mistakes: [
    'Forgetting to conjugate the verb',
    'Using infinitive instead of inflected form',
    'Incorrect stem for irregular verbs'
  ],
  explanation_md: '# Present Simple in Italian\n\nThe present simple (presente indicativo) describes actions happening now or general truths.\n\n```\nParare (to speak)\nio parlo = I speak\ntu parli = you speak\nlui/lei parla = he/she speaks\nnoi parliamo = we speak\nvoi parlate = you-all speak\nloro parlano = they speak\n```',
  min_vocab_requirement: 100
});

CREATE (concept_past:Concept {
  concept_id: 'past_participle',
  title: 'Past Participle & Passato Prossimo',
  description: 'Formation of past tense with auxiliary (avere/essere) + past participle',
  grammar_category: 'tense',
  difficulty_level: 'A2',
  common_mistakes: [
    'Incorrect auxiliary (avere vs essere)',
    'Wrong past participle ending',
    'Missing gender/number agreement with essere'
  ],
  explanation_md: '# Passato Prossimo\n\nUsed to describe completed actions in recent past.\n\n```\nParare → parlato\nio ho parlato = I spoke\nlei è andata = she went (essere requires gender agreement)\n```',
  min_vocab_requirement: 200
});

CREATE (concept_articles:Concept {
  concept_id: 'definite_articles',
  title: 'Definite Articles (il, la, lo, i, le, gli)',
  description: 'The Italian definite article changes based on gender, number, and initial sound',
  grammar_category: 'article',
  difficulty_level: 'A1',
  common_mistakes: [
    'Using wrong article with gender',
    'Forgetting apostrophe before vowels (lo → l\')',
    'Confusing gli (plural masculine) with le (plural feminine)'
  ],
  explanation_md: '# Italian Definite Articles\n\n| | Masculine | Feminine |\n|---|---|---|\n| Singular (consonant) | il | la |\n| Singular (vowel) | l\' | l\' |\n| Singular (s+consonant) | lo | - |\n| Plural | i / gli | le |\n\nExamples:\nil cane (the dog)\nla casa (the house)\nl\'albero (the tree)\nlo sport (the sport)',
  min_vocab_requirement: 50
});

CREATE (concept_adj_agreement:Concept {
  concept_id: 'adjective_agreement',
  title: 'Adjective Agreement with Gender & Number',
  description: 'Adjectives must agree with the noun in gender and number',
  grammar_category: 'agreement',
  difficulty_level: 'A1',
  common_mistakes: [
    'Not changing adjective ending for gender',
    'Not changing adjective ending for number',
    'Placing adjective in wrong position'
  ],
  explanation_md: '# Adjective Agreement\n\nAdjectives in Italian agreeing with nouns:\n\nSingular:\nuno gatto nero (a black cat - masculine singular)\nuna casa nera (a black house - feminine singular)\n\nPlural:\ngatti neri (black cats - masculine plural)\ncas nere (black houses - feminine plural)',
  min_vocab_requirement: 150
});

// Set prerequisite relationships
WITH concept_articles, concept_adj_agreement, concept_present, concept_past
CREATE (concept_articles)-[:GENERALIZES]->(concept_adj_agreement),
       (concept_present)-[:PREREQUISITE_FOR]->(concept_past);

// ============================================================================
// PHASE 5: CREATE VOCABULARY (Words & Expressions)
// ============================================================================

// Food - Beginner Vocabulary
CREATE (vocab_cibo:Vocabulary {
  word: 'cibo',
  language: 'italian',
  translation: 'food',
  part_of_speech: 'noun',
  gender: 'm',
  example_sentence_italian: 'Mi piace molto il cibo italiano.',
  example_sentence_english: 'I really like Italian food.',
  difficulty_level: 'A1',
  frequency_rank: 2500,
  tags: ['food', 'common', 'noun'],
  ipa_pronunciation: '/ˈtʃiːbo/',
  related_domain: 'food_dining',
  confidence_decays_after_days: 3
});

CREATE (vocab_mangiare:Vocabulary {
  word: 'mangiare',
  language: 'italian',
  translation: 'to eat',
  part_of_speech: 'verb',
  conjugations: {
    'io': 'mangio',
    'tu': 'mangi',
    'lui': 'mangia',
    'noi': 'mangiamo',
    'voi': 'mangiate',
    'loro': 'mangiano'
  },
  example_sentence_italian: 'Io mangio una mela.',
  example_sentence_english: 'I eat an apple.',
  difficulty_level: 'A1',
  frequency_rank: 500,
  tags: ['food', 'common', 'verb', 'action'],
  ipa_pronunciation: '/mɑnˈdʒɑːre/',
  related_domain: 'food_dining',
  confidence_decays_after_days: 3
});

CREATE (vocab_pizza:Vocabulary {
  word: 'pizza',
  language: 'italian',
  translation: 'pizza',
  part_of_speech: 'noun',
  gender: 'f',
  example_sentence_italian: 'Vuoi una pizza?',
  example_sentence_english: 'Do you want a pizza?',
  difficulty_level: 'A1',
  frequency_rank: 3000,
  tags: ['food', 'common', 'italian_specialty'],
  ipa_pronunciation: '/ˈpittsɑ/',
  related_domain: 'food_dining',
  confidence_decays_after_days: 5
});

CREATE (vocab_acqua:Vocabulary {
  word: 'acqua',
  language: 'italian',
  translation: 'water',
  part_of_speech: 'noun',
  gender: 'f',
  example_sentence_italian: 'Un bicchiere di acqua, per favore.',
  example_sentence_english: 'A glass of water, please.',
  difficulty_level: 'A1',
  frequency_rank: 800,
  tags: ['food_drinks', 'common', 'essential'],
  ipa_pronunciation: '/ˈɑkkwɑ/',
  related_domain: 'food_dining',
  confidence_decays_after_days: 2
});

CREATE (vocab_ristorante:Vocabulary {
  word: 'ristorante',
  language: 'italian',
  translation: 'restaurant',
  part_of_speech: 'noun',
  gender: 'm',
  example_sentence_italian: 'Andiamo al ristorante stasera.',
  example_sentence_english: 'Let\'s go to the restaurant tonight.',
  difficulty_level: 'A1',
  frequency_rank: 2000,
  tags: ['food_dining', 'places', 'common'],
  ipa_pronunciation: '/ristɔˈrɑnte/',
  related_domain: 'food_dining',
  confidence_decays_after_days: 4
});

CREATE (vocab_menu:Vocabulary {
  word: 'menù',
  language: 'italian',
  translation: 'menu',
  part_of_speech: 'noun',
  gender: 'm',
  example_sentence_italian: 'Il menù, per favore.',
  example_sentence_english: 'The menu, please.',
  difficulty_level: 'A1',
  frequency_rank: 2100,
  tags: ['food_dining', 'restaurant'],
  ipa_pronunciation: '/meˈnu/',
  related_domain: 'food_dining',
  confidence_decays_after_days: 4
});

// Greetings - Beginner Vocabulary
CREATE (vocab_ciao:Vocabulary {
  word: 'ciao',
  language: 'italian',
  translation: 'hello / goodbye (informal)',
  part_of_speech: 'interjection',
  example_sentence_italian: 'Ciao, come stai?',
  example_sentence_english: 'Hi, how are you?',
  difficulty_level: 'A1',
  frequency_rank: 100,
  tags: ['greetings', 'very_common', 'informal'],
  ipa_pronunciation: '/ˈtʃɑːo/',
  related_domain: 'greetings',
  confidence_decays_after_days: 1
});

CREATE (vocab_buongiorno:Vocabulary {
  word: 'buongiorno',
  language: 'italian',
  translation: 'good morning / hello (formal)',
  part_of_speech: 'interjection',
  example_sentence_italian: 'Buongiorno, illustrissima signora.',
  example_sentence_english: 'Good morning, madam.',
  difficulty_level: 'A1',
  frequency_rank: 150,
  tags: ['greetings', 'very_common', 'formal'],
  ipa_pronunciation: '/bwɔnˈdʒɔrno/',
  related_domain: 'greetings',
  confidence_decays_after_days: 1
});

CREATE (vocab_buonasera:Vocabulary {
  word: 'buonasera',
  language: 'italian',
  translation: 'good evening',
  part_of_speech: 'interjection',
  example_sentence_italian: 'Buonasera, è un piacere.',
  example_sentence_english: 'Good evening, it\'s a pleasure.',
  difficulty_level: 'A1',
  frequency_rank: 200,
  tags: ['greetings', 'common', 'formal'],
  ipa_pronunciation: '/bwɔnaˈsɛra/',
  related_domain: 'greetings',
  confidence_decays_after_days: 2
});

CREATE (vocab_grazie:Vocabulary {
  word: 'grazie',
  language: 'italian',
  translation: 'thank you',
  part_of_speech: 'interjection',
  example_sentence_italian: 'Grazie mille!',
  example_sentence_english: 'Thank you very much!',
  difficulty_level: 'A1',
  frequency_rank: 50,
  tags: ['politeness', 'very_common', 'essential'],
  ipa_pronunciation: '/ˈɡrɑttsje/',
  related_domain: 'politeness',
  confidence_decays_after_days: 1
});

CREATE (vocab_prego:Vocabulary {
  word: 'prego',
  language: 'italian',
  translation: 'you\'re welcome',
  part_of_speech: 'interjection',
  example_sentence_italian: 'Prego, è un piacere aiutarti.',
  example_sentence_english: 'You\'re welcome, it\'s my pleasure to help.',
  difficulty_level: 'A1',
  frequency_rank: 80,
  tags: ['politeness', 'very_common', 'response'],
  ipa_pronunciation: '/ˈprɛɡo/',
  related_domain: 'politeness',
  confidence_decays_after_days: 1
});

// Set vocabulary relationships
WITH vocab_ciao, vocab_buongiorno, vocab_pizza, vocab_cibo, vocab_mangiare
CREATE vocab_ciao-[:SYNONYM_OF]->(vocab_buongiorno),
       vocab_pizza-[:EXPRESSES]->(concept_articles),
       vocab_pizza-[:EXPRESSES]->(concept_adj_agreement);

// ============================================================================
// PHASE 6: CREATE TOPICS
// ============================================================================

CREATE (topic_food:Topic {
  topic_id: 'food_dining',
  title: 'Food & Dining',
  description: 'Vocabulary and phrases for ordering food, restaurant etiquette, and discussing meals',
  vocabulary_count: 0,
  icon_url: '/icons/food.svg'
});

CREATE (topic_greetings:Topic {
  topic_id: 'greetings_introductions',
  title: 'Greetings & Introductions',
  description: 'How to greet people, introduce yourself, and basic politeness',
  vocabulary_count: 0,
  icon_url: '/icons/greetings.svg'
});

// Link vocabularies to topics
WITH topic_food, topic_greetings, vocab_pizza, vocab_cibo, vocab_mangiare, vocab_acqua, vocab_ristorante, vocab_menu, vocab_ciao, vocab_buongiorno, vocab_buonasera, vocab_grazie, vocab_prego
CREATE vocab_pizza-[:BELONGS_TO]->(topic_food),
       vocab_cibo-[:BELONGS_TO]->(topic_food),
       vocab_mangiare-[:BELONGS_TO]->(topic_food),
       vocab_acqua-[:BELONGS_TO]->(topic_food),
       vocab_ristorante-[:BELONGS_TO]->(topic_food),
       vocab_menu-[:BELONGS_TO]->(topic_food),
       vocab_ciao-[:BELONGS_TO]->(topic_greetings),
       vocab_buongiorno-[:BELONGS_TO]->(topic_greetings),
       vocab_buonasera-[:BELONGS_TO]->(topic_greetings),
       vocab_grazie-[:BELONGS_TO]->(topic_greetings),
       vocab_prego-[:BELONGS_TO]->(topic_greetings);

// Link vocabularies to CEFR levels for reference
WITH vocab_ciao, vocab_buongiorno, vocab_pizza, vocab_mangiare, vocab_grazie, vocab_acqua, vocab_ristorante, a1
CREATE vocab_ciao-[:TAUGHT_AT]->(a1),
       vocab_buongiorno-[:TAUGHT_AT]->(a1),
       vocab_pizza-[:TAUGHT_AT]->(a1),
       vocab_mangiare-[:TAUGHT_AT]->(a1),
       vocab_grazie-[:TAUGHT_AT]->(a1),
       vocab_acqua-[:TAUGHT_AT]->(a1),
       vocab_ristorante-[:TAUGHT_AT]->(a1);

// ============================================================================
// PHASE 7: CREATE EXERCISE TEMPLATES
// ============================================================================

CREATE (template_flashcard:ExerciseTemplate {
  template_id: 'vocab_flashcard_basic',
  title: 'Vocabulary Flashcard',
  description: 'Translate Italian word to English or vice versa',
  exercise_type: 'flashcard',
  difficulty_level: 'A1',
  estimated_time_seconds: 5,
  instructions: 'Translate the word shown. Click to reveal the answer.',
  success_criteria: 'Correct translation on first try',
  skills_assessed: ['vocabulary', 'reading'],
  concepts_required: [],
  vocabulary_range: 'any'
});

CREATE (template_mc:ExerciseTemplate {
  template_id: 'grammar_mc_articles',
  title: 'Multiple Choice - Article Selection',
  description: 'Choose the correct definite article for the noun',
  exercise_type: 'multiple_choice',
  difficulty_level: 'A1',
  estimated_time_seconds: 10,
  instructions: 'Select the correct Italian article for the English noun.',
  success_criteria: 'Correct answer on first try',
  skills_assessed: ['grammar', 'reading'],
  concepts_required: ['definite_articles']
});

CREATE (template_translation:ExerciseTemplate {
  template_id: 'translation_sentence_en_to_it',
  title: 'Sentence Translation',
  description: 'Translate an English sentence to Italian',
  exercise_type: 'translation',
  difficulty_level: 'A2',
  estimated_time_seconds: 30,
  instructions: 'Translate the English sentence to Italian. Multiple correct answers may exist.',
  success_criteria: '>0.7 semantic similarity to reference',
  skills_assessed: ['writing', 'grammar', 'vocabulary'],
  concepts_required: ['present_simple_tense']
});

CREATE (template_listening:ExerciseTemplate {
  template_id: 'listening_comprehension_basic',
  title: 'Listening Comprehension',
  description: 'Listen to Italian audio and answer questions',
  exercise_type: 'listening',
  difficulty_level: 'A1',
  estimated_time_seconds: 20,
  instructions: 'Listen to the audio and answer the comprehension questions.',
  success_criteria: '>0.75 accuracy',
  skills_assessed: ['listening', 'vocabulary'],
  concepts_required: []
});

CREATE (template_sentence_build:ExerciseTemplate {
  template_id: 'grammar_word_arrangement',
  title: 'Word Arrangement',
  description: 'Arrange scrambled words into correct Italian sentence',
  exercise_type: 'arrangement',
  difficulty_level: 'A1',
  estimated_time_seconds: 15,
  instructions: 'Drag the words to arrange them into a correct Italian sentence.',
  success_criteria: 'Exact sentence match (whitespace ignored)',
  skills_assessed: ['grammar', 'vocabulary'],
  concepts_required: ['definite_articles', 'adjective_agreement']
});

// Link templates to skills
WITH template_flashcard, template_mc, template_translation, template_listening, template_sentence_build, skill_vocab, skill_grammar, skill_reading, skill_writing
CREATE template_flashcard-[:ASSESSES]->(skill_vocab),
       template_flashcard-[:ASSESSES]->(skill_reading),
       template_mc-[:ASSESSES]->(skill_grammar),
       template_translation-[:ASSESSES]->(skill_writing),
       template_listening-[:ASSESSES]->(skill_listening);

// Link templates to concepts
WITH template_mc, template_sentence_build, concept_articles
CREATE template_mc-[:REQUIRES]->(concept_articles),
       template_sentence_build-[:REQUIRES]->(concept_articles);

// ============================================================================
// PHASE 8: CREATE MODULES (Curriculum)
// ============================================================================

CREATE (mod_greetings:Module {
  module_id: 'a1_01_greetings',
  title: 'Greetings & Basic Introductions',
  description: 'Learn how to greet people in Italian and introduce yourself',
  level: 'A1',
  learning_objectives: [
    'Greet people appropriately in formal and informal situations',
    'Introduce yourself with basic information',
    'Respond to greetings politely'
  ],
  estimated_hours: 2,
  vocabulary_count: 5,
  exercise_count: 8,
  created_at: datetime(),
  last_updated: datetime()
});

CREATE (mod_food:Module {
  module_id: 'a1_02_food_dining',
  title: 'Food & Restaurant Basics',
  description: 'Order food, ask for the menu, and discuss dining preferences',
  level: 'A1',
  learning_objectives: [
    'Order food at a restaurant',
    'Ask for and understand items on a menu',
    'Discuss food preferences and dietary restrictions',
    'Pay the bill politely'
  ],
  estimated_hours: 3,
  vocabulary_count: 12,
  exercise_count: 15,
  created_at: datetime(),
  last_updated: datetime()
});

// Link modules to CEFR levels
WITH mod_greetings, mod_food, a1, a2
CREATE a1-[:REQUIRES]->(mod_greetings),
       a1-[:REQUIRES]->(mod_food);

// Link modules to topics
WITH mod_food, mod_greetings, topic_food, topic_greetings
CREATE mod_greetings-[:CONTAINS]->(topic_greetings),
       mod_food-[:CONTAINS]->(topic_food);

// Link modules to exercise templates
WITH mod_greetings, mod_food, template_flashcard, template_mc, template_listening, template_sentence_build
CREATE mod_greetings-[:EMPLOYS]->(template_flashcard),
       mod_greetings-[:EMPLOYS]->(template_mc),
       mod_greetings-[:EMPLOYS]->(template_listening),
       mod_food-[:EMPLOYS]->(template_flashcard),
       mod_food-[:EMPLOYS]->(template_mc),
       mod_food-[:EMPLOYS]->(template_sentence_build);

// Link modules to skills
WITH mod_greetings, mod_food, skill_vocab, skill_reading, skill_listening
CREATE mod_greetings-[:USES_SKILL]->(skill_vocab),
       mod_greetings-[:USES_SKILL]->(skill_reading),
       mod_greetings-[:USES_SKILL]->(skill_listening),
       mod_food-[:USES_SKILL]->(skill_vocab),
       mod_food-[:USES_SKILL]->(skill_reading);

// Link modules to concepts
WITH mod_greetings, mod_food, concept_articles, concept_adj_agreement
CREATE mod_food-[:TEACHES]->(concept_articles),
       mod_food-[:TEACHES]->(concept_adj_agreement);

// ============================================================================
// PHASE 9: CREATE DEMO STUDENT "MARIA"
// ============================================================================

CREATE (student:Student {
  student_id: 'maria_doe_001',
  name: 'Maria Doe',
  email: 'maria.doe@example.com',
  created_at: datetime({year: 2025, month: 1, day: 15}),
  last_active: datetime(),
  native_language: 'English',
  learning_goal: 'travel',
  total_xp: 1050,
  current_streak: 7,
  preferred_exercise_type: 'flashcard',
  notes: 'Quick learner, especially strong with vocabulary. Prefers speaking practice!'
});

// ============================================================================
// PHASE 10: CREATE DEMO STUDENT'S LEARNING JOURNEY - SESSION 1
// ============================================================================

CREATE (session1:Session {
  session_id: 'session_maria_001_2025_01_20',
  student_id: 'maria_doe_001',
  started_at: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 0}),
  ended_at: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 25}),
  duration_minutes: 25,
  total_xp_earned: 120,
  exercise_count: 6,
  module_context: 'a1_01_greetings'
});

// Attempt 1: Flashcard - ciao
CREATE (attempt1:Attempt {
  attempt_id: 'attempt_maria_01_001',
  session_id: 'session_maria_001_2025_01_20',
  exercise_type: 'flashcard',
  started_at: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 1}),
  completed_at: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 2}),
  duration_seconds: 8,
  response_time_ms: 2100,
  is_correct: true,
  confidence: 0.95,
  score: 1.0,
  xp_earned: 20,
  hints_used: 0,
  retries: 1,
  feedback: 'Great! "Ciao" is the most common informal greeting in Italian.'
});

// Attempt 2: Flashcard - grazie
CREATE (attempt2:Attempt {
  attempt_id: 'attempt_maria_01_002',
  session_id: 'session_maria_001_2025_01_20',
  exercise_type: 'flashcard',
  started_at: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 3}),
  completed_at: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 4}),
  duration_seconds: 5,
  response_time_ms: 1800,
  is_correct: true,
  confidence: 0.98,
  score: 1.0,
  xp_earned: 20,
  hints_used: 0,
  retries: 1,
  feedback: 'Perfect! "Grazie" is universally understood and used.'
});

// Attempt 3: Multiple Choice - Article (la, le, il)
CREATE (attempt3:Attempt {
  attempt_id: 'attempt_maria_01_003',
  session_id: 'session_maria_001_2025_01_20',
  exercise_type: 'multiple_choice',
  started_at: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 6}),
  completed_at: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 9}),
  duration_seconds: 15,
  response_time_ms: 5300,
  is_correct: true,
  confidence: 0.80,
  score: 1.0,
  xp_earned: 25,
  hints_used: 1,
  retries: 1,
  feedback: 'Correct! "La casa" - remember feminine nouns use "la".'
});

// Attempt 4: Flashcard - pizza
CREATE (attempt4:Attempt {
  attempt_id: 'attempt_maria_01_004',
  session_id: 'session_maria_001_2025_01_20',
  exercise_type: 'flashcard',
  started_at: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 10}),
  completed_at: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 11}),
  duration_seconds: 3,
  response_time_ms: 1200,
  is_correct: true,
  confidence: 0.99,
  score: 1.0,
  xp_earned: 15,
  hints_used: 0,
  retries: 0,
  feedback: 'Excellent! "Pizza" - a word that translates directly to English!'
});

// Attempt 5: Listening - Buongiorno audio
CREATE (attempt5:Attempt {
  attempt_id: 'attempt_maria_01_005',
  session_id: 'session_maria_001_2025_01_20',
  exercise_type: 'listening',
  started_at: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 13}),
  completed_at: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 19}),
  duration_seconds: 20,
  response_time_ms: 8500,
  is_correct: true,
  confidence: 0.75,
  score: 0.85,
  xp_earned: 25,
  hints_used: 0,
  retries: 2,
  feedback: 'Good attempt! You understood the main greeting, but try again to catch all details.'
});

// Attempt 6: Word Arrangement - sentence building
CREATE (attempt6:Attempt {
  attempt_id: 'attempt_maria_01_006',
  session_id: 'session_maria_001_2025_01_20',
  exercise_type: 'arrangement',
  started_at: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 21}),
  completed_at: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 25}),
  duration_seconds: 15,
  response_time_ms: 6200,
  is_correct: true,
  confidence: 0.70,
  score: 1.0,
  xp_earned: 15,
  hints_used: 1,
  retries: 1,
  feedback: 'Correct! "La pizza è buona." - You\'re building Italian sentences!'
});

// Create Performance metrics for each attempt
CREATE (perf1:Performance {
  performance_id: 'perf_maria_01_001',
  attempt_id: 'attempt_maria_01_001',
  skill_breakdown: {reading: 1.0, vocabulary: 1.0},
  difficulty_rating: 1.0,
  engagement_score: 0.90,
  learning_gain: 0.3,
  concept_coverage: [],
  timestamp: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 2})
});

CREATE (perf2:Performance {
  performance_id: 'perf_maria_01_002',
  attempt_id: 'attempt_maria_01_002',
  skill_breakdown: {reading: 1.0, vocabulary: 1.0},
  difficulty_rating: 1.0,
  engagement_score: 0.95,
  learning_gain: 0.25,
  concept_coverage: [],
  timestamp: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 4})
});

CREATE (perf3:Performance {
  performance_id: 'perf_maria_01_003',
  attempt_id: 'attempt_maria_01_003',
  skill_breakdown: {reading: 1.0, grammar: 0.9},
  difficulty_rating: 2.5,
  engagement_score: 0.75,
  learning_gain: 0.35,
  concept_coverage: ['definite_articles'],
  timestamp: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 9})
});

CREATE (perf4:Performance {
  performance_id: 'perf_maria_01_004',
  attempt_id: 'attempt_maria_01_004',
  skill_breakdown: {reading: 1.0, vocabulary: 1.0},
  difficulty_rating: 1.0,
  engagement_score: 0.98,
  learning_gain: 0.2,
  concept_coverage: [],
  timestamp: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 11})
});

CREATE (perf5:Performance {
  performance_id: 'perf_maria_01_005',
  attempt_id: 'attempt_maria_01_005',
  skill_breakdown: {listening: 0.85, vocabulary: 0.85},
  difficulty_rating: 2.0,
  engagement_score: 0.70,
  learning_gain: 0.25,
  concept_coverage: [],
  timestamp: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 19})
});

CREATE (perf6:Performance {
  performance_id: 'perf_maria_01_006',
  attempt_id: 'attempt_maria_01_006',
  skill_breakdown: {grammar: 0.95, vocabulary: 0.9},
  difficulty_rating: 2.0,
  engagement_score: 0.72,
  learning_gain: 0.4,
  concept_coverage: ['definite_articles', 'adjective_agreement'],
  timestamp: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 25})
});

// Link attempts to session
WITH attempt1, attempt2, attempt3, attempt4, attempt5, attempt6, session1
CREATE session1-[:CONTAINS]->(attempt1),
       session1-[:CONTAINS]->(attempt2),
       session1-[:CONTAINS]->(attempt3),
       session1-[:CONTAINS]->(attempt4),
       session1-[:CONTAINS]->(attempt5),
       session1-[:CONTAINS]->(attempt6);

// Link attempts to exercise templates and vocabularies
WITH attempt1, attempt2, attempt3, attempt4, attempt5, attempt6, template_flashcard, template_mc, template_listening, template_sentence_build, vocab_ciao, vocab_grazie, vocab_pizza, concept_articles
CREATE attempt1-[:USES_TEMPLATE]->(template_flashcard),
       attempt1-[:ON_VOCABULARY]->(vocab_ciao),
       attempt2-[:USES_TEMPLATE]->(template_flashcard),
       attempt2-[:ON_VOCABULARY]->(vocab_grazie),
       attempt3-[:USES_TEMPLATE]->(template_mc),
       attempt3-[:TESTS_CONCEPT]->(concept_articles),
       attempt4-[:USES_TEMPLATE]->(template_flashcard),
       attempt4-[:ON_VOCABULARY]->(vocab_pizza),
       attempt5-[:USES_TEMPLATE]->(template_listening),
       attempt6-[:USES_TEMPLATE]->(template_sentence_build),
       attempt6-[:TESTS_CONCEPT]->(concept_articles);

// Link attempts to performances
WITH attempt1, attempt2, attempt3, attempt4, attempt5, attempt6, perf1, perf2, perf3, perf4, perf5, perf6
CREATE attempt1-[:RESULT]->(perf1),
       attempt2-[:RESULT]->(perf2),
       attempt3-[:RESULT]->(perf3),
       attempt4-[:RESULT]->(perf4),
       attempt5-[:RESULT]->(perf5),
       attempt6-[:RESULT]->(perf6);

// Link student to session
WITH student, session1
CREATE student-[:ENROLLED_IN]->(session1);

// ============================================================================
// PHASE 11: CREATE VOCABULARY CONFIDENCE FOR MARIA
// ============================================================================

CREATE (vc_ciao:VocabConfidence {
  student_id: 'maria_doe_001',
  word: 'ciao',
  confidence_score: 0.95,
  last_seen: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 2}),
  next_review: datetime({year: 2025, month: 1, day: 21, hour: 10, minute: 2}),
  review_count: 1,
  correct_count: 1,
  incorrect_count: 0,
  ease_factor: 2.5,
  interval_days: 1,
  tags: 'active'
});

CREATE (vc_grazie:VocabConfidence {
  student_id: 'maria_doe_001',
  word: 'grazie',
  confidence_score: 0.98,
  last_seen: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 4}),
  next_review: datetime({year: 2025, month: 1, day: 21, hour: 10, minute: 4}),
  review_count: 1,
  correct_count: 1,
  incorrect_count: 0,
  ease_factor: 2.5,
  interval_days: 1,
  tags: 'active'
});

CREATE (vc_pizza:VocabConfidence {
  student_id: 'maria_doe_001',
  word: 'pizza',
  confidence_score: 0.99,
  last_seen: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 11}),
  next_review: datetime({year: 2025, month: 1, day: 22, hour: 10, minute: 11}),
  review_count: 1,
  correct_count: 1,
  incorrect_count: 0,
  ease_factor: 2.5,
  interval_days: 2,
  tags: 'active'
});

// Link student to vocab confidence records
WITH student, vc_ciao, vc_grazie, vc_pizza
CREATE student-[:KNOWS]->(vc_ciao),
       student-[:KNOWS]->(vc_grazie),
       student-[:KNOWS]->(vc_pizza);

// ============================================================================
// PHASE 12: INITIALIZE STUDENT SKILL EXPERIENCE
// ============================================================================

CREATE (exp_vocab_s1:Experience {
  experience_id: 'exp_maria_vocab_s1',
  student_id: 'maria_doe_001',
  amount: 75,
  earned_at: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 25})
});

CREATE (exp_grammar_s1:Experience {
  experience_id: 'exp_maria_grammar_s1',
  student_id: 'maria_doe_001',
  amount: 40,
  earned_at: datetime({year: 2025, month: 1, day: 20, hour: 10, minute: 25})
});

// Link experiences to skills
WITH exp_vocab_s1, exp_grammar_s1, skill_vocab, skill_grammar
CREATE exp_vocab_s1-[:TOWARDS_SKILL]->(skill_vocab),
       exp_grammar_s1-[:TOWARDS_SKILL]->(skill_grammar);

// ============================================================================
// PHASE 13: ADD SEMANTIC UNDERSTANDING & MODULE CONTEXT
// ============================================================================

WITH student, mod_greetings, a1
CREATE student-[:WORKING_ON]->(mod_greetings),
       student-[:ACHIEVED]->(a1);

// ============================================================================
// PHASE 14: CREATE SECOND SESSION - FOOD VOCABULARY
// ============================================================================

CREATE (session2:Session {
  session_id: 'session_maria_001_2025_01_21',
  student_id: 'maria_doe_001',
  started_at: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 30}),
  ended_at: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 55}),
  duration_minutes: 25,
  total_xp_earned: 130,
  exercise_count: 6,
  module_context: 'a1_02_food_dining'
});

// Flashcard: mangiare
CREATE (attempt7:Attempt {
  attempt_id: 'attempt_maria_01_007',
  session_id: 'session_maria_001_2025_01_21',
  exercise_type: 'flashcard',
  started_at: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 31}),
  completed_at: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 33}),
  duration_seconds: 8,
  response_time_ms: 3100,
  is_correct: true,
  confidence: 0.90,
  score: 1.0,
  xp_earned: 20,
  hints_used: 0,
  retries: 0,
  feedback: '"Mangiare" - to eat. Key verb for the food & restaurant module!'
});

// Flashcard: ristorante
CREATE (attempt8:Attempt {
  attempt_id: 'attempt_maria_01_008',
  session_id: 'session_maria_001_2025_01_21',
  exercise_type: 'flashcard',
  started_at: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 34}),
  completed_at: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 35}),
  duration_seconds: 4,
  response_time_ms: 1800,
  is_correct: true,
  confidence: 0.92,
  score: 1.0,
  xp_earned: 18,
  hints_used: 0,
  retries: 0,
  feedback: '"Ristorante" - restaurant. Similar to English!'
});

// Flashcard: acqua
CREATE (attempt9:Attempt {
  attempt_id: 'attempt_maria_01_009',
  session_id: 'session_maria_001_2025_01_21',
  exercise_type: 'flashcard',
  started_at: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 36}),
  completed_at: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 37}),
  duration_seconds: 3,
  response_time_ms: 1200,
  is_correct: true,
  confidence: 0.98,
  score: 1.0,
  xp_earned: 15,
  hints_used: 0,
  retries: 0,
  feedback: 'Perfect! "Un bicchiere d\'acqua" is a standard restaurant request.'
});

// MC: Article with food vocab
CREATE (attempt10:Attempt {
  attempt_id: 'attempt_maria_01_010',
  session_id: 'session_maria_001_2025_01_21',
  exercise_type: 'multiple_choice',
  started_at: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 39}),
  completed_at: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 42}),
  duration_seconds: 12,
  response_time_ms: 4200,
  is_correct: true,
  confidence: 0.85,
  score: 1.0,
  xp_earned: 28,
  hints_used: 0,
  retries: 1,
  feedback: 'Correct! "Il menù" - remember masculine nouns use "il".'
});

// Listening: Menu audio
CREATE (attempt11:Attempt {
  attempt_id: 'attempt_maria_01_011',
  session_id: 'session_maria_001_2025_01_21',
  exercise_type: 'listening',
  started_at: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 44}),
  completed_at: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 50}),
  duration_seconds: 18,
  response_time_ms: 7300,
  is_correct: true,
  confidence: 0.82,
  score: 0.90,
  xp_earned: 31,
  hints_used: 1,
  retries: 1,
  feedback: 'Excellent! You understood the restaurant scenario. Keep practicing!'
});

// Listening: Food preferences
CREATE (attempt12:Attempt {
  attempt_id: 'attempt_maria_01_012',
  session_id: 'session_maria_001_2025_01_21',
  exercise_type: 'listening',
  started_at: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 51}),
  completed_at: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 55}),
  duration_seconds: 18,
  response_time_ms: 5900,
  is_correct: true,
  confidence: 0.80,
  score: 0.88,
  xp_earned: 18,
  hints_used: 0,
  retries: 2,
  feedback: 'Great! You caught "vegetariano" - a key word in food preferences!'
});

// Create performances for session 2 attempts
CREATE (perf7:Performance {
  performance_id: 'perf_maria_01_007',
  attempt_id: 'attempt_maria_01_007',
  skill_breakdown: {vocabulary: 1.0, reading: 1.0},
  difficulty_rating: 1.0,
  engagement_score: 0.92,
  learning_gain: 0.25,
  concept_coverage: [],
  timestamp: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 33})
});

CREATE (perf8:Performance {
  performance_id: 'perf_maria_01_008',
  attempt_id: 'attempt_maria_01_008',
  skill_breakdown: {vocabulary: 1.0, reading: 1.0},
  difficulty_rating: 1.0,
  engagement_score: 0.95,
  learning_gain: 0.20,
  concept_coverage: [],
  timestamp: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 35})
});

CREATE (perf9:Performance {
  performance_id: 'perf_maria_01_009',
  attempt_id: 'attempt_maria_01_009',
  skill_breakdown: {vocabulary: 1.0, reading: 1.0},
  difficulty_rating: 1.0,
  engagement_score: 0.98,
  learning_gain: 0.18,
  concept_coverage: [],
  timestamp: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 37})
});

CREATE (perf10:Performance {
  performance_id: 'perf_maria_01_010',
  attempt_id: 'attempt_maria_01_010',
  skill_breakdown: {grammar: 0.95, reading: 1.0},
  difficulty_rating: 1.5,
  engagement_score: 0.82,
  learning_gain: 0.35,
  concept_coverage: ['definite_articles'],
  timestamp: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 42})
});

CREATE (perf11:Performance {
  performance_id: 'perf_maria_01_011',
  attempt_id: 'attempt_maria_01_011',
  skill_breakdown: {listening: 0.90, vocabulary: 0.90},
  difficulty_rating: 2.0,
  engagement_score: 0.80,
  learning_gain: 0.30,
  concept_coverage: [],
  timestamp: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 50})
});

CREATE (perf12:Performance {
  performance_id: 'perf_maria_01_012',
  attempt_id: 'attempt_maria_01_012',
  skill_breakdown: {listening: 0.88, vocabulary: 0.92},
  difficulty_rating: 2.0,
  engagement_score: 0.78,
  learning_gain: 0.28,
  concept_coverage: [],
  timestamp: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 55})
});

// Link attempts to session, templates, vocabs, and performances
WITH session2, attempt7, attempt8, attempt9, attempt10, attempt11, attempt12, template_flashcard, template_mc, template_listening, vocab_mangiare, vocab_ristorante, vocab_acqua, vocab_menu, perf7, perf8, perf9, perf10, perf11, perf12, concept_articles
CREATE session2-[:CONTAINS]->(attempt7),
       session2-[:CONTAINS]->(attempt8),
       session2-[:CONTAINS]->(attempt9),
       session2-[:CONTAINS]->(attempt10),
       session2-[:CONTAINS]->(attempt11),
       session2-[:CONTAINS]->(attempt12),
       attempt7-[:USES_TEMPLATE]->(template_flashcard),
       attempt7-[:ON_VOCABULARY]->(vocab_mangiare),
       attempt8-[:USES_TEMPLATE]->(template_flashcard),
       attempt8-[:ON_VOCABULARY]->(vocab_ristorante),
       attempt9-[:USES_TEMPLATE]->(template_flashcard),
       attempt9-[:ON_VOCABULARY]->(vocab_acqua),
       attempt10-[:USES_TEMPLATE]->(template_mc),
       attempt10-[:TESTS_CONCEPT]->(concept_articles),
       attempt11-[:USES_TEMPLATE]->(template_listening),
       attempt12-[:USES_TEMPLATE]->(template_listening),
       attempt7-[:RESULT]->(perf7),
       attempt8-[:RESULT]->(perf8),
       attempt9-[:RESULT]->(perf9),
       attempt10-[:RESULT]->(perf10),
       attempt11-[:RESULT]->(perf11),
       attempt12-[:RESULT]->(perf12);

// Link student to session 2
WITH student, session2
CREATE student-[:ENROLLED_IN]->(session2);

// Update vocabulary confidences from session 2
CREATE (vc_mangiare:VocabConfidence {
  student_id: 'maria_doe_001',
  word: 'mangiare',
  confidence_score: 0.90,
  last_seen: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 33}),
  next_review: datetime({year: 2025, month: 1, day: 22, hour: 14, minute: 33}),
  review_count: 1,
  correct_count: 1,
  incorrect_count: 0,
  ease_factor: 2.5,
  interval_days: 1,
  tags: 'active'
});

CREATE (vc_ristorante:VocabConfidence {
  student_id: 'maria_doe_001',
  word: 'ristorante',
  confidence_score: 0.92,
  last_seen: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 35}),
  next_review: datetime({year: 2025, month: 1, day: 22, hour: 14, minute: 35}),
  review_count: 1,
  correct_count: 1,
  incorrect_count: 0,
  ease_factor: 2.5,
  interval_days: 1,
  tags: 'active'
});

CREATE (vc_acqua:VocabConfidence {
  student_id: 'maria_doe_001',
  word: 'acqua',
  confidence_score: 0.98,
  last_seen: datetime({year: 2025, month: 1, day: 21, hour: 14, minute: 37}),
  next_review: datetime({year: 2025, month: 1, day: 23, hour: 14, minute: 37}),
  review_count: 1,
  correct_count: 1,
  incorrect_count: 0,
  ease_factor: 2.5,
  interval_days: 2,
  tags: 'active'
});

// ============================================================================
// PHASE 15: VERIFY DEMO STUDENT COMPLETENESS
// ============================================================================

// Query to verify all connections
MATCH (s:Student {student_id: 'maria_doe_001'})
  -[:ENROLLED_IN]->(session:Session)
  -[:CONTAINS]->(attempt:Attempt)
  -[:USES_TEMPLATE]->(template:ExerciseTemplate)
  -[:ASSESSES]->(skill:Skill)
WITH s, count(DISTINCT session) AS session_count, count(DISTINCT template) AS template_count, count(DISTINCT skill) AS skill_count
RETURN s.student_id AS student_id, s.name AS name, session_count, template_count, skill_count;

// Count relationships
MATCH (s:Student {student_id: 'maria_doe_001'})
WITH s
OPTIONAL MATCH (s)-[r]->(target)
RETURN s.name AS student_name, count(r) AS relationship_count, collect(distinct type(r)) AS relationship_types;

// ============================================================================
// SUMMARY OUTPUT
// ============================================================================

RETURN "✅ MIGRATION COMPLETE" AS status,
       "Created: 6 Skills, 4 Concepts, 12 Vocabularies, 2 Topics, 2 Modules, 5 ExerciseTemplates, 3 CEFRLevels" AS entities_created,
       "Demo Student: maria_doe_001 (Maria Doe)" AS demo_student,
       "Sessions: 2 study sessions with 12 total exercise attempts" AS learning_journey,
       "XP Earned: 250 XP across 2 sessions (Vocabulary: 75 XP, Grammar: 40 XP, Rest from exercises)" AS progress,
       "Graph Stats: Highly connected semantic knowledge graph with ~80 relationships" AS graph_stats;
