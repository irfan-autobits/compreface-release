FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV CUDA=11.8
ENV TF_FORCE_GPU_ALLOW_GROWTH=true

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    software-properties-common \
    curl \
    pkg-config \
    unzip \
    python3-dev \
    python3-distutils \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Ensure Python uses pip3
RUN ln -s $(which python3) /usr/local/bin/python

# Upgrade pip and install required packages
RUN python -m pip --no-cache-dir install --upgrade pip setuptools wheel

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# MXNet CUDA Optimization
ENV MXNET_ENGINE_TYPE=ThreadedEnginePerDevice
ENV MXNET_CUDNN_AUTOTUNE_DEFAULT=0

# Copy source code
COPY . /app
WORKDIR /app

# Expose required ports
EXPOSE 8000  

# Run the application
CMD ["python3", "run.py"]
