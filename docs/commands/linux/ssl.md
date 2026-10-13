
# Certbot


Install  certbot
```sh
sudo apt update
sudo apt install certbot -y
```

Get SSL for first time - dns challange
```sh
sudo certbot certonly --manual --preferred-challenges dns -d example.com -d www.example.com
```

Get SSL for first time - dns challange Wildcard
```sh
sudo certbot certonly --manual --preferred-challenges dns -d example.com -d '*.example.com'
```

```sh
sudo certbot renew --cert-name example.com --manual --preferred-challenges dns
```

List of certificates
```sh
sudo certbot certificates
```