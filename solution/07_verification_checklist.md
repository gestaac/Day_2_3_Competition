# End-to-End Verification — run in this order tomorrow before raising your hand

> Aim to make every line in **PASS** state. Each row maps to a marking-sheet aspect (column noted).

## Block 1 — pfSense base (A2: 0.25 + 0.25 + 0.6 + 0.4 + 0.1 + 0.4 + 0.4 marks)

| # | From | Command / Action | PASS criteria |
|---|------|------------------|---------------|
| 1.1 | Client1 browser | `https://172.16.100.254` | Login `admin` / `P@ssw0rd` succeeds |
| 1.2 | Client1 CMD | `ipconfig /release && ipconfig /renew && ipconfig /all` | IP `172.16.100.x`, DNS `192.168.2.10`, domain `manila.com`, gateway `172.16.100.254` |
| 1.3 | Client1 browser | `https://www.nationalmuseum.gov.ph` | Loads (self-signed warning OK) |
| 1.4 | Client1 browser | `https://www.starcity.com.ph` | **Blocked** by firewall |
| 1.5 | pfSense GUI | Firewall → Rules → each tab | No "any any" allows, block-starcity rule is **above** allow-internet rule |

## Block 2 — VPN + Snort (A2: 1.0 + 0.7 + 0.4 marks)

| # | From | Command / Action | PASS criteria |
|---|------|------------------|---------------|
| 2.1 | Client3 | Connect OpenVPN with profile, user `VPNUser` / `P@ssw0rd` | Tunnel "Connected" |
| 2.2 | Client3 CMD | `ping 192.168.2.10` | Replies (routes via tunnel) |
| 2.3 | Client3 browser | `https://www.manila.com` | Loads (cert warning OK if self-signed) |
| 2.4 | Client3 CMD | `nmap -sF -p 1-1024 <pfSense WAN IP>` then `nmap -sX -p 1-1024 <pfSense WAN IP>` (XMAS scan — marking sheet mentions "Xmas tree scan") | Snort Alerts tab on pfSense shows `sid 100001` firing |
| 2.5 | Client3 browser | `https://www.starcity.com.ph` (via VPN) | Blocked |

## Block 3 — LINSRV1 / DMZ Linux (A3: 0.25 + 0.25 + 0.25 + 0.25 + 0.4 + 0.75 + 0.25 + 0.25 + 0.4 + 0.25 + 0.4 + 0.4 marks)

| # | From | Command / Action | PASS criteria |
|---|------|------------------|---------------|
| 3.1 | WINSRV1 ADUC | View `Computers` container | `LINSRV1` computer account present |
| 3.2 | WINSRV1 DNS | manila.com zone | `linsrv1` A record `192.168.1.10` |
| 3.3 | LINSRV1 | `realm list` | Shows `manila.com` joined |
| 3.4 | LINSRV1 | `grep -E "^(Port|PermitRootLogin|AllowUsers|MaxAuth)" /etc/ssh/sshd_config` | Port 2022, PermitRootLogin no, AllowUsers C1 C2, MaxAuthTries 3 |
| 3.5 | Client1 PuTTY | `C1@192.168.1.10` port 2022 | Logs in. Try `ssh root@192.168.1.10 -p 2022` → **denied** |
| 3.6 | LINSRV1 (as C1) | `sudo useradd fred` | Succeeds (asks for password) |
| 3.7 | LINSRV1 (as M001 if you can ssh, otherwise skip) | `sudo useradd bar` | **Denied** (not in IT group) |
| 3.8 | LINSRV1 | `systemctl status firewalld` | active (running) |
| 3.9 | LINSRV1 | `firewall-cmd --list-all --permanent` | Services include `http https kerberos`, port `2022/tcp`; **no** `ssh` (port 22) |
| 3.10 | LINSRV1 | `sestatus` | enforcing, policy `targeted` |
| 3.11 | LINSRV1 | `ls -Z /var/www/manila` | `httpd_sys_content_t` |
| 3.12 | LINSRV1 | `useradd bob; echo "password" \| passwd --stdin bob` | **Rejected** (too short / no complexity) |
| 3.13 | LINSRV1 | `passwd bob` → `P@ssw0rd12` | Accepted. `chage -l bob` → max 30, warn 5 |
| 3.14 | Client1 Firefox | `https://www.manila.com` | Loads. **No cert warning** if PKI signed (else accept warning) |
| 3.15 | LINSRV1 | Open cert with `openssl s_client -connect www.manila.com:443 -showcerts </dev/null` | Chain shows WINSRV3 → WINSRV4 (if PKI-signed) |

## Block 4 — WINSRV1 (AD/GPO/Share) (A4: 0.6 + 0.25 + 0.25 + 1.0 + 0.7 marks)

| # | From | Command / Action | PASS criteria |
|---|------|------------------|---------------|
| 4.1 | WINSRV1 GPM | Browse domain root | GPOs visible: `lockout`, `Banner`, `restrict control panel`, `disabled add and remove program panel`, `autolock`, `certenroll` (and `Default Domain Policy`) |
| 4.2 | WINSRV1 ADAC | Domain → System → Password Settings Container | `ExecutivePSO` exists, applied to Executive, min length 16 |
| 4.3 | WINSRV1 ADUC | Properties of M004 | Logon works with `P@ssw0rdP@ssw0rd` |
| 4.4 | WINSRV1 | `Get-SmbShare pictures` | Path `C:\shares\pictures`, share perms `Executive=Full`, `Marketing=Read` |
| 4.5 | Client2 (as M001) | Run → `\\winsrv1\pictures\park.jpg` | Opens (read OK) |
| 4.6 | Client2 (as M004) | Right-click → can copy/edit | Full control (write succeeds) |
| 4.7 | Client2 (as M002) | Try open share | Access denied |
| 4.8 | WINSRV1 Event Viewer | Security log, after step 4.5 | Event ID 4663 with park.jpg + ReadData |

## Block 5 — WINSRV3 / Cert / Clients (A5, A6, A7: scattered marks)

| # | From | Command / Action | PASS criteria |
|---|------|------------------|---------------|
| 5.1 | WINSRV3 — Server Manager → Tools → **Certification Authority** → expand CA → **Issued Certificates** | (look at the list) | Web Server cert for `webtest.manila.com` listed |
| 5.2 | Client2 Chrome | `https://webtest.manila.com` | Loads. **No cert warning.** View cert → chain WINSRV3 → WINSRV4 |
| 5.3 | Client2 CMD | `ping www.manila.com` | Resolves to `192.168.1.10` |
| 5.4 | Client2 CMD | `gpresult /v | findstr /i certenroll` | `certenroll` policy applied |
| 5.5 | Client2 — Start → type **"Manage computer certificates"** → click result → expand **Personal → Certificates** | (look in the list) | A computer cert issued by `manila Issuing CA` (WINSRV3) is present |
| 5.6 | Client2 logon | At login screen | Banner title "WorldSkills ASEAN Manila", text "Authorized access only" |
| 5.7 | Client2 logon as M004 | Wait 10 sec idle | Screen locks (autolock GPO) |
| 5.8 | Client2 as M001 | Open Control Panel | **Blocked** by `restrict control panel` |
| 5.9 | Client2 as M004 | Open Control Panel | **Allowed** (Exec is denied the restrict GPO) |
| 5.10 | Client2 as any domain user | Open **Chrome** | Home page = `www.manila.com` (the `google` GPO worked) |
| 5.11 | Client2 Chrome | Settings → search "home" | Home page URL field is **greyed out** (locked) |
| 5.12 | Client2 CMD | `gpresult /r` | Output lists **Applied Group Policy Objects** including `google`, `certenroll`, `lockout`, `Banner`, `restrict control panel` |
| 5.13 | Client1 PuTTY | SSH as `M001@manila.com` → port 2022 to LINSRV1 | Denied (not in AllowUsers C1 C2) — **expected**, this is just to confirm SSH ACL |

## Block 6 — Submission

| # | Action | PASS |
|---|--------|------|
| 6.1 | Deliverable doc combined, on competitor laptop **Desktop** | Filename has your country code |
| 6.2 | Contains: exec summary (MA1), GPO recommendations table (3 GPOs) | All sections filled |
| 6.3 | Verbally tell experts where it is | Done before leaving room |

---

## Useful checks — pick GUI or commands

These all check the same thing — use whichever you're faster at.

### Client side (Client1 / Client2)

| Check | GUI way (clicks) | Command (CMD) |
|-------|------------------|---------------|
| IP / DNS / DHCP source | Click the network icon in system tray → click connection name → **Properties** → scroll to "Properties" panel at bottom | `ipconfig /all` |
| GPO applied? | Start → type `rsop.msc` (Resultant Set of Policy) → Enter → review tree | `gpresult /r` |
| Refresh policies | (no clean GUI — must use command) | `gpupdate /force` |
| Resolve a hostname | Start → type `cmd` → Enter (you're in CMD already) | `nslookup www.manila.com 192.168.2.10` |
| See applied banner | Just sign out — the banner appears on the logon screen before the password box | (none) |

### LINSRV1 (Linux server — terminal only, no desktop)

| Check | Command (the only way on RHEL/Rocky server) |
|-------|---------------------------------------------|
| Domain joined? | `realm list` |
| SELinux mode? | `sestatus` |
| Firewall allowed services? | `firewall-cmd --list-all --permanent` |
| Web server listening on 80/443? | `ss -tlnp \| grep -E ':(443\|80\|2022) '` |
| Recent SSH attempts? | `journalctl -u sshd --since "5 min ago"` |

> Linux servers don't ship with a desktop. Commands ARE the interface. The grader expects you to know these — they'll run the same commands during marking.

### WINSRV1 (Windows server — has GUI for everything)

| Check | GUI way (clicks) | PowerShell |
|-------|------------------|------------|
| List all GPOs | Server Manager → Tools → **Group Policy Management** → expand Forest → Domains → manila.com → **Group Policy Objects** → see all rows in right pane | `Get-GPO -All \| Select DisplayName` |
| Fine-grained password policy exists? | Server Manager → Tools → **Active Directory Administrative Center** → Tree View → manila (local) → System → **Password Settings Container** → row count >= 1 | `Get-ADFineGrainedPasswordPolicy -Filter *` |
| Share `pictures` exists with right perms? | Server Manager → **File and Storage Services** → **Shares** → click "pictures" → see Permissions in right pane | `Get-SmbShare pictures; Get-SmbShareAccess pictures` |
| Audit set on park.jpg? | File Explorer → right-click `C:\shares\pictures\park.jpg` → **Properties** → **Security** → **Advanced** → **Auditing** tab | `(Get-Acl C:\shares\pictures\park.jpg -Audit).Audit` |
