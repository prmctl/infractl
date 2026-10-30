

FRRouting is an open-source software suite for implementing routing protocols on operating systems such as Linux.

# Installation


## Install
```sh
sudo apt update
sudo apt install -y frr frr-pythontools
vtysh --version
sudo systemctl status frr
sudo systemctl enable --now frr
```

## IP Forwarding
```sh
sysctl net.ipv4.ip_forward
sudo sysctl -w net.ipv4.ip_forward=1
echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-routing.conf
sudo sysctl --system
```
## FRR Command  
```sh
sudo vtysh
show version
```

# Configoration

## ‌Basic Conf
Enter global configuration mode.
```sh
configure terminal
```
Set the router hostname to R1.
```sh
hostname R1
```
Exit configuration mode and return to privileged EXEC mode.
```sh
end
```
Save the current configuration.
```sh
write memory
```

## Config Scenario


### Static Route
If both networks are directly connected to R1, Linux automatically recognizes the connected routes through the IP addresses assigned to its interfaces, so there is no need to configure static routes.

```sh
configure terminal
ip route 192.168.30.0/24 10.0.12.2
end
write memory
```

### 






# Architecture

## Components

zebra: Manages communication between FRR and the operating system's routing table.
bgpd: Implements the BGP protocol.
ospfd: Implements the OSPF protocol for IPv4.
staticd: Manages static routes.
vtysh: Provides a unified command-line interface (CLI) for configuring and monitoring FRR.

‍‍‍```sh
                +----------------------+
                |    Network Admin     |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |        vtysh         |
                |  CLI Configuration   |
                +----------+-----------+
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
       +-----------+ +-----------+ +-----------+
       |   bgpd    | |   ospfd   | |  staticd  |
       |    BGP    | | OSPF IPv4 | |  Static   |
       |           | |           | |  Routes   |
       +-----+-----+ +-----+-----+ +-----+-----+
             |             |             |
             +-------------+-------------+
                           |
                           v
                +----------------------+
                |        zebra         |
                | Routing Management   |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |    Linux Kernel      |
                |    Routing Table     |
                |       (FIB)          |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |   Network Interfaces |
                |   Packet Forwarding  |
                +----------------------+


```