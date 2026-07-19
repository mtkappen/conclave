from decimal import Decimal
import json
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


def validate_json(value):
    """Validate that a field contains valid JSON."""
    try:
        if isinstance(value, str):
            json.loads(value)
        elif isinstance(value, (dict, list)):
            pass  # Already parsed JSON
        else:
            raise ValidationError("Must be valid JSON")
    except json.JSONDecodeError:
        raise ValidationError("Must be valid JSON")


class GameSystem(models.Model):
    """Predefined or custom game systems for character sheets."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_custom = models.BooleanField(default=False, help_text="True if created by a user")
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True)
    
    # Templates stored as JSON
    attribute_template = models.JSONField(
        default=dict, 
        help_text="Predefined attributes (e.g., {'strength': {'label': 'Strength', 'type': 'number', 'default': 10}})"
    )
    skill_template = models.JSONField(
        default=list, 
        help_text="Predefined skills list"
    )
    combat_stat_template = models.JSONField(
        default=dict,
        help_text="Combat stats template (HP, AC, etc.)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name}{' (Custom)' if self.is_custom else ''}"


class CampaignGameSettings(models.Model):
    """Game system settings for a specific campaign."""
    campaign = models.OneToOneField('Campaign', on_delete=models.CASCADE, related_name='game_settings')
    game_system = models.ForeignKey('GameSystem', on_delete=models.PROTECT)
    
    # Customizations
    custom_attributes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Attribute overrides/additions for this campaign"
    )
    custom_skills = models.JSONField(
        default=list,
        blank=True,
        help_text="Skill overrides/additions for this campaign"
    )
    
    # Rule book configuration
    rule_book_source = models.CharField(
        max_length=100,
        default='custom',
        help_text="Official rulebook ID or 'custom' for custom content"
    )
    rule_book_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Title of the selected rule book"
    )
    
    # Visibility settings (JSON)
    field_visibility = models.JSONField(
        default=dict,
        blank=True,
        help_text="Visibility rules for fields: 'public', 'player_only', 'dm_only'"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.campaign.title} - {self.game_system.name}"

    def get_effective_attributes(self):
        """Merge base template with custom attributes."""
        attrs = dict(self.game_system.attribute_template)
        attrs.update(self.custom_attributes)
        return attrs

    def get_effective_skills(self):
        """Merge base skills with custom skills."""
        skills = list(self.game_system.skill_template)
        for custom in self.custom_skills:
            if custom not in skills:
                skills.append(custom)
        return skills


class CharacterSheet(models.Model):
    """Flexible character sheet supporting any game system."""
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    campaign = models.ForeignKey('Campaign', on_delete=models.CASCADE)
    game_settings = models.ForeignKey('CampaignGameSettings', on_delete=models.PROTECT, null=True, blank=True)
    
    # Basic info
    name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=100, blank=True, help_text="Character class/archetype")
    level = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    background = models.CharField(max_length=200, blank=True)
    
    # Dynamic data stored as JSON
    attributes = models.JSONField(
        default=dict,
        help_text="Attribute values: {'strength': 16, 'dexterity': 14, ...}"
    )
    skills = models.JSONField(
        default=dict,
        help_text="Skill values: {'acrobatics': 5, 'stealth': 3, ...}"
    )
    combat_stats = models.JSONField(
        default=dict,
        help_text="Combat stats: {'hp': 10, 'max_hp': 10, 'ac': 12, ...}"
    )
    
    # Spell tracking (for magic systems)
    spell_slots = models.JSONField(
        default=dict,
        blank=True,
        help_text="Spell slots by level: {'1': 4, '2': 3, ...}"
    )
    known_spells = models.JSONField(
        default=list,
        blank=True,
        help_text="List of known spells with details"
    )
    prepared_spells = models.JSONField(
        default=list,
        blank=True,
        help_text="Currently prepared spells"
    )
    
    # Custom fields for anything else
    custom_fields = models.JSONField(
        default=dict,
        blank=True,
        help_text="Any additional custom fields"
    )
    
    # Inventory (keeping separate model for better querying)
    # Still use InventoryItem model with character_sheet foreign key
    
    avatar = models.ImageField(upload_to='characters/', null=True, blank=True)
    description = models.TextField(blank=True)
    
    # Visibility overrides per field (JSON)
    field_visibility = models.JSONField(
        default=dict,
        blank=True,
        help_text="Per-field visibility: {'strength': 'public', 'secret_notes': 'dm_only'}"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'campaign', 'name')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.class_name}) - {self.campaign.title}"

    def get_attribute_modifier(self, attribute_name):
        """Calculate modifier for D&D-style attributes: (value - 10) // 2."""
        value = self.attributes.get(attribute_name, 10)
        return (int(value) - 10) // 2

    def get_proficiency_bonus(self, level=None):
        """D&D 5e proficiency bonus by level."""
        if level is None:
            level = self.level
        if level < 5:
            return 2
        elif level < 9:
            return 3
        elif level < 13:
            return 4
        elif level < 17:
            return 5
        else:
            return 6


class User(AbstractUser):
    """Custom user model with real name and avatar."""
    real_name = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    must_change_password = models.BooleanField(default=False, help_text="User must change password on next login")

    def __str__(self):
        return self.real_name or self.username


class Campaign(models.Model):
    """D&D Campaign with title and description."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Last update timestamp
    last_message_date = models.DateTimeField(null=True, blank=True, help_text="Timestamp of the most recent chat message")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    def get_member_count(self):
        """Return total number of members in campaign."""
        return self.campaignmembership_set.count()
    
    def get_player_count(self):
        """Return number of players (excluding DM and Spectators)."""
        return self.campaignmembership_set.filter(role='PLAYER').count()
    
    def get_dm(self):
        """Return the Dungeon Master for this campaign."""
        dm_membership = self.campaignmembership_set.filter(role='DM').first()
        return dm_membership.user if dm_membership else None
    
    def update_last_message_date(self):
        """Update the last message date to now."""
        from django.utils import timezone
        self.last_message_date = timezone.now()
        self.save(update_fields=['last_message_date'])


class CampaignMembership(models.Model):
    """Links users to campaigns with specific roles."""
    ROLE_CHOICES = [
        ('DM', 'Dungeon Master'),
        ('PLAYER', 'Player'),
        ('SPECTATOR', 'Spectator'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'campaign')

    def __str__(self):
        return f"{self.user.username} - {self.campaign.title} ({self.get_role_display()})"
    
    def get_character_name(self):
        """Return the character name if user has a character in this campaign, else None."""
        try:
            character = Character.objects.filter(user=self.user, campaign=self.campaign).first()
            return character.name if character else None
        except:
            return None
    
    def get_display_name(self):
        """Return display name with character name if available."""
        user_display = self.user.real_name or self.user.username
        char_name = self.get_character_name()
        if char_name and self.role == 'PLAYER':
            return f"{user_display} ({char_name})"
        return user_display


class Character(models.Model):
    """Character sheet for a player in a campaign."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=50, help_text="Character class (e.g., Fighter, Wizard)")
    level = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Stats
    strength = models.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(20)])
    dexterity = models.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(20)])
    constitution = models.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(20)])
    intelligence = models.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(20)])
    wisdom = models.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(20)])
    charisma = models.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(20)])
    
    # Combat stats
    health_points = models.IntegerField(default=10)
    max_health_points = models.IntegerField(default=10)
    armor_class = models.IntegerField(default=10)
    
    avatar = models.ImageField(upload_to='characters/', null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'campaign', 'name')

    def __str__(self):
        return f"{self.name} ({self.class_name}) - {self.campaign.title}"


class InventoryItem(models.Model):
    """Items belonging to a character."""
    character = models.ForeignKey(Character, on_delete=models.CASCADE, null=True, blank=True)
    character_sheet = models.ForeignKey(CharacterSheet, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    weight = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.0'))
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='inventory/', null=True, blank=True)

    def __str__(self):
        if self.character_sheet:
            return f"{self.name} x{self.quantity} ({self.character_sheet.name})"
        return f"{self.name} x{self.quantity} ({self.character.name})"


class PartyGroup(models.Model):
    """Groups for split-party mode during sessions."""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # e.g., "Group A", "Exploration Team"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.campaign.title} - {self.name}"


class PartyGroupMember(models.Model):
    """Links players to party groups."""
    group = models.ForeignKey(PartyGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')

    def __str__(self):
        username = self.user.username if self.user else "Deleted User"
        return f"{username} in {self.group.name}"


class ChatMessage(models.Model):
    """Chat messages with visibility controls."""
    VISIBILITY_CHOICES = [
        ('PUBLIC', 'Public'),
        ('DM_ONLY', 'DM Only - DM and sender only'),
        ('SECRET_WHISPER', 'Secret Whisper - Selected recipients only (excludes DM)'),
        ('SPLIT_GROUP', 'Split Group'),
    ]

    TYPE_CHOICES = [
        ('IC', 'In-Character'),
        ('OOC_RELEVANT', 'Out-of-Character Relevant'),
        ('OOC_OFFTOPIC', 'Out-of-Character Off Topic'),
        ('DICE_ROLL', 'Dice Roll'),
    ]

    content = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    
    visibility_type = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='PUBLIC')
    party_group = models.ForeignKey(PartyGroup, null=True, blank=True, on_delete=models.SET_NULL)
    reveal_status = models.BooleanField(default=False, help_text="True if revealed to all after split")
    
    message_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='OOC_RELEVANT')
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # For whispers: track specific recipients (many-to-many for multiple recipients)
    recipients = models.ManyToManyField(User, blank=True, related_name='received_whispers', help_text="Specific recipients for whisper messages")
    
    # Store sender's name at time of creation for archival purposes
    sender_username = models.CharField(max_length=150, blank=True, help_text="Username at time of posting (preserved after user deletion)")
    sender_real_name = models.CharField(max_length=100, blank=True, help_text="Real name at time of posting (preserved after user deletion)")
    
    # For NPC chat: track which character the DM is posting as
    npc_character_id = models.IntegerField(null=True, blank=True, help_text="CharacterSheet ID when DM posts as an NPC")
    npc_character_name = models.CharField(max_length=100, blank=True, help_text="NPC name at time of posting")

    def __str__(self):
        return f"{self.get_sender_display_name()}: {self.content[:50]}..."
    
    def get_sender_display_name(self):
        """Return display name for sender, preserving original name even if deleted."""
        # Use stored name if available (user was deleted)
        if self.sender_username:
            return self.sender_real_name or self.sender_username
        # Otherwise use current user data
        if self.sender:
            return self.sender.real_name or self.sender.username
        return "Unknown"
    
    def save(self, *args, **kwargs):
        # Store sender's name before saving for archival purposes
        if self.sender and not self.sender_username:
            self.sender_username = self.sender.username
            self.sender_real_name = self.sender.real_name or ''
        
        # Update campaign's last message date when saving a new message
        super().save(*args, **kwargs)
        if self.created_at:
            self.campaign.update_last_message_date()
    
    def get_npc_avatar_url(self):
        """Get the avatar URL for the NPC character if posting as an NPC."""
        if not self.npc_character_id:
            return None
        try:
            from .models import CharacterSheet
            char = CharacterSheet.objects.get(pk=self.npc_character_id)
            if char.avatar:
                return char.avatar.url
        except:
            pass
        return None


class DiceRollLog(models.Model):
    """Logs of dice rolls."""
    VISIBILITY_CHOICES = [
        ('PUBLIC', 'Public'),
        ('DM_ONLY', 'DM Only'),
    ]

    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    
    formula = models.CharField(max_length=100)  # e.g., "2d6+3"
    result = models.IntegerField()
    modifier = models.IntegerField(default=0)
    
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='PUBLIC')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Store sender's name at time of creation for archival purposes
    sender_username = models.CharField(max_length=150, blank=True, help_text="Username at time of rolling (preserved after user deletion)")
    sender_real_name = models.CharField(max_length=100, blank=True, help_text="Real name at time of rolling (preserved after user deletion)")

    def __str__(self):
        return f"{self.get_sender_display_name()}: {self.formula} = {self.result}"
    
    def get_sender_display_name(self):
        """Return display name for sender, preserving original name even if deleted."""
        # Use stored name if available (user was deleted)
        if self.sender_username:
            return self.sender_real_name or self.sender_username
        # Otherwise use current user data
        if self.sender:
            return self.sender.real_name or self.sender.username
        return "Unknown"
    
    def save(self, *args, **kwargs):
        # Store sender's name before saving for archival purposes
        if self.sender and not self.sender_username:
            self.sender_username = self.sender.username
            self.sender_real_name = self.sender.real_name or ''
        
        super().save(*args, **kwargs)


class PersonalNotebook(models.Model):
    """Personal notebook for a user in a campaign - only visible to the owner."""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'campaign')  # One notebook per user per campaign
    
    def __str__(self):
        return f"{self.title} ({self.user.username} - {self.campaign.title})"


class CampaignRuleBook(models.Model):
    """Campaign rule book - visible to all members, editable only by DM."""
    campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE, related_name='rule_book')
    title = models.CharField(max_length=200, default="Campaign Rule Book")
    
    # Link to game settings if using official rulebook
    game_settings = models.ForeignKey(CampaignGameSettings, on_delete=models.SET_NULL, null=True, blank=True)
    
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Rule Book for {self.campaign.title}"


# Default game system templates (created via migration or management command)
DEFAULT_GAME_SYSTEMS = {
    'dnd_5e': {
        'name': 'Dungeons & Dragons 5e',
        'description': 'Dungeons & Dragons Fifth Edition',
        'attribute_template': {
            'strength': {'label': 'Strength', 'type': 'number', 'default': 10, 'min': 1, 'max': 30},
            'dexterity': {'label': 'Dexterity', 'type': 'number', 'default': 10, 'min': 1, 'max': 30},
            'constitution': {'label': 'Constitution', 'type': 'number', 'default': 10, 'min': 1, 'max': 30},
            'intelligence': {'label': 'Intelligence', 'type': 'number', 'default': 10, 'min': 1, 'max': 30},
            'wisdom': {'label': 'Wisdom', 'type': 'number', 'default': 10, 'min': 1, 'max': 30},
            'charisma': {'label': 'Charisma', 'type': 'number', 'default': 10, 'min': 1, 'max': 30},
        },
        'skill_template': [
            'acrobatics', 'animal_handling', 'arcana', 'athletics', 'deception',
            'history', 'insight', 'intimidation', 'investigation', 'medicine',
            'nature', 'perception', 'performance', 'persuasion', 'religion',
            'sleight_of_hand', 'stealth', 'survival'
        ],
        'combat_stat_template': {
            'hp': {'label': 'Current HP', 'type': 'number', 'default': 10},
            'max_hp': {'label': 'Max HP', 'type': 'number', 'default': 10},
            'ac': {'label': 'Armor Class', 'type': 'number', 'default': 10},
            'initiative': {'label': 'Initiative', 'type': 'number', 'default': 0},
            'speed': {'label': 'Speed', 'type': 'number', 'default': 30},
            'proficiency_bonus': {'label': 'Proficiency Bonus', 'type': 'number', 'default': 2},
        }
    },
    'pathfinder_2e': {
        'name': 'Pathfinder Second Edition',
        'description': 'Pathfinder RPG Second Edition',
        'attribute_template': {
            'strength': {'label': 'Strength', 'type': 'number', 'default': 10},
            'dexterity': {'label': 'Dexterity', 'type': 'number', 'default': 10},
            'constitution': {'label': 'Constitution', 'type': 'number', 'default': 10},
            'intelligence': {'label': 'Intelligence', 'type': 'number', 'default': 10},
            'wisdom': {'label': 'Wisdom', 'type': 'number', 'default': 10},
            'charisma': {'label': 'Charisma', 'type': 'number', 'default': 10},
        },
        'skill_template': [
            'acrobatics', 'arcana', 'athletics', 'crafting', 'deception', 'diplomacy',
            'intimidation', 'investigation', 'medicine', 'nature', 'occultism',
            'performance', 'religion', 'society', 'stealth', 'survival', 'thievery'
        ],
        'combat_stat_template': {
            'hp': {'label': 'Current HP', 'type': 'number', 'default': 10},
            'max_hp': {'label': 'Max HP', 'type': 'number', 'default': 10},
            'ac': {'label': 'Armor Class', 'type': 'number', 'default': 10},
            'tac': {'label': 'Tactical AC', 'type': 'number', 'default': 10},
            'will_dc': {'label': 'Will DC', 'type': 'number', 'default': 10},
            'reflex_dc': {'label': 'Reflex DC', 'type': 'number', 'default': 10},
            'perception': {'label': 'Perception', 'type': 'number', 'default': 0},
            'speed': {'label': 'Speed', 'type': 'number', 'default': 25},
        }
    },
    'world_of_darkness': {
        'name': 'World of Darkness',
        'description': 'Vampire: The Masquerade / World of Darkness',
        'attribute_template': {
            'intelligence': {'label': 'Intelligence', 'type': 'number', 'default': 1, 'min': 0, 'max': 5},
            'wits': {'label': 'Wits', 'type': 'number', 'default': 1, 'min': 0, 'max': 5},
            'presence': {'label': 'Presence', 'type': 'number', 'default': 1, 'min': 0, 'max': 5},
            'strength': {'label': 'Strength', 'type': 'number', 'default': 1, 'min': 0, 'max': 5},
            'dexterity': {'label': 'Dexterity', 'type': 'number', 'default': 1, 'min': 0, 'max': 5},
            'stamina': {'label': 'Stamina', 'type': 'number', 'default': 1, 'min': 0, 'max': 5},
            'charisma': {'label': 'Charisma', 'type': 'number', 'default': 1, 'min': 0, 'max': 5},
            'manipulation': {'label': 'Manipulation', 'type': 'number', 'default': 1, 'min': 0, 'max': 5},
            'composure': {'label': 'Composure', 'type': 'number', 'default': 1, 'min': 0, 'max': 5},
        },
        'skill_template': [
            'athletics', 'brawl', 'drive', 'firearms', 'larceny', 'stealth', 'survival',
            'awareness', 'empathy', 'expression', 'intimidation', 'leadership', 'performance',
            'science', 'slang', 'streetwise', 'subterfuge'
        ],
        'combat_stat_template': {
            'health': {'label': 'Health Levels', 'type': 'number', 'default': 7},
            'willpower': {'label': 'Willpower', 'type': 'number', 'default': 3},
            'defense': {'label': 'Defense', 'type': 'number', 'default': 0},
            'initiative': {'label': 'Initiative', 'type': 'number', 'default': 0},
        }
    },
}