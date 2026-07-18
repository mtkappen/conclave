"""
Test all URL routes to ensure they resolve correctly.
This tests the URL configuration from campaigns/urls.py
"""
import pytest
from django.urls import reverse, resolve


class TestURLResolution:
    """Test that all URLs resolve to their expected views."""

    def test_setup_url_resolves(self):
        """Test /setup/ URL resolves."""
        url = reverse('campaigns:setup')
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

    def test_campaign_detail_url_resolves(self, db_setup):
        """Test campaign detail URL with pk parameter."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:campaign_detail', kwargs={'pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/'

    def test_create_character_url_resolves(self, db_setup):
        """Test character creation URL with campaign pk."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:create_character', kwargs={'pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/character/create/'

    def test_character_detail_url_resolves(self, db_setup):
        """Test character detail URL with pk parameter."""
        char_id = db_setup['character'].id
        url = reverse('campaigns:character_detail', kwargs={'pk': char_id})
        assert url == f'/character/{char_id}/'

    def test_character_edit_url_resolves(self, db_setup):
        """Test character edit URL with pk parameter."""
        char_id = db_setup['character'].id
        url = reverse('campaigns:edit_character', kwargs={'pk': char_id})
        assert url == f'/character/{char_id}/edit/'

    def test_add_inventory_url_resolves(self, db_setup):
        """Test inventory add URL with character pk."""
        char_id = db_setup['character'].id
        url = reverse('campaigns:add_inventory', kwargs={'character_pk': char_id})
        assert url == f'/character/{char_id}/inventory/add/'

    def test_delete_character_url_resolves(self, db_setup):
        """Test character delete URL with pk parameter."""
        char_id = db_setup['character'].id
        url = reverse('campaigns:delete_character', kwargs={'pk': char_id})
        assert url == f'/character/{char_id}/delete/'

    def test_dm_roster_url_resolves(self, db_setup):
        """Test DM roster URL with campaign pk."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:dm_roster', kwargs={'pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/dm/roster/'

    def test_chat_messages_url_resolves(self, db_setup):
        """Test chat messages API URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:get_messages', kwargs={'pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/chat/messages/'

    def test_post_chat_url_resolves(self, db_setup):
        """Test post chat API URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:post_message', kwargs={'pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/chat/post/'

    def test_post_dice_url_resolves(self, db_setup):
        """Test post dice roll API URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:post_dice', kwargs={'pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/dice/post/'

    def test_members_url_resolves(self, db_setup):
        """Test members management URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:members', kwargs={'pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/members/'

    def test_add_member_url_resolves(self, db_setup):
        """Test add member URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:add_member', kwargs={'pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/members/add/'

    def test_update_role_url_resolves(self, db_setup):
        """Test update membership role URL."""
        membership = db_setup['regular_user'].membership_set.first()
        if membership:
            url = reverse('campaigns:update_role', kwargs={'pk': membership.id})
            assert f'/membership/{membership.id}/role/' in url

    def test_remove_member_url_resolves(self, db_setup):
        """Test remove member URL."""
        membership = db_setup['regular_user'].membership_set.first()
        if membership:
            url = reverse('campaigns:remove_member', kwargs={'pk': membership.id})
            assert f'/membership/{membership.id}/remove/' in url

    def test_leave_campaign_url_resolves(self, db_setup):
        """Test leave campaign URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:leave_campaign', kwargs={'pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/leave/'

    def test_notebook_url_resolves(self, db_setup):
        """Test notebook URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:notebook', kwargs={'pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/notebook/'

    def test_rule_book_url_resolves(self, db_setup):
        """Test rule book URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:rule_book', kwargs={'pk': campaign_id})
        assert url == f'/campaign/{campaign_id}/rule-book/'

    def test_edit_rule_book_url_resolves(self, db_setup):
        """Test edit rule book URL."""
        campaign_id = db_setup['campaign'].id
        url = reverse('campaigns:edit_rule_book', kwargs={'pk': campaign_id})
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
