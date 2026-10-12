# Disk And File System

Prepare
```sh
sudo apt update
sudo apt install -y fio stress-ng lvm2 mdadm dmsetup e2fsprogs sysstat smartmontools util-linux
```

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

## Filesystem Space Exhaustion (Disk Full)
A full filesystem causes writes requiring additional space to fail with ENOSPC (No space left on device). This can disrupt databases, logging, uploads, and service startup. Existing data generally remains readable; the filesystem does not automatically become read-only.
Empty files may still be created if inodes and directory-entry space are available. Check capacity with df -h, inodes with df -i, and mount status (rw/ro) with findmnt.
Deletion usually works. Moving files within the same filesystem does not free space; moving them to another filesystem does. Deleted files held open by processes retain their space until closed; inspect them with lsof +L1.
Check service errors using journalctl -u <service> and configured application logs, often under /var/log/. Logs on the full filesystem may be missing.
Recover by safely removing or relocating unnecessary data, verifying free space, and checking service health. Failed services may need restarting; failed writes are not automatically recovered.

### incident generator
```sh
mountpoint /mnt/fs-lab && chaosd attack disk fill --path /mnt/fs-lab/fill-rest.bin --fallocate=false --size 600M
```

---
## Inode Exhaustion
When a filesystem runs out of free inodes, creating new files, directories, or symlinks fails with ENOSPC (No space left on device), even when disk space remains available. Existing files generally remain readable and writable if sufficient data space is available.
This can disrupt uploads, temporary files, sessions, log rotation, database operations, and service startup. Check inode usage with df -i and compare it with disk usage using df -h.
Check journalctl -u <service> and configured application logs for failed file creation. The error message alone does not distinguish inode exhaustion from disk-space exhaustion.
Stop excessive file creation and safely delete unnecessary files. Deleted files still held open retain their inodes until closed; check with lsof +L1. Verify free inodes and service health after cleanup.
For directories containing millions of files, use find or unsorted ls -1U for inspection and controlled cleanup. Prevent recurrence through retention policies and inode monitoring; splitting files across directories improves manageability but does not reduce total inode usage.


### incident generator
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
---
## Filesystem Read-only
A filesystem may become read-only because of a filesystem error or a failure in the storage path. For example, the filesystem driver may detect inconsistent metadata or a journal error and stop further writes. With ext4, the `errors=remount-ro` mount option tells the filesystem to remount as read-only after certain errors.

A filesystem error can follow an unexpected shutdown, a kernel or filesystem bug, or an unsafe administrative operation. A storage failure can come from the disk or any part of the storage path, such as a controller, RAID, virtual disk, or network storage. A storage I/O error may trigger a filesystem error and cause a read-only remount.

A read-only mount can also be intentional. If the filesystem was deliberately mounted read-only, or a configuration enforces that state, correcting the configuration may be enough. Disk-space or inode exhaustion alone normally causes write failures such as `No space left on device`; it does not, by itself, make the filesystem read-only.

Reading may remain possible, while writes, deletions, and renames fail with `Read-only file system`. Data already stored may still be readable, but recent or failed writes are not guaranteed to be preserved.

### Diagnose

Check the mount state and options:

```bash
findmnt -T /affected/path -o TARGET,SOURCE,FSTYPE,OPTIONS
```

Inspect kernel messages from the current boot:

```bash
journalctl -k -b
```

Search current-boot messages for common filesystem and storage errors:

```bash
journalctl -k -b | grep -Ei 'error|fail|I/O|ext4|xfs|btrfs|nvme|scsi|remount|journal'
```

If the server has rebooted since the incident, inspect the previous boot as well. Previous-boot logs are available only if they were retained by the system journal:

```bash
journalctl -k -b -1
journalctl -k -b -1 | grep -Ei 'error|fail|I/O|ext4|xfs|btrfs|nvme|scsi|remount|journal'
```

Look for filesystem errors, journal aborts, I/O errors, device resets, and messages indicating a read-only remount. These messages can help distinguish a filesystem-level error from a failure in the storage path.

### Recovery

1. Identify and resolve the underlying filesystem, storage, or configuration problem. Do not treat a remount to read-write as a fix if the cause is still present.
2. Preserve important data before attempting repairs. If the storage device or path is still failing, avoid in-place repairs until the storage is stable; consider recovering from a copy or image.
3. Stop services that use the filesystem, then unmount it before running a filesystem repair tool.
4. If a filesystem check is needed, use the tool appropriate for that filesystem. For ext4, for example:

   ```bash
   e2fsck -f /dev/DEVICE
   ```

   Replace `/dev/DEVICE` with the correct, unmounted filesystem device. Never run `e2fsck` on a mounted filesystem.
5. After resolving the cause and completing any needed repair, mount the filesystem read-write. Verify that writes work and check the kernel logs for new errors before restoring dependent services.
6. Check application-level consistency as well. Filesystem repair restores filesystem structure; it does not guarantee complete data recovery or database integrity.

A root filesystem may require a rescue or recovery environment to unmount and repair it. If read-only mode was intentional and there is no filesystem or storage error, correcting the configuration and remounting read-write may be sufficient.


### incident generator
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



## Deleted Files Still Held Open
Deleting a file removes its directory entry, but its disk space remains allocated while a process holds it open. This commonly occurs when an active service log is deleted. du no longer counts the file, while df still reports its allocated space.
Use lsof +L1 to identify deleted files still open, including the owning PID and file descriptor. Recover space through the application's supported log-reopening procedure or a controlled service restart. Space is released when the last open reference is closed; deleting the pathname again or running sync does not help.
Verify recovery with df -h and lsof +L1. Prevent recurrence through correctly configured log rotation and service-specific log reopening.


```sh
findmnt -T /mnt/fs-lab -o TARGET,SOURCE,OPTIONS
df -h /mnt/fs-lab
```

```sh
mountpoint /mnt/fs-lab && python3 - <<'PY'
import os
import time

with open("/mnt/fs-lab/held-open.log", "wb") as f:
    block = b"x" * (1024 * 1024)
    for _ in range(100):
        f.write(block)
    f.flush()
    os.fsync(f.fileno())

    print(f"PID: {os.getpid()} — holding a 100 MiB file open", flush=True)
    while True:
        time.sleep(1)
PY
```

```sh
df -h /mnt/fs-lab
du -xsh /mnt/fs-lab

rm /mnt/fs-lab/held-open.log

ls -lh /mnt/fs-lab
df -h /mnt/fs-lab
du -xsh /mnt/fs-lab

lsof /mnt/lab/held-open.log
lsof +L1
systemctl status 1495
```

```sh
ps -p 1495 -o pid,cmd
kill -TERM 1495
```


## High Storage I/O Latency

Storage I/O latency occurs when reads, writes, or flush operations take longer than expected. Symptoms include slow file operations, delayed database commits, application timeouts, and processes waiting for I/O.
Common causes include workload exceeding storage capacity, shared-storage contention, IOPS or throughput limits, device errors and retries, and network-storage delays. High IOPS alone does not indicate a problem; latency can also increase under low load.
Diagnostic commands:

```sh
iostat -xz -y 1                   # Device latency, queue depth, IOPS and throughput
pidstat -d 1                      # Per-process I/O activity
findmnt -T /data/path             # Identify the affected filesystem
lsblk                             # Map storage devices and layers
vmstat 1                          # Check I/O wait and swap activity
journalctl -k --since "30 minutes ago"  # I/O errors, timeouts and resets
```
In iostat, inspect r_await and w_await (average completion time in milliseconds) and aqu-sz (average outstanding requests). Compare them with the normal baseline; %util alone does not prove saturation.
Correlate application slowdown with device latency and workload changes. High latency with growing queues during heavy activity suggests saturation; high latency under light activity suggests storage degradation, throttling, or infrastructure issues.

```sh
modprobe dm-delay
df -h /var/tmp

test ! -e /var/tmp/latency-lab.img &&
fallocate -l 512M /var/tmp/latency-lab.img
```
```sh
mkdir -p /mnt/latency-lab

LAT_LOOP=$(losetup --find --show /var/tmp/latency-lab.img)
LAT_SECTORS=$(blockdev --getsz "$LAT_LOOP")

dmsetup create latency-lab --table "0 $LAT_SECTORS linear $LAT_LOOP 0"

mkfs.ext4 -m 0 /dev/mapper/latency-lab
mount /dev/mapper/latency-lab /mnt/latency-lab
```

test I/O Latency
```sh
python3 - <<'PY'
import os
import time

with open("/mnt/latency-lab/probe.bin", "wb", buffering=0) as f:
    start = time.monotonic()
    for _ in range(20):
        f.write(b"x" * 4096)
        os.fsync(f.fileno())
    elapsed = time.monotonic() - start

print(f"Total: {elapsed:.3f}s; average write+fsync: {elapsed / 20:.3f}s")
PY
```

generate incident

```sh
dmsetup suspend latency-lab

dmsetup reload latency-lab --table "0 $LAT_SECTORS delay $LAT_LOOP 0 200"

dmsetup resume latency-lab
```
