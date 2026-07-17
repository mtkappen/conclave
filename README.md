# D&D Tabletop Application 🎲

A lightweight, self-contained Python web application for small Dungeons & Dragons groups (up to 12 players + spectators). Runs on a local network without external dependencies.

## Features (Phase 1 Complete) ✅

- **User Authentication**: Register, login, logout
- **Campaign Management**: Create and join campaigns
- **Character Sheets**: Full character creation with stats, HP, AC, etc.
- **Inventory System**: Add items to characters with images
- **DM Tools**: View all player character sheets in a campaign
- **Role-Based Access**: Admin, DM, Player, Spectator roles

## Technology Stack

- **Backend**: Django 4.2
- **Database**: SQLite (file-based, no server needed)
- **Server**: Django Development Server on port 8020
- **File Storage**: Local filesystem for images

## Quick Start

### First Time Setup

1. **Run the setup script:**
   ```powershell
   .\setup.bat
   ```

2. **Start the server:**
   ```powershell
   .\run_server.bat
   ```

3. **Access the application:**
   - Local: http://localhost:8020
   - Network: http://YOUR_IP:8020

### Default Admin Account

- **Username**: admin
- **Password**: admin123
- ⚠️ Change this after first login!

## User Roles

| Role | Permissions |
|------|-------------|
| **Administrator** | Create campaigns, manage all aspects, export data |
| **Dungeon Master (DM)** | Run games, view all character sheets, moderate chat |
| **Player** | Create characters, play in campaigns, roll dice |
| **Spectator** | Watch sessions, post OOC comments (read-only for stats) |

## Project Structure

```
dnd-app/
├── campaigns/           # Main app (models, views, forms)
├── dnd_app/            # Django project settings
├── templates/          # HTML templates
│   ├── base.html
│   ├── registration/   # Login/Register pages
│   └── campaigns/      # Campaign & character pages
├── media/              # User uploads (avatars, inventory images)
├── static/             # Static files (CSS, JS)
├── db.sqlite3          # Database file
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
├── setup.bat           # Setup script
└── run_server.bat      # Server startup script
```

## Next Phases (Coming Soon)

### Phase 2: Chat & Visibility 📝
- Real-time chat with auto-refresh
- Message types: In-Character, Out-of-Character
- DM-only whispers
- Color-coded messages

### Phase 3: Split Party & Dice 🎲
- Dynamic party groups for split sessions
- Private group chats
- Dice roller with hidden rolls
- Roll history and logs

### Phase 4: Character Management & Moderation 🛡️
- First-time user tutorial
- DM character roster view
- Message tagging workflow
- Edit/delete permissions

### Phase 5: Export & Polish 📦
- Campaign export (ZIP with data + images)
- Chat log export (CSV)
- UI polish and testing

## Network Access

To allow other computers on your network to access the app:

1. Find your IP address: `ipconfig` (look for IPv4 Address)
2. Share that IP with players: `http://YOUR_IP:8020`
3. Ensure Windows Firewall allows Python connections

## Troubleshooting

**Port already in use?**
- Change port in `run_server.bat`: `python manage.py runserver 8021`

**Database errors?**
- Delete `db.sqlite3` and run: `python manage.py migrate`

**Permission denied for media files?**
- Ensure the `media/` folder has write permissions

## License

This is a personal project for local D&D groups. Not for commercial use.

---

**Happy Adventuring!** 🐉⚔️🛡️