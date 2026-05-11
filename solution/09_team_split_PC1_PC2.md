# Team Split — PC1 (teammate) + PC2 (you) + PC3 (ESXi)

## Your physical setup

```
   ┌─────────────────┐         ┌─────────────────┐
   │   PC1 laptop    │         │   PC2 laptop    │
   │  (teammate)     │         │  (you)          │
   │ competitor1a    │         │ competitor1b    │
   └────────┬────────┘         └────────┬────────┘
            │                           │
            └──────────┬────────────────┘
                       │ (LAN)
                       ▼
              ┌─────────────────┐
              │  PC3 — ESXi     │
              │  192.168.1.1    │
              │  user: wsauser  │
              │  pass: Andres@9V4│
              │                 │
              │  Hosts ALL VMs: │
              │  WINSRV1/3/4    │
              │  LINSRV1        │
              │  pfSense        │
              │  Client1/2/3    │
              │  ISP            │
              └─────────────────┘
```

**Key fact:** Both of you share the same VMs. You don't each have your own WINSRV1 — there's one WINSRV1 and both of you can connect to its console.

## How to connect to a VM from your laptop

Both you and your teammate do the same thing:

1. On your laptop (PC1 or PC2), open **VMware Workstation Pro** (already installed).
2. File menu → **Connect to Server…**
3. Server: `192.168.1.1` — User: `wsauser` — Password: `Andres@9V4` → **Connect**.
4. In the left pane you'll see the ESXi host with all VMs listed beneath it. Double-click any VM name to open its console in a new tab.
5. Power on the VM (if not already on) with the green ▶ button.

> Both PC1 and PC2 can have the **same VM** open at the same time. ESXi will show "Console already connected" but lets you take it. If both teammates type at the same console, one of you will frustrate the other — only one person should be actively driving each VM.

---

## Suggested division of work

> Goal: maximise parallel progress without stepping on each other. The split below comes from the dependency graph: pfSense needs AD, LINSRV1 needs both, so AD-side and network-side can run mostly in parallel, then meet.

### PC1 (Teammate) — "Windows track"
Handles everything **inside the Servers VLAN** and the LAN client side.

| Order | File | What |
|-------|------|------|
| 1 | `03_winsrv1_create_users.md` | Create AD users/groups (only if missing) |
| 2 | `02_winsrv1_gpo_setup.md` | All 6 GPOs + PSO + share + audit |
| 3 | `05_winsrv3_iis_cert.md` | WINSRV3 IIS site + cert + DNS record |
| 4 | `06_verification_checklist.md` **Blocks 4 & 5** | Verify on Client2 (logon banner, autolock, share access, cert) |

### PC2 (You) — "Network + DMZ track"
Handles **pfSense and Linux** plus external client.

| Order | File | What |
|-------|------|------|
| 1 | `01_pfsense_checklist.md` **Sections 1–6** | Admin password, DHCP, base firewall rules, NAT, install packages |
| 2 | `04_linsrv1_setup.md` | LINSRV1 full RHEL setup |
| 3 | `01_pfsense_checklist.md` **Sections 7–10** | OpenVPN (needs PC1's AD ready), Snort, starcity block |
| 4 | `06_verification_checklist.md` **Blocks 1, 2 & 3** | Verify on Client1 (firewall) + Client3 (VPN, nmap) + LINSRV1 |

### Joint at the end
| Order | File | What |
|-------|------|------|
| Last | `07_GPO_recommendations_submission.md` | One of you writes the .docx — decide who has better English/typing. The other keeps fixing remaining marks. |

---

## Sync points — wait for each other before crossing these lines

These are the **hand-off moments**. Stop and confirm with your teammate before continuing past each one.

### 🟢 Sync 1 — after ~20 min
**PC1 must have finished:** `03_winsrv1_create_users.md` (Executive, Marketing, IT, VPNGroup, VPNUser all exist).
**Why:** PC2 cannot configure pfSense OpenVPN LDAP until VPNUser exists. PC2 cannot let LINSRV1 join the domain in a useful way until the IT group exists for sudo.

> **PC2 keeps working on:** pfSense sections 1–5 (admin pwd, DHCP, base firewall rules, NAT, NO VPN/Snort yet) — none of those need AD.

### 🟢 Sync 2 — after ~45–60 min
**PC1 must have finished:** All 6 GPOs created + linked at domain root. The `certenroll` GPO especially.
**PC2 must have finished:** pfSense sections 1–5 (so the Servers↔DMZ AD ports are open).
**Why:** LINSRV1 `realm join` (PC2's track) needs Servers AD ports open AND AD up. WINSRV3 cert enrollment (PC1's track) needs `certenroll` for clients to trust it.

### 🟢 Sync 3 — after ~90 min
**PC1 must have finished:** WINSRV3 IIS up + DNS A record for `webtest.manila.com` on WINSRV1.
**PC2 must have finished:** LINSRV1 fully configured (realm joined, httpd HTTPS up).
**Why:** From here, both of you can start the verification block on Clients.

### 🟢 Sync 4 — final check
Walk through `06_verification_checklist.md` together. PC1 reads each row, PC2 performs the test on the relevant client/VM. Tick or fix.

---

## Rules to avoid stepping on each other

1. **Group Policy Management is the worst culprit.** If both PC1 and PC2 edit the same GPO in parallel, the last save wins and the other person's clicks are silently lost. **Only PC1 touches GPOs** — PC2 stays out of WINSRV1's GPMC.

2. **pfSense web UI is the second worst.** Two simultaneous logins can both "Apply changes" and stomp on each other. **Only PC2 touches the pfSense GUI.** If PC1 needs to verify a firewall rule, they should *look* via Client1's browser but not save anything.

3. **DNS edits on WINSRV1.** PC1 owns these (since they need to add the `webtest` A record for IIS anyway). PC2 just says "please also add `linsrv1` and `www.manila.com` A records pointing to 192.168.1.10" — PC1 adds them once.

4. **AD account password resets.** Don't both try to reset M004's password. PC1 does it once per `02_winsrv1_gpo_setup.md` Task 2.

5. **VM console sharing.** When you both have the same VM console open, the cursor fights. If you need to confirm something on PC1's VM, message your teammate first instead of grabbing the console.

6. **Save-the-work moment every 30 min.** On pfSense: **Diagnostics → Backup & Restore → Backup**. On Windows: `Backup-GPO -All -Path C:\GpoBackup` from PowerShell. If something corrupts, you can roll back without redoing 2 hours of work.

---

## What if your teammate finishes early / is stuck?

**Teammate finished their track:**
- They can pick up Block 4/5 of `06_verification_checklist.md` from your side, OR
- Start drafting the `07_GPO_recommendations_submission.md` document, OR
- Browse `08_quick_reference_CHEATSHEET.md` and double-check your config matches.

**Teammate is stuck:**
- Don't wait silently — say "I'm done with X, what do you need?"
- The fastest unblock is usually you re-reading the relevant `.md` file aloud while they click.
- If a step is hard-stuck for >10 minutes, **skip it** and note it on a piece of paper. Come back at the end. Marks for unfinished work = 0, but marks for finished neighbouring work still count.

---

## Communication tip

Use a piece of paper between your laptops as a shared status board:

```
PC1 (teammate)              PC2 (you)
────────────────             ────────────────
[X] Users created           [X] pfSense admin pwd
[X] GPO: lockout            [X] pfSense DHCP
[X] GPO: Banner             [X] LAN rules
[ ] GPO: autolock           [X] DMZ rules
[ ] Share+audit             [ ] OpenVPN (waits for AD)
[ ] WINSRV3 IIS             [ ] LINSRV1 join
```

Tick boxes as you finish each row. When your teammate looks over, they see exactly where you are. Saves a lot of "are you done with X yet?".

---

## At submission time

The submission file lives on **PC2's Desktop** (per PDF: "saved on the desktop of the competitor computer" — and your username on PC2 is `competitor1b`). 

1. Save final `.docx` named with your country code on `C:\Users\competitor1b\Desktop\`.
2. **Both** teammates verify the file exists and opens correctly.
3. **One** of you raises a hand and tells the expert "file is on PC2 desktop, named `<code>.docx`."
4. Do not log out of PC2 until the expert has confirmed they collected the file.
