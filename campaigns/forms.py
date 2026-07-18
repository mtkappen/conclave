from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Campaign, Character, InventoryItem


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