
# Installation

## Package Manager

```sh
sudo apt update
sudo apt install nginx
```



# Managment


``` bash
sudo systemctl status nginx
```


## Process
``` bash
ps aux | grep nginx
```


```text
root      2283 ... nginx: master process ...
www-data  2285 ... nginx: worker process
www-data  2286 ... nginx: worker process
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


Master Process با root اجرا شده. وظیفه اصلی‌اش مدیریت Nginx است: config را می‌خواند، workerها را ایجاد و مدیریت می‌کند و reload/shutdown را کنترل می‌کند.

اما معمولاً خود Master درخواست HTTP کاربران را پردازش نمی‌کند.

Worker Processها درخواست‌ها و connectionهای واقعی را پردازش می‌کنند. نکته امنیتی خوبی هم همین‌جا می‌بینی: workerهای تو root نیستند؛ با کاربر محدودتر www-data اجرا شده‌اند.

## Port & network

``` bash
sudo ss -lntp | grep nginx
```

```text
LISTEN 0      511          0.0.0.0:80        0.0.0.0:*    users:(("nginx",pid=2286,fd=5),("nginx",pid=2285,fd=5),("nginx",pid=2283,fd=5))
LISTEN 0      511             [::]:80           [::]:*    users:(("nginx",pid=2286,fd=6),("nginx",pid=2285,fd=6),("nginx",pid=2283,fd=6))
```

511 شماره پورت یا تعداد connectionهای فعلی نیست. این مقدار listen backlog است؛ یعنی kernel چه تعداد connection در صف listen می‌تواند نگه دارد.



```sh
nginx -t
```

```sh
systemctl reload nginx
```