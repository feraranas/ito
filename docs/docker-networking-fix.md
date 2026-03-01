# Docker Container Networking: Database Connection Fix

## The Problem

The server was failing with this error during sync:

```
ConnectError: [internal] Internal server error
error: connect ECONNREFUSED 127.0.0.1:5432
```

The gRPC server couldn't connect to PostgreSQL, causing all database operations (like `listNotes`) to fail.

## Root Cause

The `.env` file had:

```
DB_HOST=localhost
```

This works when running the server directly on your machine, but **fails inside a Docker container**.

## Why `localhost` Doesn't Work in Docker

Each Docker container is an isolated environment with its own network namespace. When you use `localhost` or `127.0.0.1` inside a container, it refers to **that container itself**, not:

- Your host machine
- Other containers
- The PostgreSQL container

```
┌─────────────────────────────────────────────────────────┐
│                     Host Machine                        │
│                                                         │
│  ┌─────────────────┐         ┌─────────────────┐       │
│  │  ito-server     │         │  ito-postgres   │       │
│  │  container      │         │  container      │       │
│  │                 │         │                 │       │
│  │  localhost:5432 │ ──X──>  │  postgres:5432  │       │
│  │  (points here!) │         │                 │       │
│  └─────────────────┘         └─────────────────┘       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

When the server tries to connect to `localhost:5432`, it's looking for PostgreSQL **inside its own container**, where nothing is listening on port 5432.

## The Fix

Change `DB_HOST` from `localhost` to the Docker Compose service name:

```diff
- DB_HOST=localhost
+ DB_HOST=db
```

## How Docker Compose Networking Works

Docker Compose automatically creates a network for your services and sets up DNS resolution. Each service can be reached by its service name.

From `docker-compose.yml`:

```yaml
services:
  ito-grpc-server:    # Can be reached as "ito-grpc-server"
    ...

  db:                  # Can be reached as "db"
    image: postgres:16
    ...
```

Docker's internal DNS resolves `db` to the PostgreSQL container's IP address:

```
┌─────────────────────────────────────────────────────────┐
│                Docker Compose Network                   │
│                                                         │
│  ┌─────────────────┐         ┌─────────────────┐       │
│  │  ito-server     │         │  ito-postgres   │       │
│  │                 │         │  (service: db)  │       │
│  │                 │         │                 │       │
│  │  db:5432        │ ──────> │  postgres:5432  │       │
│  │  (DNS resolves  │         │                 │       │
│  │   to container) │         │                 │       │
│  └─────────────────┘         └─────────────────┘       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Key Concepts

### 1. Container Isolation
Each container has its own:
- Filesystem
- Process space
- Network namespace (including its own `localhost`)

### 2. Docker Compose Networks
Docker Compose automatically:
- Creates a bridge network for all services
- Assigns each container an IP on that network
- Sets up DNS so services can find each other by name

### 3. Service Discovery
Use the **service name** (from `docker-compose.yml`) to connect between containers:

| Service Definition | Hostname to Use |
|-------------------|-----------------|
| `db:` | `db` |
| `minio:` | `minio` |
| `ito-grpc-server:` | `ito-grpc-server` |

### 4. Port Mapping vs Internal Ports

```yaml
db:
  ports:
    - '5432:5432'  # host:container
```

- **From host machine**: Connect to `localhost:5432` (mapped port)
- **From another container**: Connect to `db:5432` (internal network)

## Common Patterns

### Environment Variables for Different Contexts

Some projects use different env files:

```
.env              # For Docker (DB_HOST=db)
.env.local        # For local development (DB_HOST=localhost)
```

### Checking Container Connectivity

Debug network issues from inside a container:

```bash
# Enter the server container
docker compose exec ito-grpc-server sh

# Test DNS resolution
nslookup db

# Test connectivity
nc -zv db 5432
```

## Summary

| Context | Use |
|---------|-----|
| Running on host machine | `localhost` or `127.0.0.1` |
| Running in Docker container | Service name (e.g., `db`) |

When running services in Docker Compose, always use **service names** for inter-container communication.
