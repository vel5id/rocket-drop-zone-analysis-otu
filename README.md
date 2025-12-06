# 🚀 Rocket Drop Zone Analysis & Ecological Impact Assessment (OTU)

> Monte Carlo simulation toolkit for modeling the first-stage drop zone of the Proton launch vehicle and assessing ecological sustainability using the Q_OTU composite index.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌍 Select Language / Выберите язык / Seleccione idioma

| 🇬🇧 [English](#-english) | 🇷🇺 [Русский](#-русский) | 🇪🇸 [Español](#-español) | 🤖 [AI/LLM Context](#-aillm-context) |
|:---:|:---:|:---:|:---:|

---

<details open>
<summary><h2>🇬🇧 English</h2></summary>

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
├── main.py                     # Entry point (demo)
├── run_pipeline.py             # Full simulation pipeline
├── run_otu_pipeline.py         # Q_OTU calculation pipeline
└── requirements.txt            # Python dependencies
```

---

## 🔬 Mathematical Models

### 1. Ballistic Model

Equations of motion in geocentric coordinate system:

$$\frac{d\vec{r}}{dt} = \vec{v}$$

$$\frac{d\vec{v}}{dt} = \vec{g} + \vec{a}_{drag} + \vec{a}_{wind}$$

### 2. Atmosphere Model

U.S. Standard Atmosphere 1976 with exponential interpolation between layers.

### 3. Dispersion Ellipse

3σ dispersion ellipse is constructed from the covariance matrix of impact coordinates.

---

## 🚀 Installation & Usage

```bash
# Clone the repository
git clone https://github.com/vel5id/rocket-drop-zone-analysis-otu.git
cd rocket-drop-zone-analysis-otu

# Create virtual environment
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Authenticate with Google Earth Engine
earthengine authenticate

# Run demo
python main.py
```

---

## 📈 Examples

```python
from core.monte_carlo import run_monte_carlo
from config.rocket_params import PROTON_SEPARATION
from config.simulation_config import build_default_config

config = build_default_config()
config.iterations = 1000
impacts = run_monte_carlo(PROTON_SEPARATION, config)
```

</details>

---

<details>
<summary><h2>🇷🇺 Русский</h2></summary>

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

| Индекс | Название | Вес | Описание |
|--------|----------|-----|----------|
| Q_Vi | Вегетационный индекс | 0.35 | Нормализованный NDVI |
| Q_Si | Прочность почв | 0.35 | 0.6×BD + 0.4×Clay |
| Q_Bi | Качество почв | 0.30 | 0.7×SOC + 0.3×N |
| Q_Relief | Рельеф | множитель | Уклон, экспозиция, водные объекты |

---

## 📊 Исходные данные

### Характеристики РН "Протон"

Источники:
- [Encyclopedia Astronautica](http://www.astronautix.com/p/proton.html)
- [Gunter's Space Page](https://space.skyrocket.de/doc_lau/proton.htm)
- Документация ГКНПЦ им. М.В. Хруничева

#### Первая ступень

| Параметр | Значение | Ед. изм. |
|----------|----------|----------|
| Диаметр | 7.4 | м |
| Длина | 21.18 | м |
| Сухая масса | 30,600 | кг |
| Масса топлива | 428,300 | кг |

#### Двигательная установка (6× РД-275М)

| Параметр | Значение | Ед. изм. |
|----------|----------|----------|
| Тяга | 10,026 | кН |
| Уд. импульс (ур. моря) | 288 | с |
| Уд. импульс (вакуум) | 316 | с |
| Время работы | 123 | с |

#### Параметры отделения

| Параметр | Среднее | σ | Ед. |
|----------|---------|---|-----|
| Высота | 43,000 | 500 | м |
| Скорость | 1,738 | 30 | м/с |
| Угол траектории | 25 | 1 | ° |
| Дальность | 306 | — | км |

### Спутниковые данные (Google Earth Engine)

| Датасет | ID | Разрешение |
|---------|----|------------|
| NDVI | `MODIS/061/MOD13A2` | 1 км |
| DEM | `USGS/SRTMGL1_003` | 30 м |
| Водные объекты | `JRC/GSW1_4/GlobalSurfaceWater` | 30 м |
| Почвы | SoilGrids 250m | 250 м |

---

## 🚀 Установка и запуск

```bash
git clone https://github.com/vel5id/rocket-drop-zone-analysis-otu.git
cd rocket-drop-zone-analysis-otu
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
earthengine authenticate
python main.py
```

</details>

---

<details>
<summary><h2>🇪🇸 Español</h2></summary>

## 🎯 Propósito del Proyecto

Este paquete de software fue desarrollado **para una publicación científica** dedicada a la metodología para determinar zonas de caída ecológicamente seguras para las partes separables de vehículos de lanzamiento.

**Objetivos principales:**
1. Modelado de trayectoria balística Monte Carlo de la primera etapa del Proton
2. Construcción de elipses de dispersión 3σ para la zona de impacto
3. Cálculo del índice ecológico compuesto Q_OTU para cada celda del territorio
4. Visualización de resultados en mapas interactivos con superposición de datos satelitales

---

## 📚 Base Científica

### Índice de Sostenibilidad Ecológica Territorial (Q_OTU)

El índice compuesto Q_OTU evalúa la capacidad del territorio para resistir el daño ecológico de los impactos de fragmentos de cohetes:

$$Q_{OTU} = (k_{Vi} \cdot Q_{Vi} + k_{Si} \cdot Q_{Si} + k_{Bi} \cdot Q_{Bi}) \times Q_{Relief}$$

**Componentes del índice:**

| Índice | Nombre | Peso | Descripción |
|--------|--------|------|-------------|
| Q_Vi | Índice de Vegetación | 0.35 | NDVI normalizado |
| Q_Si | Resistencia del Suelo | 0.35 | 0.6×BD + 0.4×Arcilla |
| Q_Bi | Calidad del Suelo | 0.30 | 0.7×SOC + 0.3×N |
| Q_Relief | Modificador de Relieve | multiplicador | Pendiente, aspecto, cuerpos de agua |

---

## 📊 Fuentes de Datos

### Especificaciones del Vehículo de Lanzamiento Proton

Fuentes:
- [Encyclopedia Astronautica](http://www.astronautix.com/p/proton.html)
- [Gunter's Space Page](https://space.skyrocket.de/doc_lau/proton.htm)

#### Primera Etapa

| Parámetro | Valor | Unidad |
|-----------|-------|--------|
| Diámetro | 7.4 | m |
| Longitud | 21.18 | m |
| Masa Seca | 30,600 | kg |
| Masa de Propelente | 428,300 | kg |

#### Sistema de Propulsión (6× RD-275M)

| Parámetro | Valor | Unidad |
|-----------|-------|--------|
| Empuje Total | 10,026 | kN |
| Impulso Específico (nivel del mar) | 288 | s |
| Impulso Específico (vacío) | 316 | s |
| Tiempo de Combustión | 123 | s |

### Datos Satelitales (Google Earth Engine)

| Conjunto de Datos | ID | Resolución |
|-------------------|----|------------|
| NDVI | `MODIS/061/MOD13A2` | 1 km |
| DEM | `USGS/SRTMGL1_003` | 30 m |
| Cuerpos de Agua | `JRC/GSW1_4/GlobalSurfaceWater` | 30 m |
| Suelos | SoilGrids 250m | 250 m |

---

## 🚀 Instalación y Uso

```bash
git clone https://github.com/vel5id/rocket-drop-zone-analysis-otu.git
cd rocket-drop-zone-analysis-otu
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
earthengine authenticate
python main.py
```

</details>

---

<details>
<summary><h2>🤖 AI/LLM Context</h2></summary>

## AI Assistant Instructions

This section provides structured context for AI assistants (ChatGPT, Claude, Gemini, Copilot, etc.) working with this codebase.

### Project Overview

```yaml
project_name: rocket-drop-zone-analysis-otu
domain: Aerospace Engineering & Environmental Science
purpose: Monte Carlo simulation of rocket stage drop zones + ecological impact assessment
language: Python 3.10+
key_dependencies:
  - numpy, scipy, numba (computations)
  - earthengine-api, geemap (satellite data)
  - folium, plotly (visualization)
  - geopandas, shapely (geospatial)
```

### Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    SIMULATION PIPELINE                       │
├─────────────────────────────────────────────────────────────┤
│  config/           →  Rocket parameters, simulation config   │
│  core/             →  Ballistics, atmosphere, Monte Carlo    │
│  grid/             →  Spatial grid, dispersion ellipses      │
├─────────────────────────────────────────────────────────────┤
│                    ECOLOGICAL PIPELINE                        │
├─────────────────────────────────────────────────────────────┤
│  gee/              →  Google Earth Engine data fetching      │
│  indices/          →  Individual ecological indices          │
│  otu/              →  Composite Q_OTU calculation            │
├─────────────────────────────────────────────────────────────┤
│                    OUTPUT                                     │
├─────────────────────────────────────────────────────────────┤
│  visualization/    →  Maps, heatmaps, reports                │
│  output/           →  Generated files (gitignored)           │
└─────────────────────────────────────────────────────────────┘
```

### Key Formulas

**Q_OTU (Ecological Sustainability Index):**
```
Q_OTU = (0.35×Q_Vi + 0.35×Q_Si + 0.30×Q_Bi) × Q_Relief

Where:
- Q_Vi = normalized NDVI [0,1]
- Q_Si = 0.6×norm(bulk_density) + 0.4×norm(clay) [0,1]
- Q_Bi = 0.7×norm(SOC) + 0.3×norm(nitrogen) [0,1]
- Q_Relief = f(slope, aspect, water) [0,1]
```

### Entry Points

| Script | Purpose | Example |
|--------|---------|---------|
| `main.py` | Quick demo | `python main.py` |
| `run_pipeline.py` | Full simulation | `python run_pipeline.py --iterations 500 --gpu` |
| `run_otu_pipeline.py` | OTU calculation | `python run_otu_pipeline.py --iterations 1000` |

### Important Files for Code Understanding

| File | Description |
|------|-------------|
| `config/rocket_params.py` | Proton LV physical parameters |
| `config/otu_config.py` | All Q_OTU weights and thresholds |
| `core/monte_carlo.py` | Monte Carlo simulation driver |
| `core/gpu_ballistics.py` | Numba JIT-accelerated ballistics |
| `otu/otu_logic.py` | Core Q_OTU calculation logic |
| `gee/local_processor.py` | GEE data fetching with chunking |
| `visualization/satellite_overlay.py` | Interactive map generation |

### Common Tasks

**1. Modify rocket parameters:**
Edit `config/rocket_params.py` — `PROTON_STAGE_ONE`, `PROTON_ENGINE_BLOCK`, `PROTON_SEPARATION`

**2. Change Q_OTU weights:**
Edit `config/otu_config.py` — `OTUWeights` class

**3. Add new ecological index:**
1. Create `indices/new_index.py`
2. Add calculation in `otu/otu_logic.py`
3. Update `otu/calculator.py` to include it

**4. Change GEE datasets:**
Edit `config/gee_config.py` — add new `DatasetReference`

### Testing

```bash
pytest tests/ -v
```

### Code Style

- Type hints used throughout
- Dataclasses for configuration
- NumPy vectorization preferred
- Numba JIT for hot paths

### Gotchas

1. **GEE Authentication**: Requires `earthengine authenticate` before first run
2. **GPU Mode**: Uses Numba JIT, not actual GPU — naming is legacy
3. **Large Areas**: Use chunking via `chunk_manager.py` to avoid GEE payload limits
4. **Output Files**: All in `output/` directory, gitignored

</details>

---

## 👥 Author

- Development: vel5id

## 📞 Contact

For questions and suggestions: [GitHub Issues](https://github.com/vel5id/rocket-drop-zone-analysis-otu/issues)
