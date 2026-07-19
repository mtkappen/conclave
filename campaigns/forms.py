from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Campaign, Character, CharacterSheet, InventoryItem, GameSystem, CampaignGameSettings


class UserSettingsForm(forms.ModelForm):
    """Form for users to edit their profile settings."""
    class Meta:
        model = User
        fields = ['real_name', 'avatar']
        widgets = {
            'real_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class UserRegistrationForm(UserCreationForm):
    """Form for user registration."""
    real_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'real_name', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class AdminUserCreationForm(forms.ModelForm):
    """Form for admin to create new users with default password."""
    real_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    default_password = forms.CharField(
        label='Default Password',
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Temporary Password'})
    )

    class Meta:
        model = User
        fields = ['username', 'real_name']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Set the default password and mark for password change
        user.set_password(self.cleaned_data['default_password'])
        user.must_change_password = True
        if commit:
            user.save()
        return user


class PasswordChangeForm(forms.Form):
    """Form for users to change their password on first login."""
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        
        if password1 and len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        return cleaned_data


class UserPasswordChangeForm(forms.Form):
    """Form for users to voluntarily change their password."""
    current_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        password = self.cleaned_data.get('current_password')
        if not self.user.check_password(password):
            raise forms.ValidationError("Current password is incorrect.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        
        if password1 and len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        # Prevent using the same password
        if password1 and self.user.check_password(password1):
            raise forms.ValidationError("New password cannot be the same as your current password.")
        
        return cleaned_data


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with better labels."""
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class CampaignForm(forms.ModelForm):
    """Form for creating/editing campaigns."""
    class Meta:
        model = Campaign
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CharacterForm(forms.ModelForm):
    """Form for creating/editing character sheets."""
    class Meta:
        model = Character
        fields = ['name', 'class_name', 'level', 'strength', 'dexterity', 
                  'constitution', 'intelligence', 'wisdom', 'charisma',
                  'health_points', 'max_health_points', 'armor_class', 
                  'avatar', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'class_name': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.NumberInput(attrs={'class': 'form-control'}),
            'strength': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
            'dexterity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
            'constitution': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
            'intelligence': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
            'wisdom': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
            'charisma': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
            'health_points': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_health_points': forms.NumberInput(attrs={'class': 'form-control'}),
            'armor_class': forms.NumberInput(attrs={'class': 'form-control'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class GameSystemForm(forms.ModelForm):
    """Form for creating custom game systems."""
    class Meta:
        model = GameSystem
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CampaignGameSettingsForm(forms.ModelForm):
    """Form for DM to configure game system for a campaign."""
    class Meta:
        model = CampaignGameSettings
        fields = ['game_system', 'rule_book_source', 'rule_book_title']
        widgets = {
            'game_system': forms.Select(attrs={'class': 'form-control'}),
            'rule_book_source': forms.TextInput(attrs={'class': 'form-control'}),
            'rule_book_title': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CharacterSheetForm(forms.Form):
    """Dynamic form for character sheet creation/editing based on game system."""
    
    # Basic info fields
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    class_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Class/Archetype'}))
    level = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    background = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    avatar = forms.ImageField(required=False)
    
    def __init__(self, *args, **kwargs):
        self.game_settings = kwargs.pop('game_settings', None)
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        
        if self.game_settings:
            # Add dynamic attribute fields
            attributes = self.game_settings.get_effective_attributes()
            for attr_key, attr_config in attributes.items():
                field_name = f'attr_{attr_key}'
                default = attr_config.get('default', 10)
                min_val = attr_config.get('min', 1)
                max_val = attr_config.get('max', 30)
                label = attr_config.get('label', attr_key.title())
                
                # Use existing value if editing, otherwise use default
                initial_value = None
                if self.instance and hasattr(self.instance, 'attributes'):
                    initial_value = self.instance.attributes.get(attr_key)
                
                self.fields[field_name] = forms.IntegerField(
                    min_value=min_val,
                    max_value=max_val,
                    initial=initial_value if initial_value is not None else default,
                    label=label,
                    widget=forms.NumberInput(attrs={'class': 'form-control'})
                )
            
            # Add dynamic skill fields
            skills = self.game_settings.get_effective_skills()
            for skill in skills:
                field_name = f'skill_{skill}'
                
                # Use existing value if editing, otherwise use 0
                initial_value = None
                if self.instance and hasattr(self.instance, 'skills'):
                    initial_value = self.instance.skills.get(skill)
                
                self.fields[field_name] = forms.IntegerField(
                    min_value=0,
                    initial=initial_value if initial_value is not None else 0,
                    label=skill.replace('_', ' ').title(),
                    required=False,
                    widget=forms.NumberInput(attrs={'class': 'form-control'})
                )
            
            # Add dynamic combat stat fields
            combat_stats = self.game_settings.game_system.combat_stat_template
            for stat_key, stat_config in combat_stats.items():
                field_name = f'combat_{stat_key}'
                default = stat_config.get('default', 0)
                label = stat_config.get('label', stat_key.title())
                
                # Use existing value if editing, otherwise use default
                initial_value = None
                if self.instance and hasattr(self.instance, 'combat_stats'):
                    initial_value = self.instance.combat_stats.get(stat_key)
                
                self.fields[field_name] = forms.IntegerField(
                    min_value=0,
                    initial=initial_value if initial_value is not None else default,
                    label=label,
                    widget=forms.NumberInput(attrs={'class': 'form-control'})
                )

    def save(self, commit=True):
        """Save character sheet with dynamic data."""
        # Use existing instance if provided (for editing), otherwise create new
        if self.instance and self.instance.pk:
            instance = self.instance
        else:
            instance = CharacterSheet()
        
        # Basic fields
        instance.name = self.cleaned_data['name']
        instance.class_name = self.cleaned_data.get('class_name', '')
        instance.level = self.cleaned_data['level']
        instance.background = self.cleaned_data.get('background', '')
        instance.description = self.cleaned_data.get('description', '')
        
        if 'avatar' in self.cleaned_data:
            instance.avatar = self.cleaned_data['avatar']
        
        # Collect dynamic data
        attributes = {}
        skills = {}
        combat_stats = {}
        
        if self.game_settings:
            # Extract attribute values
            for attr_key in self.game_settings.get_effective_attributes().keys():
                field_name = f'attr_{attr_key}'
                if field_name in self.cleaned_data:
                    attributes[attr_key] = self.cleaned_data[field_name]
            
            # Extract skill values
            for skill in self.game_settings.get_effective_skills():
                field_name = f'skill_{skill}'
                if field_name in self.cleaned_data and self.cleaned_data[field_name]:
                    skills[skill] = self.cleaned_data[field_name]
            
            # Extract combat stats
            for stat_key in self.game_settings.game_system.combat_stat_template.keys():
                field_name = f'combat_{stat_key}'
                if field_name in self.cleaned_data:
                    combat_stats[stat_key] = self.cleaned_data[field_name]
        
        instance.attributes = attributes
        instance.skills = skills
        instance.combat_stats = combat_stats
        
        if commit:
            instance.save()
        
        return instance


class InventoryItemForm(forms.ModelForm):
    """Form for adding/editing inventory items."""
    class Meta:
        model = InventoryItem
        fields = ['name', 'quantity', 'weight', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class ChatMessageForm(forms.Form):
    """Form for posting chat messages."""
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Type your message...'}))
    message_type = forms.ChoiceField(choices=[
        ('IC', 'In-Character'),
        ('OOC_RELEVANT', 'Out-of-Character Relevant'),
        ('OOC_OFFTOPIC', 'Out-of-Character Off Topic'),
    ], widget=forms.Select(attrs={'class': 'form-control'}))
    visibility_type = forms.ChoiceField(choices=[
        ('PUBLIC', 'Public'),
        ('DM_ONLY', 'Send to DM Only'),
    ], widget=forms.Select(attrs={'class': 'form-control'}))


class DiceRollForm(forms.Form):
    """Form for rolling dice."""
    num_dice = forms.IntegerField(min_value=1, max_value=20, initial=1)
    die_type = forms.ChoiceField(choices=[
        (4, 'd4'),
        (6, 'd6'),
        (8, 'd8'),
        (10, 'd10'),
        (12, 'd12'),
        (20, 'd20'),
    ], initial=20)
    modifier = forms.IntegerField(initial=0)
    is_hidden = forms.BooleanField(required=False, help_text="Hide from players (DM only)")


class FirstTimeAdminSetupForm(forms.Form):
    """Form for first-time admin to set up their account."""
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'})
    )
    real_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'})
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Choose a strong password'}),
        help_text='Must be at least 8 characters long.'
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'})
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        
        if password1 and len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        return password2


class DatabaseResetForm(forms.Form):
    """Form for confirming database reset."""
    confirm = forms.BooleanField(
        required=True,
        label='I understand this will permanently delete ALL data',
        help_text='This action cannot be undone. All campaigns, users, characters, messages, and other data will be deleted.'
    )