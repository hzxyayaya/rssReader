# Backend Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (needed for compilation sometimes)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
# Note: Since app/ is in root, we copy the specific directories or just the app folder.
# Assuming build context is project root.
COPY app ./app

# Expose port
EXPOSE 8000

# Run command
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
