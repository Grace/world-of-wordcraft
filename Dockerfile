FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/app
COPY web/ /app/web

EXPOSE 5001
CMD CMD ["python", "-m", "app.main"]
