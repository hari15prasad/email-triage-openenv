FROM python:3.11-slim

# Metadata
LABEL maintainer="email-triage-openenv"
LABEL description="Email Triage OpenEnv — real-world email triage environment for AI agents"
LABEL version="1.0.0"

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user (non-root)
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy and install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY email_triage_env/ ./email_triage_env/
COPY openenv.yaml .
COPY inference.py .

# Change ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (HF Spaces uses 7860)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Environment variables with sensible defaults
ENV HOST=0.0.0.0
ENV PORT=7860
ENV WORKERS=1

# Start the FastAPI server
CMD ["uvicorn", "email_triage_env.server:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
