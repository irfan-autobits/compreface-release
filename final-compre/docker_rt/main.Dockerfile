# Use an NVIDIA base image with PyTorch and CUDA support.
# This image comes pre-installed with CUDA and is optimized for GPU use.
FROM nvcr.io/nvidia/tensorrt:23.03-py3

ENV PATH=/opt/conda/bin:$PATH

RUN apt-get update --fix-missing && \
    apt-get install -y wget bzip2 ca-certificates curl git build-essential libpq-dev python3-dev ffmpeg && \
    # libsm6 libxext6 libxrender-dev \    
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Miniconda if not already available
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && \
    bash miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh && \
    /opt/conda/bin/conda clean -a -y && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh

# Create working directory
WORKDIR /app

# Copy the environment file
COPY environment.yml /app/environment.yml

# Create the conda environment from the file
RUN conda env create -f environment.yml

# Use the conda environment for subsequent commands
# SHELL ["conda", "run", "-n", "tensorruntime", "/bin/bash", "-c"]

# Copy your application code into the container
COPY . /app

# Pre-download models
# RUN python3 -c "from storage import ensure_available; ensure_available('models', 'buffalo_l', root='/root/.insightface')"

# Expose the port your Flask/SocketIO app uses
EXPOSE 5757

# Set the entrypoint to run your application
CMD ["conda", "run", "-n", "tensorruntime", "python", "run.py"]
# CMD ["python", "run.py"]