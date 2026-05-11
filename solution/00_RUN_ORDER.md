# MA2 — Execution Runbook (do exactly in this order)

> **Hard rule:** never change a password that the project did not explicitly ask you to change. The graders log in as `Administrator` / `P@ssw0rd`, `root` / `P@ssw0rd`, and domain users with `P@ssw0rd`. Break that and you lose marks even on tasks you finished.

## Team setup — READ FIRST

You and your teammate share **one** set of VMs hosted on the ESXi server (PC3 — `192.168.1.1`):
- **PC1** = teammate
- **PC2** = you (`competitor1b`)
- **PC3** = ESXi server holding all the VMs and ISOs

Before you do anything else, open **`09_team_split_PC1_PC2.md`** and agree with your teammate on who does which track. It tells you:
- How to connect from your laptop to the VMs on PC3 (VMware Workstation → Connect to Server).
- Which files PC1 owns vs which files PC2 owns.
- The 4 sync points where you wait for each other.
- Which tools you must **never** use in parallel (GPO editor, pfSense web UI).

The order below is the **dependency** order — parallel work between PC1 and PC2 is encouraged within each step.

## Pre-flight (10 min)
1. Power on all VMs **except WINSRV4** (Offline Root CA — leave it off).
2. From **Client1** open a CMD: `ping 192.168.2.10`, `ping 192.168.1.10`, `ping 172.16.100.254`. All three must respond.
3. On **WINSRV1**, open **Server Manager → Tools menu → Active Directory Users and Computers**. Expand `manila.com` in the left tree. Verify users in Table 3 of the PDF (M001–M004, S001, C1, C2) exist. If missing, follow `03_winsrv1_create_users.md`.

## Order of operations (parallelisable but ordered for dependency)

| Step | Where | What | File |
|------|-------|------|------|
| 1 | WINSRV1 console | Create AD users/groups (only if missing), VPNGroup/VPNUser, password policies, GPOs, share, audit | `03_winsrv1_create_users.md` then `02_winsrv1_gpo_setup.md` |
| 2 | WINSRV3 console | Issue Web Server cert + bind IIS HTTPS for `webtest.manila.com` | `05_winsrv3_iis_cert.md` |
| 3 | pfSense WebGUI from Client1 | Admin pwd, DHCP, firewall rules, NAT, packages, OpenVPN, Snort, block starcity | `01_pfsense_checklist.md` |
| 4 | LINSRV1 console (or SSH) | Domain join, sudo, SSH hardening, firewalld, password policy, httpd HTTPS, SELinux | `04_linsrv1_setup.md` |
| 5 | Client3 | Install OpenVPN profile, connect, run nmap FIN scan | `01_pfsense_checklist.md` Phase 5 |
| 6 | Client1 / Client2 | Verify everything end-to-end | `06_verification_checklist.md` |
| 7 | Competitor laptop desktop | Save deliverable doc | `07_GPO_recommendations_submission.md` |

## Why this order
- WINSRV1 first → AD must exist before LINSRV1 can `realm join` and before pfSense OpenVPN can LDAP-bind.
- WINSRV3 cert issuance early → IIS site `webtest.manila.com` works for grader Client2 step.
- pfSense before LINSRV1 → LINSRV1 needs Servers-VLAN AD ports open through the firewall.
- LINSRV1 last on server side → web cert request to WINSRV3 needs everything else up.
- Clients last → pure verification.

## What to do if you fall behind
**Drop in this order (lowest marks first):**
1. Extra GPO recommendations doc — only worth 1–2 judgement marks.
2. Snort custom rule wording (just get it logging *anything*).
3. PKI-signed cert on LINSRV1 → self-signed is partial credit, accept the warning.
4. Fine-grained PSO for executives — small mark.

**Never skip these (highest marks):**
- pfSense base rules + DHCP + Snort enabled + OpenVPN works.
- LINSRV1 SSH on 2022, firewalld, SELinux enforcing.
- WINSRV1 password policy + lockout GPO + share with correct perms.
- `certenroll` GPO + clients getting cert without warning.

## Time budget (4h afternoon assumed)
| Phase | Budget | Hard cap |
|-------|--------|----------|
| Pre-flight | 10 min | 15 min |
| WINSRV1 GPO/share | 45 min | 60 min |
| WINSRV3 cert/IIS | 15 min | 25 min |
| pfSense | 60 min | 90 min |
| LINSRV1 | 45 min | 60 min |
| Client3 + verify | 30 min | 40 min |
| Submission doc | 15 min | 20 min |

If you blow past hard cap on any one, **move on** and come back if time allows.
