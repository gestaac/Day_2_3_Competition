# VMware Workstation — Install + Create Virtual Networks

> This file gets you to a state where you have VMware Workstation Pro installed and 4 virtual networks ready that mirror the competition VLANs.

## 1. Install VMware Workstation Pro (or Player)

> If you already have VMware Workstation installed, skip to section 2.

1. Download from `https://www.vmware.com/products/workstation-pro/workstation-pro-evaluation.html` (Broadcom now owns it; current free-for-personal-use license is fine for tonight).
2. Run installer → accept defaults → reboot if prompted.
3. After launch, when asked for a license: "Use Workstation Pro for **Personal Use**" (free).

> **Workstation Pro vs Player:** Player works but **does not support snapshots**. Snapshots are critical for practice — they let you rewind a broken pfSense or DC in 10 seconds. Insist on Pro.

## 2. Create the 4 virtual networks (this is the heart of the simulation)

The competition has 4 separate VLANs: **Internet (WAN), LAN, DMZ, Servers**. We simulate each with a VMware "Virtual Network" (vmnet).

### Open the Virtual Network Editor

1. In VMware Workstation, top menu → **Edit** → **Virtual Network Editor**.
2. If you see "Some settings cannot be changed because you do not have administrative privileges" at the bottom → click **Change Settings** → click **Yes** at UAC prompt.

### Add the 4 networks

The Virtual Network Editor will already have `VMnet0` (Bridged), `VMnet1` (Host-only), and `VMnet8` (NAT) by default. Leave those alone. We're adding our own.

For each network below, click **Add Network…** at the bottom right and choose the listed VMnet number. Then configure it as shown.

#### 2a. WAN (simulating "Internet")
- Click **Add Network…** → select **VMnet2** → OK.
- VMnet2 row → tick **Host-only** (no real internet needed for practice).
- **Connect a host virtual adapter to this network**: ☐ unticked (we don't want our host PC on it).
- **Use local DHCP service to distribute IP addresses to VMs**: ☑ ticked.
- **Subnet IP**: `192.0.2.0` → **Subnet mask**: `255.255.255.0`.
- Click **Apply**.

#### 2b. LAN
- **Add Network…** → **VMnet3** → OK.
- Tick **Host-only**.
- **Host virtual adapter**: ☐ unticked.
- **DHCP**: ☐ unticked (pfSense will provide DHCP).
- **Subnet IP**: `172.16.100.0` / `255.255.255.0`.
- Apply.

#### 2c. DMZ
- **Add Network…** → **VMnet4** → OK.
- Tick **Host-only**.
- **Host virtual adapter**: ☐ unticked.
- **DHCP**: ☐ unticked.
- **Subnet IP**: `192.168.1.0` / `255.255.255.0`.
- Apply.

#### 2d. Servers
- **Add Network…** → **VMnet5** → OK.
- Tick **Host-only**.
- **Host virtual adapter**: ☐ unticked.
- **DHCP**: ☐ unticked.
- **Subnet IP**: `192.168.2.0` / `255.255.255.0`.
- Apply.

### Verify in the editor
After adding all four, the list should look roughly like this:

| Name | Type | External Connection | Host Connection | DHCP | Subnet |
|------|------|---------------------|-----------------|------|--------|
| VMnet0 | Bridged | (your physical NIC) | — | — | — |
| VMnet1 | Host-only | — | Connected | — | (varies) |
| VMnet2 | Host-only | — | — | Enabled | 192.0.2.0 |
| VMnet3 | Host-only | — | — | — | 172.16.100.0 |
| VMnet4 | Host-only | — | — | — | 192.168.1.0 |
| VMnet5 | Host-only | — | — | — | 192.168.2.0 |
| VMnet8 | NAT | NAT | Connected | Enabled | (varies) |

Click **OK** at bottom to close the editor.

> **Why Host-only instead of Bridged or NAT?** Host-only networks are isolated from your real LAN — exactly like the competition VLANs. Bridged would expose your practice DHCP server to your home/office network. NAT would let your VMs reach the real internet which is unnecessary tonight and could cause Windows Update to interrupt practice.

## 3. Map of VMnet → competition role (memorize)

| Competition VLAN | VMware vmnet | Subnet | Who's on it |
|------------------|--------------|--------|-------------|
| Internet (WAN) | **vmnet2** | 192.0.2.0/24 | pfSense WAN side, Client3, (simulated ISP if you build one) |
| LAN | **vmnet3** | 172.16.100.0/24 | pfSense LAN side, Client1, Client2 |
| DMZ | **vmnet4** | 192.168.1.0/24 | pfSense DMZ side, LINSRV1 |
| Servers | **vmnet5** | 192.168.2.0/24 | pfSense Servers side, WINSRV1, WINSRV3 |

When a guide says "attach to the DMZ port group", you pick **vmnet4** in the VM's NIC settings.

## 4. Sanity check

1. Open **Command Prompt** as Administrator on your host → run `ipconfig /all`.
2. You should see VMware Network Adapter entries for VMnet1 and VMnet8 (the ones with host connection). You should **not** see them for VMnet2-5 (we unticked host connection — that's deliberate, so your host can't accidentally talk to the practice network).

If you accidentally tick "Host virtual adapter" later, your host PC will appear on the competition subnet and might confuse DHCP. Untick it.

## Next: build the VMs

Go to `02_VM_build_specs.md`.
