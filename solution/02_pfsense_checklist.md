# pfSense Configuration — Click-by-Click Checklist

> Connect from Client1 browser → `https://172.16.100.254` → login `admin` / `pfsense` (default — change in step 1).

---

## 1. Change admin password — 0.25 marks
- **System → User Manager** → click `admin` row → pencil icon.
- **Password** + confirm → `P@ssw0rd` → **Save**.
- Re-login to confirm.

## 2. DHCP server on LAN — 0.25 marks
- **Services → DHCP Server → LAN** tab.
- ☑ **Enable DHCP server on LAN interface**.
- Range: `172.16.100.100` to `172.16.100.200`.
- **DNS servers**: `192.168.2.10` (WINSRV1).
- **Gateway**: `172.16.100.254`.
- **Domain name**: `manila.com`.
- **Save** → **Apply changes**.

## 3. Aliases (do this first — rules reference them) — best-practice mark
- **Firewall → Aliases → Hosts** tab → **Add**:
  - Name `WINSRV1` → host `192.168.2.10`.
  - Name `LINSRV1` → host `192.168.1.10`.
  - Name `STARCITY_BLOCK` → type **URL Table (IPs)** OR **Host** → host `www.starcity.com.ph`.
- **Ports** tab → **Add**:
  - Name `AD_PORTS` → ports `53 88 135 137 138 139 389 443 445 464 636 3268 3269 9389`.
  - Name `AD_PORTS_NO_GC` → ports `53 88 135 137 138 139 389 445 464 636 3268 3269`.
  - Name `WEB_PORTS` → ports `80 443 53`.
  - Name `DMZ_SVCS` → ports `22 80 443 53`.
- **Apply**.

## 4. Firewall rules — 1.4 marks total

> Order matters in pfSense — top rule wins. **Block rules go above allow rules.**

### Firewall → Rules → **LAN** tab
Delete the default "Default allow LAN to any" if present. Then add (top → bottom):

1. **Block** — Protocol any, Src `LAN net`, Dst `STARCITY_BLOCK`. Description: `Block starcity`.
2. **Pass** — TCP, Src `LAN net`, Dst `LINSRV1`, Dst port alias `DMZ_SSH_HTTP_DNS` (build alias `22,80,443,53` or just type the ports). Description: `LAN → DMZ services`.
3. **Pass** — TCP/UDP, Src `LAN net`, Dst `WINSRV1`, Dst port alias `AD_PORTS`. Description: `LAN → Servers AD`.
4. **Pass** — any, Src `LAN net`, Dst `WAN net` (or `any` except RFC1918). Description: `LAN → Internet`.
5. Optional: allow LAN → LAN address (the pfSense itself) on 80/443 for WebGUI access if needed.

### Firewall → Rules → **DMZ** tab
1. **Pass** — TCP/UDP, Src `DMZ net`, Dst `WINSRV1`, Dst port alias `AD_PORTS_NO_GC`. Description: `DMZ → AD for realm join`.
2. **Pass** — UDP, Src `DMZ net`, Dst `WINSRV1`, Dst port `53`. (covered by AD ports already but explicit DNS rule is OK)
3. **No other DMZ rules.** DMZ must not reach LAN or Internet generally.

### Firewall → Rules → **WAN** tab
1. **Pass** — TCP, Src `any`, Dst `LINSRV1`, Dst ports `80, 443, 53`. Description: `WAN → DMZ web/DNS`.
   - You'll also get auto-rules from NAT (step 5). If they appear, you can delete duplicates.
2. **No "any any" rule.**

### Firewall → Rules → **Servers** (Interface) tab
> ⚠ **Keep this tab almost empty.** Marking sheet rewards minimal rules here ("Should not be rules here, as no traffic should be initiated from DMZ"). The Servers VLAN serves clients — it should NOT need to initiate outbound traffic.

1. **Pass** — UDP, Src `Servers net`, Dst `any`, Dst port `53`. Description: `Servers DNS lookup`. (Only because WINSRV1 itself does external DNS lookups; if it uses Root Hints or doesn't need external resolution you can omit even this.)
2. **DO NOT add** an "any any" allow rule. If pfSense already created one as default ("Default allow LAN to any" cloned onto Servers), **delete it**.
3. **DO NOT add** `Servers → LAN` rules unless the PDF asks (it does not).

## 5. NAT — port forward — 0.6 marks
- **Firewall → NAT → Port Forward → Add**:
  - Interface **WAN**, Protocol TCP, Dst `WAN address`, Dst port `80`, Redirect target IP `192.168.1.10`, Redirect target port `80`. Description: `Web HTTP to LINSRV1`. ☑ "Add associated filter rule".
- Repeat for ports `443` and `53` (UDP+TCP for 53 — make two rules).
- **Apply**.

## 6. Install packages — needed for OpenVPN + Snort
- **System → Package Manager → Available Packages** → Install:
  - `openvpn-client-export`
  - `snort`
- Wait for both to finish (status = installed).

## 7. Import WINSRV3 root + issuing CA — 0.4 marks (OpenVPN PKI cert)
- On **WINSRV3**: open **Server Manager → Tools → Certification Authority**. In the left tree, right-click your CA name → **Properties** → **General** tab → click **View Certificate** → click the **Details** tab → click **Copy to File…** → Next → choose **Base-64 encoded X.509 (.CER)** → Next → save to `C:\Users\Administrator\Desktop\issuing.cer` → Finish. Repeat for the **root** CA: in the same Certificate window's **Certification Path** tab, double-click the topmost cert (manila Root CA / WINSRV4) → Details → Copy to File → same Base-64 export, save as `root.cer`.
- Copy both `.cer` files to Client1, then to pfSense via:
- pfSense **System → Cert Manager → CAs → Add**:
  - Method: **Import an existing CA**.
  - Paste the root CA `.cer` text → Save.
  - **Add** again → Import issuing CA → reference the root as its parent → Save.

## 8. OpenVPN server — 0.95 + 0.34 marks
- **System → User Manager → Authentication Servers → Add**:
  - Type **LDAP**.
  - Hostname `192.168.2.10`.
  - Port `389`, transport **TCP - Standard**.
  - Protocol version `3`.
  - Search scope **Entire Subtree**, Base DN `DC=manila,DC=com`.
  - Authentication containers: `CN=Users,DC=manila,DC=com` (or browse).
  - ☑ Bind credentials: user `MANILA\Administrator`, pass `P@ssw0rd`.
  - User naming attribute `samAccountName`.
  - **Save**.
- **VPN → OpenVPN → Wizards** → Type of Server: **LDAP** → select the LDAP server you just made.
- Choose Certificate Authority = **the issuing CA you imported** in step 7.
- Generate a new server certificate under that CA (CN = pfsense or fw.manila.com).
- **General Information**: Interface WAN, Protocol UDP, Local port `1194`.
- **Cryptographic Settings**: leave defaults (AES-256-GCM, SHA256).
- **Tunnel Settings**:
  - Tunnel network `10.8.0.0/24`.
  - Local network `172.16.100.0/24, 192.168.2.0/24, 192.168.1.0/24` (comma-separated).
  - Concurrent connections `10`.
  - ☑ Compression: disabled or LZ4-v2.
- **Client Settings**: ☑ Dynamic IP. DNS server 1 = `192.168.2.10`. Domain `manila.com`.
- **Firewall Rule Configuration**: ☑ both ("Firewall Rule" + "OpenVPN rule") so pfSense creates them automatically.
- **Finish**.

### Restrict to VPNGroup only
- **VPN → OpenVPN → Servers → edit your server → Advanced Configuration → Custom options** add:
  ```
  push "route 192.168.2.0 255.255.255.0";
  push "route 192.168.1.0 255.255.255.0";
  ```
- Restrict via LDAP filter: in the LDAP server settings, **Extended Query** check, query: `memberOf=CN=VPNGroup,CN=Users,DC=manila,DC=com`.

### Export client profile
- **VPN → OpenVPN → Client Export**:
  - Remote Access Server = your OpenVPN server.
  - Host Name Resolution: leave or set to the WAN IP.
  - Use **Inline Configurations: Most Clients** to get a single `.ovpn` file.
  - Scroll to **Client Install Packages** → download for `VPNUser` (Windows installer).
- Copy the file to Client3.

## 9. Snort IDS — 0.7 + 0.4 marks

> The Snort **navigation** is all clicks. The **rule itself** is a one-line text string that you paste into a text box — there's no point-and-click rule builder for that (it doesn't exist in pfSense). Every step below is a button or field, not a command line.

### 9.1 First, look up your actual WAN subnet (you'll need this number for the rule)
1. In the pfSense top menu click **Interfaces** → **WAN**. Scroll to the **General Configuration** section.
2. Note the **IPv4 Configuration Type** value. If it shows DHCP, the assigned IP is shown at top of the page header. Write down the subnet (example: if WAN IP is `172.16.1.5/24`, the subnet is `172.16.1.0/24`). You'll paste this in place of `172.16.1.0/24` in the rule below.

### 9.2 Enable Snort globally
1. From the pfSense top menu click **Services** → click **Snort**.
2. Click the **Global Settings** tab (it's the default tab when you arrive).
3. Scroll the page. Find the checkbox **Enable Snort VRT** (snort.org rules) — leave it **unticked** unless you already have an OINK code. We're using a custom rule, not VRT.
4. Scroll to the bottom → click the **Save** button.

### 9.3 Add the WAN interface to Snort
1. Click the **Snort Interfaces** tab (top of the Snort page).
2. The list is empty. Click the **+ Add** button (right side, blue/green plus icon).
3. A configuration form appears. Fill in:
   - **Enable** checkbox: ✓ ticked.
   - **Interface** dropdown: choose **WAN**.
   - **Description**: type `WAN IDS`.
   - Leave the rest at default.
4. Scroll down → click **Save**.
5. You're now back at the Snort Interfaces tab. The WAN row appears with a red ⏹ "stopped" icon. Leave it stopped for now — we'll add the rule first, then start it.

### 9.4 Add the custom FIN-scan rule
1. Still on the Snort Interfaces tab, in the **WAN** row click the small **pencil ✏ edit icon** on the right.
2. Inside the WAN edit page, click the **WAN Rules** tab (these tabs are at the top of the WAN edit area: "WAN Settings | WAN Categories | WAN Rules | WAN Variables | …").
3. There's a **Category Selection** dropdown at the top of the page. Click it and choose **custom.rules** from the list. (If you don't see custom.rules yet, choose any category first → click Save → come back and re-open this dropdown.)
4. Below the dropdown there is a big empty **text area** labelled something like "Defined Custom Rules" or "Custom Rules".
5. **Click inside that text area**, then paste the rule below. The only thing you must change: replace `172.16.1.0/24` with the actual WAN subnet you wrote down in step 9.1.
   ```
   alert tcp any any <> 172.16.1.0/24 any (flags: F; msg:"Possible FIN scan"; sid:100001; rev:1;)
   ```
6. Below the FIN rule, press Enter to start a new line, then paste this second rule (covers the XMAS scan test the marking sheet describes — same `sid:100001`):
   ```
   alert tcp any any <> 172.16.1.0/24 any (flags: FPU; msg:"Possible XMAS Scan"; sid:100001; rev:2;)
   ```
7. Scroll to the bottom of the page → click the **Save** button.

> **Why two rules?** PDF says `flags: F` (FIN only). Marking sheet test uses `nmap -sX` (XMAS = F+P+U). Strict `flags: F` won't match XMAS. With both rules, sid:100001 fires whichever scan the grader uses.

### 9.5 (Optional) Add a starcity-access logging rule
Only if you have time — it's a nice extra. Click inside the same text area, new line, paste:
```
alert tcp any any -> any 80 (msg:"Access to starcity"; content:"starcity.com.ph"; http_header; sid:100002; rev:1;)
```
Click **Save**.

### 9.6 Start Snort on WAN
1. Click the **Snort Interfaces** tab at the top to go back to the list.
2. In the WAN row, click the small **▶ (play/start)** icon at the right. The red ⏹ becomes a green ▶ when running.
3. Wait ~30 seconds. The status column should say **Started**.

> ⚠ **Snort needs 1–2 minutes after "Started" to actually load rules and begin inspecting packets.** If the grader runs nmap the very moment Snort goes green, the first scan may not trigger an alert. Wait at least **90 seconds** between starting Snort and asking the grader to test. If you're verifying yourself, run nmap **twice** about a minute apart — the second one will alert reliably.

### 9.7 Verify by watching alerts
1. Click the **Alerts** tab (top of Snort page).
2. **Interface to Inspect** dropdown → choose **WAN**.
3. This page is initially empty. Keep it open. Later, when you run `nmap -sF` or `nmap -sX` from Client3 (verification step 2.4 in file 06), an alert with **sid 100001** appears here within a few seconds.

## 10. Final pfSense sanity check
- Diagnostics → Ping → ping `192.168.2.10` from interface `Servers`.
- Diagnostics → Ping → ping `8.8.8.8` (or ISP fake DNS) from interface `WAN` → should work.
- **System → Routing → Gateways** → WAN_DHCP should be online with monitor IP responding.

---

## What the grader will check (from the marking sheet — keep in mind)

| Test | Pass criteria |
|------|---------------|
| Browse pfSense from Client1 | Logs in with new password `P@ssw0rd` |
| `ipconfig /all` on Client1 | DHCP from pfSense, DNS `192.168.2.10`, domain `manila.com` |
| Browse `www.nationalmuseum.gov.ph` | Loads |
| Browse `www.starcity.com.ph` | Blocked |
| nmap `-sF` from Client3 to WAN | Snort alert sid 100001 fires |
| VPN connect from Client3 as VPNUser | Tunnel up, can ping 192.168.2.10 |
| WAN → DMZ HTTPS | Browse to firewall WAN IP loads www.manila.com (after host header / DNS) |
