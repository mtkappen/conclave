---
description: LLM guide for git
---

# Git Workflow Rules for This Project

## ✅ Git IS Available

**This project uses Git for version control.** Every LLM, developer, or contributor working on this codebase MUST use Git to track changes.

### Git Configuration (Already Set Up)
- **User Name:** `mtkappen`
- **Email:** `mtkappen@gmail.com`
- **Repository Location:** Root of this project directory

---

## 📋 Rules for All Code Changes

### 1. ALWAYS Use Git for Modifications
Every time you make code changes, you MUST:
1. Stage the changes with `git add .` (or specific files)
2. Commit with a descriptive message: `git commit -m "Your clear description"`
3. Push to remote if applicable: `git push`

### 2. Commit Before Major Changes
Before starting significant work, ensure you're on an up-to-date branch and consider creating a feature branch for larger changes.

### 3. Write Meaningful Commit Messages
- ✅ Good: "Add character inventory management feature"
- ❌ Bad: "fix stuff" or "update code"

### 4. Check Git Status Regularly
Before making changes, run `git status` to understand the current state of the repository.

### 5. Review Changes Before Committing
Use `git diff` to review what you're about to commit.

---

## 🔄 Standard Workflow for LLMs/Developers

```powershell
# 1. Check current status
git status

# 2. Make your code changes (using edit tools, not manual file edits)

# 3. Stage all modified files
git add .

# 4. Review what will be committed
git diff --cached

# 5. Commit with a descriptive message
git commit -m "Add/fix/update: [clear description of change]"

# 6. Push to remote (if configured)
git push
```

---

## 🚫 What NOT To Do

- **DO NOT** make code changes without committing them
- **DO NOT** ignore Git when working on this project
- **DO NOT** commit database files, virtual environments, or IDE settings (`.gitignore` handles this)
- **DO NOT** use vague commit messages like "update" or "fix"

---

## 📁 What's Already Ignored (.gitignore)

The following are excluded from version control:
- Python cache (`__pycache__/`, `*.pyc`)
- Virtual environment (`venv/`)
- Database files (`*.sqlite3`, `*.db`)
- IDE settings (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`, `Thumbs.db`)
- Environment variables (`.env`)

---

## 🛠️ Available Git Commands

| Command | Purpose |
|---------|---------|
| `git status` | Check working directory state |
| `git add .` | Stage all changes |
| `git commit -m "msg"` | Commit staged changes |
| `git log` | View commit history |
| `git diff` | See unstaged changes |
| `git push` | Upload to remote repository |
| `git pull` | Download from remote repository |

---

## 📝 For Future LLM Sessions

When you start working on this project:
1. **Verify Git is available:** Run `git --version`
2. **Check current branch:** Run `git branch`
3. **Review recent commits:** Run `git log --oneline -5`
4. **Always commit your changes** before ending a session

---

## 🎯 Commit Message Format

Use this format for consistency:
```
<type>: <description>

Examples:
- feat: Add new character creation form
- fix: Resolve login validation error
- docs: Update README with setup instructions
- refactor: Simplify campaign view logic
- test: Add unit tests for inventory model
```

---

**Remember:** Git is your friend. Every change should be tracked, reviewed, and committed properly. This ensures project history is preserved and changes are reversible if needed.
