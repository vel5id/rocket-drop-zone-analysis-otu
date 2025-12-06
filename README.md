# 🚀 Rocket Drop Zone Analysis & Ecological Impact Assessment (OTU)

> Monte Carlo simulation toolkit for modeling the first-stage drop zone of the Proton launch vehicle and assessing ecological sustainability using the Q_OTU composite index.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Table of Contents

- [Project Purpose](#-project-purpose)
- [Scientific Background](#-scientific-background)
- [Data Sources](#-data-sources)
  - [Proton Launch Vehicle Specifications](#proton-launch-vehicle-specifications)
  - [Satellite Data](#satellite-data)
- [Project Structure](#-project-structure)
- [Mathematical Models](#-mathematical-models)
- [Installation & Usage](#-installation--usage)
- [Examples](#-examples)
- [License](#-license)
- [Русская версия](#-русская-версия)

---

## 🎯 Project Purpose

This software package was developed **for a scientific publication** dedicated to the methodology for determining ecologically safe drop zones for separating parts of launch vehicles.

**Main objectives:**
1. Monte Carlo ballistic trajectory modeling of the Proton first stage
2. Construction of 3σ dispersion ellipses for the impact zone
3. Calculation of the composite ecological index Q_OTU for each territory cell
4. Visualization of results on interactive maps with satellite data overlay

---

## 📚 Scientific Background

### Territorial Ecological Sustainability Index (Q_OTU)

The composite Q_OTU index evaluates the territory's ability to withstand ecological damage from rocket fragment impacts:

$$Q_{OTU} = (k_{Vi} \cdot Q_{Vi} + k_{Si} \cdot Q_{Si} + k_{Bi} \cdot Q_{Bi}) \times Q_{Relief}$$

**Index components:**

| Index | Name | Weight | Description |
|-------|------|--------|-------------|
| Q_Vi | Vegetation Index | k_Vi = 0.35 | Normalized NDVI, characterizes vegetation cover density |
| Q_Si | Soil Strength | k_Si = 0.35 | Mechanical stability: 0.6×BD + 0.4×Clay |
| Q_Bi | Soil Quality (Bonitet) | k_Bi = 0.30 | Biological productivity: 0.7×SOC + 0.3×N |
| Q_Relief | Relief Modifier | multiplier | Accounts for slope, aspect, and water bodies |

### Additional Indices

- **Q_Fire** — Fire risk (based on biomass/NDVI)
- **Aspect Modifier** — Slope exposure modifier (north-facing slopes are more stable)

---

## 📊 Data Sources

### Proton Launch Vehicle Specifications

First stage parameters of the Proton-M launch vehicle are taken from open sources:
- [Encyclopedia Astronautica](http://www.astronautix.com/p/proton.html)
- [Gunter's Space Page](https://space.skyrocket.de/doc_lau/proton.htm)
- Khrunichev State Research and Production Space Center technical documentation

#### First Stage Geometric and Mass Characteristics

| Parameter | Value | Unit |
|-----------|-------|------|
| Diameter | 7.4 | m |
| Length | 21.18 | m |
| Dry Mass | 30,600 | kg |
| Propellant Mass | 428,300 | kg |
| Reference Area | 43.0 | m² |

#### Propulsion System Characteristics (6× RD-275M)

| Parameter | Value | Unit |
|-----------|-------|------|
| Total Thrust | 10,026 | kN |
| Specific Impulse (sea level) | 288 | s |
| Specific Impulse (vacuum) | 316 | s |
| Burn Time | 123 | s |

#### First Stage Separation Parameters

| Parameter | Mean | σ (StdDev) | Unit |
|-----------|------|------------|------|
| Separation Altitude | 43,000 | 500 | m |
| Velocity | 1,738 | 30 | m/s |
| Flight Path Angle | 25 | 1 | ° |
| Azimuth | 45 | 0.5 | ° |
| Range to Impact | 306 | — | km |

#### Monte Carlo Simulation Perturbations

| Parameter | Distribution | Mean | σ |
|-----------|--------------|------|---|
| Initial Velocity | Normal | 1,738 m/s | 150 m/s |
| Initial Altitude | Normal | 43,000 m | 2,000 m |
| Flight Path Angle | Normal | 25° | 4° |
| Azimuth | Normal | 45° | 3° |
| Drag Coefficient | Uniform | [0.7, 1.5] | — |
| Air Density (factor) | Normal | 1.0 | 0.12 |
| Along-track Wind | Normal | 0 | 40 m/s |
| Cross-track Wind | Normal | 0 | 40 m/s |
| Stage Mass | Normal | 30,600 kg | 500 kg |

### Satellite Data

Ecological data obtained from **Google Earth Engine**:

| Dataset | GEE Identifier | Resolution | Description |
|---------|----------------|------------|-------------|
| NDVI | `MODIS/061/MOD13A2` | 1 km | MODIS Terra vegetation index (16-day composite) |
| DEM | `USGS/SRTMGL1_003` | 30 m | SRTM global elevation model |
| Water Bodies | `JRC/GSW1_4/GlobalSurfaceWater` | 30 m | JRC surface water map |
| Soil (Clay) | `OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02` | 250 m | Soil clay content |
| Soil (Density) | SoilGrids 250m | 250 m | Bulk density |
| Soil (SOC) | SoilGrids 250m | 250 m | Soil organic carbon |
| Soil (Nitrogen) | SoilGrids 250m | 250 m | Total nitrogen |

---

## 📁 Project Structure

```
rocket-drop-zone-analysis-otu/
├── config/                     # Configuration and parameters
│   ├── rocket_params.py        # Proton LV specifications
│   ├── simulation_config.py    # Monte Carlo simulation parameters
│   ├── gee_config.py           # GEE dataset identifiers
│   └── otu_config.py           # Q_OTU index weights and thresholds
│
├── core/                       # Ballistic calculations core
│   ├── atmosphere.py           # Standard atmosphere model
│   ├── aerodynamics.py         # Aerodynamic coefficients
│   ├── ballistics.py           # Equations of motion, RK4 integrator
│   ├── gpu_ballistics.py       # GPU-accelerated calculations (Numba JIT)
│   ├── monte_carlo.py          # Monte Carlo simulation driver
│   ├── trajectory.py           # Trajectory propagator
│   └── geo_utils.py            # Geodetic transformations
│
├── gee/                        # Google Earth Engine integration
│   ├── authenticator.py        # GEE authentication
│   ├── data_fetcher.py         # Data retrieval
│   ├── ndvi_processor.py       # NDVI processing
│   ├── dem_processor.py        # DEM processing (slope, aspect)
│   ├── soil_processor.py       # Soil data processing
│   ├── water_processor.py      # Water bodies processing
│   ├── local_processor.py      # Local processing with chunking
│   └── ecological_index.py     # Ecological indices calculation
│
├── grid/                       # Grid operations
│   ├── grid_generator.py       # 1×1 km grid generation
│   ├── polygon_grid.py         # Polygon grid
│   ├── ellipse_calculator.py   # Dispersion ellipse calculation
│   └── cell_calculator.py      # Cell-wise calculations
│
├── indices/                    # Ecological indices
│   ├── q_otu.py                # Composite Q_OTU index
│   ├── vegetation_index.py     # Vegetation index Q_Vi
│   ├── soil_strength_index.py  # Soil strength index Q_Si
│   ├── soil_quality_index.py   # Soil quality index Q_Bi
│   └── relief_index.py         # Relief modifier Q_Relief
│
├── otu/                        # OTU pipeline
│   ├── calculator.py           # Main OTU calculator
│   ├── otu_logic.py            # Index calculation logic
│   ├── chunk_manager.py        # Chunk manager for large areas
│   ├── temporal_analyzer.py    # Temporal analysis
│   ├── geotiff_exporter.py     # GeoTIFF export
│   └── economic_damage.py      # Economic damage assessment
│
├── visualization/              # Results visualization
│   ├── satellite_overlay.py    # Satellite imagery overlay
│   ├── map_renderer.py         # Map rendering
│   ├── ellipse_plotter.py      # Ellipse plotting
│   ├── heatmap_generator.py    # Heatmap generation
│   └── report_generator.py     # Report generation
│
├── tests/                      # Unit tests
│   ├── test_ballistics.py      # Ballistics tests
│   ├── test_monte_carlo.py     # Monte Carlo tests
│   ├── test_indices.py         # Indices tests
│   └── test_otu_logic.py       # OTU logic tests
│
├── main.py                     # Entry point (demo)
├── run_pipeline.py             # Full simulation pipeline
├── run_otu_pipeline.py         # Q_OTU calculation pipeline
├── requirements.txt            # Python dependencies
└── README.md                   # Documentation
```

---

## 🔬 Mathematical Models

### 1. Ballistic Model

Equations of motion in geocentric coordinate system:

$$\frac{d\vec{r}}{dt} = \vec{v}$$

$$\frac{d\vec{v}}{dt} = \vec{g} + \vec{a}_{drag} + \vec{a}_{wind}$$

where:
- $\vec{g}$ — gravitational acceleration accounting for altitude
- $\vec{a}_{drag} = -\frac{1}{2} \cdot \rho \cdot C_d \cdot A_{ref} \cdot v^2 \cdot \frac{\vec{v}}{|v|} / m$
- $\rho(h)$ — atmospheric density per standard atmosphere model

### 2. Atmosphere Model

U.S. Standard Atmosphere 1976 with exponential interpolation between layers.

### 3. Dispersion Ellipse

3σ dispersion ellipse is constructed from the covariance matrix of impact coordinates:

$$\Sigma = \begin{bmatrix} \sigma_x^2 & \sigma_{xy} \\ \sigma_{xy} & \sigma_y^2 \end{bmatrix}$$

Semi-axes are determined as eigenvalues of $\Sigma$ multiplied by 3.

---

## 🚀 Installation & Usage

### Requirements

- Python 3.10+
- Google Earth Engine account (for satellite data retrieval)

### Installation

```bash
# Clone the repository
git clone https://github.com/vel5id/rocket-drop-zone-analysis-otu.git
cd rocket-drop-zone-analysis-otu

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Authenticate with Google Earth Engine
earthengine authenticate
```

### Running

```bash
# Demo run
python main.py

# Full simulation pipeline (500 iterations)
python run_pipeline.py --iterations 500 --gpu

# Calculate Q_OTU for specified area
python run_otu_pipeline.py --iterations 1000 --cell-size 1.0
```

---

## 📈 Examples

### Basic Simulation

```python
from core.monte_carlo import run_monte_carlo
from config.rocket_params import PROTON_SEPARATION
from config.simulation_config import build_default_config

config = build_default_config()
config.iterations = 1000

impacts = run_monte_carlo(PROTON_SEPARATION, config)
```

### Q_OTU Calculation

```python
from otu.otu_logic import compute_otu_index, compute_q_si, compute_q_bi, compute_q_relief

# Calculate components
q_si = compute_q_si(bulk_density=1400, clay=350)
q_bi = compute_q_bi(soc=45, nitrogen=3.5)
q_relief = compute_q_relief(slope_degrees=12, is_water=0, aspect_degrees=180)

# Composite index
q_otu = compute_otu_index(q_vi=0.65, q_si=q_si, q_bi=q_bi, q_relief=q_relief)
```

---

## 📄 License

This project is created for scientific research purposes.

---

## 👥 Author

- Development: vel5id

---

## 📞 Contact

For questions and suggestions: [GitHub Issues](https://github.com/vel5id/rocket-drop-zone-analysis-otu/issues)

---

---

# 🇷🇺 Русская версия

<details>
<summary><b>Нажмите, чтобы развернуть документацию на русском языке</b></summary>

## 🎯 Цель проекта

Данный программный комплекс разработан **для научной статьи**, посвящённой методологии определения экологически безопасных зон падения отделяющихся частей ракет-носителей.

**Основные задачи:**
1. Моделирование баллистической траектории первой ступени РН "Протон" методом Монте-Карло
2. Построение эллипсов рассеивания (3σ) зоны падения
3. Расчёт комплексного экологического индекса Q_OTU для каждой ячейки территории
4. Визуализация результатов на интерактивных картах с наложением спутниковых данных

---

## 📚 Научная основа

### Индекс экологической устойчивости территории (Q_OTU)

Композитный индекс Q_OTU оценивает способность территории противостоять экологическому ущербу от падения фрагментов ракеты:

$$Q_{OTU} = (k_{Vi} \cdot Q_{Vi} + k_{Si} \cdot Q_{Si} + k_{Bi} \cdot Q_{Bi}) \times Q_{Relief}$$

**Компоненты индекса:**

| Индекс | Название | Весовой коэффициент | Описание |
|--------|----------|---------------------|----------|
| Q_Vi | Вегетационный индекс | k_Vi = 0.35 | Нормализованный NDVI, характеризует плотность растительного покрова |
| Q_Si | Прочность почв | k_Si = 0.35 | Механическая устойчивость: 0.6×BD + 0.4×Clay |
| Q_Bi | Качество почв (бонитет) | k_Bi = 0.30 | Биологическая продуктивность: 0.7×SOC + 0.3×N |
| Q_Relief | Рельефный модификатор | множитель | Учитывает уклон, экспозицию склона и водные объекты |

---

## 📊 Исходные данные

### Характеристики ракеты-носителя "Протон"

Параметры первой ступени РН "Протон" взяты из открытых источников:
- [Encyclopedia Astronautica](http://www.astronautix.com/p/proton.html)
- [Gunter's Space Page](https://space.skyrocket.de/doc_lau/proton.htm)
- Техническая документация ГКНПЦ им. М.В. Хруничева

#### Геометрические и массовые характеристики первой ступени

| Параметр | Значение | Единица измерения |
|----------|----------|-------------------|
| Диаметр | 7.4 | м |
| Длина | 21.18 | м |
| Масса (сухая) | 30,600 | кг |
| Масса топлива | 428,300 | кг |
| Опорная площадь | 43.0 | м² |

#### Характеристики двигательной установки (6× РД-275М)

| Параметр | Значение | Единица измерения |
|----------|----------|-------------------|
| Суммарная тяга | 10,026 | кН |
| Удельный импульс (ур. моря) | 288 | с |
| Удельный импульс (вакуум) | 316 | с |
| Время работы | 123 | с |

#### Параметры отделения первой ступени

| Параметр | Среднее | σ (СКО) | Единица |
|----------|---------|---------|---------|
| Высота отделения | 43,000 | 500 | м |
| Скорость | 1,738 | 30 | м/с |
| Угол наклона траектории | 25 | 1 | ° |
| Азимут | 45 | 0.5 | ° |
| Дальность до точки падения | 306 | — | км |

#### Возмущения для моделирования Монте-Карло

| Параметр | Распределение | Среднее | σ |
|----------|---------------|---------|---|
| Начальная скорость | Нормальное | 1,738 м/с | 150 м/с |
| Начальная высота | Нормальное | 43,000 м | 2,000 м |
| Угол наклона траектории | Нормальное | 25° | 4° |
| Азимут | Нормальное | 45° | 3° |
| Коэффициент сопротивления | Равномерное | [0.7, 1.5] | — |
| Плотность воздуха (множитель) | Нормальное | 1.0 | 0.12 |
| Ветер вдоль трассы | Нормальное | 0 | 40 м/с |
| Ветер поперёк трассы | Нормальное | 0 | 40 м/с |
| Масса ступени | Нормальное | 30,600 кг | 500 кг |

### Спутниковые данные

Экологические данные получены из **Google Earth Engine**:

| Датасет | Идентификатор GEE | Разрешение | Описание |
|---------|-------------------|------------|----------|
| NDVI | `MODIS/061/MOD13A2` | 1 км | Индекс вегетации MODIS Terra (16-дневный композит) |
| DEM | `USGS/SRTMGL1_003` | 30 м | Глобальная модель рельефа SRTM |
| Водные объекты | `JRC/GSW1_4/GlobalSurfaceWater` | 30 м | Карта поверхностных вод JRC |
| Почвы (глина) | `OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02` | 250 м | Содержание глины в почве |
| Почвы (плотность) | SoilGrids 250m | 250 м | Объёмная плотность почвы |
| Почвы (SOC) | SoilGrids 250m | 250 м | Органический углерод почвы |
| Почвы (азот) | SoilGrids 250m | 250 м | Общий азот |

---

## 🔬 Математические модели

### 1. Баллистическая модель

Уравнения движения в геоцентрической системе координат:

$$\frac{d\vec{r}}{dt} = \vec{v}$$

$$\frac{d\vec{v}}{dt} = \vec{g} + \vec{a}_{drag} + \vec{a}_{wind}$$

где:
- $\vec{g}$ — гравитационное ускорение с учётом высоты
- $\vec{a}_{drag} = -\frac{1}{2} \cdot \rho \cdot C_d \cdot A_{ref} \cdot v^2 \cdot \frac{\vec{v}}{|v|} / m$
- $\rho(h)$ — плотность атмосферы по стандартной атмосфере

### 2. Модель атмосферы

Используется U.S. Standard Atmosphere 1976 с экспоненциальной интерполяцией между слоями.

### 3. Эллипс рассеивания

3σ эллипс рассеивания строится на основе ковариационной матрицы координат падения:

$$\Sigma = \begin{bmatrix} \sigma_x^2 & \sigma_{xy} \\ \sigma_{xy} & \sigma_y^2 \end{bmatrix}$$

Полуоси эллипса определяются как собственные значения $\Sigma$, умноженные на 3.

---

## 🚀 Установка и запуск

### Требования

- Python 3.10+
- Google Earth Engine account (для получения спутниковых данных)

### Установка

```bash
# Клонирование репозитория
git clone https://github.com/vel5id/rocket-drop-zone-analysis-otu.git
cd rocket-drop-zone-analysis-otu

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Аутентификация в Google Earth Engine
earthengine authenticate
```

### Запуск

```bash
# Демо запуск
python main.py

# Полный пайплайн симуляции (500 итераций)
python run_pipeline.py --iterations 500 --gpu

# Расчёт Q_OTU для заданной области
python run_otu_pipeline.py --iterations 1000 --cell-size 1.0
```

</details>
