
# Architecture


```text
                         ┌─────────────────┐
                         │     Master      │
                         │ config/signals  │
                         └────────┬────────┘
                                  │ fork
             ┌────────────────────┼────────────────────┐
             ▼                    ▼                    ▼
       ┌────────────┐       ┌────────────┐       ┌────────────┐
       │  Worker 1  │       │  Worker 2  │       │  Worker N  │
       │            │       │            │       │            │
       │ Event Loop │       │ Event Loop │       │ Event Loop │
       └─────┬──────┘       └────────────┘       └────────────┘
             │
             ├─ TCP accept
             ├─ TLS state machine
             ├─ HTTP parser
             ├─ phase engine
             ├─ location routing
             ├─ access control
             ├─ upstream state machine
             ├─ caching
             ├─ filters
             ├─ buffering
             └─ response writer
                    │
           ┌────────┴────────┐
           ▼                 ▼
       Static files       Upstream
                             │
                    ┌────────┼────────┐
                    ▼        ▼        ▼
                   app1     app2     app3

```


```text
$ ps aux | grep nginx

root      nginx: master process
nginx     nginx: worker process
nginx     nginx: worker process
nginx     nginx: worker process
nginx     nginx: worker process
```

## Master & Worker Process
### Master
The master process is primarily management/control infrastructure.
It handles things such as:

- validates configuration
- read configuration
- open/bind listening sockets
- create worker processes
- monitor workers
- reload config
- graceful shutdown
- restart/replace workers


### Worker
Each worker is event-driven engine
Instead of creating a new thread/process for every client, NGINX keeps a relatively small number of workers.
Each worker can manage many connections simultaneously.























---
# Command
```sh
sudo nginx -t
```

```sh
systemctl reload nginx
```

```sh
nginx -V
```

```sh
nginx -T 2>/dev/null | grep -E "listen|server_name|root"
```

---
# Cofigoration

## Config Files and Directories

### default
default config file
```sh
cat /etc/nginx/sites-available/default
```

## Context

## Directive

### server_name _;

### location

```sh
location / {
    try_files $uri $uri/ =404;
}
```



```sh
ln -s /etc/nginx/sites-available/prmctl.me /etc/nginx/sites-enabled/prmctl.me
```


























```text
             master
          PID: 2283
          user: root
              │
        ┌─────┴─────┐
        ▼           ▼
     worker       worker
    PID 2285      PID 2286
    www-data      www-data

```
