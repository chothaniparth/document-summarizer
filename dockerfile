# Base image
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Copy project files
COPY . /app

# Upgrade pip and install requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose ports
EXPOSE 8501 8000

# Default command (can be overridden in docker-compose)
CMD ["bash", "start_app.sh"]
