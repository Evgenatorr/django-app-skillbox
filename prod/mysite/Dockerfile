FROM python:3.12-slim


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
# PYTHONDONTWRITEBYTECODE=1 Отключаем создание .pyc-файлов
# PYTHONUNBUFFERED=1 Отключаем буферизацию вывода (логи в реальном времени)

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-dev gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y pip setuptools
# pip uninstall -y pip setuptools  # Удаление ненужных компонентов после установки
COPY . .
