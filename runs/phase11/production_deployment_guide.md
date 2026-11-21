# ClaimSense AI — Production Deployment & Operational Runbook
## Guide to Containerized, Cloud & On-Premises Production Hosting

**Document Version:** 1.0.0  
**Phase Reference:** Phase 11 Production Hardening  
**Target Environments:** Linux (Docker / Podman / Kubernetes) & Windows Server (Waitress / IIS)

---

## 1. Quickstart: Docker Compose Deployment

The recommended production deployment utilizes Docker Compose with an Nginx edge reverse proxy:

```bash
# 1. Clone the repository and enter directory
git clone https://github.com/anshg8252/ClaimSense-AI.git
cd ClaimSense-AI

# 2. Configure production environment variables
cat << 'EOF' > .env
FLASK_ENV=production
FLASK_DEBUG=0
PORT=5001
HOST=0.0.0.0
SQLITE_WAL_MODE=true
JSON_LOGGING=true
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
CORS_ALLOWED_ORIGINS=https://claims.yourcompany.com,http://localhost
EOF

# 3. Build container images and launch the stack in detached mode
docker compose up -d --build

# 4. Verify container health status
docker compose ps
docker compose logs -f app
```

Once running, the application is accessible at:
- Web Application & Assessor Portal: `http://localhost/`
- API Health Check: `http://localhost/api/health`
- Deep Readiness Probe: `http://localhost/api/health/ready`
- Telemetry Metrics: `http://localhost/api/health/metrics`

---

## 2. Native Bare-Metal / Virtual Machine Deployment

### 2.1 Linux Environment (Gunicorn WSGI)
```bash
# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Launch via production runner
python scripts/serve_production.py --host 0.0.0.0 --port 5001 --workers 4 --threads 4 --server gunicorn
```

### 2.2 Windows Production Environment (Waitress WSGI)
```powershell
# Create virtual environment and install dependencies
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
pip install waitress

# Launch via production runner
python scripts/serve_production.py --host 0.0.0.0 --port 5001 --threads 8 --server waitress
```

---

## 3. SQLite Database Maintenance & Automated Backups

### 3.1 Enabling Write-Ahead Logging (WAL)
Set `SQLITE_WAL_MODE=true` in your environment or `.env`. This configures:
- `PRAGMA journal_mode=WAL;`
- `PRAGMA synchronous=NORMAL;`
- `PRAGMA busy_timeout=5000;`

WAL mode decouples read transactions from write transactions, reducing p95 latency under high concurrency by up to 30%.

### 3.2 Automated Daily Backups
Schedule daily execution of `scripts/backup_database.py` via cron (Linux) or Task Scheduler (Windows):

```bash
# Execute zero-downtime backup with 30-day retention
python scripts/backup_database.py --db data/claimsense.db --dest backups --retention-days 30
```

To verify the cryptographic integrity of any backup archive:
```bash
python scripts/backup_database.py --verify backups/claimsense_20261121_120000.db
```

---

## 4. Monitoring & Health Probes

Configure your load balancer (AWS ALB, Cloudflare, Traefik, Kubernetes) with these endpoints:

| Endpoint | Target | HTTP Success Code | Expected Response | Description |
|:---|:---|:---:|:---|:---|
| `/api/health` | Load Balancer | `200 OK` | `{"status": "healthy"}` | Fast, lightweight alive check. |
| `/api/health/live` | K8s Liveness | `200 OK` | `{"status": "alive", "uptime_seconds": ...}` | Verifies process is responsive. |
| `/api/health/ready` | K8s Readiness | `200 OK` | `{"status": "ready", "ready": true, ...}` | Verifies DB, storage, and ML models. |
| `/api/health/metrics` | Prometheus / Datadog | `200 OK` | `{"entity_counts": ..., "memory_rss_mb": ...}` | Operational system metrics. |

---

## 5. Report Snapshot Persistence Management

When a claim is adjudicated:
```bash
# Freeze an immutable audit PDF report snapshot
curl -X POST http://localhost:5001/api/claims/CLM-YYYYMMDD-XXXX/freeze-report \
     -H "Cookie: session=..."
```
Subsequent requests to `GET /api/claims/CLM-YYYYMMDD-XXXX/report` will serve the frozen static PDF directly from disk with ETag caching and `X-Report-Source: persisted-snapshot`.
