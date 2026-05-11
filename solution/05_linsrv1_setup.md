# LINSRV1 — DMZ Linux setup walkthrough (Rocky / Alma / RHEL 9)

> Connect to LINSRV1 console as `root` / `P@ssw0rd`. After Task 5 (SSH on 2022) you can switch to PuTTY from Client1 if it's more comfortable.

## What you will do (10 tasks)

| # | Task | Mark |
|---|------|------|
| 1 | DNS to WINSRV1 | (enables 2) |
| 2 | Join the `manila.com` domain | 0.25 |
| 3 | sudo for IT group (C1, C2) | 0.25 |
| 4 | SSH on 2022, no root, only C1/C2, max 3 attempts | 0.25 |
| 5 | firewalld on, lock to 2022/http/https/kerberos | 0.4 + 0.25 |
| 6 | Password complexity + age (chage warnings) | 0.75 |
| 7 | Apache HTTPS for `www.manila.com` | 0.4 |
| 8 | SELinux enforcing + httpd contexts | 0.4 + 0.25 |
| 9 | Limit website to domain users (PAM auth) | 0.4 |
| 10 | Cert from WINSRV3 instead of self-signed | bonus |

---

## Step 0 — Identify your NIC

```bash
ip -o -4 route show to default
```

It usually says `default via 192.168.1.254 dev ens160 ...`. Note the device name (`ens160`, `eth0`, etc.) — you'll use it in step 1.

---

## Step 1 — DNS pointing at WINSRV1

Replace `ens160` with whatever you got in step 0.

```bash
nmcli con mod ens160 ipv4.dns 192.168.2.10
nmcli con mod ens160 ipv4.dns-search manila.com
nmcli con mod ens160 ipv4.ignore-auto-dns yes
nmcli con up   ens160
```

**Why:** Realm join (next step) uses DNS SRV records to find the domain controller. If DNS isn't pointing at WINSRV1, `realm join` fails with "Couldn't discover domain".

**Verify:**
```bash
cat /etc/resolv.conf            # should list nameserver 192.168.2.10
host manila.com                 # should resolve to 192.168.2.10
host _ldap._tcp.manila.com      # should return SRV records
```

---

## Step 2 — Sync the clock (Kerberos needs it)

```bash
dnf -y install chrony
systemctl enable --now chronyd
chronyc sources
```

**Why:** Kerberos refuses tickets if your clock is more than 5 minutes off the DC. New VMs from a paused snapshot are often skewed badly.

---

## Step 3 — Join the domain

Install the realm stack:
```bash
dnf -y install realmd sssd oddjob oddjob-mkhomedir adcli samba-common-tools \
               krb5-workstation policycoreutils-python-utils
```

Then join:
```bash
realm join -U Administrator manila.com
```

It will prompt for the AD Administrator password → `P@ssw0rd`.

**Activate home-dir auto-creation:**
```bash
authselect select sssd with-mkhomedir --force
systemctl enable --now oddjobd
```

**Use short usernames** (so the grader can type `C1` not `C1@manila.com`):
```bash
sed -i 's/^use_fully_qualified_names = .*/use_fully_qualified_names = False/' /etc/sssd/sssd.conf
sed -i 's|^fallback_homedir = .*|fallback_homedir = /home/%u|'                /etc/sssd/sssd.conf
systemctl restart sssd
```

**Verify:**
```bash
realm list                       # should show manila.com / configured
id C1                            # should return uid + groups including "domain users", "IT"
```

### Fallback — if `realm join` keeps failing

> PDF p.12: *"If domain integration fails, create local users C1 and C2 matching the expected credentials."* — this is the official fallback. You **still get most of the A3 marks** with local users; you only lose the "domain joined" specific aspect (~0.4 mark out of 3 for the whole LINSRV1 block).

If domain join keeps failing after 10 minutes of trying, switch to local users:

```bash
# Create local C1, C2 with the same password the project uses
useradd -m -s /bin/bash C1
useradd -m -s /bin/bash C2
echo "C1:P@ssw0rd" | chpasswd
echo "C2:P@ssw0rd" | chpasswd

# Create a local IT group and add them
groupadd IT
usermod -aG IT C1
usermod -aG IT C2
```

Steps 4–9 below still work — sudoers, SSH, firewall, password policy, httpd all apply the same. The only change: in `/etc/pam.d/httpd` (Step 8) keep `pam_sss.so` but also add fallback to local PAM:
```
auth      sufficient   pam_sss.so
auth      sufficient   pam_unix.so
account   sufficient   pam_sss.so
account   sufficient   pam_unix.so
```

Tell the grader you used the fallback — they explicitly allow this path.

---

## Step 4 — Sudo only for IT group (C1, C2)

```bash
cat > /etc/sudoers.d/it-admins <<'EOF'
%IT ALL=(ALL) ALL
C1  ALL=(ALL) ALL
C2  ALL=(ALL) ALL
EOF
chmod 440 /etc/sudoers.d/it-admins
visudo -c -f /etc/sudoers.d/it-admins
```

The last command **syntax-checks** the file. If you see "parsed OK", you're good. If not, fix typos before logging out (otherwise sudo is broken).

**Why both `%IT` and explicit `C1`/`C2`?** Belt + braces. If the group lookup fails for any reason, the explicit user entries still work.

**Verify** (after step 5 — once SSH works):
```bash
# As C1
sudo useradd fred          # should succeed
# As M001 (Marketing user)
sudo useradd bar           # should be DENIED — "user is not in the sudoers file"
```

---

## Step 5 — Harden SSH

Back up first (one-time):
```bash
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.orig
```

Edit `/etc/ssh/sshd_config`. You can do it with `nano` or `vi`, or fast with `sed`:

```bash
sed -i 's/^#\?Port .*/Port 2022/'                               /etc/ssh/sshd_config
sed -i 's/^#\?PermitRootLogin .*/PermitRootLogin no/'           /etc/ssh/sshd_config
sed -i 's/^#\?MaxAuthTries .*/MaxAuthTries 3/'                  /etc/ssh/sshd_config
sed -i '/^AllowUsers /d' /etc/ssh/sshd_config
echo "AllowUsers C1 C2" >> /etc/ssh/sshd_config
```

Tell SELinux that ssh now uses 2022:
```bash
semanage port -a -t ssh_port_t -p tcp 2022 2>/dev/null || \
semanage port -m -t ssh_port_t -p tcp 2022
```

Restart:
```bash
systemctl restart sshd
ss -tlnp | grep sshd       # should show *:2022
```

**Verify the four settings:**
```bash
grep -E "^(Port|PermitRootLogin|AllowUsers|MaxAuthTries)" /etc/ssh/sshd_config
```
Expected:
```
Port 2022
PermitRootLogin no
MaxAuthTries 3
AllowUsers C1 C2
```

> ⚠ **Do not log out of your root console yet.** If SSH breaks you need a way back in. Test SSH from Client1 first, then close the console.

---

## Step 6 — firewalld locked down

```bash
systemctl enable --now firewalld

firewall-cmd --permanent --remove-service=ssh         2>/dev/null   # default port 22 - gone
firewall-cmd --permanent --remove-service=cockpit     2>/dev/null   # uncommon, but no need

firewall-cmd --permanent --add-port=2022/tcp
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-service=kerberos

firewall-cmd --reload
firewall-cmd --list-all
```

Expected `services:` line: `http https kerberos` (no `ssh`); `ports:` line: `2022/tcp`.

---

## Step 7 — Password complexity + expiry policy

> PDF p.13: min 10 chars, 4 char classes, expire every 30 days, warn from day 25.

`/etc/security/pwquality.conf`:
```bash
cat > /etc/security/pwquality.conf <<'EOF'
minlen   = 10
minclass = 4
dcredit  = -1
ucredit  = -1
lcredit  = -1
ocredit  = -1
maxrepeat = 3
EOF
```

`/etc/login.defs`:
```bash
sed -i 's/^PASS_MAX_DAYS.*/PASS_MAX_DAYS  30/' /etc/login.defs
sed -i 's/^PASS_MIN_DAYS.*/PASS_MIN_DAYS  0/'  /etc/login.defs
sed -i 's/^PASS_WARN_AGE.*/PASS_WARN_AGE  5/'  /etc/login.defs
```

**Why `PASS_WARN_AGE 5`?** Expiry is at day 30; "warn starting day 25" = warn 5 days before expiry.

**Verify:**
```bash
useradd bob
passwd bob                        # try "password"  -> rejected (too short, no classes)
                                  # try "P@ssw0rd12" -> accepted
chage -l bob                      # check max 30, warn 5
```
After: `userdel -r bob` to clean up the test user.

---

## Step 8 — Apache HTTPS site for `www.manila.com`

```bash
dnf -y install httpd mod_ssl mod_authnz_pam
mkdir -p /var/www/manila
echo '<h1>Welcome to www.manila.com</h1>' > /var/www/manila/index.html
```

Generate a **self-signed** cert first — replace with WINSRV3 cert later (step 10). Self-signed is partial credit; signed is full.

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -subj "/C=PH/ST=NCR/L=Manila/O=Manila/CN=www.manila.com" \
  -keyout /etc/pki/tls/private/manila.key \
  -out    /etc/pki/tls/certs/manila.crt
chmod 600 /etc/pki/tls/private/manila.key
```

Create the vhost file `/etc/httpd/conf.d/manila.conf`:
```apache
<VirtualHost *:80>
    ServerName www.manila.com
    Redirect permanent / https://www.manila.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName www.manila.com
    DocumentRoot /var/www/manila

    SSLEngine on
    SSLCertificateFile    /etc/pki/tls/certs/manila.crt
    SSLCertificateKeyFile /etc/pki/tls/private/manila.key
    SSLProtocol           all -SSLv3 -TLSv1 -TLSv1.1
    SSLHonorCipherOrder   on

    <Directory /var/www/manila>
        AuthType Basic
        AuthName "manila.com - domain login required"
        AuthBasicProvider PAM
        AuthPAMService httpd
        Require valid-user
    </Directory>
</VirtualHost>
```

PAM service file for httpd:
```bash
cat > /etc/pam.d/httpd <<'EOF'
auth    required pam_sss.so
account required pam_sss.so
EOF
```

Allow Apache to read PAM data:
```bash
usermod -aG shadow apache
setsebool -P httpd_mod_auth_pam 1
```

---

## Step 9 — SELinux

```bash
sed -i 's/^SELINUX=.*/SELINUX=enforcing/' /etc/selinux/config
setenforce 1

semanage fcontext -a -t httpd_sys_content_t "/var/www/manila(/.*)?"
restorecon -Rv /var/www/manila

setsebool -P httpd_can_network_connect    1
setsebool -P httpd_can_network_connect_db 1
setsebool -P httpd_dbus_sssd              1
```

Now start Apache:
```bash
systemctl enable --now httpd
systemctl --no-pager status httpd
ss -tlnp | grep -E ':(80|443) '
```

**Verify:**
- From Client1 Firefox: `https://www.manila.com` → should prompt for a domain login (basic auth) → enter `M001` / `P@ssw0rd` → page loads.
- From LINSRV1: `sestatus` → enforcing.
- From LINSRV1: `ls -Z /var/www/manila` → label `httpd_sys_content_t`.

---

## Step 10 (BONUS — only if time) — Replace self-signed cert with WINSRV3 cert

This earns the **PKI mark** (~0.4 mark). Skip if you're tight on time.

1. From a domain-joined Windows box (Client1), open MMC → Certificates → Personal → Request New Certificate → enroll a "Web Server" cert with subject `CN=www.manila.com` (the `certenroll` GPO must already be applied for this template to be visible).
2. Export the cert **with private key** (`.pfx`) → copy to LINSRV1 via WinSCP.
3. On LINSRV1:
   ```bash
   openssl pkcs12 -in /tmp/manila.pfx -nokeys -out /etc/pki/tls/certs/manila.crt
   openssl pkcs12 -in /tmp/manila.pfx -nocerts -nodes -out /etc/pki/tls/private/manila.key
   chmod 600 /etc/pki/tls/private/manila.key
   systemctl restart httpd
   ```
4. Refresh Firefox on Client1 → cert warning should be gone, chain shows WINSRV3 → WINSRV4.

---

## Final summary print (run on LINSRV1)

```bash
echo "[realm]"   ; realm list
echo "[sshd]"   ; grep -E "^(Port|PermitRootLogin|AllowUsers|MaxAuth)" /etc/ssh/sshd_config
echo "[fw]"     ; firewall-cmd --list-all
echo "[selinux]"; sestatus
echo "[httpd]"  ; ss -tlnp | grep -E ':(80|443) '
```

Cross-check each line against the **`07_verification_checklist.md` Block 3**.
