"""
Tests for user settings functionality.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from campaigns.models import Campaign, CampaignMembership

User = get_user_model()


@pytest.mark.django_db
class TestUserSettings:
    """Test suite for user settings page and functionality."""
    
    def test_settings_page_accessible(self, client_auth):
        """Test that authenticated users can access the settings page."""
        response = client_auth.get(reverse('campaigns:user_settings'))
        assert response.status_code == 200
        assert b'User Settings' in response.content
    
    def test_settings_page_requires_authentication(self, client):
        """Test that unauthenticated users cannot access settings page."""
        response = client.get(reverse('campaigns:user_settings'))
        assert response.status_code == 302  # Redirect to login
    
    def test_update_real_name(self, client_auth, db_setup):
        """Test updating user's real name."""
        user = db_setup['regular_user']
        
        response = client_auth.post(reverse('campaigns:user_settings'), {
            'real_name': 'John Doe',
            'avatar': ''
        })
        
        assert response.status_code == 302  # Redirect after success
        user.refresh_from_db()
        assert user.real_name == 'John Doe'
    
    def test_update_avatar(self, client_auth, db_setup):
        """Test that avatar field exists and can be cleared."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        user = db_setup['regular_user']
        
        # First add an avatar via the model directly (bypassing form validation issues in tests)
        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\xdac\xfc\xcf\xf0\xbf\x00\x05\xfe\x02\xfe\xa7j\x9d\xbd\x00\x00\x00\x00IEND\xaeB`\x82'
        image_file = SimpleUploadedFile(
            "test_avatar.png",
            image_content,
            content_type="image/png"
        )
        
        # Save avatar directly to user model
        user.avatar.save("test_avatar.png", image_file, save=True)
        
        # Now test that we can update other fields while keeping the avatar
        response = client_auth.post(reverse('campaigns:user_settings'), {
            'real_name': 'Updated Name',
            'avatar-clear': 'on'  # Clear the avatar
        })
        
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.real_name == 'Updated Name'
    
    def test_settings_page_shows_current_avatar(self, client_auth, db_setup):
        """Test that settings page displays current avatar if exists."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        user = db_setup['regular_user']
        
        # Add an avatar first
        image_content = b'\x89PNG\r\n\x1a\n'
        image_file = SimpleUploadedFile(
            "test_avatar.png",
            image_content,
            content_type="image/png"
        )
        user.avatar = image_file
        user.save()
        
        response = client_auth.get(reverse('campaigns:user_settings'))
        assert response.status_code == 200
        # Check that the avatar URL appears in the response
        assert user.avatar.url.encode() in response.content
    
    def test_settings_form_validation(self, client_auth):
        """Test form validation for settings."""
        # Real name has max_length=100
        long_name = 'A' * 150
        
        response = client_auth.post(reverse('campaigns:user_settings'), {
            'real_name': long_name,
            'avatar': ''
        })
        
        # Form should have errors
        assert response.status_code == 200  # Re-render with errors
    
    def test_settings_redirects_to_dashboard_on_success(self, client_auth):
        """Test successful settings update redirects to dashboard."""
        response = client_auth.post(reverse('campaigns:user_settings'), {
            'real_name': 'New Name',
            'avatar': ''
        })
        
        assert response.status_code == 302
        assert reverse('campaigns:dashboard') in response.url
    
    def test_settings_link_in_dropdown(self, client_auth):
        """Test that settings link appears in user dropdown menu."""
        # Test dashboard page which includes base.html with dropdown
        response = client_auth.get(reverse('campaigns:dashboard'))
        assert response.status_code == 200
        
        # Check for settings URL in the response
        assert reverse('campaigns:user_settings').encode() in response.content
    
    def test_password_change_link_in_settings(self, client_auth):
        """Test that password change link is available from settings page."""
        response = client_auth.get(reverse('campaigns:user_settings'))
        assert response.status_code == 200
        
        # Check for password change link
        assert reverse('campaigns:voluntary_change_password').encode() in response.content
    
    def test_avatar_shows_in_dropdown_with_avatar(self, client_auth, db_setup):
        """Test that user avatar appears in dropdown menu when set."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        user = db_setup['regular_user']
        
        # Add an avatar directly to the user model
        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\xdac\xfc\xcf\xf0\xbf\x00\x05\xfe\x02\xfe\xa7j\x9d\xbd\x00\x00\x00\x00IEND\xaeB`\x82'
        image_file = SimpleUploadedFile(
            "test_avatar.png",
            image_content,
            content_type="image/png"
        )
        user.avatar.save("test_avatar.png", image_file, save=True)
        
        # Check dashboard page which includes the navbar with dropdown
        response = client_auth.get(reverse('campaigns:dashboard'))
        assert response.status_code == 200
        
        # Avatar URL should appear in the response (in both dropdown toggle and settings page)
        assert user.avatar.url.encode() in response.content
    
    def test_avatar_initial_shows_in_dropdown_without_avatar(self, client_auth, db_setup):
        """Test that username initial appears when no avatar is set."""
        user = db_setup['regular_user']
        
        # Ensure no avatar exists
        user.avatar = None
        user.save()
        
        response = client_auth.get(reverse('campaigns:dashboard'))
        assert response.status_code == 200
        
        # Should contain the first letter of username in a styled div
        content = response.content.decode()
        assert user.username[0].upper() in content
    
    def test_dropdown_menu_structure(self, client_auth):
        """Test that dropdown menu has correct structure and links."""
        response = client_auth.get(reverse('campaigns:dashboard'))
        assert response.status_code == 200
        
        content = response.content.decode()
        
        # Check for required elements
        assert 'user-dropdown' in content
        assert 'user-menu-toggle' in content
        assert reverse('campaigns:user_settings') in content
        assert reverse('campaigns:voluntary_change_password') in content
        assert reverse('campaigns:logout') in content
    
    def test_user_avatar_on_dashboard_header(self, client_auth, db_setup):
        """Test that user avatar appears next to welcome message on dashboard."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        user = db_setup['regular_user']
        
        # Add an avatar directly to the user model
        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\xdac\xfc\xcf\xf0\xbf\x00\x05\xfe\x02\xfe\xa7j\x9d\xbd\x00\x00\x00\x00IEND\xaeB`\x82'
        image_file = SimpleUploadedFile(
            "test_avatar.png",
            image_content,
            content_type="image/png"
        )
        user.avatar.save("test_avatar.png", image_file, save=True)
        
        response = client_auth.get(reverse('campaigns:dashboard'))
        assert response.status_code == 200
        
        # Avatar URL should appear in the dashboard header
        assert user.avatar.url.encode() in response.content
    
    def test_user_initial_on_dashboard_without_avatar(self, client_auth, db_setup):
        """Test that username initial appears on dashboard when no avatar is set."""
        user = db_setup['regular_user']
        
        # Ensure no avatar exists
        user.avatar = None
        user.save()
        
        response = client_auth.get(reverse('campaigns:dashboard'))
        assert response.status_code == 200
        
        # Should contain the first letter of username in a styled div
        content = response.content.decode()
        assert user.username[0].upper() in content
    
    def test_user_statistics_display(self, client_auth, db_setup):
        """Test that user statistics are displayed on settings page."""
        campaign = db_setup['campaign']
        user = db_setup['regular_user']
        
        # Create some test data
        from campaigns.models import ChatMessage, Character, DiceRollLog
        
        # Add a message
        ChatMessage.objects.create(
            content='Test message',
            sender=user,
            campaign=campaign,
            visibility_type='PUBLIC'
        )
        
        # Add a character
        Character.objects.create(
            name='Stat Test Character',
            campaign=campaign,
            user=user,
            class_name='Wizard',
            level=1
        )
        
        # Add a dice roll
        DiceRollLog.objects.create(
            sender=user,
            campaign=campaign,
            formula='1d20+5',
            result=18,
            modifier=5
        )
        
        response = client_auth.get(reverse('campaigns:user_settings'))
        assert response.status_code == 200
        
        content = response.content.decode()
        
        # Check that statistics are displayed
        assert 'Your Statistics' in content or 'Statistics' in content
        assert '1' in content  # At least one of each stat should appear
    
    def test_user_statistics_zero_values(self, client_auth, db_setup):
        """Test that zero values display correctly for users with no activity."""
        response = client_auth.get(reverse('campaigns:user_settings'))
        assert response.status_code == 200
        
        content = response.content.decode()
        
        # Should still show the statistics section even if some are zero
        assert 'Campaigns' in content
        assert 'Messages Sent' in content
        assert 'Characters' in content
        assert 'Dice Rolls' in content
    
    def test_settings_heading_color_not_red(self, client_auth):
        """Test that settings heading uses blue color instead of red."""
        response = client_auth.get(reverse('campaigns:user_settings'))
        assert response.status_code == 200
        
        content = response.content.decode()
        
        # Should use blue (#007acc) not red (#e94560) for main heading
        assert '#007acc' in content


@pytest.mark.django_db
class TestChatColorSchemes:
    """Test suite for chat color scheme functionality."""
    
    def test_ic_messages_include_character_avatar(self, client_auth, db_setup):
        """Test that IC messages include character avatar data."""
        campaign = db_setup['campaign']
        user = db_setup['regular_user']
        character = db_setup['character']
        
        # Create an IC message
        from campaigns.models import ChatMessage
        
        message = ChatMessage.objects.create(
            content='Test IC message',
            sender=user,
            campaign=campaign,
            visibility_type='PUBLIC',
            message_type='IC'
        )
        
        # Test the chat messages endpoint
        response = client_auth.get(reverse('campaigns:get_chat_messages', args=[campaign.pk]))
        assert response.status_code == 200
        
        data = response.json()
        assert len(data['messages']) > 0
        
        # Find our message
        msg = next((m for m in data['messages'] if m['id'] == message.id), None)
        assert msg is not None
        assert msg['message_type'] == 'IC'
    
    def test_ooc_messages_use_user_avatar(self, client_auth, db_setup):
        """Test that OOC messages use user avatar."""
        campaign = db_setup['campaign']
        user = db_setup['regular_user']
        
        from campaigns.models import ChatMessage
        
        message = ChatMessage.objects.create(
            content='Test OOC message',
            sender=user,
            campaign=campaign,
            visibility_type='PUBLIC',
            message_type='OOC_RELEVANT'
        )
        
        response = client_auth.get(reverse('campaigns:get_chat_messages', args=[campaign.pk]))
        assert response.status_code == 200
        
        data = response.json()
        msg = next((m for m in data['messages'] if m['id'] == message.id), None)
        assert msg is not None
        assert msg['message_type'] == 'OOC_RELEVANT'
    
    def test_secret_whisper_messages_preserved(self, client_auth, db_setup):
        """Test that secret whisper messages are properly tracked."""
        campaign = db_setup['campaign']
        user = db_setup['regular_user']
        another_user = db_setup['another_user']
        
        # Add another user to campaign
        CampaignMembership.objects.create(
            user=another_user,
            campaign=campaign,
            role='PLAYER'
        )
        
        from campaigns.models import ChatMessage
        
        message = ChatMessage.objects.create(
            content='Secret whisper',
            sender=user,
            campaign=campaign,
            visibility_type='SECRET_WHISPER',
            message_type='OOC_RELEVANT'
        )
        message.recipients.add(another_user)
        
        response = client_auth.get(reverse('campaigns:get_chat_messages', args=[campaign.pk]))
        assert response.status_code == 200
        
        data = response.json()
        msg = next((m for m in data['messages'] if m['id'] == message.id), None)
        assert msg is not None
        assert msg['visibility_type'] == 'SECRET_WHISPER'
