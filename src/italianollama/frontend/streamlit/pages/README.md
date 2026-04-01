# Streamlit Pages - Multi-Page Application

## Directory Contents

- **`__init__.py`** - Package initialization
- **`utils.py`** - Shared utilities and helper functions (NEW!)
- **`01_login.py`** - Login page with authentication
- **`02_dashboard.py`** - Main dashboard with analytics
- **`03_chat.py`** - Chat interface with Sofia
- **`04_vocabulary.py`** - Vocabulary management with spaced repetition
- **`05_settings.py`** - User settings and profile management

## Key Improvements (v0.3.1)

### ✅ Code Cleanup
- Removed old duplicate pages (`0_💬_Chat.py`, `1_📊_Progress.py`, etc.)
- Removed emoji-based file naming (problematic across platforms)
- Consistent numeric prefix for page ordering

### ✅ Shared Utilities (`utils.py`)
New centralized utility module providing:
- **API Initialization:** `get_api_client()`, `get_backend_url()`
- **Session Management:** `initialize_session_state()`, `get_student_id()`
- **Authentication Guards:** `require_auth()`, `logout()`
- **Sidebar Components:** `render_sidebar_full()`, `render_sidebar_navigation()`
- **UI Components:** `metric_card()`, `skill_progress_bar()`, `error_card()`
- **Caching:** `cache_student_data()` decorator
- **Error Handling:** `handle_api_error()`, `with_error_handling()` decorator
- **Status Checks:** `check_backend_health()`

### ✅ Enhanced Error Handling
- Try-catch blocks around all API calls
- Graceful degradation when data unavailable
- User-friendly error messages
- Backend health checks before operations

### ✅ Improved UX
- **Better Form Layouts:** Multi-column forms in vocabulary
- **Rich Feedback:** Success messages, spinners, balloons
- **Search Functionality:** Added vocabulary search on Tab 1
- **Better Organization:** Consistent tabs, expanders, containers
- **Example Sentences:** Users can add context for vocabulary
- **Feedback Buttons:** Chat page feedback mechanism
- **Comprehensive FAQ:** Detailed answers to common questions

### ✅ Consistent Patterns
- All pages follow same structure:
  1. Page config
  2. Authentication check
  3. Sidebar rendering
  4. API initialization
  5. Content sections
  6. Page navigation footer
- Uniform import pattern from `utils`
- Consistent color/emoji usage across pages

## Usage Examples

### Using Utilities in a Page

```python
import streamlit as st
from utils import (
    get_api_client,
    get_student_id,
    require_auth,
    render_sidebar_full,
    render_page_navigation,
)

# Page setup
st.set_page_config(page_title="My Page", page_icon="📄", layout="wide")

# Check auth and get student ID
require_auth()
student_id = get_student_id()

# Render sidebar
render_sidebar_full("📄 My Page")

# Get API
api = get_api_client()

# Your page logic...

# Footer navigation
render_page_navigation("📄 My Page")
```

### Cached Data Pattern

```python
@st.cache_data(ttl=300)
def get_my_data():
    """Fetch and cache data."""
    try:
        return api.get_data(student_id)
    except Exception as e:
        st.error(f"Errore: {str(e)}")
        return None
```

### Error Handling Pattern

```python
with st.spinner("Loading..."):
    try:
        result = api.some_operation()
        if result:
            st.success("✅ Success!")
        else:
            st.error("❌ Failed")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
```

## Performance Optimizations

1. **Caching with TTL:** Different TTLs for different data types
   - Profile: 60s (changes frequently)
   - Analytics: 300s (updates every 5 min)
   - Recommendations: 600s (updates every 10 min)

2. **API Client Singleton:** Shared across all pages via session state

3. **Lazy Loading:** Data only fetched when needed

4. **Search Optimization:** Filter results client-side

## Session State Flow

```
app_enhanced.py initializes:
├── student_id (None initially)
├── authenticated (False initially)
├── profile (None initially)
├── chat_history ([])
└── api_client (None, lazy-initialized)

Login page:
└── Sets student_id + authenticated + profile

All other pages:
├── Access student_id from session state
├── Access api_client from session state
└── Render with persistent user context
```

## Adding a New Page

1. Create file `XX_page_name.py` in pages/ directory
2. Follow the standard structure:
   ```python
   import streamlit as st
   from utils import require_auth, render_sidebar_full, render_page_navigation

   st.set_page_config(...)
   require_auth()
   render_sidebar_full("📄 Page Name")

   # Your content here

   render_page_navigation("📄 Page Name")
   ```
3. Streamlit auto-discovers and adds to navigation

## Troubleshooting

### Session State Issues
- Clear browser cache if student_id disappears
- Check `utils.initialize_session_state()` is called in login

### API Errors
- Verify backend is running: `curl http://localhost:8000/health`
- Check network connection
- See error details in try-catch blocks

### Performance
- Adjust TTL values in `@st.cache_data(ttl=X)`
- Use search filters before rendering large lists
- Clear cache with `st.cache_data.clear()` if needed

## Future Enhancements

- [ ] Add page transition animations
- [ ] Implement analytics tracking per page
- [ ] Add dark mode support
- [ ] Create reusable page template components
- [ ] Add A/B testing framework
- [ ] Implement role-based page access
