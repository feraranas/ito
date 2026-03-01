# Ito: Running from Source - Complete Guide

A comprehensive guide to understanding the infrastructure requirements and setup process for running Ito from source.

---

## Table of Contents

1. [What You Need vs What's Automated](#what-you-need-vs-whats-automated)
2. [Required: GROQ API Key](#required-groq-api-key)
3. [Automated: PostgreSQL Database](#automated-postgresql-database)
4. [Automated: S3 Storage (MinIO)](#automated-s3-storage-minio)
5. [The gRPC Transcription Server](#the-grpc-transcription-server)
6. [Deep Dive: How local-services-up Works](#deep-dive-how-local-services-up-works)
7. [Quick Setup Summary](#quick-setup-summary)
8. [Optional Components](#optional-components)

---

## What You Need vs What's Automated

### ✅ Things You MUST Set Up Manually

| Component | Why | How to Get It |
|-----------|-----|---------------|
| **GROQ API Key** | Required for AI transcription | Sign up at [console.groq.com](https://console.groq.com) |
| **Docker** | Runs PostgreSQL & MinIO containers | Install [Docker Desktop](https://docker.com) |
| **Bun** | Package manager & runtime | Install via [bun.sh](https://bun.sh) |
| **Rust** | Builds native components | Install via [rustup.rs](https://rustup.rs) |

### ❌ Things That Are Automated (No Setup Needed)

| Component | How It's Handled |
|-----------|------------------|
| **PostgreSQL Database** | Runs in Docker via `bun run local-services-up` |
| **S3 Storage** | MinIO (S3-compatible) runs in Docker |
| **S3 Buckets** | Automatically created by setup script |
| **Database Schema** | Created via `bun run db:migrate` |

### ❓ Optional Components

| Component | Required? | Notes |
|-----------|-----------|-------|
| **CEREBRAS_API_KEY** | No | Only for reasoning features |
| **Auth0** | No | Set `REQUIRE_AUTH=false` for local dev |
| **Stripe** | No | Only for billing features |
| **AWS Account** | No | Only for production deployment |

---

## Required: GROQ API Key

Ito uses GROQ's cloud API for speech-to-text transcription. **You don't run your own AI model** - you just need an API key.

### How to Get It

1. Visit [console.groq.com](https://console.groq.com)
2. Create an account or sign in
3. Navigate to **API Keys** section
4. Create a new API key
5. Copy the key to your `server/.env` file as `GROQ_API_KEY`

### What GROQ Provides

- High-accuracy speech-to-text transcription
- Real-time streaming transcription support
- Multiple language support
- The AI model runs on GROQ's infrastructure (no GPU needed locally)

---

## Automated: PostgreSQL Database

The database runs entirely in Docker - **no manual PostgreSQL installation required**.

### What Gets Created

- **Container name**: `ito-postgres`
- **Image**: `postgres:16` (official PostgreSQL)
- **Default port**: `5432`
- **Data persistence**: Docker volume named `pgdata`

### Database Schema

After starting the database, run migrations to create tables:

```bash
bun run db:migrate
```

This creates tables for:
- `users` - User profiles and settings
- `notes` - Transcribed text and metadata
- `interactions` - Dictation sessions (with S3 audio references)
- `dictionary` - Custom vocabulary
- `llm_settings` - User-specific LLM configuration

### Configuration (via .env)

```bash
DB_HOST=localhost
DB_PORT=5432
DB_USER=devuser
DB_PASS=devpass
DB_NAME=devdb
```

---

## Automated: S3 Storage (MinIO)

For local development, Ito uses **MinIO** - an S3-compatible object storage that runs in Docker.

### What Gets Created

- **Container name**: `ito-minio`
- **S3 API port**: `9000`
- **Web Console port**: `9001`
- **Data persistence**: Docker volume named `minio_data`

### Buckets Created Automatically

- `ito-audio-storage` - Stores raw audio recordings
- `ito-timing-storage` - Stores timing data

### Accessing MinIO Console

- **URL**: http://localhost:9001
- **Username**: `minioadmin`
- **Password**: `minioadmin`

Use the console to:
- View stored audio files
- Monitor storage usage
- Debug S3 operations

### Configuration (via .env)

```bash
BLOB_STORAGE_BUCKET=ito-audio-storage
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_FORCE_PATH_STYLE=true
```

---

## The gRPC Transcription Server

The `server/` directory contains the transcription server that connects your desktop app to GROQ.

### What It Does

1. Receives audio from the Electron app via gRPC
2. Sends audio to GROQ for transcription
3. Returns transcribed text to the app
4. Manages user data (notes, dictionary, interactions)

### Technology Stack

- **Fastify** - HTTP/gRPC server
- **Connect RPC** - Type-safe gRPC implementation
- **GROQ SDK** - AI transcription integration
- **PostgreSQL** - Data storage
- **S3/MinIO** - Audio file storage

### API Services

| Service | Purpose |
|---------|---------|
| `TranscribeFile` | Single file transcription |
| `TranscribeStream` | Real-time streaming transcription |
| `CreateNote` | Save transcribed text |
| `ListNotes` | Retrieve saved notes |
| `Dictionary` | Custom vocabulary management |
| `Interactions` | Dictation session tracking |

---

## Deep Dive: How local-services-up Works

Understanding the complete flow of `bun run local-services-up`:

### Command Chain

```
bun run local-services-up
├── bun local-db-up
│   └── docker compose up -d db
│       └── Starts PostgreSQL container
│
└── bun local-s3-up
    ├── docker compose up -d minio
    │   └── Starts MinIO container
    ├── sleep 3
    │   └── Waits for MinIO to initialize
    └── bash ./scripts/setup-minio.sh
        ├── Installs MinIO client (mc) if needed
        ├── Configures connection to local MinIO
        └── Creates storage buckets
```

### package.json Scripts

```json
{
  "local-db-up": "docker compose up -d db",
  "local-s3-up": "docker compose up -d minio && sleep 3 && bash ./scripts/setup-minio.sh",
  "local-services-up": "bun local-db-up && bun local-s3-up"
}
```

### docker-compose.yml - PostgreSQL Service

```yaml
db:
  image: postgres:16
  container_name: ito-postgres
  restart: always
  environment:
    POSTGRES_USER: '$DB_USER'
    POSTGRES_PASSWORD: '$DB_PASS'
    POSTGRES_DB: '$DB_NAME'
  ports:
    - '$DB_PORT:$DB_PORT'
  volumes:
    - pgdata:/var/lib/postgresql/data
```

Key points:
- Uses official PostgreSQL 16 image
- Environment variables come from `.env` file
- Data persists in Docker volume `pgdata`
- Automatically restarts if it crashes

### docker-compose.yml - MinIO Service

```yaml
minio:
  image: minio/minio:latest
  container_name: ito-minio
  restart: always
  command: server /data --console-address ":9001"
  environment:
    MINIO_ROOT_USER: '$S3_ACCESS_KEY_ID'
    MINIO_ROOT_PASSWORD: '$S3_SECRET_ACCESS_KEY'
  ports:
    - '9000:9000'  # S3 API
    - '9001:9001'  # MinIO Console
  volumes:
    - minio_data:/data
  healthcheck:
    test: ['CMD', 'mc', 'ready', 'local']
    interval: 5s
    timeout: 5s
    retries: 5
```

Key points:
- Exposes two ports: API (9000) and Console (9001)
- Has health check to ensure it's ready before other services use it
- Data persists in Docker volume `minio_data`

### setup-minio.sh Script

What it does:
1. Installs MinIO client (`mc`) via Homebrew (macOS) if not present
2. Configures `mc` to connect to local MinIO at `localhost:9000`
3. Creates `ito-blob-storage` bucket
4. Creates `ito-timing-storage` bucket
5. Sets bucket permissions for read/write access

---

## Quick Setup Summary

### Complete Setup Commands

```bash
# 1. Clone the repository
git clone https://github.com/heyito/ito.git
cd ito

# 2. Install app dependencies
bun install

# 3. Set up the server
cd server
cp .env.example .env
# Edit .env and add:
#   - GROQ_API_KEY=your_key_here
#   - REQUIRE_AUTH=false

bun install

# 4. Start infrastructure (PostgreSQL + MinIO)
bun run local-services-up

# 5. Run database migrations
bun run db:migrate

# 6. Start the transcription server
bun run dev

# 7. In a NEW terminal, start the Electron app
cd /path/to/ito  # (the root directory)
./build-binaries.sh  # Build Rust native components
bun run dev          # Start Electron app
```

### Minimum .env Configuration

```bash
# Database (uses Docker defaults)
DB_HOST=localhost
DB_PORT=5432
DB_USER=devuser
DB_PASS=devpass
DB_NAME=devdb

# S3/MinIO (uses Docker defaults)
BLOB_STORAGE_BUCKET=ito-audio-storage
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_FORCE_PATH_STYLE=true

# GROQ (REQUIRED - get from console.groq.com)
GROQ_API_KEY=your_groq_api_key_here

# Disable auth for local development
REQUIRE_AUTH=false
```

---

## Optional Components

### CEREBRAS_API_KEY

- **Purpose**: Used for AI reasoning features
- **Required**: No
- **Get it from**: [cerebras.ai](https://cerebras.ai)

### Auth0 (Authentication)

- **Purpose**: User authentication and management
- **Required**: No (set `REQUIRE_AUTH=false`)
- **For production**: Set up at [auth0.com](https://auth0.com)

### Stripe (Billing)

- **Purpose**: Payment processing
- **Required**: No for local development
- **Configuration**:
  ```bash
  STRIPE_SECRET_KEY=sk_test_xxx
  STRIPE_WEBHOOK_SECRET=whsec_xxx
  STRIPE_PRICE_ID=price_xxx
  ```

---

## Troubleshooting

### Database Connection Errors

```bash
# Check if containers are running
docker ps

# Restart services
bun run local-services-down
bun run local-services-up

# Verify .env credentials match docker-compose expectations
```

### GROQ API Errors

- Verify API key is valid in .env
- Check you have credits in your GROQ account
- Test API key at console.groq.com

### MinIO/S3 Issues

```bash
# Restart MinIO
bun run local-s3-down
bun run local-s3-up

# Manually run bucket setup
bash ./scripts/setup-minio.sh

# Check MinIO console at http://localhost:9001
```

### Port Conflicts

Default ports used:
- `5432` - PostgreSQL
- `9000` - MinIO S3 API
- `9001` - MinIO Console
- `3000` - gRPC Server

If these are in use, modify `docker-compose.yml` and update `.env` accordingly.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User's Computer                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐     gRPC      ┌─────────────────────────┐  │
│  │   Electron App   │◄────────────►│   Transcription Server   │  │
│  │   (Desktop UI)   │              │   (server/ directory)    │  │
│  └─────────────────┘              └───────────┬─────────────┘  │
│         │                                      │                  │
│         │ Native Rust                          │ API Calls        │
│         │ Components                           ▼                  │
│         │                          ┌─────────────────────────┐  │
│         │                          │     Docker Containers    │  │
│         │                          │  ┌─────────┐ ┌────────┐  │  │
│         ▼                          │  │PostgreSQL│ │ MinIO  │  │  │
│  ┌─────────────────┐              │  │   DB    │ │  S3    │  │  │
│  │  audio-recorder  │              │  └─────────┘ └────────┘  │  │
│  │  text-writer     │              └─────────────────────────┘  │
│  │  key-listener    │                                            │
│  └─────────────────┘                                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTPS API
                                      ▼
                            ┌─────────────────┐
                            │   GROQ Cloud    │
                            │ (AI Transcription)│
                            └─────────────────┘
```

---

*Generated from development conversation - Ito Voice Assistant*

