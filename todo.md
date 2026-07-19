# To Do List

## High Priority 🔴
- [x] ✓ Fix crash when users refresh after campaign deletion:
  - Users get 404 error at `/campaign/<pk>/` when campaign is deleted but membership still exists
  - Need to redirect to dashboard or handle stale membership references

## Medium Priority 🟡
- [ ] 🔧 Fix chat message edit/delete buttons disappearing on hover:
  - Edit and delete buttons do not stay visible while hovering over messages
  - Cannot click the buttons because they disappear before mouse can reach them
  - Need to fix CSS/JavaScript hover behavior for message actions

- [ ] 🚨 Security: Anyone can edit anyone else's messages:
  - Permission check in edit_chat_message allows users to edit others' messages
  - Only message owner, DMs, and admins should be able to edit messages
  - Need to fix permission logic to properly restrict access

## Low Priority 🟢
- [x] ✓ NPC Chat Support - Enable DMs to play as NPCs in chat:
  - Allow DMs to select from their created characters (NPCs) when posting IC messages
  - Add character selector dropdown in chat input for DMs
  - Display NPC name/avatar instead of DM's name when posting as character

- [ ] ⏳ Chat Message Type Editing - Allow DM/Admin to change message type (IC/OOC_RELEVANT/OOC_OFFTOPIC) for existing messages:
  - Current implementation requires opening edit modal (too slow for bulk editing)
  - Need a "rapid edit mode" where DMs/admins can quickly cycle through messages and change types
  - Should allow inline editing without diving into separate menus
