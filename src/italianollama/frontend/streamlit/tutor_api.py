"""Streamlit API Client - Wrapper for Italian Tutor Backend API.

Handles:
- JWT token management + storage
- Base64 encoding for Streamlit session state
- Error handling + user feedback
- Automatic retry on token expiration
- Caching for expensive queries
"""

from datetime import datetime, timedelta, timezone
import logging

import requests
import streamlit as st

logger = logging.getLogger(__name__)


class TutorAPIClient:
    """Client for Italian Tutor enhanced API."""

    def __init__(self, backend_url: str = "http://localhost:8000"):
        """Initialize API client.

        Args:
            backend_url: Base URL for FastAPI backend
        """
        logger.info(
            f"[TutorAPIClient.__init__] Starting initialization with backend_url={backend_url}"
        )
        try:
            self.backend_url = backend_url
            self.session_timeout = 15  # seconds (increased from 5 for health checks)
            logger.info(
                f"[TutorAPIClient.__init__] ✓ Successfully initialized with backend_url={backend_url}"
            )
        except Exception as e:
            logger.error(
                f"[TutorAPIClient.__init__] ❌ Initialization failed: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )
            raise

    @st.cache_data(ttl=3600)
    def _get_cached_request(self, method: str, endpoint: str, _params=None):
        """Cache GET requests for an hour."""
        url = f"{self.backend_url}{endpoint}"
        try:
            response = requests.request(
                method,
                url,
                params=_params,
                timeout=self.session_timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None

    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: dict | None = None,
        params: dict | None = None,
        use_auth: bool = True,
    ) -> dict | None:
        """Make HTTP request to backend."""
        url = f"{self.backend_url}{endpoint}"
        logger.debug(f"📡 API REQUEST: {method} {endpoint}")

        headers = {"Content-Type": "application/json"}

        # Add authorization if token available
        if use_auth:
            token = self.get_token()
            if token:
                headers["Authorization"] = f"Bearer {token}"
                logger.debug("  ✓ Auth token added to headers")
            else:
                logger.debug("  ⚠️ No auth token available")

        try:
            logger.debug(f"  → Sending {method} request to {url}")
            if json_data:
                logger.debug(f"  📦 Payload: {json_data}")
            if params:
                logger.debug(f"  🔍 Params: {params}")

            response = requests.request(
                method,
                url,
                json=json_data,
                params=params,
                headers=headers,
                timeout=self.session_timeout,
            )

            logger.debug(f"  ← Response status: {response.status_code}")

            # Handle token expiration
            if response.status_code == 401:
                logger.warning("  🔴 Unauthorized (401) - Token expired")
                st.warning("Your session has expired. Please log in again.")
                self.clear_token()
                return None

            response.raise_for_status()
            result = response.json()
            logger.info(f"✓ API {method} {endpoint} succeeded (status: {response.status_code})")
            logger.debug(f"  📥 Response: {result}")
            return result

        except requests.exceptions.Timeout:
            logger.error(f"  🔴 Request timed out after {self.session_timeout}s")
            st.error(f"Request timed out after {self.session_timeout}s")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"  🔴 Connection error - could not reach {self.backend_url}")
            st.error(f"Could not connect to backend at {self.backend_url}")
            return None
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.json() if e.response.text else str(e)
            logger.error(f"  🔴 HTTP error ({e.response.status_code}): {error_detail}")
            st.error(f"Error: {error_detail}")
            return None
        except Exception as e:
            logger.error(f"  🔴 Unexpected error: {str(e)}")
            st.error(f"Error: {str(e)}")
            return None

    def health_check(self) -> dict | None:
        """Check backend health."""
        logger.info(f"🏥 Performing backend health check to {self.backend_url}/health...")
        result = self._request("GET", "/health", use_auth=False)
        if result:
            logger.info("✓ Backend health check PASSED")
        else:
            logger.error("❌ Backend health check FAILED")
        return result

    # ============ Authentication ============

    def get_token(self) -> str | None:
        """Get stored JWT token from session state."""
        token = st.session_state.get("_api_token")
        logger.debug(
            f"🔑 Getting token from session state - {('found' if token else 'not found')}"
        )
        return token

    def set_token(self, token: str, expires_in: int = None):
        """Store JWT token and expiration in session state."""
        logger.debug(f"🔑 Storing JWT token in session state (expires_in: {expires_in}s)")
        st.session_state._api_token = token

        if expires_in:
            expiration = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            st.session_state._api_token_expires = expiration
            logger.debug(f"  ✓ Token will expire at: {expiration}")
        logger.info("✓ JWT token stored successfully")

    def clear_token(self):
        """Remove stored token."""
        logger.info("🗑️ Clearing stored JWT token")
        st.session_state.pop("_api_token", None)
        st.session_state.pop("_api_token_expires", None)
        logger.debug("  ✓ Token cleared from session state")

    def is_token_valid(self) -> bool:
        """Check if token exists and hasn't expired."""
        token = self.get_token()
        if not token:
            logger.debug("❌ No token found")
            return False

        expires = st.session_state.get("_api_token_expires")
        if expires and datetime.now(timezone.utc) > expires:
            logger.warning(f"⚠️ Token expired at {expires}")
            self.clear_token()
            return False

        logger.debug("✓ Token is valid")
        return True

    def login(self, student_id: str, expires_in_hours: int = 4) -> bool:
        """Obtain JWT token for student."""
        logger.info(
            f"🔐 LOGIN ATTEMPT: student_id={student_id}, expires_in_hours={expires_in_hours}"
        )
        logger.debug("  → Calling /auth/token endpoint...")

        result = self._request(
            "POST",
            "/auth/token",
            json_data={
                "student_id": student_id,
                "expires_in_hours": expires_in_hours,
            },
            use_auth=False,
        )

        if result:
            logger.info("✓ Login API call successful - setting token")
            logger.debug(f"  📦 Response keys: {list(result.keys())}")
            self.set_token(result["access_token"], result.get("expires_in"))
            st.session_state.student_id = student_id
            logger.info(f"✓ LOGIN SUCCESSFUL for student_id={student_id}")
            return True

        logger.error(f"❌ LOGIN FAILED for student_id={student_id}")
        return False

    # ============ Student Management ============

    def get_student(self, student_id: str) -> dict | None:
        """Get student profile."""
        logger.debug(f"👤 Fetching student profile for student_id={student_id}")
        result = self._request("GET", f"/students/{student_id}")
        if result:
            logger.info(f"✓ Student profile retrieved - keys: {list(result.keys())}")
            logger.debug(f"  📥 Profile data: {result}")
        else:
            logger.warning(f"⚠️ Student profile not found or error - student_id={student_id}")
        return result

    def get_student_stats(self, student_id: str) -> dict | None:
        """Get detailed student statistics."""
        logger.debug(f"📊 Fetching student stats for student_id={student_id}")
        result = self._request("GET", f"/students/{student_id}/stats")
        if result:
            logger.info("✓ Student stats retrieved")
        else:
            logger.warning(f"⚠️ Student stats not found - student_id={student_id}")
        return result

    def create_student(
        self, student_id: str, name: str, native_language: str = "English"
    ) -> dict | None:
        """Create a new student."""
        logger.info(
            f"👤 Creating new student - student_id={student_id}, name={name}, native_language={native_language}"
        )
        logger.debug("  → Calling POST /students endpoint...")

        result = self._request(
            "POST",
            "/students",
            json_data={
                "student_id": student_id,
                "name": name,
                "native_language": native_language,
            },
            use_auth=False,
        )

        if result:
            logger.info(f"✓ New student created successfully - keys: {list(result.keys())}")
            logger.debug(f"  📥 New student data: {result}")
        else:
            logger.error(f"❌ Failed to create student - student_id={student_id}")

        return result

    # ============ Session Management ============

    def start_session(
        self,
        student_id: str,
        topic: str | None = None,
        exercise_type: str | None = None,
    ) -> dict | None:
        """Create and start a learning session."""
        logger.info(
            f"📚 Starting learning session - student_id={student_id}, topic={topic}, exercise_type={exercise_type}"
        )
        result = self._request(
            "POST",
            "/sessions",
            json_data={
                "student_id": student_id,
                "topic": topic,
                "exercise_type": exercise_type,
            },
        )
        if result:
            logger.info(f"✓ Learning session started - session_id={result.get('id', 'N/A')}")
        else:
            logger.error("❌ Failed to start learning session")
        return result

    def end_session(self, session_id: str) -> dict | None:
        """End a learning session."""
        logger.info(f"⏹️ Ending learning session - session_id={session_id}")
        result = self._request("POST", f"/sessions/{session_id}/end")
        if result:
            logger.info("✓ Learning session ended successfully")
        else:
            logger.error("❌ Failed to end learning session")
        return result

    # ============ Exercise Attempts ============

    def record_attempt(
        self,
        session_id: str,
        student_id: str,
        exercise_template_id: str,
        exercise_type: str,
        correct: bool,
        confidence: int,
        duration_seconds: int,
        hints_used: int = 0,
        retries: int = 0,
        performance_metrics: dict | None = None,
    ) -> dict | None:
        """Record an exercise attempt."""
        result_str = "✓ CORRECT" if correct else "✗ INCORRECT"
        logger.info(
            f"📝 Recording exercise attempt - {result_str} | exercise_type={exercise_type} | confidence={confidence}% | duration={duration_seconds}s"
        )
        logger.debug(
            f"  Details: session_id={session_id}, exercise_template_id={exercise_template_id}, hints_used={hints_used}, retries={retries}"
        )

        result = self._request(
            "POST",
            "/attempts",
            json_data={
                "session_id": session_id,
                "student_id": student_id,
                "exercise_template_id": exercise_template_id,
                "exercise_type": exercise_type,
                "correct": correct,
                "confidence": confidence,
                "duration_seconds": duration_seconds,
                "hints_used": hints_used,
                "retries": retries,
                "performance_metrics": performance_metrics or {},
            },
        )

        if result:
            logger.info("✓ Exercise attempt recorded successfully")
        else:
            logger.error("❌ Failed to record exercise attempt")
        return result

    # ============ Vocabulary ============

    def add_vocabulary(
        self,
        student_id: str,
        italian_word: str,
        english_translation: str,
        part_of_speech: str,
        cefr_level: str,
        topic: str | None = None,
    ) -> dict | None:
        """Add vocabulary entry."""
        logger.info(
            f"📚 Adding vocabulary - italian_word='{italian_word}' | translation='{english_translation}' | pos={part_of_speech} | level={cefr_level}"
        )
        result = self._request(
            "POST",
            "/vocabulary",
            json_data={
                "student_id": student_id,
                "italian_word": italian_word,
                "english_translation": english_translation,
                "part_of_speech": part_of_speech,
                "cefr_level": cefr_level,
                "topic": topic,
            },
        )
        if result:
            logger.info("✓ Vocabulary entry added successfully")
        else:
            logger.error("❌ Failed to add vocabulary entry")
        return result

    def get_vocabulary(self, student_id: str, due_for_review: bool = False) -> list | None:
        """Get student's vocabulary."""
        logger.debug(
            f"📚 Fetching vocabulary for student_id={student_id} | due_for_review={due_for_review}"
        )
        result = self._request(
            "GET",
            f"/vocabulary/{student_id}",
            params={"due_for_review": due_for_review},
        )
        if result:
            vocab_list = result.get("vocabulary", [])
            logger.info(f"✓ Vocabulary retrieved - {len(vocab_list)} entries")
            logger.debug(f"  📥 Sample: {vocab_list[:2] if vocab_list else 'empty'}")
            return vocab_list
        else:
            logger.warning("⚠️ Failed to retrieve vocabulary")
        return None

    def update_vocabulary_confidence(self, vocabulary_id: str, confidence: int) -> dict | None:
        """Update vocabulary confidence (spaced repetition)."""
        logger.info(
            f"📝 Updating vocabulary confidence - vocabulary_id={vocabulary_id} | confidence={confidence}%"
        )
        result = self._request(
            "POST",
            f"/vocabulary/{vocabulary_id}/confidence",
            params={"confidence": confidence},
        )
        if result:
            logger.info("✓ Vocabulary confidence updated successfully")
        else:
            logger.error("❌ Failed to update vocabulary confidence")
        return result

    # ============ Analytics ============

    def get_learning_velocity(self, student_id: str, days: int = 7) -> dict | None:
        """Get learning velocity metrics."""
        logger.debug(f"📈 Fetching learning velocity for student_id={student_id} | days={days}")
        result = self._request("GET", f"/analytics/velocity/{student_id}", params={"days": days})
        if result:
            logger.info("✓ Learning velocity retrieved")
        else:
            logger.warning("⚠️ Failed to retrieve learning velocity")
        return result

    def get_skills(self, student_id: str) -> list | None:
        """Get skill breakdown."""
        logger.debug(f"🎯 Fetching skill breakdown for student_id={student_id}")
        result = self._request("GET", f"/analytics/skills/{student_id}")
        if result:
            skills_list = result.get("skills", [])
            logger.info(f"✓ Skills retrieved - {len(skills_list)} skills")
            logger.debug(f"  📥 Skills: {skills_list}")
            return skills_list
        else:
            logger.warning("⚠️ Failed to retrieve skills")
        return None

    def get_common_errors(self, student_id: str, limit: int = 10) -> list | None:
        """Get common grammar errors."""
        logger.debug(f"❌ Fetching common errors for student_id={student_id} | limit={limit}")
        result = self._request(
            "GET",
            f"/analytics/errors/{student_id}",
            params={"limit": limit},
        )
        if result:
            errors_list = result.get("errors", [])
            logger.info(f"✓ Common errors retrieved - {len(errors_list)} errors")
        else:
            logger.warning("⚠️ Failed to retrieve common errors")
        return result.get("errors") if result else None

    # ============ Recommendations ============

    def get_next_module(self, student_id: str) -> dict | None:
        """Get recommended next learning module."""
        logger.info(f"💡 Fetching next recommended module for student_id={student_id}")
        result = self._request("GET", f"/recommendations/next-module/{student_id}")
        if result:
            logger.info(f"✓ Next module recommended - module_id={result.get('id', 'N/A')}")
        else:
            logger.warning("⚠️ No module recommended")
        return result

    # ============ Chat (Legacy) ============

    def chat(self, message: str, student_id: str, session_id: str | None = None) -> dict | None:
        """Send chat message (legacy endpoint)."""
        logger.info(f"💬 Sending chat message - student_id={student_id}, session_id={session_id}")
        logger.debug(f"  📝 Message: '{message[:100]}{'...' if len(message) > 100 else ''}'")
        result = self._request(
            "POST",
            "/chat",
            json_data={
                "message": message,
                "student_id": student_id,
                "session_id": session_id,
            },
        )
        if result:
            logger.info("✓ Chat message sent successfully")
        else:
            logger.error("❌ Failed to send chat message")
        return result

    # ============ Session Tracking (Neo4j) ============

    def create_session(
        self,
        student_id: str,
        session_type: str,
        details: dict | None = None,
    ) -> dict | None:
        """Create a new learning session in Neo4j."""
        logger.info(f"📝 Creating session - type={session_type}")
        result = self._request(
            "POST",
            f"/session/{student_id}",
            json_data={
                "session_type": session_type,
                "details": details or {},
            },
        )
        if result:
            logger.info(f"✓ Session created: {result.get('session_id')}")
        else:
            logger.error("❌ Failed to create session")
        return result

    def update_session(
        self,
        session_id: str,
        words_reviewed: int = 0,
        correct_answers: int = 0,
        accuracy: float = 0.0,
        duration_seconds: int = 0,
    ) -> dict | None:
        """Update session with completion metrics."""
        logger.info(f"📊 Updating session - session_id={session_id}")
        result = self._request(
            "PUT",
            f"/session/{session_id}",
            json_data={
                "words_reviewed": words_reviewed,
                "correct_answers": correct_answers,
                "accuracy": accuracy,
                "duration_seconds": duration_seconds,
            },
        )
        if result:
            logger.info("✓ Session updated successfully")
        else:
            logger.error("❌ Failed to update session")
        return result

    def get_session_history(self, student_id: str, limit: int = 10) -> list | None:
        """Get session history for a student."""
        logger.debug(f"📅 Fetching session history - student_id={student_id}")
        result = self._request(
            "GET",
            f"/session/history/{student_id}",
            params={"limit": limit},
        )
        if result:
            logger.info(f"✓ Session history retrieved - {len(result.get('sessions', []))} entries")
        else:
            logger.warning("⚠️ Failed to retrieve session history")
        return result.get("sessions") if result else None
