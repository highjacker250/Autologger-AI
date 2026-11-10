FROM mcr.microsoft.com/playwright/python:v1.41.2-jammy

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Make start.sh executable
RUN chmod +x start.sh

# Expose port (Render sets PORT env var)
EXPOSE 8080

# Run the start script
CMD ["./start.sh"]
