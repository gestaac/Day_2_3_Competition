# 📋 ONE-PAGE COMPETITION CHEAT SHEET — print or pin

## Credentials
| System | Username | Password |
|--------|----------|----------|
| Competitor laptop | `competitor1b` | `Tagaytay_62&L` |
| ESXi host (192.168.1.1) | `wsauser` | `Andres@9V4` |
| All Windows VMs (Admin) | `Administrator` | `P@ssw0rd` |
| All AD users (M001…, C1…) | (samaccountname) | `P@ssw0rd` |
| LINSRV1 root | `root` | `P@ssw0rd` |
| LINSRV1 user | `competitor` | `P@ssw0rd` |
| pfSense (default) | `admin` | `pfsense` → CHANGE to `P@ssw0rd` |
| Executive PSO test (M004) | `M004` | `P@ssw0rdP@ssw0rd` |
| VPN | `VPNUser` | `P@ssw0rd` |

## IPs / Subnets
| VLAN | Subnet | Gateway |
|------|--------|---------|
| LAN     | 172.16.100.0/24 | 172.16.100.254 |
| Servers | 192.168.2.0/24  | 192.168.2.254  |
| DMZ     | 192.168.1.0/24  | 192.168.1.254  |
| WAN     | DHCP from ISP   | — |

| VM | IP |
|----|----|
| ISP             | (DHCP server) |
| Firewall (pfSense) | LAN .254 / DMZ .254 / Servers .254 / WAN DHCP |
| WINSRV1 (DC) | 192.168.2.10 |
| WINSRV3 (Issuing CA) | 192.168.2.30 |
| WINSRV4 (Root CA) | 192.168.2.50 (**OFF**) |
| LINSRV1 (DMZ web) | 192.168.1.10 |
| Client1/2 | DHCP on LAN |
| Client3 | DHCP on WAN side |

## Domain
- Forest / domain: `manila.com`
- DNS server: `192.168.2.10`
- Two websites the project tests:
  - ✅ `https://www.nationalmuseum.gov.ph` — allowed
  - ❌ `https://www.starcity.com.ph` — must be blocked
  - 🔵 `https://www.manila.com` → LINSRV1 (HTTPS via WINSRV3 cert)
  - 🔵 `https://webtest.manila.com` → WINSRV3 IIS

## AD users by group (Table 3)
| Group | Members |
|-------|---------|
| **Executive** | M004, S001 |
| **IT** (sudo on LINSRV1) | C1, C2 |
| **Marketing** | M001 |
| **Customer Service** | M002 |
| **Sales** | M003 |
| **VPNGroup** | VPNUser |

## Critical port lists
- **AD ports (LAN→Servers)**: 53, 88, 135, 137-139, 389, 443, 445, 464, 636, 3268-3269, 9389
- **DMZ→Servers** (realm join): 53, 88, 135, 137-139, 389, 445, 464, 636, 3268-3269
- **WAN→DMZ** (inbound web): 80, 443, 53
- **LAN→DMZ** (allowed services): 22, 80, 443, 53
- **LINSRV1 firewalld services**: `2022/tcp`, `http`, `https`, `kerberos`

## Snort custom rule (paste, edit subnet to your WAN)
```
alert tcp any any <> 172.16.1.0/24 any (flags: F; msg:"Possible FIN scan"; sid:100001; rev:1;)
```

## SSH to LINSRV1 from Client1
```
ssh -p 2022 C1@192.168.1.10
# password: P@ssw0rd
```

## GPO names (all SEVEN expected — note `google` is marking-sheet-only, NOT in the PDF)
1. `lockout` — 3 fails, 60s
2. `Banner` — title `WorldSkills ASEAN Manila`, text `Authorized access only`
3. `restrict control panel` — deny Executive
4. `disabled add and remove program panel` — apply to Executive only
5. `autolock` — 10s screen, Executive only
6. `certenroll` — autoenroll computer + user
7. **`google`** — Chrome home page = `www.manila.com`, locked from change (marking sheet A4 line 126, A7 home page check)

## Share spec
- Path: `C:\shares\pictures` → SMB name `pictures`
- Share perms: **Marketing = Read**, **Executive = Full**, no Everyone
- NTFS: tight (SYSTEM, Administrators, Executive=FC, Marketing=R&E, no inherit, no Everyone)
- Audit on `park.jpg`: Everyone → Read = Success

## Submission rule
- One `.docx` on competitor Desktop, filename = your **country code**
- Tell experts location **before** leaving the room

## Quick "did I mess up?" commands
```cmd
:: Client
gpupdate /force & gpresult /r
ipconfig /all
nslookup www.manila.com
```
```powershell
# WINSRV1
Get-GPO -All | sort DisplayName | ft DisplayName
Get-SmbShare pictures
auditpol /get /subcategory:"File System"
```
```bash
# LINSRV1
realm list; sestatus; firewall-cmd --list-all
grep -E "^(Port|Permit|Allow|MaxAuth)" /etc/ssh/sshd_config
```

## DO NOT
- ❌ Change `P@ssw0rd` on anything except where project says.
- ❌ Power on WINSRV4 unless troubleshooting.
- ❌ Add `any any` allow rule on pfSense.
- ❌ Use `Ubuntu` for LINSRV1 — must be RHEL-family (firewalld/SELinux commands).
- ❌ Skip the deliverable doc — easy marks gone if missing.
