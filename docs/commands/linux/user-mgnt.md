create new group
```sh
groupadd groupname
usermod -aG groupName Username
```

change primery group
```sh
usermod -g groupName UserName
```

change Secondery group
```sh
usermod -G groupName UserName
```

all groups

```sh
getent group
```

group info
```sh
getent group developers
```


groups list
```sh
cat /etc/group
```

user groups
```sh
groupes userName
```

delete user from group
```sh
sudo gpasswd -d username groupname
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
id username
id -gn username
```