FROM python:3.9.5-slim-buster as base
LABEL maintainer "Andrew Bilenduke <andrewbilenduke@gmail.com>"

RUN apt-get update

ENV APP_ROOT="/var/www/flask_backend"
ENV FLASK_APP="${APP_ROOT}/wsgi.py"

WORKDIR ${APP_ROOT}

COPY ./requirements.txt ./requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# DEBUG BUILD
FROM base as development

RUN pip install debugpy

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 5678

CMD [ "python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "flask", "run", "-h", "0.0.0.0", "-p", "5000" ]

# PRODUCTION BUILD
FROM base as production
RUN pip install gunicorn
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
