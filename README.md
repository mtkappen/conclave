# D&D Tabletop Application 🎲

A lightweight, self-contained Python web application for small Dungeons & Dragons groups (up to 12 players + spectators). Runs on a local network without external dependencies.

## ✅ Current Status: Production Ready

**Version**: Phase 2 Complete  
**Last Updated**: 2026-07-17  
**Total Commits**: 88+ commits with active development

---

## 🎯 Core Features (Fully Implemented)

### 🔐 User Management & Security
- **First-Time Admin Setup**: Automatic setup wizard when no users exist
- **Role-Based Access Control**: Administrator, DM, Player, Spectator roles
- **Secure Authentication**: Login/logout with password enforcement
- **Forced Password Change**: Users must change default passwords on first login
- **Voluntary Password Changes**: All users can update passwords anytime
- **Admin User Management**: Create, view, and delete user accounts
- **Database Reset**: Complete system reset for fresh starts

### 🏰 Campaign System
- **Create & Manage Campaigns**: Full CRUD operations for campaigns
- **Campaign Membership**: Invite players with specific roles (DM/Player/Spectator)
- **Role Assignment**: DMs can manage member roles and remove players
- **Campaign Roster**: View all members and their characters
- **Active Campaign Tracking**: Automatic tracking of last activity date
- **Admin Campaign Overview**: Global view of all campaigns

### 📜 Character Management
- **Full Character Sheets**: Stats, class, level, HP, AC, and descriptions
- **Character Avatars**: Upload character images
- **Six Ability Scores**: Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma
- **Combat Statistics**: Health points, max HP, armor class tracking
- **DM Roster View**: DMs can view all player characters in campaign
- **Edit & Delete**: Players manage own characters; DMs manage all

### 🎒 Inventory System
- **Item Management**: Add items with name, quantity, weight, description
- **Item Images**: Upload photos for inventory items
- **Weight Tracking**: Decimal precision for encumbrance calculations
- **Character-Specific**: Each character has independent inventory

### 💬 Real-Time Chat System (Phase 2 Complete)
- **Auto-Refresh Chat**: Updates every 4 seconds via JavaScript polling
- **Message Types**:
  - 🗨️ **Public**: Visible to all campaign members
  - 🔒 **DM Only**: Sender and DM only (purple border)
  - 🤫 **Secret Whisper**: Selected recipients only, can exclude DM!
  - 👥 **Split Group**: Visible to specific party groups (blue border)

- **Message Categories**:
  - 🎭 **In-Character (IC)**: Displays character name for players
  - 💬 **Out-of-Character Relevant**: Game-related OOC discussion
  - ☕ **Out-of-Character Off Topic**: Casual chat
  - 🎲 **Dice Rolls**: Automatic formatting for roll results

- **Advanced Features**:
  - Multi-recipient whispers (hold Ctrl/Cmd to select multiple)
  - Edit/delete messages (DMs can edit any, users own messages only)
  - "(Edited)" indicator on modified messages
  - Spectator badge on spectator posts
  - Resizable chat box with persistent height preference
  - Tab filtering: All / Story-IC / Game-OOC

### 🎲 Dice Roller System
- **Quick Roll Buttons**: d4, d6, d8, d10, d12, d20
- **Custom Rolls**: Configure count, type, and modifier
- **Hidden Rolls**: DM-only visibility option (players see "???")
- **Automatic Logging**: All rolls saved to database
- **Chat Integration**: Dice results appear in chat stream
- **Roll History**: View recent dice rolls in sidebar

### 📝 Personal Tools
- **Personal Notebook**: Private notes per campaign (only owner can view/edit)
- **Campaign Rule Book**: DM-editable rules visible to all members
- **Persistent Storage**: All data saved locally with SQLite

### 👁️ Admin & Moderation Features
- **View All Secrets**: Admin override panel to see all whispers and hidden messages
- **User Activity Tracking**: View message counts, character counts per user
- **Campaign Management**: Delete campaigns, manage members globally
- **Database Reset**: Complete wipe and fresh start option
- **Audit Trail**: Edited messages marked, sender names preserved on deletion

### 🖥️ Desktop & Mobile Optimization
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Desktop Layout**: Optimized spacing for large screens (up to 1400px)
- **Full-Width Content**: Utilizes available screen real estate effectively
- **Mobile-Friendly**: Touch-friendly buttons and navigation
- **Customizable Chat**: Resizable chat box with localStorage persistence

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend Framework** | Django 4.2 |
| **Database** | SQLite (file-based, no server needed) |
| **Server** | Django Development Server (port 8020) |
| **Frontend** | HTML5, CSS3, JavaScript (vanilla) |
| **File Storage** | Local filesystem for images and avatars |
| **Authentication** | Django Auth System with custom user model |

## 🚀 Quick Start Guide

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

- **Username**: `admin`
- **Password**: `admin123`
- ⚠️ **Important**: Change this password immediately after first login!

---

## 👥 User Roles & Permissions

| Role | Permissions |
|------|-------------|
| **Administrator** (Superuser) | Create campaigns, manage all users, view all secrets, database reset, full system access |
| **Dungeon Master (DM)** | Create campaign, manage members, edit any character, view all messages, control split groups, edit rule book |
| **Player** | Create character, send IC/OOC messages, roll dice, edit own character, maintain personal notebook |
| **Spectator** | View campaigns, post public OOC messages only, read-only access to stats |

---

## 📁 Project Structure

```
conclave/
├── campaigns/                 # Main Django app
│   ├── models.py             # User, Campaign, Character, ChatMessage, etc.
│   ├── views.py              # All view logic (40+ functions)
│   ├── forms.py              # Django forms for user input
│   ├── urls.py               # URL routing (30+ routes)
│   └── middleware.py         # Custom middleware
├── dnd_app/                  # Project settings
│   ├── settings.py           # Django configuration
│   ├── urls.py               # Main URL router
│   └── wsgi.py              # WSGI config
├── templates/                # HTML templates
│   ├── base.html            # Base template with navbar & CSS
│   ├── dashboard.html       # Main user dashboard
│   ├── registration/        # Auth templates (login, setup, password)
│   └── campaigns/           # Campaign-specific templates
│       ├── detail.html      # Campaign page with chat & dice
│       ├── chat_component.html  # Reusable chat UI
│       ├── dice_roller.html     # Dice rolling interface
│       └── ... (20+ templates)
├── static/                   # CSS, JavaScript, images
│   └── css/                 # Stylesheets with responsive design
├── media/                    # User uploads
│   ├── avatars/             # User profile pictures
│   ├── characters/          # Character sheet images
│   └── inventory/           # Item images
├── db.sqlite3               # SQLite database (auto-created)
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── setup.bat               # One-click setup script
└── run_server.bat          # One-click server startup
```

---

## 📊 Development Status

### ✅ Completed Features
- **Phase 1**: User auth, campaigns, characters, inventory, role management ✓
- **Phase 2**: Real-time chat, visibility controls, dice roller, desktop optimization ✓
- **Security**: Password enforcement, admin user management, database reset ✓
- **Privacy**: Multi-recipient whispers, secret messages, admin override panel ✓
- **UX**: Resizable chat, responsive design, persistent preferences ✓

### 📈 Project Metrics
- **Total Commits**: 88+
- **Lines of Code**: ~6,000+ (Python + templates)
- **Views Implemented**: 40+
- **URL Routes**: 30+
- **Models**: 10 (User, Campaign, Character, ChatMessage, DiceRollLog, etc.)

---

## 🌐 Network Access Setup

To allow other computers on your network to access the app:

1. **Find your IP address:**
   ```powershell
   ipconfig  # Look for IPv4 Address (e.g., 192.168.1.100)
   ```

2. **Share with players:** `http://YOUR_IP:8020`

3. **Windows Firewall**: Allow Python connections when prompted, or create inbound rule for port 8020

---

## 🔧 Troubleshooting

### Port Already in Use?
Change the port in `run_server.bat`:
```powershell
python manage.py runserver 8021
```

### Database Errors?
Reset the database:
```powershell
# Delete db.sqlite3
del db.sqlite3
# Run migrations
python manage.py migrate
# Or use the admin database reset feature in-app
```

### Permission Denied for Media Files?
Ensure the `media/` folder has write permissions for your user account.

### Chat Not Updating?
- Check browser console for JavaScript errors
- Verify auto-refresh is working (messages should update every 4 seconds)
- Try hard refresh: `Ctrl + F5`

---

## 🐛 Known Issues

See [known_bugs.md](known_bugs.md) for current tracking of bugs and planned fixes.

---

## 🔒 Security Notes

- **Local Network Only**: Not designed for internet deployment
- **Admin Override**: Global admins can view all private messages (use responsibly)
- **Password Requirements**: Minimum 8 characters, confirmation required
- **CSRF Protection**: All forms include Django CSRF tokens
- **Role Validation**: Server-side permission checks on all views

---

## 📄 License

This is a personal project for local D&D groups. Not for commercial use.

---

## 🎮 User Guide Highlights

### Creating Your First Campaign
1. Log in as admin or DM
2. Click "Create New Campaign" on dashboard
3. Enter title and description
4. You become the Dungeon Master automatically

### Adding Players to Campaign
1. Go to campaign detail page
2. Click "Manage Members" (DM only)
3. Select user from dropdown and assign role
4. Player receives access immediately

### Sending Secret Messages
1. In chat, select "🤫 Secret Whisper" from visibility dropdown
2. Hold Ctrl/Cmd and click to select multiple recipients
3. Type message and send
4. Only you and selected recipients can see it (not even DM!)

### Rolling Dice
1. Use quick buttons in sidebar (d4, d6, d8, etc.)
2. Or configure custom roll with count/type/modifier
3. Check "Hide from players" for secret rolls
4. Results appear in chat automatically

---

**Happy Adventuring!** 🐉⚔️🛡️

*Built with Django for tabletop gaming groups.*