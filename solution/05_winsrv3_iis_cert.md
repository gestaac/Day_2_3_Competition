# WINSRV3 — IIS HTTPS site `webtest.manila.com` with a CA-issued cert

> Run on **WINSRV3** (192.168.2.30) as Administrator. WINSRV3 is the Issuing CA (subordinate). WINSRV1 holds DNS.

## Goal
- IIS website **`webtest.manila.com`** on WINSRV3, port 443, HTTPS only.
- Certificate issued by **WINSRV3's CA** (so the chain is WINSRV3 ← WINSRV4 root). Internal clients trust this because of the `certenroll` GPO.
- WINSRV1 DNS has `webtest.manila.com → 192.168.2.30`.
- From Client2 Chrome → `https://webtest.manila.com` loads with **no cert warning**.

---

## Step 1 — Make sure IIS is installed

1. On WINSRV3, open **Server Manager** (Start → Server Manager tile).
2. Top-right corner click **Manage** → **Add Roles and Features**.
3. Click **Next** through the first screens (Before You Begin → Installation Type → Server Selection — accept defaults).
4. **Server Roles** page → scroll and tick **Web Server (IIS)**. A pop-up asks "Add features that are required for Web Server (IIS)?" → click **Add Features**.
5. Click **Next** → **Next** → **Next** until you reach Confirm → click **Install**.
6. When complete, click **Close**. You'll see a notification flag in Server Manager top-right.

> If "Web Server (IIS)" is already shown as installed (the tick already filled in), just click **Cancel** — nothing to do.

## Step 2 — Create the site folder and a tiny home page

1. Open **File Explorer** (yellow folder on taskbar).
2. In the address bar at the top, type `C:\inetpub\wwwroot\` and press Enter.
3. Right-click empty space → **New** → **Folder** → name it `webtest` → Enter.
4. Double-click `webtest` to enter it.
5. Right-click empty space → **New** → **Text Document** → name it `index.html` (Windows will warn about changing the extension → click **Yes**).
6. Right-click `index.html` → **Open with** → **Notepad**.
7. Paste in:
   ```html
   <h1>webtest.manila.com</h1>
   <p>IIS on WINSRV3, cert from WINSRV3 CA.</p>
   ```
8. **File → Save** → close Notepad.

## Step 3 — Request a Web Server certificate from this server's own CA

> WINSRV3 is the CA, so it can issue its own cert. The `WebServer` template is published by default in AD CS.

### GUI path (easier to grade — this is the one graders expect you to know)

**Open the Computer Certificates console:**
1. Click **Start** → start typing `Manage computer certificates`.
2. Click the matching result. The "certlm" window opens (no need to remember that name — you searched for the friendly title).

**Request the certificate:**
3. In the left tree, expand **Certificates - Local Computer** → click **Personal**.
4. Right-click the **Personal** folder (or, if it has a `Certificates` sub-folder, right-click that) → **All Tasks** → **Request New Certificate…**
5. **Before You Begin** screen → click **Next**.
6. **Select Certificate Enrollment Policy** screen → leave **Active Directory Enrollment Policy** selected → **Next**.
7. **Request Certificates** screen → tick the box next to **Web Server**.
8. Underneath the Web Server row a yellow warning shows: **More information is required to enroll for this certificate. Click here to configure settings.** Click that link. The "Certificate Properties" window opens.
9. On the **Subject** tab:
   - Left side **Subject name** → **Type** dropdown → **Common name** → in **Value** type `webtest.manila.com` → click **Add >**.
   - Right side **Alternative name** → **Type** dropdown → **DNS** → in **Value** type `webtest.manila.com` → click **Add >**.
10. Click the **General** tab → **Friendly name** = `webtest.manila.com`.
11. Click the **Private Key** tab → expand **Key options** → tick **Make private key exportable**.
12. Click **OK** to close Certificate Properties.
13. Back at the Request Certificates window, click **Enroll**.
14. After a moment it should say **STATUS: Succeeded** → click **Finish**.

You should now see the certificate listed under **Personal → Certificates** with Issued To = `webtest.manila.com`.

A new cert should appear under Personal → Certificates.

### PowerShell path (fast)
```powershell
$cert = Get-Certificate -Template "WebServer" `
           -DnsName "webtest.manila.com" `
           -SubjectName "CN=webtest.manila.com" `
           -CertStoreLocation Cert:\LocalMachine\My
$cert.Certificate.Thumbprint     # note the thumbprint
```

> **If "Web Server" doesn't appear** in the Request Certificates list, the template isn't published for this server yet. Fix it like this:
> 1. Server Manager → **Tools** menu → **Certification Authority**. (This is your CA console.)
> 2. In the left tree, expand your CA name → right-click **Certificate Templates** (the folder) → **Manage**. This opens the Certificate Templates console.
> 3. In the right pane scroll to **Web Server** → right-click → **Properties**.
> 4. Click the **Security** tab → click **Domain Computers** (add it if missing) → tick **Enroll** under Allow → OK.
> 5. Close the Templates console. Back in Certification Authority → right-click **Certificate Templates** → **New** → **Certificate Template to Issue** → pick **Web Server** → OK.
> 6. Open **Command Prompt as Administrator** → run `certutil -pulse` to refresh, then retry step 3 above.

## Step 4 — Create the IIS site and bind the cert

### GUI path
1. Open **Server Manager** → **Tools** menu → click **Internet Information Services (IIS) Manager**. The IIS Manager window opens.
2. In the left **Connections** pane, expand **WINSRV3 (MANILA\Administrator)** (or whatever your server name is). You should see two items underneath: **Application Pools** and **Sites**.
3. Right-click **Sites** → **Add Website…** The Add Website dialog opens.
4. Fill in:
   - **Site name:** `webtest`
   - **Application pool:** (auto-fills to "webtest" — leave it)
   - **Physical path:** click the **…** button → browse to `C:\inetpub\wwwroot\webtest` → OK.
   - Under **Binding** section:
     - **Type:** `http`
     - **IP address:** `All Unassigned`
     - **Port:** `80`
     - **Host name:** `webtest.manila.com`
5. Click **OK** at the bottom. The site appears in the left tree.

**Now add the HTTPS binding:**
6. In the left pane, click the new **webtest** site so it's highlighted.
7. In the right **Actions** pane click **Bindings…** → the Site Bindings dialog opens.
8. Click **Add…**:
   - **Type:** `https` (the dialog changes to show SSL options)
   - **IP address:** `All Unassigned`
   - **Port:** `443`
   - **Host name:** `webtest.manila.com`
   - Tick ✓ **Require Server Name Indication**
   - **SSL certificate** dropdown → select **webtest.manila.com** (the cert you enrolled in step 3).
9. Click **OK** → **Close**.
10. To confirm the site is running, click **webtest** in the left pane → in the right Actions pane look at "Manage Website" → **Start** (if it shows Start) or "Restart" if running.

### PowerShell path
```powershell
Import-Module WebAdministration

# Remove if exists, then create
if (Get-Website "webtest" -ErrorAction SilentlyContinue) { Remove-Website "webtest" }
New-Website -Name "webtest" `
            -PhysicalPath "C:\inetpub\wwwroot\webtest" `
            -HostHeader "webtest.manila.com" `
            -Port 80

# Add HTTPS binding with the issued cert
New-WebBinding -Name "webtest" -Protocol "https" -Port 443 `
               -HostHeader "webtest.manila.com" -SslFlags 1
$b = Get-WebBinding -Name "webtest" -Protocol "https"
$b.AddSslCertificate($cert.Certificate.Thumbprint, "My")
Start-Website "webtest"
```

## Step 5 — Add the DNS record on WINSRV1

The cert is bound to the hostname `webtest.manila.com`, but a client still needs DNS to translate that to `192.168.2.30`.

### Do this on **WINSRV1** (the DC):

**GUI (click path on WINSRV1):**
1. Log on to WINSRV1 → open **Server Manager** → **Tools** menu → click **DNS**. The DNS Manager opens.
2. In the left tree expand **WINSRV1** → **Forward Lookup Zones** → click **manila.com**.
3. Right-click in the empty area on the right side (where existing records like `(same as parent folder)` are listed) → click **New Host (A or AAAA)…**
4. Fill in the New Host dialog:
   - **Name:** `webtest` (just the host part — the zone "manila.com" auto-appends)
   - **IP address:** `192.168.2.30`
   - (Optional) Tick **Create associated pointer (PTR) record**.
5. Click **Add Host** → it should say "successfully created" → click **Done**.

**PowerShell:**
```powershell
Add-DnsServerResourceRecordA -ZoneName "manila.com" -Name "webtest" `
                             -IPv4Address "192.168.2.30" -TimeToLive 01:00:00
```

**Verify from Client2:**
1. On Client2, click **Start** → type `cmd` → Enter to open Command Prompt.
2. Type `nslookup webtest.manila.com 192.168.2.10` → Enter.
3. Should answer with `Address: 192.168.2.30`.

## Step 6 — End-to-end test from Client2

1. On Client2, open **Command Prompt** (Start → type `cmd` → Enter) and run `gpupdate /force` → wait until it says "successfully updated". This makes sure the `certenroll` GPO has run, which puts the root CA into the Trusted Root store.
2. Open **Chrome** → in the address bar type `https://webtest.manila.com` → Enter.
3. **Expected:** the page loads, you see a padlock icon (no red warning).
4. Click the **padlock icon** in the address bar → click **Connection is secure** → **Certificate is valid**.
5. In the certificate window switch to the **Details** tab and click the **Certification Path** tab (or in newer Chrome the cert opens directly to a chain view) → you should see:
   ```
   manila Root CA           (WINSRV4)
    └─ manila Issuing CA    (WINSRV3)
         └─ webtest.manila.com
   ```

If you see a cert warning, the most common causes:
- `certenroll` GPO didn't apply to Client2. Open **Command Prompt** on Client2 → run `gpresult /r` → look for `certenroll` under "Applied Group Policy Objects". If missing, run `gpupdate /force` and reboot.
- Root CA cert isn't in Client2's Trusted Root store. To check: Start → type **Manage computer certificates** → click result → expand **Trusted Root Certification Authorities → Certificates** → look for `manila Root CA` (or whatever WINSRV4 is named). If missing, import the root `.cer` manually.
- Hostname mismatch — cert CN is `webtest.manila.com` but you're hitting the URL by IP. Always use the hostname.

---

## Why this step matters
Marking aspect A5: **"CA Check — will show certs issued for users/computers"** + the A7 client-side check **"check certificate enrollment — open chrome go to https://webtest.manila.com — no certificate warning should show — when checking the chain of the certificate, whole chain should be present, including WINSRV4"**. These are easy points if `certenroll` is right.
