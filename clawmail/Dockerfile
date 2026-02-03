FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY clawmail/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY clawmail/lib/ ./lib/
COPY clawmail/scripts/ ./scripts/

# Create data directory for SQLite
RUN mkdir -p /data

# Set environment defaults
ENV CLAWHUB_DB=/data/clawhub.db
ENV CLAWHUB_RATE_LIMIT=60
ENV PYTHONUNBUFFERED=1

# Expose port (Railway sets PORT env var)
EXPOSE 5000

# Run with gunicorn
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 'scripts.server:app'"]
