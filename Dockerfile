# Use an official Python runtime as base
FROM python:3.12.3-alpine

# Set working directory inside container
WORKDIR /usr/src/app

# Copy requirements first (for caching layers)
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY app ./app

# Expose port (for WebSocket/HTTP server)
EXPOSE 7890
EXPOSE 8081

# Command to run your server
# Adjust if you’re using Flask, FastAPI, or a custom WebSocket loop
CMD ["python", "-m", "app.main"]