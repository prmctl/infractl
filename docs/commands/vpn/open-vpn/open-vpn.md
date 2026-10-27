#####################Create New Client#####################
cd /etc/openvpn/server/easy-rsa
./easyrsa gen-req new-client-name nopass


ls -l pki/private/new-client-name.key
ls -l pki/reqs/new-client-name.req


# Sign
./easyrsa sign-req client new-client-name

ls -l pki/issued/hesam-v2.crt


# Generate .ovpn
mkdir -p /etc/openvpn/server/clients

```sh
cat /etc/openvpn/server/client-common.txt \
    <(echo -e '<ca>') \
    /etc/openvpn/server/easy-rsa/pki/ca.crt \
    <(echo -e '</ca>\n<cert>') \
    /etc/openvpn/server/easy-rsa/pki/issued/new-client-name.crt \
    <(echo -e '</cert>\n<key>') \
    /etc/openvpn/server/easy-rsa/pki/private/new-client-name.key \
    <(echo -e '</key>\n<tls-crypt>') \
    /etc/openvpn/server/tc.key \
    <(echo -e '</tls-crypt>') \
    > /etc/openvpn/client/new-client-name.ovpn
```

#####################Revoke Client#####################

# Client List
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

#####################Check Client Connection#####################
# All Ips that try to connect
sudo journalctl -u openvpn-server@server --since "45 days ago" \
| grep "TLS: Initial packet" \
| sed -E 's/.*\[AF_INET\]([0-9.]+):.*/\1/' \
| sort | uniq -c | sort -nr



# All Connections
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


# Today Logs
sudo journalctl -u openvpn-server@server --since today --no-pager



