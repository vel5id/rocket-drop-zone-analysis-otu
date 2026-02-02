### 🇬🇧 English
[EN]
# 🛠️ Rocket Drop Zone Analysis (OTU) System - Technical Documentation

## 📋 Document Purpose

This file contains the complete technical documentation for the Rocket Drop Zone Analysis (OTU) system. It is intended for developers, engineers, DevOps specialists, and anyone interacting with the deployment, support, or extension of the system.

**Relation to other documents:**
- For a general overview, see [README_OVERVIEW.md](README_OVERVIEW.md)
- For scientific methodology, see [README_SCIENCE.md](README_SCIENCE.md)
- For economic analysis, see [README_ECONOMICS.md](README_ECONOMICS.md)
- For development and contribution, see [README_DEVELOPMENT.md](README_DEVELOPMENT.md)

[⬅️ Back to Main README](./README.md)

---

## 🏗️ System Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer (Frontend)"
        Browser[Web Browser]
        ReactApp[React Application]
        MapUI[Leaflet Map UI]
    end
    
    subgraph "Server Layer (Backend)"
        API[FastAPI REST API]
        
        subgraph "Business Logic"
            Sim[Monte Carlo Simulator]
            Grid[Grid Generator]
            Eco[Economic Calculator]
            Export[Export Service]
        end
        
        subgraph "Integrations"
            GEE[Google Earth Engine Client]
            Geo[Geospatial Libraries]
        end
        
        subgraph "Data Storage"
            Cache[Redis/In-memory Cache]
            FS[File System]
            DB[(PostgreSQL/GeoDB)]
        end
    end
    
    Browser --> ReactApp
    ReactApp --> MapUI
    ReactApp --> API
    API --> Sim
    API --> Grid
    API --> Eco
    API --> Export
    Sim --> Cache
    Grid --> Geo
    Eco --> GEE
    Export --> FS
```

### Component Architecture

| Component | Technologies | Purpose |
|-----------|--------------|---------|
| **API Gateway** | FastAPI, Uvicorn, Pydantic | Single entry point for all requests, validation, routing |
| **Monte Carlo Engine** | NumPy, SciPy, Numba | Execution of stochastic trajectory simulations |
| **Grid Generator** | GeoPandas, Shapely, PyProj | Creation of spatial grid within the dispersion ellipse |
| **Economic Calculator** | Pandas, NumPy | Calculation of reclamation costs and damages |
| **Google Earth Engine Client** | earthengine-api, geemap | Retrieval and processing of satellite data |
| **Frontend Application** | React, Vite, Leaflet | User interface with interactive map |
| **Export Service** | Pandas, GeoPandas, ReportLab | Generation of reports in CSV, GeoJSON, PDF formats |

---

## 📦 Technology Stack

### Backend (Python 3.10+)

#### Core Dependencies
```yaml
# requirements.txt (key components)
earthengine-api:      # Google Earth Engine integration
geopandas:           # Geospatial operations
shapely:             # Geometric primitives
pyproj:              # Coordinate transformations
rasterio:            # Raster data handling
numpy:               # Scientific computing
scipy:               # Statistics and optimization
numba:               # JIT compilation for performance
fastapi:             # Web framework
uvicorn:             # ASGI server
```

#### Utility Libraries
```yaml
pandas:              # Tabular data processing
xarray:              # Multi-dimensional arrays
h5py:                # Large data storage
tqdm:                # Progress bars
requests:            # HTTP client
pyyaml:              # Configuration files
python-multipart:    # File uploads
```

### Frontend (JavaScript/TypeScript)

#### Core Dependencies
```json
{
  "react": "^18.2.0",        // UI library
  "react-dom": "^18.2.0",    // Rendering
  "vite": "^5.0.0",          // Build and dev server
  "leaflet": "^1.9.4",       // Interactive maps
  "react-leaflet": "^4.2.1", // React integration for Leaflet
  "axios": "^1.6.0",         // HTTP client
  "recharts": "^2.10.0",     // Charts and graphs
  "tailwindcss": "^3.3.0"    // CSS framework
}
```

### Infrastructure
```yaml
Docker:              # Containerization
Docker Compose:      # Container orchestration
PostgreSQL:          # Database (with PostGIS)
Redis:               # Caching
Nginx:               # Reverse proxy
```

---

## 🚀 Installation and Setup

### Prerequisites

#### System Requirements
- **OS**: Linux (Ubuntu 20.04+), Windows 10/11, macOS 12+
- **Memory**: 8 GB RAM minimum (16 GB recommended)
- **Disk**: 10 GB free space
- **Processor**: 4+ cores

#### Software
- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **Docker 24+** and Docker Compose (optional)
- **Git** for version control

### Option 1: Installation via Docker (Recommended)

#### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/rocket-drop-zone-analysis.git
cd rocket-drop-zone-analysis
```

#### Step 2: Configure Environment Variables
```bash
cp .env.example .env
# Edit .env file
nano .env
```

#### Step 3: Run via Docker Compose
```bash
docker-compose up -d
```

#### Step 4: Verify Operation
```bash
# Check logs
docker-compose logs -f

# Check service availability
curl http://localhost:8000/health
```

### Option 2: Manual Installation (For Development)

#### Backend Installation
```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure Google Earth Engine
earthengine authenticate

# 4. Configure database (optional)
python scripts/init_db.py

# 5. Run server
python run_server.py
```

#### Frontend Installation
```bash
# 1. Navigate to frontend directory
cd gui

# 2. Install dependencies
npm install

# 3. Configure environment variables
cp .env.example .env.local

# 4. Run dev server
npm run dev
```

### Configuration

#### Main Configuration Files

**config/settings.yaml**
```yaml
app:
  name: "Rocket Drop Zone Analysis"
  version: "1.0.0"
  debug: false

simulation:
  monte_carlo_iterations: 1000
  max_cells: 50000
  iqr_filter: true
  iqr_multiplier: 1.5

geospatial:
  default_crs: "EPSG:4326"
  working_crs: "EPSG:3857"
  cell_size_km: 1.0

economic:
  currency: "USD"
  default_rates:
    fire_restoration: 5000
    soil_strength: 3000
    soil_quality: 4000
    vegetation: 8000

google_earth_engine:
  enabled: true
  collection: "COPERNICUS/S2_SR"
  max_cloud_cover: 20
```

**api/.env**
```env
# FastAPI settings
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_RELOAD=true

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/otu_db

# Cache
REDIS_URL=redis://localhost:6379/0

# Google Earth Engine
GEE_SERVICE_ACCOUNT=your-service-account@project.iam.gserviceaccount.com
GEE_PRIVATE_KEY_PATH=/path/to/private-key.json
```

---

## 🔌 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Main Endpoints

#### 1. Drop Zone Simulation
```http
POST /simulation/run
Content-Type: application/json

{
  "launch_site": {
    "lat": 45.965,
    "lon": 63.305,
    "name": "Baikonur"
  },
  "separation_params": {
    "altitude_km": 80.0,
    "velocity_mps": 2500.0,
    "flight_azimuth_deg": 45.0
  },
  "monte_carlo": {
    "iterations": 1000,
    "wind_std_dev": 15.0
  },
  "output_options": {
    "format": "geojson",
    "include_grid": true
  }
}
```

**Response:**
```json
{
  "simulation_id": "sim_abc123",
  "status": "completed",
  "ellipse": {
    "center": {"lat": 46.5, "lon": 64.2},
    "semi_major_km": 12.5,
    "semi_minor_km": 8.3,
    "rotation_deg": 25.0
  },
  "statistics": {
    "total_points": 1000,
    "filtered_points": 950,
    "area_km2": 325.7
  },
  "download_url": "/api/v1/simulation/sim_abc123/download"
}
```

#### 2. Get Satellite Data
```http
GET /gee/indices?lat=46.5&lon=64.2&radius_km=10&date=2024-01-01
```

#### 3. Economic Analysis
```http
POST /economic/calculate
Content-Type: application/json

{
  "grid_id": "grid_xyz789",
  "currency": "USD",
  "include_breakdown": true
}
```

#### 4. Export Results
```http
GET /export/{simulation_id}?format=csv
```

### Automatic Documentation

After starting the server, available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Specification**: `http://localhost:8000/openapi.json`

---

## 🐳 Deployment

### Docker Configuration

**Dockerfile.backend**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run application
CMD ["python", "run_server.py"]
```

**Dockerfile.frontend**
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY gui/package*.json ./
RUN npm ci

COPY gui/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: otu_db
      POSTGRES_USER: otu_user
      POSTGRES_PASSWORD: otu_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      - DATABASE_URL=postgresql://otu_user:otu_password@postgres:5432/otu_db
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "5173:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Cloud Platforms

#### AWS ECS/Fargate
```bash
# Build and push images
aws ecr create-repository --repository-name otu-backend
docker build -t otu-backend -f Dockerfile.backend .
docker tag otu-backend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/otu-backend:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/otu-backend:latest

# Deploy via CloudFormation/Terraform
```

#### Google Cloud Run
```bash
# Build with Cloud Build
gcloud builds submit --tag gcr.io/PROJECT_ID/otu-backend

# Deploy
gcloud run deploy otu-backend \
  --image gcr.io/PROJECT_ID/otu-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances
```bash
# Create container
az container create \
  --resource-group otu-rg \
  --name otu-backend \
  --image otu-backend:latest \
  --ports 8000 \
  --environment-variables DATABASE_URL=...
```

---

## 📊 Monitoring and Logging

### Prometheus Metrics
```python
# Example metric export
from prometheus_client import Counter, Histogram

SIMULATION_REQUESTS = Counter(
    'simulation_requests_total',
    'Total simulation requests',
    ['status']
)

SIMULATION_DURATION = Histogram(
    'simulation_duration_seconds',
    'Simulation duration in seconds',
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0]
)
```

### Logging
```yaml
# config/logging.yaml
version: 1
formatters:
  detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    formatter: detailed
    level: INFO
  file:
    class: logging.handlers.RotatingFileHandler
    filename: /var/log/otu/application.log
    maxBytes: 10485760  # 10MB
    backupCount: 5
    formatter: detailed
    level: DEBUG
loggers:
  otu:
    level: DEBUG
    handlers: [console, file]
    propagate: no
```

### Health Checks
```http
GET /health
```
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "gee": "authenticated"
  },
  "version": "1.0.0"
}
```

---

## 🔧 Troubleshooting

### Common Issues

#### Issue: GDAL Error
```
ERROR: Could not build wheels for gdal, which is required to install pyproject.toml-based projects
```
**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install gdal-bin libgdal-dev

# macOS
brew install gdal

# Windows: download wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
```

#### Issue: Google Earth Engine Authentication
```
EEException: Please authorize access to your Earth Engine account
```
**Solution:**
```bash
# Interactive authentication
earthengine authenticate

# Or via service account
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

#### Issue: Insufficient Memory for Simulation
```
MemoryError: Unable to allocate array with shape (100000, 2)
```
**Solution:**
1. Reduce Monte Carlo iterations.
2. Increase grid cell size.
3. Use `max_cells` parameter in configuration.

### Debugging

#### Enabling Detailed Logging
```bash
# Run with debug mode
python run_server.py --debug

# Or via environment variable
export OTU_LOG_LEVEL=DEBUG
```

#### Performance Profiling
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Execute code
run_simulation()

profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats(10)
```

---

## 📈 Scaling

### Horizontal Scaling
```yaml
# docker-compose.scale.yml
services:
  backend:
    image: otu-backend:latest
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://otu_user:otu_password@postgres:5432/otu_db
```

### Caching Strategy
```python
from redis import Redis
from functools import lru_cache

redis_client = Redis.from_url(REDIS_URL)

def get_cached_simulation(simulation_id: str):
    # Try getting from Redis
    cached = redis_client.get(f"simulation:{simulation_id}")
    if cached:
        return json.loads(cached)
    
    # Compute and cache
    result = compute_simulation(simulation_id)
    redis_client.setex(
        f"simulation:{simulation_id}",
        3600,  # TTL 1 hour
        json.dumps(result)
    )
    return result
```

### Load Balancing
```nginx
# nginx.conf
upstream backend_servers {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    
    location /api/ {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 🔗 Related Documents

For more information, refer to other project documents:

| Document | Target Audience | Key Content |
|----------|-----------------|-------------|
| [README_OVERVIEW.md](README_OVERVIEW.md) | General public, managers | Marketing overview, benefits, usage |
| [README_SCIENCE.md](README_SCIENCE.md) | Scientists, researchers | Mathematical models, physical principles |
| [README_ECONOMICS.md](README_ECONOMICS.md) | Economists, analysts | Damage assessment methodology, ROI analysis |
| [README_DEVELOPMENT.md](README_DEVELOPMENT.md) | Contributors | Contribution guide, testing |

---

## 📚 Additional Resources

- [Architectural Decision Records (ADR)](docs/adr/) - Documented architectural decisions
- [API Reference](docs/api/) - Complete API specification
- [Deployment Guides](docs/deployment/) - Deployment guides for various platforms
- [Performance Benchmarks](docs/benchmarks/) - Performance tests and comparisons

---

<div align="center">
    <br>
    <i>Technical documentation updated: January 2024</i>
    <br>
    © 2026 Rocket Drop Zone Analysis Team. All rights reserved.
</div>


### 🇷🇺 Русский
[RU]
# 🛠️ Rocket Drop Zone Analysis (OTU) System - Техническая документация

## 📋 Назначение документа

Этот файл содержит полную техническую документацию системы Rocket Drop Zone Analysis (OTU). Он предназначен для разработчиков, инженеров, DevOps-специалистов и всех, кто участвует в развертывании, поддержке или расширении системы.

**Связь с другими документами:**
- Для общего обзора см. [README_OVERVIEW.md](README_OVERVIEW.md)
- Для научной методологии см. [README_SCIENCE.md](README_SCIENCE.md)
- Для экономического анализа см. [README_ECONOMICS.md](README_ECONOMICS.md)
- Для разработки и вклада см. [README_DEVELOPMENT.md](README_DEVELOPMENT.md)
[⬅️ Назад](./README.md)
---

## 🏗️ Архитектура системы

### Высокоуровневая архитектура

```mermaid
graph TB
    subgraph "Клиентский слой (Frontend)"
        Browser[Веб-браузер]
        ReactApp[React Application]
        MapUI[Leaflet Map UI]
    end
    
    subgraph "Серверный слой (Backend)"
        API[FastAPI REST API]
        
        subgraph "Бизнес-логика"
            Sim[Монте-Карло симулятор]
            Grid[Генератор сетки]
            Eco[Экономический калькулятор]
            Export[Сервис экспорта]
        end
        
        subgraph "Интеграции"
            GEE[Google Earth Engine Client]
            Geo[Геопространственные библиотеки]
        end
        
        subgraph "Хранение данных"
            Cache[Redis/In-memory Cache]
            FS[Файловая система]
            DB[(PostgreSQL/GeoDB)]
        end
    end
    
    Browser --> ReactApp
    ReactApp --> MapUI
    ReactApp --> API
    API --> Sim
    API --> Grid
    API --> Eco
    API --> Export
    Sim --> Cache
    Grid --> Geo
    Eco --> GEE
    Export --> FS
```

### Компонентная архитектура

| Компонент | Технологии | Назначение |
|-----------|------------|------------|
| **API Gateway** | FastAPI, Uvicorn, Pydantic | Единая точка входа для всех запросов, валидация, маршрутизация |
| **Монте-Карло движок** | NumPy, SciPy, Numba | Выполнение стохастических симуляций траекторий |
| **Генератор сетки** | GeoPandas, Shapely, PyProj | Создание пространственной сетки внутри эллипса рассеивания |
| **Экономический калькулятор** | Pandas, NumPy | Расчет стоимости рекультивации и ущерба |
| **Google Earth Engine клиент** | earthengine-api, geemap | Получение и обработка спутниковых данных |
| **Фронтенд приложение** | React, Vite, Leaflet | Пользовательский интерфейс с интерактивной картой |
| **Сервис экспорта** | Pandas, GeoPandas, ReportLab | Генерация отчетов в CSV, GeoJSON, PDF форматах |

---

## 📦 Технологический стек

### Backend (Python 3.10+)

#### Основные зависимости
```yaml
# requirements.txt (ключевые компоненты)
earthengine-api:      # Google Earth Engine интеграция
geopandas:           # Геопространственные операции
shapely:             # Геометрические примитивы
pyproj:              # Преобразования координат
rasterio:            # Работа с растровыми данными
numpy:               # Научные вычисления
scipy:               # Статистика и оптимизация
numba:               # JIT-компиляция для производительности
fastapi:             # Веб-фреймворк
uvicorn:             # ASGI сервер
```

#### Вспомогательные библиотеки
```yaml
pandas:              # Обработка табличных данных
xarray:              # Многомерные массивы
h5py:                # Хранение больших данных
tqdm:                # Прогресс-бары
requests:            # HTTP клиент
pyyaml:              # Конфигурационные файлы
python-multipart:    # Загрузка файлов
```

### Frontend (JavaScript/TypeScript)

#### Основные зависимости
```json
{
  "react": "^18.2.0",        // UI библиотека
  "react-dom": "^18.2.0",    // Рендеринг
  "vite": "^5.0.0",          // Сборка и dev сервер
  "leaflet": "^1.9.4",       // Интерактивные карты
  "react-leaflet": "^4.2.1", // React интеграция Leaflet
  "axios": "^1.6.0",         // HTTP клиент
  "recharts": "^2.10.0",     // Графики и диаграммы
  "tailwindcss": "^3.3.0"    // CSS фреймворк
}
```

### Инфраструктура
```yaml
Docker:              # Контейнеризация
Docker Compose:      # Оркестрация контейнеров
PostgreSQL:          # База данных (с PostGIS)
Redis:               # Кэширование
Nginx:               # Reverse proxy
```

---

## 🚀 Установка и настройка

### Предварительные требования

#### Системные требования
- **ОС**: Linux (Ubuntu 20.04+), Windows 10/11, macOS 12+
- **Память**: 8 GB RAM минимум (16 GB рекомендуется)
- **Диск**: 10 GB свободного места
- **Процессор**: 4+ ядер

#### Программное обеспечение
- **Python 3.10+** с pip
- **Node.js 18+** с npm
- **Docker 24+** и Docker Compose (опционально)
- **Git** для контроля версий

### Вариант 1: Установка через Docker (рекомендуется)

#### Шаг 1: Клонирование репозитория
```bash
git clone https://github.com/your-org/rocket-drop-zone-analysis.git
cd rocket-drop-zone-analysis
```

#### Шаг 2: Настройка переменных окружения
```bash
cp .env.example .env
# Отредактируйте .env файл
nano .env
```

#### Шаг 3: Запуск через Docker Compose
```bash
docker-compose up -d
```

#### Шаг 4: Проверка работы
```bash
# Проверьте логи
docker-compose logs -f

# Проверьте доступность сервисов
curl http://localhost:8000/health
```

### Вариант 2: Ручная установка (для разработки)

#### Backend установка
```bash
# 1. Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate     # Windows

# 2. Установка зависимостей
pip install -r requirements.txt

# 3. Настройка Google Earth Engine
earthengine authenticate

# 4. Настройка базы данных (опционально)
python scripts/init_db.py

# 5. Запуск сервера
python run_server.py
```

#### Frontend установка
```bash
# 1. Переход в директорию frontend
cd gui

# 2. Установка зависимостей
npm install

# 3. Настройка переменных окружения
cp .env.example .env.local

# 4. Запуск dev сервера
npm run dev
```

### Конфигурация

#### Основные конфигурационные файлы

**config/settings.yaml**
```yaml
app:
  name: "Rocket Drop Zone Analysis"
  version: "1.0.0"
  debug: false

simulation:
  monte_carlo_iterations: 1000
  max_cells: 50000
  iqr_filter: true
  iqr_multiplier: 1.5

geospatial:
  default_crs: "EPSG:4326"
  working_crs: "EPSG:3857"
  cell_size_km: 1.0

economic:
  currency: "USD"
  default_rates:
    fire_restoration: 5000
    soil_strength: 3000
    soil_quality: 4000
    vegetation: 8000

google_earth_engine:
  enabled: true
  collection: "COPERNICUS/S2_SR"
  max_cloud_cover: 20
```

**api/.env**
```env
# FastAPI настройки
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_RELOAD=true

# База данных
DATABASE_URL=postgresql://user:pass@localhost:5432/otu_db

# Кэш
REDIS_URL=redis://localhost:6379/0

# Google Earth Engine
GEE_SERVICE_ACCOUNT=your-service-account@project.iam.gserviceaccount.com
GEE_PRIVATE_KEY_PATH=/path/to/private-key.json
```

---

## 🔌 API документация

### Базовый URL
```
http://localhost:8000/api/v1
```

### Основные эндпоинты

#### 1. Симуляция зоны падения
```http
POST /simulation/run
Content-Type: application/json

{
  "launch_site": {
    "lat": 45.965,
    "lon": 63.305,
    "name": "Baikonur"
  },
  "separation_params": {
    "altitude_km": 80.0,
    "velocity_mps": 2500.0,
    "flight_azimuth_deg": 45.0
  },
  "monte_carlo": {
    "iterations": 1000,
    "wind_std_dev": 15.0
  },
  "output_options": {
    "format": "geojson",
    "include_grid": true
  }
}
```

**Ответ:**
```json
{
  "simulation_id": "sim_abc123",
  "status": "completed",
  "ellipse": {
    "center": {"lat": 46.5, "lon": 64.2},
    "semi_major_km": 12.5,
    "semi_minor_km": 8.3,
    "rotation_deg": 25.0
  },
  "statistics": {
    "total_points": 1000,
    "filtered_points": 950,
    "area_km2": 325.7
  },
  "download_url": "/api/v1/simulation/sim_abc123/download"
}
```

#### 2. Получение спутниковых данных
```http
GET /gee/indices?lat=46.5&lon=64.2&radius_km=10&date=2024-01-01
```

#### 3. Экономический анализ
```http
POST /economic/calculate
Content-Type: application/json

{
  "grid_id": "grid_xyz789",
  "currency": "USD",
  "include_breakdown": true
}
```

#### 4. Экспорт результатов
```http
GET /export/{simulation_id}?format=csv
```

### Автоматическая документация

После запуска сервера доступны:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI спецификация**: `http://localhost:8000/openapi.json`

---

## 🐳 Развертывание

### Docker конфигурация

**Dockerfile.backend**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Запуск приложения
CMD ["python", "run_server.py"]
```

**Dockerfile.frontend**
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY gui/package*.json ./
RUN npm ci

COPY gui/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: otu_db
      POSTGRES_USER: otu_user
      POSTGRES_PASSWORD: otu_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      - DATABASE_URL=postgresql://otu_user:otu_password@postgres:5432/otu_db
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "5173:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Облачные платформы

#### AWS ECS/Fargate
```bash
# Сборка и отправка образов
aws ecr create-repository --repository-name otu-backend
docker build -t otu-backend -f Dockerfile.backend .
docker tag otu-backend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/otu-backend:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/otu-backend:latest

# Развертывание через CloudFormation/Terraform
```

#### Google Cloud Run
```bash
# Сборка с Cloud Build
gcloud builds submit --tag gcr.io/PROJECT_ID/otu-backend

# Развертывание
gcloud run deploy otu-backend \
  --image gcr.io/PROJECT_ID/otu-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances
```bash
# Создание контейнера
az container create \
  --resource-group otu-rg \
  --name otu-backend \
  --image otu-backend:latest \
  --ports 8000 \
  --environment-variables DATABASE_URL=...
```

---

## 📊 Мониторинг и логирование

### Метрики Prometheus
```python
# Пример экспорта метрик
from prometheus_client import Counter, Histogram

SIMULATION_REQUESTS = Counter(
    'simulation_requests_total',
    'Total simulation requests',
    ['status']
)

SIMULATION_DURATION = Histogram(
    'simulation_duration_seconds',
    'Simulation duration in seconds',
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0]
)
```

### Логирование
```yaml
# config/logging.yaml
version: 1
formatters:
  detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    formatter: detailed
    level: INFO
  file:
    class: logging.handlers.RotatingFileHandler
    filename: /var/log/otu/application.log
    maxBytes: 10485760  # 10MB
    backupCount: 5
    formatter: detailed
    level: DEBUG
loggers:
  otu:
    level: DEBUG
    handlers: [console, file]
    propagate: no
```

### Health checks
```http
GET /health
```
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "gee": "authenticated"
  },
  "version": "1.0.0"
}
```

---

## 🔧 Устранение неполадок

### Распространенные проблемы

#### Проблема: Ошибка GDAL
```
ERROR: Could not build wheels for gdal, which is required to install pyproject.toml-based projects
```
**Решение:**
```bash
# Ubuntu/Debian
sudo apt-get install gdal-bin libgdal-dev

# macOS
brew install gdal

# Windows: скачайте wheel с https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
```

#### Проблема: Google Earth Engine аутентификация
```
EEException: Please authorize access to your Earth Engine account
```
**Решение:**
```bash
# Интерактивная аутентификация
earthengine authenticate

# Или через service account
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

#### Проблема: Недостаточно памяти для симуляции
```
MemoryError: Unable to allocate array with shape (100000, 2)
```
**Решение:**
1. Уменьшите количество итераций Монте-Карло
2. Увеличьте размер ячейки сетки
3. Используйте параметр `max_cells` в конфигурации

### Отладка

#### Включение детального логирования
```bash
# Запуск с debug режимом
python run_server.py --debug

# Или через переменную окружения
export OTU_LOG_LEVEL=DEBUG
```

#### Профилирование производительности
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Выполнение кода
run_simulation()

profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats(10)
```

---

## 📈 Масштабирование

### Горизонтальное масштабирование
```yaml
# docker-compose.scale.yml
services:
  backend:
    image: otu-backend:latest
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://otu_user:otu_password@postgres:5432/otu_db
```

### Кэширование стратегии
```python
from redis import Redis
from functools import lru_cache

redis_client = Redis.from_url(REDIS_URL)

def get_cached_simulation(simulation_id: str):
    # Попытка получить из Redis
    cached = redis_client.get(f"simulation:{simulation_id}")
    if cached:
        return json.loads(cached)
    
    # Вычисление и кэширование
    result = compute_simulation(simulation_id)
    redis_client.setex(
        f"simulation:{simulation_id}",
        3600,  # TTL 1 час
        json.dumps(result)
    )
    return result
```

### Балансировка нагрузки
```nginx
# nginx.conf
upstream backend_servers {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    
    location /api/ {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 🔗 Связанные документы

Для получения дополнительной информации обратитесь к другим документам проекта:

| Документ | Целевая аудитория | Ключевое содержание |
|----------|-------------------|---------------------|
| [README_OVERVIEW.md](README_OVERVIEW.md) | Широкая публика, руководители | Маркетинговый обзор, преимущества, применение |
| [README_SCIENCE.md](README_SCIENCE.md) | Ученые, исследователи | Математические модели, физические принципы |
| [README_ECONOMICS.md](README_ECONOMICS.md) | Экономисты, аналитики | Методология оценки ущерба, ROI анализ |
| [README_DEVELOPMENT.md](README_DEVELOPMENT.md) | Контрибьюторы | Руководство по вкладу, тестирование |

---

## 📚 Дополнительные ресурсы

- [Архитектурные решения (ADR)](docs/adr/) - Задокументированные архитектурные решения
- [API Reference](docs/api/) - Полная спецификация API
- [Deployment Guides](docs/deployment/) - Руководства по развертыванию на различных платформах
- [Performance Benchmarks](docs/benchmarks/) - Тесты производительности и сравнения

---

<div align="center">
    <br>
    <i>Техническая документация обновлена: Январь 2024</i>
    <br>
    © 2026 Rocket Drop Zone Analysis Team. Все права защищены.
</div>


### 🇰🇿 Қазақша
[KZ]
# 🛠️ Rocket Drop Zone Analysis (OTU) System - Техникалық құжаттама

## 📋 Құжаттың мақсаты

Бұл файл Rocket Drop Zone Analysis (OTU) жүйесінің толық техникалық құжаттамасын қамтиды. Ол әзірлеушілерге, инженерлерге, DevOps мамандарына және жүйені орналастыруға, қолдауға немесе кеңейтуге қатысатын барлық адамдарға арналған.

**Басқа құжаттармен байланыс:**
- Жалпы шолу үшін: [README_OVERVIEW.md](README_OVERVIEW.md)
- Ғылыми әдістеме үшін: [README_SCIENCE.md](README_SCIENCE.md)
- Экономикалық талдау үшін: [README_ECONOMICS.md](README_ECONOMICS.md)
- Әзірлеу және үлес қосу үшін: [README_DEVELOPMENT.md](README_DEVELOPMENT.md)

[⬅️ Негізгі README-ге қайту](./README.md)

---

## 🏗️ Жүйе сәулеті

### Жоғары деңгейлі сәулет

```mermaid
graph TB
    subgraph "Клиенттік қабат (Frontend)"
        Browser[Веб-браузер]
        ReactApp[React Application]
        MapUI[Leaflet Map UI]
    end
    
    subgraph "Серверлік қабат (Backend)"
        API[FastAPI REST API]
        
        subgraph "Бизнес-логика"
            Sim[Монте-Карло симуляторы]
            Grid[Тор генераторы]
            Eco[Экономикалық калькулятор]
            Export[Экспорт сервисі]
        end
        
        subgraph "Интеграциялар"
            GEE[Google Earth Engine Client]
            Geo[Геокеңістіктік кітапханалар]
        end
        
        subgraph "Деректерді сақтау"
            Cache[Redis/In-memory Cache]
            FS[Файлдық жүйе]
            DB[(PostgreSQL/GeoDB)]
        end
    end
    
    Browser --> ReactApp
    ReactApp --> MapUI
    ReactApp --> API
    API --> Sim
    API --> Grid
    API --> Eco
    API --> Export
    Sim --> Cache
    Grid --> Geo
    Eco --> GEE
    Export --> FS
```

### Компоненттік сәулет

| Компонент | Технологиялар | Мақсаты |
|-----------|---------------|---------|
| **API Gateway** | FastAPI, Uvicorn, Pydantic | Барлық сұраныстар үшін бірыңғай кіру нүктесі, валидация, маршрутизация |
| **Монте-Карло қозғалтқышы** | NumPy, SciPy, Numba | Траекториялардың стохастикалық симуляцияларын орындау |
| **Тор генераторы** | GeoPandas, Shapely, PyProj | Шашырау эллипсі ішінде кеңістіктік торды құру |
| **Экономикалық калькулятор** | Pandas, NumPy | Рекультивация құнын және шығынды есептеу |
| **Google Earth Engine клиенті** | earthengine-api, geemap | Жерсеріктік деректерді алу және өңдеу |
| **Frontend қолданбасы** | React, Vite, Leaflet | Интерактивті картасы бар пайдаланушы интерфейсі |
| **Экспорт сервисі** | Pandas, GeoPandas, ReportLab | CSV, GeoJSON, PDF форматтарында есептерді генерациялау |

---

## 📦 Технологиялық стек

### Backend (Python 3.10+)

#### Негізгі тәуелділіктер
```yaml
# requirements.txt (негізгі компоненттер)
earthengine-api:      # Google Earth Engine интеграциясы
geopandas:           # Геокеңістіктік операциялар
shapely:             # Геометриялық примитивтер
pyproj:              # Координаттарды түрлендіру
rasterio:            # Растрлық деректермен жұмыс
numpy:               # Ғылыми есептеулер
scipy:               # Статистика және оптимизация
numba:               # Өнімділік үшін JIT-компиляция
fastapi:             # Веб-фреймворк
uvicorn:             # ASGI сервері
```

#### Көмекші кітапханалар
```yaml
pandas:              # Кестелік деректерді өңдеу
xarray:              # Көп өлшемді массивтер
h5py:                # Үлкен деректерді сақтау
tqdm:                # Прогресс-барлар
requests:            # HTTP клиент
pyyaml:              # Конфигурациялық файлдар
python-multipart:    # Файлдарды жүктеу
```

### Frontend (JavaScript/TypeScript)

#### Негізгі тәуелділіктер
```json
{
  "react": "^18.2.0",        // UI кітапханасы
  "react-dom": "^18.2.0",    // Рендеринг
  "vite": "^5.0.0",          // Жинау және dev сервер
  "leaflet": "^1.9.4",       // Интерактивті карталар
  "react-leaflet": "^4.2.1", // Leaflet-ті React-пен интеграциялау
  "axios": "^1.6.0",         // HTTP клиент
  "recharts": "^2.10.0",     // Графиктер мен диаграммалар
  "tailwindcss": "^3.3.0"    // CSS фреймворк
}
```

### Инфрақұрылым
```yaml
Docker:              # Контейнеризация
Docker Compose:      # Контейнерлерді оркестрациялау
PostgreSQL:          # Дерекқор (PostGIS-пен)
Redis:               # Кэштеу
Nginx:               # Reverse proxy
```

---

## 🚀 Орнату және баптау

### Алғышарттар

#### Жүйелік талаптар
- **ОЖ**: Linux (Ubuntu 20.04+), Windows 10/11, macOS 12+
- **Жад**: минимум 8 ГБ RAM (16 ГБ ұсынылады)
- **Диск**: 10 ГБ бос орын
- **Процессор**: 4+ ядро

#### Бағдарламалық қамтамасыз ету
- **Python 3.10+** pip-пен бірге
- **Node.js 18+** npm-мен бірге
- **Docker 24+** және Docker Compose (міндетті емес)
- **Git** нұсқаларды бақылау үшін

### 1-нұсқа: Docker арқылы орнату (ұсынылады)

#### 1-қадам: Репозиторийді клондау
```bash
git clone https://github.com/your-org/rocket-drop-zone-analysis.git
cd rocket-drop-zone-analysis
```

#### 2-қадам: Орта айнымалыларын баптау
```bash
cp .env.example .env
# .env файлын өңдеңіз
nano .env
```

#### 3-қадам: Docker Compose арқылы іске қосу
```bash
docker-compose up -d
```

#### 4-қадам: Жұмысты тексеру
```bash
# Логтарды тексеріңіз
docker-compose logs -f

# Сервистердің қолжетімділігін тексеріңіз
curl http://localhost:8000/health
```

### 2-нұсқа: Қолмен орнату (әзірлеу үшін)

#### Backend орнату
```bash
# 1. Виртуалды ортаны құру
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# немесе
.venv\Scripts\activate     # Windows

# 2. Тәуелділіктерді орнату
pip install -r requirements.txt

# 3. Google Earth Engine баптау
earthengine authenticate

# 4. Дерекқорды баптау (міндетті емес)
python scripts/init_db.py

# 5. Серверді іске қосу
python run_server.py
```

#### Frontend орнату
```bash
# 1. frontend директориясына өту
cd gui

# 2. Тәуелділіктерді орнату
npm install

# 3. Орта айнымалыларын баптау
cp .env.example .env.local

# 4. dev серверді іске қосу
npm run dev
```

### Конфигурация

#### Негізгі конфигурациялық файлдар

**config/settings.yaml**
```yaml
app:
  name: "Rocket Drop Zone Analysis"
  version: "1.0.0"
  debug: false

simulation:
  monte_carlo_iterations: 1000
  max_cells: 50000
  iqr_filter: true
  iqr_multiplier: 1.5

geospatial:
  default_crs: "EPSG:4326"
  working_crs: "EPSG:3857"
  cell_size_km: 1.0

economic:
  currency: "USD"
  default_rates:
    fire_restoration: 5000
    soil_strength: 3000
    soil_quality: 4000
    vegetation: 8000

google_earth_engine:
  enabled: true
  collection: "COPERNICUS/S2_SR"
  max_cloud_cover: 20
```

**api/.env**
```env
# FastAPI параметрлері
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_RELOAD=true

# Дерекқор
DATABASE_URL=postgresql://user:pass@localhost:5432/otu_db

# Кэш
REDIS_URL=redis://localhost:6379/0

# Google Earth Engine
GEE_SERVICE_ACCOUNT=your-service-account@project.iam.gserviceaccount.com
GEE_PRIVATE_KEY_PATH=/path/to/private-key.json
```

---

## 🔌 API құжаттамасы

### Негізгі URL
```
http://localhost:8000/api/v1
```

### Негізгі эндпоинттер

#### 1. Құлау аймағын симуляциялау
```http
POST /simulation/run
Content-Type: application/json

{
  "launch_site": {
    "lat": 45.965,
    "lon": 63.305,
    "name": "Baikonur"
  },
  "separation_params": {
    "altitude_km": 80.0,
    "velocity_mps": 2500.0,
    "flight_azimuth_deg": 45.0
  },
  "monte_carlo": {
    "iterations": 1000,
    "wind_std_dev": 15.0
  },
  "output_options": {
    "format": "geojson",
    "include_grid": true
  }
}
```

**Жауап:**
```json
{
  "simulation_id": "sim_abc123",
  "status": "completed",
  "ellipse": {
    "center": {"lat": 46.5, "lon": 64.2},
    "semi_major_km": 12.5,
    "semi_minor_km": 8.3,
    "rotation_deg": 25.0
  },
  "statistics": {
    "total_points": 1000,
    "filtered_points": 950,
    "area_km2": 325.7
  },
  "download_url": "/api/v1/simulation/sim_abc123/download"
}
```

#### 2. Жерсеріктік деректерді алу
```http
GET /gee/indices?lat=46.5&lon=64.2&radius_km=10&date=2024-01-01
```

#### 3. Экономикалық талдау
```http
POST /economic/calculate
Content-Type: application/json

{
  "grid_id": "grid_xyz789",
  "currency": "USD",
  "include_breakdown": true
}
```

#### 4. Нәтижелерді экспорттау
```http
GET /export/{simulation_id}?format=csv
```

### Автоматты құжаттама

Сервер іске қосылғаннан кейін қолжетімді:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI спецификациясы**: `http://localhost:8000/openapi.json`

---

## 🐳 Орналастыру

### Docker конфигурациясы

**Dockerfile.backend**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Жүйелік тәуелділіктерді орнату
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Тәуелділіктерді көшіру
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Бастапқы кодты көшіру
COPY . .

# Қолданбаны іске қосу
CMD ["python", "run_server.py"]
```

**Dockerfile.frontend**
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY gui/package*.json ./
RUN npm ci

COPY gui/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: otu_db
      POSTGRES_USER: otu_user
      POSTGRES_PASSWORD: otu_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      - DATABASE_URL=postgresql://otu_user:otu_password@postgres:5432/otu_db
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "5173:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Бұлттық платформалар

#### AWS ECS/Fargate
```bash
# Образдарды жинау және жіберу
aws ecr create-repository --repository-name otu-backend
docker build -t otu-backend -f Dockerfile.backend .
docker tag otu-backend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/otu-backend:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/otu-backend:latest

# CloudFormation/Terraform арқылы орналастыру
```

#### Google Cloud Run
```bash
# Cloud Build-пен жинау
gcloud builds submit --tag gcr.io/PROJECT_ID/otu-backend

# Орналастыру
gcloud run deploy otu-backend \
  --image gcr.io/PROJECT_ID/otu-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances
```bash
# Контейнер құру
az container create \
  --resource-group otu-rg \
  --name otu-backend \
  --image otu-backend:latest \
  --ports 8000 \
  --environment-variables DATABASE_URL=...
```

---

## 📊 Мониторинг және логирование

### Prometheus метрикалары
```python
# Метрикаларды экспорттау мысалы
from prometheus_client import Counter, Histogram

SIMULATION_REQUESTS = Counter(
    'simulation_requests_total',
    'Total simulation requests',
    ['status']
)

SIMULATION_DURATION = Histogram(
    'simulation_duration_seconds',
    'Simulation duration in seconds',
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0]
)
```

### Логирование
```yaml
# config/logging.yaml
version: 1
formatters:
  detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    formatter: detailed
    level: INFO
  file:
    class: logging.handlers.RotatingFileHandler
    filename: /var/log/otu/application.log
    maxBytes: 10485760  # 10MB
    backupCount: 5
    formatter: detailed
    level: DEBUG
loggers:
  otu:
    level: DEBUG
    handlers: [console, file]
    propagate: no
```

### Health checks
```http
GET /health
```
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "gee": "authenticated"
  },
  "version": "1.0.0"
}
```

---

## 🔧 Ақаулықтарды жою

### Жиі кездесетін мәселелер

#### Мәселе: GDAL қатесі
```
ERROR: Could not build wheels for gdal, which is required to install pyproject.toml-based projects
```
**Шешім:**
```bash
# Ubuntu/Debian
sudo apt-get install gdal-bin libgdal-dev

# macOS
brew install gdal

# Windows: wheel-ді https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal сайтынан жүктеп алыңыз
```

#### Мәселе: Google Earth Engine аутентификациясы
```
EEException: Please authorize access to your Earth Engine account
```
**Шешім:**
```bash
# Интерактивті аутентификация
earthengine authenticate

# Немесе service account арқылы
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

#### Мәселе: Симуляция үшін жад жеткіліксіз
```
MemoryError: Unable to allocate array with shape (100000, 2)
```
**Шешім:**
1. Монте-Карло итерациялар санын азайтыңыз
2. Тор ұяшығының өлшемін үлкейтіңіз
3. Конфигурациядағы `max_cells` параметрін қолданыңыз

### Отладка

#### Детальды логирование қосу
```bash
# debug режимімен іске қосу
python run_server.py --debug

# Немесе орта айнымалысы арқылы
export OTU_LOG_LEVEL=DEBUG
```

#### Өнімділікті профильдеу
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Кодты орындау
run_simulation()

profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats(10)
```

---

## 📈 Масштабтау

### Горизонтальды масштабтау
```yaml
# docker-compose.scale.yml
services:
  backend:
    image: otu-backend:latest
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://otu_user:otu_password@postgres:5432/otu_db
```

### Кэштеу стратегиясы
```python
from redis import Redis
from functools import lru_cache

redis_client = Redis.from_url(REDIS_URL)

def get_cached_simulation(simulation_id: str):
    # Redis-тен алуға әрекет
    cached = redis_client.get(f"simulation:{simulation_id}")
    if cached:
        return json.loads(cached)
    
    # Есептеу және кэштеу
    result = compute_simulation(simulation_id)
    redis_client.setex(
        f"simulation:{simulation_id}",
        3600,  # TTL 1 сағат
        json.dumps(result)
    )
    return result
```

### Жүктемені теңгеру
```nginx
# nginx.conf
upstream backend_servers {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    
    location /api/ {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 🔗 Байланысты құжаттар

Қосымша ақпарат алу үшін жобаның басқа құжаттарына жүгініңіз:

| Құжат | Мақсатты аудитория | Негізгі мазмұны |
|-------|--------------------|-----------------|
| [README_OVERVIEW.md](README_OVERVIEW.md) | Көпшілік, басшылар | Маркетинговый обзор, преимущества, применение |
| [README_SCIENCE.md](README_SCIENCE.md) | Ғалымдар, зерттеушілер | Математикалық модельдер, физикалық принциптер |
| [README_ECONOMICS.md](README_ECONOMICS.md) | Экономистер, аналитиктер | Шығынды бағалау әдістемесі, ROI анализ |
| [README_DEVELOPMENT.md](README_DEVELOPMENT.md) | Контрибьюторлар | Үлес қосу нұсқаулығы, тестілеу |

---

## 📚 Қосымша ресурстар

- [Архитектуралық шешімдер (ADR)](docs/adr/) - Құжатталған архитектуралық шешімдер
- [API Reference](docs/api/) - API-дің толық спецификациясы
- [Deployment Guides](docs/deployment/) - Түрлі платформаларда орналастыру бойынша нұсқаулықтар
- [Performance Benchmarks](docs/benchmarks/) - Өнімділік тесттері және салыстырулар

---

<div align="center">
    <br>
    <i>Техникалық құжаттама жаңартылды: Қаңтар 2024</i>
    <br>
    © 2026 Rocket Drop Zone Analysis Team. Барлық құқықтар қорғалған.
</div>