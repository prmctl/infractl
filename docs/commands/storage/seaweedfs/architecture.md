

# Architecture


```text
Master        ->  Knows where volumes are
Filer         ->  Knows filenames and directories
Volume Server ->  Stores the actual bytes
```


``` text
                         SeaweedFS Architecture
                 (S3 + Filer + Master + Volume Servers)


 +-------------------------------+
 |      Client / Application     |
 | AWS CLI / SDK / s3cmd / App   |
 +---------------+---------------+
                 |
                 | S3 API
                 | HTTP :8333
                 | PUT / GET / DELETE
                 v
 +-------------------------------+
 |          S3 Gateway           |
 |        weed s3 :8333          |
 |                               |
 |  S3-compatible API endpoint   |
 +---------------+---------------+
                 |
                 | Filer API
                 | HTTP / gRPC
                 v
 +-------------------------------+
 |             Filer             |
 |        weed filer :8888       |
 |                               |
 |  Paths / Directories          |
 |  File metadata                |
 |  Buckets / Permissions        |
 |  Chunk references             |
 +----------+--------------------+
            |
            |
       +----+-------------------------+
       |                              |
       | Metadata                     | Volume lookup /
       |                              | allocation
       v                              v
 +--------------------+       +-----------------------+
 | Metadata Database  |       |        Master         |
 |                    |       |      :9333            |
 | PostgreSQL         |       |                       |
 | MySQL              |       | Cluster topology      |
 | SQLite             |       | Volume locations      |
 | etc.               |       | Volume assignment     |
 |                    |       | Volume Server health  |
 | Paths              |       +-----------+-----------+
 | File entries       |                   |
 | Chunk references   |                   |
 | Permissions        |                   | topology /
 +--------------------+                   | heartbeat
                                          |
                      +-------------------+-------------------+
                      |                   |                   |
                      v                   v                   v
              +---------------+   +---------------+   +---------------+
              | Volume Server |   | Volume Server |   | Volume Server |
              |      VS1      |   |      VS2      |   |      VS3      |
              |     :8080     |   |     :8080     |   |     :8080     |
              +-------+-------+   +-------+-------+   +-------+-------+
                      |                   |                   |
                      v                   v                   v
                 /data/vol1          /data/vol2          /data/vol3
                 *.dat               *.dat               *.dat
                 *.idx               *.idx               *.idx
                 File Content        File Content        File Content


             ======== Actual File Data Path ========

 +---------+       +------------+       +---------+
 | Client  | ----> | S3 Gateway | ----> |  Filer  |
 +---------+       +------------+       +----+----+
                                            |
                         finds/allocates     |
                         volume location     |
                                            v
                                      +-----------+
                                      |  Master   |
                                      +-----------+
                                            |
                                      location info
                                            |
                                            v
                                      +-----------+
                                      |  Filer    |
                                      +-----+-----+
                                            |
                                            | actual file
                                            | read / write
                                            v
                                    +---------------+
                                    | Volume Server |
                                    |     :8080     |
                                    +-------+-------+
                                            |
                                            v
                                      .dat / .idx


 IMPORTANT:
 ┌──────────────────────────────────────────────────────────────┐
 │ Master does NOT store the actual file data.                  │
 │                                                              │
 │ Database stores metadata, paths and chunk references.        │
 │                                                              │
 │ Volume Servers store the actual file contents.               │
 │                                                              │
 │ Filer provides filesystem semantics and coordinates access.  │
 │                                                              │
 │ S3 Gateway translates S3 operations to Filer operations.     │
 └──────────────────────────────────────────────────────────────┘
```


‍‍‍‍``text
Namespace / Metadata ≠ Storage Management ≠ Actual File Data
```

‍‍‍```text
          “What is the file name and metadata?”
                         |
                         v
                Filer + Database
                         |
                         |
              “Where is the file located?”
                         |
                         v
                      Master
                         |
                         |
              “The actual file bytes”
                         |
                         v
                  Volume Servers

```

## S3 Gateway

The primary responsibility of the **S3 Gateway** is to provide an **S3-compatible API**. It receives requests and translates them into operations that the **Filer** can understand.

```text
AWS CLI
   |
   | S3 Language
   v
+----------------+
|   S3 Gateway   |   ← translator
+----------------+
   |
   | Filer operations
   v
Filer
```


## Filer
Filer as a filesystem layer.
‍‍```text
Filer = Logic / Service
```

The Filer provides SeaweedFS with concepts such as:
```text
Directory
File
Path
Filename
Size
Permissions
Timestamps
Extended attributes
Chunks belonging to a file
```

Suppose we have the following file:
```text
/photos/2026/vacation.jpg
```
For us, this path is meaningful.
However, the underlying storage layer may primarily deal with identifiers and data chunks.
The **Filer** maintains a relationship similar to this:

```text
/photos/2026/vacation.jpg
             |
             v
      metadata / chunks
             |
             v
     references to stored data
```

So, you can think of the **Filer** roughly as:

> **“The manager of files and the namespace.”**

## Metadata Database

The Filer handles the logic, while the Metadata Store maintains the state.

```text
Metadata Store = Persistent State
```

```text
Filer
  ↓
Metadata Store
```



## Master


## Volume Server


Think of a **Volume** as a **large container that holds many smaller objects/chunks**.
