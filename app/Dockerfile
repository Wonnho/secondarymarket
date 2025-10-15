# app/Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /usr/src/app

# Copy dependency file first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose your app port (example: 8000)
EXPOSE 8000

# Run the app
CMD ["python", "src/main.py"]
