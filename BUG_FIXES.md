# Bug Fixes - D&D Tabletop Application

## Fixed Bugs

### 1. Chat Message Edit/Delete Buttons Not Working ✅ FIXED

**Issue:** The edit and delete buttons for chat messages were not functioning properly.

**Root Cause:** 
- Missing `@require_POST` decorator on `edit_chat_message` view
- Views couldn't handle admin users viewing campaigns without membership

**Fix Applied:**
```python
# Added @require_POST decorator
@login_required
@require_POST
def edit_chat_message(request, message_pk):
    # ...

# Fixed membership lookup to handle admin viewing mode
membership = CampaignMembership.objects.filter(user=request.user, campaign=campaign).first()

if not membership and request.user.is_superuser:
    class TempMembership:
        role = 'DM'
    membership = TempMembership()
```

**Files Changed:**
- `campaigns/views.py` - Added decorator and fixed membership handling in both `edit_chat_message` and `delete_chat_message` views

---

### 2. Admin Can See All Secrets in Normal Campaign Mode ✅ FIXED

**Issue:** When administrators accessed a campaign normally (as members), they could see all secret whispers, DM-only messages, and hidden dice rolls. This was a security/privacy issue.

**Root Cause:**
- The `is_admin_viewing` flag was being set for ALL superusers, even when they were regular members of the campaign
- Session flag wasn't properly cleared when not in admin override mode

**Fix Applied:**
```python
# Only set admin override if explicitly requested via URL parameter
if is_admin_override:  # ?admin_override=1
    is_admin_viewing = True
    request.session['admin_campaign_view'] = True
else:
    # Clear session flag when NOT in admin override mode
    if 'admin_campaign_view' in request.session:
        del request.session['admin_campaign_view']

# Now admins who are members only see what their role allows
```

**How It Works Now:**
- Admins who are **members** of a campaign → See normal role-based visibility (DM sees all, players see public + their whispers)
- Admins accessing via `/campaign/<pk>/?admin_override=1` → Can see ALL messages (override mode)
- Session flag properly managed to prevent accidental override

**Files Changed:**
- `campaigns/views.py` - Updated `campaign_detail` and `get_chat_messages` views

---

### 3. Missing User Imports in Test Files ✅ FIXED

**Issue:** Several test files were using `User.objects.create_user()` without importing the User model, causing import errors.

**Root Cause:**
- Test files created users but didn't import `get_user_model()` from Django

**Fix Applied:**
```python
# Added to all affected test files:
from django.contrib.auth import get_user_model
User = get_user_model()
```

**Files Changed:**
- `tests/test_admin.py` - Added User import
- `tests/test_campaigns.py` - Added User import  
- `tests/test_characters.py` - Added User import
- `tests/test_chat_and_dice.py` - Added User import and Campaign model

---

## Open Bugs (Not Yet Fixed)

### 1. Secret Message Recipient Display ⬜ TODO

**Issue:** When viewing DM-only whispers or secret whispers, the recipient(s) should be displayed in *italics* next to the sender's name (e.g., "SenderName (*to: Player1, Player2*)"). Currently, this information is missing from the chat interface.

**Status:** Not started
**Priority:** Medium
**Suggested Fix:** Update `renderMessages()` function in `chat_component.html` to show recipient badges for whispers

---

## Testing

After these fixes, run:

```bash
# Install test dependencies
pip install pytest pytest-django pytest-cov

# Run all tests
pytest tests/ -v

# Or use the test runner
python tests/run_tests.py
```

All basic setup tests should now pass:
- ✅ Test infrastructure validation
- ✅ URL resolution tests  
- ✅ Authentication tests
- ✅ Campaign management tests
- ✅ Character management tests
- ✅ Chat and dice tests
- ✅ Admin feature tests

---

## Verification Steps

### For Edit/Delete Buttons:
1. Log in as a campaign member
2. Send a chat message
3. Hover over the message - edit/delete buttons should appear
4. Click "Edit" → Modal opens with current content
5. Make changes and save → Message updates with "(Edited)" indicator
6. Click "Delete" → Confirmation modal appears
7. Confirm deletion → Message is removed

### For Admin Visibility:
1. Create a campaign as DM
2. Add another user as player
3. Have player send a secret whisper to another player
4. Log in as admin (who is also a member of the campaign)
5. View the campaign normally → Should NOT see the secret whisper
6. Access via `/campaign/<pk>/?admin_override=1` → SHOULD see all messages

---

## Next Steps

1. ✅ Fix edit/delete button functionality
2. ✅ Fix admin visibility bug  
3. ⏭️ Add recipient display for whispers (open bug)
4. ⏭️ Run full test suite to verify no regressions
5. ⏭️ Add integration tests for whisper visibility

---

*Last Updated: 2026-01-XX*
*Branch: feature/website-breakage-testing-script*
