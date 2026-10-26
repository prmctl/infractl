


All ports list
```sh
/etc/services
```

Interface Type

| Interface Name | Type | Description |
|---|---|---|
| `eth0`, `eth1` | Ethernet | Ethernet interfaces using legacy naming conventions |
| `enp3s0` | Ethernet | Ethernet interface named based on its PCI bus location |
| `ens33`, `ens160` | Ethernet | Ethernet interfaces named based on their slot numbers |
| `eno1`, `eno2` | Ethernet | Onboard Ethernet interfaces |
| `enx...` | Ethernet | Ethernet interface named based on its MAC address |
| `wlan0` | Wireless | Wireless interface using legacy naming conventions |
| `wlp2s0` | Wireless | Wireless interface using predictable naming conventions |
| `wlx...` | Wireless | Wireless interface named based on its MAC address |
| `wwan0` | Mobile | Mobile broadband interface for 4G/5G connectivity |
| `lo` | Loopback | Loopback interface for internal system communication |
| `tun0` | Virtual Tunnel | Layer 3 VPN tunnel interface |
| `tap0` | Virtual Tunnel | Layer 2 VPN or virtual Ethernet tunnel interface |
| `wg0` | WireGuard | VPN interface used by WireGuard |
| `ppp0` | Point-to-Point | Interface used for PPP and PPPoE connections |
| `docker0` | Bridge | Default Docker bridge network interface |
| `br0` | Bridge | Network bridge connecting multiple interfaces |
| `virbr0` | Virtual Bridge | Virtual network bridge used by libvirt/KVM |
| `veth...` | Virtual Ethernet | Virtual Ethernet interface connecting containers to the host |
| `bond0` | Bonding | Combines multiple network interfaces into a single logical interface |
| `team0` | Teaming | Aggregates multiple network interfaces for redundancy or performance |
| `vlan100` | VLAN | Virtual LAN interface with VLAN ID 100 |
| `eth0.100` | VLAN | VLAN interface with ID 100 configured on `eth0` |
| `macvlan0` | MACVLAN | Virtual network interface with its own MAC address |
| `ipvlan0` | IPVLAN | IP-based virtual network interface |
| `vxlan100` | VXLAN | Virtual Extensible LAN interface for overlay networking |
| `gre0` | GRE Tunnel | Layer 3 network tunnel using GRE encapsulation |
| `gretap0` | GRETAP | Layer 2 Ethernet tunnel over GRE |
| `sit0` | SIT Tunnel | Tunnel interface for transporting IPv6 traffic over IPv4 |
| `ip6tnl0` | IPv6 Tunnel | Network tunnel interface using IPv6 encapsulation |
| `dummy0` | Dummy | Virtual network interface used for testing and configuration |
| `ifb0` | IFB | Intermediate Functional Block interface for ingress traffic shaping |
| `tailscale0` | VPN | Virtual network interface used by Tailscale |
| `zt...` | Overlay VPN | Virtual network interface used by ZeroTier |
