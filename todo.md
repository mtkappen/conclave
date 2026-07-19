# To Do List

## High Priority 🔴
- [x] ✓ Fix crash when users refresh after campaign deletion:
  - Users get 404 error at `/campaign/<pk>/` when campaign is deleted but membership still exists
  - Need to redirect to dashboard or handle stale membership references

## Medium Priority 🟡
- [x] ✓ NPC Selection in Chat - DMs cannot easily choose which NPC to speak as:
  - Implemented searchable dropdown with type-ahead filtering for NPCs
  - Avatar preview when browsing NPC options
  - Fixed variable name mismatch (characters vs npcs)

- [x] ✓ Fix chat message edit/delete buttons disappearing on hover:
  - Added invisible padding extension (175px) to message bubbles
  - Buttons slide out from 2rem to 4rem on hover for all message types
  - Fixed positioning for user messages and received messages

- [x] 🚨 Security: Anyone can edit anyone else's messages:
  - Fixed permission check in edit_chat_message (was using OR operator incorrectly)
  - Fixed permission check in delete_chat_message (non-members could bypass)
  - Added admin override mode support for superusers viewing without membership

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
