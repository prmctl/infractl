


‍‍```text
html - for default static files, e.g. global 5xx error page
master - for main configuration, e.g. acls, listen directives, and domains
_acls - for access control lists, e.g. geo or map modules
_basic - for rate limiting rules, redirect maps, or proxy params
_listen - for all listen directives; also stores SSL configuration
_server - for domains configuration; also stores all backends definitions
modules - for modules which are dynamically loading into NGINX
snippets - for NGINX aliases, configuration templates

```



# Reverse Proxy


```sh
server {

  location /app/ {
    # backend layer: OpenResty as a front for app
    proxy_pass http://192.168.154.102:80;

  }

  location /app/v3 {
    # backend layer: uWSGI Python app
    uwsgi_pass 192.168.154.102:8080;
  }

  location /app/v4 {
    # backend layer: php-fpm app
    fastcgi_pass 192.168.154.102:8081;
  }
}

```

```text
You should always use proxy_pass only for HTTP servers working on the backend layer (set also the http:// protocol before referencing the HTTP backend) and other *_pass directives only for non-HTTP backend servers (like a uWSGI or FastCGI).

Directives such as uwsgi_pass, fastcgi_pass, or scgi_pass are designed specifically for non-HTTP apps and you should use them instead of the proxy_pass (non-HTTP talking).
```


# Load Balancing
```sh
upstream backend {

  server bk01_node:80 max_fails=3 fail_timeout=5s;
  server bk02_node:80 max_fails=3 fail_timeout=5s;
  server bk01_node:80 max_fails=3 fail_timeout=5s down;  
}
```

```text
Sometimes we need to turn off backends e.g. at maintenance-time. I think good solution is marks the server as permanently unavailable with down parameter even if the downtime takes a short time.

It's also important if you use IP Hash load balancing technique. If one of the servers needs to be temporarily removed, it should be marked with this parameter in order to preserve the current hashing of client IP addresses.
```
