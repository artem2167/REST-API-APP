FROM python:3.10-slim
WORKDIR /app

# Установим postgresql-client для pg_isready
RUN apt-get update && apt-get install -y postgresql-client
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
