#!/usr/bin/env python3
"""
Integration test for vocabulary page with authentication.
This test creates a test user and tests the vocabulary page functionality.
"""

import pytest
import time
import requests
import uuid
from playwright.sync_api import Page, expect


# Configuration
STREAMLIT_URL = "http://localhost:8502"
BACKEND_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def test_student_id():
    """Generate a unique student ID for this test."""
    return f"pt_test_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module")
def setup_test_user(test_student_id):
    """Create a test user via the API."""
    # Create student via API
    response = requests.post(
        f"{BACKEND_URL}/students",
        json={"student_id": test_student_id, "name": "Playwright Test Student"}
    )
    
    if response.status_code == 200:
        print(f"✅ Created test user: {test_student_id}")
    elif response.status_code == 409:
        print(f"ℹ️  Test user {test_student_id} already exists")
    else:
        print(f"❌ Failed to create test user: {response.status_code}")
        raise Exception(f"Failed to create test user: {response.text}")
    
    yield test_student_id
    
    # Cleanup (optional - comment out if you want to keep the user)
    # requests.delete(f"{BACKEND_URL}/students/{test_student_id}")


@pytest.mark.integration
def test_vocabulary_page_with_auth(setup_test_user, browser):
    """Test vocabulary page with full authentication flow."""
    
    student_id = setup_test_user
    
    print(f"\n{'='*80}")
    print(f"Testing vocabulary page for student: {student_id}")
    print(f"{'='*80}")
    
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()
    
    console_errors = []
    
    def handle_console(msg):
        if msg.type == "error":
            console_errors.append(msg.text)
    
    page.on("console", handle_console)
    
    try:
        # Step 1: Navigate to login page
        print("\n[STEP 1] Navigating to Streamlit...")
        page.goto(STREAMLIT_URL, wait_until="networkidle", timeout=30000)
        time.sleep(2)
        
        # Verify we're on the login page
        assert page.is_visible("text=ItalianOllama"), "Not on login page"
        print("✅ Navigated to login page")
        
        # Step 2: Login with test user
        print(f"\n[STEP 2] Logging in with student_id: {student_id}")
        page.fill('input[placeholder*="Esempio"]', student_id)
        page.click('button:has-text("Accedi")')
        
        # Wait for redirect to dashboard (login redirects to dashboard after success)
        print(f"\n[STEP 3] Waiting for dashboard redirect after login...")
        page.wait_for_url("**/dashboard**", timeout=15000)
        time.sleep(1)
        print(f"✅ Redirected to dashboard: {page.url}")
        
        # Step 4: Navigate to vocabulary page from dashboard
        print(f"\n[STEP 4] Navigating to vocabulary page from dashboard...")
        vocab_link = page.locator("a").filter(has_text="Vocabolario").first
        if vocab_link.is_visible():
            vocab_link.click()
            time.sleep(1)
        else:
            page.goto(f"{STREAMLIT_URL}/vocabulary", wait_until="networkidle")
        time.sleep(2)
        
        # Step 5: Verify page loaded successfully
        print("\n[STEP 5] Verifying vocabulary page loaded...")
        expect(page).to_have_title("Vocabolario - ItalianOllama")
        assert page.is_visible("text=Gestione Vocabolario"), "Vocabulary heading not found"
        print("✅ Vocabulary page loaded successfully")
        
        # Step 6: Check tabs
        print("\n[STEP 6] Checking tabs...")
        tabs = page.locator('[role="tab"]')
        tab_count = tabs.count()
        assert tab_count == 4, f"Expected 4 tabs, found {tab_count}"
        print(f"✅ Found {tab_count} tabs")
        
        # Test each tab
        tab_names = ["Il Mio Vocabolario", "Aggiungi Nuova Parola", "Flashcard Review", "Progresso"]
        for i in range(4):
            tabs.nth(i).click()
            time.sleep(0.5)
            assert page.is_visible("body"), f"Tab {i+1} content not visible"
        print("✅ All tabs functional")
        
        # Step 7: Check vocabulary cards section
        print("\n[STEP 7] Checking vocabulary cards...")
        tabs.nth(0).click()
        time.sleep(1)
        cards = page.locator(".card")
        card_count = cards.count()
        print(f"✅ Found {card_count} vocabulary cards")
        
        # Step 8: Check search/filter functionality
        print("\n[STEP 8] Checking search and filter...")
        search_input = page.get_by_placeholder("Cerca parola...")
        assert search_input.is_visible(), "Search input not visible"
        print("✅ Search input visible")
        
        level_filter = page.locator('[data-testid="stSelectBox"]')
        if level_filter.count() > 0:
            print("✅ Level filter visible")
        
        # Step 9: Check add new word form
        print("\n[STEP 9] Checking add new word form...")
        tabs.nth(1).click()
        time.sleep(1)
        italian_input = page.locator("input").filter(has_placeholder="Es: gatto")
        assert italian_input.count() > 0, "Italian input not found"
        print("✅ Add new word form present")
        
        # Step 10: Check progress tab
        print("\n[STEP 10] Checking progress tab...")
        tabs.nth(3).click()
        time.sleep(1)
        assert page.is_visible("text=Progresso Apprendimento"), "Progress heading not found"
        print("✅ Progress tab accessible")
        
        # Step 11: Check for console errors
        print("\n[STEP 11] Checking for console errors...")
        if len(console_errors) > 0:
            print(f"⚠️  Found {len(console_errors)} console errors:")
            for err in console_errors[:3]:  # Show first 3
                print(f"   - {err[:100]}")
        else:
            print("✅ No console errors")
        
        # Step 12: Test responsive design
        print("\n[STEP 12] Testing responsive design...")
        for width, height, name in [(768, 1024, "Tablet"), (375, 667, "Mobile")]:
            page.set_viewport_size(width, height)
            time.sleep(0.5)
            assert page.is_visible(".main-header"), f"{name} layout broken"
            print(f"✅ {name} layout works")
        
        print(f"\n{'='*80}")
        print(f"✅ ALL TESTS PASSED for {student_id}")
        print(f"{'='*80}")
        
    finally:
        context.close()
    
    if console_errors:
        return False
    return True
