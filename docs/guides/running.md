# Running

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://localhost:8000`. API docs at `/docs`.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATA_PATH` | `./data` | Directory for assetforge.db, attachments/, backups/ |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Listen port |
| `LOG_LEVEL` | `info` | uvicorn log level |

Copy `.env.example` to `.env` and adjust as needed.

---

## Docker

Copy `.env.example` to `.env` and adjust `HOST`/`PORT` as needed —
`docker-compose.yml` reads it automatically, and the Dockerfile's `CMD` picks
up `$HOST`/`$PORT` from the container environment at start (falling back to
`0.0.0.0`/`8000` if unset).

```bash
# Build
docker build -t assetforge .

# Run (mount data directory for persistence, pass your .env through)
# -p must match PORT in .env if you changed it from the 8000 default
docker run -d \
  --name assetforge \
  --env-file .env \
  -p 8000:8000 \
  -v /path/to/your/data:/app/data \
  assetforge
```

Or with `docker-compose.yml` (already wired to `.env`):

```yaml
services:
  assetforge:
    build: .
    env_file:
      - .env
    ports:
      - "${PORT:-8000}:${PORT:-8000}"
    volumes:
      - ${DATA_PATH:-./data}:/app/data
    environment:
      - DATA_PATH=/app/data
    restart: unless-stopped
```

```bash
docker compose up -d
```

---

## Backup

The simplest backup is a directory copy:

```bash
cp -r data/ backups/assetforge_$(date +%Y%m%d)/
```

Or rsync to your NAS:

```bash
rsync -av data/ homelab-nas:/backups/assetforge/
```

The tracker also auto-backs up `assetforge.db` to `data/backups/` before any
import or replace operation.

A scheduled backup via APScheduler is added in V1.

---

## Restore

```bash
# From JSON export
curl -X POST http://localhost:8000/api/import/json \
     -F "file=@assetforge_backup.json"

# From SQLite snapshot (V1)
# Stop the server, replace data/assetforge.db, restart
cp assetforge_backup.db data/assetforge.db
```

The JSON import endpoint auto-backs up the existing DB before replacing.
