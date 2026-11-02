

# Bacula
It is the core backup engine responsible for scheduling, transferring, storing, and restoring data.

## Components

### 1. Director — The Brain of the System
**Service Name:** `bacula-director`
The Director is responsible for making decisions about backup operations.
It determines:
- Which server should be backed up?
- Which files or data should be included in the backup?
- When should the backup job run?
- Should the backup be Full or Incremental?
- Where should the backup data be stored?
The Director does not read database files directly.
Instead, it coordinates backup operations between the File Daemon and the Storage Daemon.
---

### 2. File Daemon — The Agent on Each Server
**Service Name:** `bacula-fd`
The File Daemon is responsible for accessing and transferring data from the servers being backed up.
Typically, each server that needs to be backed up has its own File Daemon installed.

#### Our Architecture
In our environment, we have two File Daemons:

| Server | File Daemon | Purpose |
|--------|-------------|---------|
| `backup` | `backup-fd` | Backs up files from the central backup server |
| `database` | `database-fd` | Backs up data from the PostgreSQL and MySQL server |

Therefore, having `bacula-fd` installed on both servers is completely normal.

#### Important Notes
- Each File Daemon operates independently.
- Each server has its own File Daemon configuration.
- Changing the File Daemon configuration on the `backup` server does not affect the `database` server.
- For live PostgreSQL or MySQL databases, database-aware backup tools should be used to ensure consistent backups.

---

### 3. Storage Daemon — Backup Storage Manager
**Service Name:** `bacula-sd`
The Storage Daemon receives backup data and writes it to the configured storage destination.

Backup storage can be configured using:
- A dedicated storage server
- Dedicated disks or storage volumes
- Other supported storage destinations
The Storage Daemon is responsible for managing the physical storage of backup data.

---

### 4. Catalog — Backup Metadata Database
**Database:** PostgreSQL
the Bacula Catalog is stored in PostgreSQL on the `backup` server.
The Catalog maintains metadata about backup operations.

#### Information Stored in the Catalog
- Which Job was executed and when?
- Was the backup successful or unsuccessful?
- Which files were included in the backup?
- Which Volume contains the backup data?
- Which backup is required for a Restore operation?

### Important Concept
The Catalog does not contain the actual backup data.
For example:
If a database backup is 10 GB:
- The **10 GB of backup data** is stored by the Storage Daemon.
- The **backup metadata** is stored in the Catalog.
The Catalog helps Bacula locate and restore backup data when needed.
---

## 5. Console — Command-Line Management Tool
**Program Name:** `bconsole`
The Bacula Console is a command-line interface used to communicate with the Director.
It allows administrators to manage and monitor backup operations.

### Common Commands
Connect to the Bacula Console:

```bash
bconsole
```
Check the Director status:

```bash
status director
```
Check the Storage Daemon status:

```bash
status storage
```
List backup Jobs:

```bash
list jobs
```

### Web-Based Management
Bacularis provides a web-based interface for many Bacula management operations.
Using Bacularis, administrators can:
- Create and configure backup Jobs
- Monitor backup status
- Run backup Jobs
- Perform Restore operations
- View Job history and execution results

---

## Summary — Bacula Components

| Component | Service / Program | Responsibility |
|-----------|-------------------|----------------|
| Director | `bacula-director` | Coordinates and schedules backup Jobs |
| File Daemon | `bacula-fd` | Reads and transfers data from client servers |
| Storage Daemon | `bacula-sd` | Receives and stores backup data |
| Catalog | PostgreSQL | Stores backup metadata and Job information |
| Console | `bconsole` | Provides command-line management |

## Backup Workflow
The typical backup workflow is:
1. **Director** starts a backup Job.
2. **File Daemon** reads and sends the required data.
3. **Storage Daemon** receives and stores the backup data.
4. **Catalog** records the backup metadata.
5. **Bacularis or bconsole** allows administrators to monitor and manage the backup.

### Architecture Overview

```text
                 +----------------------+
                 |       Bacularis      |
                 |   Web Management UI  |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |       Director       |
                 |    bacula-director   |
                 +----------+-----------+
                            |
              +-------------+-------------+
              |                           |
              v                           v
    +--------------------+      +--------------------+
    |    File Daemon     |      |   Storage Daemon   |
    |     bacula-fd      |----->|     bacula-sd      |
    |   database server  |      |    backup server   |
    +--------------------+      +---------+----------+
                                          |
                                          v
                                +--------------------+
                                |   Backup Storage   |
                                |    Backup Files    |
                                +--------------------+

                 +----------------------+
                 |       Catalog        |
                 |      PostgreSQL      |
                 |     backup server    |
                 +----------------------+
```
**Note:** The diagram is a simplified logical overview. The Director coordinates the components, while backup data is transferred from the File Daemon to the Storage Daemon. The Catalog stores metadata rather than the backup files themselves.



## Lifecycle

1. Director starts a Job.
For example, it instructs the system to back up the database server.

2. The Database Server Agent prepares and sends the data.
   For a live database, appropriate PostgreSQL or MySQL tools must be used to ensure a consistent backup.

3. Storage Daemon stores the data.
Backup files are written to the disk of the backup server.

4. Catalog records the results.
   Job details and file information are recorded so they can be located and restored later.

5. Bacularis displays the backup status.
   For example, it shows backup success or failure, execution time, and backup size.




# Baculum
It is a web-based management panel for Bacula that simplifies job creation, status monitoring, backup execution, and data restoration.


