FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system deps (optional: needed if you use things like Pillow, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port for EB or Docker testing
EXPOSE 5000

# Start app with Gunicorn, binding to 0.0.0.0:PORT
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:application"]
