"""
Question bank for the Italian Placement Test.

Organized by CEFR level with modular structure for easy maintenance and extension.
Uses Pydantic models for type safety and validation.
"""

from italianollama.backend.placement_test.models import (
    CEFRLevel,
    Question,
    QuestionOption,
    TestSection,
    PlacementTestConfig,
)


# ============================================================================
# SECTION A: A1 LEVEL (Questions 1-10)
# ============================================================================


# ==========================================================================
# SECTION A: A1 LEVEL (Questions 1-60)
# ==========================================================================

SECTION_A_QUESTIONS = [

# Original 10 questions
    Question(
        id=1,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-1: Questa è una domanda di esempio per il livello A1 numero 1.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 1"),
            QuestionOption(key="b", text="Risposta B esempio 1"),
            QuestionOption(key="c", text="Risposta C esempio 1"),
            QuestionOption(key="d", text="Risposta D esempio 1"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 1",
        grammar_point="Grammatica A1 esempio 1"
    ),

    Question(
        id=2,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-2: Questa è una domanda di esempio per il livello A1 numero 2.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 2"),
            QuestionOption(key="b", text="Risposta B esempio 2"),
            QuestionOption(key="c", text="Risposta C esempio 2"),
            QuestionOption(key="d", text="Risposta D esempio 2"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 2",
        grammar_point="Grammatica A1 esempio 2"
    ),

    Question(
        id=3,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-3: Questa è una domanda di esempio per il livello A1 numero 3.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 3"),
            QuestionOption(key="b", text="Risposta B esempio 3"),
            QuestionOption(key="c", text="Risposta C esempio 3"),
            QuestionOption(key="d", text="Risposta D esempio 3"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 3",
        grammar_point="Grammatica A1 esempio 3"
    ),

    Question(
        id=4,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-4: Questa è una domanda di esempio per il livello A1 numero 4.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 4"),
            QuestionOption(key="b", text="Risposta B esempio 4"),
            QuestionOption(key="c", text="Risposta C esempio 4"),
            QuestionOption(key="d", text="Risposta D esempio 4"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 4",
        grammar_point="Grammatica A1 esempio 4"
    ),

    Question(
        id=5,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-5: Questa è una domanda di esempio per il livello A1 numero 5.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 5"),
            QuestionOption(key="b", text="Risposta B esempio 5"),
            QuestionOption(key="c", text="Risposta C esempio 5"),
            QuestionOption(key="d", text="Risposta D esempio 5"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 5",
        grammar_point="Grammatica A1 esempio 5"
    ),

    Question(
        id=6,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-6: Questa è una domanda di esempio per il livello A1 numero 6.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 6"),
            QuestionOption(key="b", text="Risposta B esempio 6"),
            QuestionOption(key="c", text="Risposta C esempio 6"),
            QuestionOption(key="d", text="Risposta D esempio 6"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 6",
        grammar_point="Grammatica A1 esempio 6"
    ),

    Question(
        id=7,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-7: Questa è una domanda di esempio per il livello A1 numero 7.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 7"),
            QuestionOption(key="b", text="Risposta B esempio 7"),
            QuestionOption(key="c", text="Risposta C esempio 7"),
            QuestionOption(key="d", text="Risposta D esempio 7"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 7",
        grammar_point="Grammatica A1 esempio 7"
    ),

    Question(
        id=8,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-8: Questa è una domanda di esempio per il livello A1 numero 8.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 8"),
            QuestionOption(key="b", text="Risposta B esempio 8"),
            QuestionOption(key="c", text="Risposta C esempio 8"),
            QuestionOption(key="d", text="Risposta D esempio 8"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 8",
        grammar_point="Grammatica A1 esempio 8"
    ),

    Question(
        id=9,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-9: Questa è una domanda di esempio per il livello A1 numero 9.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 9"),
            QuestionOption(key="b", text="Risposta B esempio 9"),
            QuestionOption(key="c", text="Risposta C esempio 9"),
            QuestionOption(key="d", text="Risposta D esempio 9"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 9",
        grammar_point="Grammatica A1 esempio 9"
    ),

    Question(
        id=10,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-10: Questa è una domanda di esempio per il livello A1 numero 10.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 10"),
            QuestionOption(key="b", text="Risposta B esempio 10"),
            QuestionOption(key="c", text="Risposta C esempio 10"),
            QuestionOption(key="d", text="Risposta D esempio 10"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 10",
        grammar_point="Grammatica A1 esempio 10"
    ),

    Question(
        id=11,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-11: Questa è una domanda di esempio per il livello A1 numero 11.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 11"),
            QuestionOption(key="b", text="Risposta B esempio 11"),
            QuestionOption(key="c", text="Risposta C esempio 11"),
            QuestionOption(key="d", text="Risposta D esempio 11"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 11",
        grammar_point="Grammatica A1 esempio 11"
    ),

    Question(
        id=12,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-12: Questa è una domanda di esempio per il livello A1 numero 12.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 12"),
            QuestionOption(key="b", text="Risposta B esempio 12"),
            QuestionOption(key="c", text="Risposta C esempio 12"),
            QuestionOption(key="d", text="Risposta D esempio 12"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 12",
        grammar_point="Grammatica A1 esempio 12"
    ),

    Question(
        id=13,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-13: Questa è una domanda di esempio per il livello A1 numero 13.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 13"),
            QuestionOption(key="b", text="Risposta B esempio 13"),
            QuestionOption(key="c", text="Risposta C esempio 13"),
            QuestionOption(key="d", text="Risposta D esempio 13"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 13",
        grammar_point="Grammatica A1 esempio 13"
    ),

    Question(
        id=14,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-14: Questa è una domanda di esempio per il livello A1 numero 14.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 14"),
            QuestionOption(key="b", text="Risposta B esempio 14"),
            QuestionOption(key="c", text="Risposta C esempio 14"),
            QuestionOption(key="d", text="Risposta D esempio 14"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 14",
        grammar_point="Grammatica A1 esempio 14"
    ),

    Question(
        id=15,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-15: Questa è una domanda di esempio per il livello A1 numero 15.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 15"),
            QuestionOption(key="b", text="Risposta B esempio 15"),
            QuestionOption(key="c", text="Risposta C esempio 15"),
            QuestionOption(key="d", text="Risposta D esempio 15"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 15",
        grammar_point="Grammatica A1 esempio 15"
    ),

    Question(
        id=16,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-16: Questa è una domanda di esempio per il livello A1 numero 16.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 16"),
            QuestionOption(key="b", text="Risposta B esempio 16"),
            QuestionOption(key="c", text="Risposta C esempio 16"),
            QuestionOption(key="d", text="Risposta D esempio 16"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 16",
        grammar_point="Grammatica A1 esempio 16"
    ),

    Question(
        id=17,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-17: Questa è una domanda di esempio per il livello A1 numero 17.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 17"),
            QuestionOption(key="b", text="Risposta B esempio 17"),
            QuestionOption(key="c", text="Risposta C esempio 17"),
            QuestionOption(key="d", text="Risposta D esempio 17"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 17",
        grammar_point="Grammatica A1 esempio 17"
    ),

    Question(
        id=18,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-18: Questa è una domanda di esempio per il livello A1 numero 18.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 18"),
            QuestionOption(key="b", text="Risposta B esempio 18"),
            QuestionOption(key="c", text="Risposta C esempio 18"),
            QuestionOption(key="d", text="Risposta D esempio 18"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 18",
        grammar_point="Grammatica A1 esempio 18"
    ),

    Question(
        id=19,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-19: Questa è una domanda di esempio per il livello A1 numero 19.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 19"),
            QuestionOption(key="b", text="Risposta B esempio 19"),
            QuestionOption(key="c", text="Risposta C esempio 19"),
            QuestionOption(key="d", text="Risposta D esempio 19"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 19",
        grammar_point="Grammatica A1 esempio 19"
    ),

    Question(
        id=20,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-20: Questa è una domanda di esempio per il livello A1 numero 20.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 20"),
            QuestionOption(key="b", text="Risposta B esempio 20"),
            QuestionOption(key="c", text="Risposta C esempio 20"),
            QuestionOption(key="d", text="Risposta D esempio 20"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 20",
        grammar_point="Grammatica A1 esempio 20"
    ),

    Question(
        id=21,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-21: Questa è una domanda di esempio per il livello A1 numero 21.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 21"),
            QuestionOption(key="b", text="Risposta B esempio 21"),
            QuestionOption(key="c", text="Risposta C esempio 21"),
            QuestionOption(key="d", text="Risposta D esempio 21"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 21",
        grammar_point="Grammatica A1 esempio 21"
    ),

    Question(
        id=22,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-22: Questa è una domanda di esempio per il livello A1 numero 22.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 22"),
            QuestionOption(key="b", text="Risposta B esempio 22"),
            QuestionOption(key="c", text="Risposta C esempio 22"),
            QuestionOption(key="d", text="Risposta D esempio 22"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 22",
        grammar_point="Grammatica A1 esempio 22"
    ),

    Question(
        id=23,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-23: Questa è una domanda di esempio per il livello A1 numero 23.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 23"),
            QuestionOption(key="b", text="Risposta B esempio 23"),
            QuestionOption(key="c", text="Risposta C esempio 23"),
            QuestionOption(key="d", text="Risposta D esempio 23"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 23",
        grammar_point="Grammatica A1 esempio 23"
    ),

    Question(
        id=24,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-24: Questa è una domanda di esempio per il livello A1 numero 24.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 24"),
            QuestionOption(key="b", text="Risposta B esempio 24"),
            QuestionOption(key="c", text="Risposta C esempio 24"),
            QuestionOption(key="d", text="Risposta D esempio 24"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 24",
        grammar_point="Grammatica A1 esempio 24"
    ),

    Question(
        id=25,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-25: Questa è una domanda di esempio per il livello A1 numero 25.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 25"),
            QuestionOption(key="b", text="Risposta B esempio 25"),
            QuestionOption(key="c", text="Risposta C esempio 25"),
            QuestionOption(key="d", text="Risposta D esempio 25"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 25",
        grammar_point="Grammatica A1 esempio 25"
    ),

    Question(
        id=26,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-26: Questa è una domanda di esempio per il livello A1 numero 26.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 26"),
            QuestionOption(key="b", text="Risposta B esempio 26"),
            QuestionOption(key="c", text="Risposta C esempio 26"),
            QuestionOption(key="d", text="Risposta D esempio 26"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 26",
        grammar_point="Grammatica A1 esempio 26"
    ),

    Question(
        id=27,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-27: Questa è una domanda di esempio per il livello A1 numero 27.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 27"),
            QuestionOption(key="b", text="Risposta B esempio 27"),
            QuestionOption(key="c", text="Risposta C esempio 27"),
            QuestionOption(key="d", text="Risposta D esempio 27"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 27",
        grammar_point="Grammatica A1 esempio 27"
    ),

    Question(
        id=28,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-28: Questa è una domanda di esempio per il livello A1 numero 28.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 28"),
            QuestionOption(key="b", text="Risposta B esempio 28"),
            QuestionOption(key="c", text="Risposta C esempio 28"),
            QuestionOption(key="d", text="Risposta D esempio 28"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 28",
        grammar_point="Grammatica A1 esempio 28"
    ),

    Question(
        id=29,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-29: Questa è una domanda di esempio per il livello A1 numero 29.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 29"),
            QuestionOption(key="b", text="Risposta B esempio 29"),
            QuestionOption(key="c", text="Risposta C esempio 29"),
            QuestionOption(key="d", text="Risposta D esempio 29"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 29",
        grammar_point="Grammatica A1 esempio 29"
    ),

    Question(
        id=30,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-30: Questa è una domanda di esempio per il livello A1 numero 30.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 30"),
            QuestionOption(key="b", text="Risposta B esempio 30"),
            QuestionOption(key="c", text="Risposta C esempio 30"),
            QuestionOption(key="d", text="Risposta D esempio 30"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 30",
        grammar_point="Grammatica A1 esempio 30"
    ),

    Question(
        id=31,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-31: Questa è una domanda di esempio per il livello A1 numero 31.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 31"),
            QuestionOption(key="b", text="Risposta B esempio 31"),
            QuestionOption(key="c", text="Risposta C esempio 31"),
            QuestionOption(key="d", text="Risposta D esempio 31"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 31",
        grammar_point="Grammatica A1 esempio 31"
    ),

    Question(
        id=32,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-32: Questa è una domanda di esempio per il livello A1 numero 32.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 32"),
            QuestionOption(key="b", text="Risposta B esempio 32"),
            QuestionOption(key="c", text="Risposta C esempio 32"),
            QuestionOption(key="d", text="Risposta D esempio 32"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 32",
        grammar_point="Grammatica A1 esempio 32"
    ),

    Question(
        id=33,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-33: Questa è una domanda di esempio per il livello A1 numero 33.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 33"),
            QuestionOption(key="b", text="Risposta B esempio 33"),
            QuestionOption(key="c", text="Risposta C esempio 33"),
            QuestionOption(key="d", text="Risposta D esempio 33"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 33",
        grammar_point="Grammatica A1 esempio 33"
    ),

    Question(
        id=34,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-34: Questa è una domanda di esempio per il livello A1 numero 34.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 34"),
            QuestionOption(key="b", text="Risposta B esempio 34"),
            QuestionOption(key="c", text="Risposta C esempio 34"),
            QuestionOption(key="d", text="Risposta D esempio 34"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 34",
        grammar_point="Grammatica A1 esempio 34"
    ),

    Question(
        id=35,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-35: Questa è una domanda di esempio per il livello A1 numero 35.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 35"),
            QuestionOption(key="b", text="Risposta B esempio 35"),
            QuestionOption(key="c", text="Risposta C esempio 35"),
            QuestionOption(key="d", text="Risposta D esempio 35"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 35",
        grammar_point="Grammatica A1 esempio 35"
    ),

    Question(
        id=36,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-36: Questa è una domanda di esempio per il livello A1 numero 36.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 36"),
            QuestionOption(key="b", text="Risposta B esempio 36"),
            QuestionOption(key="c", text="Risposta C esempio 36"),
            QuestionOption(key="d", text="Risposta D esempio 36"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 36",
        grammar_point="Grammatica A1 esempio 36"
    ),

    Question(
        id=37,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-37: Questa è una domanda di esempio per il livello A1 numero 37.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 37"),
            QuestionOption(key="b", text="Risposta B esempio 37"),
            QuestionOption(key="c", text="Risposta C esempio 37"),
            QuestionOption(key="d", text="Risposta D esempio 37"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 37",
        grammar_point="Grammatica A1 esempio 37"
    ),

    Question(
        id=38,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-38: Questa è una domanda di esempio per il livello A1 numero 38.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 38"),
            QuestionOption(key="b", text="Risposta B esempio 38"),
            QuestionOption(key="c", text="Risposta C esempio 38"),
            QuestionOption(key="d", text="Risposta D esempio 38"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 38",
        grammar_point="Grammatica A1 esempio 38"
    ),

    Question(
        id=39,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-39: Questa è una domanda di esempio per il livello A1 numero 39.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 39"),
            QuestionOption(key="b", text="Risposta B esempio 39"),
            QuestionOption(key="c", text="Risposta C esempio 39"),
            QuestionOption(key="d", text="Risposta D esempio 39"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 39",
        grammar_point="Grammatica A1 esempio 39"
    ),

    Question(
        id=40,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-40: Questa è una domanda di esempio per il livello A1 numero 40.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 40"),
            QuestionOption(key="b", text="Risposta B esempio 40"),
            QuestionOption(key="c", text="Risposta C esempio 40"),
            QuestionOption(key="d", text="Risposta D esempio 40"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 40",
        grammar_point="Grammatica A1 esempio 40"
    ),

    Question(
        id=41,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-41: Questa è una domanda di esempio per il livello A1 numero 41.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 41"),
            QuestionOption(key="b", text="Risposta B esempio 41"),
            QuestionOption(key="c", text="Risposta C esempio 41"),
            QuestionOption(key="d", text="Risposta D esempio 41"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 41",
        grammar_point="Grammatica A1 esempio 41"
    ),

    Question(
        id=42,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-42: Questa è una domanda di esempio per il livello A1 numero 42.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 42"),
            QuestionOption(key="b", text="Risposta B esempio 42"),
            QuestionOption(key="c", text="Risposta C esempio 42"),
            QuestionOption(key="d", text="Risposta D esempio 42"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 42",
        grammar_point="Grammatica A1 esempio 42"
    ),

    Question(
        id=43,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-43: Questa è una domanda di esempio per il livello A1 numero 43.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 43"),
            QuestionOption(key="b", text="Risposta B esempio 43"),
            QuestionOption(key="c", text="Risposta C esempio 43"),
            QuestionOption(key="d", text="Risposta D esempio 43"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 43",
        grammar_point="Grammatica A1 esempio 43"
    ),

    Question(
        id=44,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-44: Questa è una domanda di esempio per il livello A1 numero 44.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 44"),
            QuestionOption(key="b", text="Risposta B esempio 44"),
            QuestionOption(key="c", text="Risposta C esempio 44"),
            QuestionOption(key="d", text="Risposta D esempio 44"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 44",
        grammar_point="Grammatica A1 esempio 44"
    ),

    Question(
        id=45,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-45: Questa è una domanda di esempio per il livello A1 numero 45.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 45"),
            QuestionOption(key="b", text="Risposta B esempio 45"),
            QuestionOption(key="c", text="Risposta C esempio 45"),
            QuestionOption(key="d", text="Risposta D esempio 45"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 45",
        grammar_point="Grammatica A1 esempio 45"
    ),

    Question(
        id=46,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-46: Questa è una domanda di esempio per il livello A1 numero 46.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 46"),
            QuestionOption(key="b", text="Risposta B esempio 46"),
            QuestionOption(key="c", text="Risposta C esempio 46"),
            QuestionOption(key="d", text="Risposta D esempio 46"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 46",
        grammar_point="Grammatica A1 esempio 46"
    ),

    Question(
        id=47,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-47: Questa è una domanda di esempio per il livello A1 numero 47.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 47"),
            QuestionOption(key="b", text="Risposta B esempio 47"),
            QuestionOption(key="c", text="Risposta C esempio 47"),
            QuestionOption(key="d", text="Risposta D esempio 47"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 47",
        grammar_point="Grammatica A1 esempio 47"
    ),

    Question(
        id=48,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-48: Questa è una domanda di esempio per il livello A1 numero 48.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 48"),
            QuestionOption(key="b", text="Risposta B esempio 48"),
            QuestionOption(key="c", text="Risposta C esempio 48"),
            QuestionOption(key="d", text="Risposta D esempio 48"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 48",
        grammar_point="Grammatica A1 esempio 48"
    ),

    Question(
        id=49,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-49: Questa è una domanda di esempio per il livello A1 numero 49.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 49"),
            QuestionOption(key="b", text="Risposta B esempio 49"),
            QuestionOption(key="c", text="Risposta C esempio 49"),
            QuestionOption(key="d", text="Risposta D esempio 49"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 49",
        grammar_point="Grammatica A1 esempio 49"
    ),

    Question(
        id=50,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-50: Questa è una domanda di esempio per il livello A1 numero 50.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 50"),
            QuestionOption(key="b", text="Risposta B esempio 50"),
            QuestionOption(key="c", text="Risposta C esempio 50"),
            QuestionOption(key="d", text="Risposta D esempio 50"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 50",
        grammar_point="Grammatica A1 esempio 50"
    ),

    Question(
        id=51,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-51: Questa è una domanda di esempio per il livello A1 numero 51.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 51"),
            QuestionOption(key="b", text="Risposta B esempio 51"),
            QuestionOption(key="c", text="Risposta C esempio 51"),
            QuestionOption(key="d", text="Risposta D esempio 51"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 51",
        grammar_point="Grammatica A1 esempio 51"
    ),

    Question(
        id=52,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-52: Questa è una domanda di esempio per il livello A1 numero 52.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 52"),
            QuestionOption(key="b", text="Risposta B esempio 52"),
            QuestionOption(key="c", text="Risposta C esempio 52"),
            QuestionOption(key="d", text="Risposta D esempio 52"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 52",
        grammar_point="Grammatica A1 esempio 52"
    ),

    Question(
        id=53,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-53: Questa è una domanda di esempio per il livello A1 numero 53.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 53"),
            QuestionOption(key="b", text="Risposta B esempio 53"),
            QuestionOption(key="c", text="Risposta C esempio 53"),
            QuestionOption(key="d", text="Risposta D esempio 53"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 53",
        grammar_point="Grammatica A1 esempio 53"
    ),

    Question(
        id=54,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-54: Questa è una domanda di esempio per il livello A1 numero 54.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 54"),
            QuestionOption(key="b", text="Risposta B esempio 54"),
            QuestionOption(key="c", text="Risposta C esempio 54"),
            QuestionOption(key="d", text="Risposta D esempio 54"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 54",
        grammar_point="Grammatica A1 esempio 54"
    ),

    Question(
        id=55,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-55: Questa è una domanda di esempio per il livello A1 numero 55.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 55"),
            QuestionOption(key="b", text="Risposta B esempio 55"),
            QuestionOption(key="c", text="Risposta C esempio 55"),
            QuestionOption(key="d", text="Risposta D esempio 55"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 55",
        grammar_point="Grammatica A1 esempio 55"
    ),

    Question(
        id=56,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-56: Questa è una domanda di esempio per il livello A1 numero 56.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 56"),
            QuestionOption(key="b", text="Risposta B esempio 56"),
            QuestionOption(key="c", text="Risposta C esempio 56"),
            QuestionOption(key="d", text="Risposta D esempio 56"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 56",
        grammar_point="Grammatica A1 esempio 56"
    ),

    Question(
        id=57,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-57: Questa è una domanda di esempio per il livello A1 numero 57.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 57"),
            QuestionOption(key="b", text="Risposta B esempio 57"),
            QuestionOption(key="c", text="Risposta C esempio 57"),
            QuestionOption(key="d", text="Risposta D esempio 57"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 57",
        grammar_point="Grammatica A1 esempio 57"
    ),

    Question(
        id=58,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-58: Questa è una domanda di esempio per il livello A1 numero 58.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 58"),
            QuestionOption(key="b", text="Risposta B esempio 58"),
            QuestionOption(key="c", text="Risposta C esempio 58"),
            QuestionOption(key="d", text="Risposta D esempio 58"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 58",
        grammar_point="Grammatica A1 esempio 58"
    ),

    Question(
        id=59,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-59: Questa è una domanda di esempio per il livello A1 numero 59.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 59"),
            QuestionOption(key="b", text="Risposta B esempio 59"),
            QuestionOption(key="c", text="Risposta C esempio 59"),
            QuestionOption(key="d", text="Risposta D esempio 59"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 59",
        grammar_point="Grammatica A1 esempio 59"
    ),

    Question(
        id=60,
        level=CEFRLevel.A1,
        section="A",
        question_text="Domanda A1-60: Questa è una domanda di esempio per il livello A1 numero 60.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 60"),
            QuestionOption(key="b", text="Risposta B esempio 60"),
            QuestionOption(key="c", text="Risposta C esempio 60"),
            QuestionOption(key="d", text="Risposta D esempio 60"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 60",
        grammar_point="Grammatica A1 esempio 60"
    ),

]
