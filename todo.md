# To Do List

## High Priority
- [ ] Fix crash when users refresh after campaign deletion:
  - Users get 404 error at `/campaign/<pk>/` when campaign is deleted but membership still exists
  - Need to redirect to dashboard or handle stale membership references

## Medium Priority
- [ ] NPC Chat Support - Enable DMs to play as NPCs in chat:
  - Allow DMs to select from their created characters (NPCs) when posting IC messages
  - Add character selector dropdown in chat input for DMs
  - Display NPC name/avatar instead of DM's name when posting as character

## Low Priority
- [ ] Chat Message Type Editing - Allow DM/Admin to change message type (IC/OOC_RELEVANT/OOC_OFFTOPIC) for existing messages:
  - Add edit option to change message_type for existing messages
  - Currently only content can be edited, not the message classification
