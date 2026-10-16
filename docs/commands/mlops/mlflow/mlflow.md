# Airflow Architecture
<div style="height: 10px;"></div>


## Life Cycle

### 1. DAG Definition
Component: Developer
- A developer creates a Python file defining a DAG.
- The DAG contains tasks, dependencies, schedules, and execution configurations.
- The DAG file is placed in a location accessible to the DAG Processor.
Example:
```text
extract >> transform >> load
```

### 2. DAG Discovery & Parsing
Component: DAG Processor
- Discovers new or modified DAG files.
- Parses Python files to identify DAGs, tasks, and dependencies.
- Validates DAG definitions.
- Serializes DAG information and stores it in the Metadata Database.
- Makes DAG definitions available to the Scheduler and UI.
Note: Task logic is not executed during parsing, but top-level Python code may run.

### 3. DAG Run Creation
Component: Scheduler
- Evaluates DAG schedules and trigger conditions.
- Creates a new DAG Run when a workflow is due.
- Each DAG Run represents one execution of the entire DAG.
- Assigns a unique Run ID and tracks its execution state.
Common DAG Run States:
queued → running → success / failed

DAG Runs can also be created through manual or API triggers.

### 4. Task Dependency Evaluation
Component: Scheduler
- Identifies Task Instances belonging to the DAG Run.
- Evaluates upstream dependencies and Trigger Rules.
- Checks execution constraints such as Pools, concurrency limits, and available capacity.
- Marks eligible Task Instances as scheduled.
Example:

```text
extract (success)
       ↓
transform (scheduled)
       ↓
load (none)
```

### 5. Task Queuing
Components: Scheduler + Executor
- The Scheduler selects eligible Task Instances for execution.
- Marks selected Task Instances as queued.
- Submits them to the configured Executor.
- The Executor manages task dispatch according to its implementation.
Execution methods:
Executor	Dispatch Mechanism
LocalExecutor	Local processes
CeleryExecutor	Message broker (Redis/RabbitMQ)
KubernetesExecutor	Kubernetes API (Pod creation)

Note: The queued state does not necessarily mean a task is stored in an external message queue.

### 6. Task Execution
Component: Worker / Task Runtime
- The execution environment starts the Task Instance.
- The Task Instance transitions to running.
- Executes the actual task logic, such as Python code, shell commands, SQL queries, or API requests.
- Produces logs and may exchange data through XCom.
- In Airflow 3, the Task Runtime communicates with Airflow services through the Task Execution API.
Execution environments:
Executor	Execution Environment
LocalExecutor	Local worker processes
CeleryExecutor	Celery Workers
KubernetesExecutor	Kubernetes Pods


### 7. Task Completion & State Update
Components: Task Runtime + API Server + Scheduler
- The Task Runtime reports execution results.
- Airflow persists task states and relevant metadata in the Metadata Database.
- Successful tasks transition to success.
- Failed tasks may transition to up_for_retry if retries remain.
- The Scheduler evaluates completed tasks and schedules eligible downstream tasks.
Typical Task State Lifecycle:

```text
none
  ↓
scheduled
  ↓
queued
  ↓
running
  ├── success
  ├── failed
  └── up_for_retry → scheduled → queued → running
```

Other possible states include skipped, deferred, and upstream_failed.

### 8. DAG Run Completion
Component: Scheduler
- Evaluates the states of the DAG's leaf tasks (tasks without downstream dependencies).
- Marks the DAG Run as success when all leaf tasks are success or skipped.
- Marks the DAG Run as failed if any leaf task is failed or upstream_failed.
- Records the final execution state and completion time.
Note: Trigger Rules can cause a DAG Run to succeed even if an intermediate task failed.


### 9. Monitoring & Logging
Components: API Server + Metadata Database + Log Storage
- The Airflow UI displays DAG Runs, Task Instances, execution states, and logs.
- Task logs are stored locally or in remote storage such as S3.
- Users can monitor executions, inspect failures, and retry or clear tasks.
Monitoring occurs throughout the entire lifecycle, not only after execution.


## Key Concepts

### DAG (Directed Acyclic Graph)
- A DAG represents a workflow consisting of multiple tasks and their dependencies.
- Defines what tasks should run, in what order, and on what schedule.
- Directed means tasks have a defined execution direction.
- Acyclic means tasks cannot form circular dependencies.
- A DAG can be executed multiple times, creating separate DAG Runs.
Example:
```text
extract_data → transform_data → train_model → evaluate_model
```

### Task
- A Task is the smallest unit of work managed by Airflow.
- Represents a specific operation within a DAG.
- Can execute Python functions, shell commands, SQL queries, API requests, or containerized applications.
- Tasks can have dependencies on other tasks.
- Each Task can have its own retry policy, timeout, and execution configuration.

```sh
@task
def extract_data():
    print("Extracting data...")
```


### Operator
- An Operator is a template that defines how a task performs a specific operation.
- Each Operator instance represents a Task within a DAG.
- Different Operators support different types of operations.

```sh
from airflow.providers.standard.operators.bash import BashOperator
run_script = BashOperator(task_id="run_script",bash_command="python train.py")
```


### DAG Run
- A DAG Run represents one execution instance of an entire DAG.
- Created by the Scheduler or triggered manually/API.
- Each DAG Run has a unique Run ID within its DAG.
- Contains Task Instances corresponding to the DAG's tasks.
- Tracks the overall execution state.
Common DAG Run States:
- queued
- running
- success
- failed

```sh
DAG: daily_etl
DAG Run 1 → 2026-10-13 → success
DAG Run 2 → 2026-10-14 → success
DAG Run 3 → 2026-10-15 → running
```

### Task Instance
- A Task Instance represents a specific occurrence of a Task within a DAG Run.
- Each DAG Run creates its own Task Instances.
- Tracks execution state, start/end time, and retry attempts.
- The same Task can have different states across different DAG Runs.

```sh
Task: extract_data
DAG Run 1 → Task Instance → success
DAG Run 2 → Task Instance → failed
DAG Run 3 → Task Instance → running
```

### Task Dependencies
- Define the execution order and relationships between tasks.
- A downstream task generally waits for its upstream dependencies.
- Dependencies can be defined using >>, <<, or TaskFlow API.
- Trigger Rules determine when a task is eligible to run based on upstream states.

```text
extract >> transform >> load
extract >> [transform_a, transform_b]
```

### XCom (Cross-Communication)
- Enables data exchange between tasks.
- Commonly used to pass small values such as IDs, file paths, or metadata.
- By default, XCom values are stored in the Metadata Database.
- Large datasets should be stored externally, such as in S3 or MinIO.

```sh
@task
def extract():
    return "s3://bucket/data.csv"
@task
def transform(file_path):
    print(file_path)
transform(extract())
```

### Variables
- Store global key-value configurations accessible across DAGs.
- Useful for environment-specific settings and reusable configuration.
- Managed through the Airflow UI, API, or configured secrets backends.
- Should not be used to store sensitive credentials without appropriate secret management.

```sh
from airflow.sdk import Variable
bucket = Variable.get("data_bucket")
```

### Connections
- Store configuration required to connect to external systems.
- Can include host, port, username, password, and additional parameters.
- Identified by a unique conn_id.
- Used by Hooks and Operators to access external services.

```sh
PostgresHook(postgres_conn_id="analytics_db")
```
### Pools
- Control how many tasks can use a shared resource simultaneously.
- Prevent resource overload and excessive concurrent operations.
- Each Pool has a configurable number of slots.
- Tasks can occupy one or multiple slots.

```text
Pool: database_pool
Available Slots: 3

Task A → Running
Task B → Running
Task C → Running
Task D → Waiting
```

### Trigger Rules
- Define when a task can execute based on the states of its upstream tasks.
- The default trigger rule is all_success.
- Useful for branching, error handling, and cleanup operations.

```sh
cleanup = EmptyOperator(task_id="cleanup",trigger_rule="all_done")
```


## Components
### DAG Processor
- Discovers and parses Python DAG files.
- Extracts DAG definitions, tasks, dependencies, and schedules.
- Serializes DAG information and stores it in the Metadata Database.
- Does not execute tasks.

### Scheduler
- Creates DAG Runs based on schedules or triggers.
- Evaluates task dependencies and execution conditions.
- Identifies tasks ready for execution.
- Queues eligible tasks through the configured Executor.
- Monitors task states and determines DAG Run completion.

### Executor
- Determines how and where tasks are executed.
- Receives tasks from the Scheduler and manages their execution.
- Different Executor types support different execution environments.

### Worker / Task Runtime
- Performs the actual execution of task code.
- Runs Python functions, shell commands, SQL queries, API calls, etc.
- Produces logs, results, and task execution status.
- Its implementation depends on the Executor.
Examples:
- LocalExecutor → Local processes
- CeleryExecutor → Persistent Celery Workers
- KubernetesExecutor → Temporary Kubernetes Pods

### API Server
- Provides the Airflow Web UI and REST API.
- Handles user interactions, DAG triggering, and monitoring.
- Exposes the Task Execution API for communication between task runtimes and Airflow services.

### Metadata Database
- Stores Airflow's operational metadata.
- Maintains DAG definitions, DAG Runs, Task Instances, execution states, Variables, and Connections.
- Commonly uses PostgreSQL or MySQL.
- Does not store the actual datasets processed by tasks.

### Triggerer
- Manages asynchronous triggers for deferrable tasks.
- Allows tasks to wait for external events without occupying Worker slots.
- Resumes deferred tasks when their trigger conditions are met.

### Message Broker (CeleryExecutor Only)
- Typically Redis or RabbitMQ.
- Queues tasks submitted by CeleryExecutor.
- Distributes queued tasks to available Celery Workers.

### DAG Files / DAG Bundles
- Contain workflow definitions written in Python.
- Define tasks, dependencies, schedules, and execution configurations.
- DAG Bundles in Airflow 3 support different sources and versioned DAG code.

### Log Storage
- Stores task execution logs for monitoring and debugging.
- Can use local filesystems or remote storage such as Amazon S3.









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