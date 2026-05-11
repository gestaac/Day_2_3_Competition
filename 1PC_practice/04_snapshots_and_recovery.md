# VMware Snapshots — Use Them Aggressively Tonight

> The single biggest productivity tool for practice. A snapshot saves the entire VM state (RAM, disk, settings). You can roll back in 10 seconds. Without snapshots, one bad GPO can cost you 30 minutes.

## Take a snapshot

1. Power state doesn't matter, but **powered-off snapshots are smaller**. Prefer to snapshot after a clean shutdown.
2. In VMware Workstation, click the VM tab → top menu **VM** → **Snapshot** → **Take Snapshot…**
3. Give it a clear name. Suggested names per practice stage:

| When | Snapshot name |
|------|---------------|
| Just after OS install, before any config | `01-fresh-install` |
| After base IP + hostname set | `02-network-set` |
| After domain join (Win/Linux) | `03-joined` |
| After main config task done | `04-configured` |
| Before doing something you're not sure about | `experiment-NN` |

4. Optionally tick **Snapshot the virtual machine's memory** — useful if you want to resume mid-task without booting. Bigger snapshot though.
5. **Take Snapshot**. The status bar at the bottom shows progress.

## Revert to a snapshot (the "oh no" button)

1. **VM** menu → **Snapshot** → **Snapshot Manager…**
2. The tree shows all snapshots. Click the one you want to go back to.
3. Click **Go To** at the bottom-right → confirm.
4. The VM reverts in 5–15 seconds. Power state matches what you snapshotted.

## Why this is useful for practice

Example session flow:
1. Power on pfSense → snapshot `01-fresh-install`.
2. Do all of Section 4 (firewall rules). Notice you accidentally allowed `any any` somewhere. Decide to redo.
3. Snapshot Manager → click `01-fresh-install` → Go To. 15 seconds later you're back to a blank firewall.
4. Redo Section 4 — this time correctly.
5. Snapshot `02-firewall-clean`.
6. Move on to Section 8 (OpenVPN). Wizard fails. Try to fix; mess it up more.
7. Snapshot Manager → revert to `02-firewall-clean`.
8. Try OpenVPN wizard again from scratch.

Each revert costs 15 seconds. Without snapshots each fix would be 10–30 minutes.

## Snapshot housekeeping

- After a successful practice run, **delete the experiment snapshots** to save disk space (Snapshot Manager → click → Delete). The base ones (`01-fresh-install`, `04-configured`) you keep.
- Each snapshot consumes disk equal to the changes since the previous one — usually a few hundred MB to a few GB. If your disk is filling up, delete intermediates.
- **Don't keep more than 5 snapshots per VM**. Performance degrades with long snapshot chains.

## Linked clones — the second power tool

If you've built a WINSRV1 and want to also practice on a fresh WINSRV3 without installing again:

1. Power off WINSRV1 → take snapshot `dc-base` if you don't have one.
2. Right-click WINSRV1 in left pane → **Manage** → **Clone…**
3. Source: **Existing snapshot** → pick `dc-base` → Next.
4. **Linked clone** (saves disk space — only changes are stored). Next.
5. Name `WINSRV3-clone` → Finish.
6. Boot the clone. Change hostname to WINSRV3 and IP to 192.168.2.30. Same domain join steps.

Total time: 5 min vs 40 min for a fresh install.

> Linked clones DEPEND on the original. Don't delete WINSRV1 or your linked WINSRV3 breaks.

## Snapshot quick reference

| Action | Steps |
|--------|-------|
| Take snapshot | VM menu → Snapshot → Take Snapshot |
| Revert to last | VM menu → Snapshot → Revert to Snapshot (jumps to the most recent) |
| Manage all | VM menu → Snapshot → Snapshot Manager |
| Delete (free space) | Snapshot Manager → select → Delete |
| Clone from snapshot | Right-click VM → Manage → Clone |

## Don't snapshot during real competition

Tomorrow's competition VMs live on ESXi, not Workstation. ESXi has snapshots too but they're slower and the venue may have disabled them or have policies about them. **Only use snapshots tonight on your practice setup**, not tomorrow on the competition VMs.

If you want a safety net tomorrow, use the **pfSense built-in backup** (Diagnostics → Backup & Restore → Backup) and `Backup-GPO` PowerShell on WINSRV1. Those are file-based exports the venue won't restrict.
