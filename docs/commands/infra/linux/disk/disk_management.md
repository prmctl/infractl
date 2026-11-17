






# Partitioning


## fdisk


## gdisk


## parted




# LVM

## Cocepts

### PV (Physical Volume)
A disk or partition that we initialize for use with LVM.

### VG (Volume Group)
A storage pool created from one or more Physical Volumes (PVs).

### LV (Logical Volume)
A logical storage space allocated from a VG, where we can create a filesystem or configure swap space.


## LVM Disk Partitioning Step by Step

### 1. Check Disk and LVM Status

```bash
lsblk -f
sudo pvs
sudo vgs
sudo lvs
```

### 2. Create PV and VG (If Needed)

```bash
sudo pvcreate /dev/sdX1
sudo vgcreate my-vg /dev/sdX1
```

Or extend an existing VG:

```bash
sudo vgextend ubuntu-vg /dev/sdX1
```

> Skip this step if PV and VG already exist. Ensure the target partition is unused before running `pvcreate`.

### 3. Create a Logical Volume

```bash
sudo lvcreate -L 20G -n data-lv ubuntu-vg
```

### 4. Create a Filesystem

> Verify the LV path before formatting. `mkfs` destroys existing filesystem data.

```bash
sudo mkfs.ext4 /dev/ubuntu-vg/data-lv
```

### 5. Create a Mount Point

```bash
sudo mkdir -p /data
```

### 6. Mount the Filesystem

Make sure `/data` does not contain existing data.

```bash
sudo mount /dev/ubuntu-vg/data-lv /data
```

Verify:

```bash
df -hT /data
```

### 7. Make the Mount Persistent

Get UUID:

```bash
sudo blkid /dev/ubuntu-vg/data-lv
```

Back up and edit `/etc/fstab`:

```bash
sudo cp /etc/fstab /etc/fstab.bak
sudo nano /etc/fstab
```

Add the following line using the actual UUID:

```fstab
UUID=<YOUR_UUID> /data ext4 defaults 0 2
```

Verify:

```bash
sudo findmnt --verify
sudo systemctl daemon-reload
sudo umount /data
sudo mount /data
df -hT /data
```

### 8. Final Verification

```bash
lsblk -f
sudo lvs
sudo vgs
df -hT
```

---

**Workflow:**
`Disk → Partition → PV → VG → LV → Filesystem → Mount → fstab`





# Linux Storage Architecture: GPT, LVM & RAID

Linux storage architecture typically combines **GPT partitioning, LVM, filesystems, and optionally RAID** to provide flexible and reliable storage management.

## 1. Single Disk with LVM

A common layout for a Linux server with one 200GB disk.

```text
/dev/sda (200GB)
│
├── /dev/sda1   1GB   → EFI (/boot/efi)
├── /dev/sda2   2GB   → /boot
└── /dev/sda3   197GB → LVM
                          │
                          ▼
                     PV (sda3)
                          │
                          ▼
                     VG (ubuntu-vg)
                          │
                          ├── root-lv   40GB → /
                          ├── var-lv    30GB → /var
                          ├── home-lv   20GB → /home
                          ├── data-lv   80GB → /data
                          └── Free Space ~27GB
```

**Key Points:**
- GPT defines physical disk partitions.
- PV provides storage capacity to LVM.
- VG combines available storage into a logical pool.
- LV allocates storage from the VG.
- Keep some VG space free for future expansion.
- LVM does not provide redundancy by default.

## 2. Multiple Disks with a Single VG

Multiple physical disks can contribute storage to the same VG.

```text
/dev/sda (OS Disk)
├── sda1 → EFI
├── sda2 → /boot
└── sda3 → PV1 ───┐
                  │
/dev/sdb          │
└── sdb1 → PV2 ───┼── VG (ubuntu-vg)
                  │        │
/dev/sdc          │        ├── root-lv → /
└── sdc1 → PV3 ───┘        ├── var-lv  → /var
                           └── data-lv → /data
```

**Key Points:**
- EFI and `/boot` are typically located on the OS disk.
- Additional disks do not require separate EFI or `/boot` partitions.
- An LV can span multiple physical disks.
- Additional PVs can expand VG capacity.
- Disk failure may cause data loss without redundancy.

## 3. Multiple Disks with Separate VGs

Separate VGs provide independent storage pools for the operating system and application data.

```text
/dev/sda (OS Disk)
├── sda1 → EFI
├── sda2 → /boot
└── sda3 → PV
             │
             ▼
         system-vg
             ├── root-lv → /
             └── var-lv  → /var


/dev/sdb ── PV ──┐
                 ├── data-vg
/dev/sdc ── PV ──┘      │
                        ├── app-lv    → /app
                        └── backup-lv → /backup
```

**Advantages:**
- Independent OS and data storage management.
- Better workload isolation.
- Easier capacity planning.
- No automatic disk failure protection.

## 4. RAID + LVM (Production Architecture)

RAID provides disk-level redundancy, while LVM provides flexible logical volume management.

Example: Two disks configured as RAID1.

```text
/dev/sda (200GB)      /dev/sdb (200GB)
       │                     │
       ├── EFI               ├── EFI
       ├── boot              ├── boot
       └── LVM RAID Member   └── LVM RAID Member
                 │           │
                 └─────┬─────┘
                       │
                  RAID1 (md0)
                       │
                       ▼
                      PV
                       │
                       ▼
                  VG (system-vg)
                       │
                       ├── root-lv → /
                       ├── var-lv  → /var
                       └── home-lv → /home
```

**Key Points:**
- RAID1 mirrors data across two disks.
- Usable RAID1 capacity is approximately one disk.
- LVM operates on top of the RAID device.
- EFI partitions require appropriate boot redundancy configuration.
- RAID does not replace backups.

## 5. Separate OS and Data RAID Arrays

A common architecture for production servers with dedicated OS and data disks.

```text
OS Disks
────────
Disk 1 ──┐
         ├── RAID1
Disk 2 ──┘     │
               ├── EFI / Boot Setup
               └── PV
                    │
                 system-vg
                    ├── root-lv → /
                    └── var-lv  → /var


Data Disks
──────────
Disk 3 ──┐
Disk 4 ──┤
Disk 5 ──┼── RAID10 / RAID6
Disk 6 ──┘         │
                   ▼
                  PV
                   │
                data-vg
                   ├── app-lv → /app
                   └── db-lv  → /var/lib/mysql
```

**Advantages:**
- OS and application data isolation.
- Disk failure protection through RAID.
- Independent storage expansion and management.
- Suitable for database and application workloads.

## 6. Filesystems and Mount Points

Each LV requires a filesystem before mounting.

| LV | Filesystem | Mount Point |
|---|---|---|
| root-lv | ext4 | `/` |
| var-lv | ext4 | `/var` |
| home-lv | ext4 | `/home` |
| data-lv | XFS | `/data` |

**Important:**
- `ext4`: Supports growing and offline shrinking.
- `XFS`: Supports growing but not shrinking.
- `/etc/fstab`: Configures persistent filesystem mounts.
- EFI: Typically FAT32, mounted at `/boot/efi`.
- `/boot`: Commonly ext4 when configured separately.

## 7. Architecture Comparison

| Architecture | Flexibility | Disk Redundancy | Typical Use |
|---|---|---|---|
| Single Disk + LVM | High | No | Lab / Small Servers |
| Multiple PVs + One VG | High | No | Capacity Expansion |
| Separate VGs | High | No* | OS / Data Isolation |
| RAID1 + LVM | High | Yes | Production OS |
| RAID10/6 + LVM | High | Yes | Production Data |
| Separate RAID Arrays + LVM | High | Yes | Enterprise Servers |

*Separate VGs provide logical isolation, not redundancy by themselves.*

## 8. Production Best Practices

1. Use **GPT + UEFI** for modern Linux installations.
2. Use **LVM** for flexible volume management.
3. Use **RAID** when disk failure tolerance is required.
4. Separate OS and application data when appropriate.
5. Keep unallocated VG space for future expansion.
6. Monitor disk health, RAID status, and filesystem usage.
7. Maintain independent backups.
8. Design filesystem sizes based on workload requirements.

## 9. Storage Architecture Summary

**Without RAID:**

```text
Physical Disk(s)
       ↓
GPT Partitioning (optional for data disks)
       ↓
Physical Volume (PV)
       ↓
Volume Group (VG)
       ↓
Logical Volume (LV)
       ↓
Filesystem (ext4 / XFS)
       ↓
Mount Point
```

**With RAID:**

```text
Physical Disks
       ↓
Partitions (if used)
       ↓
RAID Array
       ↓
Physical Volume (PV)
       ↓
Volume Group (VG)
       ↓
Logical Volume (LV)
       ↓
Filesystem
       ↓
Mount Point
```

**Core Principle:**

- **GPT:** Physical partition management.
- **RAID:** Disk redundancy and/or performance.
- **LVM:** Flexible logical storage management.
- **Filesystem:** Data organization and storage.
- **Mount Point:** Filesystem integration into the Linux directory tree.

> **Production Rule:** RAID protects against certain disk failures, LVM manages storage flexibility, and backups protect against data loss. Each serves a different purpose.

