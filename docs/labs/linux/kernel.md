# Linux Kernel 

## 1. Kernel Fundamentals 

### Kernel چیست؟

### Kernel Space vs User Space

### Kernel Mode vs User Mode

### System Calls

- `open()`
- `read()`
- `write()`
- `fork()`
- `exec()`

### Kernel Modules

- `lsmod`
- `modprobe`
- `rmmod`

### Kernel Information

- `uname`
- `/proc`
- `/sys`

---

## 2. Process Management 

### Process

- Process چیست؟
- PID
- PPID
- Parent Process
- Child Process

### Process States

- Running
- Sleeping
- Stopped
- Zombie

### Process Creation

- `fork()`
- `exec()`

### Threads

### Context Switch

### Process Scheduling

- Scheduler
- Priority
- `nice`
- `renice`
- CPU Time

### Signals

- `SIGTERM`
- `SIGKILL`
- `SIGHUP`
- `SIGINT`

### Process Monitoring

- `ps`
- `top`
- `htop`
- `pidstat`
- `/proc/<PID>`

---

## 3. Memory Management 

### Memory Concepts

- Physical Memory
- Virtual Memory
- Process Address Space
- Page
- Paging
- Page Table
- Page Fault
- Page Cache
- `mmap`

### Swap

- Swap چیست؟
- Swappiness

### Memory Pressure

- Memory Pressure
- OOM
- OOM Killer

### Memory Monitoring

- `free`
- `vmstat`
- `/proc/meminfo`
- `top`

---

## 4. File System & VFS 

### Virtual File System (VFS)

- VFS
- inode
- dentry

### File Descriptor

- File Descriptor چیست؟
- File Descriptor Limits
- `ulimit`
- `/proc/sys/fs/`

### File Systems

- ext4
- XFS
- tmpfs
- procfs
- sysfs

### Mount

### File System Monitoring

- `df`
- `du`
- `lsblk`
- `mount`

---

## 5. I/O Management 

### I/O Fundamentals

- I/O چیست؟
- File Descriptor
- `read()`
- `write()`

### I/O Models

- Blocking I/O
- Non-blocking I/O

### I/O Multiplexing

- `select`
- `poll`
- `epoll` 

### Asynchronous I/O

- Async I/O
- `io_uring` (آشنایی)

### I/O Monitoring

- `iostat`
- `iotop`
- `vmstat`

---

## 6. Linux Networking 

### Linux Network Stack

### Network Fundamentals

- Network Interface
- IP Address
- Port

### Socket

- Socket چیست؟
- TCP Socket
- UDP Socket
- Unix Domain Socket

### TCP

- TCP Connection
- TCP States
  - `LISTEN`
  - `ESTABLISHED`
  - `TIME_WAIT`
  - `CLOSE_WAIT`

### Routing

- Routing
- Routing Table

### DNS Basics

### Netfilter

- Netfilter
- `iptables`
- `nftables`

### Network Namespace

### Network Troubleshooting

- `ip`
- `ss`
- `ping`
- `traceroute`
- `dig`
- `curl`
- `tcpdump`
- `ethtool`

---

## 7. Inter-Process Communication (IPC) 

### IPC چیست؟

### IPC Mechanisms

- Signals
- Pipe
- FIFO
- Shared Memory
- Unix Domain Socket
- Message Queue

---

## 8. Resource Isolation 

### Linux Namespaces

- Namespace چیست؟
- PID Namespace
- Network Namespace
- Mount Namespace
- User Namespace
- UTS Namespace
- IPC Namespace
- Cgroup Namespace

### Control Groups (cgroups)

- cgroups چیست؟
- CPU Limits
- Memory Limits
- I/O Limits
- cgroup v2

### Containers

- Container چیست؟
- Namespace + cgroups
- ارتباط Kernel با Docker
- ارتباط Kernel با Kubernetes

---

## 9. Kernel Security 

### User & Identity

- UID
- GID

### File Permissions

### Linux Capabilities

### seccomp

### Linux Security Modules (LSM)

- SELinux
- AppArmor

### Container Security

---

## 10. Kernel Configuration & Tuning 

### Kernel Interfaces

- `/proc`
- `/sys`

### sysctl

- `sysctl`
- `sysctl -a`
- `/etc/sysctl.conf`
- `/etc/sysctl.d/`

### Kernel Tuning

- Network Tuning
- TCP Tuning
- Memory Tuning
- File Descriptor Limits

---

## 11. Observability & Troubleshooting 

### Kernel Logs

- `dmesg`
- `journalctl -k`

### Kernel Information

- `/proc`
- `/sys`

### System Call Tracing

- `strace`

### Open Files

- `lsof`

### Performance Analysis

- `perf`
- `ftrace`
- eBPF

### Troubleshooting Methodology

#### CPU Bottleneck

- `top`
- `htop`
- `pidstat`
- `perf`

#### Memory Bottleneck

- `free`
- `vmstat`
- `/proc/meminfo`
- OOM Killer

#### Disk I/O Bottleneck

- `iostat`
- `iotop`
- `vmstat`

#### Network Bottleneck

- `ss`
- `ip`
- `tcpdump`
- `ethtool`

---

## 12. Kernel Boot & Runtime 

### Boot Process

1. BIOS / UEFI
2. Bootloader
3. GRUB
4. Kernel Loading
5. initramfs
6. Kernel Initialization
7. PID 1
8. systemd

