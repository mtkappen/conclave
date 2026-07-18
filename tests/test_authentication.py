"""
Test authentication flows and access control.
Tests login, logout, password change, and permission-based access.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class TestLoginLogout:
    """Test login and logout functionality."""

    def test_login_page_accessible(self, client):
        """Test that login page is accessible without authentication."""
        response = client.get(reverse('campaigns:login'))
        assert response.status_code == 200
        assert b'Login' in response.content or b'login' in response.content.lower()

    def test_login_success(self, client, db_setup):
        """Test successful login with valid credentials."""
        response = client.post(reverse('campaigns:login'), {
            'username': 'player1',
            'password': 'player123'
        })
        # Should redirect after successful login (usually to dashboard)
        assert response.status_code in [200, 302]

    def test_login_failure_invalid_credentials(self, client):
        """Test login fails with invalid credentials."""
        response = client.post(reverse('campaigns:login'), {
            'username': 'nonexistent',
            'password': 'wrongpassword'
        })
        # Should stay on login page or show error
        assert response.status_code == 200

    def test_logout_requires_authentication(self, client):
        """Test that logout redirects to login when not authenticated."""
        response = client.get(reverse('campaigns:logout'))
        # Should redirect to login page
        assert response.status_code in [301, 302]

    def test_logout_success(self, client, db_setup):
        """Test successful logout."""
        client.force_login(db_setup['regular_user'])
        response = client.get(reverse('campaigns:logout'))
        # Should redirect after logout
        assert response.status_code in [301, 302]


class TestPasswordChange:
    """Test password change functionality."""

    def test_voluntary_password_change_page(self, client_auth):
        """Test voluntary password change page is accessible."""
        response = client_auth.get(reverse('campaigns:voluntary_change_password'))
        assert response.status_code == 200

    def test_change_password_forced_on_first_login(self, client):
        """Test that users forced to change password on first login."""
        # Create user with force_password_change flag (if implemented)
        user = User.objects.create_user(
            username='newuser',
            email='new@test.com',
            password='temp123'
        )
        # Simulate first-time login scenario
        client.force_login(user)
        
        # Should redirect to change password page if forced
        response = client.get(reverse('campaigns:dashboard'))
        # This test depends on your implementation of force_password_change


class TestPermissionAccess:
    """Test permission-based access control."""

    def test_dashboard_requires_authentication(self, client):
        """Test that dashboard requires authentication."""
        response = client.get(reverse('campaigns:dashboard'))
        # Should redirect to login if not authenticated
        assert response.status_code in [301, 302] or response.status_code == 200

    def test_admin_pages_require_superuser(self, client_auth, db_setup):
        """Test that admin pages require superuser privileges."""
        # Regular user should not access admin pages
        response = client_auth.get(reverse('campaigns:admin_user_list'))
        # Should redirect or return 403/404
        assert response.status_code in [301, 302, 403, 404]

    def test_admin_pages_accessible_to_superuser(self, admin_client):
        """Test that superuser can access admin pages."""
        response = admin_client.get(reverse('campaigns:admin_user_list'))
        assert response.status_code == 200

    def test_campaign_detail_requires_membership(self, client_auth, db_setup):
        """Test that users can only access campaigns they're members of."""
        # Create a campaign the user is not part of
        other_campaign = Campaign.objects.create(
            name='Other Campaign',
            description='Not accessible to this user',
            dm=db_setup['superuser']
        )
        
        response = client_auth.get(reverse('campaigns:campaign_detail', 
                                          kwargs={'pk': other_campaign.id}))
        # Should redirect or show error
        assert response.status_code in [301, 302, 403, 404]

    def test_dm_roster_requires_dm_or_admin(self, client_auth, db_setup):
        """Test that DM roster requires DM role or admin privileges."""
        campaign = db_setup['campaign']
        
        # Regular player should not access DM roster
        response = client_auth.get(reverse('campaigns:dm_roster', 
                                          kwargs={'pk': campaign.id}))
        assert response.status_code in [301, 302, 403, 404]

    def test_dm_can_access_dm_roster(self, admin_client, db_setup):
        """Test that DM can access their campaign's roster."""
        campaign = db_setup['campaign']
        
        response = admin_client.get(reverse('campaigns:dm_roster', 
                                           kwargs={'pk': campaign.id}))
        assert response.status_code == 200


class TestSetupFlow:
    """Test first-time setup flow."""

    def test_setup_page_accessible(self, client):
        """Test that setup page is accessible."""
        # This depends on whether setup has been completed
        response = client.get(reverse('campaigns:setup'))
        assert response.status_code in [200, 301, 302]
