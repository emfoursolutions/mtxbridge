# Quick Start Guide - SQLite Edition

Get up and running in under 2 minutes with no external database!

## Prerequisites

- Python 3.11+
- That's it!

## Installation Steps

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements-dev.txt
```

### 2. Initialize Database

```bash
python init_sqlite.py
```

This will:
- Create the SQLite database at `instance/mtxman.db`
- Set up all tables
- Optionally create an admin user

When prompted:
- Enter your username (should match your LDAP/AD username if using LDAP)
- Enter your email
- Enter your display name

### 3. Run the Application

```bash
python app.py
```

Or use make:
```bash
make run
```

### 4. Access the Application

Open your browser to: **http://localhost:5000**

Log in with the credentials you just created!

## What's Next?

### Configure LDAP (Optional)

If you want to use real LDAP/AD authentication:

1. Edit `.env` file with your LDAP server details:
   ```bash
   LDAP_HOST=ldap://your-ad-server.example.com
   LDAP_BASE_DN=dc=example,dc=com
   LDAP_BIND_USER_DN=cn=service_account,dc=example,dc=com
   LDAP_BIND_USER_PASSWORD=your_password
   ```

2. Restart the app

### Create Your First Customer

1. Log in to http://localhost:5000
2. Click **Customers** → **Create Customer**
3. Fill in the details
4. Click **Create API Key** to generate a streaming key
5. Copy the API key (it's only shown once!)

### Test with MediaMTX

Use the API key to authenticate to MediaMTX streams:

```bash
# As query parameter
rtsp://localhost:8554/stream?api_key=mtx_your_key_here

# As username
rtsp://mtx_your_key_here@localhost:8554/stream

# As password
rtsp://user:mtx_your_key_here@localhost:8554/stream
```

## Troubleshooting

### "No module named 'app'"

Make sure you're in the project directory and virtual environment is activated.

### "Database is locked"

SQLite doesn't handle concurrent writes well. For production with multiple workers, use PostgreSQL:

```bash
# Switch to PostgreSQL
pip install -r requirements-postgres.txt

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/mtxman

# Initialize
python manage.py init-db
python manage.py create-admin your_username
```

### "Permission denied" on instance/mtxman.db

Make sure the `instance/` directory is writable:

```bash
chmod 755 instance/
chmod 644 instance/mtxman.db
```

## Database Location

Your SQLite database is stored at:
```
instance/mtxman.db
```

To reset everything:
```bash
rm instance/mtxman.db
python init_sqlite.py
```

## Switching to PostgreSQL Later

Already using SQLite but want to switch to PostgreSQL?

1. Install PostgreSQL driver:
   ```bash
   pip install psycopg2-binary
   ```

2. Update `.env`:
   ```bash
   DATABASE_URL=postgresql://user:password@localhost:5432/mtxman
   ```

3. Migrate your data (manual export/import) or start fresh:
   ```bash
   python manage.py init-db
   ```

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review test files in `tests/` for usage examples
- Open an issue on GitHub
