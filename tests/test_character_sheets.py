"""
Test new character sheet system with game system templates.
Tests GameSystem, CampaignGameSettings, CharacterSheet models and related views/forms.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from campaigns.models import (
    GameSystem, CampaignGameSettings, CharacterSheet, 
    Campaign, CampaignMembership, InventoryItem
)

User = get_user_model()


class TestGameSystemModel:
    """Test GameSystem model functionality."""

    def test_default_game_systems_exist(self, db):
        """Test that default game systems are created by migration."""
        assert GameSystem.objects.filter(name='Dungeons & Dragons 5e').exists()
        assert GameSystem.objects.filter(name='Pathfinder Second Edition').exists()
        assert GameSystem.objects.filter(name='World of Darkness').exists()

    def test_game_system_has_templates(self, db):
        """Test that game systems have attribute and skill templates."""
        dnd = GameSystem.objects.get(name='Dungeons & Dragons 5e')
        
        assert 'strength' in dnd.attribute_template
        assert 'dexterity' in dnd.attribute_template
        assert len(dnd.skill_template) > 0
        assert 'acrobatics' in dnd.skill_template

    def test_custom_game_system_creation(self, db):
        """Test creating a custom game system."""
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='test123'
        )
        
        custom_system = GameSystem.objects.create(
            name='Custom Homebrew System',
            description='A custom game system',
            is_custom=True,
            created_by=user,
            attribute_template={
                'might': {'label': 'Might', 'type': 'number', 'default': 10},
                'agility': {'label': 'Agility', 'type': 'number', 'default': 10}
            },
            skill_template=['stealth', 'combat'],
            combat_stat_template={
                'hp': {'label': 'Health Points', 'type': 'number', 'default': 20}
            }
        )
        
        assert custom_system.is_custom is True
        assert custom_system.created_by == user
        assert 'might' in custom_system.attribute_template


class TestCampaignGameSettings:
    """Test CampaignGameSettings model functionality."""

    def test_campaign_game_settings_creation(self, db):
        """Test creating game settings for a campaign."""
        game_system = GameSystem.objects.get(name='Dungeons & Dragons 5e')
        
        campaign = Campaign.objects.create(
            title='Test Campaign',
            description='A test campaign'
        )
        
        settings = CampaignGameSettings.objects.create(
            campaign=campaign,
            game_system=game_system,
            rule_book_source='dnd_5e_phb'
        )
        
        assert settings.campaign == campaign
        assert settings.game_system == game_system

    def test_get_effective_attributes(self, db):
        """Test merging base and custom attributes."""
        game_system = GameSystem.objects.get(name='Dungeons & Dragons 5e')
        
        campaign = Campaign.objects.create(title='Test Campaign')
        
        settings = CampaignGameSettings.objects.create(
            campaign=campaign,
            game_system=game_system,
            custom_attributes={'strength': {'default': 16}}
        )
        
        effective_attrs = settings.get_effective_attributes()
        assert 'strength' in effective_attrs

    def test_get_effective_skills(self, db):
        """Test merging base and custom skills."""
        game_system = GameSystem.objects.get(name='Dungeons & Dragons 5e')
        
        campaign = Campaign.objects.create(title='Test Campaign')
        
        settings = CampaignGameSettings.objects.create(
            campaign=campaign,
            game_system=game_system,
            custom_skills=['custom_skill']
        )
        
        effective_skills = settings.get_effective_skills()
        assert 'acrobatics' in effective_skills  # From base template
        assert 'custom_skill' in effective_skills  # Custom addition


class TestCharacterSheetModel:
    """Test CharacterSheet model functionality."""

    def test_character_sheet_creation_with_game_system(self, db):
        """Test creating a character sheet with game system settings."""
        user = User.objects.create_user(
            username='player1',
            email='player1@test.com',
            password='player123'
        )
        
        game_system = GameSystem.objects.get(name='Dungeons & Dragons 5e')
        campaign = Campaign.objects.create(title='Test Campaign')
        
        settings = CampaignGameSettings.objects.create(
            campaign=campaign,
            game_system=game_system
        )
        
        character = CharacterSheet.objects.create(
            user=user,
            campaign=campaign,
            game_settings=settings,
            name='Test Character',
            class_name='Wizard',
            level=1,
            attributes={'strength': 8, 'intelligence': 16},
            skills={'arcana': 5},
            combat_stats={'hp': 10, 'max_hp': 10, 'ac': 12}
        )
        
        assert character.name == 'Test Character'
        assert character.attributes.get('strength') == 8
        assert character.skills.get('arcana') == 5

    def test_character_sheet_without_game_system(self, db):
        """Test creating a character sheet without game system (backward compatibility)."""
        user = User.objects.create_user(
            username='player1',
            email='player1@test.com',
            password='player123'
        )
        
        campaign = Campaign.objects.create(title='Test Campaign')
        
        character = CharacterSheet.objects.create(
            user=user,
            campaign=campaign,
            name='Simple Character',
            class_name='Fighter',
            level=1
        )
        
        assert character.name == 'Simple Character'
        assert character.attributes == {}

    def test_get_attribute_modifier(self, db):
        """Test calculating attribute modifiers."""
        user = User.objects.create_user(
            username='player1',
            email='player1@test.com',
            password='player123'
        )
        
        campaign = Campaign.objects.create(title='Test Campaign')
        
        character = CharacterSheet.objects.create(
            user=user,
            campaign=campaign,
            name='Test Character',
            attributes={'strength': 16}
        )
        
        modifier = character.get_attribute_modifier('strength')
        assert modifier == 3  # (16 - 10) // 2

    def test_proficiency_bonus_by_level(self, db):
        """Test proficiency bonus calculation by level."""
        user = User.objects.create_user(
            username='player1',
            email='player1@test.com',
            password='player123'
        )
        
        campaign = Campaign.objects.create(title='Test Campaign')
        
        character = CharacterSheet.objects.create(
            user=user,
            campaign=campaign,
            name='Test Character',
            level=5
        )
        
        bonus = character.get_proficiency_bonus()
        assert bonus == 3  # Level 5-8 = +3


class TestCharacterSheetCreationView:
    """Test character sheet creation view."""

    @pytest.fixture
    def campaign_with_game_system(self, db):
        """Set up campaign with game system settings."""
        user = User.objects.create_user(
            username='cs_player1',
            email='cs_player1@test.com',
            password='player123'
        )
        
        dm = User.objects.create_superuser(
            username='cs_dm',
            email='cs_dm@test.com',
            password='dm123'
        )
        
        game_system = GameSystem.objects.get(name='Dungeons & Dragons 5e')
        campaign = Campaign.objects.create(title='Test Campaign')
        
        CampaignMembership.objects.create(
            user=user,
            campaign=campaign,
            role='PLAYER'
        )
        
        CampaignMembership.objects.create(
            user=dm,
            campaign=campaign,
            role='DM'
        )
        
        CampaignGameSettings.objects.create(
            campaign=campaign,
            game_system=game_system
        )
        
        return {
            'user': user,
            'campaign': campaign,
            'game_system': game_system
        }

    @pytest.fixture
    def client_cs_auth(self, client, campaign_with_game_system):
        """Authenticated client fixture for character sheet tests."""
        client.force_login(campaign_with_game_system['user'])
        return client

    def test_create_character_page_accessible(self, client_cs_auth, campaign_with_game_system):
        """Test that create character page is accessible."""
        response = client_cs_auth.get(
            reverse('campaigns:create_character', 
                   kwargs={'campaign_pk': campaign_with_game_system['campaign'].id})
        )
        assert response.status_code == 200

    def test_create_character_with_game_system(self, client_cs_auth, campaign_with_game_system):
        """Test creating character with dynamic game system fields."""
        response = client_cs_auth.post(
            reverse('campaigns:create_character', 
                   kwargs={'campaign_pk': campaign_with_game_system['campaign'].id}), {
                'name': 'Dynamic Character',
                'class_name': 'Rogue',
                'level': 1,
                'attr_strength': 14,
                'attr_dexterity': 16,
                'attr_constitution': 12,
                'attr_intelligence': 10,
                'attr_wisdom': 13,
                'attr_charisma': 8,
                'skill_stealth': 5,
                'skill_acrobatics': 3,
                'combat_hp': 10,
                'combat_max_hp': 10,
                'combat_ac': 14,
                'combat_initiative': 0,
                'combat_speed': 30,
                'combat_proficiency_bonus': 2
            }
        )
        
        assert response.status_code in [301, 302], f"Expected redirect but got {response.status_code}"
        assert CharacterSheet.objects.filter(name='Dynamic Character').exists()
        
        character = CharacterSheet.objects.get(name='Dynamic Character')
        assert character.attributes.get('strength') == 14
        assert character.skills.get('stealth') == 5

    def test_create_character_without_game_system(self, client, db):
        """Test creating character without game system settings."""
        user = User.objects.create_user(
            username='player1',
            email='player1@test.com',
            password='player123'
        )
        
        dm = User.objects.create_superuser(
            username='dm',
            email='dm@test.com',
            password='dm123'
        )
        
        campaign = Campaign.objects.create(title='Test Campaign')
        
        CampaignMembership.objects.create(
            user=user,
            campaign=campaign,
            role='PLAYER'
        )
        
        CampaignMembership.objects.create(
            user=dm,
            campaign=campaign,
            role='DM'
        )
        
        client.force_login(user)
        
        response = client.post(
            reverse('campaigns:create_character', 
                   kwargs={'campaign_pk': campaign.id}), {
                'name': 'Simple Character',
                'class_name': 'Fighter',
                'level': 1,
                'strength': 14,
                'dexterity': 12,
                'constitution': 13,
                'intelligence': 10,
                'wisdom': 12,
                'charisma': 10,
                'health_points': 12,
                'max_health_points': 12,
                'armor_class': 14
            }
        )
        
        assert response.status_code in [301, 302]


class TestCharacterSheetEditView:
    """Test character sheet editing view."""

    @pytest.fixture
    def character_with_settings(self, db):
        """Set up character with game system settings."""
        user = User.objects.create_user(
            username='cs_edit_player',
            email='cs_edit_player@test.com',
            password='player123'
        )
        
        dm = User.objects.create_superuser(
            username='cs_edit_dm',
            email='cs_edit_dm@test.com',
            password='dm123'
        )
        
        game_system = GameSystem.objects.get(name='Dungeons & Dragons 5e')
        campaign = Campaign.objects.create(title='Test Campaign')
        
        CampaignMembership.objects.create(
            user=user,
            campaign=campaign,
            role='PLAYER'
        )
        
        CampaignMembership.objects.create(
            user=dm,
            campaign=campaign,
            role='DM'
        )
        
        settings = CampaignGameSettings.objects.create(
            campaign=campaign,
            game_system=game_system
        )
        
        character = CharacterSheet.objects.create(
            user=user,
            campaign=campaign,
            game_settings=settings,
            name='Test Character',
            class_name='Wizard',
            level=1,
            attributes={'strength': 10},
            skills={},
            combat_stats={}
        )
        
        return {
            'user': user,
            'character': character,
            'campaign': campaign
        }

    @pytest.fixture
    def client_cs_edit_auth(self, client, character_with_settings):
        """Authenticated client fixture for edit tests."""
        client.force_login(character_with_settings['user'])
        return client

    def test_edit_character_page_accessible(self, client_cs_edit_auth, character_with_settings):
        """Test that edit character page is accessible to owner."""
        response = client_cs_edit_auth.get(
            reverse('campaigns:edit_character', 
                   kwargs={'pk': character_with_settings['character'].id})
        )
        assert response.status_code == 200

    def test_edit_character_success(self, client_cs_edit_auth, character_with_settings):
        """Test successfully editing a character."""
        response = client_cs_edit_auth.post(
            reverse('campaigns:edit_character', 
                   kwargs={'pk': character_with_settings['character'].id}), {
                'name': 'Updated Character',
                'class_name': 'Sorcerer',
                'level': 2,
                'attr_strength': 10,
                'attr_dexterity': 14,
                'attr_constitution': 13,
                'attr_intelligence': 12,
                'attr_wisdom': 10,
                'attr_charisma': 16,
                'combat_hp': 15,
                'combat_max_hp': 15,
                'combat_ac': 12,
                'combat_initiative': 0,
                'combat_speed': 30,
                'combat_proficiency_bonus': 2
            }
        )
        
        assert response.status_code in [301, 302]
        
        character = CharacterSheet.objects.get(id=character_with_settings['character'].id)
        assert character.name == 'Updated Character'
        assert character.level == 2

    def test_edit_character_requires_owner(self, client_cs_edit_auth, character_with_settings):
        """Test that players cannot edit other players' characters."""
        # Create another player's character
        other_user = User.objects.create_user(
            username='cs_other_player',
            email='cs_other@test.com',
            password='other123'
        )
        
        CampaignMembership.objects.create(
            user=other_user,
            campaign=character_with_settings['campaign'],
            role='PLAYER'
        )
        
        other_character = CharacterSheet.objects.create(
            user=other_user,
            campaign=character_with_settings['campaign'],
            name="Other's Character",
            class_name='Fighter',
            level=1
        )
        
        response = client_cs_edit_auth.get(
            reverse('campaigns:edit_character', 
                   kwargs={'pk': other_character.id})
        )
        
        assert response.status_code in [301, 302, 403]


class TestCharacterSheetDetailView:
    """Test character sheet detail view."""

    def test_character_detail_accessible(self, client, db):
        """Test that character detail page is accessible."""
        user = User.objects.create_user(
            username='cs_view_player',
            email='cs_view_player@test.com',
            password='player123'
        )
        
        campaign = Campaign.objects.create(title='Test Campaign')
        
        CampaignMembership.objects.create(
            user=user,
            campaign=campaign,
            role='PLAYER'
        )
        
        character = CharacterSheet.objects.create(
            user=user,
            campaign=campaign,
            name='View Test Character',
            class_name='Cleric',
            level=1
        )
        
        client.force_login(user)
        
        response = client.get(
            reverse('campaigns:character_detail', 
                   kwargs={'pk': character.id})
        )
        assert response.status_code == 200

    def test_character_detail_shows_game_system(self, client, db):
        """Test that character detail shows game system info."""
        user = User.objects.create_user(
            username='cs_gs_player',
            email='cs_gs_player@test.com',
            password='player123'
        )
        
        dm = User.objects.create_superuser(
            username='cs_gs_dm',
            email='cs_gs_dm@test.com',
            password='dm123'
        )
        
        game_system = GameSystem.objects.get(name='Dungeons & Dragons 5e')
        campaign = Campaign.objects.create(title='Test Campaign')
        
        CampaignMembership.objects.create(
            user=user,
            campaign=campaign,
            role='PLAYER'
        )
        
        CampaignMembership.objects.create(
            user=dm,
            campaign=campaign,
            role='DM'
        )
        
        settings = CampaignGameSettings.objects.create(
            campaign=campaign,
            game_system=game_system
        )
        
        character = CharacterSheet.objects.create(
            user=user,
            campaign=campaign,
            game_settings=settings,
            name='GS Test Character',
            class_name='Wizard'
        )
        
        client.force_login(user)
        
        response = client.get(
            reverse('campaigns:character_detail', 
                   kwargs={'pk': character.id})
        )
        
        assert response.status_code == 200
        # Check that game system info is displayed
        assert b'Game System:' in response.content


class TestCharacterSheetPermissions:
    """Test character sheet access permissions."""

    def test_dm_can_view_all_characters(self, client, db):
        """Test that DMs can view all characters in campaign."""
        user1 = User.objects.create_user(
            username='cs_perm_player',
            email='cs_perm_player@test.com',
            password='player123'
        )
        
        dm = User.objects.create_superuser(
            username='cs_perm_dm',
            email='cs_perm_dm@test.com',
            password='dm123'
        )
        
        campaign = Campaign.objects.create(title='Test Campaign')
        
        CampaignMembership.objects.create(
            user=user1,
            campaign=campaign,
            role='PLAYER'
        )
        
        CampaignMembership.objects.create(
            user=dm,
            campaign=campaign,
            role='DM'
        )
        
        character = CharacterSheet.objects.create(
            user=user1,
            campaign=campaign,
            name="Player's Character",
            class_name='Fighter',
            level=1
        )
        
        client.force_login(dm)
        
        response = client.get(
            reverse('campaigns:character_detail', 
                   kwargs={'pk': character.id})
        )
        
        assert response.status_code == 200

    def test_player_cannot_view_other_players_characters(self, client, db):
        """Test that players cannot view other players' characters."""
        user1 = User.objects.create_user(
            username='cs_perm_player1',
            email='cs_perm_player1@test.com',
            password='player123'
        )
        
        user2 = User.objects.create_user(
            username='cs_perm_player2',
            email='cs_perm_player2@test.com',
            password='player123'
        )
        
        campaign = Campaign.objects.create(title='Test Campaign')
        
        CampaignMembership.objects.create(
            user=user1,
            campaign=campaign,
            role='PLAYER'
        )
        
        CampaignMembership.objects.create(
            user=user2,
            campaign=campaign,
            role='PLAYER'
        )
        
        character = CharacterSheet.objects.create(
            user=user2,
            campaign=campaign,
            name="Other's Character",
            class_name='Rogue',
            level=1
        )
        
        client.force_login(user1)
        
        response = client.get(
            reverse('campaigns:character_detail', 
                   kwargs={'pk': character.id})
        )
        
        assert response.status_code in [301, 302, 403]


class TestInventoryWithCharacterSheet:
    """Test inventory management with CharacterSheet."""

    def test_add_inventory_to_character_sheet(self, client, db):
        """Test adding inventory items to a character sheet."""
        user = User.objects.create_user(
            username='cs_inv_player',
            email='cs_inv_player@test.com',
            password='player123'
        )
        
        campaign = Campaign.objects.create(title='Test Campaign')
        
        CampaignMembership.objects.create(
            user=user,
            campaign=campaign,
            role='PLAYER'
        )
        
        character = CharacterSheet.objects.create(
            user=user,
            campaign=campaign,
            name='Inventory Test',
            class_name='Fighter',
            level=1
        )
        
        client.force_login(user)
        
        response = client.post(
            reverse('campaigns:add_inventory_item', 
                   kwargs={'character_pk': character.id}), {
                'name': 'Longsword',
                'quantity': 1,
                'weight': 3.0,
                'description': 'A sharp sword'
            }
        )
        
        assert response.status_code in [301, 302]
        assert InventoryItem.objects.filter(character_sheet=character, name='Longsword').exists()


class TestCampaignCreationWithGameSystem:
    """Test campaign creation with game system selection."""

    def test_create_campaign_with_game_system(self, client, db):
        """Test creating a campaign with a selected game system."""
        user = User.objects.create_superuser(
            username='cs_camp_dm',
            email='cs_camp_dm@test.com',
            password='dm123'
        )
        
        client.force_login(user)
        
        response = client.post(
            reverse('campaigns:create_campaign'), {
                'title': 'D&D Campaign',
                'description': 'A D&D 5e campaign',
                'game_system': GameSystem.objects.get(name='Dungeons & Dragons 5e').id
            }
        )
        
        assert response.status_code in [301, 302]
        
        campaign = Campaign.objects.get(title='D&D Campaign')
        assert CampaignGameSettings.objects.filter(campaign=campaign).exists()

    def test_create_campaign_without_game_system(self, client, db):
        """Test creating a campaign without selecting a game system."""
        user = User.objects.create_superuser(
            username='cs_camp_dm2',
            email='cs_camp_dm2@test.com',
            password='dm123'
        )
        
        client.force_login(user)
        
        response = client.post(
            reverse('campaigns:create_campaign'), {
                'title': 'Simple Campaign',
                'description': 'A campaign without game system'
            }
        )
        
        assert response.status_code in [301, 302]
        
        campaign = Campaign.objects.get(title='Simple Campaign')
        # Game settings should not exist if not selected
        assert not CampaignGameSettings.objects.filter(campaign=campaign).exists()
