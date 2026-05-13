# Use the official Python image
FROM python:3.12-slim

# Security best practice: run as non-root user
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set working directory
WORKDIR $HOME/app

# Copy dependency file first (maximises Docker layer caching)
COPY --chown=user requirements.txt .

# Install dependencies in a single layer
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code
COPY --chown=user . .

# Expose both ports:
#   7860 → HuggingFace Spaces (required)
#   5000 → local Docker / docker-compose
EXPOSE 7860 5000

# Health check — longer start-period gives the container time to boot fully
HEALTHCHECK --interval=30s --timeout=10s --start-period=180s --retries=5 \
    CMD python -c "import urllib.request, os; port = os.environ.get('PORT', 7860); urllib.request.urlopen('http://localhost:' + str(port) + '/health')"

# PORT defaults to 7860 for HuggingFace Spaces.
# Override with PORT=5000 in docker-compose.yml for local dev.
ENV PORT=7860
CMD gunicorn \
    --workers 1 \
    --bind "0.0.0.0:${PORT}" \
    --timeout 120 \
    --log-level info \
    --access-logfile - \
    --error-logfile -\
    run:app

