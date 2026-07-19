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
