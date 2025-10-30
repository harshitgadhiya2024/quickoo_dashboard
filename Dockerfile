FROM ubuntu:22.04

# Set environment variables to prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies including sudo, git, vim, nano, and Python
RUN apt-get update && apt-get install -y \
    sudo \
    git \
    vim \
    nano \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic links for python and pip (force overwrite if exists)
RUN ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# Copy your application code
COPY . /app

# Install Flask and other dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV NAME=World

# Run the Flask server
CMD ["python", "main.py"]