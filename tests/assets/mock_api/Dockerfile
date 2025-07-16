# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the necessary files into the container
COPY main.py data.json /app/

# Install required Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastapi uvicorn

# Expose the port FastAPI will run on
EXPOSE 5000
