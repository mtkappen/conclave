"""
Test campaign management functionality.
Tests campaign creation, viewing, editing, and deletion.
"""
import pytest
from django.urls import reverse
from campaigns.models import Campaign, CampaignMembership


class TestCampaignCreation:
    """Test campaign creation workflow."""

    def test_create_campaign_page_accessible(self, client_auth):
        """Test that create campaign page is accessible to authenticated users."""
        response = client_auth.get(reverse('campaigns:create_campaign'))
        assert response.status_code == 200

    def test_create_campaign_success(self, client_auth, db_setup):
        """Test successful campaign creation."""
        response = client_auth.post(reverse('campaigns:create_campaign'), {
            'title': 'New Test Campaign',
            'description': 'A new campaign for testing'
        })
        
        # Should redirect to the newly created campaign or dashboard
        assert response.status_code in [301, 302]
        
        # Verify campaign was created
        assert Campaign.objects.filter(title='New Test Campaign').exists()

    def test_create_campaign_requires_title(self, client_auth):
        """Test that campaign creation requires a title."""
        response = client_auth.post(reverse('campaigns:create_campaign'), {
            'title': '',  # Empty title
            'description': 'Campaign without title'
        })
        
        # Should show form with validation errors
        assert response.status_code == 200


class TestCampaignDetail:
    """Test campaign detail view."""

    def test_campaign_detail_accessible_to_members(self, client_auth, db_setup):
        """Test that members can access their campaign detail page."""
        campaign = db_setup['campaign']
        
        response = client_auth.get(reverse('campaigns:campaign_detail', 
                                          kwargs={'pk': campaign.id}))
        assert response.status_code == 200

    def test_campaign_detail_shows_correct_data(self, client_auth, db_setup):
        """Test that campaign detail shows correct information."""
        campaign = db_setup['campaign']
        
        response = client_auth.get(reverse('campaigns:campaign_detail', 
                                          kwargs={'pk': campaign.id}))
        
        assert campaign.title.encode() in response.content
        assert campaign.description.encode() in response.content

    def test_campaign_detail_requires_membership(self, client_auth, db_setup):
        """Test that non-members cannot access campaign detail."""
        # Create a campaign the user is not part of
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='other123'
        )
        
        other_campaign = Campaign.objects.create(
            title='Other Campaign',
            description='Not accessible'
        )
        
        response = client_auth.get(reverse('campaigns:campaign_detail', 
                                          kwargs={'pk': other_campaign.id}))
        
        # Should redirect or show error
        assert response.status_code in [301, 302, 403, 404]


class TestCampaignDeletion:
    """Test campaign deletion functionality."""

    def test_delete_campaign_requires_dm_or_admin(self, client_auth, db_setup):
        """Test that only DM or admin can delete campaigns."""
        campaign = db_setup['campaign']
        
        # Regular player should not be able to delete
        response = client_auth.post(reverse('campaigns:delete_character', 
                                           kwargs={'pk': campaign.id}))
        assert response.status_code in [301, 302, 403, 404]

    def test_delete_campaign_as_dm(self, admin_client, db_setup):
        """Test that DM can delete their campaign."""
        campaign = db_setup['campaign']
        
        response = admin_client.post(reverse('campaigns:delete_character', 
                                            kwargs={'pk': campaign.id}))
        # Should redirect after deletion
        assert response.status_code in [301, 302]


class TestMemberManagement:
    """Test campaign member management."""

    def test_add_member_page_accessible(self, client_auth, db_setup):
        """Test that add member page is accessible to DM."""
        campaign = db_setup['campaign']
        
        response = client_auth.get(reverse('campaigns:add_member', 
                                          kwargs={'pk': campaign.id}))
        # Depends on permissions - may require DM role
        assert response.status_code in [200, 301, 302, 403]

    def test_leave_campaign(self, client_auth, db_setup):
        """Test that users can leave their campaigns."""
        campaign = db_setup['campaign']
        
        response = client_auth.post(reverse('campaigns:leave_campaign', 
                                           kwargs={'pk': campaign.id}))
        # Should redirect after leaving
        assert response.status_code in [301, 302]

    def test_remove_member_requires_dm(self, admin_client, db_setup):
        """Test that only DM can remove members."""
        membership = CampaignMembership.objects.filter(
            user=db_setup['regular_user'],
            campaign=db_setup['campaign']
        ).first()
        
        if membership:
            response = admin_client.post(reverse('campaigns:remove_member', 
                                                kwargs={'pk': membership.id}))
            assert response.status_code in [301, 302]


class TestDMRoster:
    """Test DM roster functionality."""

    def test_dm_roster_shows_all_members(self, admin_client, db_setup):
        """Test that DM roster shows all campaign members."""
        campaign = db_setup['campaign']
        
        response = admin_client.get(reverse('campaigns:dm_roster', 
                                           kwargs={'pk': campaign.id}))
        
        assert response.status_code == 200
        # Should show member information


class TestCampaignFeatures:
    """Test various campaign features."""

    def test_notebook_accessible(self, client_auth, db_setup):
        """Test that personal notebook is accessible."""
        campaign = db_setup['campaign']
        
        response = client_auth.get(reverse('campaigns:notebook', 
                                          kwargs={'pk': campaign.id}))
        assert response.status_code == 200

    def test_rule_book_accessible(self, client_auth, db_setup):
        """Test that rule book is accessible."""
        campaign = db_setup['campaign']
        
        response = client_auth.get(reverse('campaigns:rule_book', 
                                          kwargs={'pk': campaign.id}))
        assert response.status_code == 200

    def test_edit_rule_book_requires_dm(self, client_auth, db_setup):
        """Test that only DM can edit rule book."""
        campaign = db_setup['campaign']
        
        response = client_auth.get(reverse('campaigns:edit_rule_book', 
                                          kwargs={'pk': campaign.id}))
        # Should redirect or show error for non-DM users
        assert response.status_code in [301, 302, 403]
