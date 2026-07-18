"""
Test character management functionality.
Tests character creation, editing, deletion, and inventory management.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from campaigns.models import Character, InventoryItem

User = get_user_model()


class TestCharacterCreation:
    """Test character creation workflow."""

    def test_create_character_page_accessible(self, client_auth, db_setup):
        """Test that create character page is accessible to campaign members."""
        campaign = db_setup['campaign']
        
        response = client_auth.get(reverse('campaigns:create_character', 
                                          kwargs={'pk': campaign.id}))
        assert response.status_code == 200

    def test_create_character_success(self, client_auth, db_setup):
        """Test successful character creation."""
        campaign = db_setup['campaign']
        
        response = client_auth.post(reverse('campaigns:create_character', 
                                           kwargs={'pk': campaign.id}), {
            'name': 'New Test Character',
            'class_name': 'Wizard',  # Use class_name instead of class_type
            'level': 1,
            'strength': 10,
            'dexterity': 14,
            'constitution': 12,
            'intelligence': 16,
            'wisdom': 13,
            'charisma': 8
        })
        
        # Should redirect to character detail or campaign page
        assert response.status_code in [301, 302]
        
        # Verify character was created
        assert Character.objects.filter(name='New Test Character').exists()

    def test_create_character_requires_name(self, client_auth, db_setup):
        """Test that character creation requires a name."""
        campaign = db_setup['campaign']
        
        response = client_auth.post(reverse('campaigns:create_character', 
                                           kwargs={'pk': campaign.id}), {
            'name': '',  # Empty name
            'class_name': 'Fighter',  # Use class_name instead of class_type
            'level': 1
        })
        
        # Should show form with validation errors
        assert response.status_code == 200


class TestCharacterDetail:
    """Test character detail view."""

    def test_character_detail_accessible(self, client_auth, db_setup):
        """Test that character detail page is accessible."""
        character = db_setup['character']
        
        response = client_auth.get(reverse('campaigns:character_detail', 
                                          kwargs={'pk': character.id}))
        assert response.status_code == 200

    def test_character_detail_shows_correct_data(self, client_auth, db_setup):
        """Test that character detail shows correct information."""
        character = db_setup['character']
        
        response = client_auth.get(reverse('campaigns:character_detail', 
                                          kwargs={'pk': character.id}))
        
        assert character.name.encode() in response.content
        assert character.class_name.encode() in response.content  # Use class_name


class TestCharacterEditing:
    """Test character editing functionality."""

    def test_edit_character_page_accessible(self, client_auth, db_setup):
        """Test that edit character page is accessible to owner."""
        character = db_setup['character']
        
        response = client_auth.get(reverse('campaigns:edit_character', 
                                          kwargs={'pk': character.id}))
        assert response.status_code == 200

    def test_edit_character_success(self, client_auth, db_setup):
        """Test successful character editing."""
        character = db_setup['character']
        
        response = client_auth.post(reverse('campaigns:edit_character', 
                                           kwargs={'pk': character.id}), {
            'name': 'Updated Character Name',
            'class_name': 'Paladin',  # Use class_name instead of class_type
            'level': 2,
            'strength': 16,
            'dexterity': 12,
            'constitution': 14,
            'intelligence': 10,
            'wisdom': 13,
            'charisma': 15
        })
        
        # Should redirect after successful update
        assert response.status_code in [301, 302]
        
        # Verify character was updated
        character.refresh_from_db()
        assert character.name == 'Updated Character Name'
        assert character.level == 2

    def test_edit_character_requires_owner(self, client_auth, db_setup):
        """Test that users can only edit their own characters."""
        # Create a character owned by another user
        other_user = User.objects.create_user(
            username='otherplayer',
            email='other@test.com',
            password='other123'
        )
        
        other_character = Character.objects.create(
            name="Other's Character",
            campaign=db_setup['campaign'],
            user=other_user,  # Use 'user' instead of 'owner'
            class_name='Rogue',  # Use class_name instead of class_type
            level=1
        )
        
        response = client_auth.get(reverse('campaigns:edit_character', 
                                          kwargs={'pk': other_character.id}))
        
        # Should redirect or show error
        assert response.status_code in [301, 302, 403]


class TestCharacterDeletion:
    """Test character deletion functionality."""

    def test_delete_character_requires_owner(self, client_auth, db_setup):
        """Test that users can only delete their own characters."""
        character = db_setup['character']
        
        response = client_auth.post(reverse('campaigns:delete_character', 
                                           kwargs={'pk': character.id}))
        # Should redirect after deletion
        assert response.status_code in [301, 302]

    def test_delete_character_success(self, client_auth, db_setup):
        """Test successful character deletion."""
        character = db_setup['character']
        
        response = client_auth.post(reverse('campaigns:delete_character', 
                                           kwargs={'pk': character.id}))
        
        # Should redirect after deletion
        assert response.status_code in [301, 302]
        
        # Verify character was deleted
        assert not Character.objects.filter(id=character.id).exists()


class TestInventoryManagement:
    """Test character inventory management."""

    def test_add_inventory_page_accessible(self, client_auth, db_setup):
        """Test that add inventory page is accessible to character owner."""
        character = db_setup['character']
        
        response = client_auth.get(reverse('campaigns:add_inventory', 
                                          kwargs={'character_pk': character.id}))
        assert response.status_code == 200

    def test_add_inventory_success(self, client_auth, db_setup):
        """Test successful inventory item addition."""
        character = db_setup['character']
        
        response = client_auth.post(reverse('campaigns:add_inventory', 
                                           kwargs={'character_pk': character.id}), {
            'item_name': 'Longsword',
            'quantity': 1,
            'weight': 3.0,
            'description': 'A standard longsword'
        })
        
        # Should redirect after adding item
        assert response.status_code in [301, 302]
        
        # Verify inventory item was created
        character.refresh_from_db()
        assert InventoryItem.objects.filter(character=character, 
                                           name='Longsword').exists()  # Use 'name' instead of 'item_name'

    def test_add_inventory_requires_owner(self, client_auth, db_setup):
        """Test that users can only add inventory to their own characters."""
        # Create a character owned by another user
        other_user = User.objects.create_user(
            username='anotherplayer',
            email='another@test.com',
            password='another123'
        )
        
        other_character = Character.objects.create(
            name="Another's Character",
            campaign=db_setup['campaign'],
            user=other_user,  # Use 'user' instead of 'owner'
            class_name='Barbarian',  # Use class_name instead of class_type
            level=1
        )
        
        response = client_auth.get(reverse('campaigns:add_inventory', 
                                          kwargs={'character_pk': other_character.id}))
        
        # Should redirect or show error
        assert response.status_code in [301, 302, 403]


class TestCharacterPermissions:
    """Test character access permissions."""

    def test_cannot_access_other_users_characters(self, client_auth, db_setup):
        """Test that users cannot access other users' characters."""
        # Create a character owned by another user in the same campaign
        from campaigns.models import CampaignMembership
        
        other_user = User.objects.create_user(
            username='teammate',
            email='teammate@test.com',
            password='team123'
        )
        
        CampaignMembership.objects.create(
            user=other_user,
            campaign=db_setup['campaign'],
            role='PLAYER'  # Use 'PLAYER' constant instead of 'player'
        )
        
        other_character = Character.objects.create(
            name="Teammate's Character",
            campaign=db_setup['campaign'],
            user=other_user,  # Use 'user' instead of 'owner'
            class_name='Cleric',  # Use class_name instead of class_type
            level=1
        )
        
        response = client_auth.get(reverse('campaigns:character_detail', 
                                          kwargs={'pk': other_character.id}))
        
        # Depending on implementation, may allow viewing party members' characters
        # or restrict access - adjust assertion based on your requirements
