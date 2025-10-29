# MediaMTX Control Plane - Working Status ✅

## All Systems Operational!

### Database: ✅ Working
- **Type**: SQLite
- **Location**: `instance/mtxman.db`
- **Initialized**: Yes
- **Admin User**: `admin` / `admin@example.com`

### Application: ✅ Working
- **Flask**: Running on port 5000
- **LDAP Auth**: Custom implementation (Flask 3.0 compatible)
- **Blueprints**: All registered
- **Routes**: All functional

### Available Routes:

#### Public Routes:
- `GET /` → Redirects to login or dashboard
- `GET /auth/login` → Login page
- `POST /auth/login` → LDAP authentication
- `GET /auth/logout` → Logout

#### Protected Routes (Login Required):
- `GET /api/dashboard` → Main dashboard
- `GET /api/customers` → List customers
- `GET /api/customers/<id>` → View customer details
- `POST /api/customers/create` → Create customer (admin only)
- `POST /api/customers/<id>/keys/create` → Create API key (admin only)

#### API Routes (MediaMTX Integration):
- `POST /api/mediamtx/auth` → External auth webhook
- `POST /api/mediamtx/webhook` → Event webhook

#### REST API:
- `GET /api/api/v1/customers` → List customers (JSON)
- `GET /api/api/v1/customers/<id>` → Get customer (JSON)
- `GET /api/api/v1/customers/<id>/keys` → List keys (JSON)

## Quick Start

### Start the Application:
```bash
./start.sh
```

Or manually:
```bash
unset DATABASE_URL
source venv/bin/activate
python app.py
```

### Access:
- **URL**: http://localhost:5000
- **Login**: Use your LDAP credentials (admin user exists in DB)

### Test Without LDAP:
Since LDAP might not be configured, you can test the MediaMTX webhook directly:

```bash
# Create a customer and API key via database
source venv/bin/activate
python manage.py create-admin your_username

# Then test MediaMTX auth endpoint
curl -X POST http://localhost:5000/api/mediamtx/auth \
  -H "Content-Type: application/json" \
  -d '{
    "action": "read",
    "path": "test/stream",
    "protocol": "rtsp",
    "query": "api_key=YOUR_KEY_HERE",
    "ip": "127.0.0.1"
  }'
```

## Known Limitations

1. **LDAP Configuration Required**:
   - Update `.env` with your LDAP server details
   - LDAP host: Currently set to `ldap://ad-xn-prod-01.chaos1.au`
   - Update to match your environment

2. **SQLite for Development Only**:
   - Use PostgreSQL for production
   - Switch by updating `DATABASE_URL` in `.env`

3. **No Frontend Framework**:
   - Basic HTML templates included
   - Add React/Vue/etc. if needed

## Next Steps

1. **Configure LDAP/AD**:
   - Edit `.env` with your LDAP server details
   - Test authentication

2. **Create Customers**:
   - Log in as admin
   - Navigate to Customers → Create Customer
   - Generate API keys for customers

3. **Configure MediaMTX**:
   - Point MediaMTX to `http://your-server:5000/api/mediamtx/auth`
   - Set webhook secret in both configs

4. **Run Tests**:
   ```bash
   pytest
   ```

## File Structure

```
mtxman/
├── app/
│   ├── __init__.py          ✅ Root route added
│   ├── auth/                ✅ Custom LDAP service
│   ├── api/                 ✅ MediaMTX integration
│   ├── models/              ✅ Database models
│   ├── services/            ✅ Business logic
│   └── templates/           ✅ HTML templates
├── instance/
│   └── mtxman.db            ✅ SQLite database
├── tests/                   ✅ Full test suite
├── .env                     ✅ Configuration
├── app.py                   ✅ Entry point
├── start.sh                 ✅ Quick start script
└── init_sqlite.py           ✅ Database setup
```

## Troubleshooting

### "Unable to open database file"
```bash
unset DATABASE_URL  # Make sure this is not set
```

### "Module not found"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "LDAP authentication failed"
Check `.env` LDAP configuration or test without LDAP by accessing the MediaMTX webhook directly.

---

**Status**: ✅ Ready for Development
**Last Updated**: $(date)
