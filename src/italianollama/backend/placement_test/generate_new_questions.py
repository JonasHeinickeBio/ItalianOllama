import random

random.seed(42)

SECTION_A_ADDITIONAL = []
SECTION_B_ADDITIONAL = []
SECTION_C_ADDITIONAL = []
SECTION_D_ADDITIONAL = []
SECTION_E_ADDITIONAL = []

for i in range(11, 61):
    SECTION_A_ADDITIONAL.append(Question(
        id=i,
        level=CEFRLevel.A1,
        section="A",
        question_text=f"Domanda A1-{i}: Questa è una domanda di esempio per il livello A1 numero {i}.",
        options=[
            QuestionOption(key="a", text=f"Risposta A esempio {i}"),
            QuestionOption(key="b", text=f"Risposta B esempio {i}"),
            QuestionOption(key="c", text=f"Risposta C esempio {i}"),
            QuestionOption(key="d", text=f"Risposta D esempio {i}"),
        ],
        correct_answer="a",
        correct_answer_text=f"Risposta A esempio {i}",
        grammar_point=f"Grammatica A1 esempio {i}"
    ))

for i in range(61, 121):
    SECTION_B_ADDITIONAL.append(Question(
        id=i,
        level=CEFRLevel.A2,
        section="B",
        question_text=f"Domanda A2-{i}: Questa è una domanda di esempio per il livello A2 numero {i}.",
        options=[
            QuestionOption(key="a", text=f"Risposta A esempio {i}"),
            QuestionOption(key="b", text=f"Risposta B esempio {i}"),
            QuestionOption(key="c", text=f"Risposta C esempio {i}"),
            QuestionOption(key="d", text=f"Risposta D esempio {i}"),
        ],
        correct_answer="a",
        correct_answer_text=f"Risposta A esempio {i}",
        grammar_point=f"Grammatica A2 esempio {i}"
    ))

for i in range(121, 181):
    SECTION_C_ADDITIONAL.append(Question(
        id=i,
        level=CEFRLevel.B1,
        section="C",
        question_text=f"Domanda B1-{i}: Questa è una domanda di esempio per il livello B1 numero {i}.",
        options=[
            QuestionOption(key="a", text=f"Risposta A esempio {i}"),
            QuestionOption(key="b", text=f"Risposta B esempio {i}"),
            QuestionOption(key="c", text=f"Risposta C esempio {i}"),
            QuestionOption(key="d", text=f"Risposta D esempio {i}"),
        ],
        correct_answer="a",
        correct_answer_text=f"Risposta A esempio {i}",
        grammar_point=f"Grammatica B1 esempio {i}"
    ))

for i in range(181, 241):
    SECTION_D_ADDITIONAL.append(Question(
        id=i,
        level=CEFRLevel.B2,
        section="D",
        question_text=f"Domanda B2-{i}: Questa è una domanda di esempio per il livello B2 numero {i}.",
        options=[
            QuestionOption(key="a", text=f"Risposta A esempio {i}"),
            QuestionOption(key="b", text=f"Risposta B esempio {i}"),
            QuestionOption(key="c", text=f"Risposta C esempio {i}"),
            QuestionOption(key="d", text=f"Risposta D esempio {i}"),
        ],
        correct_answer="a",
        correct_answer_text=f"Risposta A esempio {i}",
        grammar_point=f"Grammatica B2 esempio {i}"
    ))

for i in range(241, 301):
    SECTION_E_ADDITIONAL.append(Question(
        id=i,
        level=CEFRLevel.C1,
        section="E",
        question_text=f"Domanda C1-{i}: Questa è una domanda di esempio per il livello C1 numero {i}.",
        options=[
            QuestionOption(key="a", text=f"Risposta A esempio {i}"),
            QuestionOption(key="b", text=f"Risposta B esempio {i}"),
            QuestionOption(key="c", text=f"Risposta C esempio {i}"),
            QuestionOption(key="d", text=f"Risposta D esempio {i}"),
        ],
        correct_answer="a",
        correct_answer_text=f"Risposta A esempio {i}",
        grammar_point=f"Grammatica C1 esempio {i}"
    ))

with open("/home/jhe24/ItalianOllama/src/italianollama/backend/placement_test/new_question_bank.py", "w") as f:
    f.write('''"""
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


# ============================================================================
# SECTION A: A1 LEVEL (Questions 1-60)
# ============================================================================

SECTION_A_QUESTIONS = [
''')
    
    for q in SECTION_A_QUESTIONS + SECTION_A_ADDITIONAL:
        f.write(f'''    Question(
        id={q.id},
        level=CEFRLevel.{q.level.name},
        section="{q.section}",
        question_text="{q.question_text}",
        options=[
''')
        for opt in q.options:
            f.write(f'            QuestionOption(key="{opt.key}", text="{opt.text}"),\n')
        f.write(f'''        ],
        correct_answer="{q.correct_answer}",
        correct_answer_text="{q.correct_answer_text}",
        grammar_point="{q.grammar_point}"
    ),
''')

    f.write(''']

# ============================================================================
# SECTION B: A2 LEVEL (Questions 61-120)
# ============================================================================

SECTION_B_QUESTIONS = [
''')
    
    for q in SECTION_B_QUESTIONS + SECTION_B_ADDITIONAL:
        f.write(f'''    Question(
        id={q.id},
        level=CEFRLevel.{q.level.name},
        section="{q.section}",
        question_text="{q.question_text}",
        options=[
''')
        for opt in q.options:
            f.write(f'            QuestionOption(key="{opt.key}", text="{opt.text}"),\n')
        f.write(f'''        ],
        correct_answer="{q.correct_answer}",
        correct_answer_text="{q.correct_answer_text}",
        grammar_point="{q.grammar_point}"
    ),
''')

    f.write(''']

# ============================================================================
# SECTION C: B1 LEVEL (Questions 121-180)
# ============================================================================

SECTION_C_QUESTIONS = [
''')
    
    for q in SECTION_C_QUESTIONS + SECTION_C_ADDITIONAL:
        f.write(f'''    Question(
        id={q.id},
        level=CEFRLevel.{q.level.name},
        section="{q.section}",
        question_text="{q.question_text}",
        options=[
''')
        for opt in q.options:
            f.write(f'            QuestionOption(key="{opt.key}", text="{opt.text}"),\n')
        f.write(f'''        ],
        correct_answer="{q.correct_answer}",
        correct_answer_text="{q.correct_answer_text}",
        grammar_point="{q.grammar_point}"
    ),
''')

    f.write(''']

# ============================================================================
# SECTION D: B2 LEVEL (Questions 181-240)
# ============================================================================

SECTION_D_QUESTIONS = [
''')
    
    for q in SECTION_D_QUESTIONS + SECTION_D_ADDITIONAL:
        f.write(f'''    Question(
        id={q.id},
        level=CEFRLevel.{q.level.name},
        section="{q.section}",
        question_text="{q.question_text}",
        options=[
''')
        for opt in q.options:
            f.write(f'            QuestionOption(key="{opt.key}", text="{opt.text}"),\n')
        f.write(f'''        ],
        correct_answer="{q.correct_answer}",
        correct_answer_text="{q.correct_answer_text}",
        grammar_point="{q.grammar_point}"
    ),
''')

    f.write(''']

# ============================================================================
# SECTION E: C1 LEVEL (Questions 241-300)
# ============================================================================

SECTION_E_QUESTIONS = [
''')
    
    for q in SECTION_E_QUESTIONS + SECTION_E_ADDITIONAL:
        f.write(f'''    Question(
        id={q.id},
        level=CEFRLevel.{q.level.name},
        section="{q.section}",
        question_text="{q.question_text}",
        options=[
''')
        for opt in q.options:
            f.write(f'            QuestionOption(key="{opt.key}", text="{opt.text}"),\n')
        f.write(f'''        ],
        correct_answer="{q.correct_answer}",
        correct_answer_text="{q.correct_answer_text}",
        grammar_point="{q.grammar_point}"
    ),
''')

    f.write(''']

# ============================================================================
# PLACEMENT TEST CONFIGURATION
# ============================================================================

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
''')
