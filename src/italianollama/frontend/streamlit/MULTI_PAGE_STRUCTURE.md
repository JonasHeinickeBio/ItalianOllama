# Streamlit Multi-Page App Structure

## Overview

The ItalianOllama Streamlit frontend has been refactored into a multi-page application using Streamlit's `pages/` directory structure. This provides better organization, code reusability, and cleaner navigation.

## Directory Structure

```
streamlit/
├── app_enhanced.py              # Main entry point (initializes session state)
└── pages/
    ├── 01_login.py              # 🔐 Login page (separate authentication)
    ├── 02_dashboard.py          # 📊 Dashboard (learning metrics)
    ├── 03_chat.py               # 💬 Chat with Sofia
    ├── 04_vocabulary.py         # 📝 Vocabulary management
    └── 05_settings.py           # ⚙️ User settings & profile
```

## How It Works

### 1. **Main App (`app_enhanced.py`)**
- **Purpose:** Entry point that initializes global session state
- **Behavior:** Automatically redirects to appropriate page based on authentication status
- **Session State Initialized:**
  - `student_id` - Current logged-in student ID
  - `authenticated` - Boolean authentication flag
  - `profile` - Student profile data
  - `chat_history` - Chat messages history

### 2. **Login Page (`pages/01_login.py`)**
- **Purpose:** Handles user authentication and account creation
- **Features:**
  - Backend health check
  - Login/register form with student ID
  - Automatic profile creation for new students
  - Token storage in `st.session_state`
  - Redirect to dashboard after successful login

### 3. **Dashboard Page (`pages/02_dashboard.py`)**
- **Purpose:** Main dashboard showing learning analytics
- **Features:**
  - 4 key metrics (XP, Streak, Vocabulary, Sessions)
  - Learning velocity analytics
  - Skills breakdown with progress bars
  - Common errors tracking
  - Module recommendations
  - Sidebar navigation accessible from all pages

### 4. **Chat Page (`pages/03_chat.py`)**
- **Purpose:** Chat interface with Sofia AI tutor
- **Features:**
  - Chat history persistence (in session state)
  - Real-time responses from backend
  - Clear history button
  - Character translations and feedback

### 5. **Vocabulary Page (`pages/04_vocabulary.py`)**
- **Purpose:** Vocabulary management with spaced repetition
- **Features:**
  - Three tabs: View, Add, Review
  - SM-2 spaced repetition algorithm
  - Confidence tracking
  - CEFR level management
  - Topic organization

### 6. **Settings Page (`pages/05_settings.py`)**
- **Purpose:** User profile and account settings
- **Features:**
  - Profile information display
  - Token management
  - Account statistics
  - Support and FAQ
  - Logout functionality

## Session State Persistence

**Key Feature:** User ID and authentication state persist across all pages automatically through Streamlit's session state mechanism.

```python
# Initialized in app_enhanced.py
if "student_id" not in st.session_state:
    st.session_state.student_id = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Accessible from any page
student_id = st.session_state.student_id
authenticated = st.session_state.authenticated
```

## Navigation Patterns

### 1. **Check Authentication Before Showing Content**
```python
if not st.session_state.get("authenticated"):
    st.error("❌ Non autenticato. Vai alla pagina di login.")
    if st.button("🔐 Vai al Login"):
        st.switch_page("pages/01_login.py")
    st.stop()
```

### 2. **Navigate Between Pages**
```python
if st.button("📊 Dashboard"):
    st.switch_page("pages/02_dashboard.py")
```

### 3. **Logout (Clear Session and Redirect)**
```python
if st.button("Logout"):
    api.clear_token()
    st.session_state.authenticated = False
    st.session_state.student_id = None
    st.switch_page("pages/01_login.py")
```

## Sidebar Navigation

Every page (except login) includes a consistent sidebar with:
- App logo and branding
- Current student ID
- Navigation radio buttons for page switching
- Logout button
- Page-specific controls (e.g., "Clear Chat" on chat page)

## API Client Initialization

Each page independently initializes the API client:

```python
from italianollama.frontend.streamlit.tutor_api import TutorAPIClient

backend_url = get_backend_url()  # From env or config
api = TutorAPIClient(backend_url)

# Use api methods:
api.login(student_id)
api.get_student(student_id)
api.chat(message, student_id)
```

## Caching Strategy

Each page uses `@st.cache_data()` with appropriate TTL values:

- **Profile data:** TTL=60s (changes frequently)
- **Analytics/Skills:** TTL=300s (updates every 5 min)
- **Module recommendations:** TTL=600s (updates every 10 min)

## Running the App

### Development
```bash
cd src
streamlit run italianollama/frontend/streamlit/app_enhanced.py
```

### With Custom Backend URL
```bash
BACKEND_URL=http://api.example.com:8000 streamlit run italianollama/frontend/streamlit/app_enhanced.py
```

## Benefits of Multi-Page Structure

| Aspect | Benefit |
|--------|---------|
| **Organization** | Each page has single responsibility |
| **Maintainability** | Easier to find and update page logic |
| **Reusability** | Common functions (caching, auth checks) in each page |
| **Navigation** | Clear, explicit page routing via `st.switch_page()` |
| **Session Persistence** | User ID auto-persists across page switches |
| **Scaling** | Easy to add new pages or modify existing ones |

## Troubleshooting

### Session State Lost Between Pages
**Symptom:** `student_id` becomes None after switching pages
**Solution:** Make sure session state is initialized in `app_enhanced.py` and only reset on logout

### Authentication Check Loop
**Symptom:** Page keeps redirecting to login
**Solution:** Verify that `login_student()` is setting both `authenticated=True` and `student_id` correctly

### API Calls Failing Across Pages
**Symptom:** API client works on one page but not another
**Solution:** Ensure each page re-initializes the API client with `TutorAPIClient(backend_url)`

## Future Enhancements

- [ ] Add page-specific analytics/logging
- [ ] Implement role-based page access
- [ ] Add page transition animations
- [ ] Create reusable page template components
- [ ] Add A/B testing framework for UI variants
