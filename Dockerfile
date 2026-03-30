FROM python:3.11-slim

WORKDIR /app

# Install curl for Docker healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Copy entrypoint and make it executable
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Create a non-root user and switch to it for security
RUN umask 0002 && \
    useradd -m botuser && \
    chown -R botuser:botuser /app

USER botuser

# Expose web port
EXPOSE 8000

# Run the application via entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "main.py"]
