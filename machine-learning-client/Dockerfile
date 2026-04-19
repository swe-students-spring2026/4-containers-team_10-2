FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY .env ./.env

EXPOSE 5001

CMD ["python", "-m", "app.server"]
