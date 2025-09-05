# Ubuntu-based image for web terminal
FROM ubuntu:24.04

# Install Python, pip, and other essentials
RUN apt-get update && \
    apt-get install -y python3 python3-pip bash curl && \
    apt-get clean

# Set workdir
WORKDIR /app

# Copy app files
COPY app/ /app/
COPY static/ /app/static/

# Install Python dependencies
RUN pip3 install fastapi uvicorn websockets

# Expose port for FastAPI
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
