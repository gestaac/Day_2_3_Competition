# Deliverable — Combine into ONE .docx and save to the Desktop with your country code as the filename

> The PDF says you must submit a single answer document with:
> 1. **Executive Summary** (from MA1 morning vulnerability assessment).
> 2. **3 additional GPO recommendations** in the table below (this section).
>
> Below are filled-in suggestions that you can lift directly. Pick the **three you can defend orally** — graders sometimes ask "why this and not X".

---

## Section A — Executive Summary template (paste into doc, fill in your findings)

> Replace italicised hints with what you actually found during MA1.

**Executive Summary — Apache web server vulnerability assessment (LINSRV1 — MA1)**

During the morning assessment we performed a configuration audit of the Apache `httpd` service hosting `www.manila.com` and the supporting OS. The two most significant findings, ranked by business risk, are:

1. **TLS version not restricted in ssl.conf** — `SSLProtocol` is left at the default, which still permits TLS 1.0 / 1.1 negotiation. *Severity 7 / Risk High. Why a problem:* Compliance and downgrade-attack exposure; vulnerable cipher suites can be negotiated. *Mitigation:* Set `SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1` and pin `SSLHonorCipherOrder on` in the vhost.
2. **LDAP authentication used in cleartext (no LDAPS)** — directory queries from the host carry credentials in plaintext. *Severity 8 / Risk High. Why a problem:* Any network observer in DMZ can capture creds. *Mitigation:* Re-bind sssd to LDAPS:636 against WINSRV1 using the AD CS CA chain.

Additional notable findings — included on the recommendations table:

3. SELinux was previously not enforcing — re-enabled and `httpd_sys_content_t` labels applied to `/var/www/manila`.
4. Apache runs as default `apache` user — acceptable; consider a service-scoped account for stricter separation.
5. File / folder permissions on `/var/www` were world-readable; tightened to `apache:apache 0750`.
6. Default Apache `ServerTokens` / `ServerSignature` were leaking version banner; set `ServerTokens Prod` and `ServerSignature Off`.

| # | Description | Severity (0-10) | Risk (L/M/H/Crit) | Why is this a problem? | Mitigation Recommendation |
|---|-------------|-----------------|-------------------|------------------------|---------------------------|
| 1 | `SSLProtocol` undefined → TLS 1.0/1.1 accepted | 7 | High | Allows downgrade to known-weak protocols; fails PCI/HIPAA TLS requirements | Set `SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1` and disable weak ciphers (`SSLCipherSuite HIGH:!aNULL:!MD5`) |
| 2 | LDAP in cleartext (port 389, not 636) | 8 | High | Credentials & directory data visible on the wire — DMZ host = exposure | Switch sssd to LDAPS:636, distribute AD CS root via the `certenroll` GPO so the chain is trusted |
| 3 | SELinux disabled / permissive on initial state | 6 | Medium | Apache compromise would not be contained by MAC layer | `setenforce 1`, `SELINUX=enforcing` in `/etc/selinux/config`, `restorecon -R /var/www/manila` |

---

## Section B — Three additional GPO recommendations (the table the PDF asks for)

Pick **three** of the four below to fill the table. Reasoning column matters more than the policy name — graders look for "could you defend this choice over alternatives".

### Option 1 — Disable LLMNR + NetBIOS (NBT-NS)

| Name of Policy | Recommended Path to Setting | Effects of Applying this GPO | Why selected over other choices |
|----------------|-----------------------------|-------------------------------|----------------------------------|
| **Turn off Multicast Name Resolution** + **NetBT NodeType = P-node** | Computer Configuration → Policies → Administrative Templates → Network → DNS Client → "Turn off multicast name resolution" = **Enabled**. NetBIOS via DHCP options or Registry: `HKLM\System\CurrentControlSet\Services\NetBT\Parameters\NodeType = 2`. | Stops Windows from broadcasting LLMNR (UDP 5355) and NBT-NS (UDP 137) name queries on the LAN. | Kills the entire class of "Responder"-style credential-theft attacks that dominate internal pentests. Cheaper than full SMB signing rollout and has near-zero application impact in an AD-DNS environment where every machine should be using `192.168.2.10` for resolution. |

### Option 2 — Disable SMBv1 (client and server)

| Name of Policy | Recommended Path to Setting | Effects of Applying this GPO | Why selected over other choices |
|----------------|-----------------------------|-------------------------------|----------------------------------|
| **Configure SMBv1 client/server = Disabled** | Computer → Preferences → Windows Settings → Registry: <br>`HKLM\System\CurrentControlSet\Services\mrxsmb10\Start = 4`<br>`HKLM\System\CurrentControlSet\Services\LanmanServer\Parameters\SMB1 = 0` | Removes SMB1 entirely; only SMB2+ negotiation is possible. | Closes the WannaCry / EternalBlue family (CVE-2017-0143 etc.) at the protocol layer. Modern Windows 10 / Server 2022 clients never need SMB1. Preferable to relying on IDS signature for SMB1 because it removes the exploit surface instead of detecting after the fact. |

### Option 3 — AppLocker Default Rules + Block executables from temp paths

| Name of Policy | Recommended Path to Setting | Effects of Applying this GPO | Why selected over other choices |
|----------------|-----------------------------|-------------------------------|----------------------------------|
| **AppLocker — Executable rules: default rules + deny `%TEMP%`, `%APPDATA%`** | Computer → Policies → Windows Settings → Security Settings → Application Control Policies → AppLocker → Executable Rules | Allows only signed/trusted binaries; blocks the standard malware drop directories (`%LOCALAPPDATA%\Temp`, `%APPDATA%\Roaming`). | Defeats most commodity ransomware loaders without needing to deploy an EDR product. Chosen over **Software Restriction Policies** (SRP) because SRP is deprecated and AppLocker supports publisher/path/hash rules and an Audit-only enforcement mode for safe rollout. |

### Option 4 — Audit policy: Logon Success/Failure + Object Access Success

| Name of Policy | Recommended Path to Setting | Effects of Applying this GPO | Why selected over other choices |
|----------------|-----------------------------|-------------------------------|----------------------------------|
| **Advanced Audit Policy** — Account Logon (Success+Failure), Logon/Logoff (Success+Failure), Object Access (Success) | Computer → Policies → Windows Settings → Security Settings → Advanced Audit Policy Configuration → Audit Policies | Generates Event IDs 4624, 4625, 4663, 4672 etc., enabling SIEM correlation and the file-read auditing required by this project (park.jpg). | Selected over the legacy "Audit Policy" node because **only** Advanced Audit Policy respects sub-category settings — the legacy policy gets overridden silently on Server 2008+. Required for our auditing on `park.jpg` to actually log. |

---

## Section C — File naming & where to save

- Combine Section A + the chosen three rows from Section B (and any other answers the project asks for) into **one** file.
- Save as `.docx` (Word) on the **competitor laptop Desktop**.
- Filename = your **country code** (e.g. `PH.docx`, `SG.docx`, `VN.docx`). The PDF makes this mandatory.
- Tell the experts where the file is **before you leave the room**.
