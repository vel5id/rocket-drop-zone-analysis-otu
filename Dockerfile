# Rocket Drop Zone Analysis OTU - Dockerfile
# Ссылка на спецификацию: infrastructure/docker из требований проекта

FROM python:3.10-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgdal-dev \
    libspatialindex-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml ./

# Установка Python зависимостей
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ".[dev]" && \
    pip install --no-cache-dir earthengine-api

# Копирование исходного кода
COPY . .

# Создание директорий для выходных данных
RUN mkdir -p output outputs logs

# Настройка переменных окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV EE_ACCOUNT=""
ENV EE_PRIVATE_KEY=""
ENV EE_TOKEN=""

# Команда по умолчанию
CMD ["python", "main.py"]

# Метки
LABEL maintainer="vel5id"
LABEL version="1.0.0"
LABEL description="Monte Carlo simulation toolkit for rocket stage drop zones analysis"