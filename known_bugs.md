# Known Bugs & Issues

## Chat Message Edit/Delete UI

- [ ] **Fix edit and delete boxes for chat messages** - The edit/delete buttons/boxes are not displaying correctly or are missing from the chat interface. Need to investigate why they're not showing up properly.

---

## Admin Secret Visibility in Normal Campaign Mode

- [ ] **Admin can see all secrets in normal campaign mode** - Currently, admins can view all campaign secrets (DM whispers, hidden dice rolls) when browsing campaigns normally at `/campaign/<pk>/`. They should only be able to see these secrets through the admin interface at `/admin/campaigns/` and selecting "View Secrets". This is a security/privacy issue that needs to be fixed.

---

## Secret Message Recipient Display

- [ ] **Show recipient in secret messages** - When viewing DM-only whispers or split-group messages, the recipient(s) should be displayed in *italics* next to the sender's name (e.g., "SenderName (*to: Player1, Player2*)"). Currently, this information is missing from the chat interface.

---

## Dashboard Campaign Text Color

- ✅ **Fixed**: Changed campaign title and "No Campaigns Yet" heading from red (#e94560) to white (#fff) on dashboard

---

## Status Legend
- ⬜ = Not Started / Open Bug
- ✅ = Fixed / Resolved
- 🔄 = In Progress
