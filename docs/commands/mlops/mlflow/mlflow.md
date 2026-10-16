
---
# Installation
<div style="height: 10px;"></div>


## Python
```sh
mkdir mlflow-project && cd mlflow-project

python3 -m venv venv
source venv/bin/activate
```

```sh
pip install mlflow
```
```sh
mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlartifacts
```



## Docker

```sh
mkdir mlflow && cd mlflow && mkdir -p data/mlartifacts
```
```sh
touch Dockerfile  docker-compose.yml
```
```sh
FROM python:3.11-slim
RUN pip install --no-cache-dir mlflow
WORKDIR /app
EXPOSE 5000
```

```sh
services:
  mlflow:
    build: .
    container_name: mlflow
    ports:
      - "127.0.0.1:5000:5000"
    volumes:
      - ./data:/app/data
    command: >
      mlflow server
      --host 0.0.0.0
      --port 5000
      --backend-store-uri sqlite:////app/data/mlflow.db
      --artifacts-destination /app/data/mlartifacts
      --allowed-hosts localhost,127.0.0.1
    restart: unless-stopped
```

```sh
docker compose up -d --build
```