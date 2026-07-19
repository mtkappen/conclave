# Quick Reference Guide - D&D Tabletop Test Suite

## 🚀 Running Tests (Quick Commands)

### All Tests
```bash
python tests/run_tests.py
# OR
pytest tests/ -v
```

### Specific Categories
```bash
pytest tests/test_authentication.py -v      # Login, logout, permissions
pytest tests/test_campaigns.py -v           # Campaign CRUD operations
pytest tests/test_characters.py -v          # Character management
pytest tests/test_chat_and_dice.py -v       # Chat and dice rolling
pytest tests/test_admin.py -v               # Admin features
pytest tests/test_urls.py -v                # URL resolution
```

### With Coverage
```bash
pytest --cov=campaigns --cov-report=html tests/
# View: tests/coverage_html/index.html
```

## 📁 Test File Structure

| File | Purpose | Tests Count |
|------|---------|-------------|
| `conftest.py` | Fixtures and configuration | - |
| `test_basic_setup.py` | Infrastructure validation | 6 |
| `test_urls.py` | URL resolution (30+ routes) | 25+ |
| `test_authentication.py` | Login, logout, permissions | 15+ |
| `test_campaigns.py` | Campaign management | 15+ |
| `test_characters.py` | Character & inventory | 15+ |
| `test_chat_and_dice.py` | Chat messages, dice rolls | 12+ |
| `test_admin.py` | Admin features | 12+ |

## 🔧 Available Fixtures

```python
def test_example(client_auth, admin_client, db_setup):
    """Use these fixtures in your tests."""
    
    # client_auth - Logged in as regular user (player1)
    response = client_auth.get('/some-url/')
    
    # admin_client - Logged in as superuser (admin)
    response = admin_client.get('/admin-url/')
    
    # db_setup - Access to test data
    user = db_setup['superuser']      # Admin user
    user = db_setup['regular_user']   # player1
    campaign = db_setup['campaign']   # Test Campaign
    character = db_setup['character'] # Test Character
```

## 📝 Writing New Tests

### Basic Pattern
```python
import pytest
from django.urls import reverse
from campaigns.models import Campaign

class TestFeatureName:
    """Describe the feature being tested."""
    
    def test_something(self, client_auth, db_setup):
        """Test specific behavior."""
        # Arrange
        campaign = db_setup['campaign']
        
        # Act
        response = client_auth.get(
            reverse('campaigns:campaign_detail', 
                   kwargs={'pk': campaign.id})
        )
        
        # Assert
        assert response.status_code == 200
```

### Testing Permissions
```python
def test_requires_permission(self, client_auth):
    """Test that permission is required."""
    response = client_auth.get('/admin-url/')
    assert response.status_code in [301, 302, 403]  # Redirect or forbidden

def test_admin_can_access(self, admin_client):
    """Test that admin can access."""
    response = admin_client.get('/admin-url/')
    assert response.status_code == 200
```

## 🎯 Common Test Scenarios

### Create Resource
```python
response = client_auth.post(reverse('campaigns:create_campaign'), {
    'title': 'New Campaign',
    'description': 'Test description'
})
assert response.status_code in [301, 302]  # Redirect after create
assert Campaign.objects.filter(title='New Campaign').exists()
```

### Update Resource
```python
character = db_setup['character']
response = client_auth.post(
    reverse('campaigns:edit_character', kwargs={'pk': character.id}),
    {'name': 'Updated Name', 'class_name': 'Wizard', 'level': 2}
)
assert response.status_code in [301, 302]
character.refresh_from_db()
assert character.name == 'Updated Name'
```

### Delete Resource
```python
response = client_auth.post(
    reverse('campaigns:delete_character', kwargs={'pk': character.id})
)
assert response.status_code in [301, 302]
assert not Character.objects.filter(id=character.id).exists()
```

## ⚠️ Important Notes

### Model Field Names (Use These!)
- ✅ `Campaign.title` (NOT name)
- ✅ `Character.class_name` (NOT class_type)
- ✅ `Character.user` (NOT owner)
- ✅ `CampaignMembership.role = 'PLAYER'` (NOT 'player')
- ✅ `InventoryItem.name` (NOT item_name)

### URL Resolution
Always use Django's `reverse()` for URLs:
```python
from django.urls import reverse

url = reverse('campaigns:campaign_detail', kwargs={'pk': campaign.id})
response = client_auth.get(url)
```

## 🐛 Debugging Tests

### Run Single Test
```bash
pytest tests/test_campaigns.py::TestCampaignCreation::test_create_campaign_success -v
```

### With Debugger
```bash
pytest tests/ -v --pdb  # Drop into pdb on failure
```

### Show Output
```bash
pytest tests/ -v -s  # Show print statements and logs
```

## 📊 Test Coverage Commands

```bash
# Terminal report with missing lines
pytest --cov=campaigns --cov-report=term-missing tests/

# HTML report
pytest --cov=campaigns --cov-report=html tests/

# XML report (for CI/CD)
pytest --cov=campaigns --cov-report=xml tests/
```

## 🔍 Quick Test Checklist

Before committing code:
- [ ] Run all tests: `pytest tests/ -v`
- [ ] Check for failures or errors
- [ ] Review coverage if adding new features
- [ ] Fix any broken tests

## 📚 Documentation Links

- Full guide: `tests/README.md`
- Summary: `tests/TESTING_SUMMARY.md`
- Django Testing: https://docs.djangoproject.com/en/stable/topics/testing/
- Pytest Docs: https://docs.pytest.org/
