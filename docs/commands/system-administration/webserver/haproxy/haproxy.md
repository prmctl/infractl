
# Configoration

## global
process-level settings go here . The global section appears at the top of your configuration file. It defines process-level directives such as 
- the maximum number of connections to accept.
- where to store logs. 
- which user and group the process should run under.

```sh
global
  maxconn 60000
  log 127.0.0.1 local0
  log 127.0.0.1 local1 notice
  user  haproxy
  group haproxy
  chroot /var/empty
```



## defaults
A defaults section stores common settings inherited by the frontend and backend sections that follow it. It can also condense long configurations by reducing duplicated lines.

```sh
defaults
  mode http
  balance roundrobin

# Inherits mode
frontend website
  bind :80
  default_backend web_servers

# Inherits mode and balance
backend web_servers
  server s1 192.168.1.25:80
  server s2 192.168.1.26:80

# Overrides mode
frontend mysql
  mode tcp
  bind :3306
  default_backend mysql_servers

# Overrides mode and balance
backend mysql_servers
  mode tcp
  balance leastconn
  server db1 192.168.1.29:3306
  server db2 192.168.1.30:3306
```

```sh
defaults http_defaults
  mode http

defaults tcp_defaults
  mode tcp

# Inherits from http_defaults
frontend website from http_defaults
  bind :80
  default_backend web_servers

# Inherits from tcp_defaults
frontend mysql from tcp_defaults
  mode tcp
  bind :3306
  default_backend mysql_servers
```



## frontend listener
A frontend that accepts requests from clients
A frontend section defines the IP addresses and ports that clients can connect to.

```sh
frontend myfrontend
  # Set the proxy mode to http (layer 7) or tcp (layer 4)
  mode http
  # Receive HTTP traffic on all IP addresses assigned to the server at port 80
  bind :80
  # Choose the default pool of backend servers
  default_backend web_servers
```

### Traffic mode
A frontend section’s mode should match the mode of the backend section it sends traffic to. A mismatch will cause the configuration to not work.
```sh
frontend foo.com
  mode http
  bind 192.168.1.5:80
  default_backend foo_servers

frontend db.foo.com
  mode tcp
  bind 192.168.1.15:3306
  default_backend db_servers
```


### Conditionals forward
can choose a different backend with the use_backend directive followed by a conditional statement. These conditionals are called ACLs.
```sh
frontend foo_and_bar
  mode http
  bind :80
  use_backend foo_servers if { req.hdr(host) -i foo.com }
  default_backend bar_servers
```


## Backend
A backend section defines a pool of servers to which the load balancer will route requests.

```sh
frontend myfrontend
  mode http
  bind :80
  default_backend web_servers

backend web_servers
  mode http
  balance roundrobin
  server myfirstserver  192.168.1.25:80 check
  server mysecondserver 192.168.1.26:80 check
  server mythirdserver  192.168.1.27:80 check
```
### LB Algorithms

#### leastconn
the server with the lowest number of connections receives the connection (request). Use this algorithm when you expect long-lived connections, such as for SQL databases, gRPC streams, LDAP, and other protocols that keep connections open for an extended period of time. This algorithm is not well suited for protocols that have short sessions, such as HTTP. It takes server weights and queued connections into account as well when choosing the best server.

#### roundrobin
The roundrobin load balancing algorithm sends each new request to the next available server in the pool. By cycling through servers in order, it helps ensure that traffic is distributed evenly across all servers in the backend

#### random
It selects a server without having to analyze all servers, and since it will choose the least loaded of two randomly-chosen servers, it won’t select the most-loaded servers.

#### first
This algorithm will choose the first server in the list with open connection slots and send connections to it until it can’t receive any more connections.You must use the maxconn directive with this algorithm to establish the maximum number of connections for each server:
```sh
backend web_servers
  mode http
  balance first
  server s1 192.168.1.25:80 check maxconn 100
  server s2 192.168.1.26:80 check maxconn 100
  server s3 192.168.1.27:80 check maxconn 100
```

#### hash
Use hash-based algorithms when you need to maintain affinity, or requests from the same client should reach the same server.

```sh
backend web_servers {0-1}
  balance hash src,ipmask(24)
  server app1 10.0.0.1:8080 check
  server app2 10.0.0.2:8080 check
  server app3 10.0.0.3:8080 check
```

### Health Checks
Adding the check argument to each server line is a good practice; this enables health checking to remove unhealthy servers that don’t respond to a TCP connection from the load balancing rotation.

## Listens



# Custome Rule


## ACLs
We can use ACLs in many scenarios, including routing traffic, blocking traffic, and transforming messages. An ACL has no effect on your configuration until you reference it with an if or unless conditional statement on another line.



## Client IP preservation




# Protocol support

