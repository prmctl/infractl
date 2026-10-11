


#### Create New Client

```sh
#!/bin/bash
set -e

CLIENT="$1"

EASYRSA="/etc/openvpn/server/easy-rsa"
OUTPUT="/etc/openvpn/server/clients"
COMMON="/etc/openvpn/server/client-common.txt"
TLS_KEY="/etc/openvpn/server/tc.key"

cd "$EASYRSA"

./easyrsa build-client-full "$CLIENT" nopass

mkdir -p "$OUTPUT"

cat \
  "$COMMON" \
  <(echo '<ca>') \
  "$EASYRSA/pki/ca.crt" \
  <(echo '</ca>') \
  <(echo '<cert>') \
  "$EASYRSA/pki/issued/$CLIENT.crt" \
  <(echo '</cert>') \
  <(echo '<key>') \
  "$EASYRSA/pki/private/$CLIENT.key" \
  <(echo '</key>') \
  <(echo '<tls-crypt>') \
  "$TLS_KEY" \
  <(echo '</tls-crypt>') \
  > "$OUTPUT/$CLIENT.ovpn"

chmod 600 "$OUTPUT/$CLIENT.ovpn"

echo "Created: $OUTPUT/$CLIENT.ovpn"
```




#### Revoke

```sh
ls -1 /etc/openvpn/server/easy-rsa/pki/issued | sed 's/\.crt$//'

cd /etc/openvpn/server/easy-rsa

./easyrsa revoke revoked-client-1
./easyrsa revoke revoked-client-2
./easyrsa revoke revoked-client-3

./easyrsa gen-crl
cp -f /etc/openvpn/server/easy-rsa/pki/crl.pem /etc/openvpn/server/crl.pem
chmod 644 /etc/openvpn/server/crl.pem
systemctl restart openvpn-server@server
```

```sh
sudo journalctl -u openvpn-server@server --since "45 days ago" \
| grep "TLS: Initial packet" \
| sed -E 's/.*\[AF_INET\]([0-9.]+):.*/\1/' \
| sort | uniq -c | sort -nr
```




#### All Connections

```sh
sudo journalctl -u openvpn-server@server --since "today" --no-pager | awk '
/CN=/ {
    match($0,/CN=([^ ,]+)/,u)
    last_user=u[1]
}

/Peer Connection Initiated/ {
    match($0,/([A-Za-z]{3} [ 0-9]{2} [0-9:]{8})/,t)
    match($0,/\[AF_INET\]([0-9.]+):/,ip)
    printf "%s | SUCCESS | user=%s | ip=%s\n",t[1],last_user,ip[1]
}

/AUTH_FAILED/ {
    match($0,/([A-Za-z]{3} [ 0-9]{2} [0-9:]{8})/,t)
    match($0,/\[AF_INET\]([0-9.]+):/,ip)
    match($0,/user=([^ ]+)/,u)
    if(u[1]=="") user=last_user
    else user=u[1]
    printf "%s | FAILED  | user=%s | ip=%s\n",t[1],user,ip[1]
}
'
```


#### Today Logs
```sh
sudo journalctl -u openvpn-server@server --since today --no-pager
```