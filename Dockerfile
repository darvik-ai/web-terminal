# Ubuntu-based image for web terminal
FROM ubuntu:24.04


# Install Python, pip, venv, and other essentials
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv bash curl && \
    apt-get clean

# Set workdir
WORKDIR /app

# Copy app files
COPY app/ /app/
COPY static/ /app/static/


# Set up Python virtual environment and install dependencies
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN /venv/bin/pip install --upgrade pip && /venv/bin/pip install fastapi uvicorn websockets

# Expose port for FastAPI
EXPOSE 8000

# Start the FastAPI server using the virtual environment
CMD ["/venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
