FROM python:3-alpine
COPY ./app /app
WORKDIR /app
RUN pip install --upgrade pip && ls -lisa /app && pip install -r /app/requirements.txt --no-cache-dir
CMD gunicorn -w 4 --bind 0.0.0.0:5000 wsgi:app
