
# Airflow Architecture
<div style="height: 10px;"></div>



---
# Installation
<div style="height: 10px;"></div>









## Docker
```sh
mkdir airflow-project && cd airflow-project && mkdir -p dags logs plugins config
```
```sh
curl -LfO https://airflow.apache.org/docs/apache-airflow/3.1.0/docker-compose.yaml
```
```sh
echo "AIRFLOW_UID=$(id -u)" > .env
```
```sh
docker compose up airflow-init
```
```sh
docker compose up -d
```