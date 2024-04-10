FROM python:3.9
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY ../../requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY ../.. /app
EXPOSE 8000
RUN apt-get update && apt install wait-for-it
ENTRYPOINT wait-for-it db:5432 -t 0 && python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000