
# OpenSSL

Check the locally installed certificate:
```sh
sudo openssl x509 -in /etc/letsencrypt/live/prmctl.me/fullchain.pem -noout -dates
```

Show the subject, issuer, and validity dates:
```sh
sudo openssl x509 -in /etc/letsencrypt/live/prmctl.me/fullchain.pem -noout -subject -issuer -dates
```

Check the Certificate Actually Served by the Website
```sh
echo | openssl s_client  -connect prmctl.me:443 -servername prmctl.me 2>/dev/null | openssl x509 -noout -dates -subject -issuer
```

# Certbot

Install Certbot
```sh
sudo apt update
sudo apt install certbot
certbot --version
```

Request a certificate using a manual DNS challenge:
```sh
sudo certbot certonly  --manual  --preferred-challenges dns  -d prmctl.me
```

```sh
sudo certbot certonly  --manual  --preferred-challenges dns  -d api.prmctl.me
```

Obtain a Wildcard Certificate
```sh
sudo certbot certonly  --manual  --preferred-challenges dns  -d prmctl.me  -d "*.prmctl.me"
```
List Certificates Managed by Certbot
```sh
sudo certbot certificates
```

If you need to request a new certificate before the existing one expires:
```sh
sudo certbot certonly --manual --preferred-challenges dns --force-renewal  --cert-name prmctl.me  -d prmctl.me
```

Renew certificates that are eligible for automatic renewal:
```sh
sudo certbot renew
```

Test renewal without actually replacing certificates:
```sh
sudo certbot renew --dry-run
```

