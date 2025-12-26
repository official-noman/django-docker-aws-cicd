# Base Image
FROM python:3.9-slim

# Working Directory
WORKDIR /app

# Install System Dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Project Code
COPY . .

# Expose Port
EXPOSE 8000

# Default Command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi:application"] 
#nginx er rqst django rcv kore ekhane gunicorn diye
