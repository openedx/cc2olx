FROM python:3.11.10-alpine3.20

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir /app

ENTRYPOINT ["cc2olx"]
