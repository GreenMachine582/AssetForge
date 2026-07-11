FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATA_PATH=/app/data \
    HOST=0.0.0.0 \
    PORT=8000

EXPOSE 8000

# Shell form so $HOST/$PORT are expanded at container start, letting
# --env-file/-e or docker-compose's env_file override the ENV defaults above.
CMD uvicorn main:app --host ${HOST} --port ${PORT}
