# Use a Python base image
FROM python:3.11-slim


# Set the working directory
WORKDIR /app

# Copy the project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron

# Add the cron job
RUN echo "0 * * * * python /app/main.py >> /app/logs/cron.log 2>&1" > /etc/cron.d/snipeit_cron

# Apply cron job
RUN chmod 0644 /etc/cron.d/snipeit_cron && crontab /etc/cron.d/snipeit_cron

# Create a logs directory
RUN mkdir -p /app/logs

# Start cron and keep the container running
CMD ["cron", "-f"]
