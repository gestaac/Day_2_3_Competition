# WINSRV1 — GPOs, password policies, share, auditing (walkthrough)

> Run on **WINSRV1** as Administrator. We do this in **two ways** — GUI clicks (the way graders expect you to know) **plus** a PowerShell equivalent (faster + reproducible). Pick whichever you're comfortable with per task.

## How to open the tools (do this once at the start — keep them all open)

Server Manager opens by default the first time you log in to WINSRV1. If it's not open: **Start button** (Windows logo, bottom-left) → click the **Server Manager** tile (green icon).

Inside Server Manager, click the **Tools** menu at the top-right corner. From this single menu you can open every tool you need today:

| Tool you'll click in Tools menu | What it's for |
|---------------------------------|---------------|
| **Group Policy Management** | Creating and editing the 6 GPOs |
| **Active Directory Administrative Center** | Creating the Fine-Grained Password Policy (PSO) |
| **Active Directory Users and Computers** | Resetting M004's password, looking up group membership |
| **DNS** | Adding A records (used in file 05) |
| **Event Viewer** | Verifying the audit log entry |

Other places you'll go (not in Tools menu):
- **File Explorer** — to create `C:\shares\pictures`.
- **Server Manager → left sidebar → File and Storage Services → Shares** — to create the share with the wizard.
- **PowerShell (Administrator)** — for verification commands (Start → type `PowerShell` → right-click → **Run as administrator**).

> If you ever forget where a tool lives: click **Start** and just type its name (e.g. "Group Policy") — Windows search will find it.

---

## Task 1 — Domain password policy: length 8, history 30

> PDF p.11: *"all domain users' passwords to be 8 characters in length, and keep a history of 30 past passwords"*

### GUI path
1. In **Server Manager**, click the **Tools** menu (top-right) → click **Group Policy Management**. A new window opens.
2. In its left tree: expand **Forest: manila.com** → **Domains** → **manila.com**.
3. Find **Default Domain Policy** → right-click it → click **Edit…**. The Group Policy Management Editor opens in another window.
4. In the editor's left tree, expand: **Computer Configuration** → **Policies** → **Windows Settings** → **Security Settings** → **Account Policies** → click **Password Policy**.
5. In the right pane, double-click each setting and change it:
   - **Minimum password length** → `8` → OK.
   - **Enforce password history** → `30 passwords remembered` → OK.
   - **Password must meet complexity requirements** → Enabled (leave the default).
6. Close the editor window (the X). Go back to the Group Policy Management window — your changes are saved automatically.
7. Open **PowerShell (Admin)** and run `gpupdate /force` so the DC re-reads the policy.

### PowerShell equivalent
```powershell
Set-ADDefaultDomainPasswordPolicy -Identity manila.com `
    -MinPasswordLength 8 -PasswordHistoryCount 30 -ComplexityEnabled $true
```

### Verify
```powershell
Get-ADDefaultDomainPasswordPolicy | Select MinPasswordLength, PasswordHistoryCount
```

> ⚠ Do **NOT** change anyone's password just because you set this policy. Existing `P@ssw0rd` (8 chars) already complies.

---

## Task 2 — Fine-grained password policy for Executive group (length 16)

> PDF p.11: *"fine-grained password policy that requires members of the executive group to have a 16-character long password. Change password to P@ssw0rdP@ssw0rd during testing for one member"*

### GUI path
1. Server Manager → **Tools** menu → click **Active Directory Administrative Center**. A new window opens.
2. On the **left navigation pane**, click the small **Tree View** icon at the top (two stacked rectangles) to switch from the default list view to a tree.
3. In the tree expand: **manila (local)** → **System** → click **Password Settings Container**.
4. Look at the **Tasks pane on the right** → under "Password Settings Container" → click **New** → click **Password Settings**.
5. A form opens. Fill it in:
   - **Name** = `ExecutivePSO`
   - **Precedence** = `10` (lower number wins if multiple policies apply)
   - **Minimum password length** = `16`
   - **Enforce minimum password history** = `30`
   - **Password must meet complexity requirements** = tick the box ✓
6. Scroll to **Directly Applies To** at the bottom → click **Add…** → type `Executive` → click **Check Names** → OK.
7. Click **OK** to save.

Then change M004's password using the same window:
1. In the left tree of ADAC, click **manila (local)** → double-click **Manila** (the OU you made).
2. Right-click the **M004** user → click **Reset password…**
3. Type `P@ssw0rdP@ssw0rd` in both boxes.
4. **Untick** "User must change password at next logon".
5. Click **OK**.

> If you don't see ADAC in the Tools menu, just use **Active Directory Users and Computers** for the password reset (same Tools menu); but the PSO **must** be created in ADAC — ADUC doesn't have the wizard for it.

### PowerShell equivalent
```powershell
New-ADFineGrainedPasswordPolicy -Name "ExecutivePSO" -Precedence 10 `
    -MinPasswordLength 16 -PasswordHistoryCount 30 -ComplexityEnabled $true

Add-ADFineGrainedPasswordPolicySubject -Identity "ExecutivePSO" -Subjects "Executive"

Set-ADAccountPassword -Identity M004 -Reset `
    -NewPassword (ConvertTo-SecureString "P@ssw0rdP@ssw0rd" -AsPlainText -Force)
```

### Verify
```powershell
Get-ADUserResultantPasswordPolicy -Identity M004      # should show ExecutivePSO
```

---

## Task 3 — GPO `lockout` (3 fails, 60s)

> PDF p.11: *"lock accounts after 3 failed logon attempts for all domain users. Account duration lockout is 60 seconds."*

### GUI path
1. In **Group Policy Management** (still open from Task 1), expand **Forest: manila.com → Domains → manila.com**.
2. Right-click **manila.com** (the domain itself, not an OU) → click **Create a GPO in this domain, and Link it here…**
3. In the dialog box: **Name** = `lockout` → click **OK**.
4. The new GPO appears under `manila.com` in the tree. Right-click it → click **Edit…**. The editor opens.
5. In the editor, expand: **Computer Configuration** → **Policies** → **Windows Settings** → **Security Settings** → **Account Policies** → click **Account Lockout Policy**.
6. In the right pane, double-click each setting and configure:
   - **Account lockout threshold** → `3` invalid logon attempts → OK (Windows will offer to set the next two values to 30 minutes — click OK to accept, we'll change them next).
   - **Account lockout duration** → `1` minute → OK.
   - **Reset account lockout counter after** → `1` minute → OK.
7. Close the editor.

> Account lockout policies must be set at the **domain root level** to take effect on domain accounts — that's why we link at `manila.com`, not at an OU.

### Verify
```powershell
Get-ADDefaultDomainPasswordPolicy | Select LockoutThreshold, LockoutDuration, LockoutObservationWindow
```

---

## Task 4 — GPO `Banner` (logon title + text)

> PDF p.11: *"login banner/title 'WorldSkills ASEAN Manila'"* and *"login banner/text 'Authorized access only'"*

### GUI path
1. In **Group Policy Management** → right-click **manila.com** → **Create a GPO in this domain, and Link it here…** → Name = `Banner` → OK.
2. Right-click the new `Banner` GPO under manila.com → **Edit…**
3. In the editor, expand: **Computer Configuration** → **Policies** → **Windows Settings** → **Security Settings** → **Local Policies** → click **Security Options**.
4. The right pane has a long alphabetical list of settings. Scroll to find these two (both start with "Interactive logon:"):
   - Double-click **Interactive logon: Message title for users attempting to log on** → tick **Define this policy setting** → type `WorldSkills ASEAN Manila` → OK.
   - Double-click **Interactive logon: Message text for users attempting to log on** → tick **Define this policy setting** → type `Authorized access only` → OK.
5. Close the editor.

### Verify
On Client1/2, run `gpupdate /force`, sign out, look at the logon screen — banner must appear before the password box.

---

## Task 5 — GPO `restrict control panel` (deny Executive)

> PDF p.11: *"restrict access to the control panel – which is only applicable to all users, except for the executive group"*

### GUI path
1. In **Group Policy Management** → right-click **manila.com** → **Create a GPO in this domain, and Link it here…** → Name = `restrict control panel` → OK.
2. Right-click the new GPO → **Edit…**
3. In the editor expand: **User Configuration** → **Policies** → **Administrative Templates** → click **Control Panel**.
4. In the right pane, double-click **Prohibit access to Control Panel and PC settings** → click the **Enabled** radio button → OK.
5. Close the editor.
6. Back in **Group Policy Management**, click (single-click, don't right-click) the `restrict control panel` GPO under manila.com so it's highlighted.
7. In the right pane, click the **Delegation** tab (top of the right pane).
8. Click the **Advanced…** button at the bottom right of the Delegation tab. A Security Settings dialog opens.
9. Click **Add…** → type `Executive` → click **Check Names** → OK. `Executive` is now in the list.
10. Click **Executive** so it's highlighted. In the lower box, find the row **Apply group policy** → tick the box in the **Deny** column.
11. Click **OK**. Windows warns about "Deny entries take precedence" — click **Yes**.

**Why "Deny Apply"?** Because the policy targets everyone by default (Authenticated Users), an explicit Deny is the easiest way to carve out the Executive group without breaking other GPOs.

---

## Task 6 — GPO `disabled add and remove program panel` (Executive ONLY)

> PDF p.11: *"does not allow executive group to use control panel to add new program, uninstall or change a program"*

This GPO is the opposite of task 5 — it applies **only** to Executive.

### GUI path
1. In **Group Policy Management** → right-click **manila.com** → **Create a GPO in this domain, and Link it here…** → Name = `disabled add and remove program panel` → OK.
2. Right-click the new GPO → **Edit…**
3. In the editor expand: **User Configuration** → **Policies** → **Administrative Templates** → **Control Panel** → click **Programs**.
4. In the right pane:
   - Double-click **Hide "Programs and Features" page** → **Enabled** → OK.
   - If you see **Prevent uninstall, change or repair from "Programs and Features"** → Enabled → OK.
5. Still in the editor, navigate to **User Configuration** → **Policies** → **Administrative Templates** → **Control Panel** → **Add or Remove Programs** (if this node exists on your build):
   - Double-click **Remove Add or Remove Programs** → **Enabled** → OK.
6. Close the editor.
7. Back in **Group Policy Management**, single-click the GPO so it's highlighted, then click the **Scope** tab in the right pane.
8. Under **Security Filtering** at the bottom, you'll see `Authenticated Users`. Click it → click **Remove** → **OK** to confirm.
9. Click **Add…** → type `Executive` → **Check Names** → OK.
10. Now click the **Delegation** tab → **Add…** → type `Authenticated Users` → Check Names → OK. In the permission dialog choose **Read** → OK.

> Step 10 is required: post-2016 Windows refuses to process a GPO if Authenticated Users can't even **read** it (Microsoft hardened this after MS16-072). Read-only doesn't apply the policy, but lets the client see it exists.

---

## Task 7 — GPO `autolock` (10s screen, Executive only)

> PDF p.11: *"auto lock screen after 10 seconds of inactivity – only applicable to the executive group"*

### GUI path
1. In **Group Policy Management** → right-click **manila.com** → **Create a GPO in this domain, and Link it here…** → Name = `autolock` → OK.
2. Right-click the new GPO → **Edit…**
3. In the editor expand: **User Configuration** → **Policies** → **Administrative Templates** → **Control Panel** → click **Personalization**.
4. In the right pane, double-click each and set:
   - **Enable screen saver** → **Enabled** → OK.
   - **Password protect the screen saver** → **Enabled** → OK.
   - **Screen saver timeout** → **Enabled** → "Number of seconds to wait..." → type `10` → OK.
   - **Force specific screen saver** → **Enabled** → "Screen saver executable name" → type `scrnsave.scr` → OK.
5. Close the editor.
6. Back in **Group Policy Management**, single-click the `autolock` GPO → **Scope** tab → under **Security Filtering**:
   - Click **Authenticated Users** → **Remove** → OK.
   - Click **Add…** → type `Executive` → Check Names → OK.
7. Click the **Delegation** tab → **Add…** → type `Authenticated Users` → OK → choose **Read** in the permission dropdown → OK.

### Verify
Log on Client2 as M004 (Executive) → wait 10 seconds → screen should lock and require password.

---

## Task 8 — GPO `certenroll` (auto-enrollment of certificates)

> PDF p.11: *"computers on the domain will automatically receive a certificate from the issuing CA through application of the GPO. These GPO's should be set to autoenroll."*

### GUI path
1. In **Group Policy Management** → right-click **manila.com** → **Create a GPO in this domain, and Link it here…** → Name = `certenroll` → OK.
2. Right-click the new GPO → **Edit…**
3. In the editor, expand: **Computer Configuration** → **Policies** → **Windows Settings** → **Security Settings** → click **Public Key Policies**.
4. In the right pane, double-click **Certificate Services Client – Auto-Enrollment**:
   - **Configuration Model** dropdown → **Enabled**
   - Tick ✓ **Renew expired certificates, update pending certificates, and remove revoked certificates**
   - Tick ✓ **Update certificates that use certificate templates**
   - Click **OK**.
5. Now do the same under the **User Configuration** side: expand **User Configuration** → **Policies** → **Windows Settings** → **Security Settings** → click **Public Key Policies** → double-click **Certificate Services Client – Auto-Enrollment** → same three settings → OK.
6. Close the editor.
7. To verify on Client1: open **Command Prompt** → run `gpupdate /force` and then `certutil -pulse`. Within a minute, open Start → type **"Manage computer certificates"** → click the result. Under **Personal → Certificates** you should see a new machine cert issued by WINSRV3.

---

## Task 8B — GPO `google` (Chrome home page = www.manila.com, locked)

> **Important — this GPO is NOT in the PDF tasks list, but the MARKING SHEET tests for it explicitly.** Worth ~0.7 marks across A4 + A7 (home page set, GPO named "google", locked from change).

> Marking-sheet quote: *"verify that a google policy exists at the domain level and is set to control the homepage… setting at: computer configuration > administrative templates > google > startup, home page and new tab page > configure the home page URL > www.manila.com"*

> The grader test is: on Client2, open Chrome → home page must be `www.manila.com`. Try to change it via Chrome settings → it should be greyed out / revert on reopen.

### Two ways to do it — pick the one that works on your server

#### Option A — If Chrome ADMX templates are already on WINSRV1 (preferred — matches the marking-sheet wording exactly)

1. Quick check first: open **File Explorer** → browse to `C:\Windows\PolicyDefinitions\`. Look for `chrome.admx` (or `google.admx`). If present → use this option. If not → use Option B.
2. In **Group Policy Management** → right-click **manila.com** → **Create a GPO in this domain, and Link it here…** → Name = `google` → OK.
3. Right-click the new GPO → **Edit…**
4. In the editor, expand: **Computer Configuration** → **Policies** → **Administrative Templates** → **Google** → **Google Chrome** → **Startup, Home page and new tab page**.
5. In the right pane:
   - Double-click **Configure the home page URL** → **Enabled** → in the "Home page URL" box type `https://www.manila.com` → OK.
   - Double-click **Use New Tab Page as homepage** → **Disabled** → OK.
   - Double-click **Action on startup** → **Enabled** → dropdown → **Open a list of URLs** → OK.
   - Double-click **URLs to open on startup** → **Enabled** → click **Show…** → row 1 → `https://www.manila.com` → OK → OK.
6. Close the editor.

#### Option B — If Chrome ADMX is missing (registry-based — works without any template install)

This pushes the same Chrome policy registry keys that the ADMX template would push. Chrome reads them identically.

1. In **Group Policy Management** → right-click **manila.com** → **Create a GPO in this domain, and Link it here…** → Name = `google` → OK.
2. Right-click the new GPO → **Edit…**
3. In the editor, expand: **Computer Configuration** → **Preferences** → **Windows Settings** → right-click **Registry** → **New** → **Registry Item**.
4. Fill in:
   - **Action:** Update
   - **Hive:** HKEY_LOCAL_MACHINE
   - **Key Path:** `Software\Policies\Google\Chrome`
   - **Value name:** `HomepageLocation`
   - **Value type:** REG_SZ
   - **Value data:** `https://www.manila.com`
   - OK.
5. Repeat **New → Registry Item** for each row below (same Hive and Key Path):

   | Value name | Value type | Value data |
   |------------|-----------|------------|
   | `HomepageIsNewTabPage` | REG_DWORD | `0` |
   | `ShowHomeButton` | REG_DWORD | `1` |
   | `RestoreOnStartup` | REG_DWORD | `4` |

6. Now add the startup URL list. Right-click **Registry** → **New** → **Registry Item**:
   - **Hive:** HKEY_LOCAL_MACHINE
   - **Key Path:** `Software\Policies\Google\Chrome\RestoreOnStartupURLs`
   - **Value name:** `1`
   - **Value type:** REG_SZ
   - **Value data:** `https://www.manila.com`
   - OK.
7. Close the editor.

### Verify
1. On Client2, open **Command Prompt** → run `gpupdate /force` → wait for "successfully updated".
2. Open Chrome → it should open to `www.manila.com`.
3. Click the 3-dot menu → **Settings** → search for "home" → the Home page URL field should be **greyed out** (locked by policy).
4. On Client2 run `gpresult /r` in CMD → under "Applied Group Policy Objects" you should see `google`.

> If Chrome was already running on Client2 with a custom home page, close ALL Chrome windows, then `gpupdate /force`, then reopen Chrome.

---

## Task 9 — Share `\\WINSRV1\pictures` with NTFS + share permissions

> PDF p.12: share `pictures` at `C:\shares\pictures` — Marketing = R, Executive = FC, no one else.

### GUI path (Server Manager wizard)
1. **Make the folder using File Explorer:**
   - Open **File Explorer** (yellow folder icon on the taskbar, or Windows+E).
   - Click **This PC** in the left pane → double-click **Local Disk (C:)**.
   - Right-click in empty space → **New** → **Folder** → name it `shares` → Enter.
   - Double-click `shares` to enter it → right-click empty space → **New** → **Folder** → name it `pictures` → Enter.
2. **Open the share wizard:**
   - Open **Server Manager**. In the left sidebar click **File and Storage Services**.
   - In the new view, click **Shares** in the second column.
   - On the right under TASKS dropdown → click **New Share…**
3. **Select Profile:** click **SMB Share – Quick** → click **Next**.
4. **Share location:**
   - Choose **Type a custom path** → click **Browse…** → expand C:\ → click `shares` → click `pictures` → click **Select Folder**.
   - Click **Next**.
5. **Share name:** make sure it says `pictures` (auto-filled) → click **Next**.
6. **Other settings:** leave defaults (Enable access-based enumeration is a nice-to-have to tick) → click **Next**.
7. **Permissions:** click the **Customize permissions…** button. A "Advanced Security Settings for pictures" window opens.

   **Set Share permissions first:**
   - Click the **Share** tab (top of that window).
   - Click **Everyone** in the list → click **Remove**.
   - Click **Add** → **Select a principal** → type `Executive` → Check Names → OK → tick **Full Control** → OK.
   - Click **Add** → **Select a principal** → type `Marketing` → Check Names → OK → tick **Read** (already ticked by default) → OK.

   **Then set NTFS permissions:**
   - Click the **Permissions** tab.
   - Click **Disable inheritance** → choose **Convert inherited permissions into explicit permissions on this object**.
   - Click `Users` in the list → **Remove**. Keep `SYSTEM` and `Administrators` (they show Full control).
   - Click **Add** → **Select a principal** → type `Executive` → OK → tick **Full control** → OK.
   - Click **Add** → **Select a principal** → type `Marketing` → OK → tick **Read & execute** + **List folder contents** + **Read** → OK.
   - Click **OK** on the Advanced Security Settings window.
8. Back in the wizard click **Next** → **Create**. When it says "Successful," click **Close**.

### Why NTFS + share both?
Best practice = **tightest of either applies**. Share perms are evaluated for remote access; NTFS for everything. Graders reward you for not leaving NTFS wide open even when share is tight.

### Verify
```powershell
Get-SmbShare pictures | fl Name, Path, FolderEnumerationMode
Get-SmbShareAccess pictures
(Get-Acl C:\shares\pictures).Access | ft IdentityReference, FileSystemRights, AccessControlType
```

---

## Task 10 — Audit reads on `park.jpg`

> PDF p.12: *"set auditing on this file so it is logged when read by a member of any group"*

### Confirm `park.jpg` exists
Open **File Explorer** → browse to `C:\shares\pictures\`. You should see `park.jpg`. If it isn't there, find any small `.jpg` (right-click → Copy from any other folder) and paste it into `C:\shares\pictures\` with the name `park.jpg`. (The PDF says it's pre-provided.)

### GUI path for the auditing rule on the file
1. In **File Explorer**, browse to `C:\shares\pictures\`.
2. Right-click **`park.jpg`** → **Properties** → click the **Security** tab → click **Advanced** at the bottom.
3. In the Advanced Security Settings window, click the **Auditing** tab (top). If prompted by UAC click **Continue**.
4. Click **Add** at the bottom-left. The "Auditing Entry" dialog opens.
5. Click the blue link **Select a principal** at the top → type `Everyone` → **Check Names** → OK.
6. **Type** dropdown → **Success**.
7. **Applies to** dropdown → **This folder, subfolders and files** (or just **This object only** since it's a file).
8. Click **Show advanced permissions** (link on the right side). Now tick: ✓ **Read data**, ✓ **Read attributes**, ✓ **Read extended attributes**.
9. Click **OK** to close Auditing Entry → **OK** to close Advanced Security Settings → **OK** to close Properties.

### Turn on the audit category at the DC level (do this via GPO so it survives reboot)
1. In **Group Policy Management** (Server Manager → Tools → Group Policy Management): expand **Forest → Domains → manila.com → Domain Controllers**.
2. Right-click **Default Domain Controllers Policy** → **Edit…**.
3. In the editor expand: **Computer Configuration** → **Policies** → **Windows Settings** → **Security Settings** → **Advanced Audit Policy Configuration** → **Audit Policies** → click **Object Access**.
4. In the right pane, double-click **Audit File System** → tick **Configure the following audit events** → tick **Success** → OK.
5. Close the editor.
6. Open **Command Prompt** as Administrator (Start → type `cmd` → right-click → Run as administrator) → run `gpupdate /force`.

### Verify
1. On **Client2**, log in as **M001** (password `P@ssw0rd`).
2. Click Start → in the search box type `\\winsrv1\pictures\park.jpg` → Enter (or open File Explorer and paste that in the address bar). The image should open.
3. On **WINSRV1**, open **Server Manager** → **Tools** menu → **Event Viewer** → expand **Windows Logs** → click **Security**.
4. In the right "Actions" pane click **Filter Current Log…** → in **Event IDs** type `4663` → OK.
5. You should see a recent 4663 event where "Object Name" contains `park.jpg`.

---

## Final step — push to clients

After ALL GPOs above are created and linked:

```cmd
gpupdate /force
```

On WINSRV1, then on each Client1, Client2, Client3. Sign out and sign in again — most user-targeted GPOs (banner, autolock, restrict CP) need a logoff to fully apply.

---

## "Did everything stick?" quick visual check on WINSRV1

| Check | Where to look (clicks) | What you should see |
|-------|------------------------|---------------------|
| All GPOs created | Server Manager → Tools → **Group Policy Management** → expand Forest → Domains → manila.com → **Group Policy Objects** | A row for each: `Banner`, `autolock`, `certenroll`, `disabled add and remove program panel`, `google`, `lockout`, `restrict control panel`, plus the two defaults. |
| All GPOs linked at the domain | Group Policy Management → click **manila.com** in the tree → look at the right pane | Each of the **7** new GPOs listed as linked, **Link Enabled = Yes**. |
| Fine-Grained Password Policy | Server Manager → Tools → **Active Directory Administrative Center** → Tree View → manila (local) → System → **Password Settings Container** | `ExecutivePSO` listed. |
| Share exists | Server Manager → **File and Storage Services** → **Shares** | A row "pictures" with path `C:\shares\pictures`. |
| File audit on park.jpg | File Explorer → right-click `C:\shares\pictures\park.jpg` → Properties → Security → Advanced → Auditing tab | A Success entry for "Everyone" / Read data. |
| DC audit category enabled | Server Manager → Tools → **Event Viewer** → Windows Logs → Security → Filter "4663" | At least one 4663 event after a test read. |
