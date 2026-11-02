# PostgreSQL Backup Guide Using Bash

## Overview

This guide explains how to configure a Bash script to generate compressed, timestamped PostgreSQL database backups using `pg_dump` in the Custom archive format.

### Configuration Details

| Parameter | Example Value |
|---|---|
| Database | `app_postgres` |
| Backup Tool | `pg_dump` |
| Example Version | PostgreSQL 16 |
| Operating System User | `dbbackup` |
| Script Path | `/opt/db-backup/backup-postgresql.sh` |
| Backup Directory | `/var/backups/databases/postgresql` |
| Output Format | `.dump` (Custom) |

## Step 1 — Install Prerequisites

Update the package repositories and install the PostgreSQL client and required utilities:

```bash
sudo apt update
sudo apt install -y postgresql-client-16 util-linux
```

The PostgreSQL client version should be compatible with the PostgreSQL server version. In particular, `pg_dump` must not be older than the server's major version.

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
  /var/backups/databases/postgresql
```

The backup scripts remain under root ownership, while the `dbbackup` user has access to the configuration and backup directories.

## Step 3 — Configure PostgreSQL Connection Credentials

Create the PostgreSQL password file:

```bash
sudo nano /etc/db-backup/pgpass
```

Add the following entry:

```text
127.0.0.1:5432:app_postgres:backup_user:YOUR_POSTGRES_PASSWORD
```

Replace `YOUR_POSTGRES_PASSWORD` with the actual password of the PostgreSQL backup user.

Set the appropriate ownership and permissions:

```bash
sudo chown dbbackup:dbbackup /etc/db-backup/pgpass
sudo chmod 600 /etc/db-backup/pgpass
```

The PostgreSQL backup user must have permission to connect to the database and read all required data and database objects.

## Step 4 — Create the PostgreSQL Backup Script

Create the backup script:

```bash
sudo nano /opt/db-backup/backup-postgresql.sh
```

Add the following content:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

DB_NAME="app_postgres"
DB_HOST="127.0.0.1"
DB_PORT="5432"
DB_USER="backup_user"

DEST="/var/backups/databases/postgresql"

export PGPASSFILE="/etc/db-backup/pgpass"
export PGCONNECT_TIMEOUT=10

DATE="$(date +%Y%m%d_%H%M%S)"
OUT="$DEST/${DB_NAME}_${DATE}.dump"
TMP=""

log() {
    echo "[$(date -Is)] [postgresql] $*"
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

[[ -r "$PGPASSFILE" ]] || {
    log "ERROR: Password file not readable"
    exit 1
}

TMP="$(mktemp "$DEST/.backup.XXXXXXXX.dump")"

log "Starting backup: $DB_NAME"

pg_dump \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --dbname="$DB_NAME" \
    --format=custom \
    --compress=6 \
    --no-password \
    --file="$TMP"

pg_restore --list "$TMP" >/dev/null
test -s "$TMP"

mv -n -- "$TMP" "$OUT"
TMP=""

log "SUCCESS: $OUT"
```

### Script Functionality

The script performs the following operations:

1. Enables strict Bash error handling and restrictive file permissions.
2. Defines the PostgreSQL connection parameters and backup destination.
3. Generates a timestamped filename for each backup.
4. Uses `flock` to prevent concurrent backup executions.
5. Verifies that the PostgreSQL password file is readable.
6. Creates a temporary file for the backup.
7. Executes `pg_dump` using the Custom archive format with compression level `6`.
8. Checks the archive structure using `pg_restore --list`.
9. Verifies that the generated backup file is not empty.
10. Moves the completed backup to its final timestamped filename.
11. Removes temporary files when the script exits.

Each successful execution creates a separate backup file.

Example output:

```text
app_postgres_20261102_020000.dump
app_postgres_20261103_020000.dump
app_postgres_20261104_020000.dump
```

## Step 5 — Configure Script Permissions

Set the script ownership to `root` and make it executable:

```bash
sudo chown root:root /opt/db-backup/backup-postgresql.sh
sudo chmod 755 /opt/db-backup/backup-postgresql.sh
```

This allows the `dbbackup` user to execute the script without modifying its contents.

## Step 6 — Execute and Verify the Backup

Run the backup script as the `dbbackup` user:

```bash
sudo -u dbbackup /opt/db-backup/backup-postgresql.sh
```

Check the generated backup files:

```bash
sudo ls -lh /var/backups/databases/postgresql/
```

Verify the archive structure:

```bash
sudo pg_restore --list \
  /var/backups/databases/postgresql/app_postgres_BACKUP.dump
```

Replace `app_postgres_BACKUP.dump` with the actual backup filename.

The `pg_restore --list` command verifies that the archive's table of contents can be read. It does not guarantee that all archived data is valid or that the database can be fully restored.

## Step 7 — Restore a PostgreSQL Backup

Before restoring the backup, create a separate test database.

Create the target database:

```bash
sudo -u postgres createdb app_postgres_restore
```

Restore the backup using `pg_restore`:

```bash
pg_restore \
  --host=127.0.0.1 \
  --port=5432 \
  --username=restore_user \
  --dbname=app_postgres_restore \
  --no-owner \
  --no-acl \
  --exit-on-error \
  /path/to/app_postgres_BACKUP.dump
```

Replace the example backup path with the actual archive location.

The `restore_user` must have sufficient privileges to create and restore the required database objects in the target database.

### Restore Options

- **`--no-owner`:** Prevents restoration of original object ownership.
- **`--no-acl`:** Skips restoration of access control privileges.
- **`--exit-on-error`:** Stops the restore operation immediately if an SQL error occurs.
- **`--dbname`:** Specifies the target database for restoration.

**Important:** Perform restoration tests in an isolated environment to avoid accidentally modifying production data.

## Technical Considerations

- **Custom Archive Format:** PostgreSQL's Custom format is designed for use with `pg_restore` and supports selective and parallel restoration.
- **Timestamped Backups:** Each backup is stored as a separate file with a unique date and time.
- **Concurrency Protection:** The `flock` utility prevents multiple instances of the backup script from running simultaneously.
- **Temporary File Cleanup:** Incomplete temporary backup files are removed if the script fails.
- **Database Consistency:** `pg_dump` generates a transactionally consistent logical backup of a single PostgreSQL database.
- **Global Objects:** PostgreSQL roles, tablespaces, and other cluster-wide objects are not included in this database dump and must be backed up separately, for example using `pg_dumpall --globals-only`.
- **Backup Validation:** Periodic test restores are necessary to verify that backups can be successfully recovered.
- **Backup Retention:** A separate retention and cleanup policy must be implemented to prevent excessive disk usage.
- **Off-Server Storage:** Backup files should be transferred to an independent server or storage system to protect against failure of the original database server.

## Conclusion

The Bash-based PostgreSQL backup solution generates compressed, timestamped logical backups of the `app_postgres` database using `pg_dump` in the Custom archive format.

The script runs under the dedicated `dbbackup` system account, uses restricted filesystem permissions, prevents concurrent execution, and performs basic archive validation before finalizing each backup.

For production environments, this solution should be integrated with automated scheduling, centralized backup storage, retention management, monitoring, and regular restore testing.