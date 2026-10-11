window.INFRACTL_NAV = [
  {
    "label": "Getting Started",
    "href": "",
    "icon": "tools",
    "color": "cyan"
  },
  {
    "group": "Templates · Reusable Configs",
    "items": [
      {
        "label": "Overview",
        "href": "templates/",
        "icon": "template",
        "color": "green"
      },
      {
        "label": "Databases",
        "href": "templates/databases/",
        "icon": "db",
        "color": "green"
      },
      {
        "label": "Kubernetes",
        "href": "templates/kubernetes/",
        "icon": "k8s",
        "color": "green"
      },
      {
        "label": "Linux System",
        "href": "templates/linux-system/",
        "icon": "terminal",
        "color": "green"
      },
      {
        "label": "Web Servers",
        "href": "templates/web-servers/",
        "icon": "server",
        "color": "green",
        "children": [
          {
            "label": "Nginx Reverse Proxy",
            "href": "templates/web-servers/nginx/",
            "icon": "note",
            "color": "green"
          }
        ]
      }
    ]
  },
  {
    "group": "Laboratories · Hands-on",
    "items": [
      {
        "label": "Overview",
        "href": "lab/",
        "icon": "labs",
        "color": "blue"
      },
      {
        "label": "Databases",
        "href": "lab/databases/",
        "icon": "db",
        "color": "blue"
      },
      {
        "label": "DNS",
        "href": "lab/dns/",
        "icon": "dns",
        "color": "blue",
        "children": [
          {
            "label": "DNS Resolution Failure",
            "href": "lab/dns/resolution-failure/",
            "icon": "note",
            "color": "blue"
          }
        ]
      },
      {
        "label": "Kubernetes",
        "href": "lab/kubernetes/",
        "icon": "k8s",
        "color": "blue"
      },
      {
        "label": "System",
        "href": "lab/system/",
        "icon": "terminal",
        "color": "blue"
      },
      {
        "label": "Web Servers",
        "href": "lab/web-servers/",
        "icon": "server",
        "color": "blue"
      }
    ]
  },
  {
    "group": "Common Commands · Quick Reference",
    "items": [
      {
        "label": "Overview",
        "href": "commands/",
        "icon": "tools",
        "color": "cyan"
      },
      {
        "label": "Databases",
        "href": "commands/databases/",
        "icon": "db",
        "color": "cyan"
      },
      {
        "label": "DNS",
        "href": "commands/dns/",
        "icon": "dns",
        "color": "cyan",
        "children": [
          {
            "label": "BIND9 Primary / Secondary",
            "href": "commands/dns/bind9/",
            "icon": "note",
            "color": "cyan"
          },
          {
            "label": "CoreDNS",
            "href": "commands/dns/coredns/",
            "icon": "note",
            "color": "cyan"
          },
          {
            "label": "Unbound",
            "href": "commands/dns/unbound/",
            "icon": "note",
            "color": "cyan"
          }
        ]
      },
      {
        "label": "Kubernetes",
        "href": "commands/kubernetes/",
        "icon": "k8s",
        "color": "cyan"
      },
      {
        "label": "Linux",
        "href": "commands/linux/",
        "icon": "tools",
        "color": "cyan",
        "children": [
          {
            "label": "Certbot — Important Commands Cheat Sheet",
            "href": "commands/linux/certbot/",
            "icon": "note",
            "color": "cyan"
          },
          {
            "label": "DNS",
            "href": "commands/linux/dns/",
            "icon": "dns",
            "color": "cyan"
          },
          {
            "label": "File System",
            "href": "commands/linux/file_system/",
            "icon": "note",
            "color": "cyan"
          },
          {
            "label": "Linux Kernel",
            "href": "commands/linux/kernel/",
            "icon": "note",
            "color": "cyan"
          },
          {
            "label": "Nework",
            "href": "commands/linux/nework/",
            "icon": "note",
            "color": "cyan"
          },
          {
            "label": "Open Vpn",
            "href": "commands/linux/open-vpn/",
            "icon": "note",
            "color": "cyan"
          },
          {
            "label": "SSH",
            "href": "commands/linux/ssh/",
            "icon": "note",
            "color": "cyan"
          },
          {
            "label": "OpenSSL",
            "href": "commands/linux/ssl/",
            "icon": "note",
            "color": "cyan"
          },
          {
            "label": "Systemd",
            "href": "commands/linux/systemd/",
            "icon": "note",
            "color": "cyan"
          }
        ]
      },
      {
        "label": "Networking",
        "href": "commands/networking/",
        "icon": "net",
        "color": "cyan"
      },
      {
        "label": "Observability",
        "href": "commands/observability/",
        "icon": "observe",
        "color": "cyan",
        "children": [
          {
            "label": "Runbook: Prometheus Node Exporter Installation",
            "href": "commands/observability/prometheus-install/",
            "icon": "note",
            "color": "cyan"
          }
        ]
      },
      {
        "label": "Security",
        "href": "commands/security/",
        "icon": "security",
        "color": "cyan"
      },
      {
        "label": "Storage",
        "href": "commands/storage/",
        "icon": "storage",
        "color": "cyan",
        "children": [
          {
            "label": "Seaweedfs",
            "href": "commands/storage/seaweedfs/",
            "icon": "tools",
            "color": "cyan",
            "children": [
              {
                "label": "Architecture",
                "href": "commands/storage/seaweedfs/architecture/",
                "icon": "note",
                "color": "cyan"
              },
              {
                "label": "Installation Guide",
                "href": "commands/storage/seaweedfs/installation-guide/",
                "icon": "note",
                "color": "cyan"
              }
            ]
          }
        ]
      },
      {
        "label": "Web Servers",
        "href": "commands/web-servers/",
        "icon": "server",
        "color": "cyan",
        "children": [
          {
            "label": "Nginx",
            "href": "commands/web-servers/nginx/",
            "icon": "tools",
            "color": "cyan",
            "children": [
              {
                "label": "Architecture",
                "href": "commands/web-servers/nginx/architecture/",
                "icon": "note",
                "color": "cyan"
              },
              {
                "label": "Architecture",
                "href": "commands/web-servers/nginx/nginx/",
                "icon": "note",
                "color": "cyan"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    "group": "Field Notes · Experience",
    "items": [
      {
        "label": "Latest Posts",
        "href": "field-notes/",
        "icon": "note",
        "color": "purple"
      }
    ]
  },
  {
    "group": "Tools · Utilities",
    "items": [
      {
        "label": "Overview",
        "href": "tools/",
        "icon": "tools",
        "color": "cyan"
      }
    ]
  }
];
