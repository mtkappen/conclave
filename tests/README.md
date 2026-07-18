# D&D Tabletop Application Test Suite

This directory contains the complete test suite for the D&D Tabletop application.

## Overview

The test suite covers all major functionality of the application:

- **Authentication & Authorization** - Login, logout, password changes, permissions
- **Campaign Management** - Creation, viewing, editing, deletion
- **Character Management** - Creation, editing, inventory management
- **Chat & Communication** - Real-time messaging, message editing/deletion
- **Dice Rolling** - Dice roll tracking and display
- **Admin Features** - User management, campaign administration
- **URL Resolution** - All routes resolve correctly

## Prerequisites

Install test dependencies:

```bash
pip install pytest pytest-django pytest-cov
```

Or update requirements.txt with:

```
pytest>=7.0.0
pytest-django>=4.5.0
pytest-cov>=4.0.0
```

## Running Tests

### Run All Tests

```bash
# Using the test runner script
python tests/run_tests.py

# Or directly with pytest
cd tests && pytest -v

# From project root
pytest tests/ -v
```

### Run Specific Test Files

```bash
# Test authentication only
pytest tests/test_authentication.py -v

# Test campaign features only
pytest tests/test_campaigns.py -v

# Test character management
pytest tests/test_characters.py -v

# Test chat and dice features
pytest tests/test_chat_and_dice.py -v

# Test admin functionality
pytest tests/test_admin.py -v

# Test URL resolution
pytest tests/test_urls.py -v
```

### Run Specific Tests

```bash
# Run a specific test function
pytest tests/test_authentication.py::TestLoginLogout::test_login_success -v

# Run all tests in a class
pytest tests/test_campaigns.py::TestCampaignCreation -v
```

### With Coverage Report

```bash
# Generate coverage report with HTML output
pytest --cov=campaigns --cov-report=html tests/

# View coverage in terminal with missing lines
pytest --cov=campaigns --cov-report=term-missing tests/
```

## Test Structure

### Fixtures (`conftest.py`)

- `db_setup` - Creates test users, campaigns, and characters
- `client_auth` - Authenticated client for testing user views
- `admin_client` - Superuser client for testing admin views

### Test Files

1. **test_urls.py** - URL resolution and view mapping tests
2. **test_authentication.py** - Login, logout, password change, permissions
3. **test_campaigns.py** - Campaign CRUD operations and member management
4. **test_characters.py** - Character creation, editing, inventory
5. **test_chat_and_dice.py** - Chat messages, dice rolling APIs
6. **test_admin.py** - Admin user management and system features

## Test Categories

### Critical Paths (Must Pass)

These tests cover essential user workflows:

1. User registration → login → dashboard flow
2. Campaign creation → character creation → campaign entry
3. Chat functionality (real-time updates)
4. Dice rolling feature
5. Admin user management
6. Password change flows

### Edge Cases

Tests for boundary conditions and error handling:

1. Accessing admin routes without permissions
2. Deleting non-existent resources
3. Character inventory operations
4. Member role changes
5. Secret whisper visibility controls

## Test Data

The `db_setup` fixture creates the following test data:

- **Users**: 
  - `admin` (superuser)
  - `player1` (regular user)
  - `player2` (another regular user)

- **Campaigns**:
  - `Test Campaign` (owned by admin, player1 is a member)

- **Characters**:
  - `Test Character` (owned by player1)

## Writing New Tests

### Basic Test Structure

```python
import pytest
from django.urls import reverse
from campaigns.models import Campaign

class TestFeatureName:
    """Test feature description."""
    
    def test_something(self, client_auth, db_setup):
        """Test specific behavior."""
        # Arrange
        campaign = db_setup['campaign']
        
        # Act
        response = client_auth.get(reverse('campaigns:campaign_detail', 
                                          kwargs={'pk': campaign.id}))
        
        # Assert
        assert response.status_code == 200
```

### Using Fixtures

- `client` - Unauthenticated test client
- `client_auth` - Authenticated as regular user
- `admin_client` - Authenticated as superuser
- `db_setup` - Access to pre-created test data

Example:

```python
def test_feature_with_data(self, admin_client, db_setup):
    campaign = db_setup['campaign']
    character = db_setup['character']
    
    # Use the fixtures in your test
    response = admin_client.get(...)
    assert ...
```

## Continuous Integration

Add to your CI/CD pipeline:

```yaml
test:
  script:
    - pip install pytest pytest-django pytest-cov
    - python manage.py migrate
    - pytest tests/ --cov=campaigns --cov-report=xml
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## Troubleshooting

### Common Issues

1. **Database errors**: Ensure migrations are applied
   ```bash
   python manage.py migrate
   ```

2. **Import errors**: Make sure Django settings module is set
   ```bash
   export DJANGO_SETTINGS_MODULE=dnd_app.settings
   ```

3. **Permission denied**: Check file permissions on test files

### Running Tests in Debug Mode

```bash
# Run with Python debugger
pytest tests/test_authentication.py::TestLoginLogout::test_login_success -v --pdb

# Show print statements
pytest tests/ -v -s
```

## Coverage Goals

- **Unit Tests**: 80%+ code coverage for models and forms
- **Integration Tests**: All critical paths covered
- **Edge Cases**: Permission checks, error handling tested

## Notes

- Tests use an in-memory SQLite database by default (configured in Django settings)
- Each test runs in isolation with a fresh database state
- Fixtures automatically clean up after tests complete
