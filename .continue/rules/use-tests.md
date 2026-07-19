---
description: llm guide for the testing system
---

# D&D Tabletop Testing Suite - LLM Instruction Guide

## Overview

This is a comprehensive pytest-based test suite for the D&D Tabletop Django application. It provides automated testing coverage for all major features including authentication, campaigns, characters, chat, dice rolling, and admin functionality.

---

## Test Suite Architecture

### Directory Structure
```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── pytest.ini               # Pytest settings with coverage config
├── run_tests.py             # Test runner script
├── README.md                # Human-readable documentation
├── TESTING_SUMMARY.md       # Overview of test coverage
├── QUICK_REFERENCE.md       # Quick command reference
├── test_basic_setup.py      # Infrastructure validation tests
├── test_urls.py            # URL resolution tests (30+ routes)
├── test_authentication.py  # Login, logout, permissions
├── test_campaigns.py       # Campaign CRUD and member management
├── test_characters.py      # Character creation, editing, inventory
├── test_chat_and_dice.py   # Chat messages and dice rolling APIs
└── test_admin.py           # Admin user management features
```

---

## Core Fixtures (conftest.py)

### Available Fixtures for All Tests

#### 1. `db_setup` - Pre-populated Test Database
**Purpose:** Provides ready-to-use test data with proper relationships

**Returns Dictionary With:**
- `superuser`: Admin user (username='admin')
- `regular_user`: Regular player (username='player1')  
- `another_user`: Second player (username='player2')
- `campaign`: Test campaign ("Test Campaign")
- `character`: Test character owned by regular_user

**Usage Example:**
```python
def test_feature(self, db_setup):
    campaign = db_setup['campaign']
    user = db_setup['regular_user']
    
    # Use these objects in your test
    response = client.get(...)
```

#### 2. `client_auth` - Authenticated Test Client
**Purpose:** HTTP client logged in as regular user (player1)

**Use When:** Testing views that require authentication but not admin privileges

**Usage Example:**
```python
def test_authenticated_view(self, client_auth):
    response = client_auth.get('/protected-url/')
    assert response.status_code == 200
```

#### 3. `admin_client` - Superuser Test Client  
**Purpose:** HTTP client logged in as superuser (admin)

**Use When:** Testing admin-only views and features

**Usage Example:**
```python
def test_admin_view(self, admin_client):
    response = admin_client.get('/admin-url/')
    assert response.status_code == 200
```

#### 4. `client` - Unauthenticated Test Client
**Purpose:** HTTP client with no login (built-in pytest-django fixture)

**Use When:** Testing public views or authentication flows

**Usage Example:**
```python
def test_public_view(self, client):
    response = client.get('/public-url/')
    assert response.status_code == 200
```

---

## Test Module Breakdown

### 1. `test_basic_setup.py` - Infrastructure Validation
**Purpose:** Verify testing infrastructure works correctly

**Tests Include:**
- Pytest is running properly
- Django settings loaded
- Database fixture creates data correctly
- Authenticated clients work
- Models are importable

**When to Run:** Always run these first when setting up or debugging the test environment

---

### 2. `test_urls.py` - URL Resolution Testing  
**Purpose:** Ensure all 30+ URL routes resolve correctly and map to views

**Coverage:**
- Authentication URLs (login, logout, password change)
- Campaign URLs (create, detail, delete)
- Character URLs (create, edit, delete, inventory)
- Chat/Dice API endpoints
- Admin URLs (user management, campaign list)
- Member management URLs

**When to Run:** After any URL configuration changes or when adding new routes

---

### 3. `test_authentication.py` - Auth & Permissions
**Purpose:** Test login/logout flows and permission-based access control

**Coverage:**
- Login page accessibility
- Successful/failed login attempts
- Logout functionality
- Password change (voluntary and forced)
- Permission checks (admin vs regular user)
- Access to admin pages without privileges
- Campaign membership requirements

**Key Test Patterns:**
```python
# Test permission denied
def test_requires_permission(self, client_auth):
    response = client_auth.get('/admin-url/')
    assert response.status_code in [301, 302, 403]

# Test admin access allowed  
def test_admin_can_access(self, admin_client):
    response = admin_client.get('/admin-url/')
    assert response.status_code == 200
```

---

### 4. `test_campaigns.py` - Campaign Management
**Purpose:** Test campaign CRUD operations and member management

**Coverage:**
- Campaign creation (requires title, not name)
- Campaign detail view (membership required)
- Campaign deletion (DM or admin only)
- Member management (add, remove, leave)
- DM roster access
- Rule book functionality
- Personal notebook access

**Important Model Field Names:**
- `Campaign.title` (NOT 'name')
- `CampaignMembership.role = 'PLAYER'` (NOT 'player')
- Use `CampaignMembership.objects.filter(...)` for lookups

---

### 5. `test_characters.py` - Character Management  
**Purpose:** Test character creation, editing, and inventory

**Coverage:**
- Character creation (requires name, class_name)
- Character detail view
- Character editing (owner or DM only)
- Character deletion
- Inventory item addition
- Permission checks (owner-only operations)

**Important Model Field Names:**
- `Character.class_name` (NOT 'class_type')
- `Character.user` (NOT 'owner')
- `InventoryItem.name` (NOT 'item_name')

---

### 6. `test_chat_and_dice.py` - Chat & Dice APIs
**Purpose:** Test real-time messaging and dice rolling functionality

**Coverage:**
- Get chat messages API endpoint
- Post chat message (with HTML content)
- Message editing (owner or DM only)
- Message deletion (owner or DM only)
- Dice roll posting
- Visibility controls (public, DM-only, whispers)
- Membership requirements for posting

**API Endpoints Tested:**
- `/campaign/<pk>/chat/messages/` - GET messages
- `/campaign/<pk>/chat/post/` - POST message
- `/chat/message/<pk>/edit/` - POST edit
- `/chat/message/<pk>/delete/` - POST delete  
- `/campaign/<pk>/dice/post/` - POST dice roll

---

### 7. `test_admin.py` - Admin Features
**Purpose:** Test superuser-only functionality

**Coverage:**
- User list (superuser only)
- Create new user
- Delete user (cannot delete self)
- Admin campaign list
- Database reset
- Secret whisper viewing
- DM feature access for admins

---

## Running Tests - LLM Commands

### Basic Test Execution

```bash
# Run all tests with verbose output
pytest tests/ -v

# Using the test runner script
python tests/run_tests.py

# Run specific test file
pytest tests/test_authentication.py -v

# Run specific test class
pytest tests/test_campaigns.py::TestCampaignCreation -v

# Run single test function
pytest tests/test_urls.py::TestURLResolution::test_login_url_resolves -v
```

### With Coverage Reporting

```bash
# Terminal coverage with missing lines
pytest --cov=campaigns --cov-report=term-missing tests/

# HTML coverage report
pytest --cov=campaigns --cov-report=html tests/
# View: tests/coverage_html/index.html

# XML for CI/CD integration  
pytest --cov=campaigns --cov-report=xml tests/
```

### Debug Mode

```bash
# Drop into Python debugger on failure
pytest tests/test_basic_setup.py -v --pdb

# Show print statements and logs
pytest tests/ -v -s

# Stop at first failure
pytest tests/ -v --maxfail=1
```

---

## Writing New Tests - LLM Guidelines

### Standard Test Pattern

```python
import pytest
from django.urls import reverse
from campaigns.models import Campaign, Character  # Import needed models

class TestFeatureName:
    """Describe what feature you're testing."""
    
    def test_specific_behavior(self, client_auth, db_setup):
        """Test specific behavior with clear description."""
        
        # ARRANGE - Set up test data
        campaign = db_setup['campaign']
        user = db_setup['regular_user']
        
        # ACT - Perform the action being tested
        response = client_auth.post(
            reverse('campaigns:create_campaign'),
            {'title': 'New Campaign', 'description': 'Test'}
        )
        
        # ASSERT - Verify expected outcome
        assert response.status_code in [301, 302]  # Redirect after create
        assert Campaign.objects.filter(title='New Campaign').exists()
```

### Key Principles for LLMs

1. **Always Use `reverse()` for URLs**
   ```python
   # ✅ CORRECT
   url = reverse('campaigns:campaign_detail', kwargs={'pk': campaign.id})
   
   # ❌ WRONG - Don't hardcode URLs
   response = client.get('/campaign/1/')
   ```

2. **Use Correct Model Field Names** (CRITICAL!)
   ```python
   # ✅ CORRECT field names from models.py
   Campaign.title          # NOT 'name'
   Character.class_name    # NOT 'class_type'  
   Character.user          # NOT 'owner'
   CampaignMembership.role = 'PLAYER'  # NOT 'player'
   InventoryItem.name      # NOT 'item_name'
   ```

3. **Test Both Success and Failure Cases**
   ```python
   def test_success_case(self, client_auth, db_setup):
       """When user has permission, action succeeds."""
       response = client_auth.post(...)
       assert response.status_code == 200
   
   def test_permission_denied(self, client_auth):
       """When user lacks permission, access denied."""
       response = client_auth.get('/admin-url/')
       assert response.status_code in [301, 302, 403]
   ```

4. **Use Fixtures Appropriately**
   - `db_setup` → Need pre-existing data (campaigns, users, characters)
   - `client_auth` → Testing as regular authenticated user
   - `admin_client` → Testing admin/superuser features
   - `client` → Testing unauthenticated/public views

5. **Check Redirects Properly**
   ```python
   # After POST that creates/updates/deletes, expect redirect
   assert response.status_code in [301, 302]
   
   # For GET requests that should succeed
   assert response.status_code == 200
   
   # For permission denied scenarios  
   assert response.status_code in [301, 302, 403, 404]
   ```

---

## Common Test Scenarios for LLMs

### Creating Resources
```python
def test_create_resource(self, client_auth):
    """Test successful resource creation."""
    response = client_auth.post(
        reverse('campaigns:create_campaign'),
        {'title': 'New Campaign', 'description': 'Test'}
    )
    
    assert response.status_code in [301, 302]
    assert Campaign.objects.filter(title='New Campaign').exists()
```

### Updating Resources  
```python
def test_update_resource(self, client_auth, db_setup):
    """Test successful resource update."""
    character = db_setup['character']
    
    response = client_auth.post(
        reverse('campaigns:edit_character', kwargs={'pk': character.id}),
        {'name': 'Updated Name', 'class_name': 'Wizard', 'level': 2}
    )
    
    assert response.status_code in [301, 302]
    character.refresh_from_db()
    assert character.name == 'Updated Name'
```

### Deleting Resources
```python
def test_delete_resource(self, client_auth, db_setup):
    """Test successful resource deletion."""
    character = db_setup['character']
    
    response = client_auth.post(
        reverse('campaigns:delete_character', kwargs={'pk': character.id})
    )
    
    assert response.status_code in [301, 302]
    assert not Character.objects.filter(id=character.id).exists()
```

### Testing Permissions
```python
def test_requires_admin(self, client_auth):
    """Regular users cannot access admin features."""
    response = client_auth.get(reverse('campaigns:admin_user_list'))
    assert response.status_code in [301, 302, 403]

def test_admin_can_access(self, admin_client):
    """Admins can access admin features."""
    response = admin_client.get(reverse('campaigns:admin_user_list'))
    assert response.status_code == 200
```

### Testing API Endpoints (JSON)
```python
def test_post_json_api(self, client_auth, db_setup):
    """Test posting to JSON API endpoint."""
    campaign = db_setup['campaign']
    
    response = client_auth.post(
        reverse('campaigns:post_message', kwargs={'pk': campaign.id}),
        {'content': 'Hello!', 'message_type': 'OOC_RELEVANT'},
        content_type='application/json'
    )
    
    assert response.status_code in [200, 201]
    data = response.json()
    assert data.get('success') == True
```

---

## Troubleshooting Guide for LLMs

### Common Issues & Solutions

#### Issue: "User is not defined" Error
**Cause:** Missing import in test file  
**Solution:** Add to top of file:
```python
from django.contrib.auth import get_user_model
User = get_user_model()
```

#### Issue: Import Errors or Module Not Found
**Cause:** Django settings not loaded  
**Solution:** Ensure pytest.ini has correct DJANGO_SETTINGS_MODULE:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = dnd_app.settings
```

#### Issue: Database Errors
**Cause:** Migrations not applied or database issues  
**Solution:** 
```bash
python manage.py migrate
# Then run tests again
```

#### Issue: Test Fails with 403 Forbidden
**Cause:** Permission check failing (expected in some tests)  
**Solution:** Verify this is the intended behavior. If testing permission denial, assert it's expected:
```python
assert response.status_code == 403  # Expected for unauthorized access
```

#### Issue: Field Name Errors (e.g., 'Campaign has no field name')
**Cause:** Using wrong model field names  
**Solution:** Check models.py for correct field names. Common mistakes:
- Use `title` not `name` for Campaign
- Use `class_name` not `class_type` for Character
- Use `user` not `owner` for Character
- Use `'PLAYER'` not `'player'` for role

#### Issue: Tests Pass Locally but Fail in CI/CD
**Cause:** Different database or environment settings  
**Solution:** Ensure pytest uses in-memory database (configured in settings.py)

---

## Best Practices for LLMs

### 1. Test Isolation
- Each test should be independent
- Don't rely on other tests running first
- Use fixtures for fresh data each time

### 2. Descriptive Test Names
```python
# ✅ GOOD - Clear what's being tested
def test_cannot_delete_self_as_admin(self, admin_client, db_setup):

# ❌ BAD - Vague
def test_delete_test(self, admin_client):
```

### 3. Assert Specific Outcomes
```python
# ✅ GOOD - Specific assertion
assert Campaign.objects.filter(title='New Campaign').exists()

# ❌ BAD - Too general  
assert True
```

### 4. Test Edge Cases
- Empty inputs
- Invalid data
- Permission boundaries
- Concurrent access scenarios (if applicable)

### 5. Use Appropriate HTTP Methods
```python
# GET for reading
response = client_auth.get(url)

# POST for creating/updating/deleting  
response = client_auth.post(url, data)

# PUT/PATCH for partial updates (if implemented)
```

---

## When to Add New Tests - LLM Decision Tree

### ✅ ADD TESTS WHEN:
- Adding new URL routes or views
- Implementing new features (e.g., new model, new functionality)
- Fixing bugs (add regression test)
- Changing permission logic
- Modifying API endpoints
- Updating authentication flows

### ❌ DON'T ADD TESTS WHEN:
- Making minor CSS/styling changes
- Updating documentation only
- Changing comments in code
- Refactoring without behavior change (unless adding coverage gaps)

---

## Test Coverage Goals for LLMs

### Minimum Acceptable Coverage
- **Models:** 80%+ method coverage
- **Views:** All critical paths tested
- **Permissions:** Every access control point tested
- **URLs:** 100% route resolution coverage

### Critical Paths (Must Have Tests)
1. User registration → login → dashboard flow
2. Campaign creation → character creation → campaign entry  
3. Chat functionality (post, edit, delete messages)
4. Dice rolling feature
5. Admin user management
6. Permission-based access control

---

## Git Workflow for Test Changes

### When Modifying Tests:
```bash
# 1. Make your test changes
# 2. Run tests to verify they pass
pytest tests/ -v

# 3. Stage and commit with descriptive message
git add tests/
git commit -m "test