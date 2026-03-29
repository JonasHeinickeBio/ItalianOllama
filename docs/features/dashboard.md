# Dashboard Features

The Streamlit-based analytics dashboard provides comprehensive insights into learning progress.

## Overview

Access the dashboard at `/dashboard/` after logging into the chat interface.

The dashboard features:
- Multi-page analytics
- Visual charts and graphs
- Real-time data from Neo4j
- Secure JWT authentication

## Pages

| Page | Description | URL Path |
|------|-------------|----------|
| **Progress** | CEFR level & milestones | `/dashboard/` |
| **Vocabulary** | Word mastery insights | `/dashboard/vocabulary` |
| **Grammar** | Error patterns | `/dashboard/grammar` |
| **Knowledge Graph** | Memory visualization | `/dashboard/knowledge-graph` |
| **Test Readiness** | Exam preparation | `/dashboard/test-readiness` |

## Progress Page

### Key Metrics

The main page displays:

```
┌─────────────────────────────────────────┐
│  📊 Your Progress                       │
├─────────────────────────────────────────┤
│  CEFR Level    │  B1  ████████░░  75%  │
│  Vocabulary    │  150 words           │
│  Grammar       │  23 errors           │
│  Sessions      │  15 completed        │
└─────────────────────────────────────────┘
```

### CEFR Progress

Shows progression through CEFR levels:

- **A1 → A2**: Foundation building
- **A2 → B1**: Elementary to Intermediate
- **B1 → B2**: Intermediate to Upper
- **B2 → C1**: Upper to Advanced
- **C1 → C2**: Advanced to Mastery

### Milestones

Achievements displayed as badges:
- First Lesson Completed
- 7-Day Streak
- 100 Words Learned
- A2 Level Achieved
- First Writing Exercise

## Vocabulary Page

### Confidence Overview

Shows vocabulary mastery distribution:

```
Confidence Levels:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
90-100% ████████████████████░░░░  45% (Mastered)
70-89%  ██████████████░░░░░░░░░░  30% (Learning)
50-69%  ████████░░░░░░░░░░░░░░░░░  15% (Review Needed)
<50%    ████░░░░░░░░░░░░░░░░░░░░░   8% (Struggling)
```

### Spaced Repetition Queue

Words due for review based on:
- Last practiced date
- Confidence level
- Learning curve

### Topic Distribution

Word counts by topic:
- Greetings: 25 words
- Food: 30 words
- Travel: 20 words
- Business: 15 words
- etc.

## Grammar Page

### Error Patterns

Top grammar errors displayed as chart:

```
Most Common Errors:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gender Agreement   █████████████████  8
Verb Conjugation   ████████████      6
Prepositions       ██████████        4
Article Usage      ████████          3
Word Order         ████              2
```

### Error Details

Click on any error to see:
- Example sentences
- Correct forms
- Practice recommendations

### Rule Breakdown

Grammar rules violated:
- Article agreement
- Pronoun usage
- Tense conjugation
- Subjunctive mood

## Knowledge Graph Page

### Neo4j Visualization

Interactive graph showing:

- **Student node** (center)
- **Vocabulary nodes** (connected)
- **Topic clusters** (grouped)
- **Grammar relationships**

### Features

- Zoom and pan
- Click nodes for details
- Filter by topic/confidence
- Relationship highlighting

### Data Displayed

```
Graph Statistics:
- Total nodes: 180
- Vocabulary: 150
- Topics: 12
- Relationships: 245
```

## Test Readiness Page

### Exam Readiness Scores

Shows preparedness for various exams:

| Exam | Readiness | Status |
|------|-----------|--------|
| TELC A1 | 85% | ✅ Ready |
| TELC A2 | 72% | ⚠️ Almost |
| Goethe B1 | 45% | 🔄 Keep practicing |

### Skill Breakdown

Detailed skills analysis:

```
Reading    ████████████████░░░░  80%
Writing    ██████████████░░░░░░  65%
Listening  ████████████░░░░░░░░  55%
Speaking   ██████████░░░░░░░░░░  45%
```

### Recommendations

Suggested next steps:
- Practice writing exercises
- Focus on listening comprehension
- Schedule speaking practice

## Shared Components

### KPI Row

Displays key metrics across all pages:
- Current CEFR level
- Total vocabulary
- Grammar errors
- Session count

### Confidence Table

Sortable table with:
- Word
- Translation
- Confidence score
- Last practiced
- Topic

### Radar Chart

Skill visualization:
- Vocabulary
- Grammar
- Writing
- Reading
- Listening
- Speaking

## Authentication

### Access Control

- JWT required for access
- Validates via Chainlit login
- Session persists 4 hours

### Login Flow

1. Click dashboard link in chat
2. Token validated automatically
3. Redirected to dashboard

### Logout

Click logout in sidebar to:
- Clear session
- Redirect to chat
- Require re-authentication

## Data Refresh

### Caching

Dashboard uses Streamlit caching:
- API responses cached for 5 minutes
- Manual refresh button available
- Auto-refresh on page navigation

### Real-time Updates

- Scores update after exercises
- Vocabulary updates after practice
- Progress updates immediately

## Navigation

### Sidebar

Contains:
- Student info
- Navigation menu
- Logout button
- Quick stats

### Mobile View

Responsive design works on:
- Desktop
- Tablet
- Mobile (stacked layout)

## Export Features

### Download Data

Available exports:
- Vocabulary list (CSV)
- Progress report (PDF)
- Grammar errors (CSV)

## Related Documentation

- [Chat Interface](chat-interface.md)
- [Exercise Types](exercises.md)
- [Progress Tracking](progress-tracking.md)
