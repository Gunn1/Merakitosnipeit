sudo docker build -t merakitosnipeit-cron:latest .
docker run --env-file .env merakitosnipeit-cron:latest
