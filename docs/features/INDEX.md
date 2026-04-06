# Features Index

Comprehensive documentation for ItalianOllama features.

## Core Features

### [Flashcard Review](flashcard-review.md)

Spaced repetition flashcard system with confidence-based learning:

- **SM-2 Algorithm** - Intelligent review scheduling
- **Confidence Assessment** - 3-level mastery tracking
- **Session Tracking** - Complete Neo4j integration
- **Analytics Dashboard** - Visual progress visualization

**Key Components:**
- Vocabulary list with CEFR filtering
- Add new words interface
- Flashcard review session
- Progress analytics

**Use Cases:**
- Daily vocabulary practice
- Spaced repetition review
- CEFR level preparation
- Exam preparation

### [Session Tracking](session-tracking.md)

Neo4j-based system for monitoring learning sessions:

- **Complete History** - Track all learning activities
- **Real-time Metrics** - Accuracy, words reviewed, duration
- **Analytics Dashboard** - Progress visualization
- **Spaced Repetition Integration** - Review scheduling

**Key Features:**
- Session creation and updates
- History retrieval and display
- Session metrics calculation
- Data export capabilities

**Data Models:**
- Session nodes with metrics
- Student relationships
- Timeline tracking

### [Vocabulary Learning](vocabulary/README.md)

Complete guide to the vocabulary learning system with flashcards, Neo4j session tracking, and progress analytics:

- **Flashcard Review** - Confidence-based spaced repetition
- **Vocabulary Management** - Add, organize, and search words
- **Session Tracking** - Complete progress tracking in Neo4j
- **Analytics Dashboard** - Visual progress visualization

### [Progress Tracking](progress-tracking.md)

Student progress tracking across multiple dimensions using Neo4j graph database.

- **CEFR Level** - Proficiency assessment
- **Vocabulary** - Word mastery with confidence
- **Grammar** - Error patterns and improvements
- **Exercises** - Completion history and scores
- **Streaks** - Daily practice consistency

**Metrics:**
- Vocabulary: Total, Mastered, Learning, Review Needed
- Grammar: Total errors, unique rules, improvement
- Exercises: Completed, average score, time spent

**CEFR Progression:**
- A1 → A2 → B1 → B2 → C1 → C2
- Level requirements and assessments

### [Dashboard](dashboard.md)

Streamlit-based analytics dashboard:

- **Multi-page Analytics** - Progress, vocabulary, grammar
- **Visual Charts** - Real-time data visualization
- **Real-time Data** - Neo4j integration
- **Secure Authentication** - JWT token management

**Pages:**
- Progress: CEFR level & milestones
- Vocabulary: Word mastery insights
- Grammar: Error patterns
- Knowledge Graph: Memory visualization
- Test Readiness: Exam preparation

## Getting Started

### For Students

1. **Start Learning** - Access vocabulary page from chat
2. **Add Words** - Add Italian words to your vocabulary
3. **Review Flashcards** - Use confidence-based assessment
4. **Track Progress** - Monitor your CEFR level progression
5. **Review Sessions** - Check session history and analytics

### For Developers

1. **Setup** - Configure Neo4j connection
2. **Run Frontend** - Start Streamlit dashboard
3. **Test Features** - Verify session tracking
4. **View Analytics** - Check progress visualization

## Feature Comparison

| Feature | Flashcard Review | Session Tracking | Progress Tracking | Dashboard |
|---------|-----------------|------------------|-------------------|-----------|
| **Purpose** | Vocabulary practice | Session monitoring | Progress analysis | Analytics display |
| **Input** | User confidence | System automatically | User activities | Data visualization |
| **Storage** | Neo4j Session nodes | Neo4j Session nodes | Neo4j Student/Vocabulary | Neo4j queries |
| **Output** | Review queue | Session history | CEFR level | Charts & metrics |
| **User Action** | Manual (review) | Automatic | Automatic | Visual only |

## Related Documentation

- [Architecture Overview](../architecture/overview.md)
- [Database Schema](../architecture/database.md)
- [Backend API](../api/endpoints.md)
- [Development Guide](../development/setup.md)
- [Vocabulary Documentation](../vocabulary/README.md)

## Support

- [Troubleshooting](../troubleshooting/common-issues.md)
- [FAQ](../troubleshooting/faq.md)
- [GitHub Issues](https://github.com/JonasHeinickeBio/ItalianOllama/issues)
