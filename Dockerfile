FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir httpx2

COPY src/ /app/src/

RUN mkdir -p /data
ENV TZ=Europe/Warsaw
ENV SVCDESK_DB=/data/svcdesk.db

EXPOSE 8080
CMD ["uvicorn", "svcdesk.main:app", "--app-dir", "/app/src", "--host", "0.0.0.0", "--port", "8080"]
