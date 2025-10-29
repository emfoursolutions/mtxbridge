# ABOUTME: Multi-stage Docker build for MediaMTX control plane Flask app
# ABOUTME: Creates optimized production-ready container image

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libldap2-dev \
    libsasl2-dev \
    && rm -rf /var/lib/apt/lists/*

# Development stage
FROM base as development

COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

COPY . .

CMD ["python", "app.py"]

# Production stage
FROM base as production

# Create non-root user
RUN useradd -m -u 1000 mtxman && \
    chown -R mtxman:mtxman /app

# Install production dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt && \
    pip install gunicorn

# Copy application code
COPY --chown=mtxman:mtxman . .

# Switch to non-root user
USER mtxman

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "60", "wsgi:app"]
