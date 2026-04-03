"""
Question bank for the Italian Placement Test.

Organized by CEFR level with modular structure for easy maintenance and extension.
Uses Pydantic models for type safety and validation.
"""

import random

from italianollama.backend.placement_test.models import (
    CEFRLevel,
    Question,
    QuestionOption,
    TestSection,
    PlacementTestConfig,
)


# ==========================================================================
# SECTION A: A1 LEVEL (Questions 1-60)
# ==========================================================================

SECTION_A_QUESTIONS = [
    Question(
        id=1,
        level=CEFRLevel.A1,
        section="A",
        question_text="Al ristorante dobbiamo ______ un tavolo.",
        options=[
            QuestionOption(key="a", text="prenotare"),
            QuestionOption(key="b", text="cucinare"),
            QuestionOption(key="c", text="portare"),
            QuestionOption(key="d", text="ordinare"),
        ],
        correct_answer="a",
        correct_answer_text="prenotare",
        grammar_point="Infinitive collocations: prenotare un tavolo"
    ),
    Question(
        id=2,
        level=CEFRLevel.A1,
        section="A",
        question_text="Lei ______ Anna e abita ______ Roma.",
        options=[
            QuestionOption(key="a", text="è / a"),
            QuestionOption(key="b", text="ha / in"),
            QuestionOption(key="c", text="sei / da"),
            QuestionOption(key="d", text="sono / per"),
        ],
        correct_answer="a",
        correct_answer_text="è / a",
        grammar_point="Essere + preposition a (city)"
    ),
    Question(
        id=3,
        level=CEFRLevel.A1,
        section="A",
        question_text="«Di dove sei? Sei di Firenze?» — «No, non ______ di Firenze, sono di Milano.»",
        options=[
            QuestionOption(key="a", text="sei"),
            QuestionOption(key="b", text="sono"),
            QuestionOption(key="c", text="siamo"),
            QuestionOption(key="d", text="è"),
        ],
        correct_answer="b",
        correct_answer_text="sono",
        grammar_point="Essere io: non sono"
    ),
    Question(
        id=4,
        level=CEFRLevel.A1,
        section="A",
        question_text="______ zaino è sul banco.",
        options=[
            QuestionOption(key="a", text="Il"),
            QuestionOption(key="b", text="Lo"),
            QuestionOption(key="c", text="La"),
            QuestionOption(key="d", text="Un"),
        ],
        correct_answer="b",
        correct_answer_text="Lo",
        grammar_point="Lo before s + consonant (zaino)"
    ),
    Question(
        id=5,
        level=CEFRLevel.A1,
        section="A",
        question_text="Ogni mattina io ______ un caffè prima di uscire.",
        options=[
            QuestionOption(key="a", text="beve"),
            QuestionOption(key="b", text="bevono"),
            QuestionOption(key="c", text="bevo"),
            QuestionOption(key="d", text="beviamo"),
        ],
        correct_answer="c",
        correct_answer_text="bevo",
        grammar_point="Bere: io bevo"
    ),
    Question(
        id=6,
        level=CEFRLevel.A1,
        section="A",
        question_text="«Quanti anni hai?» — «______ ventidue anni.»",
        options=[
            QuestionOption(key="a", text="Sono"),
            QuestionOption(key="b", text="Ho"),
            QuestionOption(key="c", text="Faccio"),
            QuestionOption(key="d", text="Sto"),
        ],
        correct_answer="b",
        correct_answer_text="Ho",
        grammar_point="Avere for age: ho … anni"
    ),
    Question(
        id=7,
        level=CEFRLevel.A1,
        section="A",
        question_text="Il contrario di «grande» è:",
        options=[
            QuestionOption(key="a", text="lungo"),
            QuestionOption(key="b", text="bello"),
            QuestionOption(key="c", text="piccolo"),
            QuestionOption(key="d", text="caro"),
        ],
        correct_answer="c",
        correct_answer_text="piccolo",
        grammar_point="Antonyms: grande ↔ piccolo"
    ),
    Question(
        id=8,
        level=CEFRLevel.A1,
        section="A",
        question_text="Noi ______ in un appartamento al secondo piano.",
        options=[
            QuestionOption(key="a", text="vivo"),
            QuestionOption(key="b", text="vivete"),
            QuestionOption(key="c", text="vivono"),
            QuestionOption(key="d", text="viviamo"),
        ],
        correct_answer="d",
        correct_answer_text="viviamo",
        grammar_point="Vivere: noi viviamo"
    ),
    Question(
        id=9,
        level=CEFRLevel.A1,
        section="A",
        question_text="«Come stai?» — «______, grazie!»",
        options=[
            QuestionOption(key="a", text="Buongiorno"),
            QuestionOption(key="b", text="Prego"),
            QuestionOption(key="c", text="Bene"),
            QuestionOption(key="d", text="Certo"),
        ],
        correct_answer="c",
        correct_answer_text="Bene",
        grammar_point="Responding to come stai"
    ),
    Question(
        id=10,
        level=CEFRLevel.A1,
        section="A",
        question_text="Il plurale di «lo studente» è:",
        options=[
            QuestionOption(key="a", text="i studenti"),
            QuestionOption(key="b", text="li studenti"),
            QuestionOption(key="c", text="gli studenti"),
            QuestionOption(key="d", text="le studenti"),
        ],
        correct_answer="c",
        correct_answer_text="gli studenti",
        grammar_point="Plural: lo → gli (s + consonant)"
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


# ==========================================================================
# SECTION B: A2 LEVEL (Questions 61-120)
# ==========================================================================

SECTION_B_QUESTIONS = [
    Question(
        id=61,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-61: Questa è una domanda di esempio per il livello A2 numero 61.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 61"),
            QuestionOption(key="b", text="Risposta B esempio 61"),
            QuestionOption(key="c", text="Risposta C esempio 61"),
            QuestionOption(key="d", text="Risposta D esempio 61"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 61",
        grammar_point="Grammatica A2 esempio 61"
    ),
    Question(
        id=62,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-62: Questa è una domanda di esempio per il livello A2 numero 62.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 62"),
            QuestionOption(key="b", text="Risposta B esempio 62"),
            QuestionOption(key="c", text="Risposta C esempio 62"),
            QuestionOption(key="d", text="Risposta D esempio 62"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 62",
        grammar_point="Grammatica A2 esempio 62"
    ),
    Question(
        id=63,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-63: Questa è una domanda di esempio per il livello A2 numero 63.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 63"),
            QuestionOption(key="b", text="Risposta B esempio 63"),
            QuestionOption(key="c", text="Risposta C esempio 63"),
            QuestionOption(key="d", text="Risposta D esempio 63"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 63",
        grammar_point="Grammatica A2 esempio 63"
    ),
    Question(
        id=64,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-64: Questa è una domanda di esempio per il livello A2 numero 64.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 64"),
            QuestionOption(key="b", text="Risposta B esempio 64"),
            QuestionOption(key="c", text="Risposta C esempio 64"),
            QuestionOption(key="d", text="Risposta D esempio 64"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 64",
        grammar_point="Grammatica A2 esempio 64"
    ),
    Question(
        id=65,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-65: Questa è una domanda di esempio per il livello A2 numero 65.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 65"),
            QuestionOption(key="b", text="Risposta B esempio 65"),
            QuestionOption(key="c", text="Risposta C esempio 65"),
            QuestionOption(key="d", text="Risposta D esempio 65"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 65",
        grammar_point="Grammatica A2 esempio 65"
    ),
    Question(
        id=66,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-66: Questa è una domanda di esempio per il livello A2 numero 66.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 66"),
            QuestionOption(key="b", text="Risposta B esempio 66"),
            QuestionOption(key="c", text="Risposta C esempio 66"),
            QuestionOption(key="d", text="Risposta D esempio 66"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 66",
        grammar_point="Grammatica A2 esempio 66"
    ),
    Question(
        id=67,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-67: Questa è una domanda di esempio per il livello A2 numero 67.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 67"),
            QuestionOption(key="b", text="Risposta B esempio 67"),
            QuestionOption(key="c", text="Risposta C esempio 67"),
            QuestionOption(key="d", text="Risposta D esempio 67"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 67",
        grammar_point="Grammatica A2 esempio 67"
    ),
    Question(
        id=68,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-68: Questa è una domanda di esempio per il livello A2 numero 68.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 68"),
            QuestionOption(key="b", text="Risposta B esempio 68"),
            QuestionOption(key="c", text="Risposta C esempio 68"),
            QuestionOption(key="d", text="Risposta D esempio 68"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 68",
        grammar_point="Grammatica A2 esempio 68"
    ),
    Question(
        id=69,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-69: Questa è una domanda di esempio per il livello A2 numero 69.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 69"),
            QuestionOption(key="b", text="Risposta B esempio 69"),
            QuestionOption(key="c", text="Risposta C esempio 69"),
            QuestionOption(key="d", text="Risposta D esempio 69"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 69",
        grammar_point="Grammatica A2 esempio 69"
    ),
    Question(
        id=70,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-70: Questa è una domanda di esempio per il livello A2 numero 70.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 70"),
            QuestionOption(key="b", text="Risposta B esempio 70"),
            QuestionOption(key="c", text="Risposta C esempio 70"),
            QuestionOption(key="d", text="Risposta D esempio 70"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 70",
        grammar_point="Grammatica A2 esempio 70"
    ),
    Question(
        id=71,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-71: Questa è una domanda di esempio per il livello A2 numero 71.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 71"),
            QuestionOption(key="b", text="Risposta B esempio 71"),
            QuestionOption(key="c", text="Risposta C esempio 71"),
            QuestionOption(key="d", text="Risposta D esempio 71"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 71",
        grammar_point="Grammatica A2 esempio 71"
    ),
    Question(
        id=72,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-72: Questa è una domanda di esempio per il livello A2 numero 72.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 72"),
            QuestionOption(key="b", text="Risposta B esempio 72"),
            QuestionOption(key="c", text="Risposta C esempio 72"),
            QuestionOption(key="d", text="Risposta D esempio 72"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 72",
        grammar_point="Grammatica A2 esempio 72"
    ),
    Question(
        id=73,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-73: Questa è una domanda di esempio per il livello A2 numero 73.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 73"),
            QuestionOption(key="b", text="Risposta B esempio 73"),
            QuestionOption(key="c", text="Risposta C esempio 73"),
            QuestionOption(key="d", text="Risposta D esempio 73"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 73",
        grammar_point="Grammatica A2 esempio 73"
    ),
    Question(
        id=74,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-74: Questa è una domanda di esempio per il livello A2 numero 74.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 74"),
            QuestionOption(key="b", text="Risposta B esempio 74"),
            QuestionOption(key="c", text="Risposta C esempio 74"),
            QuestionOption(key="d", text="Risposta D esempio 74"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 74",
        grammar_point="Grammatica A2 esempio 74"
    ),
    Question(
        id=75,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-75: Questa è una domanda di esempio per il livello A2 numero 75.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 75"),
            QuestionOption(key="b", text="Risposta B esempio 75"),
            QuestionOption(key="c", text="Risposta C esempio 75"),
            QuestionOption(key="d", text="Risposta D esempio 75"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 75",
        grammar_point="Grammatica A2 esempio 75"
    ),
    Question(
        id=76,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-76: Questa è una domanda di esempio per il livello A2 numero 76.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 76"),
            QuestionOption(key="b", text="Risposta B esempio 76"),
            QuestionOption(key="c", text="Risposta C esempio 76"),
            QuestionOption(key="d", text="Risposta D esempio 76"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 76",
        grammar_point="Grammatica A2 esempio 76"
    ),
    Question(
        id=77,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-77: Questa è una domanda di esempio per il livello A2 numero 77.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 77"),
            QuestionOption(key="b", text="Risposta B esempio 77"),
            QuestionOption(key="c", text="Risposta C esempio 77"),
            QuestionOption(key="d", text="Risposta D esempio 77"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 77",
        grammar_point="Grammatica A2 esempio 77"
    ),
    Question(
        id=78,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-78: Questa è una domanda di esempio per il livello A2 numero 78.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 78"),
            QuestionOption(key="b", text="Risposta B esempio 78"),
            QuestionOption(key="c", text="Risposta C esempio 78"),
            QuestionOption(key="d", text="Risposta D esempio 78"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 78",
        grammar_point="Grammatica A2 esempio 78"
    ),
    Question(
        id=79,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-79: Questa è una domanda di esempio per il livello A2 numero 79.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 79"),
            QuestionOption(key="b", text="Risposta B esempio 79"),
            QuestionOption(key="c", text="Risposta C esempio 79"),
            QuestionOption(key="d", text="Risposta D esempio 79"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 79",
        grammar_point="Grammatica A2 esempio 79"
    ),
    Question(
        id=80,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-80: Questa è una domanda di esempio per il livello A2 numero 80.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 80"),
            QuestionOption(key="b", text="Risposta B esempio 80"),
            QuestionOption(key="c", text="Risposta C esempio 80"),
            QuestionOption(key="d", text="Risposta D esempio 80"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 80",
        grammar_point="Grammatica A2 esempio 80"
    ),
    Question(
        id=81,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-81: Questa è una domanda di esempio per il livello A2 numero 81.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 81"),
            QuestionOption(key="b", text="Risposta B esempio 81"),
            QuestionOption(key="c", text="Risposta C esempio 81"),
            QuestionOption(key="d", text="Risposta D esempio 81"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 81",
        grammar_point="Grammatica A2 esempio 81"
    ),
    Question(
        id=82,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-82: Questa è una domanda di esempio per il livello A2 numero 82.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 82"),
            QuestionOption(key="b", text="Risposta B esempio 82"),
            QuestionOption(key="c", text="Risposta C esempio 82"),
            QuestionOption(key="d", text="Risposta D esempio 82"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 82",
        grammar_point="Grammatica A2 esempio 82"
    ),
    Question(
        id=83,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-83: Questa è una domanda di esempio per il livello A2 numero 83.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 83"),
            QuestionOption(key="b", text="Risposta B esempio 83"),
            QuestionOption(key="c", text="Risposta C esempio 83"),
            QuestionOption(key="d", text="Risposta D esempio 83"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 83",
        grammar_point="Grammatica A2 esempio 83"
    ),
    Question(
        id=84,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-84: Questa è una domanda di esempio per il livello A2 numero 84.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 84"),
            QuestionOption(key="b", text="Risposta B esempio 84"),
            QuestionOption(key="c", text="Risposta C esempio 84"),
            QuestionOption(key="d", text="Risposta D esempio 84"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 84",
        grammar_point="Grammatica A2 esempio 84"
    ),
    Question(
        id=85,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-85: Questa è una domanda di esempio per il livello A2 numero 85.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 85"),
            QuestionOption(key="b", text="Risposta B esempio 85"),
            QuestionOption(key="c", text="Risposta C esempio 85"),
            QuestionOption(key="d", text="Risposta D esempio 85"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 85",
        grammar_point="Grammatica A2 esempio 85"
    ),
    Question(
        id=86,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-86: Questa è una domanda di esempio per il livello A2 numero 86.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 86"),
            QuestionOption(key="b", text="Risposta B esempio 86"),
            QuestionOption(key="c", text="Risposta C esempio 86"),
            QuestionOption(key="d", text="Risposta D esempio 86"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 86",
        grammar_point="Grammatica A2 esempio 86"
    ),
    Question(
        id=87,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-87: Questa è una domanda di esempio per il livello A2 numero 87.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 87"),
            QuestionOption(key="b", text="Risposta B esempio 87"),
            QuestionOption(key="c", text="Risposta C esempio 87"),
            QuestionOption(key="d", text="Risposta D esempio 87"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 87",
        grammar_point="Grammatica A2 esempio 87"
    ),
    Question(
        id=88,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-88: Questa è una domanda di esempio per il livello A2 numero 88.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 88"),
            QuestionOption(key="b", text="Risposta B esempio 88"),
            QuestionOption(key="c", text="Risposta C esempio 88"),
            QuestionOption(key="d", text="Risposta D esempio 88"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 88",
        grammar_point="Grammatica A2 esempio 88"
    ),
    Question(
        id=89,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-89: Questa è una domanda di esempio per il livello A2 numero 89.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 89"),
            QuestionOption(key="b", text="Risposta B esempio 89"),
            QuestionOption(key="c", text="Risposta C esempio 89"),
            QuestionOption(key="d", text="Risposta D esempio 89"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 89",
        grammar_point="Grammatica A2 esempio 89"
    ),
    Question(
        id=90,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-90: Questa è una domanda di esempio per il livello A2 numero 90.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 90"),
            QuestionOption(key="b", text="Risposta B esempio 90"),
            QuestionOption(key="c", text="Risposta C esempio 90"),
            QuestionOption(key="d", text="Risposta D esempio 90"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 90",
        grammar_point="Grammatica A2 esempio 90"
    ),
    Question(
        id=91,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-91: Questa è una domanda di esempio per il livello A2 numero 91.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 91"),
            QuestionOption(key="b", text="Risposta B esempio 91"),
            QuestionOption(key="c", text="Risposta C esempio 91"),
            QuestionOption(key="d", text="Risposta D esempio 91"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 91",
        grammar_point="Grammatica A2 esempio 91"
    ),
    Question(
        id=92,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-92: Questa è una domanda di esempio per il livello A2 numero 92.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 92"),
            QuestionOption(key="b", text="Risposta B esempio 92"),
            QuestionOption(key="c", text="Risposta C esempio 92"),
            QuestionOption(key="d", text="Risposta D esempio 92"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 92",
        grammar_point="Grammatica A2 esempio 92"
    ),
    Question(
        id=93,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-93: Questa è una domanda di esempio per il livello A2 numero 93.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 93"),
            QuestionOption(key="b", text="Risposta B esempio 93"),
            QuestionOption(key="c", text="Risposta C esempio 93"),
            QuestionOption(key="d", text="Risposta D esempio 93"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 93",
        grammar_point="Grammatica A2 esempio 93"
    ),
    Question(
        id=94,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-94: Questa è una domanda di esempio per il livello A2 numero 94.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 94"),
            QuestionOption(key="b", text="Risposta B esempio 94"),
            QuestionOption(key="c", text="Risposta C esempio 94"),
            QuestionOption(key="d", text="Risposta D esempio 94"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 94",
        grammar_point="Grammatica A2 esempio 94"
    ),
    Question(
        id=95,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-95: Questa è una domanda di esempio per il livello A2 numero 95.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 95"),
            QuestionOption(key="b", text="Risposta B esempio 95"),
            QuestionOption(key="c", text="Risposta C esempio 95"),
            QuestionOption(key="d", text="Risposta D esempio 95"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 95",
        grammar_point="Grammatica A2 esempio 95"
    ),
    Question(
        id=96,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-96: Questa è una domanda di esempio per il livello A2 numero 96.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 96"),
            QuestionOption(key="b", text="Risposta B esempio 96"),
            QuestionOption(key="c", text="Risposta C esempio 96"),
            QuestionOption(key="d", text="Risposta D esempio 96"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 96",
        grammar_point="Grammatica A2 esempio 96"
    ),
    Question(
        id=97,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-97: Questa è una domanda di esempio per il livello A2 numero 97.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 97"),
            QuestionOption(key="b", text="Risposta B esempio 97"),
            QuestionOption(key="c", text="Risposta C esempio 97"),
            QuestionOption(key="d", text="Risposta D esempio 97"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 97",
        grammar_point="Grammatica A2 esempio 97"
    ),
    Question(
        id=98,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-98: Questa è una domanda di esempio per il livello A2 numero 98.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 98"),
            QuestionOption(key="b", text="Risposta B esempio 98"),
            QuestionOption(key="c", text="Risposta C esempio 98"),
            QuestionOption(key="d", text="Risposta D esempio 98"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 98",
        grammar_point="Grammatica A2 esempio 98"
    ),
    Question(
        id=99,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-99: Questa è una domanda di esempio per il livello A2 numero 99.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 99"),
            QuestionOption(key="b", text="Risposta B esempio 99"),
            QuestionOption(key="c", text="Risposta C esempio 99"),
            QuestionOption(key="d", text="Risposta D esempio 99"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 99",
        grammar_point="Grammatica A2 esempio 99"
    ),
    Question(
        id=100,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-100: Questa è una domanda di esempio per il livello A2 numero 100.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 100"),
            QuestionOption(key="b", text="Risposta B esempio 100"),
            QuestionOption(key="c", text="Risposta C esempio 100"),
            QuestionOption(key="d", text="Risposta D esempio 100"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 100",
        grammar_point="Grammatica A2 esempio 100"
    ),
    Question(
        id=101,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-101: Questa è una domanda di esempio per il livello A2 numero 101.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 101"),
            QuestionOption(key="b", text="Risposta B esempio 101"),
            QuestionOption(key="c", text="Risposta C esempio 101"),
            QuestionOption(key="d", text="Risposta D esempio 101"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 101",
        grammar_point="Grammatica A2 esempio 101"
    ),
    Question(
        id=102,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-102: Questa è una domanda di esempio per il livello A2 numero 102.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 102"),
            QuestionOption(key="b", text="Risposta B esempio 102"),
            QuestionOption(key="c", text="Risposta C esempio 102"),
            QuestionOption(key="d", text="Risposta D esempio 102"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 102",
        grammar_point="Grammatica A2 esempio 102"
    ),
    Question(
        id=103,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-103: Questa è una domanda di esempio per il livello A2 numero 103.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 103"),
            QuestionOption(key="b", text="Risposta B esempio 103"),
            QuestionOption(key="c", text="Risposta C esempio 103"),
            QuestionOption(key="d", text="Risposta D esempio 103"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 103",
        grammar_point="Grammatica A2 esempio 103"
    ),
    Question(
        id=104,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-104: Questa è una domanda di esempio per il livello A2 numero 104.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 104"),
            QuestionOption(key="b", text="Risposta B esempio 104"),
            QuestionOption(key="c", text="Risposta C esempio 104"),
            QuestionOption(key="d", text="Risposta D esempio 104"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 104",
        grammar_point="Grammatica A2 esempio 104"
    ),
    Question(
        id=105,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-105: Questa è una domanda di esempio per il livello A2 numero 105.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 105"),
            QuestionOption(key="b", text="Risposta B esempio 105"),
            QuestionOption(key="c", text="Risposta C esempio 105"),
            QuestionOption(key="d", text="Risposta D esempio 105"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 105",
        grammar_point="Grammatica A2 esempio 105"
    ),
    Question(
        id=106,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-106: Questa è una domanda di esempio per il livello A2 numero 106.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 106"),
            QuestionOption(key="b", text="Risposta B esempio 106"),
            QuestionOption(key="c", text="Risposta C esempio 106"),
            QuestionOption(key="d", text="Risposta D esempio 106"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 106",
        grammar_point="Grammatica A2 esempio 106"
    ),
    Question(
        id=107,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-107: Questa è una domanda di esempio per il livello A2 numero 107.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 107"),
            QuestionOption(key="b", text="Risposta B esempio 107"),
            QuestionOption(key="c", text="Risposta C esempio 107"),
            QuestionOption(key="d", text="Risposta D esempio 107"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 107",
        grammar_point="Grammatica A2 esempio 107"
    ),
    Question(
        id=108,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-108: Questa è una domanda di esempio per il livello A2 numero 108.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 108"),
            QuestionOption(key="b", text="Risposta B esempio 108"),
            QuestionOption(key="c", text="Risposta C esempio 108"),
            QuestionOption(key="d", text="Risposta D esempio 108"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 108",
        grammar_point="Grammatica A2 esempio 108"
    ),
    Question(
        id=109,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-109: Questa è una domanda di esempio per il livello A2 numero 109.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 109"),
            QuestionOption(key="b", text="Risposta B esempio 109"),
            QuestionOption(key="c", text="Risposta C esempio 109"),
            QuestionOption(key="d", text="Risposta D esempio 109"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 109",
        grammar_point="Grammatica A2 esempio 109"
    ),
    Question(
        id=110,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-110: Questa è una domanda di esempio per il livello A2 numero 110.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 110"),
            QuestionOption(key="b", text="Risposta B esempio 110"),
            QuestionOption(key="c", text="Risposta C esempio 110"),
            QuestionOption(key="d", text="Risposta D esempio 110"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 110",
        grammar_point="Grammatica A2 esempio 110"
    ),
    Question(
        id=111,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-111: Questa è una domanda di esempio per il livello A2 numero 111.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 111"),
            QuestionOption(key="b", text="Risposta B esempio 111"),
            QuestionOption(key="c", text="Risposta C esempio 111"),
            QuestionOption(key="d", text="Risposta D esempio 111"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 111",
        grammar_point="Grammatica A2 esempio 111"
    ),
    Question(
        id=112,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-112: Questa è una domanda di esempio per il livello A2 numero 112.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 112"),
            QuestionOption(key="b", text="Risposta B esempio 112"),
            QuestionOption(key="c", text="Risposta C esempio 112"),
            QuestionOption(key="d", text="Risposta D esempio 112"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 112",
        grammar_point="Grammatica A2 esempio 112"
    ),
    Question(
        id=113,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-113: Questa è una domanda di esempio per il livello A2 numero 113.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 113"),
            QuestionOption(key="b", text="Risposta B esempio 113"),
            QuestionOption(key="c", text="Risposta C esempio 113"),
            QuestionOption(key="d", text="Risposta D esempio 113"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 113",
        grammar_point="Grammatica A2 esempio 113"
    ),
    Question(
        id=114,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-114: Questa è una domanda di esempio per il livello A2 numero 114.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 114"),
            QuestionOption(key="b", text="Risposta B esempio 114"),
            QuestionOption(key="c", text="Risposta C esempio 114"),
            QuestionOption(key="d", text="Risposta D esempio 114"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 114",
        grammar_point="Grammatica A2 esempio 114"
    ),
    Question(
        id=115,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-115: Questa è una domanda di esempio per il livello A2 numero 115.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 115"),
            QuestionOption(key="b", text="Risposta B esempio 115"),
            QuestionOption(key="c", text="Risposta C esempio 115"),
            QuestionOption(key="d", text="Risposta D esempio 115"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 115",
        grammar_point="Grammatica A2 esempio 115"
    ),
    Question(
        id=116,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-116: Questa è una domanda di esempio per il livello A2 numero 116.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 116"),
            QuestionOption(key="b", text="Risposta B esempio 116"),
            QuestionOption(key="c", text="Risposta C esempio 116"),
            QuestionOption(key="d", text="Risposta D esempio 116"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 116",
        grammar_point="Grammatica A2 esempio 116"
    ),
    Question(
        id=117,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-117: Questa è una domanda di esempio per il livello A2 numero 117.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 117"),
            QuestionOption(key="b", text="Risposta B esempio 117"),
            QuestionOption(key="c", text="Risposta C esempio 117"),
            QuestionOption(key="d", text="Risposta D esempio 117"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 117",
        grammar_point="Grammatica A2 esempio 117"
    ),
    Question(
        id=118,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-118: Questa è una domanda di esempio per il livello A2 numero 118.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 118"),
            QuestionOption(key="b", text="Risposta B esempio 118"),
            QuestionOption(key="c", text="Risposta C esempio 118"),
            QuestionOption(key="d", text="Risposta D esempio 118"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 118",
        grammar_point="Grammatica A2 esempio 118"
    ),
    Question(
        id=119,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-119: Questa è una domanda di esempio per il livello A2 numero 119.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 119"),
            QuestionOption(key="b", text="Risposta B esempio 119"),
            QuestionOption(key="c", text="Risposta C esempio 119"),
            QuestionOption(key="d", text="Risposta D esempio 119"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 119",
        grammar_point="Grammatica A2 esempio 119"
    ),
    Question(
        id=120,
        level=CEFRLevel.A2,
        section="B",
        question_text="Domanda A2-120: Questa è una domanda di esempio per il livello A2 numero 120.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 120"),
            QuestionOption(key="b", text="Risposta B esempio 120"),
            QuestionOption(key="c", text="Risposta C esempio 120"),
            QuestionOption(key="d", text="Risposta D esempio 120"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 120",
        grammar_point="Grammatica A2 esempio 120"
    ),
]


# ==========================================================================
# SECTION C: B1 LEVEL (Questions 121-180)
# ==========================================================================

SECTION_C_QUESTIONS = [
    Question(
        id=121,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-121: Questa è una domanda di esempio per il livello B1 numero 121.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 121"),
            QuestionOption(key="b", text="Risposta B esempio 121"),
            QuestionOption(key="c", text="Risposta C esempio 121"),
            QuestionOption(key="d", text="Risposta D esempio 121"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 121",
        grammar_point="Grammatica B1 esempio 121"
    ),
    Question(
        id=122,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-122: Questa è una domanda di esempio per il livello B1 numero 122.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 122"),
            QuestionOption(key="b", text="Risposta B esempio 122"),
            QuestionOption(key="c", text="Risposta C esempio 122"),
            QuestionOption(key="d", text="Risposta D esempio 122"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 122",
        grammar_point="Grammatica B1 esempio 122"
    ),
    Question(
        id=123,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-123: Questa è una domanda di esempio per il livello B1 numero 123.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 123"),
            QuestionOption(key="b", text="Risposta B esempio 123"),
            QuestionOption(key="c", text="Risposta C esempio 123"),
            QuestionOption(key="d", text="Risposta D esempio 123"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 123",
        grammar_point="Grammatica B1 esempio 123"
    ),
    Question(
        id=124,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-124: Questa è una domanda di esempio per il livello B1 numero 124.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 124"),
            QuestionOption(key="b", text="Risposta B esempio 124"),
            QuestionOption(key="c", text="Risposta C esempio 124"),
            QuestionOption(key="d", text="Risposta D esempio 124"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 124",
        grammar_point="Grammatica B1 esempio 124"
    ),
    Question(
        id=125,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-125: Questa è una domanda di esempio per il livello B1 numero 125.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 125"),
            QuestionOption(key="b", text="Risposta B esempio 125"),
            QuestionOption(key="c", text="Risposta C esempio 125"),
            QuestionOption(key="d", text="Risposta D esempio 125"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 125",
        grammar_point="Grammatica B1 esempio 125"
    ),
    Question(
        id=126,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-126: Questa è una domanda di esempio per il livello B1 numero 126.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 126"),
            QuestionOption(key="b", text="Risposta B esempio 126"),
            QuestionOption(key="c", text="Risposta C esempio 126"),
            QuestionOption(key="d", text="Risposta D esempio 126"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 126",
        grammar_point="Grammatica B1 esempio 126"
    ),
    Question(
        id=127,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-127: Questa è una domanda di esempio per il livello B1 numero 127.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 127"),
            QuestionOption(key="b", text="Risposta B esempio 127"),
            QuestionOption(key="c", text="Risposta C esempio 127"),
            QuestionOption(key="d", text="Risposta D esempio 127"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 127",
        grammar_point="Grammatica B1 esempio 127"
    ),
    Question(
        id=128,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-128: Questa è una domanda di esempio per il livello B1 numero 128.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 128"),
            QuestionOption(key="b", text="Risposta B esempio 128"),
            QuestionOption(key="c", text="Risposta C esempio 128"),
            QuestionOption(key="d", text="Risposta D esempio 128"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 128",
        grammar_point="Grammatica B1 esempio 128"
    ),
    Question(
        id=129,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-129: Questa è una domanda di esempio per il livello B1 numero 129.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 129"),
            QuestionOption(key="b", text="Risposta B esempio 129"),
            QuestionOption(key="c", text="Risposta C esempio 129"),
            QuestionOption(key="d", text="Risposta D esempio 129"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 129",
        grammar_point="Grammatica B1 esempio 129"
    ),
    Question(
        id=130,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-130: Questa è una domanda di esempio per il livello B1 numero 130.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 130"),
            QuestionOption(key="b", text="Risposta B esempio 130"),
            QuestionOption(key="c", text="Risposta C esempio 130"),
            QuestionOption(key="d", text="Risposta D esempio 130"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 130",
        grammar_point="Grammatica B1 esempio 130"
    ),
    Question(
        id=131,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-131: Questa è una domanda di esempio per il livello B1 numero 131.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 131"),
            QuestionOption(key="b", text="Risposta B esempio 131"),
            QuestionOption(key="c", text="Risposta C esempio 131"),
            QuestionOption(key="d", text="Risposta D esempio 131"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 131",
        grammar_point="Grammatica B1 esempio 131"
    ),
    Question(
        id=132,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-132: Questa è una domanda di esempio per il livello B1 numero 132.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 132"),
            QuestionOption(key="b", text="Risposta B esempio 132"),
            QuestionOption(key="c", text="Risposta C esempio 132"),
            QuestionOption(key="d", text="Risposta D esempio 132"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 132",
        grammar_point="Grammatica B1 esempio 132"
    ),
    Question(
        id=133,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-133: Questa è una domanda di esempio per il livello B1 numero 133.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 133"),
            QuestionOption(key="b", text="Risposta B esempio 133"),
            QuestionOption(key="c", text="Risposta C esempio 133"),
            QuestionOption(key="d", text="Risposta D esempio 133"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 133",
        grammar_point="Grammatica B1 esempio 133"
    ),
    Question(
        id=134,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-134: Questa è una domanda di esempio per il livello B1 numero 134.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 134"),
            QuestionOption(key="b", text="Risposta B esempio 134"),
            QuestionOption(key="c", text="Risposta C esempio 134"),
            QuestionOption(key="d", text="Risposta D esempio 134"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 134",
        grammar_point="Grammatica B1 esempio 134"
    ),
    Question(
        id=135,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-135: Questa è una domanda di esempio per il livello B1 numero 135.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 135"),
            QuestionOption(key="b", text="Risposta B esempio 135"),
            QuestionOption(key="c", text="Risposta C esempio 135"),
            QuestionOption(key="d", text="Risposta D esempio 135"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 135",
        grammar_point="Grammatica B1 esempio 135"
    ),
    Question(
        id=136,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-136: Questa è una domanda di esempio per il livello B1 numero 136.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 136"),
            QuestionOption(key="b", text="Risposta B esempio 136"),
            QuestionOption(key="c", text="Risposta C esempio 136"),
            QuestionOption(key="d", text="Risposta D esempio 136"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 136",
        grammar_point="Grammatica B1 esempio 136"
    ),
    Question(
        id=137,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-137: Questa è una domanda di esempio per il livello B1 numero 137.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 137"),
            QuestionOption(key="b", text="Risposta B esempio 137"),
            QuestionOption(key="c", text="Risposta C esempio 137"),
            QuestionOption(key="d", text="Risposta D esempio 137"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 137",
        grammar_point="Grammatica B1 esempio 137"
    ),
    Question(
        id=138,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-138: Questa è una domanda di esempio per il livello B1 numero 138.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 138"),
            QuestionOption(key="b", text="Risposta B esempio 138"),
            QuestionOption(key="c", text="Risposta C esempio 138"),
            QuestionOption(key="d", text="Risposta D esempio 138"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 138",
        grammar_point="Grammatica B1 esempio 138"
    ),
    Question(
        id=139,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-139: Questa è una domanda di esempio per il livello B1 numero 139.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 139"),
            QuestionOption(key="b", text="Risposta B esempio 139"),
            QuestionOption(key="c", text="Risposta C esempio 139"),
            QuestionOption(key="d", text="Risposta D esempio 139"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 139",
        grammar_point="Grammatica B1 esempio 139"
    ),
    Question(
        id=140,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-140: Questa è una domanda di esempio per il livello B1 numero 140.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 140"),
            QuestionOption(key="b", text="Risposta B esempio 140"),
            QuestionOption(key="c", text="Risposta C esempio 140"),
            QuestionOption(key="d", text="Risposta D esempio 140"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 140",
        grammar_point="Grammatica B1 esempio 140"
    ),
    Question(
        id=141,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-141: Questa è una domanda di esempio per il livello B1 numero 141.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 141"),
            QuestionOption(key="b", text="Risposta B esempio 141"),
            QuestionOption(key="c", text="Risposta C esempio 141"),
            QuestionOption(key="d", text="Risposta D esempio 141"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 141",
        grammar_point="Grammatica B1 esempio 141"
    ),
    Question(
        id=142,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-142: Questa è una domanda di esempio per il livello B1 numero 142.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 142"),
            QuestionOption(key="b", text="Risposta B esempio 142"),
            QuestionOption(key="c", text="Risposta C esempio 142"),
            QuestionOption(key="d", text="Risposta D esempio 142"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 142",
        grammar_point="Grammatica B1 esempio 142"
    ),
    Question(
        id=143,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-143: Questa è una domanda di esempio per il livello B1 numero 143.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 143"),
            QuestionOption(key="b", text="Risposta B esempio 143"),
            QuestionOption(key="c", text="Risposta C esempio 143"),
            QuestionOption(key="d", text="Risposta D esempio 143"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 143",
        grammar_point="Grammatica B1 esempio 143"
    ),
    Question(
        id=144,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-144: Questa è una domanda di esempio per il livello B1 numero 144.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 144"),
            QuestionOption(key="b", text="Risposta B esempio 144"),
            QuestionOption(key="c", text="Risposta C esempio 144"),
            QuestionOption(key="d", text="Risposta D esempio 144"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 144",
        grammar_point="Grammatica B1 esempio 144"
    ),
    Question(
        id=145,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-145: Questa è una domanda di esempio per il livello B1 numero 145.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 145"),
            QuestionOption(key="b", text="Risposta B esempio 145"),
            QuestionOption(key="c", text="Risposta C esempio 145"),
            QuestionOption(key="d", text="Risposta D esempio 145"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 145",
        grammar_point="Grammatica B1 esempio 145"
    ),
    Question(
        id=146,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-146: Questa è una domanda di esempio per il livello B1 numero 146.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 146"),
            QuestionOption(key="b", text="Risposta B esempio 146"),
            QuestionOption(key="c", text="Risposta C esempio 146"),
            QuestionOption(key="d", text="Risposta D esempio 146"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 146",
        grammar_point="Grammatica B1 esempio 146"
    ),
    Question(
        id=147,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-147: Questa è una domanda di esempio per il livello B1 numero 147.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 147"),
            QuestionOption(key="b", text="Risposta B esempio 147"),
            QuestionOption(key="c", text="Risposta C esempio 147"),
            QuestionOption(key="d", text="Risposta D esempio 147"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 147",
        grammar_point="Grammatica B1 esempio 147"
    ),
    Question(
        id=148,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-148: Questa è una domanda di esempio per il livello B1 numero 148.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 148"),
            QuestionOption(key="b", text="Risposta B esempio 148"),
            QuestionOption(key="c", text="Risposta C esempio 148"),
            QuestionOption(key="d", text="Risposta D esempio 148"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 148",
        grammar_point="Grammatica B1 esempio 148"
    ),
    Question(
        id=149,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-149: Questa è una domanda di esempio per il livello B1 numero 149.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 149"),
            QuestionOption(key="b", text="Risposta B esempio 149"),
            QuestionOption(key="c", text="Risposta C esempio 149"),
            QuestionOption(key="d", text="Risposta D esempio 149"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 149",
        grammar_point="Grammatica B1 esempio 149"
    ),
    Question(
        id=150,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-150: Questa è una domanda di esempio per il livello B1 numero 150.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 150"),
            QuestionOption(key="b", text="Risposta B esempio 150"),
            QuestionOption(key="c", text="Risposta C esempio 150"),
            QuestionOption(key="d", text="Risposta D esempio 150"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 150",
        grammar_point="Grammatica B1 esempio 150"
    ),
    Question(
        id=151,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-151: Questa è una domanda di esempio per il livello B1 numero 151.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 151"),
            QuestionOption(key="b", text="Risposta B esempio 151"),
            QuestionOption(key="c", text="Risposta C esempio 151"),
            QuestionOption(key="d", text="Risposta D esempio 151"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 151",
        grammar_point="Grammatica B1 esempio 151"
    ),
    Question(
        id=152,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-152: Questa è una domanda di esempio per il livello B1 numero 152.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 152"),
            QuestionOption(key="b", text="Risposta B esempio 152"),
            QuestionOption(key="c", text="Risposta C esempio 152"),
            QuestionOption(key="d", text="Risposta D esempio 152"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 152",
        grammar_point="Grammatica B1 esempio 152"
    ),
    Question(
        id=153,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-153: Questa è una domanda di esempio per il livello B1 numero 153.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 153"),
            QuestionOption(key="b", text="Risposta B esempio 153"),
            QuestionOption(key="c", text="Risposta C esempio 153"),
            QuestionOption(key="d", text="Risposta D esempio 153"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 153",
        grammar_point="Grammatica B1 esempio 153"
    ),
    Question(
        id=154,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-154: Questa è una domanda di esempio per il livello B1 numero 154.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 154"),
            QuestionOption(key="b", text="Risposta B esempio 154"),
            QuestionOption(key="c", text="Risposta C esempio 154"),
            QuestionOption(key="d", text="Risposta D esempio 154"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 154",
        grammar_point="Grammatica B1 esempio 154"
    ),
    Question(
        id=155,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-155: Questa è una domanda di esempio per il livello B1 numero 155.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 155"),
            QuestionOption(key="b", text="Risposta B esempio 155"),
            QuestionOption(key="c", text="Risposta C esempio 155"),
            QuestionOption(key="d", text="Risposta D esempio 155"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 155",
        grammar_point="Grammatica B1 esempio 155"
    ),
    Question(
        id=156,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-156: Questa è una domanda di esempio per il livello B1 numero 156.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 156"),
            QuestionOption(key="b", text="Risposta B esempio 156"),
            QuestionOption(key="c", text="Risposta C esempio 156"),
            QuestionOption(key="d", text="Risposta D esempio 156"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 156",
        grammar_point="Grammatica B1 esempio 156"
    ),
    Question(
        id=157,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-157: Questa è una domanda di esempio per il livello B1 numero 157.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 157"),
            QuestionOption(key="b", text="Risposta B esempio 157"),
            QuestionOption(key="c", text="Risposta C esempio 157"),
            QuestionOption(key="d", text="Risposta D esempio 157"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 157",
        grammar_point="Grammatica B1 esempio 157"
    ),
    Question(
        id=158,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-158: Questa è una domanda di esempio per il livello B1 numero 158.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 158"),
            QuestionOption(key="b", text="Risposta B esempio 158"),
            QuestionOption(key="c", text="Risposta C esempio 158"),
            QuestionOption(key="d", text="Risposta D esempio 158"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 158",
        grammar_point="Grammatica B1 esempio 158"
    ),
    Question(
        id=159,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-159: Questa è una domanda di esempio per il livello B1 numero 159.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 159"),
            QuestionOption(key="b", text="Risposta B esempio 159"),
            QuestionOption(key="c", text="Risposta C esempio 159"),
            QuestionOption(key="d", text="Risposta D esempio 159"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 159",
        grammar_point="Grammatica B1 esempio 159"
    ),
    Question(
        id=160,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-160: Questa è una domanda di esempio per il livello B1 numero 160.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 160"),
            QuestionOption(key="b", text="Risposta B esempio 160"),
            QuestionOption(key="c", text="Risposta C esempio 160"),
            QuestionOption(key="d", text="Risposta D esempio 160"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 160",
        grammar_point="Grammatica B1 esempio 160"
    ),
    Question(
        id=161,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-161: Questa è una domanda di esempio per il livello B1 numero 161.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 161"),
            QuestionOption(key="b", text="Risposta B esempio 161"),
            QuestionOption(key="c", text="Risposta C esempio 161"),
            QuestionOption(key="d", text="Risposta D esempio 161"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 161",
        grammar_point="Grammatica B1 esempio 161"
    ),
    Question(
        id=162,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-162: Questa è una domanda di esempio per il livello B1 numero 162.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 162"),
            QuestionOption(key="b", text="Risposta B esempio 162"),
            QuestionOption(key="c", text="Risposta C esempio 162"),
            QuestionOption(key="d", text="Risposta D esempio 162"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 162",
        grammar_point="Grammatica B1 esempio 162"
    ),
    Question(
        id=163,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-163: Questa è una domanda di esempio per il livello B1 numero 163.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 163"),
            QuestionOption(key="b", text="Risposta B esempio 163"),
            QuestionOption(key="c", text="Risposta C esempio 163"),
            QuestionOption(key="d", text="Risposta D esempio 163"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 163",
        grammar_point="Grammatica B1 esempio 163"
    ),
    Question(
        id=164,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-164: Questa è una domanda di esempio per il livello B1 numero 164.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 164"),
            QuestionOption(key="b", text="Risposta B esempio 164"),
            QuestionOption(key="c", text="Risposta C esempio 164"),
            QuestionOption(key="d", text="Risposta D esempio 164"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 164",
        grammar_point="Grammatica B1 esempio 164"
    ),
    Question(
        id=165,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-165: Questa è una domanda di esempio per il livello B1 numero 165.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 165"),
            QuestionOption(key="b", text="Risposta B esempio 165"),
            QuestionOption(key="c", text="Risposta C esempio 165"),
            QuestionOption(key="d", text="Risposta D esempio 165"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 165",
        grammar_point="Grammatica B1 esempio 165"
    ),
    Question(
        id=166,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-166: Questa è una domanda di esempio per il livello B1 numero 166.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 166"),
            QuestionOption(key="b", text="Risposta B esempio 166"),
            QuestionOption(key="c", text="Risposta C esempio 166"),
            QuestionOption(key="d", text="Risposta D esempio 166"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 166",
        grammar_point="Grammatica B1 esempio 166"
    ),
    Question(
        id=167,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-167: Questa è una domanda di esempio per il livello B1 numero 167.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 167"),
            QuestionOption(key="b", text="Risposta B esempio 167"),
            QuestionOption(key="c", text="Risposta C esempio 167"),
            QuestionOption(key="d", text="Risposta D esempio 167"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 167",
        grammar_point="Grammatica B1 esempio 167"
    ),
    Question(
        id=168,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-168: Questa è una domanda di esempio per il livello B1 numero 168.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 168"),
            QuestionOption(key="b", text="Risposta B esempio 168"),
            QuestionOption(key="c", text="Risposta C esempio 168"),
            QuestionOption(key="d", text="Risposta D esempio 168"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 168",
        grammar_point="Grammatica B1 esempio 168"
    ),
    Question(
        id=169,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-169: Questa è una domanda di esempio per il livello B1 numero 169.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 169"),
            QuestionOption(key="b", text="Risposta B esempio 169"),
            QuestionOption(key="c", text="Risposta C esempio 169"),
            QuestionOption(key="d", text="Risposta D esempio 169"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 169",
        grammar_point="Grammatica B1 esempio 169"
    ),
    Question(
        id=170,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-170: Questa è una domanda di esempio per il livello B1 numero 170.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 170"),
            QuestionOption(key="b", text="Risposta B esempio 170"),
            QuestionOption(key="c", text="Risposta C esempio 170"),
            QuestionOption(key="d", text="Risposta D esempio 170"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 170",
        grammar_point="Grammatica B1 esempio 170"
    ),
    Question(
        id=171,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-171: Questa è una domanda di esempio per il livello B1 numero 171.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 171"),
            QuestionOption(key="b", text="Risposta B esempio 171"),
            QuestionOption(key="c", text="Risposta C esempio 171"),
            QuestionOption(key="d", text="Risposta D esempio 171"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 171",
        grammar_point="Grammatica B1 esempio 171"
    ),
    Question(
        id=172,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-172: Questa è una domanda di esempio per il livello B1 numero 172.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 172"),
            QuestionOption(key="b", text="Risposta B esempio 172"),
            QuestionOption(key="c", text="Risposta C esempio 172"),
            QuestionOption(key="d", text="Risposta D esempio 172"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 172",
        grammar_point="Grammatica B1 esempio 172"
    ),
    Question(
        id=173,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-173: Questa è una domanda di esempio per il livello B1 numero 173.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 173"),
            QuestionOption(key="b", text="Risposta B esempio 173"),
            QuestionOption(key="c", text="Risposta C esempio 173"),
            QuestionOption(key="d", text="Risposta D esempio 173"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 173",
        grammar_point="Grammatica B1 esempio 173"
    ),
    Question(
        id=174,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-174: Questa è una domanda di esempio per il livello B1 numero 174.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 174"),
            QuestionOption(key="b", text="Risposta B esempio 174"),
            QuestionOption(key="c", text="Risposta C esempio 174"),
            QuestionOption(key="d", text="Risposta D esempio 174"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 174",
        grammar_point="Grammatica B1 esempio 174"
    ),
    Question(
        id=175,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-175: Questa è una domanda di esempio per il livello B1 numero 175.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 175"),
            QuestionOption(key="b", text="Risposta B esempio 175"),
            QuestionOption(key="c", text="Risposta C esempio 175"),
            QuestionOption(key="d", text="Risposta D esempio 175"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 175",
        grammar_point="Grammatica B1 esempio 175"
    ),
    Question(
        id=176,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-176: Questa è una domanda di esempio per il livello B1 numero 176.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 176"),
            QuestionOption(key="b", text="Risposta B esempio 176"),
            QuestionOption(key="c", text="Risposta C esempio 176"),
            QuestionOption(key="d", text="Risposta D esempio 176"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 176",
        grammar_point="Grammatica B1 esempio 176"
    ),
    Question(
        id=177,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-177: Questa è una domanda di esempio per il livello B1 numero 177.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 177"),
            QuestionOption(key="b", text="Risposta B esempio 177"),
            QuestionOption(key="c", text="Risposta C esempio 177"),
            QuestionOption(key="d", text="Risposta D esempio 177"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 177",
        grammar_point="Grammatica B1 esempio 177"
    ),
    Question(
        id=178,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-178: Questa è una domanda di esempio per il livello B1 numero 178.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 178"),
            QuestionOption(key="b", text="Risposta B esempio 178"),
            QuestionOption(key="c", text="Risposta C esempio 178"),
            QuestionOption(key="d", text="Risposta D esempio 178"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 178",
        grammar_point="Grammatica B1 esempio 178"
    ),
    Question(
        id=179,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-179: Questa è una domanda di esempio per il livello B1 numero 179.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 179"),
            QuestionOption(key="b", text="Risposta B esempio 179"),
            QuestionOption(key="c", text="Risposta C esempio 179"),
            QuestionOption(key="d", text="Risposta D esempio 179"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 179",
        grammar_point="Grammatica B1 esempio 179"
    ),
    Question(
        id=180,
        level=CEFRLevel.B1,
        section="C",
        question_text="Domanda B1-180: Questa è una domanda di esempio per il livello B1 numero 180.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 180"),
            QuestionOption(key="b", text="Risposta B esempio 180"),
            QuestionOption(key="c", text="Risposta C esempio 180"),
            QuestionOption(key="d", text="Risposta D esempio 180"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 180",
        grammar_point="Grammatica B1 esempio 180"
    ),
]


# ==========================================================================
# SECTION D: B2 LEVEL (Questions 181-240)
# ==========================================================================

SECTION_D_QUESTIONS = [
    Question(
        id=181,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-181: Questa è una domanda di esempio per il livello B2 numero 181.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 181"),
            QuestionOption(key="b", text="Risposta B esempio 181"),
            QuestionOption(key="c", text="Risposta C esempio 181"),
            QuestionOption(key="d", text="Risposta D esempio 181"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 181",
        grammar_point="Grammatica B2 esempio 181"
    ),
    Question(
        id=182,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-182: Questa è una domanda di esempio per il livello B2 numero 182.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 182"),
            QuestionOption(key="b", text="Risposta B esempio 182"),
            QuestionOption(key="c", text="Risposta C esempio 182"),
            QuestionOption(key="d", text="Risposta D esempio 182"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 182",
        grammar_point="Grammatica B2 esempio 182"
    ),
    Question(
        id=183,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-183: Questa è una domanda di esempio per il livello B2 numero 183.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 183"),
            QuestionOption(key="b", text="Risposta B esempio 183"),
            QuestionOption(key="c", text="Risposta C esempio 183"),
            QuestionOption(key="d", text="Risposta D esempio 183"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 183",
        grammar_point="Grammatica B2 esempio 183"
    ),
    Question(
        id=184,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-184: Questa è una domanda di esempio per il livello B2 numero 184.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 184"),
            QuestionOption(key="b", text="Risposta B esempio 184"),
            QuestionOption(key="c", text="Risposta C esempio 184"),
            QuestionOption(key="d", text="Risposta D esempio 184"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 184",
        grammar_point="Grammatica B2 esempio 184"
    ),
    Question(
        id=185,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-185: Questa è una domanda di esempio per il livello B2 numero 185.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 185"),
            QuestionOption(key="b", text="Risposta B esempio 185"),
            QuestionOption(key="c", text="Risposta C esempio 185"),
            QuestionOption(key="d", text="Risposta D esempio 185"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 185",
        grammar_point="Grammatica B2 esempio 185"
    ),
    Question(
        id=186,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-186: Questa è una domanda di esempio per il livello B2 numero 186.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 186"),
            QuestionOption(key="b", text="Risposta B esempio 186"),
            QuestionOption(key="c", text="Risposta C esempio 186"),
            QuestionOption(key="d", text="Risposta D esempio 186"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 186",
        grammar_point="Grammatica B2 esempio 186"
    ),
    Question(
        id=187,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-187: Questa è una domanda di esempio per il livello B2 numero 187.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 187"),
            QuestionOption(key="b", text="Risposta B esempio 187"),
            QuestionOption(key="c", text="Risposta C esempio 187"),
            QuestionOption(key="d", text="Risposta D esempio 187"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 187",
        grammar_point="Grammatica B2 esempio 187"
    ),
    Question(
        id=188,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-188: Questa è una domanda di esempio per il livello B2 numero 188.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 188"),
            QuestionOption(key="b", text="Risposta B esempio 188"),
            QuestionOption(key="c", text="Risposta C esempio 188"),
            QuestionOption(key="d", text="Risposta D esempio 188"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 188",
        grammar_point="Grammatica B2 esempio 188"
    ),
    Question(
        id=189,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-189: Questa è una domanda di esempio per il livello B2 numero 189.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 189"),
            QuestionOption(key="b", text="Risposta B esempio 189"),
            QuestionOption(key="c", text="Risposta C esempio 189"),
            QuestionOption(key="d", text="Risposta D esempio 189"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 189",
        grammar_point="Grammatica B2 esempio 189"
    ),
    Question(
        id=190,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-190: Questa è una domanda di esempio per il livello B2 numero 190.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 190"),
            QuestionOption(key="b", text="Risposta B esempio 190"),
            QuestionOption(key="c", text="Risposta C esempio 190"),
            QuestionOption(key="d", text="Risposta D esempio 190"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 190",
        grammar_point="Grammatica B2 esempio 190"
    ),
    Question(
        id=191,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-191: Questa è una domanda di esempio per il livello B2 numero 191.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 191"),
            QuestionOption(key="b", text="Risposta B esempio 191"),
            QuestionOption(key="c", text="Risposta C esempio 191"),
            QuestionOption(key="d", text="Risposta D esempio 191"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 191",
        grammar_point="Grammatica B2 esempio 191"
    ),
    Question(
        id=192,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-192: Questa è una domanda di esempio per il livello B2 numero 192.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 192"),
            QuestionOption(key="b", text="Risposta B esempio 192"),
            QuestionOption(key="c", text="Risposta C esempio 192"),
            QuestionOption(key="d", text="Risposta D esempio 192"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 192",
        grammar_point="Grammatica B2 esempio 192"
    ),
    Question(
        id=193,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-193: Questa è una domanda di esempio per il livello B2 numero 193.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 193"),
            QuestionOption(key="b", text="Risposta B esempio 193"),
            QuestionOption(key="c", text="Risposta C esempio 193"),
            QuestionOption(key="d", text="Risposta D esempio 193"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 193",
        grammar_point="Grammatica B2 esempio 193"
    ),
    Question(
        id=194,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-194: Questa è una domanda di esempio per il livello B2 numero 194.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 194"),
            QuestionOption(key="b", text="Risposta B esempio 194"),
            QuestionOption(key="c", text="Risposta C esempio 194"),
            QuestionOption(key="d", text="Risposta D esempio 194"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 194",
        grammar_point="Grammatica B2 esempio 194"
    ),
    Question(
        id=195,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-195: Questa è una domanda di esempio per il livello B2 numero 195.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 195"),
            QuestionOption(key="b", text="Risposta B esempio 195"),
            QuestionOption(key="c", text="Risposta C esempio 195"),
            QuestionOption(key="d", text="Risposta D esempio 195"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 195",
        grammar_point="Grammatica B2 esempio 195"
    ),
    Question(
        id=196,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-196: Questa è una domanda di esempio per il livello B2 numero 196.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 196"),
            QuestionOption(key="b", text="Risposta B esempio 196"),
            QuestionOption(key="c", text="Risposta C esempio 196"),
            QuestionOption(key="d", text="Risposta D esempio 196"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 196",
        grammar_point="Grammatica B2 esempio 196"
    ),
    Question(
        id=197,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-197: Questa è una domanda di esempio per il livello B2 numero 197.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 197"),
            QuestionOption(key="b", text="Risposta B esempio 197"),
            QuestionOption(key="c", text="Risposta C esempio 197"),
            QuestionOption(key="d", text="Risposta D esempio 197"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 197",
        grammar_point="Grammatica B2 esempio 197"
    ),
    Question(
        id=198,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-198: Questa è una domanda di esempio per il livello B2 numero 198.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 198"),
            QuestionOption(key="b", text="Risposta B esempio 198"),
            QuestionOption(key="c", text="Risposta C esempio 198"),
            QuestionOption(key="d", text="Risposta D esempio 198"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 198",
        grammar_point="Grammatica B2 esempio 198"
    ),
    Question(
        id=199,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-199: Questa è una domanda di esempio per il livello B2 numero 199.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 199"),
            QuestionOption(key="b", text="Risposta B esempio 199"),
            QuestionOption(key="c", text="Risposta C esempio 199"),
            QuestionOption(key="d", text="Risposta D esempio 199"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 199",
        grammar_point="Grammatica B2 esempio 199"
    ),
    Question(
        id=200,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-200: Questa è una domanda di esempio per il livello B2 numero 200.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 200"),
            QuestionOption(key="b", text="Risposta B esempio 200"),
            QuestionOption(key="c", text="Risposta C esempio 200"),
            QuestionOption(key="d", text="Risposta D esempio 200"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 200",
        grammar_point="Grammatica B2 esempio 200"
    ),
    Question(
        id=201,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-201: Questa è una domanda di esempio per il livello B2 numero 201.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 201"),
            QuestionOption(key="b", text="Risposta B esempio 201"),
            QuestionOption(key="c", text="Risposta C esempio 201"),
            QuestionOption(key="d", text="Risposta D esempio 201"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 201",
        grammar_point="Grammatica B2 esempio 201"
    ),
    Question(
        id=202,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-202: Questa è una domanda di esempio per il livello B2 numero 202.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 202"),
            QuestionOption(key="b", text="Risposta B esempio 202"),
            QuestionOption(key="c", text="Risposta C esempio 202"),
            QuestionOption(key="d", text="Risposta D esempio 202"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 202",
        grammar_point="Grammatica B2 esempio 202"
    ),
    Question(
        id=203,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-203: Questa è una domanda di esempio per il livello B2 numero 203.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 203"),
            QuestionOption(key="b", text="Risposta B esempio 203"),
            QuestionOption(key="c", text="Risposta C esempio 203"),
            QuestionOption(key="d", text="Risposta D esempio 203"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 203",
        grammar_point="Grammatica B2 esempio 203"
    ),
    Question(
        id=204,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-204: Questa è una domanda di esempio per il livello B2 numero 204.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 204"),
            QuestionOption(key="b", text="Risposta B esempio 204"),
            QuestionOption(key="c", text="Risposta C esempio 204"),
            QuestionOption(key="d", text="Risposta D esempio 204"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 204",
        grammar_point="Grammatica B2 esempio 204"
    ),
    Question(
        id=205,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-205: Questa è una domanda di esempio per il livello B2 numero 205.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 205"),
            QuestionOption(key="b", text="Risposta B esempio 205"),
            QuestionOption(key="c", text="Risposta C esempio 205"),
            QuestionOption(key="d", text="Risposta D esempio 205"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 205",
        grammar_point="Grammatica B2 esempio 205"
    ),
    Question(
        id=206,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-206: Questa è una domanda di esempio per il livello B2 numero 206.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 206"),
            QuestionOption(key="b", text="Risposta B esempio 206"),
            QuestionOption(key="c", text="Risposta C esempio 206"),
            QuestionOption(key="d", text="Risposta D esempio 206"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 206",
        grammar_point="Grammatica B2 esempio 206"
    ),
    Question(
        id=207,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-207: Questa è una domanda di esempio per il livello B2 numero 207.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 207"),
            QuestionOption(key="b", text="Risposta B esempio 207"),
            QuestionOption(key="c", text="Risposta C esempio 207"),
            QuestionOption(key="d", text="Risposta D esempio 207"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 207",
        grammar_point="Grammatica B2 esempio 207"
    ),
    Question(
        id=208,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-208: Questa è una domanda di esempio per il livello B2 numero 208.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 208"),
            QuestionOption(key="b", text="Risposta B esempio 208"),
            QuestionOption(key="c", text="Risposta C esempio 208"),
            QuestionOption(key="d", text="Risposta D esempio 208"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 208",
        grammar_point="Grammatica B2 esempio 208"
    ),
    Question(
        id=209,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-209: Questa è una domanda di esempio per il livello B2 numero 209.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 209"),
            QuestionOption(key="b", text="Risposta B esempio 209"),
            QuestionOption(key="c", text="Risposta C esempio 209"),
            QuestionOption(key="d", text="Risposta D esempio 209"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 209",
        grammar_point="Grammatica B2 esempio 209"
    ),
    Question(
        id=210,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-210: Questa è una domanda di esempio per il livello B2 numero 210.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 210"),
            QuestionOption(key="b", text="Risposta B esempio 210"),
            QuestionOption(key="c", text="Risposta C esempio 210"),
            QuestionOption(key="d", text="Risposta D esempio 210"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 210",
        grammar_point="Grammatica B2 esempio 210"
    ),
    Question(
        id=211,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-211: Questa è una domanda di esempio per il livello B2 numero 211.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 211"),
            QuestionOption(key="b", text="Risposta B esempio 211"),
            QuestionOption(key="c", text="Risposta C esempio 211"),
            QuestionOption(key="d", text="Risposta D esempio 211"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 211",
        grammar_point="Grammatica B2 esempio 211"
    ),
    Question(
        id=212,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-212: Questa è una domanda di esempio per il livello B2 numero 212.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 212"),
            QuestionOption(key="b", text="Risposta B esempio 212"),
            QuestionOption(key="c", text="Risposta C esempio 212"),
            QuestionOption(key="d", text="Risposta D esempio 212"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 212",
        grammar_point="Grammatica B2 esempio 212"
    ),
    Question(
        id=213,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-213: Questa è una domanda di esempio per il livello B2 numero 213.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 213"),
            QuestionOption(key="b", text="Risposta B esempio 213"),
            QuestionOption(key="c", text="Risposta C esempio 213"),
            QuestionOption(key="d", text="Risposta D esempio 213"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 213",
        grammar_point="Grammatica B2 esempio 213"
    ),
    Question(
        id=214,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-214: Questa è una domanda di esempio per il livello B2 numero 214.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 214"),
            QuestionOption(key="b", text="Risposta B esempio 214"),
            QuestionOption(key="c", text="Risposta C esempio 214"),
            QuestionOption(key="d", text="Risposta D esempio 214"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 214",
        grammar_point="Grammatica B2 esempio 214"
    ),
    Question(
        id=215,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-215: Questa è una domanda di esempio per il livello B2 numero 215.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 215"),
            QuestionOption(key="b", text="Risposta B esempio 215"),
            QuestionOption(key="c", text="Risposta C esempio 215"),
            QuestionOption(key="d", text="Risposta D esempio 215"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 215",
        grammar_point="Grammatica B2 esempio 215"
    ),
    Question(
        id=216,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-216: Questa è una domanda di esempio per il livello B2 numero 216.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 216"),
            QuestionOption(key="b", text="Risposta B esempio 216"),
            QuestionOption(key="c", text="Risposta C esempio 216"),
            QuestionOption(key="d", text="Risposta D esempio 216"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 216",
        grammar_point="Grammatica B2 esempio 216"
    ),
    Question(
        id=217,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-217: Questa è una domanda di esempio per il livello B2 numero 217.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 217"),
            QuestionOption(key="b", text="Risposta B esempio 217"),
            QuestionOption(key="c", text="Risposta C esempio 217"),
            QuestionOption(key="d", text="Risposta D esempio 217"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 217",
        grammar_point="Grammatica B2 esempio 217"
    ),
    Question(
        id=218,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-218: Questa è una domanda di esempio per il livello B2 numero 218.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 218"),
            QuestionOption(key="b", text="Risposta B esempio 218"),
            QuestionOption(key="c", text="Risposta C esempio 218"),
            QuestionOption(key="d", text="Risposta D esempio 218"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 218",
        grammar_point="Grammatica B2 esempio 218"
    ),
    Question(
        id=219,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-219: Questa è una domanda di esempio per il livello B2 numero 219.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 219"),
            QuestionOption(key="b", text="Risposta B esempio 219"),
            QuestionOption(key="c", text="Risposta C esempio 219"),
            QuestionOption(key="d", text="Risposta D esempio 219"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 219",
        grammar_point="Grammatica B2 esempio 219"
    ),
    Question(
        id=220,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-220: Questa è una domanda di esempio per il livello B2 numero 220.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 220"),
            QuestionOption(key="b", text="Risposta B esempio 220"),
            QuestionOption(key="c", text="Risposta C esempio 220"),
            QuestionOption(key="d", text="Risposta D esempio 220"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 220",
        grammar_point="Grammatica B2 esempio 220"
    ),
    Question(
        id=221,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-221: Questa è una domanda di esempio per il livello B2 numero 221.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 221"),
            QuestionOption(key="b", text="Risposta B esempio 221"),
            QuestionOption(key="c", text="Risposta C esempio 221"),
            QuestionOption(key="d", text="Risposta D esempio 221"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 221",
        grammar_point="Grammatica B2 esempio 221"
    ),
    Question(
        id=222,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-222: Questa è una domanda di esempio per il livello B2 numero 222.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 222"),
            QuestionOption(key="b", text="Risposta B esempio 222"),
            QuestionOption(key="c", text="Risposta C esempio 222"),
            QuestionOption(key="d", text="Risposta D esempio 222"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 222",
        grammar_point="Grammatica B2 esempio 222"
    ),
    Question(
        id=223,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-223: Questa è una domanda di esempio per il livello B2 numero 223.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 223"),
            QuestionOption(key="b", text="Risposta B esempio 223"),
            QuestionOption(key="c", text="Risposta C esempio 223"),
            QuestionOption(key="d", text="Risposta D esempio 223"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 223",
        grammar_point="Grammatica B2 esempio 223"
    ),
    Question(
        id=224,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-224: Questa è una domanda di esempio per il livello B2 numero 224.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 224"),
            QuestionOption(key="b", text="Risposta B esempio 224"),
            QuestionOption(key="c", text="Risposta C esempio 224"),
            QuestionOption(key="d", text="Risposta D esempio 224"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 224",
        grammar_point="Grammatica B2 esempio 224"
    ),
    Question(
        id=225,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-225: Questa è una domanda di esempio per il livello B2 numero 225.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 225"),
            QuestionOption(key="b", text="Risposta B esempio 225"),
            QuestionOption(key="c", text="Risposta C esempio 225"),
            QuestionOption(key="d", text="Risposta D esempio 225"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 225",
        grammar_point="Grammatica B2 esempio 225"
    ),
    Question(
        id=226,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-226: Questa è una domanda di esempio per il livello B2 numero 226.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 226"),
            QuestionOption(key="b", text="Risposta B esempio 226"),
            QuestionOption(key="c", text="Risposta C esempio 226"),
            QuestionOption(key="d", text="Risposta D esempio 226"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 226",
        grammar_point="Grammatica B2 esempio 226"
    ),
    Question(
        id=227,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-227: Questa è una domanda di esempio per il livello B2 numero 227.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 227"),
            QuestionOption(key="b", text="Risposta B esempio 227"),
            QuestionOption(key="c", text="Risposta C esempio 227"),
            QuestionOption(key="d", text="Risposta D esempio 227"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 227",
        grammar_point="Grammatica B2 esempio 227"
    ),
    Question(
        id=228,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-228: Questa è una domanda di esempio per il livello B2 numero 228.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 228"),
            QuestionOption(key="b", text="Risposta B esempio 228"),
            QuestionOption(key="c", text="Risposta C esempio 228"),
            QuestionOption(key="d", text="Risposta D esempio 228"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 228",
        grammar_point="Grammatica B2 esempio 228"
    ),
    Question(
        id=229,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-229: Questa è una domanda di esempio per il livello B2 numero 229.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 229"),
            QuestionOption(key="b", text="Risposta B esempio 229"),
            QuestionOption(key="c", text="Risposta C esempio 229"),
            QuestionOption(key="d", text="Risposta D esempio 229"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 229",
        grammar_point="Grammatica B2 esempio 229"
    ),
    Question(
        id=230,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-230: Questa è una domanda di esempio per il livello B2 numero 230.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 230"),
            QuestionOption(key="b", text="Risposta B esempio 230"),
            QuestionOption(key="c", text="Risposta C esempio 230"),
            QuestionOption(key="d", text="Risposta D esempio 230"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 230",
        grammar_point="Grammatica B2 esempio 230"
    ),
    Question(
        id=231,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-231: Questa è una domanda di esempio per il livello B2 numero 231.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 231"),
            QuestionOption(key="b", text="Risposta B esempio 231"),
            QuestionOption(key="c", text="Risposta C esempio 231"),
            QuestionOption(key="d", text="Risposta D esempio 231"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 231",
        grammar_point="Grammatica B2 esempio 231"
    ),
    Question(
        id=232,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-232: Questa è una domanda di esempio per il livello B2 numero 232.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 232"),
            QuestionOption(key="b", text="Risposta B esempio 232"),
            QuestionOption(key="c", text="Risposta C esempio 232"),
            QuestionOption(key="d", text="Risposta D esempio 232"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 232",
        grammar_point="Grammatica B2 esempio 232"
    ),
    Question(
        id=233,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-233: Questa è una domanda di esempio per il livello B2 numero 233.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 233"),
            QuestionOption(key="b", text="Risposta B esempio 233"),
            QuestionOption(key="c", text="Risposta C esempio 233"),
            QuestionOption(key="d", text="Risposta D esempio 233"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 233",
        grammar_point="Grammatica B2 esempio 233"
    ),
    Question(
        id=234,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-234: Questa è una domanda di esempio per il livello B2 numero 234.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 234"),
            QuestionOption(key="b", text="Risposta B esempio 234"),
            QuestionOption(key="c", text="Risposta C esempio 234"),
            QuestionOption(key="d", text="Risposta D esempio 234"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 234",
        grammar_point="Grammatica B2 esempio 234"
    ),
    Question(
        id=235,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-235: Questa è una domanda di esempio per il livello B2 numero 235.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 235"),
            QuestionOption(key="b", text="Risposta B esempio 235"),
            QuestionOption(key="c", text="Risposta C esempio 235"),
            QuestionOption(key="d", text="Risposta D esempio 235"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 235",
        grammar_point="Grammatica B2 esempio 235"
    ),
    Question(
        id=236,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-236: Questa è una domanda di esempio per il livello B2 numero 236.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 236"),
            QuestionOption(key="b", text="Risposta B esempio 236"),
            QuestionOption(key="c", text="Risposta C esempio 236"),
            QuestionOption(key="d", text="Risposta D esempio 236"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 236",
        grammar_point="Grammatica B2 esempio 236"
    ),
    Question(
        id=237,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-237: Questa è una domanda di esempio per il livello B2 numero 237.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 237"),
            QuestionOption(key="b", text="Risposta B esempio 237"),
            QuestionOption(key="c", text="Risposta C esempio 237"),
            QuestionOption(key="d", text="Risposta D esempio 237"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 237",
        grammar_point="Grammatica B2 esempio 237"
    ),
    Question(
        id=238,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-238: Questa è una domanda di esempio per il livello B2 numero 238.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 238"),
            QuestionOption(key="b", text="Risposta B esempio 238"),
            QuestionOption(key="c", text="Risposta C esempio 238"),
            QuestionOption(key="d", text="Risposta D esempio 238"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 238",
        grammar_point="Grammatica B2 esempio 238"
    ),
    Question(
        id=239,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-239: Questa è una domanda di esempio per il livello B2 numero 239.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 239"),
            QuestionOption(key="b", text="Risposta B esempio 239"),
            QuestionOption(key="c", text="Risposta C esempio 239"),
            QuestionOption(key="d", text="Risposta D esempio 239"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 239",
        grammar_point="Grammatica B2 esempio 239"
    ),
    Question(
        id=240,
        level=CEFRLevel.B2,
        section="D",
        question_text="Domanda B2-240: Questa è una domanda di esempio per il livello B2 numero 240.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 240"),
            QuestionOption(key="b", text="Risposta B esempio 240"),
            QuestionOption(key="c", text="Risposta C esempio 240"),
            QuestionOption(key="d", text="Risposta D esempio 240"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 240",
        grammar_point="Grammatica B2 esempio 240"
    ),
]


# ==========================================================================
# SECTION E: C1 LEVEL (Questions 241-300)
# ==========================================================================

SECTION_E_QUESTIONS = [
    Question(
        id=241,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-241: Questa è una domanda di esempio per il livello C1 numero 241.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 241"),
            QuestionOption(key="b", text="Risposta B esempio 241"),
            QuestionOption(key="c", text="Risposta C esempio 241"),
            QuestionOption(key="d", text="Risposta D esempio 241"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 241",
        grammar_point="Grammatica C1 esempio 241"
    ),
    Question(
        id=242,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-242: Questa è una domanda di esempio per il livello C1 numero 242.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 242"),
            QuestionOption(key="b", text="Risposta B esempio 242"),
            QuestionOption(key="c", text="Risposta C esempio 242"),
            QuestionOption(key="d", text="Risposta D esempio 242"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 242",
        grammar_point="Grammatica C1 esempio 242"
    ),
    Question(
        id=243,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-243: Questa è una domanda di esempio per il livello C1 numero 243.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 243"),
            QuestionOption(key="b", text="Risposta B esempio 243"),
            QuestionOption(key="c", text="Risposta C esempio 243"),
            QuestionOption(key="d", text="Risposta D esempio 243"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 243",
        grammar_point="Grammatica C1 esempio 243"
    ),
    Question(
        id=244,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-244: Questa è una domanda di esempio per il livello C1 numero 244.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 244"),
            QuestionOption(key="b", text="Risposta B esempio 244"),
            QuestionOption(key="c", text="Risposta C esempio 244"),
            QuestionOption(key="d", text="Risposta D esempio 244"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 244",
        grammar_point="Grammatica C1 esempio 244"
    ),
    Question(
        id=245,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-245: Questa è una domanda di esempio per il livello C1 numero 245.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 245"),
            QuestionOption(key="b", text="Risposta B esempio 245"),
            QuestionOption(key="c", text="Risposta C esempio 245"),
            QuestionOption(key="d", text="Risposta D esempio 245"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 245",
        grammar_point="Grammatica C1 esempio 245"
    ),
    Question(
        id=246,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-246: Questa è una domanda di esempio per il livello C1 numero 246.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 246"),
            QuestionOption(key="b", text="Risposta B esempio 246"),
            QuestionOption(key="c", text="Risposta C esempio 246"),
            QuestionOption(key="d", text="Risposta D esempio 246"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 246",
        grammar_point="Grammatica C1 esempio 246"
    ),
    Question(
        id=247,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-247: Questa è una domanda di esempio per il livello C1 numero 247.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 247"),
            QuestionOption(key="b", text="Risposta B esempio 247"),
            QuestionOption(key="c", text="Risposta C esempio 247"),
            QuestionOption(key="d", text="Risposta D esempio 247"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 247",
        grammar_point="Grammatica C1 esempio 247"
    ),
    Question(
        id=248,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-248: Questa è una domanda di esempio per il livello C1 numero 248.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 248"),
            QuestionOption(key="b", text="Risposta B esempio 248"),
            QuestionOption(key="c", text="Risposta C esempio 248"),
            QuestionOption(key="d", text="Risposta D esempio 248"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 248",
        grammar_point="Grammatica C1 esempio 248"
    ),
    Question(
        id=249,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-249: Questa è una domanda di esempio per il livello C1 numero 249.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 249"),
            QuestionOption(key="b", text="Risposta B esempio 249"),
            QuestionOption(key="c", text="Risposta C esempio 249"),
            QuestionOption(key="d", text="Risposta D esempio 249"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 249",
        grammar_point="Grammatica C1 esempio 249"
    ),
    Question(
        id=250,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-250: Questa è una domanda di esempio per il livello C1 numero 250.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 250"),
            QuestionOption(key="b", text="Risposta B esempio 250"),
            QuestionOption(key="c", text="Risposta C esempio 250"),
            QuestionOption(key="d", text="Risposta D esempio 250"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 250",
        grammar_point="Grammatica C1 esempio 250"
    ),
    Question(
        id=251,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-251: Questa è una domanda di esempio per il livello C1 numero 251.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 251"),
            QuestionOption(key="b", text="Risposta B esempio 251"),
            QuestionOption(key="c", text="Risposta C esempio 251"),
            QuestionOption(key="d", text="Risposta D esempio 251"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 251",
        grammar_point="Grammatica C1 esempio 251"
    ),
    Question(
        id=252,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-252: Questa è una domanda di esempio per il livello C1 numero 252.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 252"),
            QuestionOption(key="b", text="Risposta B esempio 252"),
            QuestionOption(key="c", text="Risposta C esempio 252"),
            QuestionOption(key="d", text="Risposta D esempio 252"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 252",
        grammar_point="Grammatica C1 esempio 252"
    ),
    Question(
        id=253,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-253: Questa è una domanda di esempio per il livello C1 numero 253.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 253"),
            QuestionOption(key="b", text="Risposta B esempio 253"),
            QuestionOption(key="c", text="Risposta C esempio 253"),
            QuestionOption(key="d", text="Risposta D esempio 253"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 253",
        grammar_point="Grammatica C1 esempio 253"
    ),
    Question(
        id=254,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-254: Questa è una domanda di esempio per il livello C1 numero 254.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 254"),
            QuestionOption(key="b", text="Risposta B esempio 254"),
            QuestionOption(key="c", text="Risposta C esempio 254"),
            QuestionOption(key="d", text="Risposta D esempio 254"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 254",
        grammar_point="Grammatica C1 esempio 254"
    ),
    Question(
        id=255,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-255: Questa è una domanda di esempio per il livello C1 numero 255.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 255"),
            QuestionOption(key="b", text="Risposta B esempio 255"),
            QuestionOption(key="c", text="Risposta C esempio 255"),
            QuestionOption(key="d", text="Risposta D esempio 255"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 255",
        grammar_point="Grammatica C1 esempio 255"
    ),
    Question(
        id=256,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-256: Questa è una domanda di esempio per il livello C1 numero 256.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 256"),
            QuestionOption(key="b", text="Risposta B esempio 256"),
            QuestionOption(key="c", text="Risposta C esempio 256"),
            QuestionOption(key="d", text="Risposta D esempio 256"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 256",
        grammar_point="Grammatica C1 esempio 256"
    ),
    Question(
        id=257,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-257: Questa è una domanda di esempio per il livello C1 numero 257.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 257"),
            QuestionOption(key="b", text="Risposta B esempio 257"),
            QuestionOption(key="c", text="Risposta C esempio 257"),
            QuestionOption(key="d", text="Risposta D esempio 257"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 257",
        grammar_point="Grammatica C1 esempio 257"
    ),
    Question(
        id=258,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-258: Questa è una domanda di esempio per il livello C1 numero 258.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 258"),
            QuestionOption(key="b", text="Risposta B esempio 258"),
            QuestionOption(key="c", text="Risposta C esempio 258"),
            QuestionOption(key="d", text="Risposta D esempio 258"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 258",
        grammar_point="Grammatica C1 esempio 258"
    ),
    Question(
        id=259,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-259: Questa è una domanda di esempio per il livello C1 numero 259.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 259"),
            QuestionOption(key="b", text="Risposta B esempio 259"),
            QuestionOption(key="c", text="Risposta C esempio 259"),
            QuestionOption(key="d", text="Risposta D esempio 259"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 259",
        grammar_point="Grammatica C1 esempio 259"
    ),
    Question(
        id=260,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-260: Questa è una domanda di esempio per il livello C1 numero 260.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 260"),
            QuestionOption(key="b", text="Risposta B esempio 260"),
            QuestionOption(key="c", text="Risposta C esempio 260"),
            QuestionOption(key="d", text="Risposta D esempio 260"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 260",
        grammar_point="Grammatica C1 esempio 260"
    ),
    Question(
        id=261,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-261: Questa è una domanda di esempio per il livello C1 numero 261.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 261"),
            QuestionOption(key="b", text="Risposta B esempio 261"),
            QuestionOption(key="c", text="Risposta C esempio 261"),
            QuestionOption(key="d", text="Risposta D esempio 261"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 261",
        grammar_point="Grammatica C1 esempio 261"
    ),
    Question(
        id=262,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-262: Questa è una domanda di esempio per il livello C1 numero 262.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 262"),
            QuestionOption(key="b", text="Risposta B esempio 262"),
            QuestionOption(key="c", text="Risposta C esempio 262"),
            QuestionOption(key="d", text="Risposta D esempio 262"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 262",
        grammar_point="Grammatica C1 esempio 262"
    ),
    Question(
        id=263,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-263: Questa è una domanda di esempio per il livello C1 numero 263.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 263"),
            QuestionOption(key="b", text="Risposta B esempio 263"),
            QuestionOption(key="c", text="Risposta C esempio 263"),
            QuestionOption(key="d", text="Risposta D esempio 263"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 263",
        grammar_point="Grammatica C1 esempio 263"
    ),
    Question(
        id=264,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-264: Questa è una domanda di esempio per il livello C1 numero 264.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 264"),
            QuestionOption(key="b", text="Risposta B esempio 264"),
            QuestionOption(key="c", text="Risposta C esempio 264"),
            QuestionOption(key="d", text="Risposta D esempio 264"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 264",
        grammar_point="Grammatica C1 esempio 264"
    ),
    Question(
        id=265,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-265: Questa è una domanda di esempio per il livello C1 numero 265.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 265"),
            QuestionOption(key="b", text="Risposta B esempio 265"),
            QuestionOption(key="c", text="Risposta C esempio 265"),
            QuestionOption(key="d", text="Risposta D esempio 265"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 265",
        grammar_point="Grammatica C1 esempio 265"
    ),
    Question(
        id=266,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-266: Questa è una domanda di esempio per il livello C1 numero 266.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 266"),
            QuestionOption(key="b", text="Risposta B esempio 266"),
            QuestionOption(key="c", text="Risposta C esempio 266"),
            QuestionOption(key="d", text="Risposta D esempio 266"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 266",
        grammar_point="Grammatica C1 esempio 266"
    ),
    Question(
        id=267,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-267: Questa è una domanda di esempio per il livello C1 numero 267.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 267"),
            QuestionOption(key="b", text="Risposta B esempio 267"),
            QuestionOption(key="c", text="Risposta C esempio 267"),
            QuestionOption(key="d", text="Risposta D esempio 267"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 267",
        grammar_point="Grammatica C1 esempio 267"
    ),
    Question(
        id=268,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-268: Questa è una domanda di esempio per il livello C1 numero 268.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 268"),
            QuestionOption(key="b", text="Risposta B esempio 268"),
            QuestionOption(key="c", text="Risposta C esempio 268"),
            QuestionOption(key="d", text="Risposta D esempio 268"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 268",
        grammar_point="Grammatica C1 esempio 268"
    ),
    Question(
        id=269,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-269: Questa è una domanda di esempio per il livello C1 numero 269.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 269"),
            QuestionOption(key="b", text="Risposta B esempio 269"),
            QuestionOption(key="c", text="Risposta C esempio 269"),
            QuestionOption(key="d", text="Risposta D esempio 269"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 269",
        grammar_point="Grammatica C1 esempio 269"
    ),
    Question(
        id=270,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-270: Questa è una domanda di esempio per il livello C1 numero 270.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 270"),
            QuestionOption(key="b", text="Risposta B esempio 270"),
            QuestionOption(key="c", text="Risposta C esempio 270"),
            QuestionOption(key="d", text="Risposta D esempio 270"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 270",
        grammar_point="Grammatica C1 esempio 270"
    ),
    Question(
        id=271,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-271: Questa è una domanda di esempio per il livello C1 numero 271.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 271"),
            QuestionOption(key="b", text="Risposta B esempio 271"),
            QuestionOption(key="c", text="Risposta C esempio 271"),
            QuestionOption(key="d", text="Risposta D esempio 271"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 271",
        grammar_point="Grammatica C1 esempio 271"
    ),
    Question(
        id=272,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-272: Questa è una domanda di esempio per il livello C1 numero 272.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 272"),
            QuestionOption(key="b", text="Risposta B esempio 272"),
            QuestionOption(key="c", text="Risposta C esempio 272"),
            QuestionOption(key="d", text="Risposta D esempio 272"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 272",
        grammar_point="Grammatica C1 esempio 272"
    ),
    Question(
        id=273,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-273: Questa è una domanda di esempio per il livello C1 numero 273.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 273"),
            QuestionOption(key="b", text="Risposta B esempio 273"),
            QuestionOption(key="c", text="Risposta C esempio 273"),
            QuestionOption(key="d", text="Risposta D esempio 273"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 273",
        grammar_point="Grammatica C1 esempio 273"
    ),
    Question(
        id=274,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-274: Questa è una domanda di esempio per il livello C1 numero 274.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 274"),
            QuestionOption(key="b", text="Risposta B esempio 274"),
            QuestionOption(key="c", text="Risposta C esempio 274"),
            QuestionOption(key="d", text="Risposta D esempio 274"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 274",
        grammar_point="Grammatica C1 esempio 274"
    ),
    Question(
        id=275,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-275: Questa è una domanda di esempio per il livello C1 numero 275.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 275"),
            QuestionOption(key="b", text="Risposta B esempio 275"),
            QuestionOption(key="c", text="Risposta C esempio 275"),
            QuestionOption(key="d", text="Risposta D esempio 275"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 275",
        grammar_point="Grammatica C1 esempio 275"
    ),
    Question(
        id=276,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-276: Questa è una domanda di esempio per il livello C1 numero 276.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 276"),
            QuestionOption(key="b", text="Risposta B esempio 276"),
            QuestionOption(key="c", text="Risposta C esempio 276"),
            QuestionOption(key="d", text="Risposta D esempio 276"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 276",
        grammar_point="Grammatica C1 esempio 276"
    ),
    Question(
        id=277,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-277: Questa è una domanda di esempio per il livello C1 numero 277.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 277"),
            QuestionOption(key="b", text="Risposta B esempio 277"),
            QuestionOption(key="c", text="Risposta C esempio 277"),
            QuestionOption(key="d", text="Risposta D esempio 277"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 277",
        grammar_point="Grammatica C1 esempio 277"
    ),
    Question(
        id=278,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-278: Questa è una domanda di esempio per il livello C1 numero 278.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 278"),
            QuestionOption(key="b", text="Risposta B esempio 278"),
            QuestionOption(key="c", text="Risposta C esempio 278"),
            QuestionOption(key="d", text="Risposta D esempio 278"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 278",
        grammar_point="Grammatica C1 esempio 278"
    ),
    Question(
        id=279,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-279: Questa è una domanda di esempio per il livello C1 numero 279.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 279"),
            QuestionOption(key="b", text="Risposta B esempio 279"),
            QuestionOption(key="c", text="Risposta C esempio 279"),
            QuestionOption(key="d", text="Risposta D esempio 279"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 279",
        grammar_point="Grammatica C1 esempio 279"
    ),
    Question(
        id=280,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-280: Questa è una domanda di esempio per il livello C1 numero 280.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 280"),
            QuestionOption(key="b", text="Risposta B esempio 280"),
            QuestionOption(key="c", text="Risposta C esempio 280"),
            QuestionOption(key="d", text="Risposta D esempio 280"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 280",
        grammar_point="Grammatica C1 esempio 280"
    ),
    Question(
        id=281,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-281: Questa è una domanda di esempio per il livello C1 numero 281.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 281"),
            QuestionOption(key="b", text="Risposta B esempio 281"),
            QuestionOption(key="c", text="Risposta C esempio 281"),
            QuestionOption(key="d", text="Risposta D esempio 281"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 281",
        grammar_point="Grammatica C1 esempio 281"
    ),
    Question(
        id=282,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-282: Questa è una domanda di esempio per il livello C1 numero 282.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 282"),
            QuestionOption(key="b", text="Risposta B esempio 282"),
            QuestionOption(key="c", text="Risposta C esempio 282"),
            QuestionOption(key="d", text="Risposta D esempio 282"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 282",
        grammar_point="Grammatica C1 esempio 282"
    ),
    Question(
        id=283,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-283: Questa è una domanda di esempio per il livello C1 numero 283.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 283"),
            QuestionOption(key="b", text="Risposta B esempio 283"),
            QuestionOption(key="c", text="Risposta C esempio 283"),
            QuestionOption(key="d", text="Risposta D esempio 283"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 283",
        grammar_point="Grammatica C1 esempio 283"
    ),
    Question(
        id=284,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-284: Questa è una domanda di esempio per il livello C1 numero 284.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 284"),
            QuestionOption(key="b", text="Risposta B esempio 284"),
            QuestionOption(key="c", text="Risposta C esempio 284"),
            QuestionOption(key="d", text="Risposta D esempio 284"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 284",
        grammar_point="Grammatica C1 esempio 284"
    ),
    Question(
        id=285,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-285: Questa è una domanda di esempio per il livello C1 numero 285.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 285"),
            QuestionOption(key="b", text="Risposta B esempio 285"),
            QuestionOption(key="c", text="Risposta C esempio 285"),
            QuestionOption(key="d", text="Risposta D esempio 285"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 285",
        grammar_point="Grammatica C1 esempio 285"
    ),
    Question(
        id=286,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-286: Questa è una domanda di esempio per il livello C1 numero 286.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 286"),
            QuestionOption(key="b", text="Risposta B esempio 286"),
            QuestionOption(key="c", text="Risposta C esempio 286"),
            QuestionOption(key="d", text="Risposta D esempio 286"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 286",
        grammar_point="Grammatica C1 esempio 286"
    ),
    Question(
        id=287,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-287: Questa è una domanda di esempio per il livello C1 numero 287.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 287"),
            QuestionOption(key="b", text="Risposta B esempio 287"),
            QuestionOption(key="c", text="Risposta C esempio 287"),
            QuestionOption(key="d", text="Risposta D esempio 287"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 287",
        grammar_point="Grammatica C1 esempio 287"
    ),
    Question(
        id=288,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-288: Questa è una domanda di esempio per il livello C1 numero 288.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 288"),
            QuestionOption(key="b", text="Risposta B esempio 288"),
            QuestionOption(key="c", text="Risposta C esempio 288"),
            QuestionOption(key="d", text="Risposta D esempio 288"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 288",
        grammar_point="Grammatica C1 esempio 288"
    ),
    Question(
        id=289,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-289: Questa è una domanda di esempio per il livello C1 numero 289.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 289"),
            QuestionOption(key="b", text="Risposta B esempio 289"),
            QuestionOption(key="c", text="Risposta C esempio 289"),
            QuestionOption(key="d", text="Risposta D esempio 289"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 289",
        grammar_point="Grammatica C1 esempio 289"
    ),
    Question(
        id=290,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-290: Questa è una domanda di esempio per il livello C1 numero 290.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 290"),
            QuestionOption(key="b", text="Risposta B esempio 290"),
            QuestionOption(key="c", text="Risposta C esempio 290"),
            QuestionOption(key="d", text="Risposta D esempio 290"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 290",
        grammar_point="Grammatica C1 esempio 290"
    ),
    Question(
        id=291,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-291: Questa è una domanda di esempio per il livello C1 numero 291.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 291"),
            QuestionOption(key="b", text="Risposta B esempio 291"),
            QuestionOption(key="c", text="Risposta C esempio 291"),
            QuestionOption(key="d", text="Risposta D esempio 291"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 291",
        grammar_point="Grammatica C1 esempio 291"
    ),
    Question(
        id=292,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-292: Questa è una domanda di esempio per il livello C1 numero 292.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 292"),
            QuestionOption(key="b", text="Risposta B esempio 292"),
            QuestionOption(key="c", text="Risposta C esempio 292"),
            QuestionOption(key="d", text="Risposta D esempio 292"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 292",
        grammar_point="Grammatica C1 esempio 292"
    ),
    Question(
        id=293,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-293: Questa è una domanda di esempio per il livello C1 numero 293.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 293"),
            QuestionOption(key="b", text="Risposta B esempio 293"),
            QuestionOption(key="c", text="Risposta C esempio 293"),
            QuestionOption(key="d", text="Risposta D esempio 293"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 293",
        grammar_point="Grammatica C1 esempio 293"
    ),
    Question(
        id=294,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-294: Questa è una domanda di esempio per il livello C1 numero 294.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 294"),
            QuestionOption(key="b", text="Risposta B esempio 294"),
            QuestionOption(key="c", text="Risposta C esempio 294"),
            QuestionOption(key="d", text="Risposta D esempio 294"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 294",
        grammar_point="Grammatica C1 esempio 294"
    ),
    Question(
        id=295,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-295: Questa è una domanda di esempio per il livello C1 numero 295.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 295"),
            QuestionOption(key="b", text="Risposta B esempio 295"),
            QuestionOption(key="c", text="Risposta C esempio 295"),
            QuestionOption(key="d", text="Risposta D esempio 295"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 295",
        grammar_point="Grammatica C1 esempio 295"
    ),
    Question(
        id=296,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-296: Questa è una domanda di esempio per il livello C1 numero 296.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 296"),
            QuestionOption(key="b", text="Risposta B esempio 296"),
            QuestionOption(key="c", text="Risposta C esempio 296"),
            QuestionOption(key="d", text="Risposta D esempio 296"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 296",
        grammar_point="Grammatica C1 esempio 296"
    ),
    Question(
        id=297,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-297: Questa è una domanda di esempio per il livello C1 numero 297.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 297"),
            QuestionOption(key="b", text="Risposta B esempio 297"),
            QuestionOption(key="c", text="Risposta C esempio 297"),
            QuestionOption(key="d", text="Risposta D esempio 297"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 297",
        grammar_point="Grammatica C1 esempio 297"
    ),
    Question(
        id=298,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-298: Questa è una domanda di esempio per il livello C1 numero 298.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 298"),
            QuestionOption(key="b", text="Risposta B esempio 298"),
            QuestionOption(key="c", text="Risposta C esempio 298"),
            QuestionOption(key="d", text="Risposta D esempio 298"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 298",
        grammar_point="Grammatica C1 esempio 298"
    ),
    Question(
        id=299,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-299: Questa è una domanda di esempio per il livello C1 numero 299.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 299"),
            QuestionOption(key="b", text="Risposta B esempio 299"),
            QuestionOption(key="c", text="Risposta C esempio 299"),
            QuestionOption(key="d", text="Risposta D esempio 299"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 299",
        grammar_point="Grammatica C1 esempio 299"
    ),
    Question(
        id=300,
        level=CEFRLevel.C1,
        section="E",
        question_text="Domanda C1-300: Questa è una domanda di esempio per il livello C1 numero 300.",
        options=[
            QuestionOption(key="a", text="Risposta A esempio 300"),
            QuestionOption(key="b", text="Risposta B esempio 300"),
            QuestionOption(key="c", text="Risposta C esempio 300"),
            QuestionOption(key="d", text="Risposta D esempio 300"),
        ],
        correct_answer="a",
        correct_answer_text="Risposta A esempio 300",
        grammar_point="Grammatica C1 esempio 300"
    ),
]

# ==========================================================================
# PLACEMENT TEST CONFIGURATION
# ==========================================================================

def get_placement_test() -> PlacementTestConfig:
    """
    Get the complete placement test configuration.
    
    Returns:
        PlacementTestConfig with all sections and questions
    """
    return PlacementTestConfig(
        name="Italian Language Placement Test",
        description="Comprehensive 50-question placement test (A1–C1) modelled on CILS, PLIDA, CLA UniTrento",
        language="Italian",
        version="2.0.0",
        sections=[
            TestSection(
                level=CEFRLevel.A1,
                section_letter="A",
                passing_score=7,
                questions=random.sample(SECTION_A_QUESTIONS, 50),
            ),
            TestSection(
                level=CEFRLevel.A2,
                section_letter="B",
                passing_score=7,
                questions=random.sample(SECTION_B_QUESTIONS, 50),
            ),
            TestSection(
                level=CEFRLevel.B1,
                section_letter="C",
                passing_score=7,
                questions=random.sample(SECTION_C_QUESTIONS, 50),
            ),
            TestSection(
                level=CEFRLevel.B2,
                section_letter="D",
                passing_score=7,
                questions=random.sample(SECTION_D_QUESTIONS, 50),
            ),
            TestSection(
                level=CEFRLevel.C1,
                section_letter="E",
                passing_score=7,
                questions=random.sample(SECTION_E_QUESTIONS, 50),
            ),
        ],
    )