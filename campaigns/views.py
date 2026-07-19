from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.html import escape
import json
import re

from .models import User, Campaign, CampaignMembership, Character, CharacterSheet, InventoryItem, ChatMessage, DiceRollLog, PartyGroup, PartyGroupMember, PersonalNotebook, CampaignRuleBook, GameSystem, CampaignGameSettings
from .forms import AdminUserCreationForm, CustomAuthenticationForm, CampaignForm, CharacterForm, CharacterSheetForm, InventoryItemForm, PasswordChangeForm, UserPasswordChangeForm, FirstTimeAdminSetupForm, DatabaseResetForm, UserSettingsForm


def first_time_admin_setup(request):
    """View for first-time admin to set up their account."""
    # Check if any users exist - if so, redirect to login
    if User.objects.exists():
        return redirect('campaigns:login')
    
    if request.method == 'POST':
        form = FirstTimeAdminSetupForm(request.POST)
        if form.is_valid():
            # Create the first user as superuser (email set to empty string since not used)
            user = User.objects.create_superuser(
                username=form.cleaned_data['username'],
                real_name=form.cleaned_data['real_name'],
                password=form.cleaned_data['password1'],
                email=''  # Email field required by Django but not used in this app
            )
            
            messages.success(request, 'Welcome! Your administrator account has been created.')
            return redirect('campaigns:dashboard')
    else:
        form = FirstTimeAdminSetupForm()
    
    return render(request, 'registration/first_time_setup.html', {'form': form})


def custom_login(request):
    """Custom login view with password change enforcement."""
    # Redirect to first-time setup if no users exist
    if not User.objects.exists():
        return redirect('campaigns:first_time_setup')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Check if user must change password
            if user.must_change_password:
                login(request, user)
                return redirect('campaigns:change_password')
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.real_name or user.username}!')
            return redirect('campaigns:dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def change_password(request):
    """Force users to change password on first login."""
    user = request.user
    
    # Only redirect if password must be changed
    if not user.must_change_password:
        return redirect('campaigns:dashboard')
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password1'])
            user.must_change_password = False
            user.save()
            
            messages.success(request, 'Password changed successfully!')
            return redirect('campaigns:dashboard')
    else:
        form = PasswordChangeForm()
    
    return render(request, 'registration/change_password.html', {'form': form})


@login_required
def voluntary_change_password(request):
    """Allow any authenticated user (including admins) to change their password voluntarily."""
    if request.method == 'POST':
        form = UserPasswordChangeForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('campaigns:dashboard')
    else:
        form = UserPasswordChangeForm(user=request.user)
    
    return render(request, 'registration/voluntary_change_password.html', {'form': form})


@login_required
def user_settings(request):
    """Allow users to edit their profile settings (real name, avatar, password)."""
    if request.method == 'POST':
        settings_form = UserSettingsForm(request.POST, request.FILES, instance=request.user)
        
        if settings_form.is_valid():
            settings_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('campaigns:dashboard')
    else:
        settings_form = UserSettingsForm(instance=request.user)
    
    # Calculate user statistics
    campaign_count = CampaignMembership.objects.filter(user=request.user).count()
    message_count = ChatMessage.objects.filter(sender=request.user).count()
    character_count = Character.objects.filter(user=request.user).count()
    dice_roll_count = DiceRollLog.objects.filter(sender=request.user).count()
    
    return render(request, 'registration/user_settings.html', {
        'settings_form': settings_form,
        'campaign_count': campaign_count,
        'message_count': message_count,
        'character_count': character_count,
        'dice_roll_count': dice_roll_count,
    })


@login_required
def admin_create_user(request):
    """Admin-only view to create new users."""
    # Check if user is super admin (only one allowed)
    if not request.user.is_superuser:
        messages.error(request, 'Only the system administrator can create users.')
        return redirect('campaigns:dashboard')
    
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, 
                f'User "{user.username}" created successfully. Default password: {form.cleaned_data["default_password"]}. User must change password on first login.'
            )
            return redirect('campaigns:admin_user_list')
    else:
        form = AdminUserCreationForm()
    
    return render(request, 'registration/admin_create_user.html', {'form': form})


@login_required
def admin_user_list(request):
    """Admin-only view to list all users."""
    if not request.user.is_superuser:
        messages.error(request, 'Only the system administrator can view user list.')
        return redirect('campaigns:dashboard')
    
    users = User.objects.all().order_by('username')
    
    # Calculate campaign counts for each user
    user_data = []
    for user in users:
        membership_count = CampaignMembership.objects.filter(user=user).count()
        character_count = Character.objects.filter(user=user).count()
        message_count = ChatMessage.objects.filter(sender=user).count()
        
        user_data.append({
            'user': user,
            'membership_count': membership_count,
            'character_count': character_count,
            'message_count': message_count,
        })
    
    return render(request, 'registration/admin_user_list.html', {'user_data': user_data})


@login_required
def delete_user(request, pk):
    """Admin-only view to delete a user. Preserves chat history."""
    if not request.user.is_superuser:
        messages.error(request, 'Only the system administrator can delete users.')
        return redirect('campaigns:admin_user_list')
    
    user = get_object_or_404(User, pk=pk)
    
    # Prevent deleting the superuser themselves
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('campaigns:admin_user_list')
    
    # Get related data counts for confirmation message
    membership_count = CampaignMembership.objects.filter(user=user).count()
    character_count = Character.objects.filter(user=user).count()
    message_count = ChatMessage.objects.filter(sender=user).count()
    dice_roll_count = DiceRollLog.objects.filter(sender=user).count()
    
    if request.method == 'POST':
        username = user.username
        
        # Delete related data first (memberships, characters)
        # Chat messages and dice rolls will remain with sender set to NULL but names preserved
        
        # First, ensure all existing messages/rolls have their names stored
        # This handles any old records that might not have the fields populated yet
        for msg in ChatMessage.objects.filter(sender=user):
            if not msg.sender_username:
                msg.sender_username = user.username
                msg.sender_real_name = user.real_name or ''
                msg.save(update_fields=['sender_username', 'sender_real_name'])
        
        for roll in DiceRollLog.objects.filter(sender=user):
            if not roll.sender_username:
                roll.sender_username = user.username
                roll.sender_real_name = user.real_name or ''
                roll.save(update_fields=['sender_username', 'sender_real_name'])
        
        # Delete memberships
        CampaignMembership.objects.filter(user=user).delete()
        
        # Delete characters (this will also delete their inventory items due to CASCADE)
        Character.objects.filter(user=user).delete()
        
        # Set sender to NULL for chat messages and dice rolls (names already preserved in fields)
        ChatMessage.objects.filter(sender=user).update(sender=None)
        DiceRollLog.objects.filter(sender=user).update(sender=None)
        PartyGroupMember.objects.filter(user=user).update(user=None)
        
        # Finally delete the user
        user.delete()
        
        messages.success(request, f'User "{username}" has been deleted. Their chat history and dice rolls have been preserved with their original names intact.')
        return redirect('campaigns:admin_user_list')
    
    context = {
        'object': user,
        'object_type': 'user',
        'membership_count': membership_count,
        'character_count': character_count,
        'message_count': message_count,
        'dice_roll_count': dice_roll_count,
    }
    
    return render(request, 'registration/admin_delete_user.html', context)


@login_required
def database_reset(request):
    """View for admin to completely reset the database (including all users)."""
    if not request.user.is_superuser:
        messages.error(request, 'Only the system administrator can reset the database.')
        return redirect('campaigns:dashboard')
    
    if request.method == 'POST':
        form = DatabaseResetForm(request.POST)
        if form.is_valid():
            # Delete all data in proper order to avoid foreign key issues
            
            # 1. Delete related data first (chat messages, dice rolls, etc.)
            ChatMessage.objects.all().delete()
            DiceRollLog.objects.all().delete()
            PersonalNotebook.objects.all().delete()
            CampaignRuleBook.objects.all().delete()
            
            # 2. Delete campaign memberships and characters
            CampaignMembership.objects.all().delete()
            Character.objects.all().delete()
            InventoryItem.objects.all().delete()
            PartyGroupMember.objects.all().delete()
            PartyGroup.objects.all().delete()
            
            # 3. Delete campaigns
            Campaign.objects.all().delete()
            
            # 4. Delete ALL users including the current admin
            User.objects.all().delete()
            
            # Log out the current user (their account no longer exists)
            logout(request)
            
            messages.success(request, 'Database has been completely reset. All accounts and data have been deleted.')
            return redirect('campaigns:first_time_setup')
    else:
        form = DatabaseResetForm()
    
    # Count current data
    user_count = User.objects.count()
    campaign_count = Campaign.objects.count()
    character_count = Character.objects.count()
    message_count = ChatMessage.objects.count()
    
    context = {
        'form': form,
        'user_count': user_count,
        'campaign_count': campaign_count,
        'character_count': character_count,
        'message_count': message_count,
    }
    
    return render(request, 'registration/database_reset.html', context)


@login_required
def admin_campaign_list(request):
    """Admin-only view to list all campaigns and manage them."""
    if not request.user.is_superuser:
        messages.error(request, 'Only the system administrator can view all campaigns.')
        return redirect('campaigns:dashboard')
    
    # Get all campaigns with their membership counts
    campaigns = Campaign.objects.all().order_by('-created_at')
    
    # Pre-calculate DM for each campaign to avoid template method calls
    campaign_data = []
    for campaign in campaigns:
        dm_membership = campaign.campaignmembership_set.filter(role='DM').first()
        member_count = campaign.campaignmembership_set.count()
        
        campaign_data.append({
            'campaign': campaign,
            'dm_user': dm_membership.user if dm_membership else None,
            'member_count': member_count,
        })
    
    context = {
        'campaign_data': campaign_data,
    }
    
    return render(request, 'registration/admin_campaign_list.html', context)


def custom_logout(request):
    """Logout view."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('campaigns:login')


def dashboard(request):
    """Main dashboard showing campaigns user has access to."""
    if not request.user.is_authenticated:
        return redirect('campaigns:login')
    
    memberships = CampaignMembership.objects.filter(user=request.user).select_related('campaign')
    
    # Get campaigns where user is a member
    campaigns = [m.campaign for m in memberships]
    
    return render(request, 'dashboard.html', {
        'memberships': memberships,
        'campaigns': campaigns,
    })


@login_required
def create_campaign(request):
    """Create a new campaign."""
    if request.method == 'POST':
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save()
            
            # Add creator as DM (campaign creator becomes the Dungeon Master)
            CampaignMembership.objects.create(
                user=request.user,
                campaign=campaign,
                role='DM'
            )
            
            # Get game system selection from POST data
            game_system_id = request.POST.get('game_system')
            if game_system_id:
                try:
                    game_system = GameSystem.objects.get(pk=game_system_id)
                    CampaignGameSettings.objects.create(
                        campaign=campaign,
                        game_system=game_system
                    )
                except GameSystem.DoesNotExist:
                    pass
            
            messages.success(request, f'Campaign "{campaign.title}" created successfully! You are the Dungeon Master.')
            
            return redirect('campaigns:dashboard')
    else:
        form = CampaignForm()
    
    # Get available game systems for the form
    game_systems = GameSystem.objects.filter(is_custom=False).order_by('name')
    
    return render(request, 'campaigns/create_campaign.html', {
        'form': form,
        'game_systems': game_systems,
    })


@login_required
def campaign_detail(request, pk):
    """View a specific campaign."""
    campaign = get_object_or_404(Campaign, pk=pk)
    
    # Get membership (admins can view any campaign without membership)
    membership = CampaignMembership.objects.filter(user=request.user, campaign=campaign).first()
    
    # Track if this is an admin viewing without being a member
    is_admin_viewing = False
    
    # Check for admin override mode (accessed from /admin/campaigns/ with ?admin_override=1)
    is_admin_override = request.GET.get('admin_override') == '1' and request.user.is_superuser
    
    # If no membership and not a superuser, deny access
    if not membership and not request.user.is_superuser:
        messages.error(request, 'You do not have access to this campaign.')
        return redirect('campaigns:dashboard')
    
    # For admins without membership, create a temporary membership object for role checking
    if not membership and request.user.is_superuser:
        is_admin_viewing = True
        class TempMembership:
            role = 'DM'  # Admins get DM-level access for moderation
            is_temporary = True  # Flag to indicate this is admin viewing mode
        membership = TempMembership()
    
    # IMPORTANT: Only set admin override if explicitly requested via URL parameter AND admin has no membership
    # If admin is a regular member of the campaign, they should see normal visibility based on their role
    # This fixes the bug where admins could see all secrets in normal campaign mode
    is_temporary = getattr(membership, 'is_temporary', False)
    
    if is_admin_override and not is_temporary:
        # Admin explicitly requested override AND doesn't have a real membership
        is_admin_viewing = True
        # Set session flag so AJAX calls know this is an admin override view
        request.session['admin_campaign_view'] = True
    elif request.user.is_superuser and membership and not is_temporary:
        # Admin is a regular member - clear any admin viewing flags
        is_admin_viewing = False
        if 'admin_campaign_view' in request.session:
            del request.session['admin_campaign_view']
    else:
        # Clear the session flag when NOT in admin override mode
        if 'admin_campaign_view' in request.session:
            del request.session['admin_campaign_view']
    
    # Get characters for this campaign (membership should never be None here due to earlier checks)
    if membership and membership.role == 'DM':
        characters = CharacterSheet.objects.filter(campaign=campaign).select_related('user')
    else:
        characters = CharacterSheet.objects.filter(campaign=campaign, user=request.user)
    
    # Get recent chat messages (will be expanded in Phase 2)
    recent_messages = ChatMessage.objects.filter(campaign=campaign).order_by('-created_at')[:10]
    
    # Check if user has a character in this campaign
    has_character = CharacterSheet.objects.filter(user=request.user, campaign=campaign).exists()
    
    # Get all campaign members with their roles and characters
    all_memberships = CampaignMembership.objects.filter(campaign=campaign).select_related('user')
    
    context = {
        'campaign': campaign,
        'membership': membership,
        'characters': characters,
        'recent_messages': recent_messages,
        'has_character': has_character,
        'is_admin_viewing': is_admin_viewing,
        'all_memberships': all_memberships,
    }
    
    return render(request, 'campaigns/detail.html', context)


@login_required
def create_character(request, campaign_pk):
    """Create a new character for a campaign."""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    membership = get_object_or_404(CampaignMembership, user=request.user, campaign=campaign)
    
    # Get game settings for this campaign
    try:
        game_settings = CampaignGameSettings.objects.get(campaign=campaign)
    except CampaignGameSettings.DoesNotExist:
        game_settings = None
    
    if request.method == 'POST':
        # Check if this is a CharacterSheet submission (has attr_ fields) or Character submission
        has_dynamic_fields = any(key.startswith('attr_') or key.startswith('skill_') for key in request.POST.keys())
        
        if game_settings and has_dynamic_fields:
            # Use CharacterSheetForm for dynamic character sheets
            form = CharacterSheetForm(request.POST, request.FILES, game_settings=game_settings)
            if form.is_valid():
                character_sheet = form.save(commit=False)
                character_sheet.user = request.user
                character_sheet.campaign = campaign
                character_sheet.game_settings = game_settings
                character_sheet.save()
                
                messages.success(request, f'Character "{character_sheet.name}" created successfully!')
                return redirect('campaigns:campaign_detail', pk=campaign_pk)
        else:
            # Use CharacterForm for simple characters
            form = CharacterForm(request.POST, request.FILES)
            if form.is_valid():
                character = form.save(commit=False)
                character.user = request.user
                character.campaign = campaign
                character.save()
                
                messages.success(request, f'Character "{character.name}" created successfully!')
                return redirect('campaigns:campaign_detail', pk=campaign_pk)
    else:
        if game_settings:
            form = CharacterSheetForm(game_settings=game_settings)
        else:
            form = CharacterForm()
    
    return render(request, 'campaigns/create_character.html', {
        'form': form,
        'campaign': campaign,
        'membership': membership,
        'game_settings': game_settings,
    })


@login_required
def edit_character(request, pk):
    """Edit a character (DM can edit any, players only their own)."""
    # Try to find CharacterSheet first, then fall back to Character
    character_sheet = CharacterSheet.objects.filter(pk=pk).first()
    character = None
    if not character_sheet:
        character = get_object_or_404(Character, pk=pk)
    
    campaign = character_sheet.campaign if character_sheet else character.campaign
    
    # Check permissions
    membership = CampaignMembership.objects.filter(user=request.user, campaign=campaign).first()
    if not membership:
        messages.error(request, 'You do not have access to this campaign.')
        return redirect('campaigns:dashboard')
    
    user_field = character_sheet.user if character_sheet else character.user
    # DMs can edit all characters, players only their own
    if membership and membership.role != 'DM' and user_field != request.user:
        messages.error(request, 'You do not have permission to edit this character.')
        detail_url = 'campaigns:character_detail'
        return redirect(detail_url, pk=pk)
    
    # Get game settings for this campaign
    try:
        game_settings = CampaignGameSettings.objects.get(campaign=campaign)
    except CampaignGameSettings.DoesNotExist:
        game_settings = None
    
    if request.method == 'POST':
        if character_sheet and game_settings:
            form = CharacterSheetForm(request.POST, request.FILES, game_settings=game_settings, instance=character_sheet)
            if form.is_valid():
                character_sheet = form.save()
                messages.success(request, f'Character "{character_sheet.name}" updated successfully!')
                return redirect('campaigns:character_detail', pk=pk)
        else:
            character = get_object_or_404(Character, pk=pk)
            form = CharacterForm(request.POST, request.FILES, instance=character)
            if form.is_valid():
                character = form.save()
                messages.success(request, f'Character "{character.name}" updated successfully!')
                return redirect('campaigns:character_detail', pk=pk)
    else:
        if character_sheet and game_settings:
            form = CharacterSheetForm(game_settings=game_settings, instance=character_sheet)
        else:
            character = get_object_or_404(Character, pk=pk)
            form = CharacterForm(instance=character)
    
    return render(request, 'campaigns/create_character.html', {
        'form': form,
        'campaign': campaign,
        'membership': membership,
        'character': character_sheet if character_sheet else character,
        'game_settings': game_settings,
    })


@login_required
def character_detail(request, pk):
    """View a character."""
    # Try to find CharacterSheet first, then fall back to Character
    character_sheet = CharacterSheet.objects.filter(pk=pk).first()
    character = None
    if not character_sheet:
        character = get_object_or_404(Character, pk=pk)
    
    campaign = character_sheet.campaign if character_sheet else character.campaign
    
    # Check permissions
    membership = CampaignMembership.objects.filter(user=request.user, campaign=campaign).first()
    if not membership:
        messages.error(request, 'You do not have access to this campaign.')
        return redirect('campaigns:dashboard')
    
    user_field = character_sheet.user if character_sheet else character.user
    # DMs can view all characters, players only their own
    if membership and membership.role != 'DM' and user_field != request.user:
        messages.error(request, 'You do not have permission to view this character.')
        return redirect('campaigns:campaign_detail', pk=campaign.pk)
    
    # Get inventory for both models
    inventory = InventoryItem.objects.filter(character_sheet=character_sheet) if character_sheet else InventoryItem.objects.filter(character=character)
    
    # Get game settings for displaying field labels
    try:
        game_settings = CampaignGameSettings.objects.get(campaign=campaign)
    except CampaignGameSettings.DoesNotExist:
        game_settings = None
    
    return render(request, 'campaigns/character_detail.html', {
        'character': character_sheet if character_sheet else character,
        'inventory': inventory,
        'membership': membership,
        'game_settings': game_settings,
    })


@login_required
def add_inventory_item(request, character_pk):
    """Add an item to a character's inventory."""
    # Try to find CharacterSheet first, then fall back to Character
    character_sheet = CharacterSheet.objects.filter(pk=character_pk).first()
    character = None
    if not character_sheet:
        character = get_object_or_404(Character, pk=character_pk)
    
    campaign = character_sheet.campaign if character_sheet else character.campaign
    
    # Check permissions (DMs can edit any, players only their own)
    membership = CampaignMembership.objects.filter(user=request.user, campaign=campaign).first()
    if not membership:
        messages.error(request, 'You do not have access to this campaign.')
        return redirect('campaigns:dashboard')
    
    user_field = character_sheet.user if character_sheet else character.user
    if membership and membership.role != 'DM' and user_field != request.user:
        messages.error(request, 'You do not have permission to edit this character.')
        return redirect('campaigns:character_detail', pk=character_pk)
    
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            if character_sheet:
                item.character_sheet = character_sheet
            else:
                item.character = character
            item.save()
            
            messages.success(request, f'Item "{item.name}" added to inventory!')
            return redirect('campaigns:character_detail', pk=character_pk)
    else:
        form = InventoryItemForm()
    
    return render(request, 'campaigns/add_inventory.html', {
        'form': form,
        'character': character_sheet if character_sheet else character,
    })


@login_required
def dm_character_roster(request, campaign_pk):
    """DM view to see all characters in a campaign."""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    membership = get_object_or_404(CampaignMembership, user=request.user, campaign=campaign)
    
    # Only DMs can access this
    if membership and membership.role != 'DM':
        messages.error(request, 'Only Dungeon Masters can view the full roster.')
        return redirect('campaigns:campaign_detail', pk=campaign_pk)
    
    characters = CharacterSheet.objects.filter(campaign=campaign).select_related('user')
    
    return render(request, 'campaigns/dm_roster.html', {
        'campaign': campaign,
        'characters': characters,
        'membership': membership,
    })


@login_required
def delete_campaign(request, pk):
    """Delete a campaign (DM or Admin only)."""
    campaign = get_object_or_404(Campaign, pk=pk)
    
    # Check if user is a global superuser (system admin) OR is the DM of this campaign
    is_global_admin = request.user.is_superuser
    
    membership = CampaignMembership.objects.filter(user=request.user, campaign=campaign).first()
    is_campaign_dm = membership and membership.role == 'DM'
    
    if not is_global_admin and not is_campaign_dm:
        messages.error(request, 'Only the system administrator or Dungeon Master can delete campaigns.')
        return redirect('campaigns:dashboard')
    
    # Determine where to redirect after deletion (from query param or default)
    next_url = request.GET.get('next', 'campaigns:dashboard')
    
    if request.method == 'POST':
        campaign_title = campaign.title
        
        # Delete related objects first to avoid ProtectedError
        CharacterSheet.objects.filter(campaign=campaign).delete()
        ChatMessage.objects.filter(campaign=campaign).delete()
        DiceRollLog.objects.filter(campaign=campaign).delete()
        PersonalNotebook.objects.filter(campaign=campaign).delete()
        PartyGroup.objects.filter(campaign=campaign).delete()
        CampaignMembership.objects.filter(campaign=campaign).delete()
        
        campaign.delete()
        messages.success(request, f'Campaign "{campaign_title}" has been deleted.')
        
        # Handle redirect based on where user came from
        if next_url == 'campaigns:admin_campaign_list':
            return redirect('campaigns:admin_campaign_list')
        else:
            return redirect('campaigns:dashboard')
    
    return render(request, 'campaigns/confirm_delete.html', {
        'object': campaign,
        'object_type': 'campaign',
        'next_url': next_url,
    })


@login_required
def delete_character(request, pk):
    """Delete a character (Admin or character owner)."""
    # Try to find CharacterSheet first, then fall back to Character
    character_sheet = CharacterSheet.objects.filter(pk=pk).first()
    character = None
    if not character_sheet:
        character = get_object_or_404(Character, pk=pk)
    
    campaign = character_sheet.campaign if character_sheet else character.campaign
    membership = get_object_or_404(CampaignMembership, user=request.user, campaign=campaign)
    
    user_field = character_sheet.user if character_sheet else character.user
    # Only DM or the character owner can delete
    if membership and membership.role != 'DM' and user_field != request.user:
        messages.error(request, 'You do not have permission to delete this character.')
        return redirect('campaigns:character_detail', pk=pk)
    
    if request.method == 'POST':
        character_name = character_sheet.name if character_sheet else character.name
        campaign_pk = campaign.pk
        if character_sheet:
            character_sheet.delete()
        else:
            character.delete()
        messages.success(request, f'Character "{character_name}" has been deleted.')
        return redirect('campaigns:campaign_detail', pk=campaign_pk)
    
    object_to_delete = character_sheet if character_sheet else character
    return render(request, 'campaigns/confirm_delete.html', {
        'object': object_to_delete,
        'object_type': 'character',
    })


@login_required
def get_chat_messages(request, campaign_pk):
    """Fetch chat messages for a campaign with visibility filtering."""
    try:
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        
        # Check if user is a member of this campaign
        membership = CampaignMembership.objects.filter(user=request.user, campaign=campaign).first()
        
        # Track if this is an admin viewing without being a member
        is_admin_viewing = False
        
                # Check for admin override mode (accessed from /admin/campaigns/ with ?admin_override=1)
        # Note: We need to check the query params from the referring page, but since this is AJAX
        # we'll rely on session or a different approach. For now, we'll pass it via a header or
        # store it in session when the page loads.
        # Actually, let's check if the user explicitly set admin_override in their session
        is_admin_override = request.session.get('admin_campaign_view', False) and request.user.is_superuser
        
        # If no membership and not a superuser, deny access
        if not membership and not request.user.is_superuser:
            return JsonResponse({'error': 'You do not have access to this campaign.'}, status=403)
        
        # For admins without membership, create a temporary membership object for role checking
        if not membership and request.user.is_superuser:
            is_admin_viewing = True
            class TempMembership:
                role = 'DM'  # Admins get DM-level access for moderation
                is_temporary = True  # Flag to indicate this is admin viewing mode
            membership = TempMembership()
        
        # IMPORTANT: Only admins WITHOUT membership can see all secrets (admin override mode)
        # Admins who ARE members of the campaign should only see what their role allows
        # This fixes the security bug where admins could see DM whispers and hidden dice rolls in normal mode
        is_temporary = getattr(membership, 'is_temporary', False)
        
        if is_admin_override and not is_temporary:
            # Admin explicitly requested override AND doesn't have a real membership
            is_admin_viewing = True
        elif request.user.is_superuser and membership and not is_temporary:
            # Admin is a regular member - treat them as their assigned role, NOT as admin viewing
            is_admin_viewing = False

        # Get user's current party group if in split mode
        user_group = None
        if membership and membership.role == 'PLAYER':
            try:
                group_member = PartyGroupMember.objects.filter(user=request.user).first()
                if group_member and group_member.group.campaign == campaign:
                    user_group = group_member.group
            except:
                pass

        # Base query for visible messages with prefetch to avoid N+1 queries
        visible_messages = ChatMessage.objects.filter(campaign=campaign).prefetch_related('recipients')

        # Filter based on visibility type and user role
        # Note: Superusers with campaign membership are treated as their assigned role (DM/Player/Spectator)
        # Only superusers WITHOUT membership get admin override access
        
        user_role = membership.role if membership else None
        
        if user_role == 'DM' and not is_admin_viewing:
            # DMs see almost everything, but NOT secret whispers not meant for them
            # They can see: PUBLIC, their own messages, DM_ONLY (as sender or receiver), SECRET_WHISPER where they're recipient
            base_query = Q(visibility_type='PUBLIC') | Q(sender=request.user)
            
            # DMs can see all DM_ONLY messages (they are the recipient)
            base_query |= Q(visibility_type='DM_ONLY')
            
            # DMs can only see SECRET_WHISPER where they are a recipient
            base_query |= Q(visibility_type='SECRET_WHISPER', recipients=request.user)
            
            # Add SPLIT_GROUP condition if applicable
            if user_group:
                base_query |= Q(visibility_type='SPLIT_GROUP', party_group=user_group)
            
            visible_messages = visible_messages.filter(base_query).order_by('created_at')
        elif request.user.is_superuser and is_admin_viewing:
            # Superuser viewing without membership (admin override mode) - can see everything
            visible_messages = visible_messages.order_by('created_at')
        else:
            # Players, Spectators, and DMs in admin override mode have restrictions
            # They can see:
            # 1. PUBLIC messages (everyone)
            # 2. Their own messages regardless of visibility type  
            # 3. DM_ONLY messages sent TO them or FROM them (to DM)
            # 4. SECRET_WHISPER messages where they are a recipient
            # 5. SPLIT_GROUP messages for their group
            
            base_query = Q(visibility_type='PUBLIC') | Q(sender=request.user)
            
            # Add DM_ONLY conditions (sender can see their own DM whispers, or if they're the DM receiving them)
            # Note: Old single-recipient field removed, so we only check sender
            base_query |= Q(visibility_type='DM_ONLY', sender=request.user)
            
            # Add SECRET_WHISPER condition
            base_query |= Q(visibility_type='SECRET_WHISPER', recipients=request.user)
            
            # Add SPLIT_GROUP condition if applicable
            if user_group:
                base_query |= Q(visibility_type='SPLIT_GROUP', party_group=user_group)
            
            visible_messages = visible_messages.filter(base_query).order_by('created_at')

        # Get dice rolls (public only for non-DMs)
        if membership and membership.role == 'DM':
            dice_rolls = DiceRollLog.objects.filter(campaign=campaign).order_by('created_at')
        else:
            dice_rolls = DiceRollLog.objects.filter(campaign=campaign, visibility='PUBLIC').order_by('created_at')

        # Serialize messages
        message_list = []
        for msg in visible_messages[:50]:  # Limit to last 50 messages
            # Use stored name for archival (preserves original username even if deleted)
            sender_name = msg.get_sender_display_name()
            sender_id = msg.sender.id if msg.sender else None
            
            # Get sender's avatar
            sender_avatar = None
            if msg.sender and msg.sender.avatar:
                sender_avatar = msg.sender.avatar.url
            
            # Determine display name based on message type (for all IC messages from players)
            display_sender_name = sender_name
            character_avatar = None
            if msg.message_type == 'IC' and msg.sender:
                # Show character name for IC messages from any player
                try:
                    char = CharacterSheet.objects.get(user=msg.sender, campaign=campaign)
                    display_sender_name = char.name
                    if char.avatar:
                        character_avatar = char.avatar.url
                except CharacterSheet.DoesNotExist:
                    pass
            
            # Check if this is a whisper to the current user (DM_ONLY or SECRET_WHISPER)
            # IMPORTANT: "whisper-to-me" styling should only apply when someone ELSE sent a whisper TO you
            # If YOU sent the whisper, it should show with normal styling (not cyan highlight)
            is_dm_whisper_to_me = False
            if msg.visibility_type == 'DM_ONLY':
                # DM_ONLY messages are visible to sender and the campaign DM
                # For backwards compatibility, we can't check recipient field anymore
                # Only mark as "whisper-to-me" if someone else sent it TO you (as the DM)
                is_dm_whisper_to_me = (msg.sender != request.user)  # Not the sender means you're receiving it
            elif msg.visibility_type == 'SECRET_WHISPER':
                # SECRET_WHISPER: Only mark as "whisper-to-me" if someone else sent it TO you
                # If you sent it, don't highlight it (you already know what you sent)
                is_dm_whisper_to_me = (msg.sender != request.user) and msg.recipients.filter(id=request.user.id).exists()
            
            # Get the sender's role for badge display
            sender_membership = CampaignMembership.objects.filter(user=msg.sender, campaign=campaign).first() if msg.sender else None
            sender_role = sender_membership.role if sender_membership else None
            
            # Get recipient list for whispers (for display to sender and recipients)
            recipient_names = []
            if msg.visibility_type == 'SECRET_WHISPER':
                for recipient in msg.recipients.all():
                    recipient_names.append(recipient.real_name or recipient.username)
            
            message_list.append({
                'id': msg.id,
                'content': msg.content,
                'sender_id': sender_id,
                'sender_name': display_sender_name,
                'real_sender_name': sender_name,
                'character_name': display_sender_name if msg.message_type == 'IC' and display_sender_name != sender_name else None,
                'visibility_type': msg.visibility_type,
                'message_type': msg.message_type,
                'is_edited': msg.is_edited,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'formatted_time': msg.created_at.strftime('%b %d, %H:%M'),
                'sender_role': sender_role,
                'is_dm_whisper_to_me': is_dm_whisper_to_me,
                'sender_avatar': sender_avatar,
                'character_avatar': character_avatar,
                'recipient_names': recipient_names,
            })

        dice_list = []
        for roll in dice_rolls[:20]:  # Limit to last 20 rolls
            # Use stored name for archival (preserves original username even if deleted)
            roll_sender_name = roll.get_sender_display_name()
            
            dice_list.append({
                'id': roll.id,
                'formula': roll.formula,
                'result': roll.result,
                'visibility': roll.visibility,
                'sender_name': roll_sender_name,
                'created_at': roll.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })

        return JsonResponse({
            'messages': message_list,
            'dice_rolls': dice_list,
            'user_role': membership.role if membership else None,
            'has_character': CharacterSheet.objects.filter(user=request.user, campaign=campaign).exists(),
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Server error loading messages: {str(e)}'}, status=500)


@login_required
@require_POST
def post_chat_message(request, campaign_pk):
    """Post a new chat message."""
    try:
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        membership = CampaignMembership.objects.filter(user=request.user, campaign=campaign).first()
        if not membership:
            return JsonResponse({'error': 'You are not a member of this campaign'}, status=403)
        
        # Parse JSON body with error handling
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': f'Invalid JSON format: {str(e)}'}, status=400)
        
        content = data.get('content', '').strip()
        visibility_type = data.get('visibility_type', 'PUBLIC')
        message_type = data.get('message_type', 'OOC_RELEVANT')
        recipient_user_ids = data.get('recipient_user_ids', [])  # Now accepts multiple recipients
        
        if not content:
            return JsonResponse({'error': 'Message content is required'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    
    # Handle whispers (DM_ONLY or SECRET_WHISPER) with multiple recipients
    dm_recipient = None
    secret_recipients = []
    
    if visibility_type == 'DM_ONLY':
        # DM_ONLY: Only sender and DM can see (old behavior for players sending to DM)
        # No specific recipient needed, just mark as DM_ONLY
        pass
    
    elif visibility_type == 'SECRET_WHISPER':
        # SECRET_WHISPER: Selected recipients only (excludes DM unless they're selected)
        if not recipient_user_ids or len(recipient_user_ids) == 0:
            return JsonResponse({'error': 'At least one recipient is required for whispers'}, status=400)
        
        # Validate all recipients are campaign members
        for user_id in recipient_user_ids:
            try:
                user_id_int = int(user_id)
                recipient = User.objects.get(pk=user_id_int)
                recipient_membership = CampaignMembership.objects.filter(user=recipient, campaign=campaign).first()
                
                if not recipient_membership:
                    return JsonResponse({'error': f'Recipient {user_id} is not a member of this campaign'}, status=400)
                
                secret_recipients.append(recipient)
            except (ValueError, User.DoesNotExist):
                return JsonResponse({'error': f'Invalid recipient ID: {user_id}'}, status=400)
    
    # Handle old single-recipient format for backwards compatibility
    if not secret_recipients and 'recipient_user_id' in data and data['recipient_user_id']:
        try:
            recipient = User.objects.get(pk=data['recipient_user_id'])
            recipient_membership = CampaignMembership.objects.filter(user=recipient, campaign=campaign).first()
            
            if not recipient_membership:
                return JsonResponse({'error': 'Recipient is not a member of this campaign'}, status=400)
            
                        # For backwards compatibility, treat single-recipient DM whispers as DM_ONLY
            if visibility_type in ['PLAYER_WHISPER', 'SPECTATOR_WHISPER']:
                visibility_type = 'DM_ONLY'
                dm_recipient = recipient
        except (ValueError, User.DoesNotExist):
            pass
    
    # Validate visibility based on role
    # Note: membership should never be None here due to get_object_or_404 above
    if membership and membership.role == 'SPECTATOR':
        # Spectators can post PUBLIC OOC messages, DM_ONLY whispers, and SECRET_WHISPER
        if visibility_type not in ['PUBLIC', 'DM_ONLY', 'SECRET_WHISPER']:
            return JsonResponse({'error': 'Spectators can only send public messages or private whispers'}, status=400)
        if message_type == 'IC':
            return JsonResponse({'error': 'Spectators cannot send In-Character messages'}, status=400)
    elif membership and membership.role != 'DM' and membership.role != 'PLAYER':
        return JsonResponse({'error': 'Invalid role'}, status=400)
    
    # Players can send PUBLIC, DM_ONLY (to DM), or SECRET_WHISPER
    # DMs can send everything
    if visibility_type not in ['PUBLIC', 'DM_ONLY', 'SECRET_WHISPER', 'SPLIT_GROUP']:
        return JsonResponse({'error': 'Invalid visibility type'}, status=400)
    
        # Check if user has a character for IC messages
    if message_type == 'IC' and membership and membership.role == 'PLAYER':
        if not CharacterSheet.objects.filter(user=request.user, campaign=campaign).exists():
            return JsonResponse({'error': 'You need a character to send In-Character messages'}, status=400)
    
    # Handle split group visibility
    party_group = None
    if visibility_type == 'SPLIT_GROUP':
        if membership and membership.role != 'DM':
            return JsonResponse({'error': 'Only DMs can send split-group messages'}, status=400)
        group_id = data.get('party_group_id')
        if group_id:
            party_group = get_object_or_404(PartyGroup, pk=group_id, campaign=campaign)
    
    try:
        # Create message (note: recipient field was removed, using recipients ManyToMany instead)
        message = ChatMessage.objects.create(
            content=content,
            sender=request.user,
            campaign=campaign,
            visibility_type=visibility_type,
            party_group=party_group,
            message_type=message_type,
        )
        
        # Add recipients for SECRET_WHISPER (must be done after message is saved)
        if secret_recipients:
            message.recipients.set(secret_recipients)
        
        return JsonResponse({
            'success': True,
            'message_id': message.id,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Failed to create message: {str(e)}'}, status=500)


@login_required
@require_POST
def post_dice_roll(request, campaign_pk):
    """Post a dice roll result and create a chat message."""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    membership = CampaignMembership.objects.filter(user=request.user, campaign=campaign).first()
    if not membership:
        return JsonResponse({'error': 'You are not a member of this campaign'}, status=403)
    
    data = json.loads(request.body)
    formula = data.get('formula', '').strip()
    result = data.get('result')
    modifier = data.get('modifier', 0)
    visibility = data.get('visibility', 'PUBLIC')
    
    if not formula or result is None:
        return JsonResponse({'error': 'Formula and result are required'}, status=400)
    
        # Validate visibility
    if membership and membership.role != 'DM' and visibility == 'DM_ONLY':
        # Players can hide rolls from other players (DM sees all)
        pass  # Allow it
    
    roll = DiceRollLog.objects.create(
        sender=request.user,
        campaign=campaign,
        formula=formula,
        result=result,
        modifier=modifier,
        visibility=visibility,
    )
    
    # Always create a chat message for the dice roll (so it appears in the chat stream)
    # Create a simple single-line format with bold name and "Result:" label, bold/italic result value
    content = f"<strong>{escape(request.user.real_name or request.user.username)} rolled</strong> {formula}: <strong><em>Result:</em></strong> <strong><em>{result}</em></strong>"
    
    # Map visibility from DiceRollLog to ChatMessage
    visibility_type = 'DM_ONLY' if visibility == 'DM_ONLY' else 'PUBLIC'
    
    ChatMessage.objects.create(
        content=content,
        sender=request.user,
        campaign=campaign,
        visibility_type=visibility_type,
        message_type='DICE_ROLL',
    )
    
    return JsonResponse({
        'success': True,
        'roll_id': roll.id,
        'result': result,
    })


@login_required
@require_POST
def edit_chat_message(request, message_pk):
    """Edit a chat message (DMs/Admins can edit any, users can edit their own)."""
    message = get_object_or_404(ChatMessage, pk=message_pk)
    campaign = message.campaign
    membership = CampaignMembership.objects.filter(user=request.user, campaign=campaign).first()
    
    # Handle admin viewing mode (admin without membership but with access)
    if not membership and request.user.is_superuser:
        class TempMembership:
            role = 'DM'
        membership = TempMembership()
    
            # Check permissions
    if membership and membership.role != 'DM' and message.sender != request.user:
        return JsonResponse({'error': 'You do not have permission to edit this message'}, status=403)
    
    data = json.loads(request.body)
    content = data.get('content', '').strip()
    
    if not content:
        return JsonResponse({'error': 'Message content is required'}, status=400)
    
    message.content = content
    message.is_edited = True
    message.save()
    
    return JsonResponse({
        'success': True,
        'message_id': message.id,
    })


@login_required
@require_POST
def delete_chat_message(request, message_pk):
    """Delete a chat message (DMs/Admins can delete any, users can delete their own)."""
    message = get_object_or_404(ChatMessage, pk=message_pk)
    campaign = message.campaign
    membership = CampaignMembership.objects.filter(user=request.user, campaign=campaign).first()
    
    # Handle admin viewing mode (admin without membership but with access)
    if not membership and request.user.is_superuser:
        class TempMembership:
            role = 'DM'
        membership = TempMembership()
    
            # Check permissions
    if membership and membership.role != 'DM' and message.sender != request.user:
        return JsonResponse({'error': 'You do not have permission to delete this message'}, status=403)
    
    message.delete()
    
    return JsonResponse({'success': True})


@login_required
def manage_campaign_members(request, campaign_pk):
    """DM view to manage campaign members and assign roles."""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    membership = get_object_or_404(CampaignMembership, user=request.user, campaign=campaign)
    
        # Only DMs can manage members
    if membership and membership.role != 'DM':
        messages.error(request, 'Only Dungeon Masters can manage campaign members.')
        return redirect('campaigns:campaign_detail', pk=campaign_pk)
    
    # Get all current members
    current_members = CampaignMembership.objects.filter(campaign=campaign).select_related('user')
    
    # Get users not yet in this campaign
    existing_user_ids = current_members.values_list('user_id', flat=True)
    available_users = User.objects.exclude(id__in=existing_user_ids).order_by('username')
    
    context = {
        'campaign': campaign,
        'membership': membership,
        'current_members': current_members,
        'available_users': available_users,
    }
    
    return render(request, 'campaigns/manage_members.html', context)


@login_required
@require_POST
def add_campaign_member(request, campaign_pk):
    """Add a new member to the campaign."""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    membership = get_object_or_404(CampaignMembership, user=request.user, campaign=campaign)
    
        # Only DMs can add members
    if membership and membership.role != 'DM':
        return JsonResponse({'error': 'Only Dungeon Masters can add members'}, status=403)
    
    user_id = request.POST.get('user_id')
    role = request.POST.get('role', 'PLAYER')
    
    if not user_id:
        return JsonResponse({'error': 'User ID is required'}, status=400)
    
    user = get_object_or_404(User, pk=user_id)
    
    # Check if already a member
    if CampaignMembership.objects.filter(user=user, campaign=campaign).exists():
        return JsonResponse({'error': 'User is already a member'}, status=400)
    
    # Create membership
    CampaignMembership.objects.create(
        user=user,
        campaign=campaign,
        role=role
    )
    
    # Note: messages.success is not used here as this is an AJAX endpoint
    # Success feedback is handled via the JSON response
    return JsonResponse({'success': True})


@login_required
@require_POST
def update_member_role(request, membership_pk):
    """Update a member's role in the campaign."""
    membership_obj = get_object_or_404(CampaignMembership, pk=membership_pk)
    campaign = membership_obj.campaign
    
    # Check if current user is DM of this campaign
    user_membership = CampaignMembership.objects.filter(user=request.user, campaign=campaign).first()
    if not user_membership:
        return JsonResponse({'error': 'You are not a member of this campaign'}, status=403)
    
    # Only DMs can change roles
    if user_membership.role != 'DM':
        return JsonResponse({'error': 'Only Dungeon Masters can change roles'}, status=403)
    
    # Prevent users from changing their own role
    if membership_obj.user == request.user:
        return JsonResponse({'error': 'You cannot change your own role'}, status=400)
    
    new_role = request.POST.get('role')
    
    # Validate the role exists in CampaignMembership.ROLE_CHOICES
    valid_roles = [choice[0] for choice in CampaignMembership.ROLE_CHOICES]
    
    if not new_role or new_role not in valid_roles:
        return JsonResponse({'error': f'Invalid role. Valid roles are: {", ".join(valid_roles)}'}, status=400)
    
    # Update the role
    membership_obj.role = new_role
    membership_obj.save(update_fields=['role'])  # Only update the role field
    
    return JsonResponse({'success': True})


@login_required
@require_POST
def remove_campaign_member(request, membership_pk):
    """Remove a member from the campaign."""
    try:
        membership_obj = get_object_or_404(CampaignMembership, pk=membership_pk)
        campaign = membership_obj.campaign
        
        # Check if current user is DM of this campaign
        user_membership = CampaignMembership.objects.filter(user=request.user, campaign=campaign).first()
        if not user_membership or user_membership.role != 'DM':
            return JsonResponse({'error': 'Only Dungeon Masters can remove members'}, status=403)
        
        # Prevent users from removing themselves
        if membership_obj.user == request.user:
            return JsonResponse({'error': 'You cannot remove yourself.'}, status=400)
        
        # DMs can only remove Players and Spectators (not other DMs)
        if user_membership.role == 'DM' and membership_obj.role == 'DM':
            return JsonResponse({'error': 'You cannot remove another Dungeon Master. Transfer the campaign or delete it instead.'}, status=403)
        
        # Ensure at least one member remains
        member_count = CampaignMembership.objects.filter(campaign=campaign).count()
        if member_count == 1:
            return JsonResponse({'error': 'Cannot remove the last member of the campaign.'}, status=400)
        
        username = membership_obj.user.real_name or membership_obj.user.username
        membership_obj.delete()
        
        # Note: messages.success is not used here as this is an AJAX endpoint
        # Success feedback is handled via the JSON response
        return JsonResponse({'success': True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Failed to remove member: {str(e)}'}, status=500)


@login_required
@require_POST
def leave_campaign(request, campaign_pk):
    """Allow a user to leave a campaign."""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    membership = get_object_or_404(CampaignMembership, user=request.user, campaign=campaign)
    
        # DMs cannot leave their own campaigns (they must delete or transfer first)
    if membership and membership.role == 'DM':
        return JsonResponse({'error': 'As Dungeon Master, you cannot leave this campaign. You can delete it or transfer DM role to another player.'}, status=403)
    
    # Ensure at least one member remains
    member_count = CampaignMembership.objects.filter(campaign=campaign).count()
    if member_count == 1:
        return JsonResponse({'error': 'Cannot leave: campaign would have no members. Delete the campaign instead.'}, status=400)
    
    username = request.user.real_name or request.user.username
    membership.delete()
    
    # Note: messages.success is not used here as this is an AJAX endpoint
    # Success feedback is handled via the JSON response
    return JsonResponse({'success': True})


@login_required
def admin_view_secret_whispers(request, campaign_pk):
    """Admin-only view to see all secret whispers in a campaign (override privacy)."""
    if not request.user.is_superuser:
        messages.error(request, 'Only system administrators can access this feature.')
        return redirect('campaigns:dashboard')
    
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    
    # Get all secret whispers in the campaign
    secret_messages = ChatMessage.objects.filter(
        campaign=campaign,
        visibility_type='SECRET_WHISPER'
    ).select_related('sender', 'campaign').prefetch_related('recipients').order_by('-created_at')
    
    # Also get DM_ONLY messages for completeness
    dm_only_messages = ChatMessage.objects.filter(
        campaign=campaign,
        visibility_type='DM_ONLY'
    ).select_related('sender', 'campaign').prefetch_related('recipients').order_by('-created_at')
    
    context = {
        'campaign': campaign,
        'secret_messages': secret_messages,
        'dm_only_messages': dm_only_messages,
    }
    
    return render(request, 'campaigns/admin_view_secrets.html', context)


@login_required
def my_personal_notebook(request, campaign_pk):
    """View and edit personal notebook for a specific campaign. Only visible to the owner."""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    
    # Check if user is a member of this campaign
    membership = CampaignMembership.objects.filter(user=request.user, campaign=campaign).first()
    if not membership:
        messages.error(request, 'You do not have access to this campaign.')
        return redirect('campaigns:dashboard')
    
    # Get or create the user's personal notebook for this campaign
    notebook, created = PersonalNotebook.objects.get_or_create(
        user=request.user,
        campaign=campaign,
        defaults={'title': 'My Notes', 'content': ''}
    )
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '')
        
        if not title:
            messages.error(request, 'Notebook title is required.')
        else:
            notebook.title = title
            notebook.content = content
            notebook.save()
            messages.success(request, 'Your notes have been saved!')
    
    context = {
        'campaign': campaign,
        'membership': membership,
        'notebook': notebook,
    }
    
    return render(request, 'campaigns/personal_notebook.html', context)


@login_required
def delete_personal_notebook(request, pk):
    """Delete a personal notebook (only the owner can delete)."""
    notebook = get_object_or_404(PersonalNotebook, pk=pk)
    
    # Only the owner can delete their own notebook
    if notebook.user != request.user:
        messages.error(request, 'You do not have permission to delete this notebook.')
        return redirect('campaigns:dashboard')
    
    campaign_pk = notebook.campaign.pk
    
    if request.method == 'POST':
        notebook.delete()
        messages.success(request, 'Your personal notebook has been deleted.')
        return redirect('campaigns:campaign_detail', pk=campaign_pk)
    
    return render(request, 'campaigns/confirm_delete.html', {
        'object': notebook,
        'object_type': 'personal notebook',
    })


@login_required
def view_campaign_rule_book(request, campaign_pk):
    """View the campaign rule book. Accessible to all members."""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    
    # Check if user is a member of this campaign
    membership = CampaignMembership.objects.filter(user=request.user, campaign=campaign).first()
    if not membership and not request.user.is_superuser:
        messages.error(request, 'You do not have access to this campaign.')
        return redirect('campaigns:dashboard')
    
    # Get or create the rule book for this campaign
    rule_book, created = CampaignRuleBook.objects.get_or_create(campaign=campaign)
    
    context = {
        'campaign': campaign,
        'membership': membership,
        'rule_book': rule_book,
        'can_edit': membership.role == 'DM' if membership else False,
    }
    
    return render(request, 'campaigns/campaign_rule_book.html', context)


@login_required
def edit_campaign_rule_book(request, campaign_pk):
    """Edit the campaign rule book. Only DM can edit."""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    membership = get_object_or_404(CampaignMembership, user=request.user, campaign=campaign)
    
        # Only DMs can edit the rule book
    if membership and membership.role != 'DM':
        messages.error(request, 'Only the Dungeon Master can edit the campaign rule book.')
        return redirect('campaigns:view_rule_book', campaign_pk=campaign_pk)
    
    # Get or create the rule book for this campaign
    rule_book, created = CampaignRuleBook.objects.get_or_create(campaign=campaign)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '')
        
        if not title:
            messages.error(request, 'Rule book title is required.')
        else:
            rule_book.title = title
            rule_book.content = content
            rule_book.save()
            messages.success(request, 'Campaign rule book has been updated!')
            return redirect('campaigns:view_rule_book', campaign_pk=campaign_pk)
    
    context = {
        'campaign': campaign,
        'membership': membership,
        'rule_book': rule_book,
        'is_editing': True,
    }
    
    return render(request, 'campaigns/campaign_rule_book.html', context)