# Install / Rebuild Guides

> **When do you need this file?**
> - The PDF says VMs are pre-built ("VMs should all be preset"). In normal case you only configure, not install.
> - But you're uploading ISOs tonight, so the venue **might** ask you to build VMs from scratch.
> - Use this file as a backup if (a) a VM is missing tomorrow, (b) a VM won't boot, or (c) a tool inside a VM is missing (e.g. Snort package on pfSense).

---

## 0. Connect to ESXi from your laptop (you'll do this every time)

1. On PC2 (or PC1), find **VMware Workstation Pro** — usually a desktop icon. Double-click.
2. Top-left menu: **File** → **Connect to Server…**
3. Fill in:
   - **Server name:** `192.168.1.1`
   - **User name:** `wsauser`
   - **Password:** `Andres@9V4`
4. Click **Connect**. If you see a security/SSL warning, click **Connect Anyway**.
5. On the left pane, your ESXi host appears with VMs listed underneath. Double-click any VM name → console opens in a tab.
6. Power on with the green **▶ Play** button (top toolbar).

---

## 1. Quick "is a VM broken?" decision tree

```
VM listed in left pane?
├── No  → Section 4 (create new VM from ISO)
└── Yes
    │
    Powers on?
    ├── No   → Section 5 (troubleshoot)
    └── Yes
        │
        Boots to a login screen / web UI?
        ├── No   → likely OS install never finished → Section 4
        └── Yes
            │
            Has the right IP?
            ├── No   → my file 04/05/02 covers reconfiguring
            └── Yes  → use the matching configure guide (files 01-05)
```

**Rule of thumb:** If you'd need to spend more than 30 minutes installing a VM from scratch, skip that VM, do what you can on the others, and tell the expert you're working with limited resources. Marks for unfinished installs = 0; marks for nearby finished work still count.

---

## 2. pfSense 2.7 — package installs (HIGH likelihood needed)

> Even if pfSense itself is pre-built, **Snort** and **openvpn-client-export** may not be installed yet. The PDF says "packages have been pre-downloaded" which usually means the package files exist on the box but you still click to install them. Verify before configuring.

### Steps (in pfSense web UI — log in from Client1 browser at `https://172.16.100.254`)

1. Top menu → **System** → **Package Manager**.
2. Click the **Installed Packages** tab.
3. Look for `snort` and `openvpn-client-export` in the list.
   - If both are there with a green icon → skip the rest of this section.
   - If either is missing or shows as "available but not installed" → continue.
4. Click the **Available Packages** tab.
5. In the search box at top, type `snort`. Click **Search**.
6. Click the **+ Install** button at the right of the `snort` row.
7. Confirm by clicking **Confirm**. The install runs and shows a log — wait for "Success" at the bottom.
8. Go back to **Available Packages**. Search `openvpn-client`.
9. Click **+ Install** on `openvpn-client-export` → Confirm.
10. Go back to **Installed Packages** to confirm both are now green.

> **If the venue isolated pfSense from the internet** and "available packages" is empty: the pre-downloaded packages should be in `/root/` or `/conf/packages/` on pfSense itself. Open the **Diagnostics → Command Prompt** in the web UI and run `ls /root/*.txz` to find them. Then `pkg add /root/snort-VERSION.txz`. Ask an expert if you can't find the files — they'll point you to where they staged them.

---

## 3. pfSense 2.7 — full OS install from ISO (LOW likelihood needed)

Skip this section unless the firewall VM literally doesn't exist or refuses to boot.

### VM specs to create on ESXi
| Setting | Value |
|---------|-------|
| Guest OS | Other → FreeBSD 64-bit |
| vCPU | 1 |
| RAM | 1024 MB |
| Disk | 8 GB (thin provisioned is fine) |
| Network adapters | **4** — assign to WAN, LAN, DMZ, Servers port groups (one each) |
| CD/DVD | Point to your uploaded `pfSense-CE-2.7.2-RELEASE-amd64.iso`, ☑ Connect at power on |

### Install steps (text installer)

1. Power on the VM. It boots from ISO and shows the FreeBSD bootloader → wait 5 seconds, it auto-continues.
2. **Copyright and distribution notice** screen → press **Enter** to accept.
3. **Welcome** → highlight **Install** → press **Enter**.
4. **Keymap Selection** → **Continue with default keymap** → Enter.
5. **Partitioning** → **Auto (ZFS)** is fine → Enter. Accept the defaults on the next two screens (stripe, the only disk).
6. **Confirm to proceed?** → **Yes** → install runs ~3 minutes.
7. **Manual Configuration** prompt → **No** → Enter.
8. **Complete** → **Reboot** → Enter. Eject the ISO before it boots (Edit VM → CD/DVD → Disconnect).
9. After reboot, pfSense console menu appears.
10. **Assign Interfaces** prompt — press `1`:
    - "Should VLANs be set up now?" → `n`
    - "Enter the WAN interface name" → likely `vmx0` (whichever the venue's port group for WAN maps to — check via "Auto-detection" if unsure).
    - "Enter the LAN interface name" → e.g. `vmx1`
    - "Enter the OPT1 interface name" → e.g. `vmx2` (this will become DMZ)
    - "Enter the OPT2 interface name" → e.g. `vmx3` (this will become Servers)
    - Press Enter when done → confirm `y`.
11. Console comes back. Press `2` to set IPs:
    - LAN → static `172.16.100.254/24` → no upstream gateway → no DHCP yet → no.
    - OPT1 (DMZ) → static `192.168.1.254/24` → same.
    - OPT2 (Servers) → static `192.168.2.254/24` → same.
    - WAN → leave DHCP.
12. Open `https://172.16.100.254` from Client1 browser → continue with `02_pfsense_checklist.md`.

> If the WAN interface ends up swapped with another (very common), you can re-run **option 1 Assign Interfaces** at the console any time without reinstalling.

---

## 4. Rocky Linux 9 — install from ISO (only if LINSRV1 or ISP missing)

### VM specs
| Setting | Value |
|---------|-------|
| Guest OS | Linux → Red Hat Enterprise Linux 9 64-bit |
| vCPU | 2 |
| RAM | 2048 MB |
| Disk | 20 GB |
| Network adapter | 1, attached to **DMZ** port group (for LINSRV1) or **Internet** port group (for ISP) |
| CD/DVD | `Rocky-9.x-x86_64-dvd1.iso`, ☑ Connect at power on |

### Install (Anaconda installer — graphical)
1. Power on. From the boot menu pick **Install Rocky Linux 9** (top option) → Enter.
2. Language: English → **Continue**.
3. On the "Installation Summary" page click each item that has a yellow ⚠ icon to fill it in:
   - **Network & Host Name** → toggle ON the NIC → click **Configure** → **IPv4 Settings** tab → Method = **Manual** → Add:
     - Address `192.168.1.10`, Netmask `255.255.255.0`, Gateway `192.168.1.254`. DNS `192.168.2.10`. → Save.
     - Host name field at bottom-left → `linsrv1.manila.com` → Apply.
   - **Installation Destination** → tick the disk → **Done**. (Accept automatic partitioning.)
   - **Software Selection** → choose **Server** (no GUI). Required additional add-ons: tick **Network Servers**, **System Tools**.
   - **Root Password** → `P@ssw0rd` → tick "Allow root SSH login with password" → Done (Done twice if it complains about weak password).
   - **User Creation** → User name `competitor`, Full name `competitor`, password `P@ssw0rd`, ☑ Make this user administrator → Done.
4. Click **Begin Installation**. Wait ~10 minutes.
5. When done, click **Reboot System**. Eject ISO before it reboots.
6. After reboot, log in as root → continue with `05_linsrv1_setup.md`.

> For the **ISP** simulator VM: same install, but IP `198.51.100.1/24` (or whatever the venue's "Internet" subnet is — check with the expert). After install, install bind (`dnf -y install bind`) and configure DNS for `www.nationalmuseum.gov.ph` and `www.starcity.com.ph` plus a simple http server. **Usually the ISP VM is provided pre-built** — don't waste time building it unless absolutely necessary.

---

## 5. Windows Server 2022 — install from ISO (only if WINSRV1/3/4 missing)

> Rebuilding a DC from scratch is a 60+ minute job (install OS, install AD DS, promote, create users, install AD CS, etc.). **If you find a server VM completely missing, talk to the expert first** — they may have a backup. Don't burn 90 minutes on a rebuild during a 4-hour exam unless you have no choice.

### VM specs (per server)
| Setting | Value |
|---------|-------|
| Guest OS | Windows Server 2022 64-bit |
| vCPU | 2 |
| RAM | 4096 MB |
| Disk | 60 GB |
| Network adapter | 1, attached to **Servers** port group |
| CD/DVD | `WindowsServer2022.iso`, ☑ Connect at power on |

### Install steps
1. Power on → press any key when "Press any key to boot from CD" appears.
2. Language English → Next → **Install now**.
3. Pick edition: **Windows Server 2022 Standard (Desktop Experience)** — Next → accept license → Next.
4. **Custom: Install Windows only** → pick the disk → Next. Wait ~15 minutes.
5. Reboot. Set Administrator password to `P@ssw0rd` → Finish.
6. After login: **Server Manager** opens automatically.
7. Click **Local Server** in the left pane. On the right, click the **Computer name** value to rename → Change → set:
   - WINSRV1: `WINSRV1`
   - WINSRV3: `WINSRV3`
   - WINSRV4: `WINSRV4`
8. Set static IP:
   - Click **Ethernet** value → right-click adapter → Properties → IPv4 → use:
     - WINSRV1: `192.168.2.10 / 255.255.255.0 / 192.168.2.254`, DNS `127.0.0.1`
     - WINSRV3: `192.168.2.30 / 255.255.255.0 / 192.168.2.254`, DNS `192.168.2.10`
     - WINSRV4: `192.168.2.50 / 255.255.255.0 / 192.168.2.254`, DNS `192.168.2.10`
9. Reboot to apply rename.

### After install — install required roles (WINSRV1 only)
1. Server Manager → **Manage** → **Add Roles and Features**.
2. Next through Before/Type/Server until **Server Roles**.
3. Tick: **Active Directory Domain Services**, **DNS Server**, **DHCP Server**, **File and Storage Services** (already on).
4. Click Next through, click **Install**.
5. When done, click the **yellow flag** notification in Server Manager top-right → **Promote this server to a domain controller**.
6. Choose **Add a new forest** → Root domain name: `manila.com` → Next.
7. Set Directory Services Restore Mode password = `P@ssw0rd` → Next.
8. Click Next through (DNS delegation warning is fine, NetBIOS = `MANILA`, paths = defaults, Review = OK, Prerequisites checks → ignore warnings).
9. Click **Install**. Server reboots automatically.
10. After reboot, log in as `MANILA\Administrator` / `P@ssw0rd`.
11. Now continue with `04_winsrv1_create_users.md` and `03_winsrv1_gpo_setup.md`.

### AD Certificate Services on WINSRV3 (Issuing CA)
Doing this from scratch is complex. The PDF says it's pre-configured. If you absolutely have to rebuild:
1. Join WINSRV3 to manila.com domain first.
2. Add Roles → tick **Active Directory Certificate Services** → Next → ☑ **Certification Authority** + **Certification Authority Web Enrollment** → Install.
3. Click the post-deployment notification → Configure AD CS → Setup Type = **Enterprise CA** → CA Type = **Subordinate CA** → New private key → defaults → **Save the request to a file** (you'd need to take this to the offline WINSRV4 root, sign it, then return the signed cert).
4. This is genuinely a 30+ min task. If you're rebuilding WINSRV3 from zero, you almost certainly won't finish the module — focus on other marks.

---

## 6. Windows 10 — install for Client1/2/3 (only if missing)

### VM specs
| Setting | Value |
|---------|-------|
| Guest OS | Windows 10 64-bit |
| vCPU | 2 |
| RAM | 4096 MB |
| Disk | 40 GB |
| Network adapter | Client1/2: **LAN** port group / Client3: **Internet** port group |
| CD/DVD | `Windows10.iso` |

### Install
1. Power on → install → English → **Install now**.
2. Edition: **Windows 10 Pro** (needed for domain join) → Next → accept license → **Custom Install** → pick disk → Next → wait ~15 min.
3. After reboot, OOBE: region Philippines → keyboard US.
4. **Sign in options**: pick **Domain join instead** (small link bottom-left of "Who's going to use this PC?").
5. Local username: `competitor` → password `P@ssw0rd`. Security questions = anything.
6. Privacy options: turn everything off → Accept.
7. After desktop loads:
   - Rename PC: Start → Settings → System → About → Rename this PC → set `CLIENT1` / `CLIENT2` / `CLIENT3` → restart.
   - **Domain join** (Client1, Client2 only — Client3 stays workgroup):
     Start → Settings → Accounts → Access work or school → Connect → "Join this device to a local Active Directory domain" → `manila.com` → credentials: `MANILA\Administrator` / `P@ssw0rd` → restart.

---

## 7. OpenVPN client on Client3 (HIGH likelihood needed)

After you've configured the pfSense OpenVPN server (file 01 section 8):

1. In pfSense web UI: **VPN → OpenVPN → Client Export**.
2. Scroll down to **Client Install Packages**.
3. Find the row for user `VPNUser`. Click the **Windows Installers — current Windows installer 64-bit** download button. A `.exe` file downloads.
4. Copy this `.exe` to Client3 (paste into a temp folder, or upload to a share, or transfer via Diagnostics → Edit File trick).
5. On Client3: right-click the `.exe` → **Run as administrator** → click through the installer (accept defaults). It installs OpenVPN GUI **plus** your VPNUser profile in one go.
6. After install, look for the OpenVPN icon in the system tray (bottom-right). Right-click → **Connect**.
7. It prompts for credentials: `VPNUser` / `P@ssw0rd` → OK.
8. Tray icon turns green = tunnel up.

> If the installer is blocked by SmartScreen: click **More info** → **Run anyway**.

---

## 8. Chrome ADMX templates on WINSRV1 (optional, for `google` GPO Option A)

Skip this if you used Option B (registry-based GPO) — that path doesn't need ADMX.

1. Download `policy_templates.zip` from `https://chromeenterprise.google/intl/en_us/browser/download/` — this is the public Chrome Enterprise package. (Note: this needs internet on WINSRV1, or pre-download to a USB and copy.)
2. Extract the zip on WINSRV1.
3. In the extracted folder go to `windows\admx\`.
4. **Copy** `chrome.admx` (and `google.admx` if present) → paste to `C:\Windows\PolicyDefinitions\`.
5. From the same source folder, go into `en-US\` → copy `chrome.adml` (and `google.adml`) → paste to `C:\Windows\PolicyDefinitions\en-US\`.
6. Close and reopen any open Group Policy Management Editor windows.
7. Now under **Administrative Templates** → **Google** → **Google Chrome** appears.

---

## 9. Verification — checklist before tomorrow's afternoon session

Quick sanity that all the install/setup work is complete:

| Check | Where | Pass |
|-------|-------|------|
| ESXi reachable | Browser → `https://192.168.1.1/ui` | Login page loads |
| All ISOs uploaded | ESXi → Storage → Datastore browser → ISO folder | 4 .iso files visible |
| pfSense VM running | ESXi VMs list | Green play icon, IP shown |
| WINSRV1/3 VMs running | ESXi VMs list | Same |
| LINSRV1 VM running | ESXi VMs list | Same |
| Client1/2/3 VMs running | ESXi VMs list | Same |
| WINSRV4 VM **stopped** (Offline Root) | ESXi VMs list | Powered off |
| AD domain alive | From Client1 → `nslookup manila.com 192.168.2.10` | Resolves |
| pfSense web admin reachable | From Client1 → `https://172.16.100.254` | Login page |

If all 9 pass, you're at the starting line for `00_RUN_ORDER.md`.
