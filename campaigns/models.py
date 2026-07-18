from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


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
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    weight = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.0'))
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='inventory/', null=True, blank=True)

    def __str__(self):
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