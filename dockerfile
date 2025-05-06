FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Install cron
RUN apt-get update && \
    apt-get install -y cron && \
    apt-get clean

# Copy your app
COPY . /app

# Create logs directory
RUN mkdir -p /app/logs

# Add cron job
RUN echo "0 * * * * /usr/local/bin/python /app/main.py >> /app/logs/cron.log 2>&1" > /etc/cron.d/merakitosnipeit

# Set permissions
RUN chmod 0644 /etc/cron.d/merakitosnipeit

# Apply cron job
RUN crontab /etc/cron.d/merakitosnipeit

# Ensure the cron logs work
RUN touch /app/logs/cron.log

# Run cron in the foreground
CMD ["cron", "-f"]

