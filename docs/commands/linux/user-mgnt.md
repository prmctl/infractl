

create new group
```sh
groupadd groupname
```

groups list
```sh
cat /etc/group
```

create new user
```sh
useradd -m -s /bin/bash -c "prmctl prmctl" -G devops prmctl
sudo useradd -r -s /usr/sbin/nologin prmctl
sudo useradd -M -s /usr/sbin/nologin prmctl
sudo passwd prmctl
```

users list
```sh
cat /etc/passwd
```

user info
```sh 
id prmctl
```