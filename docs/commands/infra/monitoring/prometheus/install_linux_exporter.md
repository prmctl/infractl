# Runbook: Prometheus Node Exporter Installation

## Overview

Install and configure Prometheus Node Exporter on Linux to expose system metrics (CPU, memory, disk, network) to Prometheus.

- **OS:** Ubuntu / Debian
- **Default Port:** `9100/TCP`
- **Metrics Endpoint:** `http://SERVER_IP:9100/metrics`
- **Service Manager:** systemd

> Choose **one** installation method. Do not install both on the same server.

---

## Method 1: Install via APT

### 1. Update Packages

```bash
sudo apt update
```

### 2. Check Available Version

```bash
apt-cache policy prometheus-node-exporter
```

### 3. Install Node Exporter

```bash
sudo apt install -y prometheus-node-exporter
```

### 4. Enable and Start Service

```bash
sudo systemctl enable --now prometheus-node-exporter
```

### 5. Verify Installation

```bash
sudo systemctl status prometheus-node-exporter
sudo ss -tulnp | grep 9100
curl -fsS http://localhost:9100/metrics | head
```

### 6. Check Logs

```bash
sudo journalctl -u prometheus-node-exporter -n 50 --no-pager
```

---

## Method 2: Manual Installation (GitHub Binary)

### 1. Set Version and Architecture

```bash
VERSION="1.9.1"
ARCH="amd64"
cd /tmp
```

### 2. Download Binary

```bash
wget "https://github.com/prometheus/node_exporter/releases/download/v${VERSION}/node_exporter-${VERSION}.linux-${ARCH}.tar.gz"
```

> Use the appropriate architecture (`amd64` or `arm64`). Verify the download checksum against the official release before installing. Do not bypass TLS certificate validation.

### 3. Extract and Install

```bash
tar -xzf "node_exporter-${VERSION}.linux-${ARCH}.tar.gz"

sudo install -o root -g root -m 0755 \
  "node_exporter-${VERSION}.linux-${ARCH}/node_exporter" \
  /usr/local/bin/node_exporter
```

### 4. Create Service User

```bash
sudo useradd --system --no-create-home \
  --shell /usr/sbin/nologin node_exporter
```

### 5. Create systemd Service

```bash
sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<'EOF'
[Unit]
Description=Prometheus Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=node_exporter
Group=node_exporter
ExecStart=/usr/local/bin/node_exporter
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

### 6. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now node_exporter
```

### 7. Verify Installation

```bash
/usr/local/bin/node_exporter --version
sudo systemctl status node_exporter
sudo ss -tulnp | grep 9100
curl -fsS http://localhost:9100/metrics | head
```

### 8. Check Logs

```bash
sudo journalctl -u node_exporter -n 50 --no-pager
```

---

## Prometheus Configuration

### 1. Edit Prometheus Configuration

On the Prometheus server:

```bash
sudo nano /etc/prometheus/prometheus.yml
```

### 2. Add Scrape Target

Add the following job under the existing `scrape_configs` section:

```yaml
  - job_name: "node_exporter"
    scrape_interval: 15s
    static_configs:
      - targets:
          - "NODE_EXPORTER_IP:9100"
```

Replace `NODE_EXPORTER_IP` with the target server's IP address.

### 3. Validate and Restart Prometheus

```bash
promtool check config /etc/prometheus/prometheus.yml
sudo systemctl restart prometheus
```

> Commands assume a systemd-based Prometheus installation.

### 4. Verify Target

Open:

```text
http://PROMETHEUS_IP:9090/targets
```

Expected status: **UP**

Verify using PromQL:

```promql
up{job="node_exporter"}
```

Expected result: `1`

---

## Firewall Configuration

Allow inbound traffic on port `9100` from the Prometheus server only.

For UFW:

```bash
sudo ufw allow from PROMETHEUS_IP to any port 9100 proto tcp
```

Replace `PROMETHEUS_IP` with the actual Prometheus server IP.

---

## Service Management

| Action | APT Installation | Manual Installation |
|---|---|---|
| Start | `systemctl start prometheus-node-exporter` | `systemctl start node_exporter` |
| Stop | `systemctl stop prometheus-node-exporter` | `systemctl stop node_exporter` |
| Restart | `systemctl restart prometheus-node-exporter` | `systemctl restart node_exporter` |
| Status | `systemctl status prometheus-node-exporter` | `systemctl status node_exporter` |
| Logs | `journalctl -u prometheus-node-exporter -f` | `journalctl -u node_exporter -f` |

Use `sudo` for service management commands.

---

## Troubleshooting

| Issue | Check / Resolution |
|---|---|
| Service not running | `sudo journalctl -u node_exporter -n 50` |
| Port 9100 unavailable | `sudo ss -tulnp \| grep 9100` |
| Prometheus target DOWN | Verify IP, firewall, service status and connectivity |
| Metrics endpoint unreachable | `curl -v http://NODE_EXPORTER_IP:9100/metrics` |
| GitHub SSL certificate error | Check proxy, TLS inspection and CA trust; do not disable certificate verification |
| Port already in use | Check for an existing Node Exporter instance |

---

## Rollback / Uninstall

### APT Installation

```bash
sudo systemctl disable --now prometheus-node-exporter
sudo apt purge -y prometheus-node-exporter
```

### Manual Installation

```bash
sudo systemctl disable --now node_exporter
sudo rm -f /etc/systemd/system/node_exporter.service
sudo systemctl daemon-reload
sudo rm -f /usr/local/bin/node_exporter
sudo userdel node_exporter
```

Remove the corresponding scrape target from Prometheus configuration and reload or restart Prometheus.

---

## Acceptance Criteria

- [ ] Node Exporter service is `active (running)`.
- [ ] Port `9100/TCP` is listening.
- [ ] `/metrics` endpoint returns HTTP 200.
- [ ] Prometheus target status is `UP`.
- [ ] `up{job="node_exporter"}` returns `1`.
- [ ] Firewall permits access only from authorized monitoring hosts.