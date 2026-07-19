# To Do List

## High Priority 🔴
- [x] ✓ Fix crash when users refresh after campaign deletion:
  - Users get 404 error at `/campaign/<pk>/` when campaign is deleted but membership still exists
  - Need to redirect to dashboard or handle stale membership references

## Medium Priority 🟡
- [ ] 🔍 NPC Selection in Chat - DMs cannot easily choose which NPC to speak as:
  - Current implementation lacks NPC selector for IC messages
  - With many NPCs, scrolling through a single list is not practical
  - Solution: Add searchable dropdown with type-ahead filtering (type character name to filter)
  - Optionally group NPCs by campaign/character sheet for easier navigation
  - Should show avatar preview when selecting

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

- [ ] ⏳ Chat Message Type Editing - Rapid keyboard-driven full-screen mode:
  - Activate designated mode that pulls up chat in full-screen view
  - Navigate through messages rapidly using only keyboard (down arrow to move)
  - Read each message and change type with single key press (IC/OOC_RELEVANT/OOC_OFFTOPIC)
  - Auto-advance to next message after type change for efficient bulk editing
