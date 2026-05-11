# VM Build Specs for Practice (Scaled for One PC)

> Specs below are **reduced** compared to competition to fit on a single PC's RAM. They're enough to practice every task — none of the tasks need more RAM than this.

## Total RAM footprint of all VMs running at once

| VM | Practice RAM | Competition RAM |
|----|--------------|-----------------|
| pfSense | 768 MB | 1024 MB |
| WINSRV1 (DC) | 2048 MB | 4096 MB |
| WINSRV3 (CA) | 2048 MB | 4096 MB |
| LINSRV1 (DMZ) | 1536 MB | 2048 MB |
| Client1 (Win10) | 2048 MB | 4096 MB |
| Client3 (Win10) | 2048 MB | 4096 MB |
| **Total** | **~10.5 GB** | ~19 GB |
| + Host OS | ~3 GB | — |
| **Required free RAM** | **~14 GB** | — |

If you have less than 14 GB free → see `03_practice_runbook.md` for "scenarios" — running only 2–3 VMs at a time.

## Which VMs to skip on practice night

| VM | Build tonight? | Why |
|----|---------------|-----|
| ISP | ❌ No | Optional. Competition has it pre-built. You'd waste an hour. |
| WINSRV4 (Offline Root CA) | ❌ No | Always powered off in competition. No practice value. |
| Client2 | ❌ No | Identical to Client1. Build Client1 only, practice both flows on it. |

## ISO files you need to download tonight

If you haven't already, download these (pick something to do during dinner). Save anywhere — point Workstation at them when building each VM.

| ISO | Approx size | Source |
|-----|-------------|--------|
| pfSense CE 2.7.2 amd64 | 800 MB | `https://www.pfsense.org/download/` |
| Rocky Linux 9.x DVD | 10 GB | `https://rockylinux.org/download` (or AlmaLinux 9 if Rocky is slow) |
| Windows Server 2022 Eval | 5 GB | `https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2022` |
| Windows 10 Enterprise Eval | 5 GB | `https://www.microsoft.com/en-us/evalcenter/evaluate-windows-10-enterprise` |

> Microsoft eval ISOs give you 180 days free — plenty for tonight.

---

## VM 1 — pfSense (build this FIRST, ~25 min total)

VMware Workstation → **File → New Virtual Machine** → **Custom (advanced)** → Next.

1. Hardware compatibility: latest → Next.
2. Install OS: **I will install the operating system later** → Next.
3. Guest OS: **Other** → Version: **FreeBSD 14 64-bit** (or whatever Other FreeBSD is offered) → Next.
4. VM name: `pfSense-PRACTICE` → location anywhere → Next.
5. Processors: 1, Cores per processor: 1 → Next.
6. Memory: **768 MB** → Next.
7. Network type: **Use host-only networking** → Next (we'll fix this in step 11).
8. SCSI controller: LSI Logic → Next.
9. Virtual disk type: SCSI → Next.
10. Create a new virtual disk → 8 GB, **Store as a single file** → Next → Finish.
11. **Customize Hardware** (the VM was just created, click it in the left pane → **Edit virtual machine settings**):
    - Click **Network Adapter** → right side change "Network connection" to **Custom: Specific virtual network** → dropdown → **VMnet2 (WAN)**.
    - Click **Add…** → **Network Adapter** → Finish. Then select the new "Network Adapter 2" → set to **VMnet3 (LAN)**.
    - Click **Add…** → **Network Adapter** → Finish. Select Network Adapter 3 → **VMnet4 (DMZ)**.
    - Click **Add…** → **Network Adapter** → Finish. Select Network Adapter 4 → **VMnet5 (Servers)**.
    - Click **CD/DVD (SATA)** → "Use ISO image file" → Browse to your pfSense ISO → ☑ Connect at power on.
    - **Remove** the floppy drive (left list → Floppy → click "Remove" below) — saves boot menu confusion.
    - OK.
12. Power on → follow `solution/01_install_guides.md` Section 3 for the pfSense text installer. Skip the "VM specs" subtable in that file — you already set them.
13. After install completes and pfSense console menu appears:
    - Press `1` to assign interfaces. The names will be **`em0`, `em1`, `em2`, `em3`** (FreeBSD names for the 4 NICs).
    - WAN = em0, LAN = em1, OPT1 (DMZ) = em2, OPT2 (Servers) = em3.
    - Press `2` to set IPs — see file 01 of solution for the exact values.
14. **Take a snapshot now** (see file 04 of this folder). Name it `pfSense-fresh-install`. If your next practice run breaks something you can revert in 10 seconds.

## VM 2 — Rocky Linux 9 (LINSRV1) (~25 min)

1. New VM → Custom → Linux → **Red Hat Enterprise Linux 9 64-bit**.
2. Name: `LINSRV1-PRACTICE`.
3. Processors: 2, Memory: **1536 MB**.
4. Network: Custom → **VMnet4 (DMZ)**.
5. Disk: 20 GB single file.
6. Edit hardware → CD/DVD → point to Rocky 9 ISO.
7. Power on → follow `solution/01_install_guides.md` Section 4 (Anaconda walkthrough).
8. IP `192.168.1.10/24` gateway `192.168.1.254` DNS `192.168.2.10`.
9. After login, **take a snapshot** named `Rocky-fresh-install`.

## VM 3 — Windows Server 2022 (WINSRV1) (~40 min — eat dinner during install)

1. New VM → Custom → Microsoft Windows → **Windows Server 2022**.
2. Name: `WINSRV1-PRACTICE`.
3. Processors: 2, Memory: **2048 MB**.
4. Network: Custom → **VMnet5 (Servers)**.
5. Disk: 60 GB single file.
6. Edit hardware → CD/DVD → point to Server 2022 ISO.
7. Power on → follow `solution/01_install_guides.md` Section 5. Choose **Standard with Desktop Experience**.
8. After install + rename + IP set + AD DS promote: domain `manila.com`, password `P@ssw0rd`.
9. **Snapshot** named `WINSRV1-DC-fresh`.

> **Time-saver:** if you only have 4 hours total tonight, you can SKIP building WINSRV1 from ISO. Instead, install AD DS and use it during the GPO practice tomorrow morning before competition. Or, in extremis, just read `solution/03_winsrv1_gpo_setup.md` until you can recite the click paths.

## VM 4 — Windows 10 Client (we'll use it as Client1 AND Client3) (~30 min)

1. New VM → Custom → Microsoft Windows → **Windows 10 64-bit**.
2. Name: `Client1-PRACTICE`.
3. Processors: 2, Memory: **2048 MB**.
4. Network: Custom → **VMnet3 (LAN)** (we'll switch to VMnet2 when using it as Client3).
5. Disk: 40 GB single file.
6. CD/DVD → Win10 ISO.
7. Install → pick **Domain join instead** to create a local account → username `competitor` / `P@ssw0rd`.
8. After install: rename PC to `CLIENT1` → restart → join `manila.com` (Settings → Accounts → Access work or school → Connect → Domain join).
9. **Snapshot** named `Client1-domain-joined`.

> To use the same VM as Client3 later: VM Settings → Network → change to **VMnet2 (WAN)**, then in Windows leave domain (Settings → Accounts → Disconnect work or school). Take a separate snapshot called `Client3-workgroup`. Switch between the two snapshots to swap modes in 10 seconds.

## VM 5 — Windows Server (WINSRV3, optional)

If you really want to practice IIS + certs, clone WINSRV1 (right-click → Clone → Linked Clone → name `WINSRV3-PRACTICE`). Change its IP to `192.168.2.30`, rename to WINSRV3, run `dcpromo` removal (no — keep simple: just join it to manila.com and install AD CS Subordinate CA per `solution/01_install_guides.md` Section 5 last subsection — though honestly, **skip this tonight** unless you've finished everything else).

---

## After all builds — verify the network

Power on pfSense + Client1 + LINSRV1 at the same time. From Client1's Command Prompt:

```cmd
ping 172.16.100.254     :: pfSense LAN — expect replies
ping 192.168.2.10       :: WINSRV1 — expect replies (if it's also on)
```

If pings work, your virtual networks are wired correctly. If not → check each VM's NIC assignment matches the right VMnet.

## Next: run the practice drills

Go to `03_practice_runbook.md`.
