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
