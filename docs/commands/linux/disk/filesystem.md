
```sh
findmnt -T /mnt/fs-lab -o TARGET,SOURCE,OPTIONS
```


```sh
du -h
du -sh /var/log
du -h --max-depth=1 /var | sort -hr | head -10
```



# work with huge folders
remove files
```sh
ionice -c 3 nice -n 19 bash -c '
  find /mnt/inode-lab/inode-test \
    -maxdepth 1 -type f -print0 |
  head -z -n 10000 |
  xargs -0 -r -n 1000 rm --
'
```

remove files
```sh
ionice -c 3 nice -n 19 bash -c '
  find /mnt/inode-lab/inode-test \
    -maxdepth 1 -type f -print0 |
  xargs -0 -r -n 1000 bash -c '"'"'
    rm -- "$@" || exit
    sleep 0.2
  '"'"' _
'
```

show files
```sh
find /mnt/inode-lab/inode-test -maxdepth 1 -type f -print -quit
```