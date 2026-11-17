
# Design





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


## Commands

show pvs,vgs,lvs

```sh
sudo pvs
sudo vgs
sudo lvs
```




### LVM Disk Partitioning Runbook



### 1. Check Disk and LVM Status

Identify available disks, partitions, filesystems, and existing LVM configurations.

```bash
lsblk -o NAME,SIZE,FSTYPE,TYPE,MOUNTPOINTS
sudo pvs
sudo vgs
sudo lvs
df -hT
```

**Verify:**
- The correct physical disk and partition are identified.
- The target Volume Group exists.
- The Volume Group has sufficient free space.
- The target Logical Volume does not already exist.
- Important data has been backed up before making changes.

Check the available space:

```bash
sudo vgs ubuntu-vg
```

Check whether the target LV already exists:

```bash
sudo lvs ubuntu-vg/data-lv
```

Proceed only if `data-lv` does not exist and at least 20GiB of free space is available.

### 2. Create PV and VG (If Needed)

**Skip this step if the PV and VG already exist.**

Creating a new PV or changing disk partitions can destroy existing data if the wrong device is selected.

#### 2.1 Create a Physical Volume

For a verified, unused target partition:

```bash
sudo pvcreate /dev/sdX1
```

Replace `/dev/sdX1` with the actual target partition.

#### 2.2 Create a Volume Group

```bash
sudo vgcreate my-vg /dev/sdX1
```

#### 2.3 Extend an Existing Volume Group (Optional)

If adding a new PV to an existing VG:

```bash
sudo vgextend ubuntu-vg /dev/sdX1
```

#### 2.4 Verify

```bash
sudo pvs
sudo vgs
```

**Note:** The target partition must already exist before running `pvcreate`. Use a suitable partitioning tool to create it if required. Do not run `pvcreate` on an existing filesystem or LVM member containing important data.

For this server, `/dev/sda3` is already a PV belonging to `ubuntu-vg`. No PV or VG creation is required.

---

### 3. Create a Logical Volume

Create a new 20GiB Logical Volume named `data-lv`.

```bash
sudo lvcreate -L 20G -n data-lv ubuntu-vg
```

**Command explanation:**

| Option | Description |
|---|---|
| `lvcreate` | Creates a Logical Volume |
| `-L 20G` | Allocates 20GiB |
| `-n data-lv` | Sets the LV name |
| `ubuntu-vg` | Specifies the Volume Group |

Verify the new LV:

```bash
sudo lvs
sudo lvdisplay /dev/ubuntu-vg/data-lv
```

Expected result: `data-lv` exists with a size of 20GiB.

---

### 4. Create a Filesystem

Format the new Logical Volume with the ext4 filesystem.

**Warning:** Formatting an existing filesystem destroys its previous filesystem structure and can cause data loss. Confirm the target LV before proceeding.

```bash
lsblk -f /dev/ubuntu-vg/data-lv
```

For a verified, newly created, empty LV:

```bash
sudo mkfs.ext4 /dev/ubuntu-vg/data-lv
```

Verify the filesystem:

```bash
sudo blkid /dev/ubuntu-vg/data-lv
```

Expected filesystem type:

```text
TYPE="ext4"
```

---

### 5. Create a Mount Point

Create the directory where the filesystem will be mounted.

```bash
sudo mkdir -p /data
```

Verify that the directory exists and is empty:

```bash
ls -la /data
```

Check whether anything is already mounted there:

```bash
findmnt --mountpoint /data
```

Do not mount over a directory containing existing data without planning its migration.

---

### 6. Mount the Filesystem

Mount the new Logical Volume:

```bash
sudo mount /dev/ubuntu-vg/data-lv /data
```

Verify the mount:

```bash
df -hT /data
findmnt --mountpoint /data
lsblk -f
```

Expected result:

```text
/dev/mapper/ubuntu--vg-data--lv  ext4  20G  ...  /data
```

The filesystem should be mounted at `/data` and accessible.

---

### 7. Make the Mount Persistent

By default, a manual mount does not necessarily survive a reboot. Configure `/etc/fstab` to mount the filesystem automatically.

#### 7.1 Get the Filesystem UUID

```bash
sudo blkid /dev/ubuntu-vg/data-lv
```

Example:

```text
UUID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
TYPE="ext4"
```

#### 7.2 Back Up /etc/fstab

```bash
sudo cp -a /etc/fstab /etc/fstab.bak
```

#### 7.3 Edit /etc/fstab

```bash
sudo nano /etc/fstab
```

Add the following entry, replacing the placeholder with the actual UUID:

```fstab
UUID=<ACTUAL_UUID>  /data  ext4  defaults  0  2
```

**fstab fields:**

| Field | Description |
|---|---|
| UUID | Filesystem identifier |
| `/data` | Mount point |
| `ext4` | Filesystem type |
| `defaults` | Standard mount options |
| `0` | Disable dump backup |
| `2` | Filesystem check order |

Do not add a duplicate entry for the same mount point.

#### 7.4 Validate the Configuration

```bash
sudo findmnt --verify --verbose
```

Reload systemd configuration:

```bash
sudo systemctl daemon-reload
```

Test the fstab entry:

```bash
sudo umount /data
sudo mount /data
```

Verify:

```bash
findmnt --mountpoint /data
df -hT /data
```

**Expected result:** `/data` mounts successfully using the configuration in `/etc/fstab`.

---

### 8. Post-Configuration Validation

Run the following commands:

```bash
sudo pvs
sudo vgs
sudo lvs
lsblk -f
df -hT /data
findmnt --mountpoint /data
```

---

### 9. Rollback Procedure

Use this procedure only if the new LV contains no data that needs to be retained.

#### 9.1 Remove the fstab Entry

Edit `/etc/fstab` and remove the entry created for `/data`.

```bash
sudo nano /etc/fstab
```

Validate the file:

```bash
sudo findmnt --verify --verbose
sudo systemctl daemon-reload
```

#### 9.2 Unmount the Filesystem

```bash
sudo umount /data
```

Verify that it is unmounted:

```bash
findmnt --mountpoint /data
```

If the filesystem is busy, identify the processes using it before proceeding.

#### 9.3 Remove the Logical Volume

**Destructive operation:** This permanently removes the LV and its filesystem.

Only execute after confirming the correct LV and that its data is no longer required.

```bash
sudo lvremove /dev/ubuntu-vg/data-lv
```

#### 9.4 Verify Available Space

```bash
sudo lvs
sudo vgs
```

Expected result: `data-lv` no longer exists, and its allocated space is returned to `ubuntu-vg`.

Optionally remove the empty mount-point directory:

```bash
sudo rmdir /data
```

Do not remove the existing PV, VG, or root LV during this rollback.

---

### 10. LVM Command Reference

| Command | Purpose |
|---|---|
| `lsblk` | Display disks and block devices |
| `pvs` | Display Physical Volumes |
| `vgs` | Display Volume Groups |
| `lvs` | Display Logical Volumes |
| `pvcreate` | Create a Physical Volume |
| `vgcreate` | Create a Volume Group |
| `vgextend` | Add a PV to an existing VG |
| `lvcreate` | Create a Logical Volume |
| `lvdisplay` | Display detailed LV information |
| `mkfs.ext4` | Create an ext4 filesystem |
| `blkid` | Display filesystem identifiers |
| `mount` | Mount a filesystem |
| `umount` | Unmount a filesystem |
| `findmnt` | Display or verify mounted filesystems |
| `lvextend` | Extend a Logical Volume |
| `resize2fs` | Resize an ext2/3/4 filesystem |
| `lvremove` | Remove a Logical Volume |

---

### LVM Workflow Summary

```text
Physical Disk
     |
     v
Partition (if required)
     |
     v
Physical Volume (PV)
     |
     v
Volume Group (VG)
     |
     v
Logical Volume (LV)
     |
     v
Filesystem (ext4)
     |
     v
Mount Point (/data)
     |
     v
/etc/fstab
     |
     v
Validation
```

**Key Principle:** Always verify the target device, available capacity, existing data, and recovery options before making changes to storage.






















## LVM Disk Partitioning Step By Step

### 1. Check Disk and LVM Status

```sh
lsblk
sudo pvs
sudo vgs
sudo lvs
```

### 2. Create PV and VG (If Needed)
pvcreate → vgcreate / vgextend

### 3. Create a Logical Volume
```sh
sudo lvcreate -L 20G -n data-lv ubuntu-vg
```

### 4. Create a Filesystem
```sh
sudo mkfs.ext4 /dev/ubuntu-vg/data-lv
```

### 5. Create a Mount Point

```sh
sudo mkdir -p /data
```

### 6. Mount the Filesystem to a Directory

```sh
sudo mount /dev/ubuntu-vg/data-lv /data
```

### 7. Make the Mount Persistent

```sh
sudo blkid /dev/ubuntu-vg/data-lv
```
```sh
sudo findmnt --verify
```



