

```sh
sudo apt update
sudo apt install nginx
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




```text
user www-data;
worker_processes auto;

events {
    worker_connections 768;
}

http {

    include /etc/nginx/mime.types;

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```