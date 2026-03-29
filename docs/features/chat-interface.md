# Chat Interface Features

The Chainlit-based chat interface is the primary way students interact with Sofia, the Italian tutor.

## Overview

The chat interface provides:
- Real-time conversation with the AI tutor
- Interactive exercise components
- Progress tracking
- Personalized learning experience

## Getting Started

### First Visit

When you first access the chat at `/chat/`:

1. **Authentication** (if enabled):
   - Sign in with Google OAuth
   - Or continue in dev mode

2. **Profile Check**:
   - If new: Student profile created
   - If returning: Load existing profile

3. **Welcome Message**:
   - Greeting in Italian
   - Current CEFR level display
   - Dashboard link

### Starting a Conversation

Try these starter phrases:

```
Ciao! (Hello!)
Voglio imparare l'italiano. (I want to learn Italian)
Cosa posso fare? (What can I do?)
```

## Exercise Commands

| Command | Italian | Exercise Type |
|---------|---------|---------------|
| `Fai vocab` | Vocabolario | Vocabulary flashcards |
| `Fai grammatica` | Grammatica | Grammar drills |
| `Fai traduzione` | Traduzione | Translation practice |
| `Scrivi` | Scrittura | Free writing |
| `Fai test` | Test | Exam preparation |
| `Livello` | Livello | CEFR placement test |

## Interactive Components

### Vocabulary Flashcards

**Trigger:** `Fai vocab` or `Fai flashcards`

**Features:**
- Shows Italian word
- Reveal button to show translation
- Correct/Wrong buttons for self-assessment
- Updates confidence in Neo4j

**Example:**
```
┌─────────────────────────┐
│      PIZZA             │
│                         │
│   [Reveal] [✓] [✗]     │
└─────────────────────────┘
```

### Grammar Feedback

**Trigger:** `Fai grammatica` or submit text with errors

**Features:**
- Shows original text
- Highlights errors inline
- Provides corrections
- Explains the grammar rule

**Example:**
```
Original: "Io sono andato al mercato"
Corrected: "Io sono andata al mercato" ⚠️
Error: Gender agreement - "andato" → "andata"
Rule: adjectives must match noun gender
```

### Placement Quiz

**Trigger:** `Fai il test di livello` or `Placement test`

**Features:**
- Multiple choice questions
- Progress bar
- Adaptive difficulty
- CEFR result at end

**Levels:**
- A1: Beginner
- A2: Elementary
- B1: Intermediate
- B2: Upper Intermediate
- C1: Advanced
- C2: Mastery

### Writing Review

**Trigger:** `Scrivi qualcosa` or submit free writing

**Features:**
- AI feedback on writing
- Error highlighting
- Vocabulary suggestions
- Improvement tips

### Score Badge

**Displayed after:** Any exercise completion

**Levels:**
- ⭐⭐⭐ Excellent (90%+)
- ⭐⭐ Good (70-89%)
- ⭐ Fair (50-69%)
- Keep practicing (<50%)

## Conversation Flow

### Standard Flow

```
User: Ciao!
Sofia: Ciao! Come stai? Ready to learn Italian?

User: Voglio fare vocab
Sofia: [DrillCard Component]
User: [Interacts with flashcard]
Sofia: Ottimo! Word learned. Try another?

User: Mostra il mio progresso
Sofia: Your progress:
- CEFR Level: B1
- Vocabulary: 150 words
- Grammar errors: 12
```

### Adaptive Learning

Sofia adjusts based on:
- **CEFR Level**: Vocabulary difficulty
- **Past Errors**: Grammar focus areas
- **Spaced Repetition**: Review timing
- **Session History**: Exercise variety

## User Interactions

### Buttons

All interactive elements support:
- **Click**: Primary action
- **Hover**: Tooltip info
- **Keyboard**: Tab navigation

### Chat Features

| Feature | Description |
|---------|-------------|
| **Streaming** | Responses appear in real-time |
| **Markdown** | Italic, bold, lists supported |
| **Code Blocks** | For grammar examples |
| **Emojis** | Visual feedback ⭐🔤📝 |
| **Links** | To dashboard |

## Profile Management

### View Profile

```
User: Mostrami il mio profilo
Sofia: Your profile:
- Name: John
- Level: B1
- Sessions: 15
- Member since: Jan 2024
```

### Change Level

```
User: Voglio cambiare livello
Sofia: I'll reassess your level. Answer these questions...
[Placement Quiz]
Sofia: Your new level: B2!
```

## Tips for Best Experience

1. **Be Consistent** - Regular practice helps spaced repetition
2. **Try All Exercises** - Different types reinforce learning
3. **Read Feedback** - Grammar explanations improve understanding
4. **Check Dashboard** - Analytics show overall progress
5. **Don't Rush** - Take time with each exercise

## Troubleshooting

### Component Not Rendering

If interactive components don't appear:
- Check browser console for errors
- Verify WebSocket connection
- Refresh the page

### Chat Not Responding

If Sofia doesn't respond:
- Check API health: `/health`
- Verify LLM connection
- Check Neo4j connection

### Stuck in Exercise

To exit any exercise:
- Type: `Basta` (Enough)
- Type: `Cambia argomento` (Change topic)
- Type: `Aiuto` (Help)

## Related Documentation

- [Dashboard Features](dashboard.md)
- [Exercise Types](exercises.md)
- [Progress Tracking](progress-tracking.md)
