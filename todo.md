# To Do List

## User Settings ✅
- [x] Add user settings page so users can change account details:
  - [x] Full name
  - [x] Password
  - [x] Profile picture
  - [x] Other account preferences
- [x] Added user statistics (campaigns, messages, characters, dice rolls)
- [x] Updated dropdown menu with avatar display

## Chat Color Schemes ✅
- [x] Update chat color scheme logic:
  - [x] Use user's profile picture when posting as themselves
  - [x] Use character's profile picture when posting as character
  - [x] In-character chat bubbles should be teal (#40E0D0)
  - [x] Keep secret whisper messages as purple (unchanged)

## Bug Reports
- Profile pictures do not show up correctly in chat messages
- Fix edit and delete boxes for chat messages - buttons/boxes not displaying correctly or missing from chat interface
- Admin can see all secrets in normal campaign mode - security issue where admins view DM whispers and hidden dice rolls at `/campaign/<pk>/` instead of only via admin interface
- Show recipient in secret messages - recipient(s) should be displayed in italics next to sender's name for DM-only or split-group whispers

## Character Creation Flexibility
- Make character creation more flexible for other games beyond D&D:
  - Allow custom stat systems instead of fixed D&D stats
  - Support different class/role naming conventions
  - Enable customizable character fields per campaign type
  - Add support for various game systems (Pathfinder, World of Darkness, etc.)

## Campaign Game System Configuration
- [ ] Add UI for DMs to configure game system settings for campaigns:
  - [ ] Create "Configure Game System" page in DM Actions section
  - [ ] Allow selection of game system (D&D 5e, custom, etc.)
  - [ ] Enable customization of attributes, skills, and combat stats per campaign

## Bug Fixes
- [ ] Fix crash when users refresh after campaign deletion:
  - Users get 404 error at `/campaign/<pk>/` when campaign is deleted but membership still exists
  - Need to redirect to dashboard or handle stale membership references

## Chat Message Type Editing
- [ ] Allow DM/Admin to change message type (IC/OOC_RELEVANT/OOC_OFFTOPIC):
  - Add edit option to change message_type for existing messages
  - Currently only content can be edited, not the message classification

## NPC Chat Support
- [ ] Enable DMs to play as NPCs in chat:
  - Allow DMs to select from their created characters (NPCs) when posting IC messages
  - Add character selector dropdown in chat input for DMs
  - Display NPC name/avatar instead of DM's name when posting as character
