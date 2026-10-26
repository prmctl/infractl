
# iproute2

## ip      
IP, Interface, Routing, ARP

ip command structure
```sh
ip [OPTIONS] OBJECT COMMAND
```

### Interface Management

### IP Address Management

show all ip address for all interfaces
```sh
ip addr show
ip a
ip -br addr
```

show ip adress for a interface
```sh
ip addr show dev enp3s0
```

add ip adress to a interface
```sh
sudo ip addr add 192.168.1.50/24 dev enp3s0
```

delete ip adress of a interface
```sh
sudo ip addr del 192.168.1.50/24 dev enp3s0
```

replace ip adress of a interface
```sh
sudo ip addr replace 192.168.1.50/24 dev enp3s0
```

delete all ip adresss of a interface
```sh
sudo ip -4 addr flush dev enp3s0
```

### Routing Table Management
### Layer 2 Management
### Policy-Based Routing Management
### Network Namespace Management
### Network Monitoring



## ss (Socket Statistics)
used to inspect network sockets and connections.
use for:
- Identify which ports are open on the system.
- Determine which process is using a specific port.
- View established TCP connections.
- Check which services are in the `LISTEN` state.
- Inspect socket queues, timers, and internal TCP information.

```sh
ss [OPTIONS] [FILTER]
```

Display Listening TCP and UDP Ports
```sh
sudo ss -tulnp
```

Display Services Listening on Port 80
```sh
sudo ss -ltnp 'sport = :80'
```

```sh
ss -tn state established
```

## bridge

## tc      
Traffic Control
## bridge  
Ethernet Bridge Management
## rtmon   
Route Monitoring
## nstat   
Network Statistics
## lnstat  
Linux Network Statistics


---
# dnsutils
## dig
## nslookup
## nsupdate


---
# Packet Analysis
## tcpdump
## tcpflow
## tshark

---
# Network Diagnostics
## ping
## traceroute
## mtr
## ethtool

---
# net-tools
## arp


# Network Testing
## iperf3
## nc
## socat


---
# Network Scanning
## nmap
## nping