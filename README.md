# MediaMTX Control Plane

A Flask-based control plane for managing MediaMTX stream authentication via AD/LDAP and API keys.

## Features

- **AD/LDAP Authentication**: Admin users authenticate via Active Directory or LDAP
- **Customer Management**: Create and manage customers who need stream access
- **API Key Generation**: Generate secure API keys for customer stream authentication
- **MediaMTX Integration**: External authentication webhook for validating stream access
- **Permission Control**: Granular permissions for publish/read access per API key
- **Key Expiration**: Optional expiration dates for API keys
- **REST API**: Programmatic access to customer and key management
- **Flexible Database**: SQLite for quick start or PostgreSQL for production

## Architecture

```
┌─────────────────┐
│   Admin User    │
│   (AD/LDAP)     │
└────────┬────────┘
         │
         v
┌─────────────────────────────┐
│   Flask Control Plane       │
│  ┌──────────────────────┐   │
│  │  Customer Management │   │
│  │  API Key Generation  │   │
│  └──────────────────────┘   │
└────────┬────────────────────┘
         │
         v
┌─────────────────────────────┐
│    Database (SQLite/PG)     │
│  - Users (Admins)           │
│  - Customers                │
│  - API Keys                 │
└─────────────────────────────┘
         ^
         │
         │ Auth Request
         │
┌────────┴────────────────────┐
│      MediaMTX Server        │
│  - RTSP/RTMP/HLS/WebRTC     │
│  - External Auth Enabled    │
└─────────────────────────────┘
         ^
         │ Stream Access
         │ (API Key)
         │
┌────────┴────────┐
│  End User/App   │
└─────────────────┘
```

## Quick Start

### Option 1: SQLite (Fastest - No Database Server Required)

Perfect for development and testing without any external dependencies!

1. **Set up Python environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

2. **Initialize SQLite database** (interactive setup):
   ```bash
   python init_sqlite.py
   ```

   Or use the Makefile:
   ```bash
   make init-sqlite
   ```

3. **Run the application**:
   ```bash
   python app.py
   # Or: make run
   ```

4. **Access the application**:
   - Control Plane: http://localhost:5000
   - Log in with the admin credentials you created

That's it! No Docker, no PostgreSQL server needed.

### Option 2: Docker with SQLite

1. **Start the application**:
   ```bash
   docker-compose -f docker-compose.sqlite.yml up -d
   # Or: make docker-up-sqlite
   ```

2. **Initialize database**:
   ```bash
   docker-compose -f docker-compose.sqlite.yml exec app python init_sqlite.py
   ```

3. **Access the application**:
   - Control Plane: http://localhost:5000

### Option 3: Docker with PostgreSQL (Production-Like)

1. **Clone and configure**:
   ```bash
   git clone <repo>
   cd mtxman
   cp .env.example .env
   # Edit .env with your LDAP/AD settings
   ```

2. **Start services**:
   ```bash
   docker-compose up -d
   ```

3. **Initialize database**:
   ```bash
   docker-compose exec app python manage.py init-db
   docker-compose exec app python manage.py create-admin your_username
   ```

4. **Access the application**:
   - Control Plane: http://localhost:5000
   - MediaMTX (optional): rtsp://localhost:8554

### Option 4: Local Development with PostgreSQL

1. **Set up Python environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-postgres.txt  # Includes PostgreSQL driver
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit DATABASE_URL to use PostgreSQL
   # DATABASE_URL=postgresql://user:password@localhost:5432/mtxman
   ```

3. **Set up database**:
   ```bash
   # Install PostgreSQL locally or use Docker:
   docker run -d --name postgres \
     -e POSTGRES_DB=mtxman \
     -e POSTGRES_USER=mtxman \
     -e POSTGRES_PASSWORD=mtxman_password \
     -p 5432:5432 \
     postgres:15-alpine

   # Initialize database
   python manage.py init-db
   python manage.py create-admin your_username
   ```

4. **Run development server**:
   ```bash
   python app.py
   ```

## Configuration

### Environment Variables

See [.env.example](.env.example) for all configuration options. Key settings:

- **LDAP/AD Settings**: Configure your AD/LDAP server connection
- **Database**: PostgreSQL connection string
- **MediaMTX**: Webhook secret and base URL
- **Security**: Secret key, session settings

### LDAP/AD Configuration

Example for Active Directory:

```bash
LDAP_HOST=ldap://ad.company.com
LDAP_PORT=389
LDAP_BASE_DN=dc=company,dc=com
LDAP_USER_DN=ou=users,dc=company,dc=com
LDAP_BIND_USER_DN=cn=service_account,dc=company,dc=com
LDAP_BIND_USER_PASSWORD=service_password
LDAP_USER_LOGIN_ATTR=sAMAccountName
```

### MediaMTX Configuration

Configure MediaMTX to use external authentication by editing `mediamtx.yml`:

```yaml
externalAuthenticationURL: http://your-control-plane:5000/api/mediamtx/auth
```

## Usage

### Managing Customers

1. Log in with your AD/LDAP credentials
2. Navigate to **Customers** → **Create Customer**
3. Fill in customer details (name, email, organization)
4. Submit to create customer

### Generating API Keys

1. Open a customer's detail page
2. Click **Create API Key**
3. Configure:
   - Name (for identification)
   - Permissions (publish/read)
   - Expiration (optional)
4. Copy the generated API key (shown only once!)
5. Provide key to customer

### Stream Authentication

Customers can authenticate to MediaMTX using their API key in three ways:

**1. Query Parameter**:
```
rtsp://server:8554/stream/path?api_key=mtx_abc123...
```

**2. Username**:
```
rtsp://mtx_abc123...@server:8554/stream/path
```

**3. Password**:
```
rtsp://anyuser:mtx_abc123...@server:8554/stream/path
```

## API Reference

### REST API Endpoints

#### List Customers
```http
GET /api/api/v1/customers
Authorization: Required (session)
```

#### Get Customer
```http
GET /api/api/v1/customers/{id}
Authorization: Required (session)
```

#### List Customer Keys
```http
GET /api/api/v1/customers/{id}/keys
Authorization: Required (session)
```

### MediaMTX Webhook

#### External Auth
```http
POST /api/mediamtx/auth
Content-Type: application/json

{
  "action": "read" | "publish",
  "path": "stream/path",
  "protocol": "rtsp",
  "query": "api_key=xxx",
  "user": "username",
  "password": "password",
  "ip": "client_ip"
}
```

**Response**:
- `200 OK`: Authentication successful
- `401 Unauthorized`: Invalid or missing API key
- `403 Forbidden`: Valid key but insufficient permissions

## Testing

Run the complete test suite:

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# E2E tests only
pytest tests/e2e/

# With coverage report
pytest --cov=app --cov-report=html
```

## Deployment

### Production with Docker

1. **Build production image**:
   ```bash
   docker build --target production -t mtxman:latest .
   ```

2. **Run with docker-compose**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

### Production with Gunicorn

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 60 wsgi:app
```

### Environment Setup

For production:
- Set `FLASK_ENV=production`
- Use strong `SECRET_KEY`
- Enable `SESSION_COOKIE_SECURE=True` (requires HTTPS)
- Configure proper LDAP/AD credentials
- Use managed PostgreSQL database
- Set up proper logging and monitoring

## Management Commands

```bash
# Initialize database
python manage.py init-db

# Create admin user
python manage.py create-admin <username>

# List all users
python manage.py list-users

# List all customers
python manage.py list-customers
```

## Development

### Code Quality

This project uses pre-commit hooks for code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Project Structure

```
mtxman/
├── app/
│   ├── __init__.py          # App factory
│   ├── models/              # Database models
│   ├── services/            # Business logic
│   ├── auth/                # Authentication blueprint
│   ├── api/                 # API routes and MediaMTX integration
│   ├── templates/           # Jinja2 templates (optional)
│   └── static/              # Static files (optional)
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── e2e/                 # End-to-end tests
├── config.py                # Configuration classes
├── app.py                   # Development entry point
├── wsgi.py                  # Production WSGI entry point
├── manage.py                # CLI management commands
└── requirements.txt         # Python dependencies
```

## Security Considerations

- **API Keys**: Stored as SHA-256 hashes, never in plaintext
- **LDAP Passwords**: Never stored, validated against LDAP server
- **Session Security**: HTTPOnly, Secure, and SameSite cookies
- **Database**: Uses parameterized queries via SQLAlchemy ORM
- **Webhook Security**: Optional HMAC signature verification for MediaMTX webhooks

## Troubleshooting

### LDAP Connection Issues

Check LDAP configuration:
```bash
# Test LDAP connection
ldapsearch -x -H ldap://your-server -D "cn=user,dc=company,dc=com" -W
```

### Database Connection Issues

Verify PostgreSQL is running and accessible:
```bash
psql -h localhost -U mtxman -d mtxman
```

### MediaMTX Authentication Not Working

1. Check MediaMTX logs for webhook requests
2. Verify control plane is accessible from MediaMTX container
3. Check webhook secret matches in both configurations
4. Review Flask application logs for authentication attempts

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [Link to your repo issues]
- Documentation: [Link to extended docs]
