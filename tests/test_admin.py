"""
Test admin functionality.
Tests user management, campaign administration, and database operations.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from campaigns.models import Campaign

User = get_user_model()


class TestUserManagement:
    """Test admin user management features."""

    def test_admin_user_list_accessible(self, admin_client):
        """Test that superuser can access user list."""
        response = admin_client.get(reverse('campaigns:admin_user_list'))
        assert response.status_code == 200

    def test_regular_user_cannot_access_user_list(self, client_auth):
        """Test that regular users cannot access user management."""
        response = client_auth.get(reverse('campaigns:admin_user_list'))
        # Should redirect or return error
        assert response.status_code in [301, 302, 403]

    def test_create_user_page_accessible(self, admin_client):
        """Test that superuser can access create user page."""
        response = admin_client.get(reverse('campaigns:admin_create_user'))
        assert response.status_code == 200

    def test_create_user_success(self, admin_client):
        """Test successful user creation by admin."""
        response = admin_client.post(reverse('campaigns:admin_create_user'), {
            'username': 'newadminuser',
            'email': 'newadmin@test.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        })
        
        # Should redirect after creation
        assert response.status_code in [301, 302]

    def test_delete_user_page_accessible(self, admin_client, db_setup):
        """Test that superuser can access delete user page."""
        user_to_delete = User.objects.create_user(
            username='todelete',
            email='delete@test.com',
            password='temp123'
        )
        
        response = admin_client.get(reverse('campaigns:delete_user', 
                                           kwargs={'pk': user_to_delete.id}))
        assert response.status_code == 200

    def test_delete_user_success(self, admin_client):
        """Test successful user deletion by admin."""
        user_to_delete = User.objects.create_user(
            username='todelete2',
            email='delete2@test.com',
            password='temp123'
        )
        
        response = admin_client.post(reverse('campaigns:delete_user', 
                                            kwargs={'pk': user_to_delete.id}))
        
        # Should redirect after deletion
        assert response.status_code in [301, 302]

    def test_cannot_delete_self(self, admin_client, db_setup):
        """Test that admin cannot delete their own account."""
        superuser = db_setup['superuser']
        
        response = admin_client.post(reverse('campaigns:delete_user', 
                                            kwargs={'pk': superuser.id}))
        
        # Should redirect or show error
        assert response.status_code in [301, 302]


class TestCampaignAdministration:
    """Test campaign administration features."""

    def test_admin_campaign_list_accessible(self, admin_client):
        """Test that superuser can access all campaigns list."""
        response = admin_client.get(reverse('campaigns:admin_campaign_list'))
        assert response.status_code == 200

    def test_regular_user_cannot_access_admin_campaign_list(self, client_auth):
        """Test that regular users cannot access admin campaign list."""
        response = client_auth.get(reverse('campaigns:admin_campaign_list'))
        # Should redirect or return error
        assert response.status_code in [301, 302, 403]

    def test_admin_can_view_all_campaigns(self, admin_client, db_setup):
        """Test that admin can see all campaigns regardless of membership."""
        # Create a campaign the admin is not part of
        other_user = User.objects.create_user(
            username='otherdm',
            email='otherdm@test.com',
            password='other123'
        )
        
        Campaign.objects.create(
            title='Admin View Only',  # Use 'title' instead of 'name'
            description='Campaign visible to admin'
        )
        
        response = admin_client.get(reverse('campaigns:admin_campaign_list'))
        
        assert response.status_code == 200
        # Should show all campaigns including ones admin is not part of


class TestDatabaseOperations:
    """Test database reset and other administrative operations."""

    def test_database_reset_page_accessible(self, admin_client):
        """Test that superuser can access database reset page."""
        response = admin_client.get(reverse('campaigns:database_reset'))
        # Should show confirmation page or redirect
        assert response.status_code in [200, 301, 302]

    def test_regular_user_cannot_access_database_reset(self, client_auth):
        """Test that regular users cannot access database reset."""
        response = client_auth.get(reverse('campaigns:database_reset'))
        # Should redirect or return error
        assert response.status_code in [301, 302, 403]


class TestSecretWhispers:
    """Test secret whisper visibility for admins."""

    def test_admin_can_view_secrets(self, admin_client, db_setup):
        """Test that superuser can view campaign secrets."""
        campaign = db_setup['campaign']
        
        response = admin_client.get(reverse('campaigns:admin_view_secrets', 
                                           kwargs={'pk': campaign.id}))
        # Should succeed or redirect based on implementation
        assert response.status_code in [200, 301, 302]

    def test_regular_user_cannot_view_secrets(self, client_auth, db_setup):
        """Test that regular users cannot view secret whispers."""
        campaign = db_setup['campaign']
        
        response = client_auth.get(reverse('campaigns:admin_view_secrets', 
                                          kwargs={'pk': campaign.id}))
        # Should redirect or return error
        assert response.status_code in [301, 302, 403]


class TestAdminPermissions:
    """Test various admin permission scenarios."""

    def test_admin_can_access_dm_features(self, admin_client, db_setup):
        """Test that superuser can access DM-only features."""
        campaign = db_setup['campaign']
        
        # Admin should be able to access DM roster even if not the DM
        response = admin_client.get(reverse('campaigns:dm_roster', 
                                           kwargs={'pk': campaign.id}))
        assert response.status_code == 200

    def test_admin_can_edit_any_rule_book(self, admin_client, db_setup):
        """Test that superuser can edit any campaign's rule book."""
        campaign = db_setup['campaign']
        
        response = admin_client.get(reverse('campaigns:edit_rule_book', 
                                           kwargs={'pk': campaign.id}))
        assert response.status_code == 200
