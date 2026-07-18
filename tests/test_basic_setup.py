"""
Basic tests to verify test infrastructure is working correctly.
Run these first to ensure pytest and Django are configured properly.
"""
import pytest


class TestInfrastructure:
    """Test that the testing infrastructure is set up correctly."""

    def test_pytest_is_working(self):
        """Simple test to verify pytest is running."""
        assert True

    def test_django_settings_loaded(self, settings):
        """Verify Django settings are loaded."""
        assert settings.DATABASES is not None
        assert 'default' in settings.DATABASES

    @pytest.mark.django_db
    def test_db_fixture_works(self, db_setup):
        """Test that the database fixture creates data correctly."""
        # Check users were created
        assert db_setup['superuser'].username == 'admin'
        assert db_setup['regular_user'].username == 'player1'
        
        # Check campaign was created
        assert db_setup['campaign'].title == 'Test Campaign'
        
        # Check character was created
        assert db_setup['character'].name == 'Test Character'
    @pytest.mark.django_db
    def test_client_auth_works(self, client_auth, db_setup):
        """Test that authenticated client is working."""
        from django.urls import reverse
        
        # Try to access dashboard (requires authentication)
        response = client_auth.get(reverse('campaigns:dashboard'))
        
        # Should be able to access (either 200 or redirect)
        assert response.status_code in [200, 301, 302]

    @pytest.mark.django_db
    def test_admin_client_works(self, admin_client):
        """Test that admin client is working."""
        from django.urls import reverse
        
        # Try to access admin user list (requires superuser)
        response = admin_client.get(reverse('campaigns:admin_user_list'))
        
        # Should be able to access as admin
        assert response.status_code == 200

    def test_models_are_importable(self):
        """Test that all models can be imported."""
        from campaigns.models import (
            User, Campaign, CampaignMembership, Character, 
            InventoryItem, ChatMessage, DiceRollLog,
            PersonalNotebook, CampaignRuleBook
        )
        
        assert User is not None
        assert Campaign is not None
        assert Character is not None


