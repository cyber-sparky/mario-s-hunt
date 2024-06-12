# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN apt-get update && apt-get install default-libmysqlclient-dev build-essential pkg-config -y \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 5000 for the Flask app
EXPOSE 5000

# Set environment variables
ENV FLASK_RUN_HOST=0.0.0.0

# Command to run the Flask app
CMD ["python3", "app/app.py"]
