
# Installation

```sh

sudo apt update

sudo apt install -y fio stress-ng lvm2 mdadm dmsetup e2fsprogs sysstat smartmontools util-linux

```



# Incidents



## Disk And File System

### Prepare
```sh
mkdir -p /root/chaosd-install
cd /root/chaosd-install
export CHAOSD_VERSION=v1.4.1
curl -fL -o chaosd.tar.gz \"https://mirrors.chaos-mesh.org/chaosd-${CHAOSD_VERSION}-linux-amd64.tar.gz"
tar -xzf chaosd.tar.gz
cp -a "chaosd-${CHAOSD_VERSION}-linux-amd64" /usr/local/
ln -s "/usr/local/chaosd-${CHAOSD_VERSION}-linux-amd64/chaosd" /usr/local/bin/chaosd
chaosd --help
```
```sh
sudo mkdir -p /mnt/fs-lab
sudo fallocate -l 512M /var/tmp/fs-lab.img
sudo mkfs.ext4 -F -m 0 -N 4096 /var/tmp/fs-lab.img
sudo mount -o loop /var/tmp/fs-lab.img /mnt/fs-lab
mountpoint /mnt/fs-lab
```

### Filesystem Space Exhaustion (Disk Full)
A full filesystem causes writes requiring additional space to fail with ENOSPC (No space left on device). This can disrupt databases, logging, uploads, and service startup. Existing data generally remains readable; the filesystem does not automatically become read-only.
Empty files may still be created if inodes and directory-entry space are available. Check capacity with df -h, inodes with df -i, and mount status (rw/ro) with findmnt.
Deletion usually works. Moving files within the same filesystem does not free space; moving them to another filesystem does. Deleted files held open by processes retain their space until closed; inspect them with lsof +L1.
Check service errors using journalctl -u <service> and configured application logs, often under /var/log/. Logs on the full filesystem may be missing.
Recover by safely removing or relocating unnecessary data, verifying free space, and checking service health. Failed services may need restarting; failed writes are not automatically recovered.

Incident
```sh
mountpoint /mnt/fs-lab && chaosd attack disk fill --path /mnt/fs-lab/fill-rest.bin --fallocate=false --size 600M
```


### Inode Exhaustion
When a filesystem runs out of free inodes, creating new files, directories, or symlinks fails with ENOSPC (No space left on device), even when disk space remains available. Existing files generally remain readable and writable if sufficient data space is available.
This can disrupt uploads, temporary files, sessions, log rotation, database operations, and service startup. Check inode usage with df -i and compare it with disk usage using df -h.
Check journalctl -u <service> and configured application logs for failed file creation. The error message alone does not distinguish inode exhaustion from disk-space exhaustion.
Stop excessive file creation and safely delete unnecessary files. Deleted files still held open retain their inodes until closed; check with lsof +L1. Verify free inodes and service health after cleanup.
For directories containing millions of files, use find or unsorted ls -1U for inspection and controlled cleanup. Prevent recurrence through retention policies and inode monitoring; splitting files across directories improves manageability but does not reduce total inode usage.
Incident

```sh
mkdir -p /mnt/inode-lab
test ! -e /var/tmp/inode-lab-3m.img &&
fallocate -l 4G /var/tmp/inode-lab-3m.img
```

```sh
mkfs.ext4 -F -m 0 -I 256 -N 3000000 /var/tmp/inode-lab-3m.img
mount -o loop /var/tmp/inode-lab-3m.img /mnt/inode-lab
mountpoint /mnt/inode-lab
df -h /mnt/inode-lab
df -i /mnt/inode-lab
```

```sh 
mountpoint /mnt/inode-lab && python3 - <<'PY'
from pathlib import Path

directory = Path("/mnt/inode-lab/inode-test")
directory.mkdir(exist_ok=True)

for i in range(3000000):
    try:
        (directory / f"file-{i}").touch()
    except OSError as error:
        print(f"Stopped at file {i}: {error}")
        break
else:
    print("Limit reached without an error.")
PY
```

### Filesystem Read-only

A filesystem may become read-only after storage I/O failures, filesystem metadata corruption, or journal errors. For example, ext4 configured with errors=remount-ro may switch to read-only to limit further damage. Disk-space or inode exhaustion alone does not cause this transition.
Reading may remain possible, but writes, deletions, and renames fail with Read-only file system. Data already stored may survive; recent or failed writes are not guaranteed to be preserved.
Check mount options using findmnt -T /affected/path and inspect kernel logs with journalctl -k. Look for I/O errors, filesystem errors, journal aborts, and remount messages.
Recovery steps:
1. Identify and resolve the underlying storage or configuration problem.
2. Preserve important data before repairs; avoid repairing storage that is still failing.
3. Stop dependent services and unmount the affected filesystem.
4. If needed, check and repair it using the appropriate tool—for ext4, e2fsck -f /dev/DEVICE. Never run repairs on a mounted filesystem.
5. Mount it read-write, verify writes and kernel logs, then restore services and check application consistency.
A root filesystem may require a rescue environment. Filesystem repair restores structural consistency; it does not guarantee complete data recovery or database integrity. If read-only mode was intentional and no corruption exists, correcting the configuration and remounting read-write may be sufficient.

Incident
```sh
df -h /var/tmp
test ! -e /var/tmp/io-fault-lab.img &&
fallocate -l 512M /var/tmp/io-fault-lab.img
```

```sh
mkdir -p /mnt/io-fault-lab
LAB_LOOP=$(losetup --find --show /var/tmp/io-fault-lab.img)
LAB_SECTORS=$(blockdev --getsz "$LAB_LOOP")
echo "$LAB_LOOP"
```

```sh
dmsetup create io-fault-lab --table "0 $LAB_SECTORS linear $LAB_LOOP 0"
mkfs.ext4 -m 0 /dev/mapper/io-fault-lab
mount -o errors=remount-ro /dev/mapper/io-fault-lab /mnt/io-fault-lab
printf 'healthy baseline\n' > /mnt/io-fault-lab/baseline.txt
sync -f /mnt/io-fault-lab/baseline.txt
findmnt -T /mnt/io-fault-lab
```

```sh
dmsetup suspend io-fault-lab
dmsetup reload io-fault-lab --table "0 $LAB_SECTORS flakey $LAB_LOOP 0 0 3600 1 error_writes"
dmsetup resume io-fault-lab
```

Test
```sh
dd if=/dev/zero of=/mnt/io-fault-lab/write-test.bin bs=1M count=8 conv=fsync
sync -f /mnt/io-fault-lab
findmnt -T /mnt/io-fault-lab -o TARGET,SOURCE,OPTIONS
journalctl -k --since "5 minutes ago" --no-pager | tail -n 60
```