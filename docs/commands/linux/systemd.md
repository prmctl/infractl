

```sh
systemctl list-units --type=service --all
systemctl list-units --type=service --all --no-pager
systemctl list-units --type=service --state=running
systemctl --failed --type=service
systemctl list-unit-files --type=service
```