# Character Sheet Redesign Plan

## Overview
Replace rigid D&D-only character system with fully configurable sheets supporting any TTRPG.

## Architecture

### New Models

#### 1. GameSystem
Predefined or custom game systems that define available field types and templates.
- name (e.g., "D&D 5e", "Pathfinder 2e", "World of Darkness")
- is_custom (boolean)
- attribute_template (JSON - predefined attributes)
- skill_template (JSON - predefined skills)
- created_by (User, null for system defaults)

#### 2. CampaignGameSettings
Links campaign to a game system with customizations.
- campaign (OneToOne to Campaign)
- game_system (ForeignKey to GameSystem)
- custom_attributes (JSON - overrides/additions)
- custom_skills (JSON - overrides/additions)
- rule_book_source (CharField - official rulebook selection or "custom")

#### 3. CharacterSheet (replaces Character)
Main character data with flexible structure.
- user, campaign
- name, class_name, level, avatar, description
- game_settings (ForeignKey to CampaignGameSettings)
- attributes (JSON - dynamic attribute values)
- skills (JSON - skill values/proficiencies)
- combat_stats (JSON - HP, AC, etc.)
- custom_fields (JSON - any additional fields)
- inventory (JSON or keep separate InventoryItem model)

#### 4. SpellBook (optional, for magic systems)
- character (ForeignKey to CharacterSheet)
- spell_slots (JSON - slots per level)
- known_spells (JSON - spell list with details)
- prepared_spells (JSON - currently prepared)

### Field Types Supported
1. **Number** - Integer/decimal values with min/max
2. **Text** - Single line text
3. **Long Text** - Multi-line descriptions
4. **Boolean** - Toggle/on-off
5. **Calculated** - Formula-based (e.g., `strength_modifier = (strength - 10) // 2`)
6. **List** - Repeating items (inventory, spells, features)

### Visibility Controls
- **Public**: All campaign members see
- **Player Only**: Owner sees full value, others see hidden/blank
- **DM Only**: Only DM sees (secret notes, hidden modifiers)

### Workflow

#### Campaign Creation (DM)
1. Select game system from presets OR create custom
2. Choose official rulebook (if available) or upload custom content
3. Configure which sections are visible/enabled
4. Set default visibility rules for fields

#### Character Creation (Player)
1. Fill in basic info (name, class, level)
2. Enter attribute values (or use auto-roll if system supports)
3. Fill skills based on chosen background/class
4. Add inventory, spells, custom fields as needed

#### Editing
- Players edit their own sheets
- DM can view/edit all characters in campaign
- Changes tracked with timestamps

## Implementation Phases

### Phase 1: Core Models & Migrations
- Create GameSystem model with default templates (D&D 5e, Pathfinder, WoD)
- Create CampaignGameSettings model
- Create CharacterSheet model (new, alongside old Character)
- Create migration to migrate existing Character data to CharacterSheet

### Phase 2: Forms & Views
- New character creation/edit forms (dynamic based on game system)
- Game system selection interface for DMs
- Rule book integration

### Phase 3: Templates
- Dynamic character sheet template rendering
- Edit forms with field-type-specific inputs
- Responsive layout for all sections

### Phase 4: Advanced Features
- Calculated fields support
- Spell tracking system
- Import/export character sheets
- Character sheet templates/sharing

## Default Game System Templates

### D&D 5e
**Attributes**: Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma
**Skills**: Acrobatics, Animal Handling, Arcana, Athletics, Deception, History, Insight, Intimidation, Investigation, Medicine, Nature, Perception, Performance, Persuasion, Religion, Sleight of Hand, Stealth, Survival
**Combat Stats**: HP, Max HP, AC, Initiative, Speed, Proficiency Bonus

### Pathfinder 2e
**Attributes**: Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma
**Skills**: Extensive list (Acrobatics, Arcana, Athletics, etc. - ~30+)
**Combat Stats**: HP, AC, TAC, Will DC, Reflex DC, Perception, Speed

### World of Darkness
**Attributes**: Mental (Intelligence, Wits, Presence), Physical (Strength, Dexterity, Stamina), Social (Charisma, Manipulation, Composure)
**Skills**: Talents, Skills, Knowledges (customizable)
**Combat Stats**: Health Levels, Willpower, Defense, Initiative

### Custom System
- DM defines all attributes, skills, and fields
- No restrictions on naming or structure

## Migration Strategy
1. Create new models alongside existing Character model
2. Write migration script to convert existing Character data:
   - Map fixed stats (strength, dexterity, etc.) to JSON attributes
   - Preserve inventory items
   - Link to default D&D 5e game system
3. Update all views/templates to use CharacterSheet
4. Deprecate old Character model (keep for backward compatibility initially)
