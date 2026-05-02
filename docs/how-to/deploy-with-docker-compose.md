# Deploy With Docker Compose

## Topology
- Single container: `classifier-api`
- Volume mount: `./static:/app/static` for persisted uploaded files
- Healthcheck: `GET /health/liveness`

Evidence:
- `docker-compose.yml`

## Command
```bash
cd classifier-general
docker compose up -d --build
```

## Verify
```bash
docker compose ps
curl -s http://localhost:4002/health/liveness
```

## Production hardening gaps
- No reverse proxy/TLS config in this repo.
- Initial model pull can require network access if the HF cache is cold.
- No horizontal scaling coordination for in-memory labels (`/configlabel` mutates process-local state).

Evidence:
- `app/services/language_service.py`
- `app/services/classifier_service.py`
- `app/services/label_service.py`

## Unknown or inferred
- Unknown: expected deployment platform (only Docker artifacts are present).
- Inferred: this compose file targets local/dev usage.
