# Practice Drills — What to Rehearse Tonight

> **Two modes** for this file:
> - **Curated mode** (4 hours): Scenarios A → D below — highest-mark, most-mistake-prone tasks only.
> - **Complete coverage mode** (8–10 hours): Add Scenario E at the bottom — every task in `solution/`.
>
> **Choose curated** if it's already evening. **Choose complete coverage** only if you have a full weekend day available. A tired competitor scores worse than a fresh one who didn't rehearse everything.

## The flow — how practice connects to the competition guides

After you've built VMs (file `02_VM_build_specs.md`), the practice **IS the competition**. You open `solution/00_RUN_ORDER.md` and follow it from the top. The only differences:

| Aspect | Competition | Practice (one PC) |
|--------|-------------|--------------------|
| VMs hosted on | ESXi at 192.168.1.1 | VMware Workstation on your PC |
| How you reach VMs | Workstation → Connect to Server → ESXi | Click the VM tab in Workstation |
| Teammate | PC1 (real person) | None — you do both tracks |
| Stakes | Marked | Snapshot-and-retry |
| Internet websites (nationalmuseum, starcity) | Provided by real ISP VM | Simulated via DNS Resolver on pfSense — see Scenario E5 below |

**Order to follow on this practice setup:**
1. Build VMs (file `02_VM_build_specs.md`).
2. Power on what you need for the scenario.
3. Open `solution/00_RUN_ORDER.md` → start at Pre-flight → continue through each step.
4. Cherry-pick which scenario below applies based on which VMs you have running.

## Scenarios — pick based on your available RAM

If your free RAM is **less than 14 GB**, you can't run all VMs at once. Use these scenarios — each runs a subset, you snapshot at the end of one and shut down before the next.

---

## Scenario A — pfSense fluency (45–60 min) — **highest priority**

**RAM needed:** ~5 GB. **VMs on:** pfSense + Client1.

**Why this scenario first:** pfSense is the biggest single block of points (~7 marks), and it's the most click-heavy. The faster you navigate its menus, the less time you waste tomorrow.

### Drill A1 — base config (15 min)
Open `solution/02_pfsense_checklist.md`. Do sections 1–5 (admin pwd, DHCP, aliases, firewall rules, NAT). From Client1 verify: get DHCP, browse to `https://172.16.100.254` admin panel.

**Goal:** do all 5 sections in under 15 minutes by the end of your second practice run. Time yourself.

### Drill A2 — Snort + the FIN/XMAS rule (15 min)
Same file, sections 9.1 through 9.7. **The actual rule paste is one text field — practice navigating to it.**

**Goal:** find the rule text area without looking at the guide. The path is `Services → Snort → Snort Interfaces → pencil ✏ → WAN Rules tab → Category dropdown → custom.rules → text area`. Memorize this.

### Drill A3 — OpenVPN wizard (20 min — hardest)
Same file, section 8. Pre-req: you need at least the `Administrator` user reachable on WINSRV1 for LDAP — if WINSRV1 isn't built yet, skip the LDAP step and use Local Database for now (Wizard → "Local User Access" instead of LDAP).

**Goal:** export a client `.ovpn` file successfully, even if you can't fully connect. The export step trips up beginners.

### End of Scenario A
Take a snapshot of pfSense called `pfSense-base-configured`. Shut down pfSense and Client1.

---

## Scenario B — LINSRV1 fluency (60 min) — **second priority**

**RAM needed:** ~3 GB. **VMs on:** LINSRV1 + pfSense (just for the gateway).

**Why this scenario is critical:** Linux terminal commands are the area where beginners burn the most time. You can't bluff your way through `realm join` failures with clicks.

### Drill B1 — terminal warm-up (10 min)
Log in as root. Type these from memory (don't paste):

```bash
ip a                          # see your IP
hostnamectl                   # check hostname
systemctl status firewalld    # service status
sestatus                      # SELinux status
```

If any of those don't roll off your fingers, drill them 3x. They'll be your verification commands at the venue.

### Drill B2 — realm join (20 min — hardest single step)
Open `solution/05_linsrv1_setup.md` Step 1–3. Type each command (don't paste). The flow:
1. Configure DNS to point at WINSRV1 (or any DNS that resolves manila.com — see fallback below).
2. Install realmd + sssd stack.
3. `realm join -U Administrator manila.com`.
4. Verify with `realm list`.

**If WINSRV1 isn't built yet for practice**, you can still drill realm-join syntax against a different domain — even a fake one will let you see the typical error messages. Or skip to Drill B3.

**If realm join fails:** practice the fallback from `solution/05_linsrv1_setup.md` — create local C1/C2 users. This is worth doing once even if domain works tomorrow.

### Drill B3 — SSH hardening + firewalld + SELinux (15 min)
Steps 5–9 of the LINSRV1 guide. Drill the `sed`, `firewall-cmd`, `setenforce` commands.

**Goal:** when you finish, `grep -E "^(Port|Permit|Allow|MaxAuth)" /etc/ssh/sshd_config` outputs the four expected lines.

### Drill B4 — httpd vhost + PAM (15 min)
Step 8. Practice creating `/etc/httpd/conf.d/manila.conf` (use `nano` or `vi`). Make a typo on purpose, restart httpd, see how `journalctl -u httpd` shows the syntax error. **Knowing how to read Apache error logs** is more useful than getting it right the first time.

### End of Scenario B
Snapshot named `LINSRV1-configured`. Shut down.

---

## Scenario C — WINSRV1 AD/GPO clicks (60 min)

**RAM needed:** ~4 GB. **VMs on:** WINSRV1 + Client1.

Skip this scenario tonight if you didn't build WINSRV1 — just read the guide. The clicks are simple but numerous.

### Drill C1 — create the test users (10 min)
Use `solution/04_winsrv1_create_users.md` GUI path (Active Directory Users and Computers): create just **M001** (Marketing) and **M004** (Executive). Don't waste time creating all 8 users for practice — you only need to verify the share permissions and PSO work.

### Drill C2 — three GPOs and link them (20 min)
From `solution/03_winsrv1_gpo_setup.md`, do these three (pick the ones you can finish in 20 min):
- Task 3 `lockout` (account lockout)
- Task 4 `Banner` (logon message)
- Task 5 `restrict control panel`

After each: on Client1 run `gpupdate /force`, sign out, sign back in as M001 — verify the GPO took effect.

### Drill C3 — share + audit (15 min)
Task 9 + Task 10 — create the share, set NTFS + share perms, add auditing on `park.jpg`. On Client1 as M001 open `\\winsrv1\pictures\park.jpg`. Check Event Viewer on WINSRV1 for 4663.

### Drill C4 — the `google` GPO (15 min — easy to forget)
Task 8B. **This is the GPO the PDF doesn't mention but the marking sheet tests.** Practice Option B (registry-based) because it works even without Chrome ADMX templates.

### End of Scenario C
Snapshot `WINSRV1-GPO-practiced`. Shut down.

---

## Scenario D — End-to-end with everything on (only if RAM ≥ 14 GB)

**VMs on:** pfSense + WINSRV1 + LINSRV1 + Client1.

Walk through `solution/07_verification_checklist.md` Blocks 1, 3, 4 — confirm everything actually works together. This is the closest you'll get to a "dress rehearsal" tonight.

If something fails: **don't fix it.** Note what failed, snapshot the state for tomorrow morning analysis, move on.

---

## What to skip in curated mode (don't get sucked in)

| Task | Why skip (in curated mode) | Where to do it if you want complete coverage |
|------|---------------------------|-----------------------------------------------|
| Full Windows Server install from ISO | 40 min of waiting per server | Scenario E1 |
| Full Windows 10 install from ISO | Same — 30 min wait per client | Scenario E1 |
| WINSRV3 AD CS subordinate CA setup | Complex; pre-built at venue | Scenario E2 |
| ISP VM simulation | Pre-built at venue | Scenario E5 (DNS-only shortcut, no full ISP VM needed) |
| Client2 build | Identical to Client1 | Scenario E3 (linked clone, 5 min) |
| Building WINSRV4 (offline root) | Always offline at venue | Skip even in complete mode — zero practice value |

---

# Scenario E — Complete coverage practice (only if you have time)

> Only attempt this if you've finished A–D and have **at least 4 more hours** plus 24 GB+ RAM. Otherwise stay with curated mode.

## E1 — Build the missing Windows VMs (~80 min total wait, mostly background)

If you skipped them in `02_VM_build_specs.md`:

1. **Windows Server 2022 → WINSRV1** — follow `02_VM_build_specs.md` VM 3, then `solution/01_install_guides.md` Section 5. Promote to DC for `manila.com`. ~40 min including AD DS promote and reboot.
2. **Windows 10 → Client1** — follow `02_VM_build_specs.md` VM 4. Domain join to manila.com. ~30 min.

> While waiting for Windows installers to finish, **read** `solution/03_winsrv1_gpo_setup.md` end to end. Doing both at once = good time use.

3. Snapshot each after first successful boot.

## E2 — WINSRV3 as a Subordinate CA (~45 min)

For practice purposes you can do a **simplified one-tier CA** (WINSRV3 itself is Enterprise Root, not Subordinate). The grader test ("cert chain from WINSRV3 to WINSRV4") will fail this differently — but you still practice the IIS + cert + GPO autoenroll flow, which is the bulk of the marks.

1. Right-click WINSRV1 in Workstation left pane → **Manage → Clone…** → **Linked clone** from a clean snapshot → name `WINSRV3-PRACTICE`. Takes ~3 min.
2. Boot the clone. **Important first step:** because it was cloned from a domain controller, it still thinks it's the DC. You must remove it from the domain:
   - As Administrator: open **Server Manager → Tools → Active Directory Users and Computers** — this fails (it's a clone of a DC, sysprep wasn't run). 
   - Simpler approach: **destroy and rebuild** — actually, **don't clone a DC**. Skip and use a fresh Windows Server 2022 install for WINSRV3:
3. **Better path:** new VM from ISO (~30 min). Name WINSRV3, IP 192.168.2.30, DNS 192.168.2.10. Join to manila.com (Server Manager → Local Server → click "Workgroup" value → Domain → manila.com → Administrator/P@ssw0rd → restart).
4. After domain join, follow `solution/06_winsrv3_iis_cert.md` from the top:
   - Section 1: install IIS.
   - Section 2: create site folder + index.html.
   - Section 3: request the Web Server cert. **For practice**: if "Web Server" template doesn't appear, install **Active Directory Certificate Services** role first on WINSRV3 → configure as **Enterprise Root CA** (instead of Subordinate, since we don't have WINSRV4). Then the WebServer template publishes itself.
   - Sections 4–6: bind IIS, DNS record, test from Client1.

## E3 — Client2 via linked clone (~10 min)

1. Power off Client1 → right-click → **Manage → Clone…** → Linked clone → `Client2-PRACTICE`.
2. Power on Client2. Rename to CLIENT2 (Settings → System → About → Rename). Restart.
3. Re-join domain (it'll say "already joined" but the SID is duplicated — actually you'd need to leave and rejoin to get a clean computer account). For practice, leave domain → workgroup → re-join → restart.
4. Snapshot `Client2-ready`.
5. Now follow `solution/07_verification_checklist.md` **Block 4** (share access, audit log) on Client2 instead of just Client1.

## E4 — Drill the remaining tasks you skipped

With all VMs running, you can now do **every task** in `solution/`:

| Task you skipped in curated mode | File to follow |
|----------------------------------|----------------|
| Create all 8 AD users (M001–M004, S001, C1, C2, VPNUser) | `solution/04_winsrv1_create_users.md` Steps 4 (full block) |
| All 6+1 GPOs (you only did 3 in C2) | `solution/03_winsrv1_gpo_setup.md` Tasks 1–10 (full) |
| Fine-grained Password Policy + change M004 to `P@ssw0rdP@ssw0rd` | Task 2 |
| GPO `disabled add and remove program panel` (Executive only) | Task 6 |
| GPO `autolock` (Executive only) | Task 7 |
| GPO `certenroll` | Task 8 |
| GPO `google` (Chrome home page) | Task 8B |
| OpenVPN end-to-end including LDAP bind to WINSRV1 | `solution/02_pfsense_checklist.md` Section 8 |
| Client3 VPN connection + nmap FIN/XMAS scan | `solution/02_pfsense_checklist.md` end + `solution/07_verification_checklist.md` Block 2 |
| WINSRV3 IIS + cert chain test from Client2 | `solution/07_verification_checklist.md` Block 5 |
| Audit on park.jpg, confirm Event ID 4663 | Task 10 + `solution/07_verification_checklist.md` Block 4 |
| LINSRV1 PKI cert from CA (replacing self-signed) | `solution/05_linsrv1_setup.md` Step 10 |

## E5 — Simulate the ISP without building an ISP VM

The PDF's "ISP" VM provides DNS for `www.nationalmuseum.gov.ph` and `www.starcity.com.ph` plus hosts those websites. For practice you don't need a real ISP — just trick pfSense's DNS to point those names at something reachable.

1. In pfSense web UI → **Services → DNS Resolver** → scroll down to **Host Overrides** → click **+ Add**:
   - Host: `www`
   - Domain: `nationalmuseum.gov.ph`
   - IP: `192.168.1.10` (your LINSRV1 — we'll piggy-back its web server)
   - Description: `practice ISP nationalmuseum`
   - Save → Apply.
2. Same again for `www.starcity.com.ph` → IP `192.168.1.10` → Save → Apply.
3. From Client1 verify: `nslookup www.nationalmuseum.gov.ph` → should resolve to 192.168.1.10.
4. Now you can practice firewall rules for "allow nationalmuseum, block starcity" — the **block rule** is what's tested by the marker, and that works perfectly because pfSense intercepts the DNS+traffic regardless of whether the destination really exists.

> This is a hack — but it's enough to verify the firewall rule behavior. At the venue tomorrow the real ISP VM is provided, so no shortcut needed.

## E6 — Full end-to-end run

With every VM up and configured, walk through **all 60 rows** of `solution/07_verification_checklist.md`. Time how long it takes. If you can complete it in under 90 minutes, you're tomorrow-ready.

---

## When to stop and sleep

If it's past midnight and you haven't finished Scenario A, **stop and sleep**. You will lose more marks tomorrow from fatigue than from one less practice run.

If you're attempting Scenario E and the time is getting tight, **drop back to curated mode** — finish A, B, D and skip the rest.

## Final 15 minutes before bed

Open `solution/09_quick_reference_CHEATSHEET.md` and read it once. That's the highest-value bedtime content — it's what you'll mentally fall back on tomorrow when stressed.
