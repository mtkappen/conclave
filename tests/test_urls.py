"""
Test all URL routes to ensure they resolve correctly.
This tests the URL configuration from campaigns/urls.py
"""
import pytest
from django.urls import reverse, resolve


class TestURLResolution:
    """Test that all URLs resolve to their expected views."""

    @pytest.mark.django_db
    def test_setup_url_resolves(self):
        """Test /setup/ URL resolves."""
        url = reverse('campaigns:first_time_setup')
        assert url == '/setup/'
        
    def test_login_url_resolves(self):
        """Test /login/ URL resolves."""
        url = reverse('campaigns:login')
        assert url == '/login/'
        
    def test_logout_url_resolves(self):
        """Test /logout/ URL resolves."""
        url = reverse('campaigns:logout')
        assert url == '/logout/'

    def test_dashboard_url_resolves(self):
        """Test dashboard URL resolves to root."""
        url = reverse('campaigns:dashboard')
        assert url == '/'

    def test_create_campaign_url_resolves(self):
        """Test campaign creation URL resolves."""
        url = reverse('campaigns:create_campaign')
        assert url == '/campaign/create/'

    @pytest.mark.django_db
    def test_campaign_detail_url_resolves(self, db_setup):
        """Test campaign detail URL with pk parameter."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:campaign_detail', kwargs={'pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/'

    @pytest.mark.django_db
    def test_create_character_url_resolves(self, db_setup):
        """Test character creation URL with campaign pk."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:create_character', kwargs={'campaign_pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/character/create/'

    @pytest.mark.django_db
    def test_character_detail_url_resolves(self, db_setup):
        """Test character detail URL with pk parameter."""
        char_id = db_setup['character'].id
        url = reverse('campaigns:character_detail', kwargs={'pk': char_id})
        assert url == f'/character/{char_id}/'

    @pytest.mark.django_db
    def test_character_edit_url_resolves(self, db_setup):
        """Test character edit URL with pk parameter."""
        char_id = db_setup['character'].id
        url = reverse('campaigns:edit_character', kwargs={'pk': char_id})
        assert url == f'/character/{char_id}/edit/'

    @pytest.mark.django_db
    def test_add_inventory_url_resolves(self, db_setup):
        """Test inventory add URL with character pk."""
        char_id = db_setup['character'].id
        url = reverse('campaigns:add_inventory_item', kwargs={'character_pk': char_id})
        assert url == f'/character/{char_id}/inventory/add/'

    @pytest.mark.django_db
    def test_delete_character_url_resolves(self, db_setup):
        """Test character delete URL with pk parameter."""
        char_id = db_setup['character'].id
        url = reverse('campaigns:delete_character', kwargs={'pk': char_id})
        assert url == f'/character/{char_id}/delete/'

    @pytest.mark.django_db
    def test_dm_roster_url_resolves(self, db_setup):
        """Test DM roster URL with campaign pk."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:dm_roster', kwargs={'campaign_pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/dm/roster/'

    @pytest.mark.django_db
    def test_chat_messages_url_resolves(self, db_setup):
        """Test chat messages API URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:get_chat_messages', kwargs={'campaign_pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/chat/messages/'

    @pytest.mark.django_db
    def test_post_chat_url_resolves(self, db_setup):
        """Test post chat API URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:post_chat_message', kwargs={'campaign_pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/chat/post/'

    @pytest.mark.django_db
    def test_post_dice_url_resolves(self, db_setup):
        """Test post dice roll API URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:post_dice_roll', kwargs={'campaign_pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/dice/post/'

    @pytest.mark.django_db
    def test_members_url_resolves(self, db_setup):
        """Test members management URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:manage_members', kwargs={'campaign_pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/members/'

    @pytest.mark.django_db
    def test_add_member_url_resolves(self, db_setup):
        """Test add member URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:add_member', kwargs={'campaign_pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/members/add/'

    @pytest.mark.django_db
    def test_update_role_url_resolves(self, db_setup):
        """Test update membership role URL."""
        from campaigns.models import CampaignMembership
        membership = CampaignMembership.objects.filter(
            user=db_setup['regular_user'],
            campaign=db_setup['campaign']
        ).first()
        if membership:
            url = reverse('campaigns:update_role', kwargs={'membership_pk': membership.id})
            assert f'/membership/{membership.id}/role/' in url

    @pytest.mark.django_db
    def test_remove_member_url_resolves(self, db_setup):
        """Test remove member URL."""
        from campaigns.models import CampaignMembership
        membership = CampaignMembership.objects.filter(
            user=db_setup['regular_user'],
            campaign=db_setup['campaign']
        ).first()
        if membership:
            url = reverse('campaigns:remove_member', kwargs={'membership_pk': membership.id})
            assert f'/membership/{membership.id}/remove/' in url

    @pytest.mark.django_db
    def test_leave_campaign_url_resolves(self, db_setup):
        """Test leave campaign URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:leave_campaign', kwargs={'campaign_pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/leave/'

    @pytest.mark.django_db
    def test_notebook_url_resolves(self, db_setup):
        """Test notebook URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:personal_notebook', kwargs={'campaign_pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/notebook/'

    @pytest.mark.django_db
    def test_rule_book_url_resolves(self, db_setup):
        """Test rule book URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:view_rule_book', kwargs={'campaign_pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/rule-book/'

    @pytest.mark.django_db
    def test_edit_rule_book_url_resolves(self, db_setup):
        """Test edit rule book URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:edit_rule_book', kwargs={'campaign_pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/rule-book/edit/'

    # Admin URLs (require superuser)
    def test_admin_user_list_url_resolves(self):
        """Test admin user list URL."""
        url = reverse('campaigns:admin_user_list')
        assert url == '/users/'

    def test_create_user_url_resolves(self):
        """Test create user URL."""
        url = reverse('campaigns:admin_create_user')
        assert url == '/users/create/'

    def test_admin_campaign_list_url_resolves(self):
        """Test admin campaign list URL."""
        url = reverse('campaigns:admin_campaign_list')
        assert url == '/admin/campaigns/'

    def test_database_reset_url_resolves(self):
        """Test database reset URL."""
        url = reverse('campaigns:database_reset')
        assert url == '/admin/database-reset/'


class TestURLViewMapping:
    """Test that URLs map to correct view functions."""

    def test_dashboard_maps_to_view(self):
        """Verify dashboard URL maps to dashboard view."""
        resolved = resolve('/')
        assert 'dashboard' in resolved.func.__name__ or 'Dashboard' in str(resolved.func)

    def test_login_maps_to_auth_view(self):
        """Verify login URL maps to authentication view."""
        resolved = resolve('/login/')
        # Django auth views are typically LoginView
        assert resolved.url_name == 'login' or 'Login' in str(resolved.func)
