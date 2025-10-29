# Docker Setup Guide

## Fixed Issues ✅

- **Dockerfile**: Fixed development stage to copy both `requirements.txt` and `requirements-dev.txt`
- **docker-compose.sqlite.yml**: Removed DATABASE_URL override to use absolute paths from config
- **init_sqlite.py**: Added `--skip-prompt` flag for non-interactive database initialization

## Quick Start with Docker

### Option 1: SQLite (Recommended for Development)

```bash
# Build and start
docker-compose -f docker-compose.sqlite.yml up --build

# The database will be auto-initialized on first run
# Create an admin user
docker-compose -f docker-compose.sqlite.yml exec app python manage.py create-admin your_username
```

Access at: http://localhost:5000

### Option 2: PostgreSQL (Production-like)

```bash
# Build and start (includes PostgreSQL container)
docker-compose up --build

# Initialize database
docker-compose exec app python manage.py init-db
docker-compose exec app python manage.py create-admin your_username
```

Access at: http://localhost:5000

### Option 3: With MediaMTX Server

```bash
# Start with MediaMTX server included
docker-compose -f docker-compose.sqlite.yml --profile with-mediamtx up --build
```

Access:
- Control Plane: http://localhost:5000
- MediaMTX RTSP: rtsp://localhost:8554
- MediaMTX RTMP: rtmp://localhost:1935
- MediaMTX HLS: http://localhost:8888
- MediaMTX WebRTC: http://localhost:8889

## Docker Commands

### Build Images
```bash
# Development image (SQLite)
docker-compose -f docker-compose.sqlite.yml build

# Production image (PostgreSQL)
docker-compose build
```

### View Logs
```bash
# SQLite version
docker-compose -f docker-compose.sqlite.yml logs -f app

# PostgreSQL version
docker-compose logs -f app
```

### Execute Commands in Container
```bash
# Create admin user
docker-compose -f docker-compose.sqlite.yml exec app python manage.py create-admin username

# List users
docker-compose -f docker-compose.sqlite.yml exec app python manage.py list-users

# List customers
docker-compose -f docker-compose.sqlite.yml exec app python manage.py list-customers

# Access Python shell
docker-compose -f docker-compose.sqlite.yml exec app python

# Access bash shell
docker-compose -f docker-compose.sqlite.yml exec app bash
```

### Stop and Remove
```bash
# Stop containers
docker-compose -f docker-compose.sqlite.yml down

# Stop and remove volumes (deletes database!)
docker-compose -f docker-compose.sqlite.yml down -v
```

## Environment Configuration

Create a `.env` file or use environment variables:

```bash
# LDAP Configuration
LDAP_HOST=ldap://your-ad-server.example.com
LDAP_PORT=389
LDAP_BASE_DN=dc=example,dc=com
LDAP_BIND_USER_DN=cn=service_account,dc=example,dc=com
LDAP_BIND_USER_PASSWORD=your_password

# MediaMTX
MEDIAMTX_WEBHOOK_SECRET=shared-secret-with-mediamtx
```

## Volumes

### SQLite Version
- `sqlite_data:/app/instance` - Persists SQLite database across container restarts

### PostgreSQL Version
- `postgres_data` - Persists PostgreSQL database

## Troubleshooting

### Build Errors

**Error**: `Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'`

**Solution**: Fixed in latest Dockerfile - both requirements files are now copied before pip install

### Database Errors

**Error**: `unable to open database file`

**Solution**: Don't set `DATABASE_URL` environment variable in docker-compose - let config.py handle it

### Permission Errors

If you get permission errors with the SQLite volume:

```bash
docker-compose -f docker-compose.sqlite.yml down -v
docker-compose -f docker-compose.sqlite.yml up --build
```

## Production Deployment

For production, use the PostgreSQL version with proper security:

1. **Use production config**:
   ```yaml
   environment:
     FLASK_ENV: production
   ```

2. **Set strong secrets**:
   ```yaml
   environment:
     SECRET_KEY: <generate-random-secret>
     MEDIAMTX_WEBHOOK_SECRET: <generate-random-secret>
   ```

3. **Use reverse proxy** (nginx/traefik):
   - Enable HTTPS
   - Set proper headers
   - Rate limiting

4. **Database backups**:
   ```bash
   docker-compose exec db pg_dump -U mtxman mtxman > backup.sql
   ```

## Development Workflow

1. **Make code changes** - they're live-mounted in development mode
2. **Restart if needed**:
   ```bash
   docker-compose -f docker-compose.sqlite.yml restart app
   ```
3. **View logs**:
   ```bash
   docker-compose -f docker-compose.sqlite.yml logs -f app
   ```
4. **Run tests**:
   ```bash
   docker-compose -f docker-compose.sqlite.yml exec app pytest
   ```

## Multi-Stage Build

The Dockerfile uses multi-stage builds:

- **base**: Common dependencies (system packages)
- **development**: Development dependencies + live code mounting
- **production**: Production-only dependencies + optimized for deployment

Target the appropriate stage:
```bash
# Development
docker build --target development -t mtxman:dev .

# Production
docker build --target production -t mtxman:prod .
```

## Notes

- Development mode runs with Flask's built-in server (auto-reload enabled)
- Production mode runs with Gunicorn (4 workers, production-ready)
- SQLite database persists in Docker volume
- Code changes are immediately reflected (development mode only)
- Database schema changes require restart
