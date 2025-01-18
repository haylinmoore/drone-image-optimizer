# Build ECT in separate stage
FROM python:3.11-slim AS ect-builder
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    build-essential \
    nasm \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --recursive https://github.com/fhanau/Efficient-Compression-Tool.git \
    && cd Efficient-Compression-Tool \
    && mkdir build \
    && cd build \
    && cmake ../src \
    && make -j$(nproc)

# Main image
FROM python:3.11-slim

# Install all required packages
RUN apt-get update && apt-get install -y \
    pngquant \
    jpegoptim \
    webp \
    libwebp-dev \
    libwebpdemux2 \
    libjpeg62-turbo \
    libpng16-16 \
    gifsicle \
    && rm -rf /var/lib/apt/lists/*

# Copy ECT from builder
COPY --from=ect-builder /Efficient-Compression-Tool/build/ect /usr/local/bin/

# Setup app
WORKDIR /app
COPY optimize.py /app/
RUN chmod +x /app/optimize.py

ENTRYPOINT ["python3", "/app/optimize.py"]
