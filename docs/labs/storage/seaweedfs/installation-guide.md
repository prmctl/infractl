---
author: Your Name
date: 2026-09-15
description: A step-by-step guide to deploying SeaweedFS Master, Volume
  Server, Filer, and the S3-compatible gateway natively on Ubuntu
  without Docker.
tags:
- SeaweedFS
- Object Storage
- S3
- Ubuntu
- Linux
- systemd
- Infrastructure
title: How to Install and Configure SeaweedFS on Ubuntu with systemd
---

# How to Install and Configure SeaweedFS on Ubuntu with systemd

SeaweedFS is a distributed storage system designed to store and serve
large numbers of files efficiently. It can expose several storage
interfaces, including a native file-oriented API through the **Filer**
and an **S3-compatible API** for applications and tools that already
speak the Amazon S3 protocol.

This guide walks through a native, systemd-based SeaweedFS deployment on
Ubuntu. No Docker or Kubernetes is required.

By the end of the article, the server will run:

-   **Master Server** --- manages topology and volume placement.
-   **Volume Server** --- stores the actual file data.
-   **Filer** --- provides directories, filenames, and file metadata.
-   **S3 Gateway** --- exposes an S3-compatible API.
-   **AWS CLI** --- provides a convenient way to test the S3 endpoint.

> This tutorial builds a **single-node lab deployment**. It is excellent
> for learning, development, and small internal environments, but it is
> not highly available. Production deployments should use multiple
> nodes, replication, TLS, proper firewall rules, monitoring, backups,
> and an appropriate metadata backend.

## Architecture

The final request path looks like this:

``` text
Application / AWS CLI
        |
        | S3 API :8333
        v
+-------------------+
|    S3 Gateway     |
+---------+---------+
          |
          v
+-------------------+
|       Filer       | :8888
| paths + metadata  |
+---------+---------+
          |
          +--------------------+
          |                    |
          v                    v
+-------------------+   +-------------------+
|      Master       |   |   Volume Server   |
|      :9333        |   |      :8080        |
+-------------------+   +-------------------+
                               |
                               v
                         .dat / .idx files
```

The Master does not store the object payload itself. It manages topology
and allocation. The Volume Server stores file data, while the Filer adds
a conventional namespace such as `/backups/database.sql` on top of
SeaweedFS file IDs.

## Prerequisites

This guide assumes:

-   Ubuntu 24.04 LTS or a comparable modern Ubuntu release
-   An x86-64 server
-   Root access or equivalent `sudo` privileges
-   Internet access for downloading SeaweedFS and AWS CLI
-   A single-node deployment for learning purposes

Check the system first:

``` sh
uname -a
lsb_release -a
df -h
ip addr
```

## 1. Install SeaweedFS

Download and install the SeaweedFS `weed` binary using the project's
installation method, or place the downloaded binary in `/usr/local/bin`.

After installation, verify it:

``` sh
/usr/local/bin/weed version
```

You should see the installed SeaweedFS version and architecture.

You can also confirm the binary location:

``` sh
command -v weed
```

## 2. Create a Dedicated Service Account

Do not run the storage services as root. Create a dedicated system
account:

``` sh
useradd --system --home-dir /var/lib/seaweedfs --shell /usr/sbin/nologin seaweedfs
```

Create the configuration and data directories:

``` sh
mkdir -p /etc/seaweedfs
mkdir -p /var/lib/seaweedfs/master
mkdir -p /var/lib/seaweedfs/volume
mkdir -p /var/lib/seaweedfs/filer
```

Set ownership:

``` sh
chown -R seaweedfs:seaweedfs /var/lib/seaweedfs
chmod 750 /var/lib/seaweedfs
chmod 750 /var/lib/seaweedfs/master
chmod 750 /var/lib/seaweedfs/volume
chmod 750 /var/lib/seaweedfs/filer
```

## 3. Configure the Master Server

The Master tracks the cluster topology and assigns file IDs. For a
single-master deployment, explicitly use `-peers=none`.

Create the systemd unit:

``` sh
nano /etc/systemd/system/seaweed-master.service
```

Add:

``` ini
[Unit]
Description=SeaweedFS Master Server
Documentation=https://github.com/seaweedfs/seaweedfs
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=seaweedfs
Group=seaweedfs

ExecStart=/usr/local/bin/weed master -mdir=/var/lib/seaweedfs/master -ip=127.0.0.1 -ip.bind=127.0.0.1 -port=9333 -peers=none

Restart=on-failure
RestartSec=5
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
```

Reload systemd and start the service:

``` sh
systemctl daemon-reload
systemctl enable --now seaweed-master
```

Verify it:

``` sh
systemctl status seaweed-master --no-pager -l
journalctl -u seaweed-master -n 50 --no-pager
```

Check the listening ports:

``` sh
ss -lntp | grep weed
```

With the default port relationship used by this deployment, the Master
HTTP interface listens on `9333` and its gRPC endpoint on `19333`.

> Binding internal SeaweedFS components to `127.0.0.1` is intentional.
> On an Internet-facing server, do not expose internal Master, Volume,
> or Filer ports directly unless you have designed the network and
> authentication model for it.

## 4. Configure the Volume Server

The Volume Server stores the actual object data.

Create its unit:

``` sh
nano /etc/systemd/system/seaweed-volume.service
```

Add:

``` ini
[Unit]
Description=SeaweedFS Volume Server
Documentation=https://github.com/seaweedfs/seaweedfs
After=network-online.target seaweed-master.service
Wants=network-online.target
Requires=seaweed-master.service

[Service]
Type=simple
User=seaweedfs
Group=seaweedfs

ExecStart=/usr/local/bin/weed volume -dir=/var/lib/seaweedfs/volume -master=127.0.0.1:9333 -ip=127.0.0.1 -ip.bind=127.0.0.1 -port=8080 -max=5

Restart=on-failure
RestartSec=5
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
```

Start it:

``` sh
systemctl daemon-reload
systemctl enable --now seaweed-volume
```

Verify:

``` sh
systemctl status seaweed-volume --no-pager -l
journalctl -u seaweed-volume -n 50 --no-pager
ss -lntp | grep weed
```

In this example:

-   Volume HTTP: `127.0.0.1:8080`
-   Volume gRPC: `127.0.0.1:18080`

The `-max=5` option limits the number of SeaweedFS volume slots this
server will host. It does **not** mean 5 GB of storage.

## 5. Test the Master and Volume Layer

Ask the Master to allocate a file ID:

``` sh
curl http://127.0.0.1:9333/dir/assign
```

A successful response contains values similar to:

``` json
{
  "fid": "3,03761b871b",
  "url": "127.0.0.1:8080",
  "publicUrl": "127.0.0.1:8080",
  "count": 1
}
```

Create a test file:

``` sh
echo "Hello SeaweedFS" > /tmp/seaweed-test.txt
```

Upload it to the returned Volume Server using the returned `fid`:

``` sh
curl -F file=@/tmp/seaweed-test.txt http://127.0.0.1:8080/3,03761b871b
```

Read it back:

``` sh
curl http://127.0.0.1:8080/3,03761b871b
```

The response should contain:

``` text
Hello SeaweedFS
```

Inspect the Volume directory:

``` sh
ls -lh /var/lib/seaweedfs/volume/
```

SeaweedFS stores objects as records inside volume data files rather than
creating one normal filesystem file per object. You will typically see
files such as `.dat`, `.idx`, and `.vif`.

## 6. Configure the Filer

Working directly with file IDs is useful for understanding SeaweedFS,
but most applications want filenames and directories. The Filer provides
that namespace.

For example:

``` text
/backups/database.sql
/users/alice/avatar.jpg
/videos/demo.mp4
```

Create the Filer systemd unit:

``` sh
nano /etc/systemd/system/seaweed-filer.service
```

Add:

``` ini
[Unit]
Description=SeaweedFS Filer Server
Documentation=https://github.com/seaweedfs/seaweedfs
After=network-online.target seaweed-master.service seaweed-volume.service
Wants=network-online.target
Requires=seaweed-master.service

[Service]
Type=simple
User=seaweedfs
Group=seaweedfs
WorkingDirectory=/var/lib/seaweedfs/filer

ExecStart=/usr/local/bin/weed filer -master=127.0.0.1:9333 -ip=127.0.0.1 -ip.bind=127.0.0.1 -port=8888 -defaultStoreDir=/var/lib/seaweedfs/filer

Restart=on-failure
RestartSec=5
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
```

Enable it:

``` sh
systemctl daemon-reload
systemctl enable --now seaweed-filer
```

Check the service:

``` sh
systemctl status seaweed-filer --no-pager -l
journalctl -u seaweed-filer -n 50 --no-pager
ss -lntp | grep weed
```

For a simple single-node installation, SeaweedFS can use its embedded
LevelDB2 metadata store. With the configuration above, it is created
below:

``` text
/var/lib/seaweedfs/filer/filerldb2
```

For larger production deployments, evaluate an external metadata backend
appropriate for your availability and operational requirements.

## 7. Test the Filer

Create a directory:

``` sh
curl -X POST http://127.0.0.1:8888/test/
```

Create a test object:

``` sh
echo "Hello from SeaweedFS Filer" > /tmp/filer-test.txt
```

Upload it through the Filer:

``` sh
curl -F file=@/tmp/filer-test.txt http://127.0.0.1:8888/test/hello.txt
```

Read it back using its normal path:

``` sh
curl http://127.0.0.1:8888/test/hello.txt
```

Expected output:

``` text
Hello from SeaweedFS Filer
```

Opening the directory endpoint in a browser displays SeaweedFS's basic
Filer web interface:

``` text
http://127.0.0.1:8888/test/
```

The Filer interface is useful for basic browsing, upload, rename, and
deletion. It should not be confused with a full administrative console
such as MinIO Console.

## 8. Access the Filer UI Safely with SSH Tunneling

Because the Filer is bound to localhost, it is not directly reachable
from another computer.

From your workstation, create an SSH tunnel:

``` sh
ssh -L 8888:127.0.0.1:8888 root@YOUR_SERVER_IP
```

Then open:

``` text
http://127.0.0.1:8888/
```

This is preferable to exposing port `8888` directly to the public
Internet.

## 9. Configure S3 Credentials

SeaweedFS can expose an S3-compatible endpoint backed by the Filer.

Generate a strong secret:

``` sh
openssl rand -hex 32
```

Create the S3 configuration:

``` sh
nano /etc/seaweedfs/s3.json
```

Example:

``` json
{
  "identities": [
    {
      "name": "seaweed-admin",
      "credentials": [
        {
          "accessKey": "seaweedadmin",
          "secretKey": "REPLACE_WITH_A_STRONG_RANDOM_SECRET"
        }
      ],
      "actions": [
        "Admin",
        "Read",
        "List",
        "Tagging",
        "Write"
      ]
    }
  ]
}
```

Protect the credential file:

``` sh
chown root:seaweedfs /etc/seaweedfs/s3.json
chmod 640 /etc/seaweedfs/s3.json
```

Verify:

``` sh
ls -l /etc/seaweedfs/s3.json
```

Do not publish the real access key or secret key in source control,
screenshots, shell history, or a blog post.

## 10. Configure the S3 Gateway

Create a systemd unit:

``` sh
nano /etc/systemd/system/seaweed-s3.service
```

Add:

``` ini
[Unit]
Description=SeaweedFS S3 Gateway
Documentation=https://github.com/seaweedfs/seaweedfs
After=network-online.target seaweed-filer.service
Wants=network-online.target
Requires=seaweed-filer.service

[Service]
Type=simple
User=seaweedfs
Group=seaweedfs

ExecStart=/usr/local/bin/weed s3 -filer=127.0.0.1:8888 -ip=127.0.0.1 -ip.bind=127.0.0.1 -port=8333 -config=/etc/seaweedfs/s3.json

Restart=on-failure
RestartSec=5
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
```

Start the gateway:

``` sh
systemctl daemon-reload
systemctl enable --now seaweed-s3
```

Check it:

``` sh
systemctl status seaweed-s3 --no-pager -l
journalctl -u seaweed-s3 -n 50 --no-pager
ss -lntp | grep weed
```

The S3 endpoint in this deployment is:

``` text
http://127.0.0.1:8333
```

## 11. Install AWS CLI v2 on Ubuntu

If `awscli` is not available from the enabled APT repositories, install
AWS CLI v2 using AWS's installer.

Install prerequisites:

``` sh
apt update
apt install -y curl unzip
```

Download and extract AWS CLI v2 for x86-64:

``` sh
cd /tmp
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip
unzip awscliv2.zip
./aws/install
```

Verify:

``` sh
aws --version
```

## 12. Test the S3-Compatible Endpoint

Set credentials in the current shell:

``` sh
export AWS_ACCESS_KEY_ID="seaweedadmin"
export AWS_SECRET_ACCESS_KEY="REPLACE_WITH_YOUR_SECRET"
export AWS_DEFAULT_REGION="us-east-1"
```

Create a bucket:

``` sh
aws --endpoint-url http://127.0.0.1:8333 s3 mb s3://test-bucket
```

List buckets:

``` sh
aws --endpoint-url http://127.0.0.1:8333 s3 ls
```

Create a test object:

``` sh
echo "Hello through the S3 API" > /tmp/s3-test.txt
```

Upload it:

``` sh
aws --endpoint-url http://127.0.0.1:8333 s3 cp /tmp/s3-test.txt s3://test-bucket/
```

List the bucket:

``` sh
aws --endpoint-url http://127.0.0.1:8333 s3 ls s3://test-bucket/
```

Download the object to standard output:

``` sh
aws --endpoint-url http://127.0.0.1:8333 s3 cp s3://test-bucket/s3-test.txt -
```

Expected output:

``` text
Hello through the S3 API
```

If bucket creation succeeds but `PutObject` returns `InternalError`, do
not treat the deployment as complete. Inspect both S3 and Filer logs
immediately:

``` sh
journalctl -u seaweed-s3 --since "5 minutes ago" --no-pager
journalctl -u seaweed-filer --since "5 minutes ago" --no-pager
journalctl -u seaweed-volume --since "5 minutes ago" --no-pager
```

Also confirm all storage components are healthy:

``` sh
systemctl --no-pager --type=service --state=running | grep seaweed
```

## 13. Verify All Services

A healthy single-node installation should show four active services:

``` sh
systemctl status seaweed-master --no-pager
systemctl status seaweed-volume --no-pager
systemctl status seaweed-filer --no-pager
systemctl status seaweed-s3 --no-pager
```

Check all relevant listeners:

``` sh
ss -lntp | grep weed
```

The expected local endpoints are:

  Component      HTTP                       gRPC
  ------------ ------ --------------------------
  Master         9333                      19333
  Volume         8080                      18080
  Filer          8888                      18888
  S3 Gateway     8333   Depends on configuration

## 14. Understanding Where Data Lives

It is useful to separate the three storage responsibilities.

The Master metadata is stored under:

``` text
/var/lib/seaweedfs/master
```

Actual object payloads are stored by the Volume Server under:

``` text
/var/lib/seaweedfs/volume
```

Filer namespace metadata is stored under:

``` text
/var/lib/seaweedfs/filer
```

For the embedded LevelDB2 store used in this tutorial, the metadata
database is typically:

``` text
/var/lib/seaweedfs/filer/filerldb2
```

This separation matters when designing backups. Backing up only the
Filer database does not back up the object payloads, and copying only
`.dat` files does not preserve the complete namespace and metadata
strategy.

## 15. Security Considerations

The configuration in this article deliberately binds the internal
services to `127.0.0.1`.

Do not casually expose these ports to the Internet:

``` text
9333   Master HTTP
19333  Master gRPC
8080   Volume HTTP
18080  Volume gRPC
8888   Filer HTTP
18888  Filer gRPC
```

For remote access, place an authenticated reverse proxy or private
network in front of the appropriate endpoint. For production S3 access,
use a DNS name and TLS rather than exposing a plain HTTP endpoint.

You should also consider:

-   TLS certificates for public endpoints
-   firewall allowlists
-   strong S3 credentials and least-privilege policies
-   JWT protection between SeaweedFS components where appropriate
-   mTLS for gRPC communication in higher-security environments
-   dedicated data disks
-   external Filer metadata storage for larger deployments
-   monitoring and alerting
-   backups and restore testing
-   multi-node replication and failure testing

## 16. Optional: Disable Telemetry

If your SeaweedFS release has telemetry enabled and you do not want to
send telemetry, review the available Master options:

``` sh
weed master -h
```

Where supported, add the following option to the Master command:

``` text
-telemetry=false
```

After changing the unit:

``` sh
systemctl daemon-reload
systemctl restart seaweed-master
```

## 17. Troubleshooting Commands

These commands cover most first-pass troubleshooting tasks.

Check service state:

``` sh
systemctl --no-pager --type=service | grep seaweed
```

Inspect Master logs:

``` sh
journalctl -u seaweed-master -n 100 --no-pager
```

Inspect Volume logs:

``` sh
journalctl -u seaweed-volume -n 100 --no-pager
```

Inspect Filer logs:

``` sh
journalctl -u seaweed-filer -n 100 --no-pager
```

Inspect S3 logs:

``` sh
journalctl -u seaweed-s3 -n 100 --no-pager
```

Check listeners:

``` sh
ss -lntp | grep weed
```

Check disk usage:

``` sh
df -h
du -sh /var/lib/seaweedfs/*
```

Check ownership:

``` sh
ls -lah /var/lib/seaweedfs
ls -lah /var/lib/seaweedfs/volume
ls -lah /var/lib/seaweedfs/filer
```

## SeaweedFS Web UI vs. MinIO Console

One common surprise is that SeaweedFS does not ship with a full
administrative dashboard comparable to MinIO Console.

The Filer provides a basic browser-based interface for files and
directories, but cluster administration, IAM, capacity visualization,
and observability are generally handled through APIs, CLI tools,
metrics, and external monitoring systems.

A common production observability stack is:

``` text
SeaweedFS metrics
       |
       v
  Prometheus
       |
       v
    Grafana
```

If a polished all-in-one storage administration console is a hard
requirement, evaluate that requirement separately when choosing between
object-storage platforms.

## Production Notes

The single-node design in this tutorial intentionally prioritizes
clarity.

Before using the deployment for critical data, consider moving from:

``` text
1 Master
1 Volume Server
1 Filer
1 local metadata database
```

to an architecture with multiple failure domains, replicated volumes,
highly available metadata, dedicated storage devices, monitoring, and
tested backup/restore procedures.

Also remember that SeaweedFS volume limits and the host filesystem's
free capacity are different concepts. Configure volume sizing and the
number of volume slots based on the actual disks available to the
server.

## Conclusion

At this point, the core SeaweedFS stack is installed natively on Ubuntu
and managed by systemd:

``` text
Master -> Volume Server -> Filer -> S3 Gateway
```

This setup is a useful foundation for learning how SeaweedFS separates
topology, object data, namespace metadata, and protocol gateways.

The next logical production steps are **TLS and reverse proxying,
monitoring with Prometheus/Grafana, multi-node replication, backup
strategy, and failure testing**.

