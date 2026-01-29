# Rocket Drop Zone Analysis - Deployment Guide

## Оглавление
- [Локальная разработка](#локальная-разработка)
- [Docker Deployment](#docker-deployment)
- [Проблемы и решения](#проблемы-и-решения)
- [API Документация](#api-документация)

---

## Локальная разработка

### Требования
- Python 3.12+
- Node.js 20+
- npm или yarn

### Запуск бэкенда

#### Вариант 1: Системный Python (рекомендуется для Windows)
```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
C:\Users\vladi\AppData\Local\Programs\Python\Python312\python.exe -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Вариант 2: Виртуальное окружение
```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (Linux/Mac)
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Вариант 3: Через run_server.py
```bash
python run_server.py
```

**Примечание**: Если используется `uv` Python, убедитесь, что зависимости установлены в правильное окружение.

### Запуск фронтенда

```bash
# Переход в директорию GUI
cd gui

# Установка зависимостей (только первый раз)
npm install

# Запуск dev-сервера
npm run dev
```

Фронтенд будет доступен по адресу: http://localhost:5173

### Проверка работоспособности

1. **Backend Health Check**:
   ```bash
   curl http://localhost:8000/api/health
   ```
   Ожидаемый ответ: `{"status":"ok","version":"1.0.0"}`

2. **Frontend**: Откройте http://localhost:5173 в браузере
   - Статус должен показывать "IDLE" (не "DEMO")
   - Это означает, что фронтенд успешно подключился к бэкенду

3. **Запуск симуляции**: Нажмите "INITIATE SIMULATION"
   - Статус изменится на "COMPUTING"
   - В консоли бэкенда будут видны логи прогресса

---

## Docker Deployment

### Требования
- Docker 20.10+
- Docker Compose 2.0+

### Быстрый старт

#### Production (с Nginx)
```bash
# Сборка и запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

Приложение будет доступно:
- Frontend: http://localhost
- Backend API: http://localhost:8000

#### Development (с hot-reload)
```bash
# Запуск в режиме разработки
docker-compose --profile dev up -d

# Это запустит:
# - backend с volume-маунтингом для hot-reload
# - frontend-dev с Vite dev server
```

Приложение будет доступно:
- Frontend Dev: http://localhost:5173
- Backend API: http://localhost:8000

### Управление контейнерами

```bash
# Остановка всех сервисов
docker-compose down

# Остановка с удалением volumes
docker-compose down -v

# Пересборка образов
docker-compose build

# Пересборка без кэша
docker-compose build --no-cache

# Просмотр логов конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend

# Вход в контейнер
docker-compose exec backend bash
docker-compose exec frontend sh
```

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
# Google Earth Engine (опционально)
EE_ACCOUNT=your-account@example.com
EE_PRIVATE_KEY=path/to/private-key.json
EE_TOKEN=your-token

# Backend
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1

# Frontend
VITE_API_URL=http://localhost:8000
```

### Архитектура Docker

```
┌─────────────────────────────────────────┐
│           Nginx (Frontend)              │
│         Port 80 → Container 80          │
│                                         │
│  - Serves static React app              │
│  - Proxies /api/* to backend            │
│  - Gzip compression                     │
│  - Cache static assets                  │
└────────────┬────────────────────────────┘
             │
             │ /api/* proxy
             ↓
┌─────────────────────────────────────────┐
│        FastAPI (Backend)                │
│       Port 8000 → Container 8000        │
│                                         │
│  - REST API endpoints                   │
│  - Monte Carlo simulation               │
│  - Background job processing            │
│  - Health checks                        │
└─────────────────────────────────────────┘
```

### Health Checks

Docker Compose включает health checks для обоих сервисов:

- **Backend**: `curl -f http://localhost:8000/api/health`
- **Frontend**: `wget --spider http://localhost/`

Проверка статуса:
```bash
docker-compose ps
```

Здоровые контейнеры покажут статус `healthy`.

---

## Проблемы и решения

### Проблема: ModuleNotFoundError: No module named 'uvicorn'

**Причина**: Python использует другое окружение (например, uv Python вместо системного).

**Решение**:
```bash
# Используйте полный путь к системному Python
C:\Users\vladi\AppData\Local\Programs\Python\Python312\python.exe -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Или установите зависимости в текущее окружение
pip install -r requirements.txt
```

### Проблема: Фронтенд показывает "DEMO" вместо "IDLE"

**Причина**: Фронтенд не может подключиться к бэкенду.

**Решение**:
1. Убедитесь, что бэкенд запущен на порту 8000
2. Проверьте health endpoint: `curl http://localhost:8000/api/health`
3. Проверьте CORS настройки в `api/main.py`

### Проблема: Белый экран после завершения симуляции

**Причина**: Браузер зависает при рендеринге большого количества данных (36K+ ячеек).

**Временное решение**:
- Уменьшите количество итераций (100 вместо 500+)
- Увеличьте размер ячейки сетки в `server_pipeline/simulation.py`

**Долгосрочное решение** (TODO):
- Реализовать виртуализацию рендеринга
- Добавить пагинацию для больших датасетов
- Использовать WebGL для рендеринга карты

### Проблема: Docker build fails на Windows

**Причина**: Проблемы с line endings (CRLF vs LF).

**Решение**:
```bash
# Конвертировать line endings
git config core.autocrlf input
git rm --cached -r .
git reset --hard
```

### Проблема: Конфликты зависимостей

**Причина**: Несовместимые версии пакетов (например, aider-chat требует numpy==1.26.4, но установлен 2.3.5).

**Решение**:
```bash
# Создайте чистое виртуальное окружение
python -m venv venv_clean
venv_clean\Scripts\activate
pip install -r requirements.txt
```

---

## API Документация

### Endpoints

#### Health Check
```http
GET /api/health
```

**Response**:
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

#### Run Simulation
```http
POST /api/simulation/run
Content-Type: application/json

{
  "iterations": 100,
  "use_gpu": true,
  "launch_lat": 45.72341,
  "launch_lon": 63.32275,
  "azimuth": 45.0
}
```

**Response**:
```json
{
  "job_id": "0223099f",
  "status": "running",
  "progress": 0
}
```

#### Get Simulation Status
```http
GET /api/simulation/status/{job_id}
```

**Response**:
```json
{
  "job_id": "0223099f",
  "status": "running",
  "progress": 75,
  "message": "Generating ecological grid..."
}
```

#### Get Results
```http
GET /api/results/{job_id}
```

**Response**:
```json
{
  "job_id": "0223099f",
  "status": "completed",
  "progress": 100,
  "primary_ellipse": {
    "center_lat": 48.0,
    "center_lon": 66.5,
    "semi_major_km": 186.3,
    "semi_minor_km": 58.0,
    "angle_deg": 45.0
  },
  "fragment_ellipse": { ... },
  "impact_points": { "type": "FeatureCollection", ... },
  "otu_grid": { "type": "FeatureCollection", ... },
  "stats": {
    "iterations": 100,
    "simulation_time_s": 1.86,
    "primary_impacts": 100,
    "fragment_impacts": 394,
    "grid_cells": 36326
  }
}
```

### Interactive API Documentation

После запуска бэкенда, документация доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Производительность

### Результаты тестирования

| Итерации | Время симуляции | Primary | Fragments | Grid Cells | Общее время |
|----------|----------------|---------|-----------|------------|-------------|
| 100      | 1.86s          | 100     | 394       | 36,326     | 25.5s       |
| 500      | 0.00s*         | 500     | 1,958     | 35,896     | 0.6s        |

*Использование CPU parallel (Numba, 12 потоков)

### Оптимизация

1. **GPU Acceleration**: Автоматически используется Numba для параллелизации
2. **Grid Generation**: GPU-оптимизированный генератор сетки
3. **Outlier Filtering**: IQR-фильтрация для удаления выбросов
4. **GeoJSON Conversion**: Оптимизированная конвертация больших датасетов

---

## Мониторинг

### Логи

```bash
# Все логи
docker-compose logs -f

# Только backend
docker-compose logs -f backend

# Последние 100 строк
docker-compose logs --tail=100 backend
```

### Метрики

Health checks автоматически проверяют:
- Backend: доступность API
- Frontend: доступность веб-сервера
- Интервал: каждые 30 секунд

---

## Поддержка

Для вопросов и проблем:
1. Проверьте раздел "Проблемы и решения"
2. Просмотрите логи: `docker-compose logs -f`
3. Создайте issue в репозитории

---

**Версия**: 2.0.0  
**Последнее обновление**: 2026-01-29  
**Автор**: vel5id
