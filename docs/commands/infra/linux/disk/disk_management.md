
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