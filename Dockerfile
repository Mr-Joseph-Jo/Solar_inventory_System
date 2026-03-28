FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Create invoices directory
RUN mkdir -p invoices

EXPOSE 5000

# Use gunicorn for production
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "--timeout=60", "app:app"]
