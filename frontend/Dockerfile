# Frontend Dockerfile - Streamlit
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency file first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "finance.py", "--server.port=8501", "--server.address=0.0.0.0"]
