"""Self-hosted deployment documentation."""

# HorizonCast Self-Hosted Deployment Guide

## System Requirements

- Docker & Docker Compose
- 4GB+ RAM
- 50GB+ disk space
- Linux, macOS, or Windows with WSL2

## Quick Start

### 1. Clone and Setup

```bash
git clone <repo-url>
cd horizoncast
cp .env.example .env
```

### 2. Configure Environment

Edit `.env`:

```bash
# Database
POSTGRES_USER=horizoncast
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://horizoncast:your_secure_password@postgres:5432/horizoncast

# Redis
REDIS_URL=redis://redis:6379

# Clerk (optional, for auth)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_key
CLERK_SECRET_KEY=your_clerk_secret

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Start Services

```bash
docker-compose up -d
```

### 4. Initialize Database

```bash
docker-compose exec backend python -m backend.database
```

### 5. Access Application

- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: postgresql://localhost:5432/horizoncast

## Production Deployment

### With Nginx Reverse Proxy

Use `nginx.conf` to proxy frontend and backend through port 80/443.

### With Let's Encrypt

```bash
docker run -it --rm --name certbot \
  -v /etc/letsencrypt:/etc/letsencrypt \
  certbot/certbot certonly --standalone -d your-domain.com
```

## Backup and Restore

### Backup Database

```bash
docker-compose exec postgres pg_dump -U horizoncast horizoncast > backup.sql
```

### Restore Database

```bash
docker-compose exec -T postgres psql -U horizoncast horizoncast < backup.sql
```

## Scaling

For high-volume deployments, use:

- **Load balancer**: HAProxy or AWS ALB
- **Async workers**: Celery with Redis
- **Database**: PostgreSQL with replication
- **Cache**: Redis cluster

## Monitoring

Install Prometheus + Grafana:

```bash
# Add monitoring stack to docker-compose.yml
# See: https://github.com/prometheus-community/docker-compose
```

## Troubleshooting

### Container fails to start

```bash
docker-compose logs backend
docker-compose logs frontend
```

### Database connection errors

```bash
docker-compose exec postgres psql -U horizoncast -d horizoncast
```

### Out of memory

Increase Docker memory limits in `docker-compose.yml`:

```yaml
services:
  backend:
    mem_limit: 2g
```

## Support

For issues, visit: https://github.com/horizoncast/horizoncast/issues
