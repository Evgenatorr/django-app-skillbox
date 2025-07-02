FROM python:3.12-slim


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
# PYTHONDONTWRITEBYTECODE=1 Отключаем создание .pyc-файлов
# PYTHONUNBUFFERED=1 Отключаем буферизацию вывода (логи в реальном времени)

WORKDIR /app

RUN pip install --upgrade pip "poetry==2.0.0"
RUN poetry config virtualenvs.create false --local
COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY . .
