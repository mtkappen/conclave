# Website Links Inventory

This document contains a complete inventory of all links and URLs in the D&D Tabletop application.

## URL Routes (from campaigns/urls.py)

### Authentication & Setup
- `/setup/` - First-time admin setup
- `/login/` - Login page
- `/logout/` - Logout action
- `/change-password/` - Change password (admin forced)
- `/voluntary-change-password/` - Voluntary password change

### User Management (Admin Only)
- `/users/` - Admin user list
- `/users/create/` - Create new user
- `/users/<pk>/delete/` - Delete user

### Campaign Management (Admin Only)
- `/admin/campaigns/` - Admin campaign list
- `/admin/database-reset/` - Database reset

### Main Dashboard
- `/` - Dashboard (home page)

### Campaign Operations
- `/campaign/create/` - Create new campaign
- `/campaign/<pk>/` - Campaign detail view
- `/campaign/<pk>/delete/` - Delete campaign

### Character Management
- `/campaign/<campaign_pk>/character/create/` - Create character
- `/character/<pk>/` - Character detail view
- `/character/<pk>/edit/` - Edit character
- `/character/<character_pk>/inventory/add/` - Add inventory item
- `/character/<pk>/delete/` - Delete character

### DM Tools
- `/campaign/<campaign_pk>/dm/roster/` - View DM roster

### Chat & Communication
- `/campaign/<campaign_pk>/chat/messages/` - Get chat messages (API)
- `/campaign/<campaign_pk>/chat/post/` - Post chat message (API)
- `/campaign/<campaign_pk>/dice/post/` - Post dice roll (API)
- `/chat/message/<message_pk>/edit/` - Edit chat message (API)
- `/chat/message/<message_pk>/delete/` - Delete chat message (API)

### Member Management
- `/campaign/<campaign_pk>/members/` - Manage campaign members
- `/campaign/<campaign_pk>/members/add/` - Add member to campaign
- `/membership/<membership_pk>/role/` - Update member role
- `/membership/<membership_pk>/remove/` - Remove member from campaign
- `/campaign/<campaign_pk>/leave/` - Leave campaign

### Admin Tools
- `/admin/campaign/<campaign_pk>/secrets/` - View secret whispers (admin)

### Personal Features
- `/campaign/<campaign_pk>/notebook/` - Personal notebook
- `/notebook/<pk>/delete/` - Delete personal notebook entry

### Campaign Rule Book
- `/campaign/<campaign_pk>/rule-book/` - View rule book
- `/campaign/<campaign_pk>/rule-book/edit/` - Edit rule book

---

## Navigation Links (from templates)

### Base Template (`templates/base.html`)
**Authenticated User:**
- Dashboard: `{% url 'campaigns:dashboard' %}` → `/`
- Users (superuser only): `{% url 'campaigns:admin_user_list' %}` → `/users/`
- All Campaigns (superuser only): `{% url 'campaigns:admin_campaign_list' %}` → `/admin/campaigns/`
- New Campaign: `{% url 'campaigns:create_campaign' %}` → `/campaign/create/`
- Change Password: `{% url 'campaigns:voluntary_change_password' %}` → `/voluntary-change-password/`
- Logout: `{% url 'campaigns:logout' %}` → `/logout/`

**Unauthenticated User:**
- Sign In: `{% url 'campaigns:login' %}` → `/login/`

### Dashboard (`templates/dashboard.html`)
- Manage Users (superuser): `{% url 'campaigns:admin_user_list' %}` → `/users/`
- Create New Campaign: `{% url 'campaigns:create_campaign' %}` → `/campaign/create/`
- Enter Campaign: `{% url 'campaigns:campaign_detail' pk %}` → `/campaign/<pk>/`
- View Roster (DM only): `{% url 'campaigns:dm_roster' pk %}` → `/campaign/<pk>/dm/roster/`

### Dashboard VSCode Theme (`templates/dashboard_vscode.html`)
Same links as dashboard.html

### Admin User List (`templates/registration/admin_user_list.html`)
- Back to Dashboard: `{% url 'campaigns:dashboard' %}` → `/`
- Delete User: `{% url 'campaigns:delete_user' pk %}` → `/users/<pk>/delete/`
- Create New User: `{% url 'campaigns:admin_create_user' %}` → `/users/create/`
- Database Reset: `{% url 'campaigns:database_reset' %}` → `/admin/database-reset/`

### Admin Delete User (`templates/registration/admin_delete_user.html`)
- Cancel: `{% url 'campaigns:admin_user_list' %}` → `/users/`

### Chat Component (`templates/campaigns/chat_component.html`)
- Return to Admin Campaign List (superuser): `{% url 'campaigns:admin_campaign_list' %}` → `/admin/campaigns/`
- View Secrets (superuser): `{% url 'campaigns:admin_view_secrets' pk %}` → `/admin/campaign/<pk>/secrets/`
- Refresh: JavaScript action (no link)
- Create Character (if no character): `{% url 'campaigns:create_character' pk %}` → `/campaign/<pk>/character/create/`

### Create Character (`templates/campaigns/create_character.html`)
- Cancel: `{% url 'campaigns:campaign_detail' pk %}` → `/campaign/<pk>/`
- Stat Guide: JavaScript alert (no actual link)

---

## Static Assets & External Links

### Favicon
- Inline SVG favicon (data URI, no external request)

### CSS/JS Files
- Check `static/` directory for all static assets referenced in templates

---

## Notes for Testing

1. **Dynamic URLs**: Many links use Django's `{% url %}` template tag with dynamic parameters (pk values)
2. **Conditional Links**: Some links only appear based on user authentication status or permissions
3. **API Endpoints**: Chat and dice endpoints are used via AJAX, not direct navigation
4. **Admin-Only Routes**: Several routes require superuser privileges

## Testing Priorities

### Critical Paths (Must Test)
1. User registration → login → dashboard flow
2. Campaign creation → character creation → campaign entry
3. Chat functionality (real-time updates)
4. Dice rolling feature
5. Admin user management
6. Password change flows

### Edge Cases to Test
1. Accessing admin routes without permissions
2. Deleting non-existent resources
3. Character inventory operations
4. Member role changes
5. Secret whisper visibility controls

---

*Generated: 2026-07-18*
*Branch: feature/website-breakage-testing-script*
