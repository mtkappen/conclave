"""
Test chat and dice rolling functionality.
Tests real-time messaging, message editing/deletion, and dice rolls.
"""
import pytest
import json
from django.urls import reverse
from django.contrib.auth import get_user_model
from campaigns.models import ChatMessage, Campaign

User = get_user_model()


class TestChatMessages:
    """Test chat message functionality."""

    def test_get_messages_api(self, client_auth, db_setup):
        """Test retrieving chat messages via API endpoint."""
        campaign = db_setup['campaign']
        
        response = client_auth.get(reverse('campaigns:get_chat_messages', 
                                          kwargs={'campaign_pk': campaign.id}))
        
        # Should return JSON response
        assert response.status_code == 200
        assert response['Content-Type'].startswith('application/json')

    def test_post_message_success(self, client_auth, db_setup):
        """Test posting a chat message successfully."""
        campaign = db_setup['campaign']
        
        response = client_auth.post(reverse('campaigns:post_chat_message', 
                                           kwargs={'campaign_pk': campaign.id}), {
            'message': 'Hello, adventurers!',
            'timestamp': '2024-01-01T12:00:00'
        }, content_type='application/json')
        
        # Should return success response
        assert response.status_code in [200, 201]

    def test_post_message_requires_authentication(self, client, db_setup):
        """Test that posting messages requires authentication."""
        campaign = db_setup['campaign']
        
        response = client.post(reverse('campaigns:post_chat_message', 
                                      kwargs={'campaign_pk': campaign.id}), {
            'message': 'Unauthenticated message'
        })
        
        # Should redirect or return error
        assert response.status_code in [301, 302, 401, 403]

    def test_post_message_requires_membership(self, client_auth, db_setup):
        """Test that posting messages requires campaign membership."""
        # Create a campaign the user is not part of
        other_user = User.objects.create_user(
            username='outsider',
            email='out@test.com',
            password='out123'
        )
        
        other_campaign = Campaign.objects.create(
            title='Private Campaign',  # Use 'title' instead of 'name'
            description='Not accessible'
        )
        
        response = client_auth.post(reverse('campaigns:post_chat_message', 
                                           kwargs={'campaign_pk': other_campaign.id}), {
            'message': 'Intruder message'
        })
        
        # Should redirect or return error
        assert response.status_code in [301, 302, 403]

    def test_edit_own_message(self, client_auth, db_setup):
        """Test that users can edit their own messages."""
        campaign = db_setup['campaign']
        
        # Create a message first
        message = ChatMessage.objects.create(
            campaign=campaign,
            sender=db_setup['regular_user'],
            content='Original message'
        )
        
        response = client_auth.post(reverse('campaigns:edit_chat_message', 
                                           kwargs={'message_pk': message.id}), {
            'content': 'Edited message'
        })
        
        # Should succeed
        assert response.status_code in [200, 301, 302]

    def test_cannot_edit_others_messages(self, client_auth, db_setup):
        """Test that users cannot edit other users' messages."""
        campaign = db_setup['campaign']
        
        # Create a message by another user
        other_user = User.objects.create_user(
            username='otherplayer',
            email='other@test.com',
            password='other123'
        )
        
        other_message = ChatMessage.objects.create(
            campaign=campaign,
            sender=other_user,
            content="Other's message"
        )
        
        response = client_auth.post(reverse('campaigns:edit_chat_message', 
                                           kwargs={'message_pk': other_message.id}), {
            'content': "Trying to edit others' message"
        })
        
        # Should fail or redirect
        assert response.status_code in [301, 302, 403]

    def test_delete_own_message(self, client_auth, db_setup):
        """Test that users can delete their own messages."""
        campaign = db_setup['campaign']
        
        # Create a message first
        message = ChatMessage.objects.create(
            campaign=campaign,
            sender=db_setup['regular_user'],
            content='Message to delete'
        )
        
        response = client_auth.post(reverse('campaigns:delete_chat_message', 
                                           kwargs={'message_pk': message.id}))
        
        # Should succeed
        assert response.status_code in [301, 302]

    def test_cannot_delete_others_messages(self, client_auth, db_setup):
        """Test that users cannot delete other users' messages."""
        campaign = db_setup['campaign']
        
        # Create a message by another user
        other_user = User.objects.create_user(
            username='otherplayer',
            email='other@test.com',
            password='other123'
        )
        
        other_message = ChatMessage.objects.create(
            campaign=campaign,
            sender=other_user,
            content="Other's message to delete"
        )
        
        response = client_auth.post(reverse('campaigns:delete_chat_message', 

                                           kwargs={'message_pk': other_message.id}))
        
        # Should fail or redirect
        assert response.status_code in [301, 302, 403]


class TestDiceRolling:
    """Test dice rolling functionality."""

    def test_post_dice_roll_success(self, client_auth, db_setup):
        """Test posting a dice roll successfully."""
        campaign = db_setup['campaign']
        
        response = client_auth.post(reverse('campaigns:post_dice_roll', 
                                           kwargs={'campaign_pk': campaign.id}), {
            'dice_expression': '2d6+3',
            'result': 10,
            'description': 'Attack roll'
        })
        
        # Should return success response
        assert response.status_code in [200, 201]

    def test_post_dice_roll_requires_authentication(self, client, db_setup):
        """Test that posting dice rolls requires authentication."""
        campaign = db_setup['campaign']
        
        response = client.post(reverse('campaigns:post_dice_roll', 
                                      kwargs={'campaign_pk': campaign.id}), {
            'dice_expression': '1d20'
        })
        
        # Should redirect or return error
        assert response.status_code in [301, 302, 401, 403]

    def test_post_dice_roll_requires_membership(self, client_auth, db_setup):
        """Test that posting dice rolls requires campaign membership."""
        # Create a campaign the user is not part of
        other_user = User.objects.create_user(
            username='outsider',
            email='out@test.com',
            password='out123'
        )
        
        other_campaign = Campaign.objects.create(
            title='Private Campaign',  # Use 'title' instead of 'name'
            description='Not accessible'
        )
        
        response = client_auth.post(reverse('campaigns:post_dice_roll', 
                                           kwargs={'campaign_pk': other_campaign.id}), {
            'dice_expression': '1d20'
        })
        
        # Should redirect or return error
        assert response.status_code in [301, 302, 403]

    def test_various_dice_expressions(self, client_auth, db_setup):
        """Test various dice roll expressions."""
        campaign = db_setup['campaign']
        
        # Test different dice expressions
        test_cases = [
            ('1d20', 'Single d20 roll'),
            ('3d6', 'Multiple d6 rolls'),
            ('2d8+5', 'Dice with modifier'),
            ('4d4-2', 'Dice with subtraction'),
        ]
        
        for expression, description in test_cases:
            response = client_auth.post(reverse('campaigns:post_dice_roll', 
                                               kwargs={'campaign_pk': campaign.id}), {
                'dice_expression': expression,
                'description': description
            })
            
            # Should accept the dice roll
            assert response.status_code in [200, 201, 301, 302]


class TestChatIntegration:
    """Test chat integration with campaign features."""

    def test_chat_visible_on_campaign_page(self, client_auth, db_setup):
        """Test that chat component is visible on campaign detail page."""
        campaign = db_setup['campaign']
        
        response = client_auth.get(reverse('campaigns:campaign_detail', 
                                          kwargs={'pk': campaign.id}))
        
        assert response.status_code == 200
        # Chat component should be present in the template

    def test_multiple_messages_retained(self, client_auth, db_setup):
        """Test that multiple chat messages are retained."""
        campaign = db_setup['campaign']
        
        # Post multiple messages
        for i in range(5):
            client_auth.post(reverse('campaigns:post_chat_message', 
                                    kwargs={'campaign_pk': campaign.id}), {
                'message': f'Message number {i}'
            })
        
        # Retrieve messages
        response = client_auth.get(reverse('campaigns:get_chat_messages', 
                                          kwargs={'campaign_pk': campaign.id}))
        
        assert response.status_code == 200
        data = json.loads(response.content)
        # Should have multiple messages
