# Linux Storage Fault Lab v19

A Bash fault-injection and recovery lab for learning Linux storage and filesystem troubleshooting on a **disposable, dedicated Linux VPS**. It uses loop-backed image files for most exercises. A small, explicit set of Level 5 scenarios modifies the VPS host itself.

## What this lab teaches

The 101 scenarios cover filesystem permissions and inode attributes, mount state and options, ext4, XFS, Btrfs, LVM, md RAID, LUKS, device mapper, I/O behavior, deleted-but-open files, partition-table recovery, and a file-level backup restoration drill. The intended workflow is to investigate symptoms before using `hint` or `reveal`, repair the problem, and verify the result with tools appropriate to the affected layer.

The catalog has 101 registered injection paths. A registered handler is not proof that every kernel/provider combination produces the same symptom. A few scenarios are explicitly analogues or timing-dependent. `verify` is scenario-specific for selected cases and reports manual checks for many others; do not treat a generic pass as proof of data integrity.

## Requirements

Use a new VPS that contains no needed data, has a rescue console, and can be deleted and recreated. Root access and working loop devices are required. Kernel features and provider restrictions vary.

Ubuntu/Debian example:

```bash
sudo apt update
sudo apt install -y util-linux e2fsprogs xfsprogs btrfs-progs \
  lvm2 mdadm cryptsetup gdisk parted fio python3 dmsetup attr acl \
  gddrescue
```

Run `doctor` to inspect available commands and devices before starting. Missing optional utilities only affect scenarios that depend on them.

## Start the lab

```bash

chmod +x storage-fault-lab.sh ./storage-fault-lab.sh selftest
sudo ./storage-fault-lab.sh doctor
sudo ./storage-fault-lab.sh init ./storage-fault-lab.sh catalog
```

`init` creates a 1 GiB ext4 image, attaches it as a loop device, and mounts it at `/mnt/storage-fault-lab-v2`. It also creates a random namespace for the lab's LVM, RAID, and device-mapper resource names to reduce collisions with existing host resources.

Inject a random case from a level or select one by ID:

```bash
sudo ./storage-fault-lab.sh inject --level 3
sudo ./storage-fault-lab.sh inject --level 5 --id 095
```

Then investigate before revealing the intended fault:

```bash
sudo ./storage-fault-lab.sh status
sudo ./storage-fault-lab.sh hint
sudo ./storage-fault-lab.sh verify
sudo ./storage-fault-lab.sh reveal
sudo ./storage-fault-lab.sh reset
```

Use `verify` after your repair and before `reveal`. For cases where it reports that manual validation is required, use filesystem-specific tools such as `e2fsck`, `xfs_repair`, `btrfs check`/`scrub`, `pvs`/`vgs`/`lvs`, `mdadm`, `cryptsetup`, `dmsetup`, `findmnt`, `lsblk`, `blkid`, `df`, `du`, and `/proc` as appropriate. Record the evidence and the recovery steps; a successful `reset` only recreates the lab environment.

## Operational incident track

Treat every injection as a timed incident drill. Before changing state, write down the reported impact, the scope you have confirmed, the evidence collected, the next safe action, and the condition that would make you stop and escalate. Keep command output and timestamps in a separate incident note. A compact template:

```text
Incident / start time:
Reported user impact:
Scope confirmed (host, device, mount, filesystem, service):
Evidence and commands:
Hypothesis and confidence:
Risk of next action / rollback:
Recovery performed:
Validation (data, filesystem, mount, service):
Escalation trigger / handoff:
```

Use read-only inspection first. For example, collect `date -Is`, `findmnt`, `lsblk -f`, `df -hT`, `df -i`, `dmesg -T | tail -n 100`, and relevant service logs before attempting repair. Identify the exact lab loop device and its backing image before any block-level command. If evidence suggests a real device or host resource, stop the drill and escalate instead of applying a repair command by analogy.

For blind practice, have a coordinator run the injection and give the responder only the reported symptom and user impact. The responder should state what is known, what remains uncertain, and what evidence they need before changing anything. Suitable cases include ID 051 (capacity exhaustion), 060 (thin-pool pressure), 062 (degraded RAID), 076 (checksum error), and 100 (space held by a deleted open file). The coordinator can use the intended diagnosis after the attempt to review whether the response protected data and service availability.

### Scenario 101: restore from a known-good file backup

This scenario creates a copy and SHA256 manifest outside the lab image, then changes `data/important.txt` on the disposable filesystem. Both copies remain on the same VPS, so this tests file-level restoration from an intact local copy; it does not test failure-domain separation, full-volume recovery, database consistency, or a production backup system.

```bash
sudo ./storage-fault-lab.sh inject --level 5 --id 101
sudo ./storage-fault-lab.sh status
sudo ./storage-fault-lab.sh verify   # expected to fail before repair
sudo sha256sum /mnt/storage-fault-lab-v2/data/important.txt
sudo cat /var/lib/storage-fault-lab-v2/backup-important.sha256
sudo cp -a /var/lib/storage-fault-lab-v2/backup-important.txt \
  /mnt/storage-fault-lab-v2/data/important.txt
sudo sync
sudo sha256sum /mnt/storage-fault-lab-v2/data/important.txt
sudo ./storage-fault-lab.sh verify   # should pass after restoration
```

In a complete drill, record why the backup is trusted, compare the restored checksum to the manifest, confirm ownership and permissions, and test the service-level read or operation that depends on the file. `reset` removes the lab's backup copy and recreates the lab image.

For a handoff, summarize impact, confirmed scope, evidence, changes already made, remaining uncertainty, and the next safe action. Do not report recovery as complete until the relevant filesystem checks and service-level validation have passed.

## Host-impacting scenarios

IDs **086** and **088** modify the VPS root filesystem or `/etc/fstab`. They are excluded from random selection and require an explicit ID plus `--allow-host`:

```bash
sudo ./storage-fault-lab.sh inject --level 5 --id 086 --allow-host
sudo ./storage-fault-lab.sh restore-host
```

For ID 088, `restore-host` removes the tagged test entry. Do not reboot until you have reviewed the change and confirmed console/rescue access. ID 086 consumes root filesystem space while retaining a small reserve, but can still disrupt services. Delete and recreate the VPS if recovery is uncertain. `reset` refuses to run while either host fault is active; use `restore-host` first.

## Important scenario limits

- ID 082 marks an ext4 filesystem unclean for an offline check; it does not reproduce power loss or genuine journal replay.
- ID 093 is a device-mapper path-switch analogue, not multipath or real path failover.
- ID 083 creates a device-mapper latency stall; it does not reproduce a block-device timeout.
- ID 078 attempts to cancel a Btrfs balance and records whether it was still running; the operation can finish before cancellation.
- ID 095 creates a device-mapper device with a deliberately unreadable range and runs GNU ddrescue against it. It practices partial imaging and mapfile interpretation; it does not emulate a physically failing disk.
- ID 100 fills the disposable lab filesystem while a deleted file remains open, so `df` and `du` disagree. It does not stop an external service.
- Other timing-sensitive I/O cases may vary with the kernel, storage provider, and installed tools.

## Recovery and reset

`reset` recreates the disposable 1 GiB image and removes lab-owned loop-backed resources. All data placed under `/mnt/storage-fault-lab-v2` is disposable. Never store personal files there. If an unmount or device removal is busy, inspect the active processes and mounts before retrying; do not force removal of a resource you cannot identify as belonging to this lab.

The script does not automatically repair the data filesystem for every scenario. Some recovery work is intentionally manual so that the exercise tests diagnosis and safe repair rather than only resetting state.

## Practice path and assessment

Work through the lab in four passes. The aim is to explain and validate a repair, not to memorize an injection ID or command sequence.

1. **Filesystem basics:** permissions and inode attributes (001-040), mounts and options (021-040), capacity and inode pressure (051-056), and deleted-open files (057, 100).
2. **Filesystem and storage layers:** ext4, XFS, Btrfs, partition tables, swap, LUKS, md RAID, and LVM (041-065, 076-082, 089-098).
3. **I/O diagnosis:** device-mapper faults, latency, writeback, cache, and queue behavior (066-075, 083-085, 094-095).
4. **Recovery and service validation:** application checksum, backup restoration, and host-impacting configuration only inside the required disposable VM (086, 088, 099, 101).

For a blind attempt, have a coordinator inject the case and tell the responder only the symptom and impact. The responder should first state the scope and unknowns, collect read-only evidence, then propose the lowest-risk next action and a stop/escalation condition. Keep `hint` and `reveal` for the debrief.

Score each attempt from 0 to 2 in five areas: safe evidence collection, diagnosis supported by evidence, risk-aware repair, filesystem/data/service validation, and clear incident handoff. A score of 2 means the responder independently did this well; 1 means partial or prompted; 0 means missing or unsafe. Treat any unbounded destructive command, unverified repair, or action on an unidentified device as a failed attempt regardless of total. Repeat with changed symptoms or a different fault in the same layer. Consider a skill reliable only after three consecutive blind passes with no safety failure and a correct explanation of what the evidence does and does not prove.

`selftest` is a static registry/handler check. It does not execute injections, prove runtime symptoms, or test repair commands. Before relying on a new scenario or script revision, run it on a disposable VM, confirm the symptom, rehearse recovery, run `verify`, and confirm reset removes only lab-owned resources. The current lab gives strong practice in local Linux storage diagnosis; it does not reproduce physical media failure, genuine multipath/SAN failover, provider-specific disk behavior, or the full production backup/recovery process.

The catalog is not a complete storage curriculum. Deliberate follow-on topics include SMART interpretation; LVM resize and snapshot recovery; RAID replacement and completed rebuild validation; ZFS pools and datasets; quotas; NFS/client-side mount failures; and boot recovery with encrypted root. Add these as separate, opt-in modules with their own prerequisites, expected evidence, tested repair path, and verifier. Do not represent loop-device analogues as tests of physical disk health or real SAN failover.

For every incident, keep a short note with symptoms, commands and evidence, affected layer, root cause, repair, and post-repair checks. Before each attempt, classify the likely layer (device, partition table, encryption, RAID/LVM, filesystem, mount, permissions, or application) and gather evidence without changing state. After repair, confirm both the immediate symptom and the relevant on-disk or kernel state. For mount and boot scenarios, include a reboot check only when the VPS console is available and the host change has been reviewed.

Repeat cases without hints until you can explain why the first observations distinguish the failing layer from adjacent layers. Then combine faults and practice recovery from backups or images. This lab supports that progression, but it does not replace reading filesystem documentation, testing restores, or learning provider-specific disk behavior.


```sh
#!/usr/bin/env bash
# Storage Fault Lab v19: disposable VPS storage and filesystem drills.
set -Eeuo pipefail
umask 077
BASE=/var/lib/storage-fault-lab-v2
IMG=$BASE/ext4.img
MNT=/mnt/storage-fault-lab-v2
STATE=$BASE/incident
RESULT=$BASE/last-result
HISTORY=$BASE/history
LOCK=$BASE/lock
SIZE_MB=1024
export LC_ALL=C
fail(){ printf 'ERROR: %s\n' "$*" >&2; exit 1; }
need_root(){ ((EUID==0)) || fail 'Run with sudo'; }
need(){ local x; for x in "$@"; do command -v "$x" >/dev/null || fail "Missing command: $x"; done; }
owned_mount(){ findmnt -rn -M "$MNT" -o SOURCE 2>/dev/null | grep -Eq '^/dev/loop[0-9]+$'; }
loop_for_image(){ losetup -j "$IMG" 2>/dev/null | awk -F: 'NR==1{print $1}'; }
stop_lab_pid(){
 local file=$1 pid cmdline
 [[ -s "$file" ]] || return 0
 pid=$(cat "$file")
 [[ "$pid" =~ ^[0-9]+$ ]] || fail "Invalid PID in $file"
 if [[ -r "/proc/$pid/cmdline" ]]; then
   cmdline=$(tr '\0' ' ' <"/proc/$pid/cmdline")
   [[ "$cmdline" == *"$BASE"* || "$cmdline" == *"$MNT"* ]] || fail "PID $pid no longer identifies a lab process; refusing to signal it"
   kill "$pid" 2>/dev/null || :
 fi
 rm -f "$file"
}
assert_safe(){
 [[ "$BASE" == /var/lib/storage-fault-lab-v2 && "$MNT" == /mnt/storage-fault-lab-v2 ]] || fail 'Unsafe paths';
 [[ ! -L "$BASE" && ! -L "$MNT" && ! -L "$IMG" ]] || fail 'Refusing symlink lab path/image';
 if findmnt -rn -M "$MNT" >/dev/null; then
   local src; src=$(findmnt -rn -M "$MNT" -o SOURCE)
   [[ "$src" == /dev/loop* ]] || fail "Foreign mount at $MNT: $src";
   [[ "$(losetup -n -O BACK-FILE "$src" 2>/dev/null)" == "$IMG" ]] || fail 'Mount is not our image';
 fi
}
cleanup_mount(){
 assert_safe
 if findmnt -rn -M "$MNT" >/dev/null; then umount "$MNT" || fail 'Mount busy; close processes in lab'; fi
 local dev; dev=$(loop_for_image)
 [[ -z "$dev" ]] || losetup -d "$dev" || fail 'Could not detach lab loop device'
}
prepare(){
 need_root; need losetup mkfs.ext4 mount umount findmnt truncate flock awk python3 chmod chown
 [[ ! -L "$BASE" && ! -L "$MNT" ]] || fail 'Refusing symlink lab directory'
 mkdir -p "$BASE" "$MNT"
 exec 9>"$LOCK"; flock -n 9 || fail 'Another lab command is running'
 [[ ! -L "$BASE/namespace" ]] || fail 'Refusing symlink namespace file'
 if [[ -s "$BASE/namespace" ]]; then LAB_TAG=$(<"$BASE/namespace")
 else LAB_TAG="sflab_$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')"; printf '%s\n' "$LAB_TAG" >"$BASE/namespace"; fi
 [[ "$LAB_TAG" =~ ^sflab_[0-9a-f]{8}$ ]] || fail 'Invalid lab namespace'
 assert_safe
}
load_lab_tag(){
 [[ -s "$BASE/namespace" && ! -L "$BASE/namespace" ]] || fail 'Lab namespace missing; run init first'
 LAB_TAG=$(<"$BASE/namespace")
 [[ "$LAB_TAG" =~ ^sflab_[0-9a-f]{8}$ ]] || fail 'Invalid lab namespace'
}
init(){
 [[ ! -f "$BASE/fstab-token" && ! -f "$BASE/rootfill-token" ]] || fail "Host fault active: run restore-host first"
 prepare; stop_lab_pid "$BASE/holder.pid"
 stop_lab_pid "$BASE/orphan.pid"
 cleanup_mount
 if [[ -f "$BASE/meta.pid" ]]; then kill "$(cat "$BASE/meta.pid")" 2>/dev/null || :; rm -f "$BASE/meta.pid"; fi
 if [[ -f "$BASE/fio.pid" ]]; then kill "$(cat "$BASE/fio.pid")" 2>/dev/null || :; fi
 if [[ -f "$BASE/dblocked.pid" ]]; then
   # The reader can be uninterruptible until the delayed I/O completes.
   kill "$(cat "$BASE/dblocked.pid")" 2>/dev/null || :
 fi
 if [[ -f "$BASE/writeback.pid" ]]; then kill "$(cat "$BASE/writeback.pid")" 2>/dev/null || :; fi
 if command -v cryptsetup >/dev/null && cryptsetup status ${LAB_TAG}_092 >/dev/null 2>&1; then cryptsetup close ${LAB_TAG}_092 || fail "Encrypted lab mapping busy"; fi
 if [[ -d "$BASE/btrfs-mnt" ]] && findmnt -rn -M "$BASE/btrfs-mnt" >/dev/null; then
   local bsrc; bsrc=$(findmnt -rn -M "$BASE/btrfs-mnt" -o SOURCE)
   [[ "$bsrc" == /dev/loop* ]] || fail "Foreign mount at $BASE/btrfs-mnt: $bsrc"
   [[ "$(losetup -n -O BACK-FILE "$bsrc" 2>/dev/null)" == "$BASE/btrfs.img" || "$(losetup -n -O BACK-FILE "$bsrc" 2>/dev/null)" == "$BASE/btrfs-a.img" ]] || fail 'Btrfs mount is not backed by a lab image'
   umount "$BASE/btrfs-mnt" || fail 'Btrfs lab mount busy'
 fi
 if command -v dmsetup >/dev/null && dmsetup info ${LAB_TAG}_path >/dev/null 2>&1; then dmsetup remove -f ${LAB_TAG}_path || fail "Path mapping busy"; fi
 if command -v dmsetup >/dev/null && dmsetup info ${LAB_TAG}_fault >/dev/null 2>&1; then dmsetup remove -f ${LAB_TAG}_fault || fail 'dm target busy'; fi
 if command -v mdadm >/dev/null && [[ -e /dev/md/${LAB_TAG} ]]; then mdadm --stop /dev/md/${LAB_TAG} || fail 'md lab busy'; fi
 if command -v vgchange >/dev/null; then for vg in ${LAB_TAG}_059 ${LAB_TAG}_060 ${LAB_TAG}_061 ${LAB_TAG}_090 ${LAB_TAG}_092; do vgchange -an "$vg" >/dev/null 2>&1 || :; vgremove -ff -y "$vg" >/dev/null 2>&1 || :; done
 fi
 for f in "$BASE"/{lvm,raid,dm}-devices "$BASE"/dm-device; do
   [[ -f "$f" ]] || continue
   while read -r d; do [[ "$d" == /dev/loop* ]] && losetup -d "$d" 2>/dev/null || :; done < "$f"
 done
 for f in "$BASE"/{xfs,btrfs,lvm-a,lvm-b,raid-a,raid-b,raid-c,dm,gpt,swap,luks,luks-stack,path-a,path-b}.img; do
   [[ -f "$f" ]] || continue
   while read -r d; do losetup -d "$d" 2>/dev/null || :; done < <(losetup -j "$f" | cut -d: -f1)
 done
 rm -f "$BASE"/{path-a,path-b}.img "$BASE/path-devices" "$BASE"/{xfs,btrfs,lvm-a,lvm-b,raid-a,raid-b,raid-c,dm,gpt,swap,luks}.img "$BASE"/{lvm,raid,dm}-devices "$BASE"/dm-device "$BASE"/gpt-backup "$BASE"/luks-stack.img "$BASE"/luks.key "$BASE"/luks.header "$BASE"/vg061.backup "$BASE"/meta.log "$BASE"/fio.pid "$BASE"/fio.log "$BASE"/writeback.pid "$BASE"/writeback.log "$BASE"/dblocked.pid "$BASE"/dblocked.log "$BASE"/coldcache.txt "$BASE"/app-manifest.sha256 "$BASE"/balance.log "$BASE"/balance-status.txt "$BASE"/recovered.img "$BASE"/ddrescue.map "$BASE"/ddrescue.log
 rm -f "$BASE/backup-important.txt" "$BASE/backup-important.sha256"
 [[ ! -L "$IMG" ]] || fail 'Refusing symlink image'
 rm -f -- "$IMG" "$STATE" "$RESULT" "$BASE/clone.img" "$BASE/directio-result" "$BASE/holder.pid" "$BASE/orphan.pid"

 truncate -s "${SIZE_MB}M" "$IMG"
 mkfs.ext4 -F -q "$IMG"
 local dev; dev=$(losetup --find --show "$IMG")
 mount -t ext4 "$dev" "$MNT" || { losetup -d "$dev"; fail 'Mount failed'; }
 mkdir -p "$MNT"/{data,logs,archive,tmp,config,work}
 chmod 755 "$MNT"/{data,logs,archive,tmp,config,work}
 printf 'CANARY:storage-lab-v2\n' >"$MNT/data/important.txt"
 printf 'service healthy\n' >"$MNT/logs/service.log"
 printf 'mode=normal\n' >"$MNT/config/service.conf"
 printf 'payload\n' >"$MNT/work/payload.txt"
 chmod 644 "$MNT"/{data/important.txt,logs/service.log,config/service.conf,work/payload.txt}
 sync
 echo "READY: disposable $SIZE_MB MiB ext4 loop filesystem at $MNT"
}
# Registry: ID|level|short diagnosis|hint|injection type|argument
# Only entries with a nonempty implementation are selectable. Unimplemented cases are explicitly listed in catalog.
CATALOG=$(cat <<'EOF'
001|1|data directory lacks traversal|Check namei and directory execute bits|chmoddir|data:000
002|1|data file inaccessible to ordinary users|Check mode and owner|chmodfile|data/important.txt:000
003|1|important file moved to archive|Search other lab directories|move|data/important.txt:archive/important.txt
004|1|dangling symbolic link|Inspect symlink target|symlink|data/current:/missing/target
005|1|logs directory read-only to users|Inspect directory write bit|chmoddir|logs:555
006|1|archive directory inaccessible|Inspect directory modes|chmoddir|archive:000
007|1|data directory traverse-only|Check listing vs traversal|chmoddir|data:111
008|1|service log unreadable|Inspect file permissions|chmodfile|logs/service.log:000
009|1|config file absent|Search archive for missing config|move|config/service.conf:archive/service.conf
010|1|broken relative symlink|Inspect relative symlink resolution|symlink|work/latest:../../absent
011|1|important file wrong ownership|Inspect numeric UID/GID|owner|data/important.txt:65534
012|1|logs directory wrong ownership|Inspect directory ownership|owner|logs:65534
013|1|config directory inaccessible|Check all parent directory permissions|chmoddir|config:000
014|1|work directory non-writable|Check write bit on directory|chmoddir|work:555
015|1|payload moved into hidden directory|Use find including dot paths|hide|work/payload.txt:work/.cache/payload.txt
016|1|data directory SGID confusion|Inspect special mode bits|chmoddir|data:2755
017|1|service log unexpectedly executable|Inspect mode bits|chmodfile|logs/service.log:755
018|1|config file has no read permission|Inspect file mode|chmodfile|config/service.conf:200
019|1|missing expected work symlink|Check links and paths|symlink|work/current:/absent/file
020|1|mount point inaccessible to ordinary users|Inspect mountpoint permission|chmodroot|000
021|2|immutable important file|Inspect lsattr|chattr|data/important.txt:+i
022|2|append-only service log|Inspect lsattr|chattr|logs/service.log:+a
023|2|filesystem remounted read-only|Inspect findmnt mount options|remount|ro
024|2|filesystem unmounted|Inspect mount table and loop devices|unmount|plain
025|2|filesystem mounted noexec|Inspect mount flags|remount|noexec
026|2|filesystem mounted nosuid|Inspect mount flags|remount|nosuid
027|2|filesystem mounted nodev|Inspect mount flags|remount|nodev
028|2|data directory has sticky bit|Inspect special permissions|chmoddir|data:1755
029|2|work directory mode blocks traversal|Inspect namei -l|chmoddir|work:600
030|2|config file append-only|Inspect lsattr|chattr|config/service.conf:+a
031|2|config file immutable|Inspect lsattr|chattr|config/service.conf:+i
032|2|payload immutable|Inspect lsattr|chattr|work/payload.txt:+i
033|2|payload append-only|Inspect lsattr|chattr|work/payload.txt:+a
034|2|data directory owned by nobody|Inspect numeric ownership|owner|data:65534
035|2|important file hidden in work|Search full lab tree|move|data/important.txt:work/important.txt
036|2|service log moved to archive|Find file by name|move|logs/service.log:archive/service.log
037|2|work directory not searchable|Inspect directory execute bit|chmoddir|work:400
038|2|filesystem remounted sync|Inspect mount options|remount|sync
039|2|filesystem remounted dirsync|Inspect mount options|remount|dirsync
040|2|config directory inaccessible|Inspect ACL/mode of parent path|chmoddir|config:111
041|3|ext4 superblock primary magic corruption|Inspect e2fsck offline and backup superblocks|magic|zero
042|3|ext4 superblock primary magic corruption variant|Inspect ext4 superblock magic offline|magic|dead
043|3|ext4 superblock primary magic corruption variant|Inspect alternate superblocks|magic|beef
044|3|read-only mount plus inaccessible data directory|Check both mount options and permissions|combo|ro-perm
045|3|immutable file plus inaccessible data directory|Inspect both lsattr and namei|combo|immutable-perm
046|3|append-only log plus nonwritable logs directory|Inspect inode attributes and parent permissions|combo|append-perm
047|3|unmounted filesystem and missing expected file|Inspect mount state before searching paths|combo|unmount-move
048|3|read-only filesystem plus immutable file|Inspect mount flags and inode flags|combo|ro-immutable
049|3|noexec filesystem plus execute-only work directory|Inspect mount flags and mode bits|combo|noexec-perm
050|3|data file moved and data directory inaccessible|Search all directories after fixing traversal|combo|move-perm
051|3|filesystem full via generated filler|Inspect df and largest files|fill|large
052|3|filesystem full via hidden filler|Inspect dot files and df|fill|hidden
053|3|filesystem full via log filler|Inspect log size and df|fill|logs
054|3|filesystem full via work filler|Inspect du by directory|fill|work
055|3|inode exhaustion in disposable ext4 filesystem|Inspect df -i and inode count|inodes|128
056|3|ext4 reserved-block pressure|Inspect tune2fs reserved block percentage|reserve|40
057|3|ext4 orphan inode cleanup|Find unlinked open inode and its owning process; inspect /proc/*/fd|orphanhold|open-unlinked
058|3|XFS metadata corruption|Inspect xfs_repair on an offline XFS image|xfsdamage|metadata
059|3|LVM partial volume group|Inspect pvs vgs and missing PVs|lvmpartial|missing
060|3|LVM thin-pool exhaustion|Inspect lvs -a and thin pool Data%|thinfull|data
061|3|LVM metadata backup restore|Inspect vgcfgbackup and missing VG metadata|lvmmissing|metadata
062|3|RAID1 degraded member|Inspect mdadm --detail and /proc/mdstat|raiddegrade|fail
063|3|RAID1 assemble failure|Inspect mdadm --examine and assemble stopped array|raidstop|stopped
064|3|LUKS header recovery|Inspect luksDump and backed-up header|luksbad|header
065|3|swap activation failure|Inspect swap signature and swapon errors|swapbad|signature
066|4|dm-flakey transient IO errors|Inspect dmsetup table and timed read failures|dmfault|flakey
067|4|dm-delay high latency|Inspect device mapper table and read latency|dmfault|delay
068|4|dm-error persistent IO errors|Inspect device mapper target and read errors|dmfault|error
069|4|fsync latency regression|Inspect dmsetup delay target and fsync benchmark|dmfault|delay
070|4|dirty-page writeback pressure|Inspect Dirty and Writeback in /proc/meminfo and background buffered writer|writebackload|buffered
071|4|random-write throughput collapse|Inspect running workload and fio options|ioload|random
072|4|I/O queue congestion|Inspect iostat and active workload|ioload|queue
073|4|direct I/O alignment failure|Investigate O_DIRECT buffer alignment and errno|directio|unaligned
074|4|page-cache cold read regression|Inspect posix_fadvise DONTNEED and compare cold vs warm read|coldcache|fadvise
075|4|filesystem metadata contention|Inspect many metadata operations in lab directory|metaload|files
076|4|Btrfs checksum error|Inspect scrub checksum errors on a damaged data extent|btrfschecksum|data
077|4|Btrfs ENOSPC despite free blocks|Inspect btrfs filesystem usage and metadata allocation|btrfsfull|data
078|4|Btrfs balance cancellation (timing-dependent)|Inspect btrfs balance status; cancel only while running|btrfsbalance|cancel
079|4|Btrfs missing device|Inspect missing device and degraded mount|btrfsmissing|device
080|4|Btrfs snapshot space retention|Inspect subvolume list and snapshots|btrfssnapshot|retained
081|4|XFS repair and replay|Inspect xfs_repair diagnostics for damaged metadata|xfsdamage|metadata
082|4|ext4 unclean-state recovery drill (not power-loss journal replay)|Inspect offline ext4 state with tune2fs and e2fsck|uncleanext4|state
083|4|block device latency stall (not a device timeout)|Inspect dm-delay block-device response times|dmfault|delay
084|4|writeback error propagation|Inspect writeback fsync errno on dm-error device|dmfault|error
085|4|D-state I/O blocked task|Inspect ps state and dmsetup delay target; D state is timing-dependent|dblocked|reader
086|5|root filesystem full (boot risk)|Inspect df, stat -f, reserved blocks and large files|hostrootfull|root-fill
087|5|read-only remount on sacrificial filesystem (root analogue)|Inspect findmnt options and remount state; this is NOT host root|rootroanalog|ro
088|5|broken fstab emergency mode|Inspect /etc/fstab, findmnt --verify, systemd mount dependencies|hostfstab|invalid-required-uuid
089|5|root-superblock corruption analogue on isolated ext4|Inspect alternate superblocks and offline e2fsck; NOT host root|rootmagicanalog|magic
090|5|LVM and ext4 simultaneous failures|Inspect VG activation and ext4 superblock|lvmext4|stack
091|5|RAID degraded and ext4 corruption|Inspect mdadm state and ext4 offline repair|raidext4|stack
092|5|LUKS plus LVM unlock failure|Inspect cryptsetup status and LVM activation under decrypted mapping|luksstack|closed
093|5|device-mapper path switch analogue (NOT genuine multipath)|Inspect dmsetup table, two loop paths and reload mapping|pathswitch|linear
094|5|disk intermittently disconnects|Inspect intermittent I/O errors using dm-flakey|dmfault|flakey
095|5|recover readable ranges from a failing block device|Inspect the dm-error range, recovered image and ddrescue mapfile|ddrescue|partial-read
096|5|duplicate filesystem UUID after clone|Compare blkid UUID for two images|duplicateuuid|clone
097|5|partition table deleted and recovered|Inspect partition table with sfdisk and backup signatures|partitionwipe|gpt
098|5|mdraid rebuild interrupted|Inspect mdadm detail and recovery state after an interrupted rebuild|raidrebuild|interrupted
099|5|filesystem and application consistency mismatch|Compare application manifest SHA256 with on-disk payload|appmismatch|checksum
100|5|filesystem full with space held by a deleted open file|Compare df and du; inspect /proc/*/fd and stop the holder|deletedopen|hold
101|5|restore a corrupted service file from a known-good backup|Compare SHA256 evidence, restore the backup, and verify its contents|backuprestore|important-file
EOF
)
row(){ awk -F'|' -v id="$1" '$1==id{print; exit}' <<<"$CATALOG"; }
select_case(){
 local level=$1 pool chosen id
 pool=$(awk -F'|' -v l="$level" '$2==l && $5!="" && $5!="hostfstab" && $5!="hostrootfull"{print $1}' <<<"$CATALOG")
 [[ -n "$pool" ]] || fail "Level $level has no implemented scenarios; see catalog"
 local unused=""; while read -r id; do
   [[ -z "$id" ]] && continue
   if ! grep -qx "$id" "$HISTORY" 2>/dev/null; then unused+="$id"$'\n'; fi
 done <<<"$pool"
 if [[ -z "$unused" ]]; then
   # Clear only this level's history; keep history for other levels.
   if [[ -f "$HISTORY" ]]; then grep -vxFf <(printf '%s\n' "$pool") "$HISTORY" >"$HISTORY.tmp" || :; mv "$HISTORY.tmp" "$HISTORY"; fi
   unused="$pool"
 fi
 mapfile -t choices < <(printf '%s\n' "$unused" | sed '/^$/d')
 chosen=$(od -An -N4 -tu4 /dev/urandom | tr -d ' ')
 printf '%s\n' "${choices[chosen % ${#choices[@]}]}"
}
apply(){
 local kind=$1 arg=$2 a b dev
 case "$kind" in
 uncleanext4)
   # Simulates an unclean ext4 state; cannot claim genuine power-loss replay.
   need debugfs e2fsck tune2fs
   cleanup_mount
   debugfs -w -R 'set_super_value state 0' "$IMG" >/dev/null 2>&1
   [[ "$(tune2fs -l "$IMG" | awk -F: '/Filesystem state:/{print $2}')" != *clean* ]] || fail 'Could not mark ext4 unclean'
   ;;
 rootroanalog)
   mount -o remount,ro "$MNT"
   findmnt -rn -M "$MNT" -o OPTIONS | grep -Eq '(^|,)ro(,|$)' || fail 'Read-only remount not observed'
   ;;
 rootmagicanalog)
   cleanup_mount
   python3 - "$IMG" <<'PYMAGIC'
import sys
with open(sys.argv[1], 'r+b', buffering=0) as f:
    f.seek(1024+56)
    f.write(b'\0\0')
PYMAGIC
   [[ "$(od -An -tx1 -j1080 -N2 "$IMG" | tr -d ' \n')" == 0000 ]] || fail 'Superblock damage not observed'
   ;;
 pathswitch)
   need dmsetup blockdev
   truncate -s 96M "$BASE/path-a.img"
   cp -- "$BASE/path-a.img" "$BASE/path-b.img"
   local path_a path_b sectors
   path_a=$(losetup --find --show "$BASE/path-a.img")
   path_b=$(losetup --find --show "$BASE/path-b.img")
   printf '%s\n%s\n' "$path_a" "$path_b" > "$BASE/path-devices"
   sectors=$(blockdev --getsz "$path_a")
   printf '0 %s linear %s 0\n' "$sectors" "$path_a" | dmsetup create ${LAB_TAG}_path
   # A controllable two-path *analogue*: only one linear path is active.
   # Recovery drill: dmsetup suspend; dmsetup reload; dmsetup resume.
   [[ -e /dev/mapper/${LAB_TAG}_path ]] || fail 'Mapper path not created'
   ;;
 chmoddir|chmodfile|chmodroot)
   if [[ "$kind" == chmodroot ]]; then chmod "$arg" "$MNT"; else IFS=: read -r a b <<<"$arg"; chmod "$b" "$MNT/$a"; fi;;
  hostrootfull)
   # Only for a disposable VPS. Creates a uniquely named regular file on /.
   # Stops with a small reserve so that SSH/rescue commands may still function.
   [[ "$arg" == root-fill ]] || fail 'Unknown host root-full fault'
   [[ ! -e "$BASE/rootfill-token" ]] || fail 'Root fill already active'
   [[ "$(findmnt -n -o FSTYPE -T /)" != overlay ]] || fail 'Refusing overlay root'
   local target=/storage-fault-lab-rootfill.img
   [[ ! -e "$target" && ! -L "$target" ]] || fail "Target already exists: $target"
   : > "$BASE/rootfill-token"
   printf '%s\n' "$target" > "$BASE/rootfill-token"
   python3 - "$target" <<'PYFILL'
import os,sys
p=sys.argv[1]
fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
chunk=b'F'*(4*1024*1024)
try:
    while True:
        st=os.statvfs('/')
        # f_bavail is the space non-root processes can use.
        # Keep 32 MiB available to non-root users.
        if st.f_bavail*st.f_frsize <= 32*1024*1024: break
        remaining=st.f_bavail*st.f_frsize-32*1024*1024
        try: os.write(fd,chunk[:min(len(chunk),remaining)])
        except OSError as e:
            if e.errno==28: break
            raise
    os.fsync(fd)
finally: os.close(fd)
PYFILL
   echo 'Root free space reduced. This is NOT a guaranteed boot failure; inspect df and journal.'
   ;;
  hostfstab)
   [[ "$arg" == invalid-required-uuid ]] || fail 'Unknown host fault'
   [[ -f /etc/fstab && ! -L /etc/fstab ]] || fail 'Unexpected fstab path'
   [[ ! -e "$BASE/fstab.original" ]] || fail 'fstab backup exists; restore first'
   cp -a -- /etc/fstab "$BASE/fstab.original"
   local token
   token="SFLAB-088-$(cat /proc/sys/kernel/random/uuid)"
   printf '\n# STORAGE-FAULT-LAB-088 (restore with restore-host)\nUUID=%s /mnt/sflab-088-missing ext4 defaults 0 2\n' "$token" >> /etc/fstab
   printf '%s\n' "$token" > "$BASE/fstab-token"
   echo 'Host /etc/fstab modified. Reboot manually to observe boot failure; rescue console may be required.'
   ;;
 owner) IFS=: read -r a b <<<"$arg"; chown "$b:$b" "$MNT/$a";;
 move) IFS=: read -r a b <<<"$arg"; mv -- "$MNT/$a" "$MNT/$b";;
 hide) IFS=: read -r a b <<<"$arg"; mkdir -p "$(dirname "$MNT/$b")"; mv -- "$MNT/$a" "$MNT/$b";;
 symlink) IFS=: read -r a b <<<"$arg"; ln -s -- "$b" "$MNT/$a";;
 chattr) need chattr; IFS=: read -r a b <<<"$arg"; chattr "$b" "$MNT/$a";;
 remount) mount -o "remount,$arg" "$MNT";;
 unmount) umount "$MNT";;
 magic)
   dev=$(loop_for_image); [[ -n "$dev" ]] || fail 'Loop device missing'
   umount "$MNT"
   python3 - "$IMG" "$arg" <<'PY'
import sys
payload={'zero':bytes.fromhex('0000'),'dead':bytes.fromhex('dead'),'beef':bytes.fromhex('beef')}[sys.argv[2]]
with open(sys.argv[1],'r+b',buffering=0) as f:
    f.seek(1024+56)
    f.write(payload)
PY
   ;;
 combo)
   case "$arg" in
    ro-perm) chmod 000 "$MNT/data"; mount -o remount,ro "$MNT";;
    immutable-perm) chattr +i "$MNT/data/important.txt"; chmod 000 "$MNT/data";;
    append-perm) chattr +a "$MNT/logs/service.log"; chmod 555 "$MNT/logs";;
    unmount-move) mv "$MNT/data/important.txt" "$MNT/archive/important.txt"; umount "$MNT";;
    ro-immutable) chattr +i "$MNT/data/important.txt"; mount -o remount,ro "$MNT";;
    noexec-perm) chmod 111 "$MNT/work"; mount -o remount,noexec "$MNT";;
    move-perm) mv "$MNT/data/important.txt" "$MNT/archive/important.txt"; chmod 000 "$MNT/data";;
   esac;;
 inodes)
   # Recreate only the owned image with very few inodes; all existing lab data is disposable.
   cleanup_mount
   mkfs.ext4 -F -q -N "$arg" "$IMG"
   dev=$(losetup --find --show "$IMG")
   mount -t ext4 "$dev" "$MNT"
   mkdir -p "$MNT/data" "$MNT/work"
   printf 'CANARY:storage-lab-v3\n' > "$MNT/data/important.txt"
   local n=0
   while :; do
     if ! touch "$MNT/work/f$n" 2>/dev/null; then break; fi
     ((n+=1))
     ((n<2000)) || break
   done
   sync;;
 reserve)
   need tune2fs
   dev=$(loop_for_image)
   [[ -n "$dev" ]] || fail 'Loop device missing'
   tune2fs -m "$arg" "$dev" >/dev/null;;
 fill)
   local dest="$MNT/work/filler.bin"
   case "$arg" in hidden) dest="$MNT/.filler.bin";; logs) dest="$MNT/logs/big.log";; work) dest="$MNT/work/filler.bin";; esac
   # Only write to disposable image; bound by its capacity.
   dd if=/dev/zero of="$dest" bs=1M count=990 status=none || :
   sync;;
 duplicateuuid)
   need blkid
   cp --reflink=never -- "$IMG" "$BASE/clone.img"
   [[ "$(blkid -p -s UUID -o value "$IMG")" == "$(blkid -p -s UUID -o value "$BASE/clone.img")" ]] || fail 'UUID clone mismatch';;
 directio)
   python3 - "$MNT/work/unaligned.bin" "$BASE/directio-result" <<'PYDIRECT'
import os,sys
if not hasattr(os,'O_DIRECT'):
    raise SystemExit('O_DIRECT unsupported on this platform')
fd=os.open(sys.argv[1],os.O_CREAT|os.O_RDWR|os.O_DIRECT,0o600)
try:
    try: os.write(fd,b'X'*4096)
    except OSError as e: open(sys.argv[2],'w').write(f'errno={e.errno} {e.strerror}\n')
    else: raise SystemExit('Unaligned O_DIRECT unexpectedly succeeded')
finally: os.close(fd)
PYDIRECT
   ;;
 xfsdamage)
   need mkfs.xfs xfs_repair
   truncate -s 320M "$BASE/xfs.img"
   mkfs.xfs -f -q "$BASE/xfs.img"
   # Corrupt primary superblock only, while filesystem is unmounted.
   python3 - "$BASE/xfs.img" <<'PYXFS'
import sys
with open(sys.argv[1],'r+b',buffering=0) as f: f.write(b'XXXX')
PYXFS
   ;;
 lvmpartial)
   need pvcreate vgcreate lvcreate vgs pvs
   truncate -s 160M "$BASE/lvm-a.img"
   truncate -s 160M "$BASE/lvm-b.img"
   local la lb
   la=$(losetup --find --show "$BASE/lvm-a.img")
   lb=$(losetup --find --show "$BASE/lvm-b.img")
   printf '%s\n%s\n' "$la" "$lb" >"$BASE/lvm-devices"
   pvcreate -ff -y "$la" "$lb" >/dev/null
   vgcreate "${LAB_TAG}_059" "$la" "$lb" >/dev/null
   lvcreate -L 220M -n data "${LAB_TAG}_059" >/dev/null
   # Mark one PV missing using an inaccessible loop device.
   losetup -d "$lb"
   ;;
 thinfull)
   need pvcreate vgcreate lvcreate lvs
   truncate -s 384M "$BASE/lvm-a.img"
   local la; la=$(losetup --find --show "$BASE/lvm-a.img")
   printf '%s\n' "$la" >"$BASE/lvm-devices"
   pvcreate -ff -y "$la" >/dev/null
   vgcreate ${LAB_TAG}_060 "$la" >/dev/null
   lvcreate -L 220M -T ${LAB_TAG}_060/pool >/dev/null
   lvcreate -V 350M -T ${LAB_TAG}_060/pool -n data >/dev/null
   # Write to the virtual thin volume, bounded by its disposable backing PV.
   dd if=/dev/zero of=/dev/${LAB_TAG}_060/data bs=1M count=260 oflag=direct status=none 2>/dev/null || :
   lvs --noheadings -o data_percent ${LAB_TAG}_060/pool | grep -Eq '[0-9]' || fail 'Thin pool not initialized';;
 lvmmissing)
   need pvcreate vgcreate vgcfgbackup vgremove
   truncate -s 192M "$BASE/lvm-a.img"
   local la; la=$(losetup --find --show "$BASE/lvm-a.img")
   printf '%s\n' "$la" >"$BASE/lvm-devices"
   pvcreate -ff -y "$la" >/dev/null
   vgcreate ${LAB_TAG}_061 "$la" >/dev/null
   vgcfgbackup -f "$BASE/vg061.backup" ${LAB_TAG}_061 >/dev/null
   vgremove -ff -y ${LAB_TAG}_061 >/dev/null;;
 luksbad)
   need cryptsetup
   truncate -s 96M "$BASE/luks.img"
   local keyfile="$BASE/luks.key"
   head -c 64 /dev/urandom > "$keyfile"
   cryptsetup luksFormat --type luks2 --batch-mode --key-file "$keyfile" "$BASE/luks.img" >/dev/null
   cryptsetup luksHeaderBackup "$BASE/luks.img" --header-backup-file "$BASE/luks.header" >/dev/null
   python3 - "$BASE/luks.img" <<'PYLUKS'
import sys
with open(sys.argv[1],'r+b',buffering=0) as f:
 f.write(b'BROKEN!!')
 f.seek(0x4000); f.write(b'BROKEN!!')
PYLUKS
   ;;
 metaload)
   need python3
   (python3 - "$MNT/work" <<'PYMETA'
import os,sys,time
p=sys.argv[1]; end=time.monotonic()+150
while time.monotonic()<end:
 for i in range(150):
  q=os.path.join(p,f'meta-{i}'); open(q,'ab').close(); os.stat(q)
 for i in range(150):
  q=os.path.join(p,f'meta-{i}'); os.unlink(q)
PYMETA
   ) >"$BASE/meta.log" 2>&1 &
   echo "$!" > "$BASE/meta.pid";;
 btrfschecksum)
   need mkfs.btrfs btrfs filefrag
   truncate -s 512M "$BASE/btrfs.img"
   mkfs.btrfs -f -q "$BASE/btrfs.img"
   local bd offset
   bd=$(losetup --find --show "$BASE/btrfs.img")
   mkdir -p "$BASE/btrfs-mnt"
   mount "$bd" "$BASE/btrfs-mnt"
   python3 - "$BASE/btrfs-mnt/payload.bin" <<'PYBTRFSPAYLOAD'
import os,sys
with open(sys.argv[1],'wb') as f:
 f.write(os.urandom(8*1024*1024));f.flush();os.fsync(f.fileno())
PYBTRFSPAYLOAD
   # fiemap returns physical byte offsets in the btrfs device; no compression or snapshots.
   offset=$(filefrag -b1 -v "$BASE/btrfs-mnt/payload.bin" | awk '$1=="0:" {gsub(/\./,"",$4); sub(/:$/, "", $4); print $4; exit}')
   [[ "$offset" =~ ^[0-9]+$ ]] || fail 'Cannot determine physical data extent'
   umount "$BASE/btrfs-mnt"
   python3 - "$BASE/btrfs.img" "$offset" <<'PYBTRFSCORRUPT'
import sys
p,off=sys.argv[1],int(sys.argv[2]); assert off>1024*1024
with open(p,'r+b',buffering=0) as f:
 f.seek(off+128); old=f.read(1); f.seek(off+128); f.write(bytes([old[0]^0xff]))
PYBTRFSCORRUPT
   mount "$bd" "$BASE/btrfs-mnt"
   ;;
 btrfsmissing)
   need mkfs.btrfs btrfs
   truncate -s 512M "$BASE/btrfs-a.img"
   truncate -s 512M "$BASE/btrfs-b.img"
   local a b
   a=$(losetup --find --show "$BASE/btrfs-a.img")
   b=$(losetup --find --show "$BASE/btrfs-b.img")
   printf '%s\n%s\n' "$a" "$b" > "$BASE/btrfs-devices"
   mkfs.btrfs -f -q -d raid1 -m raid1 "$a" "$b"
   mkdir -p "$BASE/btrfs-mnt"
   mount "$a" "$BASE/btrfs-mnt"
   echo 'redundant data' > "$BASE/btrfs-mnt/test.txt"
   sync
   umount "$BASE/btrfs-mnt"
   losetup -d "$b"
   # Leave only the first member attached; recover with degraded mount.
   ;;
 btrfsfull)
   need mkfs.btrfs btrfs
   truncate -s 320M "$BASE/btrfs.img"
   mkfs.btrfs -f -q "$BASE/btrfs.img"
   local bd; bd=$(losetup --find --show "$BASE/btrfs.img")
   mkdir -p "$BASE/btrfs-mnt"
   mount "$bd" "$BASE/btrfs-mnt"
   dd if=/dev/urandom of="$BASE/btrfs-mnt/fill.bin" bs=1M count=400 status=none 2>/dev/null || :
   sync;;
 btrfsbalance)
   need mkfs.btrfs btrfs
   truncate -s 384M "$BASE/btrfs.img"
   mkfs.btrfs -f -q "$BASE/btrfs.img"
   local bd; bd=$(losetup --find --show "$BASE/btrfs.img")
   mkdir -p "$BASE/btrfs-mnt"
   mount "$bd" "$BASE/btrfs-mnt"
   dd if=/dev/urandom of="$BASE/btrfs-mnt/balance.dat" bs=1M count=120 status=none
   sync
   btrfs balance start -dusage=0 "$BASE/btrfs-mnt" >"$BASE/balance.log" 2>&1 &
   local balance_pid=$! tries=0 active=0
   while ((tries<30)); do
     if btrfs balance status "$BASE/btrfs-mnt" 2>/dev/null | grep -q 'is running'; then active=1; break; fi
     kill -0 "$balance_pid" 2>/dev/null || break
     sleep 0.1; ((tries+=1))
   done
   if ((active)); then btrfs balance cancel "$BASE/btrfs-mnt" >/dev/null 2>&1 || :; wait "$balance_pid" 2>/dev/null || :
   else wait "$balance_pid" 2>/dev/null || :; echo 'Balance completed before cancellation; this timing-dependent attempt did not produce a running balance.' >>"$BASE/balance.log"; fi
   btrfs balance status "$BASE/btrfs-mnt" >"$BASE/balance-status.txt" 2>&1 || :;;
 lvmext4)
   need pvcreate vgcreate lvcreate
   truncate -s 256M "$BASE/lvm-a.img"
   local la; la=$(losetup --find --show "$BASE/lvm-a.img")
   printf '%s\n' "$la" >"$BASE/lvm-devices"
   pvcreate -ff -y "$la" >/dev/null; vgcreate ${LAB_TAG}_090 "$la" >/dev/null
   lvcreate -L 128M -n data ${LAB_TAG}_090 >/dev/null
   mkfs.ext4 -F -q /dev/${LAB_TAG}_090/data
   python3 - /dev/${LAB_TAG}_090/data <<'PYLVMEXT'
import sys
with open(sys.argv[1],'r+b',buffering=0) as f: f.seek(1080);f.write(b'XX')
PYLVMEXT
   lvchange -an ${LAB_TAG}_090/data;;
 raidext4)
   apply raiddegrade fail
   mkfs.ext4 -F -q /dev/md/${LAB_TAG}
   python3 - /dev/md/${LAB_TAG} <<'PYRAIDEXT'
import sys
with open(sys.argv[1],'r+b',buffering=0) as f: f.seek(1080);f.write(b'XX')
PYRAIDEXT
   ;;
 raidrebuild)
   # Create a degraded array and attempt a replacement-member rebuild, then
   # interrupt it.  Only lab-owned loop devices and /dev/md/${LAB_TAG} are used.
   apply raiddegrade fail
   local replacement
   truncate -s 128M "$BASE/raid-c.img"
   replacement=$(losetup --find --show "$BASE/raid-c.img")
   printf '%s\n' "$replacement" >> "$BASE/raid-devices"
   mdadm /dev/md/${LAB_TAG} --remove failed >/dev/null 2>&1 || :
   mdadm /dev/md/${LAB_TAG} --add "$replacement" >/dev/null
   sleep 1
   mdadm /dev/md/${LAB_TAG} --fail "$replacement" >/dev/null
   mdadm /dev/md/${LAB_TAG} --remove "$replacement" >/dev/null
   [[ "$(mdadm --detail /dev/md/${LAB_TAG})" == *degraded* ]] || fail 'RAID is not degraded'
   ;;
 raidstop)
   apply raiddegrade fail
   mdadm --stop /dev/md/${LAB_TAG} >/dev/null
   ;;
 raiddegrade)
   need mdadm
   truncate -s 128M "$BASE/raid-a.img"
   truncate -s 128M "$BASE/raid-b.img"
   local ra rb
   ra=$(losetup --find --show "$BASE/raid-a.img")
   rb=$(losetup --find --show "$BASE/raid-b.img")
   printf '%s\n%s\n' "$ra" "$rb" >"$BASE/raid-devices"
   mdadm --create /dev/md/${LAB_TAG} --run --level=1 --raid-devices=2 --metadata=1.2 "$ra" "$rb" --force >/dev/null
   mdadm /dev/md/${LAB_TAG} --fail "$rb" >/dev/null
   ;;
 swapbad)
   need mkswap swapon
   truncate -s 64M "$BASE/swap.img"
   mkswap "$BASE/swap.img" >/dev/null
   python3 - "$BASE/swap.img" <<'PYSWAP'
import sys
with open(sys.argv[1],'r+b',buffering=0) as f:
 f.seek(4096-10); f.write(b'XXXXXXXXXX')
PYSWAP
   ;;
 dblocked)
   # Block-device delayed reads can put the reader into D state. Whether
   # the state is observable depends on kernel scheduling and timing.
   need dmsetup blockdev python3
   truncate -s 96M "$BASE/dm.img"
   local source sectors
   source=$(losetup --find --show "$BASE/dm.img")
   printf '%s\n' "$source" > "$BASE/dm-device"
   sectors=$(blockdev --getsz "$source")
   printf '0 %s delay %s 0 30000\n' "$sectors" "$source" | dmsetup create ${LAB_TAG}_fault
   (exec python3 - /dev/mapper/${LAB_TAG}_fault <<'PYBLOCK'
import os,sys
fd=os.open(sys.argv[1],os.O_RDONLY|os.O_DIRECT)
try:
    # Use an aligned read via preadv into an aligned anonymous mmap.
    import mmap
    b=mmap.mmap(-1,4096)
    os.preadv(fd,[b],0)
finally:
    os.close(fd)
PYBLOCK
   ) >"$BASE/dblocked.log" 2>&1 &
   echo $! > "$BASE/dblocked.pid"
   sleep 1
   kill -0 "$(cat "$BASE/dblocked.pid")" 2>/dev/null || fail 'Delayed reader exited early'
   ;;
 dmfault)
   need dmsetup blockdev
   truncate -s 96M "$BASE/dm.img"
   local dd sectors table
   dd=$(losetup --find --show "$BASE/dm.img")
   printf '%s\n' "$dd" > "$BASE/dm-device"
   sectors=$(blockdev --getsz "$dd")
   case "$arg" in
     error) table="0 $sectors error";;
     delay) table="0 $sectors delay $dd 0 800";;
     flakey) table="0 $sectors flakey $dd 0 5 5 1 error_reads";;
   esac
   printf '%s\n' "$table" | dmsetup create ${LAB_TAG}_fault
   ;;
 ddrescue)
   need ddrescue dmsetup blockdev
   truncate -s 96M "$BASE/dm.img"
   python3 - "$BASE/dm.img" <<'PYDISK'
import os,sys
with open(sys.argv[1],'wb',buffering=0) as f:
    for n in range(96):
        f.write(bytes([n])*1024*1024)
    os.fsync(f.fileno())
PYDISK
   local source sectors
   source=$(losetup --find --show "$BASE/dm.img")
   printf '%s\n' "$source" > "$BASE/dm-device"
   sectors=$(blockdev --getsz "$source")
   ((sectors==196608)) || fail "Unexpected source size: $sectors sectors"
   printf '0 32768 linear %s 0\n32768 16384 error\n49152 147456 linear %s 49152\n' "$source" "$source" | dmsetup create ${LAB_TAG}_fault
   ddrescue -f -n "/dev/mapper/${LAB_TAG}_fault" "$BASE/recovered.img" "$BASE/ddrescue.map" >"$BASE/ddrescue.log" 2>&1 || :
   [[ -s "$BASE/ddrescue.map" && -s "$BASE/recovered.img" ]] || fail 'ddrescue did not create recovery output and mapfile'
   ;;
 writebackload)
   # Buffered writes on lab filesystem only. No global dirty tunable changes.
   (python3 - "$MNT/work/writeback.bin" <<'PYWB'
import os,sys,time
p=sys.argv[1]
with open(p,'wb',buffering=1024*1024) as f:
    block=b'W'*(1024*1024)
    for _ in range(256):
        f.write(block)
        time.sleep(0.015)
    f.flush()
    os.fsync(f.fileno())
PYWB
   ) >"$BASE/writeback.log" 2>&1 &
   echo "$!" > "$BASE/writeback.pid"
   sleep 0.1
   kill -0 "$(cat "$BASE/writeback.pid")" 2>/dev/null || fail 'Buffered writer exited too soon';;
 coldcache)
   python3 - "$MNT/work/cache-test.bin" "$BASE/coldcache.txt" <<'PYCACHE'
import os,sys,time
p,report=sys.argv[1:]
with open(p,'wb') as f:
    block=os.urandom(1024*1024)
    for _ in range(64): f.write(block)
    f.flush();os.fsync(f.fileno())
if not hasattr(os,'posix_fadvise') or not hasattr(os,'POSIX_FADV_DONTNEED'):
    raise SystemExit('posix_fadvise DONTNEED unavailable')
fd=os.open(p,os.O_RDONLY)
try:
    os.posix_fadvise(fd,0,0,os.POSIX_FADV_DONTNEED)
    def measure():
        os.lseek(fd,0,os.SEEK_SET);start=time.monotonic()
        while os.read(fd,1024*1024): pass
        return time.monotonic()-start
    cold=measure();warm=measure()
finally: os.close(fd)
with open(report,'w') as f: f.write(f'cold_seconds={cold:.6f}\nwarm_seconds={warm:.6f}\n')
PYCACHE
   ;;
 luksstack)
   need cryptsetup pvcreate vgcreate lvcreate
   truncate -s 320M "$BASE/luks-stack.img"
   head -c 64 /dev/urandom > "$BASE/luks.key"
   cryptsetup luksFormat --type luks2 --batch-mode --key-file "$BASE/luks.key" "$BASE/luks-stack.img" >/dev/null
   cryptsetup open --key-file "$BASE/luks.key" "$BASE/luks-stack.img" ${LAB_TAG}_092
   pvcreate -ff -y /dev/mapper/${LAB_TAG}_092 >/dev/null
   vgcreate ${LAB_TAG}_092 /dev/mapper/${LAB_TAG}_092 >/dev/null
   lvcreate -L 96M -n data ${LAB_TAG}_092 >/dev/null
   mkfs.ext4 -F -q /dev/${LAB_TAG}_092/data
   lvchange -an ${LAB_TAG}_092/data
   vgchange -an ${LAB_TAG}_092 >/dev/null
   cryptsetup close ${LAB_TAG}_092
   ;;
 appmismatch)
   need sha256sum
   printf 'transaction=12345\namount=100\nstatus=committed\n' > "$MNT/data/ledger.txt"
   (cd "$MNT/data" && sha256sum ledger.txt) > "$BASE/app-manifest.sha256"
   sed -i 's/amount=100/amount=900/' "$MNT/data/ledger.txt"
   ;;
 backuprestore)
   need sha256sum
   cp -- "$MNT/data/important.txt" "$BASE/backup-important.txt"
   sha256sum "$BASE/backup-important.txt" > "$BASE/backup-important.sha256"
   printf 'CORRUPTED: restore this file from the known-good copy\n' > "$MNT/data/important.txt"
   sync;;
 ioload)
   need fio
   local ioargs
   if [[ "$arg" == random ]]; then ioargs='--rw=randwrite --bs=4k --iodepth=16'; else ioargs='--rw=randrw --bs=4k --iodepth=32'; fi
   # Deliberately bounded background load, confined to the mounted lab filesystem.
   (fio --name=sflab --filename="$MNT/work/io.bin" --size=128M --time_based --runtime=180 --direct=1 --ioengine=libaio --numjobs=2 $ioargs >"$BASE/fio.log" 2>&1) &
   printf '%s\n' "$!" > "$BASE/fio.pid"
   ;;
 btrfsdamage)
   need mkfs.btrfs btrfs
   truncate -s 320M "$BASE/btrfs.img"
   mkfs.btrfs -f -q "$BASE/btrfs.img"
   local bd
   bd=$(losetup --find --show "$BASE/btrfs.img")
   mkdir -p "$BASE/btrfs-mnt"
   mount "$bd" "$BASE/btrfs-mnt"
   dd if=/dev/urandom of="$BASE/btrfs-mnt/check.dat" bs=1M count=4 status=none
   sync; umount "$BASE/btrfs-mnt"
   # Corrupt data in a block without changing Btrfs metadata structures.
   python3 - "$BASE/btrfs.img" <<'PYBTRFS'
import sys
with open(sys.argv[1],'r+b',buffering=0) as f:
 f.seek(2*1024*1024); f.write(b'BROKEN-BLOCK')
PYBTRFS
   ;;
 btrfssnapshot)
   need mkfs.btrfs btrfs
   truncate -s 384M "$BASE/btrfs.img"
   mkfs.btrfs -f -q "$BASE/btrfs.img"
   local bd
   bd=$(losetup --find --show "$BASE/btrfs.img")
   mkdir -p "$BASE/btrfs-mnt"
   mount "$bd" "$BASE/btrfs-mnt"
   btrfs subvolume create "$BASE/btrfs-mnt/live" >/dev/null
   dd if=/dev/urandom of="$BASE/btrfs-mnt/live/data.bin" bs=1M count=80 status=none
   sync
   btrfs subvolume snapshot "$BASE/btrfs-mnt/live" "$BASE/btrfs-mnt/old-snapshot" >/dev/null
   rm "$BASE/btrfs-mnt/live/data.bin"
   sync
   ;;
 partitionwipe)
   need sgdisk partprobe
   truncate -s 128M "$BASE/gpt.img"
   sgdisk --zap-all "$BASE/gpt.img" >/dev/null
   sgdisk -n 1:2048:+64M -t 1:8300 "$BASE/gpt.img" >/dev/null
   sgdisk --backup="$BASE/gpt-backup" "$BASE/gpt.img" >/dev/null
   sgdisk --zap-all "$BASE/gpt.img" >/dev/null
   ;;
 orphanhold)
   need python3
   # An unlinked but open ext4 inode is tracked by ext4's orphan handling.
   # This exercises live orphan cleanup, NOT journal replay after a crash.
   python3 - "$MNT/work/orphan.bin" "$BASE/orphan.pid" <<'PYORPHAN' &
import os,sys,time
path,pidfile=sys.argv[1:]
with open(path,'wb',buffering=0) as f:
    f.write(b'O'*(32*1024*1024))
    os.fsync(f.fileno())
    os.unlink(path)
    with open(pidfile,'w') as out: out.write(str(os.getpid()))
    while True: time.sleep(2)
PYORPHAN
   local orphan_child=$! tries=0
   while ((tries<50)); do
     if [[ -s "$BASE/orphan.pid" && ! -e "$MNT/work/orphan.bin" ]]; then
       kill -0 "$(cat "$BASE/orphan.pid")" 2>/dev/null && break
     fi
     kill -0 "$orphan_child" 2>/dev/null || fail 'Orphan holder exited early'
     sleep 0.1
     ((tries+=1))
   done
   [[ -s "$BASE/orphan.pid" && ! -e "$MNT/work/orphan.bin" ]] || fail 'Could not create live orphan inode'
   ;;
 deletedopen)
   need python3
   # Hold an unlinked allocation while a second file fills only the disposable image.
   python3 - "$MNT/work/deleted-hold.bin" "$BASE/holder.pid" <<'PYHOLD' &
import os,sys,time
p=sys.argv[1]; f=open(p,'wb',buffering=0)
with open(sys.argv[2],'w') as pid: pid.write(str(os.getpid()))
try:
    f.write(b'Z'*(32*1024*1024)); os.fsync(f.fileno()); os.unlink(p)
    while True: time.sleep(10)
finally: f.close()
PYHOLD
   local child=$!
   local tries=0
   while ((tries<60)); do
     [[ -f "$BASE/holder.pid" && ! -e "$MNT/work/deleted-hold.bin" ]] && break
     kill -0 "$child" 2>/dev/null || fail 'Holder process died'
     sleep 0.2; ((tries+=1))
   done
   [[ -f "$BASE/holder.pid" && ! -e "$MNT/work/deleted-hold.bin" ]] || fail 'Holder did not initialize'
   python3 - "$MNT/work/full.bin" <<'PYFULL'
import errno,os,sys
p=sys.argv[1]
chunk=b'F'*(1024*1024)
fd=os.open(p,os.O_CREAT|os.O_WRONLY|os.O_EXCL,0o600)
try:
    while True:
        try: os.write(fd,chunk)
        except OSError as e:
            if e.errno==errno.ENOSPC: break
            raise
    try: os.fsync(fd)
    except OSError as e:
        if e.errno!=errno.ENOSPC: raise
finally: os.close(fd)
PYFULL
   sync;;
 *) fail "Unknown injection type $kind";;
 esac
}
inject(){
 local level='' selected='' allow_host=0
 while (($#)); do case "$1" in --allow-host) allow_host=1; shift;; --level) [[ $# -ge 2 ]] || fail 'Missing level'; level=$2; shift 2;; --id) [[ $# -ge 2 ]] || fail "Missing ID"; selected=$2; shift 2;; *) fail "Unknown option $1";; esac; done
 [[ "$level" =~ ^[1-5]$ ]] || fail 'Use inject --level 1..5'
 prepare; [[ -f "$IMG" ]] || fail 'Run init first'; [[ ! -e "$STATE" ]] || fail 'Active incident exists; use reset'
 owned_mount || fail 'Lab not mounted: run reset first'
 local id line sid lvl desc hint kind arg
 if [[ -n "$selected" ]]; then
   [[ "$selected" =~ ^[0-9]{3}$ ]] || fail 'ID must be three digits'
   id="$selected"
   line=$(row "$id")
   [[ -n "$line" ]] || fail 'Unknown scenario ID'
   [[ "$(cut -d'|' -f2 <<<"$line")" == "$level" ]] || fail 'ID not in selected level'
   [[ -n "$(cut -d'|' -f5 <<<"$line")" ]] || fail 'Scenario NOT_READY'
 else
   id=$(select_case "$level")
   line=$(row "$id")
 fi
 IFS='|' read -r sid lvl desc hint kind arg <<<"$line"
 prereqs "$kind" "$arg"
 if [[ "$kind" == hostfstab || "$kind" == hostrootfull ]]; then
   ((allow_host)) || fail 'Host mutation requires --allow-host and explicit --id'
   [[ "$selected" == 088 || "$selected" == 086 ]] || fail 'Host fault cannot be selected randomly'
 fi
 printf '%s|%s|%s|PENDING\n' "$id" "$level" "$(date -u +%Y%m%dT%H%M%SZ)" > "$STATE"
 if ! (set -Ee; apply "$kind" "$arg"); then
   sed -i 's/|PENDING$/|FAILED/' "$STATE"
   echo 'Injection failed; incident marked FAILED. Run reset.' >&2
   exit 1
 fi
 sed -i 's/|PENDING$/|INJECTED/' "$STATE"
 printf '%s\n' "$id" >>"$HISTORY"
 printf 'INJECTION ATTEMPTED (confirm symptoms before counting this drill)\nID: ST-%s\nLevel: %s\nTarget: %s\nNo root cause shown. Investigate!\n' "$id" "$level" "$MNT"
}
active(){ load_lab_tag; [[ -f "$STATE" ]] || fail 'No active incident'; IFS='|' read -r SID LEVEL DATE PHASE < "$STATE"; [[ "${PHASE:-}" == INJECTED ]] || fail "Incident not successfully injected (${PHASE:-unknown}); reset first"; LINE=$(row "$SID"); [[ -n "$LINE" ]] || fail 'Invalid state'; IFS='|' read -r _ _ DESC HINT KIND ARG <<<"$LINE"; }
hint(){ need_root; active; printf 'Hint: %s\n' "$HINT"; }
reveal(){ need_root; active; printf 'Incident %s, Level %s\nRoot cause: %s\nInjection: %s (%s)\n' "$SID" "$LEVEL" "$DESC" "$KIND" "$ARG"; }
verify(){
 need_root; active
 local ok=1
 if ! findmnt -rn -M "$MNT" >/dev/null; then echo 'FAIL: filesystem not mounted'; return 1; fi
 if ! findmnt -rn -M "$MNT" -o OPTIONS | grep -Eq '(^|,)rw(,|$)'; then echo 'FAIL: filesystem not read-write'; ok=0; fi
 if [[ ! -f "$MNT/data/important.txt" ]]; then echo 'FAIL: important.txt not at expected location'; ok=0; fi
 if ! runuser -u nobody -- test -r "$MNT/data/important.txt"; then echo 'FAIL: important.txt not readable by unprivileged user'; ok=0; fi
 case "$KIND" in
   orphanhold)
     if [[ -s "$BASE/orphan.pid" ]] && kill -0 "$(cat "$BASE/orphan.pid")" 2>/dev/null; then
       echo 'FAIL: unlinked inode still held open by lab process'; ok=0
     fi;;
   appmismatch)
     if (cd "$MNT/data" && sha256sum -c "$BASE/app-manifest.sha256" >/dev/null 2>&1); then :; else echo 'FAIL: application manifest checksum mismatch'; ok=0; fi;;
   deletedopen)
     if [[ -f "$BASE/holder.pid" ]] && kill -0 "$(cat "$BASE/holder.pid")" 2>/dev/null; then echo 'FAIL: deleted-file holder is still running'; ok=0; fi
     if [[ -e "$MNT/work/full.bin" ]]; then echo 'FAIL: lab filler still consumes space'; ok=0; fi;;
   coldcache)
     [[ -s "$BASE/coldcache.txt" ]] || { echo 'FAIL: cache timing report missing'; ok=0; }
     echo 'INFO: cache experiment is observational; timings do not prove a fault.';;
   writebackload)
     if [[ -f "$BASE/writeback.pid" ]] && kill -0 "$(cat "$BASE/writeback.pid")" 2>/dev/null; then echo 'FAIL: buffered writer still running'; ok=0; fi;;
   luksstack)
     if ! cryptsetup status ${LAB_TAG}_092 >/dev/null 2>&1; then echo 'FAIL: encrypted mapping not opened'; ok=0; fi
     if ! lvs ${LAB_TAG}_092/data >/dev/null 2>&1; then echo 'FAIL: logical volume unavailable'; ok=0; fi;;
   hostrootfull)
     if [[ -e /storage-fault-lab-rootfill.img ]]; then echo 'FAIL: injected root filler still exists'; ok=0; fi;;
   hostfstab)
     if [[ -f "$BASE/fstab-token" ]] && grep -Fq "$(cat "$BASE/fstab-token")" /etc/fstab; then
       echo 'FAIL: injected /etc/fstab entry remains'; ok=0
     fi;;
   inodes)
     if [[ "$(df -Pi "$MNT" | awk 'NR==2 {print $4}')" -lt 10 ]]; then echo 'FAIL: inode exhaustion remains'; ok=0; fi;;
   reserve)
     if [[ "$(tune2fs -l "$(loop_for_image)" 2>/dev/null | awk -F: '/Reserved block count/{gsub(/ /,"",$2);print $2}')" -gt 10000 ]]; then echo 'CHECK: ext4 reserved blocks remain elevated'; ok=0; fi;;
 esac
 case "$KIND" in
  uncleanext4|rootroanalog|rootmagicanalog|pathswitch|magic|xfsdamage|lvmpartial|raiddegrade|raidstop|raidrebuild|dmfault|ddrescue|dblocked|swapbad|partitionwipe|duplicateuuid|btrfssnapshot|directio|deletedopen|ioload|thinfull|lvmmissing|luksbad|metaload|btrfsfull|btrfsbalance|btrfschecksum|btrfsmissing|lvmext4|raidext4)
    echo 'CHECK REQUIRED: device-specific incident needs manual validation; baseline checks are insufficient.'
    ok=0;;
 esac
 if ((ok)); then
   if verify_specific; then :; else
     rc=$?
     if ((rc==1)); then ok=0; else echo 'MANUAL CHECK: no scenario-specific verifier available'; ok=0; fi
   fi
 fi
 if ((ok)); then echo 'VERIFY PASS: baseline and available scenario-specific checks passed; this is NOT proof of full data integrity.'; else return 1; fi
}
# A focused verifier for deterministic path/permission incidents.  Other
# incidents retain the conservative baseline/manual verification result.
verify_specific(){
 local path mode expected actual a b attrs opts
 case "$KIND" in
  deletedopen)
   [[ ! -e "$MNT/work/full.bin" ]] || { echo 'FAIL: remove the lab filler after stopping the holder'; return 1; }
   if [[ -s "$BASE/holder.pid" ]] && kill -0 "$(cat "$BASE/holder.pid")" 2>/dev/null; then echo 'FAIL: deleted-file holder is still running'; return 1; fi
   echo 'PASS: holder stopped and lab filler removed';;
  orphanhold)
   if [[ -s "$BASE/orphan.pid" ]] && kill -0 "$(cat "$BASE/orphan.pid")" 2>/dev/null; then
     echo 'FAIL: orphan inode holder still alive'; return 1
   fi
   echo 'PASS: orphan inode holder no longer running; kernel can reclaim inode';;
  chmoddir|chmodfile|chmodroot)
   if [[ "$KIND" == chmodroot ]]; then path="$MNT"; expected=755
   else IFS=: read -r a b <<<"$ARG"; path="$MNT/$a"
    case "$a" in
     data|logs|archive|tmp|config|work) expected=755;;
     *) expected=644;;
    esac
   fi
   [[ -e "$path" ]] || { echo "FAIL: missing $path"; return 1; }
   mode=$(stat -c %a "$path")
   [[ "$mode" == "$expected" ]] || { echo "FAIL: $path mode=$mode, expected=$expected"; return 1; }
   echo 'PASS: expected mode restored';;
  move|hide)
   IFS=: read -r a b <<<"$ARG"
   [[ -e "$MNT/$a" ]] || { echo "FAIL: original path missing: $a"; return 1; }
   [[ ! -e "$MNT/$b" ]] || { echo "FAIL: moved copy still at $b"; return 1; }
   echo 'PASS: original path restored';;
  symlink)
   IFS=: read -r a b <<<"$ARG"
   [[ ! -L "$MNT/$a" ]] || { echo "FAIL: injected symlink still exists at $a"; return 1; }
   echo 'PASS: injected symlink removed';;
  owner)
   IFS=: read -r a b <<<"$ARG"
   [[ "$(stat -c %u:%g "$MNT/$a")" == 0:0 ]] || { echo "FAIL: owner/group not restored"; return 1; }
   echo 'PASS: owner and group restored';;
  chattr)
   need lsattr
   IFS=: read -r a b <<<"$ARG"
   path="$MNT/$a"
   [[ -e "$path" ]] || { echo "FAIL: inode-attribute target is missing: $a"; return 1; }
   attrs=$(lsattr -d "$path" | awk '{print $1}')
   [[ "$b" != *i* || "$attrs" != *i* ]] || { echo "FAIL: immutable attribute remains on $a"; return 1; }
   [[ "$b" != *a* || "$attrs" != *a* ]] || { echo "FAIL: append-only attribute remains on $a"; return 1; }
   echo 'PASS: injected inode attribute cleared';;
  combo)
   case "$ARG" in
    ro-perm)
      opts=$(findmnt -rn -M "$MNT" -o OPTIONS) || return 1
      [[ ",$opts," == *,rw,* ]] || { echo 'FAIL: filesystem remains read-only'; return 1; }
      [[ "$(stat -c %a "$MNT/data")" == 755 ]] || { echo 'FAIL: data directory mode not restored'; return 1; };;
    immutable-perm)
      [[ "$(stat -c %a "$MNT/data")" == 755 ]] || { echo 'FAIL: data directory mode not restored'; return 1; }
      attrs=$(lsattr -d "$MNT/data/important.txt" | awk '{print $1}')
      [[ "$attrs" != *i* ]] || { echo 'FAIL: important.txt remains immutable'; return 1; };;
    append-perm)
      [[ "$(stat -c %a "$MNT/logs")" == 755 ]] || { echo 'FAIL: logs directory mode not restored'; return 1; }
      attrs=$(lsattr -d "$MNT/logs/service.log" | awk '{print $1}')
      [[ "$attrs" != *a* ]] || { echo 'FAIL: service.log remains append-only'; return 1; };;
    unmount-move)
      opts=$(findmnt -rn -M "$MNT" -o OPTIONS) || return 1
      [[ ",$opts," == *,rw,* ]] || { echo 'FAIL: filesystem is not mounted read-write'; return 1; }
      [[ -f "$MNT/data/important.txt" && ! -e "$MNT/archive/important.txt" ]] || { echo 'FAIL: important.txt was not restored under data/'; return 1; };;
    ro-immutable)
      opts=$(findmnt -rn -M "$MNT" -o OPTIONS) || return 1
      [[ ",$opts," == *,rw,* ]] || { echo 'FAIL: filesystem remains read-only'; return 1; }
      attrs=$(lsattr -d "$MNT/data/important.txt" | awk '{print $1}')
      [[ "$attrs" != *i* ]] || { echo 'FAIL: important.txt remains immutable'; return 1; };;
    noexec-perm)
      opts=$(findmnt -rn -M "$MNT" -o OPTIONS) || return 1
      [[ ",$opts," != *,noexec,* ]] || { echo 'FAIL: noexec remains active'; return 1; }
      [[ "$(stat -c %a "$MNT/work")" == 755 ]] || { echo 'FAIL: work directory mode not restored'; return 1; };;
    move-perm)
      [[ "$(stat -c %a "$MNT/data")" == 755 ]] || { echo 'FAIL: data directory mode not restored'; return 1; }
      [[ -f "$MNT/data/important.txt" && ! -e "$MNT/archive/important.txt" ]] || { echo 'FAIL: important.txt was not restored under data/'; return 1; };;
   esac
   echo 'PASS: every component of the combined fault was checked';;
  remount)
   local opts; opts=$(findmnt -rn -M "$MNT" -o OPTIONS) || return 1
   case "$ARG" in
    ro) [[ ",$opts," == *,rw,* ]] || return 1;;
    noexec|nosuid|nodev|sync|dirsync) [[ ",$opts," != *,$ARG,* ]] || { echo "FAIL: $ARG still active"; return 1; };;
   esac
   echo 'PASS: target mount option cleared';;
  appmismatch)
   (cd "$MNT/data" && sha256sum -c "$BASE/app-manifest.sha256" >/dev/null 2>&1) || return 1
   echo 'PASS: application checksum restored';;
  backuprestore)
   [[ -s "$BASE/backup-important.txt" && -s "$BASE/backup-important.sha256" ]] || { echo 'FAIL: known-good backup evidence missing'; return 1; }
   expected=$(awk '{print $1}' "$BASE/backup-important.sha256")
   actual=$(sha256sum "$MNT/data/important.txt" | awk '{print $1}')
   [[ "$actual" == "$expected" ]] || { echo "FAIL: restored file checksum differs (expected $expected, got $actual)"; return 1; }
   echo 'PASS: service file matches the checksum of the copy outside the lab image';;
  hostfstab)
   [[ ! -f "$BASE/fstab-token" ]] || ! grep -Fq "$(cat "$BASE/fstab-token")" /etc/fstab || return 1
   findmnt --verify --tab-file /etc/fstab >/dev/null 2>&1 || return 1
   echo 'PASS: injected fstab entry absent and fstab syntax verified';;
  *) return 2;;
 esac
}
audit(){
 local count ready missing lvl total
 echo 'Registry audit (implementation presence is not a successful runtime test):'
 printf '%-8s %-8s %-12s %-12s\n' LEVEL TOTAL CODE_PATH NOT_READY
 for lvl in 1 2 3 4 5; do
   local counts; counts=$(awk -F'|' -v l="$lvl" '$2==l{t++;if($5!="")r++;else m++}END{print t+0,r+0,m+0}' <<<"$CATALOG")
   read -r total ready missing <<<"$counts"
   printf '%-8s %-8s %-12s %-12s\n' "$lvl" "$total" "$ready" "$missing"
 done
 awk -F'|' 'NF!=6 || $1 !~ /^[0-9][0-9][0-9]$/ || $2 !~ /^[1-5]$/ {print "INVALID REGISTRY ROW: "$0; bad=1} END{exit bad}' <<<"$CATALOG" || return 1
 local duplicates; duplicates=$(cut -d'|' -f1 <<<"$CATALOG" | sort | uniq -d)
 [[ -z "$duplicates" ]] || { printf 'Duplicate IDs: %s\n' "$duplicates"; return 1; }
 local n; n=$(wc -l <<<"$CATALOG")
 [[ "$n" -eq 101 ]] || { echo "Expected 101 rows, got $n"; return 1; }
 local ids; ids=$(cut -d'|' -f1 <<<"$CATALOG" | sort)
 [[ "$ids" == "$(seq -f '%03g' 1 101)" ]] || { echo 'IDs must cover 001..101'; return 1; }
 echo 'Registry structure: PASS'
}
selftest(){
 audit || return 1
 local kinds kind missing=0
 kinds=$(awk -F'|' '$5!=""{print $5}' <<<"$CATALOG" | sort -u)
 while IFS= read -r kind; do
   if ! grep -Eq "^[[:space:]]*([a-z0-9_]+\|)*${kind}(\|[a-z0-9_]+)*\)" "$0"; then
     printf 'MISSING handler for kind: %s\n' "$kind"
     missing=1
   fi
 done <<<"$kinds"
 if ((missing)); then return 1; fi
 echo 'STATIC SELFTEST PASS: all registry injection types have handler labels.'
 echo 'Runtime effect and repair verification still require an actual VM test.'
}
prereqs(){
 local kind="$1" arg="$2" cmd
 case "$kind" in
  hostfstab) need findmnt cp sha256sum;;
  uncleanext4) need debugfs e2fsck tune2fs;;
  rootroanalog|rootmagicanalog) need mount findmnt;;
  pathswitch) need dmsetup blockdev losetup;;
  hostrootfull) need findmnt python3;;
  orphanhold) need python3;;
  chattr) need chattr lsattr;;
  combo) case "$arg" in immutable-perm|append-perm|ro-immutable) need chattr lsattr;; esac;;
  xfsdamage) need mkfs.xfs xfs_repair;;
  lvmpartial|thinfull|lvmmissing|lvmext4) need pvcreate vgcreate lvcreate vgchange;;
  raiddegrade|raidstop|raidext4|raidrebuild) need mdadm;;
  luksbad) need cryptsetup;;
  dmfault|dblocked) need dmsetup blockdev;;
  ddrescue) need ddrescue dmsetup blockdev;;
  ioload) need fio;;
  writebackload|coldcache) need python3;;
  luksstack) need cryptsetup pvcreate vgcreate lvcreate mkfs.ext4;;
  appmismatch) need sha256sum;;
  btrfsfull|btrfssnapshot|btrfschecksum|btrfsmissing|btrfsbalance) need mkfs.btrfs btrfs;;
  partitionwipe) need sgdisk;;
  swapbad) need mkswap swapon;;
  duplicateuuid) need tune2fs;;
  inodes|reserve) need mkfs.ext4 tune2fs;;
 esac
}
doctor(){
 need_root
 echo 'Host prerequisites (availability does not imply a safe or working injection):'
 for cmd in losetup mount mkfs.ext4 e2fsck tune2fs mkfs.xfs xfs_repair lvm mdadm dmsetup cryptsetup mkfs.btrfs btrfs fio sgdisk ddrescue; do
   if command -v "$cmd" >/dev/null 2>&1; then printf 'OK      %s\n' "$cmd"; else printf 'MISSING %s\n' "$cmd"; fi
 done
 echo 'Loop control:'
 if [[ -e /dev/loop-control ]]; then ls -l /dev/loop-control; else echo 'MISSING /dev/loop-control'; fi
 echo 'Disk and root mount (read-only inspection):'
 findmnt -no SOURCE,FSTYPE,TARGET /
 lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
}
restore_host(){
 need_root
 if [[ -f "$BASE/rootfill-token" ]]; then
   local fillfile; fillfile=$(cat "$BASE/rootfill-token")
   [[ "$fillfile" == /storage-fault-lab-rootfill.img && -f "$fillfile" && ! -L "$fillfile" ]] || fail 'Unexpected root fill file; inspect manually'
   rm -f -- "$fillfile" "$BASE/rootfill-token"
   sync
   echo 'Root filler removed.'
 fi
 [[ -f "$BASE/fstab-token" ]] || return 0
 [[ -f "$BASE/fstab.original" && -f "$BASE/fstab-token" ]] || fail 'No fstab backup for scenario 088'
 [[ -f /etc/fstab && ! -L /etc/fstab ]] || fail 'Unexpected /etc/fstab'
 local token; token=$(cat "$BASE/fstab-token")
 grep -Fq "$token" /etc/fstab || fail 'Injected token missing: fstab changed externally; restore manually from backup'
 # Do not overwrite other changes: remove only our tagged lines.
 python3 - "$token" <<'PYRESTORE'
from pathlib import Path
import sys
p=Path('/etc/fstab'); token=sys.argv[1]
lines=p.read_text().splitlines(keepends=True)
new=[line for line in lines if token not in line and 'STORAGE-FAULT-LAB-088' not in line]
p.write_text(''.join(new))
PYRESTORE
 findmnt --verify --tab-file /etc/fstab || fail 'fstab still has issues; inspect manually'
 rm -f "$BASE/fstab-token" "$BASE/fstab.original"
 echo 'Host fstab injection removed. If in Rescue, mount installed root and edit its /etc/fstab instead.'
}
reset(){
 [[ ! -f "$BASE/fstab-token" && ! -f "$BASE/rootfill-token" ]] || fail 'Host fault active: run restore-host before reset'
 init
}
status(){
 need_root; printf 'Image: %s\nMount: %s\n' "$IMG" "$MNT"
 if [[ -f "$STATE" ]]; then IFS='|' read -r id level date phase <"$STATE"; printf 'Active: ST-%s (level %s, %s)\n' "$id" "$level" "${phase:-legacy}"; else echo 'No active incident'; fi
 findmnt -M "$MNT" || :
}
catalog(){
 local level="${1:-all}"
 awk -F'|' -v l="$level" 'l=="all" || $2==l {printf "%s  L%s  %-12s %s\n",$1,$2,($5==""?"NOT_READY":"RUNNABLE"),$3}' <<<"$CATALOG"
}
usage(){ cat <<'TXT'
Storage Fault Lab v19 - disposable VPS practice
  sudo bash storage-fault-lab.sh init
  sudo bash storage-fault-lab.sh inject --level 1|2|3|4|5 [--id 001..101]
  sudo bash storage-fault-lab.sh inject --level 5 --id 086 --allow-host
  sudo bash storage-fault-lab.sh inject --level 5 --id 088 --allow-host
  sudo bash storage-fault-lab.sh restore-host
  sudo bash storage-fault-lab.sh hint
  sudo bash storage-fault-lab.sh verify
  sudo bash storage-fault-lab.sh reveal
  sudo bash storage-fault-lab.sh doctor
  bash storage-fault-lab.sh audit
  sudo bash storage-fault-lab.sh status
  sudo bash storage-fault-lab.sh reset
  bash storage-fault-lab.sh catalog [1|2|3|4|5]
  bash storage-fault-lab.sh selftest

101 scenarios are catalogued; 101 have injection code paths (some require optional packages/kernel features). Only RUNNABLE entries have injection code paths and are randomly
selected; analogues are explicitly labeled and are not equivalent to physical/host failures. Unimplemented scenarios remain NOT_READY. Run only on a disposable VM.
The lab is reset by RECREATING its 1024 MiB image, deleting all lab data.
Never put personal files in the lab mount or its image path.
TXT
}
case "${1:-help}" in
 init) init;; restore-host) restore_host;; inject) shift; inject "$@";; hint) hint;; verify) verify;; reveal) reveal;; status) status;; doctor) doctor;; audit) audit;; selftest) selftest;; reset) reset;; catalog) shift; catalog "$@";; help|-h|--help) usage;; *) usage; exit 2;;
esac
```