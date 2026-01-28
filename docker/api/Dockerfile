FROM python:3.11-slim

WORKDIR /app

COPY ../../requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ../../scrapers ./scrapers
COPY storage /app/storage

EXPOSE 8000
CMD ["uvicorn", "scrapers.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
