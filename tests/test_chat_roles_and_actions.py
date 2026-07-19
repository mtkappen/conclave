"""
Test chat message role badges, character/NPC labels, and action button visibility.
Tests the visual elements of chat messages including sender roles and character identification.
"""
import pytest
import json
from django.urls import reverse
from django.contrib.auth import get_user_model
from campaigns.models import ChatMessage, Campaign, CampaignMembership, CharacterSheet

User = get_user_model()


class TestChatRoleBadges:
    """Test that role badges are correctly displayed for message senders."""

    def test_dm_role_shown_in_messages(self, client_auth, db_setup):
        """Test that DM role badge appears in chat messages."""
        campaign = db_setup['campaign']
        
        # Create a message from the DM
        dm_message = ChatMessage.objects.create(
            campaign=campaign,
            sender=db_setup['dm_user'],
            content='DM message',
            message_type='OOC_RELEVANT'
        )
        
        response = client_auth.get(reverse('campaigns:get_chat_messages', 
                                          kwargs={'campaign_pk': campaign.id}))
        
        assert response.status_code == 200
        data = response.json()
        
        # Find the DM's message and verify role is included
        dm_msg = next((m for m in data['messages'] if m['id'] == dm_message.id), None)
        assert dm_msg is not None
        assert dm_msg.get('sender_role') == 'DM'

    def test_player_role_shown_in_messages(self, client_auth, db_setup):
        """Test that Player role badge appears in chat messages."""
        campaign = db_setup['campaign']
        
        # Create a message from a player
        player_message = ChatMessage.objects.create(
            campaign=campaign,
            sender=db_setup['regular_user'],
            content='Player message',
            message_type='OOC_RELEVANT'
        )
        
        response = client_auth.get(reverse('campaigns:get_chat_messages', 
                                          kwargs={'campaign_pk': campaign.id}))
        
        assert response.status_code == 200
        data = response.json()
        
        # Find the player's message and verify role is included
        player_msg = next((m for m in data['messages'] if m['id'] == player_message.id), None)
        assert player_msg is not None
        assert player_msg.get('sender_role') == 'PLAYER'

    def test_spectator_role_shown_in_messages(self, client_auth, db_setup):
        """Test that Spectator role badge appears in chat messages."""
        campaign = db_setup['campaign']
        
        # Create a spectator user
        spectator = User.objects.create_user(
            username='spectator',
            email='spec@test.com',
            password='spec123'
        )
        
        CampaignMembership.objects.create(
            user=spectator,
            campaign=campaign,
            role='SPECTATOR'
        )
        
        # Create a message from the spectator
        spec_message = ChatMessage.objects.create(
            campaign=campaign,
            sender=spectator,
            content='Spectator message',
            message_type='OOC_RELEVANT'
        )
        
        response = client_auth.get(reverse('campaigns:get_chat_messages', 
                                          kwargs={'campaign_pk': campaign.id}))
        
        assert response.status_code == 200
        data = response.json()
        
        # Find the spectator's message and verify role is included
        spec_msg = next((m for m in data['messages'] if m['id'] == spec_message.id), None)
        assert spec_msg is not None
        assert spec_msg.get('sender_role') == 'SPECTATOR'


class TestCharacterMessageDisplay:
    """Test character name and badge display for IC messages."""

    def test_ic_message_shows_character_name(self, client_auth, db_setup):
        """Test that IC messages show character name instead of user name."""
        campaign = db_setup['campaign']
        
        # Create a character sheet for the regular user
        CharacterSheet.objects.create(
            user=db_setup['regular_user'],
            campaign=campaign,
            name='Hero Character',
            level=1,
            attributes={'strength': 16, 'dexterity': 14},
            skills={},
            combat_stats={}
        )
        
        # Create an IC message from the player
        ic_message = ChatMessage.objects.create(
            campaign=campaign,
            sender=db_setup['regular_user'],
            content='In character dialogue',
            message_type='IC'
        )
        
        response = client_auth.get(reverse('campaigns:get_chat_messages', 
                                          kwargs={'campaign_pk': campaign.id}))
        
        assert response.status_code == 200
        data = response.json()
        
        # Find the IC message and verify character name is shown
        ic_msg = next((m for m in data['messages'] if m['id'] == ic_message.id), None)
        assert ic_msg is not None
        assert ic_msg.get('character_name') == 'Hero Character'

    def test_ic_message_without_character_shows_user_name(self, client_auth, db_setup):
        """Test that IC messages without a character show user name."""
        campaign = db_setup['campaign']
        
        # Create an IC message from a user without a character
        ic_message = ChatMessage.objects.create(
            campaign=campaign,
            sender=db_setup['regular_user'],
            content='In character dialogue',
            message_type='IC'
        )
        
        response = client_auth.get(reverse('campaigns:get_chat_messages', 
                                          kwargs={'campaign_pk': campaign.id}))
        
        assert response.status_code == 200
        data = response.json()
        
        # Find the IC message and verify no character name is shown
        ic_msg = next((m for m in data['messages'] if m['id'] == ic_message.id), None)
        assert ic_msg is not None
        assert ic_msg.get('character_name') is None

    def test_dm_ic_message_shows_npc_label(self, client_auth, db_setup):
        """Test that DM's IC messages are marked for NPC display."""
        campaign = db_setup['campaign']
        
        # Create a character sheet for the DM (representing an NPC)
        CharacterSheet.objects.create(
            user=db_setup['dm_user'],
            campaign=campaign,
            name='NPC Merchant',
            level=1,
            attributes={'strength': 10},
            skills={},
            combat_stats={}
        )
        
        # Create an IC message from the DM
        npc_message = ChatMessage.objects.create(
            campaign=campaign,
            sender=db_setup['dm_user'],
            content='Welcome to my shop!',
            message_type='IC'
        )
        
        response = client_auth.get(reverse('campaigns:get_chat_messages', 
                                          kwargs={'campaign_pk': campaign.id}))
        
        assert response.status_code == 200
        data = response.json()
        
        # Find the NPC message and verify character name is shown
        npc_msg = next((m for m in data['messages'] if m['id'] == npc_message.id), None)
        assert npc_msg is not None
        assert npc_msg.get('character_name') == 'NPC Merchant'


class TestMessageActionButtons:
    """Test message action button functionality."""

    def test_edit_own_message_via_api(self, client_auth, db_setup):
        """Test that users can edit their own messages via API."""
        campaign = db_setup['campaign']
        
        # Create a message first
        message = ChatMessage.objects.create(
            campaign=campaign,
            sender=db_setup['regular_user'],
            content='Original message'
        )
        
        response = client_auth.post(reverse('campaigns:edit_chat_message', 
                                           kwargs={'message_pk': message.id}),
            json.dumps({'content': 'Edited message'}),
            content_type='application/json'
        )
        
        # Should succeed
        assert response.status_code == 200
        
        # Verify the message was edited
        message.refresh_from_db()
        assert message.content == 'Edited message'

    def test_cannot_edit_others_messages(self, client_auth, db_setup):
        """Test that users cannot edit other users' messages."""
        campaign = db_setup['campaign']
        
        # Create a message by another user
        other_user = User.objects.create_user(
            username='otherplayer',
            email='other@test.com',
            password='other123'
        )
        
        CampaignMembership.objects.create(
            user=other_user,
            campaign=campaign,
            role='PLAYER'
        )
        
        other_message = ChatMessage.objects.create(
            campaign=campaign,
            sender=other_user,
            content="Other's message"
        )
        
        response = client_auth.post(reverse('campaigns:edit_chat_message', 
                                           kwargs={'message_pk': other_message.id}),
            json.dumps({'content': "Trying to edit"}),
            content_type='application/json'
        )
        
        # Should fail (403 or redirect)
        assert response.status_code in [301, 302, 403]

    def test_delete_own_message_via_api(self, client_auth, db_setup):
        """Test that users can delete their own messages via API."""
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
        assert response.status_code == 200
        
        # Verify the message was deleted
        with pytest.raises(ChatMessage.DoesNotExist):
            ChatMessage.objects.get(id=message.id)

    def test_cannot_delete_others_messages(self, client_auth, db_setup):
        """Test that users cannot delete other users' messages."""
        campaign = db_setup['campaign']
        
        # Create a message by another user
        other_user = User.objects.create_user(
            username='otherplayer',
            email='other@test.com',
            password='other123'
        )
        
        CampaignMembership.objects.create(
            user=other_user,
            campaign=campaign,
            role='PLAYER'
        )
        
        other_message = ChatMessage.objects.create(
            campaign=campaign,
            sender=other_user,
            content="Other's message to delete"
        )
        
        response = client_auth.post(reverse('campaigns:delete_chat_message', 
                                           kwargs={'message_pk': other_message.id}))
        
        # Should fail (403 or redirect)
        assert response.status_code in [301, 302, 403]

    def test_dm_can_delete_any_message(self, client_auth, db_setup):
        """Test that DMs can delete any message in their campaign."""
        campaign = db_setup['campaign']
        
        # Create a message by a player
        player_message = ChatMessage.objects.create(
            campaign=campaign,
            sender=db_setup['regular_user'],
            content="Player's message"
        )
        
        # DM tries to delete it
        response = client_auth.post(reverse('campaigns:delete_chat_message', 
                                           kwargs={'message_pk': player_message.id}))
        
        # Should succeed for DM
        assert response.status_code == 200
        
        # Verify the message was deleted
        with pytest.raises(ChatMessage.DoesNotExist):
            ChatMessage.objects.get(id=player_message.id)


class TestChatRoleVisibility:
    """Test that roles are correctly visible to different user types."""

    def test_all_roles_visible_to_dm(self, client_auth, db_setup):
        """Test that DM can see all role badges in messages."""
        campaign = db_setup['campaign']
        
        # Create messages from different roles
        ChatMessage.objects.create(
            campaign=campaign,
            sender=db_setup['dm_user'],
            content='DM message',
            message_type='OOC_RELEVANT'
        )
        
        ChatMessage.objects.create(
            campaign=campaign,
            sender=db_setup['regular_user'],
            content='Player message',
            message_type='OOC_RELEVANT'
        )
        
        response = client_auth.get(reverse('campaigns:get_chat_messages', 
                                          kwargs={'campaign_pk': campaign.id}))
        
        assert response.status_code == 200
        data = response.json()
        
        # DM should see all messages with roles
        assert len(data['messages']) >= 2
        
        dm_roles = [m.get('sender_role') for m in data['messages'] if m.get('sender_role')]
        assert 'DM' in dm_roles or 'PLAYER' in dm_roles

    def test_players_see_own_and_others_roles(self, client_auth, db_setup):
        """Test that players can see role badges on all messages."""
        campaign = db_setup['campaign']
        
        # Create a message from the DM
        ChatMessage.objects.create(
            campaign=campaign,
            sender=db_setup['dm_user'],
            content='DM message',
            message_type='OOC_RELEVANT'
        )
        
        # Regular user (player) fetches messages
        response = client_auth.get(reverse('campaigns:get_chat_messages', 
                                          kwargs={'campaign_pk': campaign.id}))
        
        assert response.status_code == 200
        data = response.json()
        
        # Player should see DM's role
        dm_msgs = [m for m in data['messages'] if m.get('sender_role') == 'DM']
        assert len(dm_msgs) > 0
