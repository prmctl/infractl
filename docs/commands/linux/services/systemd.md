# systemd

show all services
```sh
systemctl list-units --type=service --state=running
systemctl list-units --type=service --all
```

```bash
systemctl status nginx
journalctl -u nginx -n 100 --no-pager
```



```sh
sudo systemctl list-units --all --type=service 'openvpn*'
```