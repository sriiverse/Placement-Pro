# Use the official Python image
FROM python:3.12-slim

# Hugging Face highly recommends running as a non-root user
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set working directory
WORKDIR $HOME/app

# Copy the backend files to the container
COPY --chown=user . $HOME/app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose port 7860 (This is strictly required by Hugging Face)
EXPOSE 7860

# Start the Flask backend using Gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:7860", "run:app"]
