FROM arm64v8/ubuntu:22.04

# Install dependencies and Python packages
RUN apt-get update && apt-get install -y \
    python3-pip \
    ffmpeg \
    git \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip

COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install -r /requirements.txt

# Set working directory for the container
WORKDIR /workspace

# Set the entrypoint
ENTRYPOINT ["exec "$@""]
CMD ["bash"]