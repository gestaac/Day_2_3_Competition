# WINSRV1 — Create AD users, groups, OUs (only if missing)

> **When to use this:** during Pre-flight you opened **Server Manager → Tools menu → Active Directory Users and Computers** on WINSRV1 and Table 3 users (M001–M004, S001, C1, C2) **were missing**. If they're already there, skip this whole file.

## What you'll create

| Object | Why we need it |
|--------|----------------|
| OU `Manila`, OU `Singapore` | Match Table 3 "OU" column |
| Group `Marketing`, `Customer Service`, `Sales`, `Executive`, `IT`, `VPNGroup` | Used by share perms, GPOs, sudo on LINSRV1, OpenVPN |
| Users M001-M004, S001, C1, C2 | Test users graders log in as |
| User VPNUser | OpenVPN user (PDF p.10) |

All users get password `P@ssw0rd`. **Do not change this** — it's the project default.

---

## Step 1 — Open elevated PowerShell on WINSRV1

1. Click the **Start** button (Windows logo, bottom-left).
2. Start typing `PowerShell`.
3. In the search results, **right-click** "Windows PowerShell" → click **Run as administrator** → click **Yes** at the UAC prompt.
4. The PowerShell window opens with a blue background and `PS C:\Windows\system32>` prompt — that confirms you're elevated.

Verify you have the AD module:
```powershell
Import-Module ActiveDirectory
Get-ADDomain
```
You should see `manila.com` listed as the DNS root.

> If you'd rather click than type: you can do everything in this file via **Server Manager → Tools → Active Directory Users and Computers** instead. Right-click an OU → New → User; right-click the Users container → New → Group. PowerShell is just faster because there are 14 objects to create.

## Step 2 — Create the two OUs

```powershell
New-ADOrganizationalUnit -Name "Manila"    -Path "DC=manila,DC=com" -ProtectedFromAccidentalDeletion:$false
New-ADOrganizationalUnit -Name "Singapore" -Path "DC=manila,DC=com" -ProtectedFromAccidentalDeletion:$false
```

**What this does:** creates two containers in AD so users can be organised by city, matching the PDF's Table 3 layout. The `-ProtectedFromAccidentalDeletion:$false` flag is needed so you can delete/recreate during practice without errors.

**Verify:** Open `dsa.msc` → expand `manila.com` → you should see both new OUs.

## Step 3 — Create the security groups

```powershell
$groups = @("Marketing","Customer Service","Sales","Executive","IT","VPNGroup")
foreach ($g in $groups) {
    New-ADGroup -Name $g -GroupScope Global -GroupCategory Security -Path "CN=Users,DC=manila,DC=com"
}
```

**What this does:** creates the 6 security groups in the default `Users` container. Group scope **Global** = members are domain accounts only (the right choice for AD-internal RBAC). Category **Security** = can be used in ACLs (a Distribution group cannot).

**Verify:** `Get-ADGroup -Filter * | Select Name`

## Step 4 — Create the users (copy as one block)

```powershell
$pass = ConvertTo-SecureString "P@ssw0rd" -AsPlainText -Force

# M001 - Marketing, Manila
New-ADUser -SamAccountName M001 -Name M001 -DisplayName "Brand Marketing Specialist" `
  -Department Marketing -City Manila -UserPrincipalName "M001@manila.com" `
  -Path "OU=Manila,DC=manila,DC=com" -AccountPassword $pass -Enabled $true -PasswordNeverExpires $true
Add-ADGroupMember -Identity Marketing -Members M001

# M002 - Customer Service, Manila
New-ADUser -SamAccountName M002 -Name M002 -DisplayName "Customer Experience Rep" `
  -Department "Customer Service" -City Manila -UserPrincipalName "M002@manila.com" `
  -Path "OU=Manila,DC=manila,DC=com" -AccountPassword $pass -Enabled $true -PasswordNeverExpires $true
Add-ADGroupMember -Identity "Customer Service" -Members M002

# M003 - Sales, Manila
New-ADUser -SamAccountName M003 -Name M003 -DisplayName "Store Sales" `
  -Department Sales -City Manila -UserPrincipalName "M003@manila.com" `
  -Path "OU=Manila,DC=manila,DC=com" -AccountPassword $pass -Enabled $true -PasswordNeverExpires $true
Add-ADGroupMember -Identity Sales -Members M003

# M004 - EXECUTIVE, Manila
New-ADUser -SamAccountName M004 -Name M004 -DisplayName "Operations Manager" `
  -Department Operations -City Manila -UserPrincipalName "M004@manila.com" `
  -Path "OU=Manila,DC=manila,DC=com" -AccountPassword $pass -Enabled $true -PasswordNeverExpires $true
Add-ADGroupMember -Identity Executive -Members M004

# S001 - EXECUTIVE, Singapore
New-ADUser -SamAccountName S001 -Name S001 -DisplayName "Marketing Manager" `
  -Department Marketing -City Singapore -UserPrincipalName "S001@manila.com" `
  -Path "OU=Singapore,DC=manila,DC=com" -AccountPassword $pass -Enabled $true -PasswordNeverExpires $true
Add-ADGroupMember -Identity Executive -Members S001

# C1 - IT, Manila  (will get sudo on LINSRV1)
New-ADUser -SamAccountName C1 -Name C1 -DisplayName "Technical Support 1" `
  -Department IT -City Manila -UserPrincipalName "C1@manila.com" `
  -Path "OU=Manila,DC=manila,DC=com" -AccountPassword $pass -Enabled $true -PasswordNeverExpires $true
Add-ADGroupMember -Identity IT -Members C1

# C2 - IT, Singapore  (will get sudo on LINSRV1)
New-ADUser -SamAccountName C2 -Name C2 -DisplayName "Technical Support 2" `
  -Department IT -City Singapore -UserPrincipalName "C2@manila.com" `
  -Path "OU=Singapore,DC=manila,DC=com" -AccountPassword $pass -Enabled $true -PasswordNeverExpires $true
Add-ADGroupMember -Identity IT -Members C2

# VPN user
New-ADUser -SamAccountName VPNUser -Name VPNUser -DisplayName "VPN User" `
  -Department Remote -City Manila -UserPrincipalName "VPNUser@manila.com" `
  -Path "OU=Manila,DC=manila,DC=com" -AccountPassword $pass -Enabled $true -PasswordNeverExpires $true
Add-ADGroupMember -Identity VPNGroup -Members VPNUser
```

**Important flags explained:**
- `-Enabled $true` — account is on by default. Without this you cannot log in.
- `-PasswordNeverExpires $true` — stops the password from expiring during the competition. Real environments would set this false, but here it's safer.
- `-UserPrincipalName "...@manila.com"` — the "user@domain" format. SSH and many apps prefer UPN over `samAccountName`.

## Step 5 — Verify

```powershell
Get-ADUser -Filter * -SearchBase "DC=manila,DC=com" | Select SamAccountName, Enabled | Sort SamAccountName

Get-ADGroupMember Executive | Select Name      # expect: M004, S001
Get-ADGroupMember IT        | Select Name      # expect: C1, C2
Get-ADGroupMember VPNGroup  | Select Name      # expect: VPNUser
Get-ADGroupMember Marketing | Select Name      # expect: M001
```

If any user is `Enabled : False`, run:
```powershell
Enable-ADAccount -Identity <samaccountname>
```

## Why this order matters

You **must** have users before:
- LINSRV1 can `realm join` and accept them via sudo (file 04).
- pfSense OpenVPN can LDAP-bind and validate `VPNUser` (file 01).
- The share permissions in file 02 can reference `Executive` / `Marketing`.

If you run files 02/04/01 first and Marketing/Executive don't exist yet, those steps will fail silently or with cryptic "couldn't find principal" errors.
