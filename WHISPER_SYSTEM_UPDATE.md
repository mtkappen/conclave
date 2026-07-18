
# Whisper System Update - Multi-Recipient & Admin Override

## Overview
Implemented a comprehensive whisper system that allows users to send private messages to multiple recipients, with the ability to exclude even the DM. The global administrator retains ultimate oversight through a special admin panel.

## Key Features

### 1. **Multi-Recipient Whispers**
- Users can now select **multiple recipients** for whisper messages
- Hold Ctrl (Cmd on Mac) to select multiple people from the dropdown
- Works for both Players and DMs/Superusers

### 2. **Three Privacy Levels**

#### **Public Messages** 👥
- Visible to everyone in the campaign
- Default message type

#### **DM Only** 🔒
- Only visible to the sender and the Dungeon Master
- Traditional whisper to DM functionality
- Other players cannot see these messages

#### **Secret Whisper** 🤫
- **NEW**: Selected recipients only (can exclude DM!)
- Players can send secrets to other players without the DM seeing
- DMs can send secrets to specific people
- Only visible to:
  - The sender
  - All selected recipients
  - Global Administrator (via admin panel)

### 3. **Admin Override Capability** 🔐
- Global administrators can view ALL secret whispers through a special admin panel
- Accessible via "🔐 View Secrets" button in campaign chat header (admin only)
- Shows both Secret Whispers and DM-Only messages
- Includes warning banner about responsible use

## Technical Changes

### Database Schema (`campaigns/models.py`)
- **Removed**: Single `recipient` ForeignKey field
- **Added**: Multi-relationship `recipients` ManyToManyField for multiple recipients
- **Updated**: Added `SECRET_WHISPER` visibility type option
- **Backwards Compatible**: Old `recipient` field removed (migration handles this)

### View Updates (`campaigns/views.py`)
1. **`get_chat_messages()`**: Updated filtering logic to handle multi-recipient whispers
   - Players see their own secret whispers and those sent to them
   - DMs/Admins see everything by default
   - Secret whispers exclude DM unless they're selected as recipients

2. **`post_chat_message()`**: Enhanced to accept multiple recipient IDs
   - Accepts `recipient_user_ids` array instead of single ID
   - Validates all recipients are campaign members
   - Supports backwards compatibility with old single-recipient format

3. **`admin_view_secret_whispers()`**: NEW admin-only view
   - Shows all secret whispers in a campaign
   - Displays DM-only messages for completeness
   - Only accessible by superusers

### Template Updates (`templates/campaigns/chat_component.html`)
- Replaced separate "Whisper to Player" and "Whisper to Spectator" options with unified "Secret Whisper"
- Added multi-select dropdown for recipients
- Updated JavaScript to handle multiple recipient selection
- Added admin-only "View Secrets" button in chat header

### New Template (`templates/campaigns/admin_view_secrets.html`)
- Dedicated page for admins to view all private messages
- Styled with warning banner about responsible use
- Shows sender, recipients, content, and edit status
- Separates Secret Whispers from DM-Only messages

### URL Configuration (`campaigns/urls.py`)
- Added new route: `/admin/campaign/<pk>/secrets/` for admin secret viewer

### Database Migration
- Created migration `0008_add_secret_whisper_and_multi_recipients.py`
- Successfully applied to database

## Usage Instructions

### For Players:
1. Select "🤫 Secret Whisper (Select Recipients)" from visibility dropdown
2. Hold Ctrl/Cmd and click to select multiple recipients
3. Type your message and send
4. Only you and selected recipients will see it (not even the DM!)

### For DMs:
1. Same as players - can send secret whispers to anyone
2. Can also view all messages normally in chat
3. Cannot see other people's secret whispers unless they're recipients

### For Global Administrators:
1. Visit any campaign page
2. Click "🔐 View Secrets" button in chat header (only visible to admins)
3. Review all secret whispers and DM-only messages
4. Use responsibly - this is an override capability for when absolutely necessary

## Privacy Model

```
Message Type      | Sender | Recipients | DM | Other Players | Admin
------------------|--------|------------|----|---------------|-------
Public            | ✅     | Everyone   | ✅ | ✅            | ✅
DM Only           | ✅     | DM         | ✅ | ❌            | ✅
Secret Whisper    | ✅     | Selected   | ❌*| ❌            | ✅
```

*DM only sees secret whispers if they are explicitly selected as a recipient

## Backwards Compatibility
- Old single-recipient whisper format still works via `recipient_user_id` parameter
- Automatically converted to DM_ONLY visibility type
- Existing messages with old structure remain accessible

## Security Notes
- All privacy restrictions enforced server-side (not just frontend)
- Admin override requires superuser privileges
- Warning displayed when accessing admin secret viewer
- Audit trail maintained (edited messages marked)

## Future Enhancements
Potential improvements for future versions:
- Admin audit log of when secrets are viewed
- Optional notification to users when their secrets are viewed by admin
- Time-limited secret whispers that auto-delete
- Export functionality for admins
