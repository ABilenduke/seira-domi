FROM python:3.9.5-slim-buster

ENV APP_ROOT /var/www/flask_backend

WORKDIR ${APP_ROOT}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# ENTRYPOINT ["${APP_ROOT}/entrypoint.sh"]
# ENTRYPOINT ["/var/www/flask_backend/entrypoint.sh"]
