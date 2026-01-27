FROM ubuntu:22.04

LABEL author="Rowan AeroDefense"
LABEL description="Site Survey Tool with Web Interface"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/usr/lib/python3/dist-packages
WORKDIR /app

# Install system dependencies (including GNU Radio and UHD)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    libuhd-dev \
    uhd-host \
    gnuradio \
    libusb-1.0-0 \
    pkg-config \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install --no-cache-dir \
    "numpy<1.25.0" \
    scipy \
    matplotlib \
    flask \
    pyserial 

# Download UHD images (needed for USRP operation)
RUN uhd_images_downloader

# Copy the application code
# We copy the whole context to /app, assuming SiteSurveyTool is a subdirectory
COPY . /app

# Expose port for Flask
EXPOSE 5000

# Set working directory to where the scripts are
WORKDIR /app/SiteSurveyTool

# Default command
CMD ["python3", "web_interface.py"]
