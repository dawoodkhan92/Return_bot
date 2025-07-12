# Use Python 3.9 as specified in railway.json
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt from root directory
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Set the working directory to the root for the start command
WORKDIR /app

# Expose port (Railway will set the PORT environment variable)
EXPOSE $PORT

# Use Railway's PORT environment variable instead of hardcoded port
CMD ["sh", "-c", "hypercorn main:app --bind 0.0.0.0:$PORT"] 