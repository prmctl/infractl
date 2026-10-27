



# SSL

## DNS Challange

Step 1 : Check current certificate
```sh
# List existing Let's Encrypt certificates
sudo certbot certificates
# Check current Let's Encrypt certificate expiration
sudo openssl x509 -in /etc/letsencrypt/live/registry.example.com/fullchain.pem -noout -dates
# Check Harbor certificate expiration
sudo openssl x509 -in /data/secret/cert/server.crt -noout -dates
```

Step 2 : Renew SSL certificate
```sh
# Renew certificate using manual DNS-01 challenge
sudo certbot certonly --manual --preferred-challenges dns --cert-name registry.example.com -d registry.example.com
```

```sh
# Verify DNS TXT record propagation
dig TXT _acme-challenge.registry.example.com +short

# Verify using Google DNS
dig @8.8.8.8 TXT _acme-challenge.registry.example.com +short

# Verify using Cloudflare DNS
dig @1.1.1.1 TXT _acme-challenge.registry.example.com +short
```

Step 3 : Verify renewed certificate
```sh
# Verify renewed certificate expiration
sudo openssl x509 -in /etc/letsencrypt/live/registry.example.com/fullchain.pem -noout -dates

# List updated certificates
sudo certbot certificates
```

Step 4 : Check Harbor Nginx configuration
```sh
# Check Nginx container status
sudo docker ps -a --filter name=nginx

# Validate Nginx configuration
sudo docker exec nginx nginx -t

# Check SSL certificate paths
sudo docker exec nginx nginx -T 2>&1 | grep ssl_certificate
```

Step 5 : Backup existing Harbor certificates
```sh
# Backup existing SSL certificate
sudo cp -a /data/secret/cert/server.crt /data/secret/cert/server.crt.bak

# Backup existing private key
sudo cp -a /data/secret/cert/server.key /data/secret/cert/server.key.bak
```

Step 6 : Update Harbor SSL certificates
```sh
# Copy renewed full-chain certificate to Harbor
sudo install -o 10000 -g 10000 -m 600 \
  /etc/letsencrypt/live/registry.example.com/fullchain.pem /data/secret/cert/server.crt

# Copy renewed private key to Harbor
sudo install -o 10000 -g 10000 -m 600 \
  /etc/letsencrypt/live/registry.example.com/privkey.pem /data/secret/cert/server.key
```

Step 7 : Reload Harbor Nginx
```sh
# Validate Nginx configuration before reloading
sudo docker exec nginx nginx -t

# Reload Nginx without restarting Harbor
sudo docker exec nginx nginx -s reload
```


