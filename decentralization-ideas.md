Here's a consolidated design based on everything we've discussed so far.

# Project Vision

A **cross-platform desktop D&D application** written in **Rust** that works:

* Offline
* On a local network (LAN)
* Across the Internet
* Without requiring a permanent hosted server

Every player runs the same application.

---

# Core Philosophy

The application is **peer-to-peer and decentralized**.

Every participant stores a complete copy of the campaign locally.

There is **no permanent game server**.

Players synchronize data whenever they connect.

---

# Campaign Storage

Each computer contains:

* Campaign database (SQLite)
* Maps
* Character data
* Chat history
* Event history
* Assets (or references to shared assets)

Every peer has a full copy of the campaign.

---

# Synchronization Model

The application does **not** synchronize the current state.

Instead, it synchronizes an **event log**.

Example:

```
PlayerJoined

TokenMoved

GoblinDamaged

ChatMessage

SpellCast

InitiativeStarted

ItemPickedUp
```

When peers connect, they:

1. Compare known events.
2. Exchange missing events.
3. Replay events to rebuild the current state.

This naturally supports offline play and synchronization after reconnecting.

---

# DM Authority

The DM is the authoritative role for world changes.

Players generally do **not** directly modify shared world state.

Instead they submit requests.

For example:

```
Player
    ↓
Attack Goblin
    ↓
DM approves (or auto-approves)
    ↓
Official event created
    ↓
Everyone updates
```

This avoids most synchronization conflicts.

The **DM is an authority, not a server**.

---

# Data Ownership

### DM-owned

* Maps
* Fog of war
* NPCs
* Monsters
* Combat state
* Initiative
* World journal
* Quests
* Treasure
* Encounters

Only the DM creates official events affecting these.

---

### Player-owned

* Character sheet (if desired)
* Personal inventory
* Prepared spells
* Personal notes
* UI preferences
* Hotkeys
* Macros

Only that player edits these.

---

### Shared append-only

Everyone can add:

* Chat
* Dice rolls
* Combat log
* Timeline

These are never edited after they're created.

---

# Networking

### Local Network

Automatic discovery.

Players open the app.

The app discovers available campaigns.

Players join directly.

---

### Internet

Players connect directly when possible.

If direct peer-to-peer is not possible because of NATs or firewalls, an optional relay can forward encrypted traffic. The relay only forwards packets; it doesn't store campaign data or run game logic.

---

# Event Types

Examples:

```
ChatMessage

RollDice

MoveToken

DamageCreature

HealCreature

CastSpell

RevealFog

ChangeInitiative

TransferDM

AddItem

RemoveItem
```

Every event is immutable.

History is never rewritten.

---

# Offline Support

If someone disconnects:

They continue using the campaign.

The application records new events locally.

When another player reconnects later:

```
Compare event history

↓

Exchange missing events

↓

Continue playing
```

No special offline mode is required because offline operation is the default.

---

# Chat

Chat is just another event.

```
ChatMessage
{
    author
    timestamp
    message
}
```

Messages synchronize exactly like everything else.

---

# Dice

Dice rolls are also events.

```
RollRequested

↓

RollRecorded

↓

CombatLog
```

The campaign history permanently records rolls.

---

# Conflict Resolution

Because the DM owns shared world state, conflicts are minimized.

Most objects have a single writer:

* DM writes world state.
* Players write their own data.
* Everyone appends to logs.

This greatly simplifies synchronization.

---

# Role Transfer

The DM is represented as a role.

```
TransferDM

Alice

↓

Bob
```

Authority moves without migrating servers or databases.

---

# Storage

SQLite is the local database.

It stores:

* Campaign
* Event log
* Settings
* Characters
* Maps
* Assets
* Metadata

SQLite is portable, fast, and easy to back up.

---

# Rust Architecture

A Cargo workspace with separate crates:

```
workspace/
│
├── app/          # Desktop executable
├── core/         # Game engine
├── network/      # Peer sync, LAN discovery, relay support
├── storage/      # SQLite and persistence
├── protocol/     # Shared event definitions
└── ui/           # Desktop interface
```

Keeping these concerns separate should make the codebase easier to test and evolve.

---

# UI

The application is a native desktop app for:

* Windows
* macOS
* Linux

Two promising approaches are:

* **egui** if you want to stay entirely in Rust.
* **Tauri** if you're comfortable building the UI with HTML/CSS/JavaScript while keeping the backend in Rust.

---

# Long-Term Goal

The application behaves less like a traditional client/server game and more like a collaborative distributed system.

Each participant owns a complete copy of the campaign.

The campaign itself is a shared, append-only history of events.

The DM serves as the authority for the game world rather than as a dedicated host, allowing the campaign to continue syncing whenever peers reconnect without requiring a permanent central server.

## One addition I'd recommend

One enhancement I think would fit this design well is to give every campaign a **globally unique Campaign ID** (for example, a UUID) and every event a **monotonically increasing sequence number assigned by the current DM** plus a unique event ID. That gives you a canonical ordering for authoritative game events while still allowing players to create local events (like chat drafts or personal notes) offline and merge them cleanly later. It keeps synchronization deterministic without giving up the decentralized nature of the application.


It should also include voice chat and voice transcription that updates the chat with what they said. Debating on whether transcription should be done by the node or on device.


Absolutely. I think we've converged on a pretty coherent architecture. If I were starting this project today, this is the design document I'd work from.

---

# Phase 1 - Foundation

## ✅ Rust Workspace

* [ ] Create Cargo workspace
* [ ] `app` (desktop application)
* [ ] `core` (game engine)
* [ ] `protocol` (shared event definitions)
* [ ] `network` (peer sync)
* [ ] `storage` (SQLite)
* [ ] `node` (optional always-online peer)
* [ ] `ui`

---

## ✅ Cross Platform Desktop

* [ ] Windows
* [ ] macOS
* [ ] Linux

Choose UI framework

* [ ] egui (recommended if staying entirely in Rust)
  OR
* [ ] Tauri

---

# Phase 2 - Identity

No usernames/passwords.

Each installation generates:

* [ ] Ed25519 keypair
* [ ] Player ID
* [ ] Display name
* [ ] Avatar

Recovery

* [ ] Export identity
* [ ] Import identity
* [ ] Multiple trusted devices (future)

---

# Phase 3 - Campaign Model

Every campaign has

* [ ] UUID
* [ ] Metadata
* [ ] Members
* [ ] Permissions
* [ ] Event log
* [ ] Assets
* [ ] Settings

Stored locally as SQLite.

---

# Phase 4 - Event System

Everything becomes immutable events.

Examples

```text
CampaignCreated

MemberInvited

MemberRemoved

TransferDM

ChatMessage

VoiceTranscript

DiceRolled

MoveToken

Attack

DamageCreature

HealCreature

CastSpell

RevealFog

InitiativeChanged

QuestUpdated

InventoryChanged
```

Rules

* [ ] Events are immutable.
* [ ] Never edit history.
* [ ] Rebuild current state from events.

---

# Phase 5 - Ownership Model

## DM owned

* [ ] Maps
* [ ] NPCs
* [ ] Monsters
* [ ] Fog
* [ ] Initiative
* [ ] World notes
* [ ] Combat
* [ ] Loot

---

## Player owned

* [ ] Character
* [ ] Personal inventory
* [ ] Prepared spells
* [ ] Notes
* [ ] UI preferences

---

## Shared append-only

* [ ] Chat
* [ ] Dice
* [ ] Voice transcripts
* [ ] Combat log

---

# Phase 6 - Networking

Support

* [ ] Offline
* [ ] LAN
* [ ] Internet

Networking stack

* [ ] QUIC
* [ ] TLS
* [ ] Peer synchronization

LAN

* [ ] Auto discovery

Internet

* [ ] Direct peer-to-peer when possible.
* [ ] Optional relay/node when direct connections aren't possible.

---

# Phase 7 - Synchronization

When peers meet

```text
Compare event IDs

↓

Exchange missing events

↓

Replay

↓

Done
```

No database replication.

Only event synchronization.

---

# Phase 8 - Optional Node

Node capabilities

* [ ] Relay traffic
* [ ] Store campaign
* [ ] Store assets
* [ ] Synchronize peers
* [ ] Cache updates
* [ ] Optional transcription
* [ ] Optional AI features
* [ ] Optional backups

Important

The node **does not own the campaign.**

It is simply another peer that usually stays online.

---

# Phase 9 - Permissions

Roles

* [ ] Player
* [ ] DM
* [ ] Admin
* [ ] Spectator (optional)

Permissions

* [ ] Join
* [ ] Chat
* [ ] Voice
* [ ] Character control
* [ ] DM authority
* [ ] Invite
* [ ] Remove members

---

# Phase 10 - Voice

Voice codec

* [ ] Opus

Voice

* [ ] Push-to-talk
* [ ] Voice activation
* [ ] Mute
* [ ] Volume controls

---

Transcription

Preferred

```text
Speaker

↓

Local transcription

↓

Transcript event

↓

Everyone receives identical text
```

Optional

Node performs transcription if clients request it.

---

# Phase 11 - Chat

Support

* [ ] Rich text
* [ ] Images
* [ ] Dice rolls
* [ ] System messages
* [ ] Search
* [ ] Voice transcript integration

Everything stored as events.

---

# Phase 12 - Assets

Synchronize

* [ ] Maps
* [ ] Tokens
* [ ] Portraits
* [ ] Music
* [ ] Handouts

Node may cache assets.

---

# Phase 13 - Security

Authentication

* [ ] Public/private keys

Connections

* [ ] Signed challenges

Encryption

* [ ] TLS/QUIC

Future

* [ ] Campaign encryption keys
* [ ] Rotate keys when members removed

---

# Phase 14 - Membership

Events

```text
InviteMember

AcceptInvite

RemoveMember

TransferDM
```

Removing someone

* [ ] Disconnect immediately
* [ ] Reject future connections
* [ ] Stop future synchronization

Cannot

* [ ] Delete data already downloaded

---

# Phase 15 - Offline

Everything should continue working offline.

Reconnect

```text
Compare events

↓

Download missing

↓

Continue
```

---

# Phase 16 - AI (Future)

Optional

* [ ] Voice summaries
* [ ] Session recap
* [ ] NPC extraction
* [ ] Quest tracking
* [ ] Loot suggestions
* [ ] Timeline
* [ ] Semantic search

All optional.

---

# Phase 17 - Nice Features

* [ ] Campaign backups
* [ ] Multi-device sync
* [ ] Co-DM support
* [ ] Session recording (transcript only)
* [ ] Searchable campaign history
* [ ] Plugins/mods
* [ ] WASM scripting
* [ ] Mobile companion app
* [ ] Web spectator mode

---

# Overall Architecture

```text
                 Desktop App
                      │
      ┌───────────────┼────────────────┐
      │               │                │
  UI Layer      Game Engine      Voice/Chat
      │               │                │
      └───────────────┼────────────────┘
                      │
                Event System
                      │
          ┌───────────┴───────────┐
          │                       │
     SQLite Storage         Networking
                                  │
               ┌──────────────────┴─────────────────┐
               │                                    │
          LAN Peers                     Optional Node
                                             │
                                 Relay • Sync • Cache
```

## One major feature I'd add

The one thing I'd add that we haven't explicitly discussed is **asset deduplication with content hashes**.

Instead of identifying maps and images by filename:

```
goblin_cave.png
```

Store them by their cryptographic hash (for example, SHA-256):

```
sha256:8a7f...c91e
```

Then events reference the hash rather than the file itself. When syncing, peers ask, "Do you already have asset `8a7f...c91e`?" If yes, nothing is transferred. If no, they download it from another peer or the node. This avoids duplicate uploads, makes synchronization much more efficient, and provides built-in integrity checking because the hash verifies the file wasn't corrupted or altered during transfer.

Looking over everything we've discussed, I think the core philosophy can be summarized in one sentence:

> **Build a collaborative distributed system for tabletop RPGs, where every participant owns a complete copy of the campaign, the DM authoritatively advances the shared world through immutable events, and an optional node improves availability without becoming the owner of the campaign.**

That's a fairly unique design compared to most existing virtual tabletops, which are typically built around a central server or a single host machine.
