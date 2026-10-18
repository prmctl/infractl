
# Config


## Configoration


### Rate Limiting && Connection Limiting

rate limit config file
```sh
/etc/nginx/conf.d/rate-limits.conf

# General API Rate Limit
limit_req_zone $binary_remote_addr
    zone=api_limit:20m
    rate=20r/s;

# Authentication Rate Limit
limit_req_zone $binary_remote_addr
    zone=auth_limit:10m
    rate=5r/m;

# Search Rate Limit
limit_req_zone $binary_remote_addr
    zone=search_limit:10m
    rate=10r/s;

# Concurrent Connection Limit
limit_conn_zone $binary_remote_addr
    zone=conn_limit:10m;
```
must be load on nginx.conf
```sh
http {
    include /etc/nginx/mime.types;
    include /etc/nginx/conf.d/*.conf;
}
```
define rate limit 
```sh
upstream backend_api {

    server 127.0.0.1:3000;

    keepalive 32;
}

server {
    listen 80;
    server_name api.example.com;

    # Return HTTP 429 instead of 503
    limit_req_status 429;

    # Log rejected requests
    limit_req_log_level warn;

    # General API
    location /api/ {
        limit_req zone=api_limit burst=40 nodelay;
        limit_conn conn_limit 30;
        limit_req_dry_run on;
        proxy_pass http://backend_api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Authentication
    location = /login {
        limit_req zone=auth_limit burst=5 nodelay;
        proxy_pass http://backend_api;
        limit_req_dry_run on;
    }

    # Search
    location = /search {
        limit_req zone=search_limit burst=20 nodelay;
        limit_req_dry_run on;
        proxy_pass http://backend_api;
    }

    # Static files
    location /static/ {
        root /var/www;
        expires 7d;
        access_log off;
    }
}
```


### Hardening

#### fail2ban

```sh
sudo apt update
sudo apt install fail2ban
sudo vim /etc/fail2ban/filter.d/nginx-ratelimit.conf
```
```sh
[Definition]
failregex = ^<HOST> - .* ".*" 429 .*$
ignoreregex =
```

define jail
```sh
sudo vim /etc/fail2ban/jail.d/nginx-ratelimit.local
[nginx-ratelimit]
enabled = true
filter = nginx-ratelimit
logpath = /var/log/nginx/access.log
maxretry = 20
findtime = 60
bantime = 3600
port = http,https
action = nftables-multiport
```

test and activation
```sh
sudo fail2ban-regex /var/log/nginx/access.log /etc/fail2ban/filter.d/nginx-ratelimit.conf
sudo fail2ban-client status
sudo fail2ban-client status nginx-ratelimit
```
show band IPS
```sh
sudo fail2ban-client get nginx-ratelimit banip
```






## Tips

### Organising Nginx configuration

### Separate listen directives for 80 and 443 ports
- If you served HTTP and HTTPS with the exact same config (a single server that handles both HTTP and HTTPS requests) NGINX is intelligent enough to ignore the SSL directives if loaded over port 80.

- separate listen directives is certainly to help you maintain and modify your configuration. I always split the configuration if I want to redirect from HTTP to HTTPS (or www to non-www, and vice versa). For me, the right way is to define a separate server context in any such cases.

```sh
# For HTTP:
server {
  listen 10.240.20.2:80;
  # If you need redirect to HTTPS:
  return 301 https://example.com$request_uri;
}
# For HTTPS:
server {
  listen 10.240.20.2:443 ssl;
}
```


### Define the listen directives with address:port pair
```sh
# Server side:
server {
  # This block will be processed:
  listen 192.168.252.10; # --> 192.168.252.10:80
}
server {
  listen 80; # --> *:80 --> 0.0.0.0:80
  server_name api.random.com;
}
```



### Never use a hostname in a listen or upstream directives
- Generaly, uses of hostnames in a listen or upstream directives is a bad practice. In the worst case NGINX won't be able to bind to the desired TCP socket which will prevent NGINX from starting at all.
Uses of $hostname (the machine’s hostname) variable in the server_name directive is also example of bad practice (it's similar to use hostname label).
```sh
upstream bk_01 {
  server http://192.168.252.200:8080;
}
server {
  listen 10.10.100.20:80;
  location / {
    # It's OK, bk_01 is the internal name:
    proxy_pass http://bk_01;
  }
  location /api {
    proxy_pass http://192.168.253.10:80;
  }
}
```


### Use simple custom error pages
Default error pages in NGINX are simple but it reveals version information and returns the "nginx" string, which leads to information leakage vulnerability.

Create error page templates:
```sh
cat >> /usr/share/nginx/html/404.html << __EOF__
<html>
<head><title>404 Not Found</title></head>
<body>
<center><h1>404 Not Found</h1></center>
</body>
</html>
__EOF__

# Just an example, I know it is stupid...
cat >> /usr/share/nginx/html/50x.html << __EOF__
<html>
<head><title>server error</title></head>
<body>
<center><h1>server error</h1></center>
</body>
</html>
__EOF__
```
Set them on the NGINX side:
```sh
error_page 404 /404.html;
error_page 500 502 503 504 /50x.html;
location = /404.html {
  root /usr/share/nginx/html;
  internal;
}

location = /custom_50x.html {
  root /usr/share/nginx/html;
  internal;
}
```

### Configure log rotation policy
You should define a process which periodically archiving the current log file and starting a new one, renames and optionally compresses the current log files, delete old log files, and force the logging system to begin using new log files.

I think the best tool for this is a logrotate. I use it everywhere if I want to manage logs automatically, and for a good night's sleep also. It is a simple program to rotate logs, uses crontab to work. It's scheduled work, not a daemon, so no need to reload its configuration.

for manually rotation:
```sh
# Check manually (all log files):
logrotate -dv /etc/logrotate.conf

# Check manually with force rotation (specific log file):
logrotate -dv --force /etc/logrotate.d/nginx
```

for automate rotation:
```sh
# GNU/Linux distributions:
cat > /etc/logrotate.d/nginx << __EOF__
/var/log/nginx/*.log {
  daily
  missingok
  rotate 14
  compress
  delaycompress
  notifempty
  create 0640 nginx nginx
  sharedscripts
  prerotate
    if [ -d /etc/logrotate.d/httpd-prerotate ]; then \
      run-parts /etc/logrotate.d/httpd-prerotate; \
    fi \
  endscript
  postrotate
    # test ! -f /var/run/nginx.pid || kill -USR1 `cat /var/run/nginx.pid`
    invoke-rc.d nginx reload >/dev/null 2>&1
  endscript
}

/var/log/nginx/localhost/*.log {
  daily
  missingok
  rotate 14
  compress
  delaycompress
  notifempty
  create 0640 nginx nginx
  sharedscripts
  prerotate
    if [ -d /etc/logrotate.d/httpd-prerotate ]; then \
      run-parts /etc/logrotate.d/httpd-prerotate; \
    fi \
  endscript
  postrotate
    # test ! -f /var/run/nginx.pid || kill -USR1 `cat /var/run/nginx.pid`
    invoke-rc.d nginx reload >/dev/null 2>&1
  endscript
}

/var/log/nginx/domains/example.com/*.log {
  daily
  missingok
  rotate 14
  compress
  delaycompress
  notifempty
  create 0640 nginx nginx
  sharedscripts
  prerotate
    if [ -d /etc/logrotate.d/httpd-prerotate ]; then \
      run-parts /etc/logrotate.d/httpd-prerotate; \
    fi \
  endscript
  postrotate
    # test ! -f /var/run/nginx.pid || kill -USR1 `cat /var/run/nginx.pid`
    invoke-rc.d nginx reload >/dev/null 2>&1
  endscript
}
__EOF__
```


### Don't duplicate index directive, use it only in the http block
- Use the index directive one time. It only needs to occur in your http context and it will be inherited below.

```sh
http {
  index index.php index.htm index.html index.$geo.html;
  server {
    server_name www.example.com;
    location / {
    }
  }

  server {
    server_name www.example.com;
    location / {
    }
    location /data {
    }
}
```

## Hardening

### Run as an unprivileged user

```sh
# Edit/check nginx.conf:
user nginx;   # or 'www' for example; if group is omitted,
              # a group whose name equals that of user is used
# Check/set owner and group for root directory:
chown -R root:root /etc/nginx
# Set owner and group for app directory:
chown -R nginx:nginx /var/www/example.com
```

### Disable unnecessary modules
- It is recommended to disable any modules which are not required as this will minimise the risk of any potential attacks by limiting the operations allowed by the web server. I also recommend only compiling and running signed and tested modules on you production environments.

- Disable unneeded modules in order to reduce the memory utilized and improve performance. Modules that are not needed just make loading times longer.

- The best way to unload unused modules is use the configure option during installation. If you have static linking a shared module you should re-compile NGINX.

```sh
# 1a) Check which modules can be turn on or off while compiling:
./configure --help | less

# 1b) Turn off during installation:
./configure --without-http_autoindex_module

# 2) Comment modules in the configuration file e.g. modules.conf:
# load_module   /usr/share/nginx/modules/ndk_http_module.so;
# load_module   /usr/share/nginx/modules/ngx_http_auth_pam_module.so;
# load_module   /usr/share/nginx/modules/ngx_http_cache_purge_module.so;
# load_module   /usr/share/nginx/modules/ngx_http_dav_ext_module.so;
load_module     /usr/share/nginx/modules/ngx_http_echo_module.so;
# load_module   /usr/share/nginx/modules/ngx_http_fancyindex_module.so;
load_module     /usr/share/nginx/modules/ngx_http_geoip_module.so;
load_module     /usr/share/nginx/modules/ngx_http_headers_more_filter_module.so;
# load_module   /usr/share/nginx/modules/ngx_http_image_filter_module.so;
# load_module   /usr/share/nginx/modules/ngx_http_lua_module.so;
load_module     /usr/share/nginx/modules/ngx_http_perl_module.so;
# load_module   /usr/share/nginx/modules/ngx_mail_module.so;
# load_module   /usr/share/nginx/modules/ngx_nchan_module.so;
# load_module   /usr/share/nginx/modules/ngx_stream_module.so;
```


### Protect sensitive resources
Sensitive resources contains items that abusers can use to fully recreate the source code used by the site and look for bugs, vulnerabilities, and exposed passwords.





# TODO

[] Logging
[] Compression
[] Security
[] Timeouts
[] Rate Limiting
[] Virtual Hosts
[] Buffers
[] SSL/TLS
[] Real IP




