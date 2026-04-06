"""
Playwright integration tests for the vocabulary page.
Tests all major functionality including tabs, flashcards, search, and progress tracking.
"""

import pytest
import time
from pathlib import Path
from playwright.sync_api import Page, expect, Playwright


BASE_URL = "http://localhost:8502"


@pytest.fixture(scope="module")
def browser_context(browser):
    """Create browser context with consistent viewport."""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
    )
    yield context
    context.close()


@pytest.fixture(scope="module")
def page_context(browser_context):
    """Create a new page for testing."""
    page = browser_context.new_page()
    yield page
    page.close()


class TestVocabularyPage:
    """Test suite for vocabulary page functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Navigate to vocabulary page before each test."""
        # Navigate directly to the vocabulary page
        page.goto(f"{BASE_URL}")
        
        # Wait for Streamlit app to load
        page.wait_for_function("document.querySelector('#root') && document.querySelector('#root').innerHTML.length > 0", timeout=15000)
        
        # Wait for vocabulary page specific elements (tabs, header, etc.)
        page.wait_for_selector('[data-testid="stVerticalBlock"]', timeout=15000)
        
        # Wait for page to fully render
        page.wait_for_timeout(2000)

    def test_page_loads_successfully(self, page: Page):
        """Test that vocabulary page loads and shows authentication requirement."""
        # The vocabulary page should require authentication
        # Check for authentication error message
        expect(page.locator("text=Non autenticato")).to_be_visible()
        
        # Check for login button
        expect(page.locator("text=Vai al Login")).to_be_visible()
        
        # Verify page has loaded (has content)
        body_text = page.locator("body").inner_text()
        assert len(body_text) > 0, "Body should have content"

    def test_all_tabs_accessible(self, page: Page):
        """Test that all tabs are accessible and functional."""
        # Wait for tabs to load
        page.wait_for_selector('[role="tablist"]', timeout=10000)
        
        # Get all tabs
        tabs = page.locator('[role="tab"]')
        tab_count = tabs.count()
        
        assert tab_count == 4, f"Expected 4 tabs, found {tab_count}"
        
        # Test each tab
        tab_names = [
            "Il Mio Vocabolario",
            "Aggiungi Nuova Parola", 
            "Flashcard Review",
            "Progresso"
        ]
        
        for i, expected_name in enumerate(tab_names):
            tab = tabs.nth(i)
            expect(tab).to_be_visible()
            
            # Click tab and verify content
            tab.click()
            time.sleep(1)
            
            # Check that content changes
            content_found = False
            try:
                page.wait_for_selector("text=.*", timeout=5000)
                content_found = True
            except:
                pass
            
            assert content_found, f"Tab {i+1} ({expected_name}) did not load content"

    def test_vocabulary_tabs_content(self, page: Page):
        """Test content of each vocabulary tab."""
        tabs = page.locator('[role="tab"]')
        
        # Tab 1: My Vocabulary
        tabs.nth(0).click()
        time.sleep(1)
        expect(page.locator("text=Il mio Vocabolario")).to_be_visible()
        expect(page.get_by_text("Cerca parola...")).to_be_visible()
        
        # Tab 2: Add New Word
        tabs.nth(1).click()
        time.sleep(1)
        expect(page.locator("text=Aggiungi Nuova Parola")).to_be_visible()
        expect(page.get_by_placeholder("Es: gatto")).to_be_visible()
        
        # Tab 3: Flashcard Review
        tabs.nth(2).click()
        time.sleep(1)
        expect(page.locator("text=Flashcard Review Session")).to_be_visible()
        
        # Tab 4: Progress
        tabs.nth(3).click()
        time.sleep(1)
        expect(page.locator("text=Progresso Apprendimento")).to_be_visible()

    def test_search_filter_functionality(self, page: Page):
        """Test search and filter functionality."""
        # Go to My Vocabulary tab
        page.locator('[role="tab"]').nth(0).click()
        time.sleep(1)
        
        # Check filter dropdown exists
        level_filter = page.locator('[data-testid="stSelectBox"]')
        expect(level_filter).to_be_visible()
        
        # Check search input exists
        search_input = page.get_by_placeholder("Cerca parola...")
        expect(search_input).to_be_visible()
        
        # Test search with empty input (should show all)
        search_input.fill("")
        time.sleep(0.5)
        
        # Test search with a term (if any vocabulary exists)
        search_input.fill("test")
        time.sleep(0.5)

    def test_add_new_vocabulary_form(self, page: Page):
        """Test the add new vocabulary form."""
        # Navigate to Add New Word tab
        page.locator('[role="tab"]').nth(1).click()
        time.sleep(1)
        
        # Check form fields exist
        expect(page.get_by_placeholder("Es: gatto")).to_be_visible()
        expect(page.get_by_placeholder("Es: cat")).to_be_visible()
        expect(page.get_by_text("Parte del discorso")).to_be_visible()
        expect(page.get_by_text("Livello CEFR")).to_be_visible()
        
        # Check submit button
        submit_button = page.get_by_text("Aggiungi Parola")
        expect(submit_button).to_be_visible()
        expect(submit_button).to_be_enabled()

    def test_vocabulary_cards_display(self, page: Page):
        """Test that vocabulary cards display with CEFR levels."""
        page.locator('[role="tab"]').nth(0).click()
        time.sleep(1)
        
        # Check for vocabulary cards if any exist
        cards = page.locator(".card")
        card_count = cards.count()
        
        if card_count > 0:
            # Check first card has CEFR level badge
            first_card = cards.nth(0)
            
            # Look for CEFR level badge
            badges = first_card.locator(".badge")
            badge_count = badges.count()
            
            if badge_count > 0:
                badge_text = badges.nth(0).inner_text()
                assert badge_text in ["A1", "A2", "B1", "B2", "C1", "C2", "N/A"], \
                    f"Unexpected badge text: {badge_text}"

    def test_cefr_level_filter(self, page: Page):
        """Test CEFR level filtering."""
        page.locator('[role="tab"]').nth(0).click()
        time.sleep(1)
        
        level_select = page.locator("select").filter(has_text="Livello").first
        if level_select.is_visible():
            options = level_select.locator("option")
            option_count = options.count()
            
            assert option_count >= 1, "Should have at least one CEFR level option"

    def test_responsive_design(self, page: Page):
        """Test responsive design with different viewport sizes."""
        test_viewports = [
            {"width": 1920, "height": 1080, "name": "Desktop"},
            {"width": 768, "height": 1024, "name": "Tablet"},
            {"width": 375, "height": 667, "name": "Mobile"},
        ]
        
        for viewport in test_viewports:
            page.set_viewport_size(viewport["width"], viewport["height"])
            time.sleep(1)
            
            # Check page loads at this size
            expect(page.locator(".main-header")).to_be_visible()
            
            # Check tabs are visible
            tabs = page.locator('[role="tablist"]')
            expect(tabs).to_be_visible()

    def test_progress_tab_statistics(self, page: Page):
        """Test progress tab displays statistics correctly."""
        page.locator('[role="tab"]').nth(3).click()
        time.sleep(1)
        
        # Check for statistics section
        expect(page.locator("text=Statist Generali")).to_be_visible()
        
        # Check for metric cards
        metric_cards = page.locator(".metric-card")
        metric_count = metric_cards.count()
        
        # Should have at least some metric cards
        assert metric_count >= 1, "Should display at least one metric card"

    def test_no_console_errors(self, page: Page):
        """Test that no JavaScript errors occur."""
        console_errors = []
        
        def handle_console(msg):
            if msg.type == "error":
                console_errors.append(msg)
        
        page.on("console", handle_console)
        
        # Navigate through all tabs
        for i in range(4):
            page.locator('[role="tab"]').nth(i).click()
            time.sleep(1)
        
        # Check for errors
        assert len(console_errors) == 0, \
            f"Console errors found: {[e.text for e in console_errors]}"


class TestVocabularyPageEmptyState:
    """Test vocabulary page when no vocabulary exists."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Navigate to vocabulary page."""
        page.goto(f"{BASE_URL}")
        page.wait_for_function("document.querySelector('#root') && document.querySelector('#root').innerHTML.length > 0", timeout=15000)
        page.wait_for_timeout(2000)

    def test_empty_state_displayed(self, page: Page):
        """Test empty state message when no vocabulary."""
        page.locator('[role="tab"]').nth(0).click()
        time.sleep(1)
        
        # Check for empty state message
        empty_state = page.locator(".empty-state")
        
        # Should show "Ancora nessuna parola" or similar
        expect(empty_state).to_be_visible()


class TestVocabularyPageNavigation:
    """Test navigation between vocabulary page and other pages."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Navigate to vocabulary page before test."""
        page.goto(f"{BASE_URL}")
        page.wait_for_function("document.querySelector('#root') && document.querySelector('#root').innerHTML.length > 0", timeout=15000)
        page.wait_for_timeout(2000)

    def test_page_url(self, page: Page):
        """Test that vocabulary page is accessible."""
        # Already navigated to vocabulary page in setup
        expect(page).to_have_url(f"{BASE_URL}/")
        
        # Check that we're on the vocabulary page
        page.wait_for_selector('[data-testid="stVerticalBlock"]', timeout=10000)
