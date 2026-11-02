# MySQL Backup Guide Using Bash

## Overview

This guide explains how to configure a Bash script to generate compressed, timestamped MySQL database backups using `mysqldump`.

### Configuration Details

| Parameter | Example Value |
|---|---|
| Database | `app_mysql` |
| Backup Tool | `mysqldump` |
| Operating System User | `dbbackup` |
| Script Path | `/opt/db-backup/backup-mysql.sh` |
| Backup Directory | `/var/backups/databases/mysql` |
| Output Format | `.sql.gz` |

## Step 1 — Install Prerequisites

Update the package repositories and install the required utilities:

```bash
sudo apt update
sudo apt install -y default-mysql-client gzip util-linux
```

## Step 2 — Create the Backup User and Directories

Create the `dbbackup` system user if it does not already exist:

```bash
id dbbackup || sudo useradd --system \
  --shell /usr/sbin/nologin \
  --home-dir /var/lib/db-backup \
  --create-home dbbackup
```

Create the required directories with appropriate ownership and permissions:

```bash
sudo install -d -o root -g root -m 755 /opt/db-backup
sudo install -d -o root -g dbbackup -m 750 /etc/db-backup
sudo install -d -o dbbackup -g dbbackup -m 700 \
  /var/backups/databases/mysql
```

These permissions ensure that the backup scripts remain under root ownership, while the `dbbackup` user can securely access the configuration and backup directories.

## Step 3 — Configure MySQL Connection Credentials

Create the MySQL client configuration file:

```bash
sudo nano /etc/db-backup/mysql.cnf
```

Add the following content:

```ini
[client]
host=127.0.0.1
port=3306
user=backup_user
password=YOUR_MYSQL_PASSWORD
```

Replace `YOUR_MYSQL_PASSWORD` with the actual password of the MySQL backup user.

Configure file ownership and permissions:

```bash
sudo chown dbbackup:dbbackup /etc/db-backup/mysql.cnf
sudo chmod 600 /etc/db-backup/mysql.cnf
```

The MySQL backup user must have sufficient privileges to read the required tables, views, triggers, stored routines, and events.

## Step 4 — Create the Backup Script

Create the Bash script:

```bash
sudo nano /opt/db-backup/backup-mysql.sh
```

Add the following content:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

DB_NAME="app_mysql"
DEST="/var/backups/databases/mysql"
CONFIG="/etc/db-backup/mysql.cnf"

DATE="$(date +%Y%m%d_%H%M%S)"
OUT="$DEST/${DB_NAME}_${DATE}.sql.gz"
TMP=""

log() {
    echo "[$(date -Is)] [mysql] $*"
}

cleanup() {
    if [[ -n "$TMP" ]]; then
        rm -f -- "$TMP"
    fi
}

trap cleanup EXIT

exec 9>"$DEST/.backup.lock"
flock -n 9 || {
    log "ERROR: Backup already running"
    exit 1
}

[[ -r "$CONFIG" ]] || {
    log "ERROR: Configuration file not readable"
    exit 1
}

TMP="$(mktemp "$DEST/.backup.XXXXXXXX.sql.gz")"

log "Starting backup: $DB_NAME"

mysqldump \
    --defaults-extra-file="$CONFIG" \
    --single-transaction \
    --quick \
    --routines \
    --events \
    --triggers \
    --no-tablespaces \
    --hex-blob \
    --databases "$DB_NAME" \
    | gzip -c > "$TMP"

gzip -t "$TMP"
test -s "$TMP"

mv -n -- "$TMP" "$OUT"
TMP=""

log "SUCCESS: $OUT"
```

### Script Functionality

The script performs the following operations:

1. Enables strict Bash error handling and restrictive file permissions.
2. Generates a timestamped filename for each backup.
3. Uses `flock` to prevent concurrent executions.
4. Verifies that the MySQL configuration file is readable.
5. Creates a temporary file for the backup.
6. Executes `mysqldump` to generate a logical database backup.
7. Compresses the SQL dump using `gzip`.
8. Verifies the compressed file's integrity and checks that it is not empty.
9. Moves the completed backup to its final timestamped filename.
10. Removes temporary files when the script exits.

Each successful execution produces a separate backup file.

Example output:

```text
app_mysql_20261102_020000.sql.gz
app_mysql_20261103_020000.sql.gz
app_mysql_20261104_020000.sql.gz
```

## Step 5 — Configure Script Permissions

Set the script ownership to `root` and make it executable:

```bash
sudo chown root:root /opt/db-backup/backup-mysql.sh
sudo chmod 755 /opt/db-backup/backup-mysql.sh
```

This allows the `dbbackup` user to execute the script without being able to modify it.

## Step 6 — Execute and Verify the Backup

Run the backup script as the `dbbackup` user:

```bash
sudo -u dbbackup /opt/db-backup/backup-mysql.sh
```

Check the generated backup files:

```bash
sudo ls -lh /var/backups/databases/mysql/
```

Verify the integrity of the compressed backup files:

```bash
sudo gzip -t /var/backups/databases/mysql/app_mysql_*.sql.gz
```

If the command completes without errors, the compressed files have passed the gzip integrity check.

**Note:** Compression integrity verification does not guarantee database recoverability. Periodic restore testing is required.

## Step 7 — Restore a MySQL Backup

Before restoring a backup, prepare a separate test database environment or dedicated recovery server.

Because the dump is generated using the `--databases` option, it contains statements that create or select the original database.

Restore the backup using:

```bash
gzip -dc /path/to/app_mysql_BACKUP.sql.gz \
  | mysql --defaults-extra-file=/path/to/restore.cnf
```

Replace the example paths with the actual backup file and MySQL restore configuration.

**Warning:** The SQL dump may contain statements that drop or recreate database tables. Do not execute the restore command against a production database without reviewing the dump and confirming the intended restore target.

## Technical Considerations

- **Timestamped Backups:** Each backup is stored in a separate file with a unique date and time.
- **Concurrency Protection:** The `flock` utility prevents multiple instances of the backup script from running simultaneously.
- **Temporary File Cleanup:** Incomplete temporary backup files are removed if the script fails.
- **InnoDB Consistency:** The `--single-transaction` option provides a consistent snapshot for transactional InnoDB tables under appropriate conditions.
- **Compression:** SQL dumps are compressed using gzip to reduce storage requirements.
- **Backup Retention:** A separate retention and cleanup policy must be implemented to prevent the backup directory from consuming all available disk space.
- **Off-Server Storage:** Backups should also be transferred to a separate server or storage system to protect against failure or loss of the original database server.
- **Restore Validation:** Periodic restore tests should be performed to verify that the backup files are usable.

## Conclusion

The Bash-based MySQL backup solution generates compressed, timestamped logical backups of the `app_mysql` database.

The script runs under the dedicated `dbbackup` system account, uses restricted filesystem permissions, prevents concurrent executions, and validates compressed backup files before finalizing them.

For production environments, this solution should be combined with automated scheduling, centralized backup storage, retention management, monitoring, and regular restore testing.