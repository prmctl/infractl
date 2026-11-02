# Bacula Agent Installation and Configuration Guide on the Database Server

**Operating System:** Ubuntu 24.04  
**Database Server IP:** `10.0.1.94`  
**Service:** Bacula File Daemon (`bacula-fd`)  
**Port:** TCP 9102

## 1. Install Bacula File Daemon
First, update the system package repositories and install the Bacula Agent:
```bash
sudo apt update
sudo apt install -y bacula-fd
```

If using an ArvanCloud or IranServer mirror, ensure that the Ubuntu 24.04 package repository has been configured with a valid mirror URL before installation.

Verify the installation:
```bash
bacula-fd -?
```

## 2. Back Up the Existing Configuration
Before modifying the configuration, create a backup of the original file:
```bash
sudo cp /etc/bacula/bacula-fd.conf /etc/bacula/bacula-fd.conf.bak
```

## 3. Generate a Shared Secret for Agent–Director Authentication
Generate a secure shared secret for authentication between the Bacula Director and the File Daemon:
```bash
openssl rand -base64 36
```
The generated secret must be identical in both the Agent configuration and the corresponding Client resource configuration on the Bacula Director.

## 4. Configure the Bacula Agent
Open the configuration file:
```bash
sudo nano /etc/bacula/bacula-fd.conf
```
Replace its contents with the following configuration:

```conf
Director {
  Name = backup-dir
  Password = "YOUR_SHARED_SECRET"
}

FileDaemon {
  Name = database-fd
  FDport = 9102
  FDAddress = 10.0.1.94
  WorkingDirectory = /var/lib/bacula
  Pid Directory = /run/bacula
  Maximum Concurrent Jobs = 2
}

Messages {
  Name = Standard
  director = backup-dir = all, !skipped, !restored
}
```

### Configuration Parameters
- **`Director.Name`:** Name of the Bacula Director authorized to connect to the Agent.
- **`Director.Password`:** Shared authentication secret used between the Agent and Director.
- **`FileDaemon.Name`:** Name of the Agent registered in the Bacula Director configuration.
- **`FDport`:** TCP port used by the File Daemon to accept Bacula connections.
- **`FDAddress`:** Network interface address on which the File Daemon listens.

**Note:** The name `backup-dir` is an example and must match the actual Director name configured on the Backup Server.

## 5. Validate the Configuration
Before starting the service, verify the configuration file syntax:
```bash
sudo bacula-fd -t -c /etc/bacula/bacula-fd.conf
```

If no errors are reported, enable and start the service:
```bash
sudo systemctl enable --now bacula-fd
sudo systemctl restart bacula-fd
```

Check the service status:
```bash
sudo systemctl status bacula-fd --no-pager
```

Expected output:
```text
Active: active (running)
```

## 6. Verify the Agent Listening Port
Check whether the Bacula File Daemon is listening on TCP port `9102`:

```bash
sudo ss -lntp | grep 9102
```

Expected output:
```text
LISTEN ... 10.0.1.94:9102
```

This confirms that the Agent is listening on the Database Server's internal network interface and is ready to accept connections.

## 7. Restrict Access Using the Firewall
Only the Backup Server's IP address should be allowed to connect to the Bacula Agent.
Add the following UFW rule:
```bash
sudo ufw allow from BACKUP_SERVER_IP \
  to 10.0.1.94 port 9102 proto tcp
```
Replace `BACKUP_SERVER_IP` with the actual IP address of the Backup Server.

### Security Considerations
The rule above only adds an allow rule. To prevent connections from unauthorized IP addresses, the firewall must also have a restrictive default incoming policy or appropriate deny rules.

Before enabling UFW, ensure that administrative SSH access is explicitly permitted to avoid losing remote access to the server.

Verify the firewall rules:

```bash
sudo ufw status numbered
```

## 8. Prepare the Backup Script Directory

Create a dedicated directory for database backup scripts:

```bash
sudo mkdir -p /opt/bacula/scripts

sudo chown root:root /opt/bacula/scripts
sudo chmod 755 /opt/bacula/scripts
```

The database dump scripts will be stored at:

```text
/opt/bacula/scripts/backup-mysql.sh
/opt/bacula/scripts/backup-postgresql.sh
```

These scripts use `mysqldump` and `pg_dump` to generate logical backups of the local MySQL and PostgreSQL databases.

## 9. Configure Script Execution Through the Agent
A separate backup job is defined for each database in the Bacula Director configuration.

Example of executing the PostgreSQL backup script within a Bacula Job:
```conf
RunScript {
  RunsWhen = Before
  RunsOnClient = yes
  FailJobOnError = yes
  Command = "/usr/bin/sudo -n -u dbbackup /opt/bacula/scripts/backup-postgresql.sh"
}
```

### Execution Details

- **`RunsWhen = Before`:** Executes the script before the backup operation begins.
- **`RunsOnClient = yes`:** Executes the script on the Database Server rather than the Backup Server.
- **`FailJobOnError = yes`:** Marks the backup job as failed if the script returns an error.
- **`Command`:** Specifies the command used to execute the PostgreSQL backup script.

The command runs on the Database Server and requires a `dbbackup` system user with the appropriate permissions configured in `sudoers`.

**Important:** Installing the Bacula Agent alone does not automatically execute backup scripts. The corresponding Job and RunScript configurations must also be defined in the Bacula Director.

## 10. Final Verification
Run the following commands to verify the Agent configuration, service status, and listening port:

```bash
sudo bacula-fd -t -c /etc/bacula/bacula-fd.conf
sudo systemctl is-active bacula-fd
sudo ss -lntp | grep 9102
```
Once the Backup Server has been configured, verify connectivity through the Bacula Console (`bconsole`):

```text
status client=database-fd
```
This command checks the status of the registered Bacula File Daemon.

## Conclusion
After completing these steps, the Bacula File Daemon will be installed and configured on the Database Server (`10.0.1.94`) and ready to receive instructions from the Bacula Director.

The Agent receives backup commands through TCP port `9102`. During backup execution, it transfers backup data to the Bacula Storage Daemon on the Backup Server through TCP port `9103`.

### Implementation Status
This guide covers the installation and initial configuration of the Bacula File Daemon.

Successful backup execution, Director–Agent authentication, and backup data transfer must be verified through practical end-to-end testing after the Backup Server configuration is complete.