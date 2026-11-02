# Bacula and Bacularis Backup Architecture

## 1. Architecture Components

### Backup Server

- **Bacula Director:** Manages backup jobs, scheduling, and backup execution commands.
- **Bacula Storage Daemon:** Receives and stores backup data in the `/opt/backups` directory.
- **Bacularis:** Provides a web-based interface for managing and monitoring Bacula backup operations.

### Database Server (`10.0.1.94`)

- **Bacula File Daemon (Agent):** Receives instructions from the Director, executes backup scripts, and transfers backup data to the Storage Daemon.
- **MySQL:** Accessible only through `127.0.0.1:3306`.
- **PostgreSQL:** Accessible only through `127.0.0.1:5432`.
- **Bash Scripts:** Execute `mysqldump` and `pg_dump` to generate logical database backups.

## 2. Backup Execution Workflow

1. The Bacula Director initiates the database backup job according to a predefined schedule or a manual request.
2. The Director communicates with the Bacula File Daemon on the Database Server through TCP port `9102`.
3. The Agent executes the corresponding Bash backup script for MySQL or PostgreSQL.
4. The script connects to the database locally and generates a database dump file.
5. The Agent transfers the dump file to the Bacula Storage Daemon on the Backup Server through TCP port `9103`.
6. The Storage Daemon stores the backup data, while Bacula records the job execution results in its Catalog.
7. Backup status, job history, and restore operations can be managed through the Bacularis Web Interface.

## 3. Network Communication and Security

| Source | Destination | Port | Purpose |
|---|---|---|---|
| Backup Server | Database Server | TCP 9102 | Director-to-Agent communication |
| Database Server | Backup Server | TCP 9103 | Backup data transfer to Storage |
| localhost | MySQL | TCP 3306 | Local MySQL dump execution |
| localhost | PostgreSQL | TCP 5432 | Local PostgreSQL dump execution |

### Security Considerations

- Access to TCP port `9102` is restricted to the Backup Server's IP address.
- Access to TCP port `9103` is restricted to the Database Server.
- Database ports are not exposed to the external network.
- Daily backup execution does not require SSH access.
- Bacula components authenticate using configured shared secrets, and enabling TLS encryption is recommended.

## 4. Backup Job Structure

| Job Name | Backup Script | Local Output File |
|---|---|---|
| `Backup-MySQL` | `backup-mysql.sh` | `latest.sql.gz` |
| `Backup-PostgreSQL` | `backup-postgresql.sh` | `latest.dump` |

Each backup job executes its corresponding script on the Database Server before transferring backup data.

Local dump files are overwritten during subsequent executions, while backup history and stored backup versions are maintained centrally by Bacula.

### Backup Retention Policy

The retention policy for keeping the **last three successful backups** must be designed and configured separately in Bacula.

This policy should be validated through restore testing to ensure that the required backup versions remain available and recoverable.

## 5. Text-Based Architecture Diagram

```text
                 +---------------------------+
                 |       Backup Server       |
                 |                           |
                 |      Bacula Director      |
                 |      Job Scheduling       |
                 |                           |
                 |         Bacularis         |
                 |      Web Interface        |
                 +-------------+-------------+
                               |
                               | TCP 9102
                               | Backup Commands
                               v
                 +---------------------------+
                 |      Database Server      |
                 |         10.0.1.94         |
                 |                           |
                 |    Bacula File Daemon     |
                 |          (Agent)          |
                 +-------------+-------------+
                               |
                               | Execute Scripts
                               v
                  +-------------------------+
                  |      Bash Scripts       |
                  |                         |
                  |    backup-mysql.sh      |
                  | backup-postgresql.sh    |
                  +------------+------------+
                               |
                    Local DB Connections
                               |
                 +-------------+-------------+
                 |                           |
                 v                           v
       +-------------------+       +-------------------+
       |       MySQL       |       |    PostgreSQL     |
       |  127.0.0.1:3306   |       |  127.0.0.1:5432   |
       +---------+---------+       +---------+---------+
                 |                           |
                 v                           v
       +-------------------+       +-------------------+
       |   latest.sql.gz   |       |    latest.dump    |
       +---------+---------+       +---------+---------+
                 |                           |
                 +-------------+-------------+
                               |
                               | Bacula File Daemon
                               | TCP 9103
                               v
                 +---------------------------+
                 |       Backup Server       |
                 |                           |
                 |   Bacula Storage Daemon   |
                 |                           |
                 |       /opt/backups        |
                 +-------------+-------------+
                               |
                               v
                 +---------------------------+
                 |       Bacula Catalog      |
                 |                           |
                 |    Job History / Status   |
                 |    Backup Metadata        |
                 +-------------+-------------+
                               |
                               v
                 +---------------------------+
                 |         Bacularis         |
                 |                           |
                 |   Monitoring / Restore    |
                 |   Job Logs / Management   |
                 +---------------------------+
```

**Implementation Notes:**

- The database dump scripts must be configured to run before Bacula reads the generated files, for example through `Client Run Before Job`.
- The `/opt/backups` directory must be configured as the storage location through the appropriate Bacula Storage Daemon device settings.
- Bacula Catalog metadata is maintained separately from the actual backup data.
- Retention and pruning settings must be carefully configured to preserve the required restore points.