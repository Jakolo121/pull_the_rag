# Start with Alpine-based Python image for a minimal footprint
FROM python:3.12-alpine

# Add comprehensive labels for better container identification
LABEL org.opencontainers.image.title="Pull The Rag" \
    org.opencontainers.image.description="RAG application for document processing" \
    org.opencontainers.image.version="1.0.0" \
    com.docker.desktop.extension.name="Pull The Rag" \
    maintainer="i22y"

# Set working directory
WORKDIR /app

# Install system dependencies and build requirements
# We separate this into multiple logical groups for clarity
RUN apk update && \
    # First group: Basic build tools and Python development
    apk add --no-cache \
    build-base \
    python3-dev \
    py3-pip \
    git \
    # Required for PyMuPDF
    musl-dev \
    linux-headers \
    # MuPDF dependencies
    mupdf-dev \
    jpeg-dev \
    openjpeg-dev \
    zlib-dev \
    freetype-dev \
    # Additional build requirements
    gcc \
    g++ \
    make \
    cmake \
    pkgconfig \
    # Clean up cache to reduce image size
    && rm -rf /var/cache/apk/* \
    # Create necessary directories
    && mkdir -p /app/uploads /app/logs \
    && chmod 755 /app/uploads /app/logs

# Copy requirements file separately to leverage Docker cache
COPY requirements.txt .

# Set environment variables for PyMuPDF build
ENV PYMUPDF_SETUP_MUPDF_BUILD=1

# Install Python dependencies with specific considerations for PyMuPDF
RUN pip install --no-cache-dir --upgrade pip && \
    # Install wheel first to ensure proper building
    pip install --no-cache-dir wheel && \
    # Install PyMuPDF separately first
    pip install --no-cache-dir PyMuPDF && \
    # Then install the rest of the requirements
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set only the non-sensitive environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

# Create a non-root user for security
RUN adduser -D appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port the application runs on
EXPOSE 8000

# Health check to ensure application is running properly
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1

# Command to run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]