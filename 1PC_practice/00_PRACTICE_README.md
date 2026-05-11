# One-PC Practice — Tonight's Plan

## The two-folder model — how 1PC_practice and solution work together

```
┌─────────────────────────────────┐         ┌──────────────────────────────────┐
│  1PC_practice/  (this folder)   │   →     │  solution/  (the 11 main guides) │
│                                 │         │                                  │
│  Step 1: install VMware         │         │  Step 4 onwards: configuration   │
│  Step 2: create virtual         │         │  tasks — identical to            │
│          networks (vmnets)      │         │  tomorrow's competition          │
│  Step 3: build practice VMs     │         │                                  │
│                                 │         │  Read 00_RUN_ORDER, then         │
│  Once VMs are running, you're   │         │  follow each file as listed      │
│  in the same state as someone   │         │                                  │
│  starting MA2 at the venue      │         │                                  │
└─────────────────────────────────┘         └──────────────────────────────────┘
```

**The point of `1PC_practice/`** is to get you to the same starting state as the competition venue — pfSense/WinSrv/LinSrv/Clients running on a network with the right subnets. From there, **every configuration task is the same** as the competition, so you use `solution/` files unchanged.

You're right that with no real infrastructure (no physical switches, no real ESXi), the **VMware Virtual Network Editor IS your network infrastructure** for practice. The 4 host-only vmnets I'll have you create match the competition's 4 VLANs exactly:

| Competition VLAN | Subnet | Your vmnet (practice) |
|------------------|--------|------------------------|
| WAN (Internet)   | 192.0.2.0/24 (or any non-routed range) | vmnet2 |
| LAN              | 172.16.100.0/24 | vmnet3 |
| DMZ              | 192.168.1.0/24 | vmnet4 |
| Servers          | 192.168.2.0/24 | vmnet5 |

Because the subnets and IPs are identical to the PDF, every IP, every firewall rule, every DNS lookup in the `solution/` guides works on your practice setup with **zero changes**.

## What this folder is for

Tomorrow's competition uses three machines (PC1, PC2, the ESXi server PC3). Tonight you have **one PC**. This folder explains how to **simulate the competition environment on a single PC** using VMware Workstation Pro so you can rehearse the actual configuration work.

> **Key point:** the *configuration* tasks (pfSense rules, GPOs, LINSRV1 commands, etc.) are **identical** whether you're on competition ESXi or practice Workstation. The only difference is how you create / power on / network the VMs. So all the `solution/` guides still apply unchanged once your practice VMs are running.

## Folder layout

```
1PC_practice/
├── 00_PRACTICE_README.md        ← this file
├── 01_VMware_setup.md           ← install Workstation, create 4 virtual networks
├── 02_VM_build_specs.md         ← VM specs scaled for one PC + install order
├── 03_practice_runbook.md       ← which tasks to drill tonight + RAM scheduling
└── 04_snapshots_and_recovery.md ← use snapshots so mistakes cost 30 sec, not 30 min
```

## Hardware reality check — do this first

Open Task Manager (Ctrl+Shift+Esc) → **Performance** tab → **Memory**. If your PC has:

| Total RAM | What's realistic tonight |
|-----------|--------------------------|
| ≥ 32 GB | Run all 6 VMs at once (full topology). Best practice experience. |
| 16–24 GB | Run 2–3 VMs at a time (scenarios). Most beginners are here. |
| 8 GB | One VM at a time. Tight but workable — see scenario splits in file 03. |
| < 8 GB | Practice will be painful — focus on reading the guides instead and on the venue tomorrow. |

Also check:
- **Disk free:** Need ~80 GB free.
- **CPU virtualization:** Open Task Manager → Performance → CPU. Bottom-right corner should say **Virtualization: Enabled**. If it says Disabled, reboot into BIOS and enable VT-x / AMD-V before continuing.

## Recommended schedule for tonight (4 hours)

| Time | What |
|------|------|
| 30 min | Read this README + file `01_VMware_setup.md`, install/check VMware Workstation, create the 4 virtual networks |
| 45 min | Build a minimal pfSense VM (file `02_VM_build_specs.md` Section 2) — this is the most worthwhile install to practice because pfSense has a unique console install flow you'll see at the venue |
| 45 min | Build Rocky Linux 9 VM for LINSRV1 — the second-most-worthwhile install (no GUI, partitioning choices) |
| 60 min | Drill pfSense rules + Snort rule paste (the highest-mark mistake-prone work) |
| 60 min | Drill LINSRV1 commands from `solution/05_linsrv1_setup.md` — realm join is the trickiest |
| — | **Don't** build Windows Server / Windows 10 from ISO tonight. Each takes 30+ minutes of waiting and you won't learn anything useful. If you have time after the above, do read `solution/03_winsrv1_gpo_setup.md` and *imagine* the clicks. |

> If you don't finish — that's fine. **Sleep matters more than rehearsal.** A rested beginner who has read every guide once will outperform a tired beginner who has rehearsed once.

## What this practice does NOT cover

- Real ESXi server interaction (Datastore browser, Connect to Server dialog). You'll do that briefly tomorrow morning — see `solution/01_install_guides.md` Section 0. It's 5 clicks.
- Realistic network latency between PC1 and PC2. In practice you're using the same machine.
- Two competitors stepping on each other. In practice it's just you — but read `solution/10_team_split_PC1_PC2.md` tonight anyway so you know the sync points by heart.

## Where to go next — the exact reading order

### Setup phase (1PC_practice/ files)
1. **`01_VMware_setup.md`** — Install Workstation, create the 4 vmnets that simulate the competition VLANs.
2. **`02_VM_build_specs.md`** — Build VMs (pfSense, WinSrv, LinSrv, Win10 client) with scaled-down RAM.
3. **`04_snapshots_and_recovery.md`** — Snapshot each VM at clean-install state before continuing.

### Configuration phase (solution/ files — identical to tomorrow's competition)

Once VMs are running and snapshotted, **open `solution/00_RUN_ORDER.md`** and follow it like it's the real competition. Every file in `solution/` works against your practice VMs unchanged.

`03_practice_runbook.md` (this folder) tells you **which solution files to drill in which order**, and which to skip if you're tight on time:

- **Scenarios A, B, C, D** = curated 4-hour practice (the high-value tasks).
- **Scenario E** = complete coverage — every task in `solution/`. Only if you have 8+ hours.

### After practice — for tomorrow morning

The `solution/` files are exactly what you'll use at the competition. Bring them on a USB stick. The fact that you practised on Workstation instead of ESXi makes no difference — the click paths and commands are the same.
