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

from .models import User, Campaign, CampaignMembership, Character, InventoryItem, ChatMessage, DiceRollLog, PartyGroup, PartyGroupMember
from .forms import AdminUserCreationForm, CustomAuthenticationForm, CampaignForm, CharacterForm, InventoryItemForm, PasswordChangeForm, UserRegistrationForm, UserPasswordChangeForm


def register(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, 
                f'Account created successfully for {user.username}! Please log in.'
            )
            return redirect('campaigns:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def custom_login(request):
    """Custom login view with password change enforcement."""
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
            
            messages.success(request, f'Campaign "{campaign.title}" created successfully! You are the Dungeon Master.')
            
            return redirect('campaigns:dashboard')
    else:
        form = CampaignForm()
    
    return render(request, 'campaigns/create_campaign.html', {'form': form})


@login_required
def campaign_detail(request, pk):
    """View a specific campaign."""
    campaign = get_object_or_404(Campaign, pk=pk)
    
    # Get membership (admins can view any campaign without membership)
    membership = CampaignMembership.objects.filter(user=request.user, campaign=campaign).first()
    
    # Track if this is an admin viewing without being a member
    is_admin_viewing = False
    
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
    
    # Get characters for this campaign (membership should never be None here due to earlier checks)
    if membership and membership.role == 'DM':
        characters = Character.objects.filter(campaign=campaign).select_related('user')
    else:
        characters = Character.objects.filter(campaign=campaign, user=request.user)
    
    # Get recent chat messages (will be expanded in Phase 2)
    recent_messages = ChatMessage.objects.filter(campaign=campaign).order_by('-created_at')[:10]
    
    # Check if user has a character in this campaign
    has_character = Character.objects.filter(user=request.user, campaign=campaign).exists()
    
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
    
    if request.method == 'POST':
        form = CharacterForm(request.POST, request.FILES)
        if form.is_valid():
            character = form.save(commit=False)
            character.user = request.user
            character.campaign = campaign
            
            # Set default max HP if not set
            if character.max_health_points == 0:
                character.max_health_points = character.health_points
            
            character.save()
            
            messages.success(request, f'Character "{character.name}" created successfully!')
            return redirect('campaigns:campaign_detail', pk=campaign_pk)
    else:
        form = CharacterForm(initial={
            'level': 1,
            'strength': 10,
            'dexterity': 10,
            'constitution': 10,
            'intelligence': 10,
            'wisdom': 10,
            'charisma': 10,
            'health_points': 10,
            'max_health_points': 10,
            'armor_class': 10,
        })
    
    return render(request, 'campaigns/create_character.html', {
        'form': form,
        'campaign': campaign,
        'membership': membership,
    })


@login_required
def edit_character(request, pk):
    """Edit a character sheet (DM can edit any, players only their own)."""
    character = get_object_or_404(Character, pk=pk)
    
    # Check permissions
    membership = CampaignMembership.objects.filter(user=request.user, campaign=character.campaign).first()
    if not membership:
        messages.error(request, 'You do not have access to this campaign.')
        return redirect('campaigns:dashboard')
    
    # DMs can edit all characters, players only their own
    if membership.role != 'DM' and character.user != request.user:
        messages.error(request, 'You do not have permission to edit this character.')
        return redirect('campaigns:character_detail', pk=pk)
    
    if request.method == 'POST':
        form = CharacterForm(request.POST, request.FILES, instance=character)
        if form.is_valid():
            character = form.save()
            
            messages.success(request, f'Character "{character.name}" updated successfully!')
            return redirect('campaigns:character_detail', pk=pk)
    else:
        form = CharacterForm(instance=character)
    
    return render(request, 'campaigns/create_character.html', {  # Reuse create template for edit
        'form': form,
        'campaign': character.campaign,
        'membership': membership,
        'character': character,  # Pass character to indicate we're editing
    })


@login_required
def character_detail(request, pk):
    """View a character sheet."""
    character = get_object_or_404(Character, pk=pk)
    
    # Check permissions
    membership = CampaignMembership.objects.filter(user=request.user, campaign=character.campaign).first()
    if not membership:
        messages.error(request, 'You do not have access to this campaign.')
        return redirect('campaigns:dashboard')
    
    # DMs can view all characters, players only their own
    if membership.role != 'DM' and character.user != request.user:
        messages.error(request, 'You do not have permission to view this character.')
        return redirect('campaigns:campaign_detail', pk=character.campaign.pk)
    
    inventory = InventoryItem.objects.filter(character=character)
    
    return render(request, 'campaigns/character_detail.html', {
        'character': character,
        'inventory': inventory,
        'membership': membership,
    })


@login_required
def add_inventory_item(request, character_pk):
    """Add an item to a character's inventory."""
    character = get_object_or_404(Character, pk=character_pk)
    
    # Check permissions (DMs can edit any, players only their own)
    membership = CampaignMembership.objects.filter(user=request.user, campaign=character.campaign).first()
    if not membership:
        messages.error(request, 'You do not have access to this campaign.')
        return redirect('campaigns:dashboard')
    
    if membership.role != 'DM' and character.user != request.user:
        messages.error(request, 'You do not have permission to edit this character.')
        return redirect('campaigns:character_detail', pk=character_pk)
    
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.character = character
            item.save()
            
            messages.success(request, f'Item "{item.name}" added to inventory!')
            return redirect('campaigns:character_detail', pk=character_pk)
    else:
        form = InventoryItemForm()
    
    return render(request, 'campaigns/add_inventory.html', {
        'form': form,
        'character': character,
    })


@login_required
def dm_character_roster(request, campaign_pk):
    """DM view to see all characters in a campaign."""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    membership = get_object_or_404(CampaignMembership, user=request.user, campaign=campaign)
    
    # Only DMs can access this
    if membership.role != 'DM':
        messages.error(request, 'Only Dungeon Masters can view the full roster.')
        return redirect('campaigns:campaign_detail', pk=campaign_pk)
    
    characters = Character.objects.filter(campaign=campaign).select_related('user')
    
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
    character = get_object_or_404(Character, pk=pk)
    membership = get_object_or_404(CampaignMembership, user=request.user, campaign=character.campaign)
    
    # Only DM or the character owner can delete
    if membership.role != 'DM' and character.user != request.user:
        messages.error(request, 'You do not have permission to delete this character.')
        return redirect('campaigns:character_detail', pk=pk)
    
    if request.method == 'POST':
        character_name = character.name
        campaign_pk = character.campaign.pk
        character.delete()
        messages.success(request, f'Character "{character_name}" has been deleted.')
        return redirect('campaigns:campaign_detail', pk=campaign_pk)
    
    return render(request, 'campaigns/confirm_delete.html', {
        'object': character,
        'object_type': 'character',
    })


@login_required
def get_chat_messages(request, campaign_pk):
    """Fetch chat messages for a campaign with visibility filtering."""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    membership = get_object_or_404(CampaignMembership, user=request.user, campaign=campaign)
    
    # Get user's current party group if in split mode
    user_group = None
    if membership.role == 'PLAYER':
        try:
            group_member = PartyGroupMember.objects.filter(user=request.user).first()
            if group_member and group_member.group.campaign == campaign:
                user_group = group_member.group
        except:
            pass
    
    # Base query for visible messages
    visible_messages = ChatMessage.objects.filter(campaign=campaign)
    
    # Filter based on visibility type and user role
    if membership.role == 'DM':
        # DMs see everything
        visible_messages = visible_messages.order_by('created_at')
    else:
        # Players and Spectators have restrictions
        # They can see:
        # 1. PUBLIC messages
        # 2. Their own DM_ONLY messages (whispers to DM)
        # 3. DM whispers TO them (DM_ONLY messages where they are the recipient)
        # 4. SPLIT_GROUP messages for their group
        # 5. Their own messages regardless of visibility
        visible_messages = visible_messages.filter(
            Q(visibility_type='PUBLIC') |
            Q(visibility_type='DM_ONLY', sender=request.user) |  # Can see their own DM whispers
            Q(visibility_type='DM_ONLY', recipient=request.user) |  # Can see DM whispers to them
            Q(visibility_type='SPLIT_GROUP', party_group=user_group) |  # Can see their group's messages
            Q(sender=request.user)  # Always see their own messages
        )
        
        # If split mode is active and user is in a group, only show public + their group
        if user_group:
            visible_messages = visible_messages.filter(
                Q(visibility_type='PUBLIC') |
                Q(visibility_type='DM_ONLY', sender=request.user) |  # Their own whispers to DM
                Q(visibility_type='DM_ONLY', recipient=request.user) |  # DM whispers to them
                Q(visibility_type='SPLIT_GROUP', party_group=user_group) |
                Q(sender=request.user)
            )
    
    # Get dice rolls (public only for non-DMs)
    if membership.role == 'DM':
        dice_rolls = DiceRollLog.objects.filter(campaign=campaign).order_by('created_at')
    else:
        dice_rolls = DiceRollLog.objects.filter(campaign=campaign, visibility='PUBLIC').order_by('created_at')
    
    # Serialize messages
    message_list = []
    for msg in visible_messages[:50]:  # Limit to last 50 messages
        # Use stored name for archival (preserves original username even if deleted)
        sender_name = msg.get_sender_display_name()
        sender_id = msg.sender.id if msg.sender else None
        
        # Determine display name based on message type (only for current user's messages)
        display_sender_name = sender_name
        if msg.message_type == 'IC' and membership.role == 'PLAYER' and msg.sender == request.user:
            # Show character name for IC messages
            try:
                char = Character.objects.get(user=request.user, campaign=campaign)
                display_sender_name = char.name
            except Character.DoesNotExist:
                pass
        
        # Check if this is a DM whisper to the current user
        is_dm_whisper_to_me = (msg.visibility_type == 'DM_ONLY' and msg.recipient == request.user)
        
        message_list.append({
            'id': msg.id,
            'content': msg.content,
            'sender_id': sender_id,
            'sender_name': display_sender_name,
            'real_sender_name': sender_name,
            'visibility_type': msg.visibility_type,
            'message_type': msg.message_type,
            'is_edited': msg.is_edited,
            'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'formatted_time': msg.created_at.strftime('%b %d, %H:%M'),
            'is_spectator': membership.role == 'SPECTATOR',
            'is_dm_whisper_to_me': is_dm_whisper_to_me,
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
        'user_role': membership.role,
        'has_character': Character.objects.filter(user=request.user, campaign=campaign).exists(),
    })


@login_required
@require_POST
def post_chat_message(request, campaign_pk):
    """Post a new chat message."""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    membership = get_object_or_404(CampaignMembership, user=request.user, campaign=campaign)
    
    data = json.loads(request.body)
    content = data.get('content', '').strip()
    visibility_type = data.get('visibility_type', 'PUBLIC')
    message_type = data.get('message_type', 'OOC_RELEVANT')
    recipient_user_id = data.get('recipient_user_id')
    
    if not content:
        return JsonResponse({'error': 'Message content is required'}, status=400)
    
    # Handle DM whispers to specific players/spectators
    dm_recipient = None
    if membership.role == 'DM' and data.get('visibility_type') in ['PLAYER_WHISPER', 'SPECTATOR_WHISPER']:
        if not recipient_user_id:
            return JsonResponse({'error': 'Recipient is required for whispers'}, status=400)
        
        recipient = get_object_or_404(User, pk=recipient_user_id)
        recipient_membership = CampaignMembership.objects.filter(user=recipient, campaign=campaign).first()
        
        if not recipient_membership:
            return JsonResponse({'error': 'Recipient is not a member of this campaign'}, status=400)
        
        # Validate recipient type matches whisper type
        if data.get('visibility_type') == 'PLAYER_WHISPER' and recipient_membership.role != 'PLAYER':
            return JsonResponse({'error': 'Selected recipient is not a player'}, status=400)
        if data.get('visibility_type') == 'SPECTATOR_WHISPER' and recipient_membership.role != 'SPECTATOR':
            return JsonResponse({'error': 'Selected recipient is not a spectator'}, status=400)
        
        # Store as DM_ONLY with recipient tracked
        visibility_type = 'DM_ONLY'
        dm_recipient = recipient
    
    # Validate visibility based on role
    if membership.role == 'SPECTATOR':
        # Spectators can only post PUBLIC OOC messages
        visibility_type = 'PUBLIC'
        message_type = 'OOC_RELEVANT'
    elif membership.role != 'DM' and visibility_type not in ['PUBLIC', 'DM_ONLY']:
        return JsonResponse({'error': 'Invalid visibility type'}, status=400)
    
    # Check if user has a character for IC messages
    if message_type == 'IC' and membership.role == 'PLAYER':
        if not Character.objects.filter(user=request.user, campaign=campaign).exists():
            return JsonResponse({'error': 'You need a character to send In-Character messages'}, status=400)
    
    # Handle split group visibility
    party_group = None
    if visibility_type == 'SPLIT_GROUP':
        if membership.role != 'DM':
            return JsonResponse({'error': 'Only DMs can send split-group messages'}, status=400)
        group_id = data.get('party_group_id')
        if group_id:
            party_group = get_object_or_404(PartyGroup, pk=group_id, campaign=campaign)
    
    # Create message
    message = ChatMessage.objects.create(
        content=content,
        sender=request.user,
        campaign=campaign,
        visibility_type=visibility_type,
        party_group=party_group,
        message_type=message_type,
        recipient=dm_recipient,
    )
    
    return JsonResponse({
        'success': True,
        'message_id': message.id,
    })


@login_required
@require_POST
def post_dice_roll(request, campaign_pk):
    """Post a dice roll result and create a chat message."""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    membership = get_object_or_404(CampaignMembership, user=request.user, campaign=campaign)
    
    data = json.loads(request.body)
    formula = data.get('formula', '').strip()
    result = data.get('result')
    modifier = data.get('modifier', 0)
    visibility = data.get('visibility', 'PUBLIC')
    
    if not formula or result is None:
        return JsonResponse({'error': 'Formula and result are required'}, status=400)
    
    # Validate visibility
    if membership.role != 'DM' and visibility == 'DM_ONLY':
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
def edit_chat_message(request, message_pk):
    """Edit a chat message (DMs/Admins can edit any, users can edit their own)."""
    message = get_object_or_404(ChatMessage, pk=message_pk)
    campaign = message.campaign
    membership = get_object_or_404(CampaignMembership, user=request.user, campaign=campaign)
    
    # Check permissions
    if membership.role != 'DM' and message.sender != request.user:
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
    membership = get_object_or_404(CampaignMembership, user=request.user, campaign=campaign)
    
    # Check permissions
    if membership.role != 'DM' and message.sender != request.user:
        return JsonResponse({'error': 'You do not have permission to delete this message'}, status=403)
    
    message.delete()
    
    return JsonResponse({'success': True})


@login_required
def manage_campaign_members(request, campaign_pk):
    """DM view to manage campaign members and assign roles."""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    membership = get_object_or_404(CampaignMembership, user=request.user, campaign=campaign)
    
    # Only DMs can manage members
    if membership.role != 'DM':
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
    if membership.role != 'DM':
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
    if membership.role == 'DM':
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