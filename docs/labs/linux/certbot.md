# Certbot — Important Commands Cheat Sheet

## Check Certbot Version

```bash
# Show the currently installed Certbot version.
certbot --version
```

## Show Help

```bash
# Show the main Certbot help and available commands.
certbot --help
```

```bash
# Show detailed help for all Certbot options.
certbot --help all
```

---

# Certificate Management

## List Existing Certificates

```bash
# List all certificates currently managed by Certbot,
# including domain names, expiration dates, and certificate paths.
sudo certbot certificates
```

Typical certificate files are stored under:

```text
/etc/letsencrypt/live/example.com/
```

Important files:

```text
cert.pem       # Server certificate
chain.pem      # Intermediate CA certificate
fullchain.pem  # Server certificate + intermediate certificates
privkey.pem    # Private key
```

For most Nginx/Apache configurations, use:

```text
fullchain.pem
privkey.pem
```

---

# Request a Certificate with Nginx

```bash
# Obtain a certificate and automatically configure Nginx.
sudo certbot --nginx -d example.com
```

```bash
# Obtain one certificate covering both the root domain and www.
sudo certbot --nginx \
  -d example.com \
  -d www.example.com
```

```bash
# Obtain the certificate using the Nginx plugin,
# but do NOT modify the Nginx configuration.
sudo certbot certonly --nginx \
  -d example.com \
  -d www.example.com
```

---

# Request a Certificate with Apache

```bash
# Obtain a certificate and automatically configure Apache.
sudo certbot --apache -d example.com
```

```bash
# Obtain a certificate for multiple domains using Apache.
sudo certbot --apache \
  -d example.com \
  -d www.example.com
```

```bash
# Obtain the certificate using Apache validation,
# without modifying the Apache configuration.
sudo certbot certonly --apache \
  -d example.com
```

---

# Standalone Mode

```bash
# Obtain a certificate using Certbot's temporary built-in HTTP server.
# Port 80 must be available.
sudo certbot certonly --standalone \
  -d example.com
```

If Nginx is already using port 80:

```bash
# Stop Nginx before using standalone mode.
sudo systemctl stop nginx

sudo certbot certonly --standalone \
  -d example.com

sudo systemctl start nginx
```

Standalone mode is useful when no web server is installed or when Certbot should handle the ACME HTTP challenge itself.

---

# Webroot Mode

```bash
# Obtain a certificate without stopping the existing web server.
# Certbot writes the ACME challenge under the specified web root.
sudo certbot certonly --webroot \
  -w /var/www/example.com \
  -d example.com
```

For multiple domains sharing the same document root:

```bash
sudo certbot certonly --webroot \
  -w /var/www/example.com \
  -d example.com \
  -d www.example.com
```

The web server must allow access to:

```text
/.well-known/acme-challenge/
```

---

# Certificate Renewal

## Renew Certificates

```bash
# Renew all certificates that are close to expiration.
sudo certbot renew
```

Certbot normally skips certificates that do not need renewal yet.

---

## Test Automatic Renewal

```bash
# Simulate the renewal process without replacing production certificates.
sudo certbot renew --dry-run
```

This is one of the most important commands to run after setting up Certbot.

---

## Force Renewal

```bash
# Force renewal even if the certificate is not close to expiration.
sudo certbot renew --force-renewal
```

Use this carefully because Let's Encrypt applies issuance rate limits.

---

## Renew a Specific Certificate

First find the certificate name:

```bash
sudo certbot certificates
```

Then:

```bash
# Renew only the certificate with this Certbot certificate name.
sudo certbot renew \
  --cert-name example.com
```

---

# Reissue / Modify an Existing Certificate

```bash
# Reissue an existing certificate and add another domain.
sudo certbot --nginx \
  --cert-name example.com \
  -d example.com \
  -d www.example.com \
  -d api.example.com
```

This is useful when adding or removing SAN/domain names from an existing certificate.

---

# Delete a Certificate

```bash
# Safely remove a certificate managed by Certbot.
sudo certbot delete
```

Or specify the certificate directly:

```bash
sudo certbot delete \
  --cert-name example.com
```

Prefer `certbot delete` instead of manually deleting files from:

```text
/etc/letsencrypt/
```

---

# Revoke a Certificate

```bash
# Revoke a certificate that should no longer be trusted.
sudo certbot revoke \
  --cert-path /etc/letsencrypt/live/example.com/cert.pem
```

After revocation, you can remove it from Certbot:

```bash
sudo certbot delete \
  --cert-name example.com
```

Typical reasons for revocation include:

- Private key compromise
- Server compromise
- Certificate issued incorrectly
- Certificate no longer required

---

# Wildcard Certificates

Wildcard certificates usually require DNS validation.

Example:

```bash
# Request a wildcard certificate using a manual DNS challenge.
sudo certbot certonly \
  --manual \
  --preferred-challenges dns \
  -d example.com \
  -d '*.example.com'
```

Certbot will ask you to create a DNS TXT record similar to:

```text
_acme-challenge.example.com
```

Manual DNS validation is not ideal for unattended automatic renewal.

For production systems, prefer a Certbot DNS plugin supported by your DNS provider.

---

# Check Automatic Renewal Timer

On systemd-based distributions:

```bash
# Check whether the Certbot renewal timer exists and is active.
systemctl status certbot.timer
```

```bash
# List Certbot-related timers.
systemctl list-timers | grep certbot
```

On Snap installations, the timer/service naming may differ.

---

# Check Certbot Service Logs

```bash
# View Certbot-related systemd logs.
sudo journalctl -u certbot
```

```bash
# Show recent Certbot log entries.
sudo journalctl -u certbot --since today
```

Certbot also normally writes logs under:

```text
/var/log/letsencrypt/
```

The primary log file is commonly:

```text
/var/log/letsencrypt/letsencrypt.log
```

View it with:

```bash
sudo less /var/log/letsencrypt/letsencrypt.log
```

---

# Renewal Hooks

Hooks are useful when a service must reload after certificate renewal.

## Deploy Hook

```bash
# Reload Nginx only after a certificate has actually been renewed.
sudo certbot renew \
  --deploy-hook "systemctl reload nginx"
```

Example for HAProxy:

```bash
sudo certbot renew \
  --deploy-hook "systemctl reload haproxy"
```

---

## Pre Hook

```bash
# Execute a command before attempting renewal.
sudo certbot renew \
  --pre-hook "systemctl stop nginx"
```

---

## Post Hook

```bash
# Execute a command after Certbot finishes the renewal process.
sudo certbot renew \
  --post-hook "systemctl start nginx"
```

A common standalone example:

```bash
sudo certbot renew \
  --pre-hook "systemctl stop nginx" \
  --post-hook "systemctl start nginx"
```

---

# Non-Interactive Mode

Useful for scripts and automation:

```bash
# Request a certificate without interactive prompts.
sudo certbot certonly \
  --standalone \
  --non-interactive \
  --agree-tos \
  --email admin@example.com \
  -d example.com
```

---

# Register Without Email

```bash
# Register an ACME account without providing an email address.
# Generally not recommended because expiration/security notices may be missed.
sudo certbot certonly \
  --standalone \
  --register-unsafely-without-email \
  --agree-tos \
  -d example.com
```

Using a real administrative email is usually preferable.

---

# Staging Environment

```bash
# Use Let's Encrypt staging environment for testing.
# Certificates generated this way are NOT trusted by browsers.
sudo certbot certonly \
  --standalone \
  --staging \
  -d example.com
```

Staging is useful when debugging certificate issuance because it avoids production rate limits.

---

# Verbose / Debug Output

```bash
# Show more detailed Certbot output.
sudo certbot renew -v
```

For even more debugging information:

```bash
sudo certbot renew -vv
```

---

# Useful Certificate Inspection Commands

## Check Certificate Expiration

```bash
# Display start and expiration dates of the currently installed certificate.
sudo openssl x509 \
  -in /etc/letsencrypt/live/example.com/fullchain.pem \
  -noout \
  -dates
```

## Show Certificate Subject and Issuer

```bash
sudo openssl x509 \
  -in /etc/letsencrypt/live/example.com/cert.pem \
  -noout \
  -subject \
  -issuer
```

## Show Domains Inside the Certificate

```bash
sudo openssl x509 \
  -in /etc/letsencrypt/live/example.com/cert.pem \
  -noout \
  -ext subjectAltName
```

---

# Recommended Routine Checks

```bash
# Show managed certificates.
sudo certbot certificates
```

```bash
# Test certificate renewal.
sudo certbot renew --dry-run
```

```bash
# Check automatic renewal timer.
systemctl list-timers | grep certbot
```

```bash
# Check certificate expiration directly.
sudo openssl x509 -in /etc/letsencrypt/live/example.com/fullchain.pem -noout -dates
```

---

# Quick Reference

```bash
# List certificates
sudo certbot certificates

# Nginx: obtain + install certificate
sudo certbot --nginx -d example.com

# Nginx: obtain certificate only
sudo certbot certonly --nginx -d example.com

# Apache
sudo certbot --apache -d example.com

# Standalone
sudo certbot certonly --standalone -d example.com

# Webroot
sudo certbot certonly --webroot -w /var/www/example.com -d example.com

# Renew certificates
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run

# Force renewal
sudo certbot renew --force-renewal

# List certificates
sudo certbot certificates

# Delete certificate
sudo certbot delete --cert-name example.com

# Revoke certificate
sudo certbot revoke \
  --cert-path /etc/letsencrypt/live/example.com/cert.pem

# Check renewal timer
systemctl list-timers | grep certbot

# View Certbot logs
sudo less /var/log/letsencrypt/letsencrypt.log
```