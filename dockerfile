# Use Python 3.10 as the base image for broad compatibility
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system dependencies (if needed for pandas, yfinance, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY mcp-server/requirements.txt ./requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install pandas pandas_ta

# Copy the rest of the code
COPY mcp-server/ ./mcp-server/

# Expose the port the server runs on
EXPOSE 3001

# Set the default command to run the server
CMD ["python", "./mcp-server/yf_server.py"]