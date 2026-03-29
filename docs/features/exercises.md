# Exercise Types

ItalianOllama offers multiple exercise types to help students learn Italian through varied practice.

## Overview

Each exercise type targets different skills:

| Exercise | Skills | Description |
|----------|--------|-------------|
| Placement | Assessment | CEFR level assessment |
| Vocabulary | Recognition, Recall | Flashcard practice |
| Grammar | Accuracy | Error detection & correction |
| Translation | Production, Comprehension | IT↔EN translation |
| Free Writing | Production | Open writing with feedback |
| Niveau Test | Exam Prep | TELC/Goethe simulation |

## Placement Test

### Purpose

Determine the student's current CEFR level (A1-C2).

### How It Works

1. Student requests placement test
2. Sofia asks 10-15 questions
3. Questions adapt to answers
4. Final level calculated

### Question Types

- Multiple choice
- Fill in the blank
- Sentence completion
- Translation

### CEFR Levels

| Level | Description | Points |
|-------|-------------|--------|
| A1 | Beginner | 0-20 |
| A2 | Elementary | 21-40 |
| B1 | Intermediate | 41-60 |
| B2 | Upper Intermediate | 61-80 |
| C1 | Advanced | 81-90 |
| C2 | Mastery | 91-100 |

### Trigger Commands

```
Fai il test di livello
Placement test
Qual è il mio livello?
Test di placement
```

## Vocabulary Flashcards

### Purpose

Build vocabulary through spaced repetition.

### How It Works

1. Student requests vocab practice
2. Sofia presents flashcards
3. Student reveals/translates word
4. Self-assess correct/wrong
5. Confidence updated in Neo4j

### Spaced Repetition

Words appear based on:
- **Confidence < 50%**: Every session
- **Confidence 50-70%**: Every 3 days
- **Confidence 70-90%**: Every 7 days
- **Confidence > 90%**: Every 14 days

### Card Content

```
┌──────────────────────────────┐
│         PIZZA                │
│                              │
│   [Mostra] [✓ Corretto] [✗]  │
└──────────────────────────────┘

Reveal → "Pizza" (feminine noun)
```

### Topics

- Greetings & Introductions
- Numbers & Time
- Food & Dining
- Travel & Transportation
- Shopping
- Family & Relationships
- Work & Business
- Emotions & Opinions

### Trigger Commands

```
Fai vocab
Fai flashcards
Esercizi di vocabolo
Pratica il vocabolario
```

## Grammar Drills

### Purpose

Identify and correct grammar errors.

### How It Works

1. Student requests grammar practice
2. Sofia provides sentences with errors
3. Student identifies/corrects errors
4. Feedback and explanations given

### Topics Covered

- **Articles**: il, lo, la, le, i, gli, un, una
- **Nouns**: Gender (masculine/feminine), Pluralization
- **Adjectives**: Agreement, Position
- **Verbs**: Conjugation (all tenses)
- **Pronouns**: Subject, Object, Reflexive
- **Prepositions**: a, di, da, in, con, su, per
- **Word Order**: SVO, questions

### Example Exercise

```
Identify the error:

"Io ho manggiato la pizza"

Options:
A) manggiato → mangiato (spelling)
B) la pizza → il pizza (article)
C) Io → io (capitalization)

Correct: A
Explanation: Double 'g' is incorrect
```

### Trigger Commands

```
Fai grammatica
Esercizi di grammatica
Pratica la grammatica
```

## Translation Practice

### Purpose

Practice translating between Italian and English.

### How It Works

1. Student requests translation
2. Sofia gives sentence to translate
3. Student provides translation
4. Sofia evaluates and provides feedback

### Exercise Modes

**Italian → English**
```
Translate to English:
"Mi piace molto studiare l'italiano"

Your answer: I like to study Italian a lot
✓ Correct!
```

**English → Italian**
```
Translate to Italian:
"I went to the store yesterday"

Your answer: Io sono andato al negozio ieri
✓ Good! (Consider: "al" = "a + il")
```

### Difficulty Levels

| Level | Sentence Length | Complexity |
|-------|-----------------|------------|
| A1 | 3-5 words | Present tense, basic vocab |
| A2 | 5-8 words | Past tense, common vocab |
| B1 | 8-12 words | Multiple tenses |
| B2 | 12-15 words | Complex structures |
| C1+ | 15+ words | Subjunctive, advanced |

### Trigger Commands

```
Fai traduzione
Practice translation
Esercizi di traduzione
```

## Free Writing

### Purpose

Practice creative writing with AI feedback.

### How It Works

1. Student requests writing practice
2. Sofia gives a prompt
3. Student writes 50-200 words
4. Sofia provides detailed feedback

### Writing Prompts

```
Prompts by level:

A1: "Scrivi una frase su di te" (Write a sentence about yourself)
A2: "Descrivi la tua giornata tipica" (Describe your typical day)
B1: "Scrivi un'email formale a un collega"
B2: "Racconta un viaggio indimenticabile"
C1: "Scrivi la tua opinione su un tema attuale"
```

### Feedback Provided

- **Grammar corrections** with explanations
- **Vocabulary suggestions**
- **Style improvements**
- **Overall score**

### Example Feedback

```
Your text: "Io vado al mercato ogni giorno per comprare il pane."

Feedback:
✓ Good sentence structure!
Note: Consider "per comprare" → "a comprare" (purpose with "a")
Vocab: "mercato" is correct - also "supermercato"
```

### Trigger Commands

```
Scrivi qualcosa
Free writing
Esercizio di scrittura
Scrivi un testo
```

## Niveau Test (Exam Prep)

### Purpose

Prepare for official Italian exams.

### Supported Exams

| Exam | Origin | Levels |
|------|--------|--------|
| TELC | European | A1-C2 |
| Goethe | Germany | A1-C2 |
| CILS | Italy | A1-C2 |
| CELI | Italy | A1-C2 |

### How It Works

1. Student selects exam type and level
2. Timed practice test presented
3. Questions cover all sections
4. Score and readiness calculated

### Test Structure

```
TELC B1 Example:
━━━━━━━━━━━━━━━━━━━━━━━━━
Reading Comprehension  ████░░░░░░  20 min
Language Elements     ████░░░░░░  15 min
Writing               ████░░░░░░  20 min
Listening             ████░░░░░░  20 min
Speaking              ████░░░░░░  15 min
━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 90 minutes
```

### Readiness Score

Based on:
- Correct answers percentage
- Time management
- Section performance

### Trigger Commands

```
Fai un test
Exam preparation
Prepara il test Goethe
Practice for TELC
```

## Switching Exercises

### During Practice

To switch exercises mid-session:

```
Basta vocab, fai grammatica
Stop vocabulary, do grammar
Cambia esercizio
```

### Recommended Flow

For balanced practice:
1. Start with vocabulary (5-10 cards)
2. Grammar drill (5-10 questions)
3. Writing (once per session)
4. Review progress in dashboard

## Related Documentation

- [Chat Interface](chat-interface.md)
- [Dashboard](dashboard.md)
- [Progress Tracking](progress-tracking.md)
